"""CHERRY Staff AI — separate bot for staff-only customer reply drafting.

Two-stage flow:
  Stage 1 — customer message + meaning (Help Reply / Staff Reply / Cancel)
  Stage 2 — AI suggested reply OR staff text translated to customer language

No Google Sheets, no billing, no V3 logic.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.staff_ai")

VERSION = "CHERRY STAFF AI - TWO-STAGE-V4-CASE-PERSIST"
ROOT = Path(__file__).resolve().parent
KNOWLEDGE_PATH = ROOT / "CHERRY_KNOWLEDGE.md"
if not KNOWLEDGE_PATH.is_file():
    KNOWLEDGE_PATH = ROOT.parent / "CHERRY_KNOWLEDGE.md"
ACTIVE_CASE_KEY = "staff_ai_active_case"
# In-memory fallback: PTB chat_data can be empty on the next webhook request.
_ACTIVE_CASES: dict[str, dict[str, Any]] = {}
_AWAITING_STAFF_REPLY: dict[str, dict[str, Any]] = {}

FALLBACK_EN = (
    "Thank you for contacting CHERRY Wash & Dry. Our staff will assist you shortly."
)


@dataclass
class StaffUnderstanding:
    detected_language: str
    language_name: str
    staff_meaning: str


@dataclass
class StaffReplyDraft:
    staff_meaning: str
    customer_reply: str


@dataclass
class StaffTranslationDraft:
    staff_wrote: str
    language_name: str
    translated_reply: str


STAFF_REPLY_PROMPT = (
    "✍️ Please type your reply.\n"
    "You can type in Thai, Khmer, English, or Indonesian.\n"
    "AI will translate it to the customer language."
)


def parse_chat_id(raw: str) -> int | None:
    text = str(raw or "").strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_allowed_user_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in str(raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return frozenset(ids)


def staff_group_id() -> int | None:
    return parse_chat_id(os.getenv("STAFF_GROUP_ID", ""))


def is_setup_mode() -> bool:
    """True until STAFF_GROUP_ID is set on Render — allows setup commands in any staff group."""
    return staff_group_id() is None


def allowed_user_ids() -> frozenset[int]:
    return parse_allowed_user_ids(os.getenv("ALLOWED_USER_IDS", ""))


def openai_client() -> Any | None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed — pip install openai")
        return None
    timeout = float(os.getenv("OPENAI_TIMEOUT_SEC", "60") or "60")
    return OpenAI(api_key=key, timeout=timeout, max_retries=2)


def openai_error_hint(exc: Exception) -> str:
    text = str(exc).lower()
    if "insufficient_quota" in text or "exceeded your current quota" in text:
        return (
            "OpenAI quota exhausted — add billing/credits at platform.openai.com "
            "or replace OPENAI_API_KEY on Render."
        )
    if "rate limit" in text or "429" in text:
        return "OpenAI rate limit — wait a minute and try again."
    if "invalid_api_key" in text or "incorrect api key" in text:
        return "Invalid OPENAI_API_KEY on Render."
    return f"{exc.__class__.__name__}: {exc}"


def probe_openai() -> tuple[bool, str]:
    client = openai_client()
    if not client:
        return False, "NO KEY"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        client.chat.completions.create(
            model=model,
            max_tokens=5,
            messages=[{"role": "user", "content": "Reply with OK"}],
        )
        return True, "OK"
    except Exception as exc:
        logger.warning("OpenAI probe failed: %s", exc)
        return False, openai_error_hint(exc)


def load_knowledge() -> str:
    if KNOWLEDGE_PATH.is_file():
        return KNOWLEDGE_PATH.read_text(encoding="utf-8")
    logger.warning("Knowledge file missing: %s", KNOWLEDGE_PATH)
    return ""


def resolve_webhook_url() -> str:
    explicit = os.getenv("WEBHOOK_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    render = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if render:
        return f"{render.rstrip('/')}/telegram"
    return ""


def is_staff_chat(update: Update) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    if not chat:
        return False
    if is_setup_mode():
        if chat.type in ("group", "supergroup"):
            return True
        return user is not None and user.id in allowed_user_ids()
    group = staff_group_id()
    if group and chat.id == group:
        return True
    return (
        user is not None
        and user.id in allowed_user_ids()
        and chat.type == "private"
    )


def extract_customer_text(message: Any) -> str:
    if isinstance(message, str):
        text = message.strip()
    else:
        text = str(getattr(message, "text", "") or getattr(message, "caption", "") or "").strip()
    text = re.sub(
        r"^(customer|client|ลูกค้า|អតិថិជន)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    text = re.sub(r"@[A-Za-z0-9_]+\s*", "", text).strip()
    return text


def extract_message_context(message: Any) -> tuple[str, int | None, str]:
    text = extract_customer_text(message)
    telegram_id: int | None = None
    order_id = ""

    forward_from = getattr(message, "forward_from", None)
    if forward_from is not None:
        telegram_id = getattr(forward_from, "id", None)

    forward_origin = getattr(message, "forward_origin", None)
    if telegram_id is None and forward_origin is not None:
        sender = getattr(forward_origin, "sender_user", None)
        if sender is not None:
            telegram_id = getattr(sender, "id", None)

    order_match = re.search(
        r"(?:order\s*id|order)\s*[:#]?\s*(CR[-\w]+)",
        text,
        flags=re.IGNORECASE,
    )
    if order_match:
        order_id = order_match.group(1).strip().upper()

    tg_match = re.search(
        r"(?:telegram\s*id|tg\s*id|telegram)\s*[:#]?\s*(\d{5,})",
        text,
        flags=re.IGNORECASE,
    )
    if tg_match:
        try:
            telegram_id = int(tg_match.group(1))
        except ValueError:
            pass

    return text, telegram_id, order_id


def build_understand_system_prompt() -> str:
    return (
        "You are CHERRY Wash & Dry Poipet staff assistant.\n"
        "Staff pasted a customer message. Do NOT draft a customer reply.\n"
        "Return a single JSON object with exactly these keys:\n"
        "  detected_language — short code (en, th, km, id, zh, ...)\n"
        "  language_name — human-readable language name\n"
        "  staff_meaning — ONE short line in Khmer OR Thai explaining what the customer is asking\n"
        "Keep staff_meaning under 80 characters. No prices, no suggested reply."
    )


def build_reply_system_prompt(knowledge: str) -> str:
    return (
        "You are CHERRY Wash & Dry Poipet staff assistant.\n"
        "Use ONLY facts from the knowledge base below. Never invent prices or policies.\n"
        "Never promise refunds, compensation, point changes, or verified order status.\n\n"
        "Return a single JSON object with exactly these keys:\n"
        "  staff_meaning — ONE short line in Khmer OR Thai (same meaning as before)\n"
        "  customer_reply — SHORT reply in THE CUSTOMER'S LANGUAGE for staff to copy-paste\n"
        "  Style: casual chat, 1–3 short lines max, easy to copy.\n"
        "  Answer only what they asked. No filler closings.\n\n"
        "Knowledge base:\n"
        f"{knowledge}"
    )


def clamp_customer_reply(text: str, *, max_words: int = 35, max_chars: int = 220) -> str:
    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return FALLBACK_EN
    words = cleaned.split()
    if len(words) > max_words:
        cleaned = " ".join(words[:max_words]).rstrip(".,;:!?")
    if len(cleaned) > max_chars:
        cleaned = cleaned[: max_chars - 1].rsplit(" ", 1)[0].rstrip(".,;:!?") + "…"
    return cleaned


def build_reply_user_prompt(
    customer_text: str,
    *,
    staff_meaning: str = "",
    mode: str = "normal",
    previous_reply: str = "",
) -> str:
    meaning_block = f"Staff meaning: {staff_meaning}\n\n" if staff_meaning else ""
    if mode == "shorter":
        return (
            f"{meaning_block}"
            f"Customer message:\n{customer_text}\n\n"
            "Make customer_reply MUCH shorter — max 15 words, minimal facts only.\n"
            f"Previous customer_reply:\n{previous_reply}"
        )
    if mode == "rewrite":
        return (
            f"{meaning_block}"
            f"Customer message:\n{customer_text}\n\n"
            "Rewrite customer_reply with different wording. Same facts, same brevity.\n"
            f"Previous customer_reply:\n{previous_reply}"
        )
    return (
        f"{meaning_block}"
        f"Customer message:\n{customer_text}\n\n"
        "Draft a short customer-safe reply staff can copy."
    )


def parse_llm_json(raw: str) -> dict[str, Any]:
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("LLM response is not a JSON object")
    return data


def understanding_from_payload(payload: dict[str, Any]) -> StaffUnderstanding:
    meaning = str(
        payload.get("staff_meaning")
        or payload.get("staff_layer_km")
        or payload.get("staff_layer_th")
        or ""
    ).strip()
    return StaffUnderstanding(
        detected_language=str(payload.get("detected_language", "") or "unknown").strip(),
        language_name=str(payload.get("language_name", "") or "Unknown").strip(),
        staff_meaning=meaning or "—",
    )


def reply_from_payload(payload: dict[str, Any], *, mode: str = "normal") -> StaffReplyDraft:
    max_words = 15 if mode == "shorter" else 40
    max_chars = 120 if mode == "shorter" else 280
    meaning = str(
        payload.get("staff_meaning")
        or payload.get("staff_layer_km")
        or payload.get("staff_layer_th")
        or ""
    ).strip()
    return StaffReplyDraft(
        staff_meaning=meaning or "—",
        customer_reply=clamp_customer_reply(
            str(payload.get("customer_reply", "") or FALLBACK_EN),
            max_words=max_words,
            max_chars=max_chars,
        ),
    )


def draft_understand(customer_text: str) -> StaffUnderstanding:
    client = openai_client()
    if not client:
        return StaffUnderstanding("?", "Unknown", "⚠️ OPENAI_API_KEY not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,
            max_tokens=120,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_understand_system_prompt()},
                {"role": "user", "content": f"Customer message:\n{customer_text}"},
            ],
        )
        raw = response.choices[0].message.content or "{}"
        return understanding_from_payload(parse_llm_json(raw))
    except Exception as exc:
        logger.exception("OpenAI understand failed")
        return StaffUnderstanding("?", "Unknown", f"⚠️ {openai_error_hint(exc)}")


def draft_customer_reply(
    customer_text: str,
    *,
    staff_meaning: str = "",
    mode: str = "normal",
    previous_reply: str = "",
    knowledge: str = "",
) -> StaffReplyDraft:
    client = openai_client()
    if not client:
        return StaffReplyDraft(
            staff_meaning=staff_meaning or "⚠️ OPENAI_API_KEY not set",
            customer_reply=FALLBACK_EN,
        )

    kb = knowledge or load_knowledge()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    max_tokens = 180 if mode == "shorter" else 320
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3 if mode == "normal" else 0.5,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_reply_system_prompt(kb)},
                {
                    "role": "user",
                    "content": build_reply_user_prompt(
                        customer_text,
                        staff_meaning=staff_meaning,
                        mode=mode,
                        previous_reply=previous_reply,
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        draft = reply_from_payload(parse_llm_json(raw), mode=mode)
        if staff_meaning and draft.staff_meaning == "—":
            draft = StaffReplyDraft(staff_meaning=staff_meaning, customer_reply=draft.customer_reply)
        return draft
    except Exception as exc:
        logger.exception("OpenAI reply draft failed")
        return StaffReplyDraft(
            staff_meaning=staff_meaning or f"⚠️ {openai_error_hint(exc)}",
            customer_reply=FALLBACK_EN,
        )


def build_translate_system_prompt() -> str:
    return (
        "You translate staff-written replies into the customer's language for CHERRY Wash & Dry.\n"
        "Keep the same meaning as staff wrote. Do not add new facts, prices, or promises.\n"
        "Short casual chat style — easy to copy-paste. No filler closings.\n\n"
        "Return a single JSON object with exactly this key:\n"
        "  translated_reply — the staff message translated into the customer's language"
    )


def build_translate_user_prompt(
    staff_text: str,
    *,
    customer_language: str,
    language_name: str,
    customer_original: str = "",
    mode: str = "normal",
    previous_reply: str = "",
) -> str:
    context_block = ""
    if customer_original.strip():
        context_block = f"Original customer message (context only):\n{customer_original.strip()}\n\n"
    target = f"Target language: {language_name} ({customer_language})\n\n"
    if mode == "shorter":
        return (
            f"{context_block}{target}"
            f"Staff wrote:\n{staff_text}\n\n"
            "Make translated_reply MUCH shorter — max 15 words.\n"
            f"Previous translated_reply:\n{previous_reply}"
        )
    if mode == "rewrite":
        return (
            f"{context_block}{target}"
            f"Staff wrote:\n{staff_text}\n\n"
            "Rewrite translated_reply with different wording. Same meaning, same brevity.\n"
            f"Previous translated_reply:\n{previous_reply}"
        )
    return (
        f"{context_block}{target}"
        f"Staff wrote:\n{staff_text}\n\n"
        "Translate to the customer language. Keep it short."
    )


def translation_from_payload(payload: dict[str, Any], *, mode: str = "normal") -> str:
    max_words = 15 if mode == "shorter" else 40
    max_chars = 120 if mode == "shorter" else 280
    return clamp_customer_reply(
        str(payload.get("translated_reply", "") or ""),
        max_words=max_words,
        max_chars=max_chars,
    )


def draft_staff_translation(
    staff_text: str,
    *,
    customer_language: str,
    language_name: str,
    customer_original: str = "",
    mode: str = "normal",
    previous_reply: str = "",
) -> StaffTranslationDraft:
    client = openai_client()
    if not client:
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            translated_reply=FALLBACK_EN,
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    max_tokens = 120 if mode == "shorter" else 220
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.2 if mode == "normal" else 0.4,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_translate_system_prompt()},
                {
                    "role": "user",
                    "content": build_translate_user_prompt(
                        staff_text,
                        customer_language=customer_language,
                        language_name=language_name,
                        customer_original=customer_original,
                        mode=mode,
                        previous_reply=previous_reply,
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        translated = translation_from_payload(parse_llm_json(raw), mode=mode)
        if not translated or translated == FALLBACK_EN:
            translated = staff_text
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            translated_reply=translated,
        )
    except Exception as exc:
        logger.exception("OpenAI staff translation failed")
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            translated_reply=f"⚠️ {openai_error_hint(exc)}",
        )


def format_stage1_card(original_text: str, understanding: StaffUnderstanding) -> str:
    original_block = original_text.strip() or "(no text)"
    return "\n".join([
        "🤖 CHERRY Staff AI",
        "",
        "📩 Customer Message",
        original_block,
        "",
        "🌐 Language",
        understanding.language_name,
        "",
        "👀 Meaning for Staff",
        understanding.staff_meaning,
    ])


def format_stage2_card(
    draft: StaffReplyDraft,
    *,
    mode_label: str = "",
) -> str:
    header = "🤖 CHERRY AI Reply"
    if mode_label:
        header = f"{header} · {mode_label}"
    return "\n".join([
        header,
        "",
        "👀 Meaning for Staff",
        draft.staff_meaning,
        "",
        "💬 Reply /តបភ្ញៀវ",
        draft.customer_reply,
        "",
        "━━━━━━━━━━━━━━",
        "⚠️ Check before send",
    ])


def format_staff_translation_card(
    draft: StaffTranslationDraft,
    *,
    mode_label: str = "",
) -> str:
    header = "🤖 CHERRY AI Reply"
    if mode_label:
        header = f"{header} · {mode_label}"
    return "\n".join([
        header,
        "",
        "👩🏼‍💻 Staff /បុគ្គលិក",
        draft.staff_wrote,
        "",
        "🌐 Customer Language",
        draft.language_name,
        "",
        "💬 Reply /តបភ្ញៀវ",
        draft.translated_reply,
        "",
        "━━━━━━━━━━━━━━",
        "⚠️ Check before send",
    ])


def stage1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Help Reply", callback_data="staffai:help"),
            InlineKeyboardButton("✍️ Staff Reply", callback_data="staffai:staff_reply"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="staffai:cancel")],
    ])


def stage2_keyboard(*, show_send: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("🔄 Rewrite", callback_data="staffai:rewrite"),
            InlineKeyboardButton("✂️ Shorter", callback_data="staffai:shorter"),
        ],
    ]
    if show_send:
        rows.append([InlineKeyboardButton("✅ Send to Customer", callback_data="staffai:send")])
    rows.append([InlineKeyboardButton("❌ Cancel", callback_data="staffai:cancel_reply")])
    return InlineKeyboardMarkup(rows)


USAGE_TEXT = (
    "CHERRY Staff AI — 2-stage support flow\n\n"
    "1) Paste or forward a customer message → bot shows meaning only\n"
    "2) 📝 Help Reply → AI suggests a reply\n"
    "   ✍️ Staff Reply → you type, AI translates to customer language\n\n"
    "Optional: forward from customer (for Send to Customer) or add Order ID / Telegram ID in text\n"
    "Setup: /group — show this group's ID for Render"
)

SETUP_HINT = (
    "CHERRY Staff AI is running (setup mode).\n\n"
    "Send /group to get STAFF_GROUP_ID for Render.\n"
    "After deploy, paste customer messages here for AI replies.\n\n"
    "BotFather: /setprivacy → Disable (so bot sees all messages in group)."
)


def format_group_id_message(update: Update) -> str:
    chat = update.effective_chat
    user = update.effective_user
    lines = [f"CHERRY Staff AI — {VERSION}", ""]
    if chat and chat.type in ("group", "supergroup"):
        lines.extend([
            f"Group / ក្រុម: {chat.title or '-'}",
            "",
            "Copy this line to Render → Environment:",
            f"STAFF_GROUP_ID={chat.id}",
            "",
            "Then click Manual Deploy.",
        ])
    elif chat:
        lines.extend([
            f"Chat type: {chat.type}",
            f"Chat ID: {chat.id}",
            "",
            "Open your staff Telegram group and send /group there.",
        ])
    if user:
        lines.extend([
            "",
            f"Your user ID: {user.id}",
            f"(optional) ALLOWED_USER_IDS={user.id}",
        ])
    configured = staff_group_id()
    if configured is not None:
        match = chat and chat.id == configured
        lines.extend([
            "",
            f"STAFF_GROUP_ID on server: {configured}",
            f"This chat matches: {'YES' if match else 'NO'}",
        ])
    else:
        lines.append("")
        lines.append("STAFF_GROUP_ID on server: not set yet")
    return "\n".join(lines)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        await update.message.reply_text("This bot is for CHERRY staff only.")
        return
    text = USAGE_TEXT
    if is_setup_mode():
        text = f"{SETUP_HINT}\n\n{USAGE_TEXT}"
    await update.message.reply_text(text)


async def group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Always reply — used during first-time setup to get STAFF_GROUP_ID."""
    if not update.message:
        return
    await update.message.reply_text(format_group_id_message(update))


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        return
    kb = "OK" if KNOWLEDGE_PATH.is_file() else "MISSING"
    ok, llm = probe_openai()
    llm_status = llm if ok else f"FAIL — {llm}"
    await update.message.reply_text(f"{VERSION}\nKnowledge: {kb}\nOpenAI: {llm_status}")


def show_send_button(stored: dict[str, Any]) -> bool:
    return bool(stored.get("telegram_id"))


def _await_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}:{user_id}"


def set_awaiting_staff_reply(chat_id: int, user_id: int, case: dict[str, Any]) -> dict[str, Any]:
    payload = dict(case)
    payload["awaiting_staff_reply"] = True
    payload["staff_reply_user_id"] = user_id
    _AWAITING_STAFF_REPLY[_await_key(chat_id, user_id)] = payload
    logger.info(
        "awaiting staff reply chat=%s user=%s customer_lang=%s",
        chat_id,
        user_id,
        payload.get("language_name"),
    )
    return payload


def get_awaiting_staff_reply(chat_id: int, user_id: int) -> dict[str, Any] | None:
    pending = _AWAITING_STAFF_REPLY.get(_await_key(chat_id, user_id))
    return dict(pending) if isinstance(pending, dict) else None


def clear_awaiting_staff_reply(chat_id: int, user_id: int) -> None:
    _AWAITING_STAFF_REPLY.pop(_await_key(chat_id, user_id), None)


def clear_awaiting_for_chat(chat_id: int) -> None:
    prefix = f"{chat_id}:"
    for key in list(_AWAITING_STAFF_REPLY):
        if key.startswith(prefix):
            del _AWAITING_STAFF_REPLY[key]


def _active_case_key(chat_id: int) -> str:
    return str(chat_id)


def save_active_case(
    context: ContextTypes.DEFAULT_TYPE,
    case: dict[str, Any],
    *,
    chat_id: int,
) -> None:
    payload = dict(case)
    context.chat_data[ACTIVE_CASE_KEY] = payload
    _ACTIVE_CASES[_active_case_key(chat_id)] = payload


def get_active_case(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> dict[str, Any] | None:
    stored = context.chat_data.get(ACTIVE_CASE_KEY)
    if isinstance(stored, dict):
        return dict(stored)
    fallback = _ACTIVE_CASES.get(_active_case_key(chat_id))
    return dict(fallback) if isinstance(fallback, dict) else None


def clear_active_case(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    context.chat_data.pop(ACTIVE_CASE_KEY, None)
    _ACTIVE_CASES.pop(_active_case_key(chat_id), None)


async def process_staff_reply_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    stored: dict[str, Any],
    staff_text: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    if not staff_text:
        await message.reply_text("Please type your reply text.")
        return

    chat = update.effective_chat
    user = update.effective_user
    stored = dict(stored)
    stored["awaiting_staff_reply"] = False
    stored["staff_reply_user_id"] = None
    stored["reply_source"] = "staff"
    stored["staff_wrote"] = staff_text

    if chat and user:
        clear_awaiting_staff_reply(chat.id, user.id)

    try:
        await message.chat.send_action("typing")
        draft = await asyncio.to_thread(
            draft_staff_translation,
            staff_text,
            customer_language=str(stored.get("detected_language", "") or ""),
            language_name=str(stored.get("language_name", "") or "Unknown"),
            customer_original=str(stored.get("question", "") or ""),
        )
        stored["customer_reply"] = draft.translated_reply
        card = format_staff_translation_card(draft)
        await send_stage2_reply(message=message, context=context, stored=stored, card=card)
    except Exception:
        logger.exception("staff reply translation failed")
        await message.reply_text("⚠️ Could not translate. Try again or send /health.")


def new_case_payload(
    *,
    question: str,
    understanding: StaffUnderstanding,
    telegram_id: int | None,
    order_id: str,
    stage1_message_id: int,
) -> dict[str, Any]:
    return {
        "question": question,
        "detected_language": understanding.detected_language,
        "language_name": understanding.language_name,
        "staff_meaning": understanding.staff_meaning,
        "customer_reply": "",
        "reply_source": "ai",
        "staff_wrote": "",
        "awaiting_staff_reply": False,
        "staff_reply_user_id": None,
        "stage1_message_id": stage1_message_id,
        "reply_message_id": None,
        "telegram_id": telegram_id,
        "order_id": order_id,
    }


async def send_stage2_reply(
    *,
    message: Any,
    context: ContextTypes.DEFAULT_TYPE,
    stored: dict[str, Any],
    card: str,
    mode_label: str = "",
) -> None:
    sent = await message.reply_text(
        card,
        reply_markup=stage2_keyboard(show_send=show_send_button(stored)),
    )
    stored["reply_message_id"] = sent.message_id
    save_active_case(context, stored, chat_id=message.chat_id)


async def handle_staff_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        return
    message = update.effective_message
    if not message or not message.text:
        if message and message.caption:
            await message.reply_text("Photo received — please paste the customer's text question as well.")
        return

    raw_text = message.text.strip()
    if raw_text.startswith("/"):
        return

    user = update.effective_user
    chat = update.effective_chat

    if chat and user:
        pending = get_awaiting_staff_reply(chat.id, user.id)
        if pending:
            await process_staff_reply_input(
                update,
                context,
                stored=pending,
                staff_text=raw_text.strip(),
            )
            return

    stored = get_active_case(context, chat.id) if chat else None
    if (
        isinstance(stored, dict)
        and stored.get("awaiting_staff_reply")
        and user is not None
        and stored.get("staff_reply_user_id") == user.id
    ):
        await process_staff_reply_input(
            update,
            context,
            stored=stored,
            staff_text=raw_text.strip(),
        )
        return

    text, telegram_id, order_id = extract_message_context(message)
    if not text:
        return

    if is_setup_mode():
        await message.reply_text(SETUP_HINT)
        return

    chat = update.effective_chat
    logger.info(
        "stage1 chat=%s user=%s text=%r",
        getattr(chat, "id", None),
        getattr(user, "id", None),
        text[:120],
    )

    if chat:
        clear_awaiting_for_chat(chat.id)

    try:
        await message.chat.send_action("typing")
        understanding = await asyncio.to_thread(draft_understand, text)
        card = format_stage1_card(text, understanding)
        sent = await message.reply_text(card, reply_markup=stage1_keyboard())

        save_active_case(
            context,
            new_case_payload(
                question=text,
                understanding=understanding,
                telegram_id=telegram_id,
                order_id=order_id,
                stage1_message_id=sent.message_id,
            ),
            chat_id=chat.id,
        )
    except Exception:
        logger.exception("handle_staff_message failed for text=%r", text[:120])
        await message.reply_text(
            "⚠️ Could not read message. Send /health to check OpenAI, then try again."
        )


async def staff_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_staff_chat(update):
        return

    action = (query.data or "").split(":", 1)[-1]
    chat_id = query.message.chat_id if query.message else None
    if chat_id is None:
        return
    stored = get_active_case(context, chat_id)
    if not isinstance(stored, dict):
        await query.message.reply_text("Paste a customer message first.")
        return

    question = str(stored.get("question", "") or "").strip()
    staff_meaning = str(stored.get("staff_meaning", "") or "").strip()
    if not question:
        await query.message.reply_text("Paste a customer message first.")
        return

    if action == "cancel":
        if query.message and query.from_user:
            clear_awaiting_staff_reply(query.message.chat_id, query.from_user.id)
        clear_active_case(context, chat_id)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text("Cancelled.")
        return

    if action == "cancel_reply":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text("Reply dismissed. Copy manually if needed.")
        return

    if action == "help":
        if query.message and query.from_user:
            clear_awaiting_staff_reply(query.message.chat_id, query.from_user.id)
        stored["awaiting_staff_reply"] = False
        stored["staff_reply_user_id"] = None
        stored["reply_source"] = "ai"
        await query.message.chat.send_action("typing")
        draft = await asyncio.to_thread(
            draft_customer_reply,
            question,
            staff_meaning=staff_meaning,
            knowledge=load_knowledge(),
        )
        stored["staff_meaning"] = draft.staff_meaning
        stored["customer_reply"] = draft.customer_reply
        card = format_stage2_card(draft)
        await send_stage2_reply(message=query.message, context=context, stored=stored, card=card)
        return

    if action == "staff_reply":
        if not query.message or not query.from_user:
            if query.message:
                await query.message.reply_text("Could not start Staff Reply — try again.")
            return
        payload = set_awaiting_staff_reply(query.message.chat_id, query.from_user.id, stored)
        save_active_case(context, payload, chat_id=chat_id)
        await query.message.reply_text(STAFF_REPLY_PROMPT)
        return

    if action == "send":
        telegram_id = stored.get("telegram_id")
        reply_text = str(stored.get("customer_reply", "") or "").strip()
        if not telegram_id or not reply_text:
            await query.message.reply_text("Customer Telegram ID not known — copy manually.")
            return
        try:
            await context.bot.send_message(chat_id=int(telegram_id), text=reply_text)
            await query.message.reply_text(f"Sent to customer (Telegram ID {telegram_id}).")
        except Exception:
            logger.exception("send to customer failed")
            await query.message.reply_text("Could not send — copy manually.")
        return

    if action not in ("rewrite", "shorter"):
        return

    previous = str(stored.get("customer_reply", "") or "").strip()
    if not previous:
        await query.message.reply_text("Press 📝 Help Reply or ✍️ Staff Reply first.")
        return

    await query.message.chat.send_action("typing")
    mode = "rewrite" if action == "rewrite" else "shorter"
    label = "Rewrite" if action == "rewrite" else "Shorter"

    if stored.get("reply_source") == "staff":
        staff_wrote = str(stored.get("staff_wrote", "") or "").strip()
        if not staff_wrote:
            await query.message.reply_text("Staff reply text missing — press ✍️ Staff Reply again.")
            return
        draft = await asyncio.to_thread(
            draft_staff_translation,
            staff_wrote,
            customer_language=str(stored.get("detected_language", "") or ""),
            language_name=str(stored.get("language_name", "") or "Unknown"),
            customer_original=question,
            mode=mode,
            previous_reply=previous,
        )
        stored["customer_reply"] = draft.translated_reply
        card = format_staff_translation_card(draft, mode_label=label)
    else:
        draft = await asyncio.to_thread(
            draft_customer_reply,
            question,
            staff_meaning=staff_meaning,
            mode=mode,
            previous_reply=previous,
            knowledge=load_knowledge(),
        )
        stored["staff_meaning"] = draft.staff_meaning
        stored["customer_reply"] = draft.customer_reply
        card = format_stage2_card(draft, mode_label=label)

    await send_stage2_reply(
        message=query.message,
        context=context,
        stored=stored,
        card=card,
        mode_label=label,
    )


def build_health_response() -> str:
    return f"OK {VERSION}\n"


def _install_health_route() -> None:
    """Add GET /health to PTB tornado webhook app (Render health checks)."""
    import tornado.web
    from telegram.ext._utils import webhookhandler as wh

    class HealthHandler(tornado.web.RequestHandler):
        def get(self) -> None:
            self.set_header("Content-Type", "text/plain; charset=utf-8")
            self.write(build_health_response())

    class HealthWebhookApp(tornado.web.Application):
        def __init__(
            self,
            webhook_path: str,
            bot: Any,
            update_queue: Any,
            secret_token: str | None = None,
        ) -> None:
            path = webhook_path if webhook_path.startswith("/") else f"/{webhook_path}"
            shared_objects = {
                "bot": bot,
                "update_queue": update_queue,
                "secret_token": secret_token,
            }
            handlers = [
                (r"/health/?", HealthHandler),
                (rf"{path}/?", wh.TelegramHandler, shared_objects),
            ]
            super().__init__(handlers)

        def log_request(self, handler: tornado.web.RequestHandler) -> None:
            pass

    wh.WebhookAppClass = HealthWebhookApp
    try:
        import telegram.ext._updater as updater_mod

        updater_mod.WebhookAppClass = HealthWebhookApp
    except ImportError:
        pass


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Bot error — try again or send /health to check OpenAI."
            )
        except Exception:
            pass


def build_app() -> Application:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    app = Application.builder().token(token).concurrent_updates(True).build()
    app.add_error_handler(on_error)
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("group", group_cmd))
    app.add_handler(CommandHandler("chatid", group_cmd))
    app.add_handler(CommandHandler("id", group_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(CallbackQueryHandler(staff_ai_callback, pattern=r"^staffai:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_staff_message))
    return app


def main() -> None:
    logger.info("Starting %s", VERSION)
    if not KNOWLEDGE_PATH.is_file():
        logger.warning("Missing knowledge file at %s", KNOWLEDGE_PATH)
    app = build_app()
    webhook_url = resolve_webhook_url()
    port = int(os.getenv("PORT", "8080"))
    if webhook_url:
        logger.info("WEBHOOK mode %s port=%s", webhook_url, port)
        _install_health_route()
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/telegram",
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
        )
    else:
        logger.info("POLLING mode (set WEBHOOK_URL on Render)")
        app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
