"""CHERRY Staff AI — staff reply translator only.

Flow:
  Stage 1 — customer message + language + meaning (Staff Reply / Cancel)
  Stage 2 — staff types reply → AI translates/cleans to customer language

No auto-generated customer replies. No billing, no V3 logic.
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
from telegram import CopyTextButton, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.staff_ai")

VERSION = "CHERRY STAFF AI - TRANSLATOR-V2-KM-MEANING"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"
KNOWLEDGE_PATH = ROOT / "CHERRY_KNOWLEDGE.md"
if not KNOWLEDGE_PATH.is_file():
    KNOWLEDGE_PATH = ROOT.parent / "CHERRY_KNOWLEDGE.md"
ACTIVE_CASE_KEY = "staff_ai_active_case"
# In-memory fallback between webhook requests (same process).
_AWAITING_STAFF_REPLY: dict[str, dict[str, Any]] = {}
_PROMPT_TO_CASE: dict[int, dict[str, Any]] = {}

FALLBACK_EN = (
    "Thank you for contacting CHERRY Wash & Dry. Our staff will assist you shortly."
)


@dataclass
class StaffUnderstanding:
    detected_language: str
    language_name: str
    staff_meaning: str


@dataclass
class StaffTranslationDraft:
    staff_wrote: str
    language_name: str
    customer_reply: str
    staff_meaning: str = ""


STAFF_REPLY_PROMPT = (
    "✍️ Please type your reply.\n"
    "You can type in Thai, Khmer, English, or Indonesian.\n"
    "AI will translate it to the customer language."
)

REPLY_CHECK_FOOTER = "⚠️ Please check carefully before sending."

KHMER_SCRIPT_RE = re.compile(r"[\u1780-\u17FF]")
THAI_SCRIPT_RE = re.compile(r"[\u0E00-\u0E7F]")


def looks_like_khmer(text: str) -> bool:
    return bool(KHMER_SCRIPT_RE.search(str(text or "")))


def looks_like_staff_language(text: str) -> bool:
    raw = str(text or "")
    return looks_like_khmer(raw) or bool(THAI_SCRIPT_RE.search(raw))


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


def language_hints_for_text(text: str) -> list[str]:
    """Lightweight clues for LLM — helps with short/incomplete romanized messages."""
    hints: list[str] = []
    raw = str(text or "").strip()
    lower = raw.lower()
    if not lower:
        return hints

    if re.search(r"[\u1780-\u17FF]", raw):
        hints.append("Khmer script present → likely Khmer (km).")
    if re.search(r"[\u4e00-\u9fff]", raw):
        hints.append("Chinese characters present → likely Chinese (zh).")
    if re.search(r"[\u0E00-\u0E7F]", raw):
        hints.append("Thai script present → likely Thai (th).")

    id_markers = (
        "loh", "dong", "gak", "nggak", "sedikit", "hanya", "berapa", "bisa",
        "sudah", "belum", "tolong", "kapan", "mahal", "murah", "gimana", "kamu",
    )
    tl_markers = (
        "po", "ba", "kayo", "bakit", "naman", "sila", "salamat", "pwede",
        "magkano", "saan", "paano", "po ba", "lang po",
    )
    ms_markers = ("saya", "boleh", "tak", "macam", "bila", "nak", "berapa", "baju")
    km_roman = (
        "bong", "sabay", "som", "khom", "nov", "del", "tver", "luk", "ot",
        "men", "ban", "pel", "som ot", "nov del",
    )
    en_markers = (
        "the", "how", "what", "when", "price", "ready", "done", "please",
        "thank", "hello", "hi", "my", "your", "can", "will",
    )

    id_hits = sum(1 for w in id_markers if re.search(rf"\b{re.escape(w)}\b", lower))
    tl_hits = sum(1 for w in tl_markers if re.search(rf"\b{re.escape(w)}\b", lower))
    ms_hits = sum(1 for w in ms_markers if re.search(rf"\b{re.escape(w)}\b", lower))
    km_hits = sum(1 for w in km_roman if re.search(rf"\b{re.escape(w)}\b", lower))
    en_hits = sum(1 for w in en_markers if re.search(rf"\b{re.escape(w)}\b", lower))

    if id_hits >= 1 and "loh" in lower:
        hints.append("Informal Indonesian marker 'loh' → lean Indonesian (id), not Khmer.")
    if id_hits >= 2:
        hints.append(f"Multiple Indonesian markers ({id_hits}) → likely Indonesian (id).")
    if tl_hits >= 1 or (re.search(r"\bmahal\b", lower) and re.search(r"\b(ya|po|ba|lang)\b", lower)):
        hints.append("Tagalog/Filipino patterns (mahal/po/ba/lang) → likely Tagalog (tl), NOT Khmer.")
    if ms_hits >= 2 and id_hits == 0:
        hints.append(f"Malay markers ({ms_hits}) → likely Malay (ms).")
    if km_hits >= 1 and not re.search(r"[\u1780-\u17FF]", raw):
        hints.append(f"Khmer romanization hints ({km_hits}) → possible Khmer (km).")
    if en_hits >= 2 and not re.search(r"[\u1780-\u17FF\u0E00-\u0E7F\u4e00-\u9fff]", raw):
        hints.append(f"English word patterns ({en_hits}) → likely English (en).")

    if len(lower.split()) <= 4:
        hints.append(
            "Message is very short — infer language from word choice, spelling, and chat style; "
            "do not default to Khmer unless evidence supports it."
        )
    return hints


def message_topic_hints(text: str) -> list[str]:
    """Light topic hints for customer-message understanding only."""
    hints: list[str] = []
    lower = str(text or "").lower()
    if not lower.strip():
        return hints
    if any(w in lower for w in ("price", "mahal", "murah", "berapa", "harga", "เท่าไหร", "ราคา")):
        hints.append("Customer may be asking about price.")
    if any(w in lower for w in ("sedikit", "hanya", "little", "few", "น้อย", "ไม่เยอะ")):
        hints.append("Customer may mention small amount of laundry.")
    if any(w in lower for w in ("ready", "sabay", "nov", "เสร็จ", "when", "buka")):
        hints.append("Customer may ask about timing or readiness.")
    return hints


def build_understand_system_prompt() -> str:
    return (
        "You are CHERRY Wash & Dry Poipet staff assistant.\n"
        "Staff are Cambodian shop workers. They pasted a customer message.\n"
        "Do NOT draft a customer reply.\n\n"
        "CHALLENGE: messages are often SHORT, incomplete, typo-filled, or romanized (no native script).\n"
        "Use context clues, common border-area chat patterns, and word choice to pick the BEST language.\n"
        "Poipet customers often use: Khmer, Thai, English, Indonesian, Malay, Chinese, Tagalog, Vietnamese.\n\n"
        "Language rules (do not confuse):\n"
        "- Tagalog (tl): mahal, po, ba, lang, bakit, magkano, salamat — NOT Khmer.\n"
        "- Indonesian (id): loh, dong, gak, sedikit, hanya, berapa, gimana — NOT Khmer.\n"
        "- Malay (ms): saya, boleh, tak, nak, macam — similar to Indonesian; pick best fit.\n"
        "- Khmer (km): Khmer script OR romanization like bong, sabay, som ot, nov del, luk.\n"
        "- Thai (th): Thai script or romanized Thai particles.\n\n"
        "Return a single JSON object with exactly these keys:\n"
        "  detected_language — best short code (en, th, km, id, tl, ms, zh, vi, ...)\n"
        "  language_name — clear name staff can read (e.g. Tagalog, Indonesian, Khmer)\n"
        "  staff_meaning — 1–2 SHORT lines in Khmer script ONLY (ភាសាខ្មែរ). Never Thai.\n"
        "    Simple words for shop staff. Start with អតិថិជន when possible.\n"
        "    Do NOT draft a customer reply. Do NOT add shop prices unless customer asked.\n\n"
        "Examples:\n"
        '  "Kok mahal ya ka" → tl, Tagalog, "ลูกค้าถามว่าทำไมแพง" or "អតិថិជនសួរថាហេវហេតុថ្លៃ"\n'
        '  "Ini hanya sedikit loh" → id, Indonesian, "អតិថិជនមានអាវតិច"\n'
        '  "เสร็จยัง" → th, Thai, "អតិថិជនសួរថារួចហើយឬនៅ"\n'
    )


def build_understand_user_prompt(customer_text: str) -> str:
    lang_hints = language_hints_for_text(customer_text)
    topic_hints = message_topic_hints(customer_text)
    all_hints = lang_hints + topic_hints
    hint_block = ""
    if all_hints:
        hint_block = "Hints:\n" + "\n".join(f"- {h}" for h in all_hints) + "\n\n"
    return (
        f"{hint_block}"
        f"Customer message (may be incomplete):\n{customer_text.strip() or '(empty)'}\n\n"
        "Detect the most likely customer language and explain the meaning in simple Khmer for staff."
    )


def clamp_customer_reply(text: str, *, max_words: int = 30, max_chars: int = 200) -> str:
    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return FALLBACK_EN
    words = cleaned.split()
    if len(words) > max_words:
        cleaned = " ".join(words[:max_words]).rstrip(".,;:!?")
    if len(cleaned) > max_chars:
        cleaned = cleaned[: max_chars - 1].rsplit(" ", 1)[0].rstrip(".,;:!?") + "…"
    return cleaned


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


def draft_staff_reply_meaning(*, staff_wrote: str, customer_reply: str) -> str:
    """Khmer-only summary of what will be sent to the customer."""
    client = openai_client()
    if not client:
        return "—"
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=120,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Explain for Cambodian shop staff in Khmer script ONLY (1-2 short lines).\n"
                        "Summarize what the customer_reply will tell the customer.\n"
                        "NEVER use Thai, Indonesian, English, or Malay."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Staff wrote:\n{staff_wrote.strip()}\n\n"
                        f"Customer reply to send:\n{customer_reply.strip()}\n\n"
                        'Return JSON: {"staff_meaning":"..."}'
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        meaning = str(parse_llm_json(raw).get("staff_meaning", "") or "").strip()
        if looks_like_khmer(meaning):
            return meaning
    except Exception:
        logger.exception("Staff reply meaning repair failed")
    return "—"


def ensure_staff_reply_meaning(draft: StaffTranslationDraft) -> StaffTranslationDraft:
    if looks_like_khmer(draft.staff_meaning):
        return draft
    repaired = draft_staff_reply_meaning(
        staff_wrote=draft.staff_wrote,
        customer_reply=draft.customer_reply,
    )
    return StaffTranslationDraft(
        staff_wrote=draft.staff_wrote,
        language_name=draft.language_name,
        customer_reply=draft.customer_reply,
        staff_meaning=repaired,
    )


def draft_understand(customer_text: str) -> StaffUnderstanding:
    client = openai_client()
    if not client:
        return StaffUnderstanding("?", "Unknown", "⚠️ OPENAI_API_KEY not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_understand_system_prompt()},
                {"role": "user", "content": build_understand_user_prompt(customer_text)},
            ],
        )
        raw = response.choices[0].message.content or "{}"
        return understanding_from_payload(parse_llm_json(raw))
    except Exception as exc:
        logger.exception("OpenAI understand failed")
        return StaffUnderstanding("?", "Unknown", f"⚠️ {openai_error_hint(exc)}")


def build_translate_system_prompt() -> str:
    return (
        "You clean and translate staff-written replies for CHERRY Wash & Dry customers.\n"
        "You do NOT answer for staff. You do NOT add shop knowledge.\n\n"
        "RULES:\n"
        "- translated_reply: target customer language ONLY. Short, natural, easy to copy.\n"
        "- staff_meaning: 1-2 short lines in Khmer script ONLY — what customer will receive.\n"
        "- Do NOT invent information.\n"
        "- Do NOT add price, time, policy, or promise unless staff wrote it.\n"
        "- Only clean grammar/tone and translate. Keep the same meaning as staff wrote.\n"
        "- Never put Khmer/Thai in translated_reply unless that IS the customer language.\n\n"
        "Return JSON keys: translated_reply, staff_meaning"
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
    target = f"Target customer language: {language_name} ({customer_language})\n\n"
    lang_rule = (
        f"translated_reply MUST be in {language_name} only. "
        "Do NOT output Khmer or Thai unless that is the target language.\n\n"
    )
    if mode == "shorter":
        return (
            f"{context_block}{target}{lang_rule}"
            f"Staff wrote:\n{staff_text}\n\n"
            f"Make translated_reply MUCH shorter in {language_name} — max 12 words.\n"
            f"Same meaning only — do not add new facts.\n"
            f"Update staff_meaning in Khmer script only.\n"
            f"Previous translated_reply:\n{previous_reply}"
        )
    if mode == "rewrite":
        return (
            f"{context_block}{target}{lang_rule}"
            f"Staff wrote:\n{staff_text}\n\n"
            f"Rewrite translated_reply in {language_name}. Same meaning — no new facts.\n"
            f"Update staff_meaning in Khmer script only.\n"
            f"Previous translated_reply:\n{previous_reply}"
        )
    return (
        f"{context_block}{target}{lang_rule}"
        f"Staff wrote:\n{staff_text}\n\n"
        f"Translate and lightly clean to {language_name}. staff_meaning in Khmer script only."
    )


def translation_from_payload(payload: dict[str, Any], *, mode: str = "normal") -> str:
    max_words = 12 if mode == "shorter" else 30
    max_chars = 100 if mode == "shorter" else 200
    return clamp_customer_reply(
        str(payload.get("translated_reply", "") or payload.get("customer_reply", "") or ""),
        max_words=max_words,
        max_chars=max_chars,
    )


def translation_draft_from_payload(
    payload: dict[str, Any],
    *,
    staff_text: str,
    language_name: str,
    mode: str = "normal",
) -> StaffTranslationDraft:
    customer_reply = translation_from_payload(payload, mode=mode) or staff_text
    meaning = str(
        payload.get("staff_meaning")
        or payload.get("reply_meaning_km")
        or ""
    ).strip()
    return StaffTranslationDraft(
        staff_wrote=staff_text,
        language_name=language_name,
        customer_reply=customer_reply,
        staff_meaning=meaning or "—",
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
            customer_reply=FALLBACK_EN,
            staff_meaning="⚠️ OPENAI_API_KEY not set",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    max_tokens = 160 if mode == "shorter" else 280
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.15 if mode == "normal" else 0.3,
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
        draft = translation_draft_from_payload(
            parse_llm_json(raw),
            staff_text=staff_text,
            language_name=language_name,
            mode=mode,
        )
        if not draft.customer_reply or draft.customer_reply == FALLBACK_EN:
            draft = StaffTranslationDraft(
                staff_wrote=staff_text,
                language_name=language_name,
                customer_reply=staff_text,
                staff_meaning=draft.staff_meaning,
            )
        return ensure_staff_reply_meaning(draft)
    except Exception as exc:
        logger.exception("OpenAI staff translation failed")
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            customer_reply=f"⚠️ {openai_error_hint(exc)}",
            staff_meaning="—",
        )


def format_stage1_card(original_text: str, understanding: StaffUnderstanding) -> str:
    original_block = original_text.strip() or "(no text)"
    lang_line = understanding.language_name.strip() or "Unknown"
    code = understanding.detected_language.strip().lower()
    if code and code not in {"?", "unknown"}:
        lang_line = f"{lang_line} ({code})"
    return "\n".join([
        "🤖 CHERRY Staff AI",
        "",
        "📩 Customer Message",
        original_block,
        "",
        "🌐 Customer Language",
        lang_line,
        "",
        "👀 Meaning for Staff",
        understanding.staff_meaning,
    ])


def format_reply_check_card(draft: StaffTranslationDraft, *, mode_label: str = "") -> str:
    header = "🤖 CHERRY Reply Check"
    if mode_label.strip():
        header = f"{header} · {mode_label.strip()}"
    return "\n".join([
        header,
        "",
        "👀 Staff Meaning / សម្រាប់បុគ្គលិក",
        draft.staff_meaning or "—",
        "",
        "💬 Customer Reply",
        draft.customer_reply,
        "",
        "━━━━━━━━━━━━━━",
        REPLY_CHECK_FOOTER,
    ])


def stage1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Staff Reply / បុគ្គលិកឆ្លើយ", callback_data="staffai:staff_reply")],
        [InlineKeyboardButton("❌ Cancel / បោះបង់", callback_data="staffai:cancel")],
    ])


def copy_text_for_button(text: str, *, max_len: int = 256) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return FALLBACK_EN
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 1].rstrip() + "…"


def stage2_keyboard(*, copy_text: str = "", show_send: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton("🔄 Rewrite / សរសេរឡើងវិញ", callback_data="staffai:rewrite"),
            InlineKeyboardButton("✂️ Shorter / ខ្លីជាង", callback_data="staffai:shorter"),
        ],
    ]
    if copy_text.strip():
        rows.append([
            InlineKeyboardButton(
                "📋 Copy / ចម្លង",
                copy_text=CopyTextButton(text=copy_text_for_button(copy_text)),
            ),
        ])
    if show_send:
        rows.append([
            InlineKeyboardButton("✅ Send to Customer / ផ្ញើទៅអតិថិជន", callback_data="staffai:send"),
        ])
    rows.append([InlineKeyboardButton("❌ Cancel / បោះបង់", callback_data="staffai:cancel_reply")])
    return InlineKeyboardMarkup(rows)


USAGE_TEXT = (
    "CHERRY Staff AI — reply translator\n\n"
    "1) Paste or forward a customer message → bot shows language + meaning\n"
    "2) ✍️ Staff Reply → you type your answer\n"
    "3) AI translates/cleans to customer language — you copy or send\n\n"
    "Optional: forward from customer (for Send to Customer) or add Telegram ID in text\n"
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


def bind_staff_reply_wait(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    case: dict[str, Any],
) -> dict[str, Any]:
    payload = set_awaiting_staff_reply(chat_id, user_id, case)
    context.user_data["staff_ai_awaiting"] = True
    context.user_data["staff_ai_case"] = payload
    awaiting = context.application.bot_data.setdefault("staff_ai_awaiting", {})
    awaiting[_await_key(chat_id, user_id)] = payload
    save_active_case(context, payload)
    return payload


def clear_staff_reply_wait(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    *,
    prompt_id: int | None = None,
) -> None:
    clear_awaiting_staff_reply(chat_id, user_id)
    context.user_data.pop("staff_ai_awaiting", None)
    context.user_data.pop("staff_ai_case", None)
    awaiting = context.application.bot_data.get("staff_ai_awaiting", {})
    awaiting.pop(_await_key(chat_id, user_id), None)
    if prompt_id is not None:
        _PROMPT_TO_CASE.pop(prompt_id, None)


def resolve_pending_staff_case(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> dict[str, Any] | None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return None

    reply_to = message.reply_to_message
    if reply_to and reply_to.message_id in _PROMPT_TO_CASE:
        case = dict(_PROMPT_TO_CASE.pop(reply_to.message_id))
        logger.info("staff reply matched prompt_id=%s user=%s", reply_to.message_id, user.id)
        return case

    pending = get_awaiting_staff_reply(chat.id, user.id)
    if pending:
        logger.info("staff reply matched memory user=%s lang=%s", user.id, pending.get("language_name"))
        return pending

    bot_awaiting = context.application.bot_data.get("staff_ai_awaiting", {})
    mem = bot_awaiting.get(_await_key(chat.id, user.id))
    if isinstance(mem, dict) and mem.get("awaiting_staff_reply"):
        logger.info("staff reply matched bot_data user=%s", user.id)
        return dict(mem)

    if context.user_data.get("staff_ai_awaiting") and isinstance(context.user_data.get("staff_ai_case"), dict):
        case = dict(context.user_data["staff_ai_case"])
        if case.get("staff_reply_user_id") == user.id:
            logger.info("staff reply matched user_data user=%s", user.id)
            return case

    stored = context.chat_data.get(ACTIVE_CASE_KEY)
    if (
        isinstance(stored, dict)
        and stored.get("awaiting_staff_reply")
        and stored.get("staff_reply_user_id") == user.id
    ):
        logger.info("staff reply matched chat_data user=%s", user.id)
        return dict(stored)

    return None


def save_active_case(context: ContextTypes.DEFAULT_TYPE, case: dict[str, Any]) -> None:
    context.chat_data[ACTIVE_CASE_KEY] = case


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

    prompt_id = stored.get("staff_reply_prompt_id")
    if chat and user:
        clear_staff_reply_wait(
            context,
            chat.id,
            user.id,
            prompt_id=int(prompt_id) if prompt_id else None,
        )

    try:
        await message.chat.send_action("typing")
        draft = await asyncio.to_thread(
            draft_staff_translation,
            staff_text,
            customer_language=str(stored.get("detected_language", "") or ""),
            language_name=str(stored.get("language_name", "") or "Unknown"),
            customer_original=str(stored.get("question", "") or ""),
        )
        stored["customer_reply"] = draft.customer_reply
        stored["staff_reply_meaning"] = draft.staff_meaning
        card = format_reply_check_card(draft)
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
        "staff_reply_meaning": "",
        "customer_reply": "",
        "reply_source": "staff",
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
        reply_markup=stage2_keyboard(
            copy_text=str(stored.get("customer_reply", "") or ""),
            show_send=show_send_button(stored),
        ),
    )
    stored["reply_message_id"] = sent.message_id
    save_active_case(context, stored)


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

    pending = resolve_pending_staff_case(update, context)
    if pending:
        await process_staff_reply_input(
            update,
            context,
            stored=pending,
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
    stored = context.chat_data.get(ACTIVE_CASE_KEY)
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
            clear_staff_reply_wait(context, query.message.chat_id, query.from_user.id)
        context.chat_data.pop(ACTIVE_CASE_KEY, None)
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

    if action == "staff_reply":
        if not query.message or not query.from_user:
            if query.message:
                await query.message.reply_text("Could not start Staff Reply — try again.")
            return
        payload = bind_staff_reply_wait(
            context,
            query.message.chat_id,
            query.from_user.id,
            stored,
        )
        sent = await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=STAFF_REPLY_PROMPT,
            reply_markup=ForceReply(selective=True),
            reply_to_message_id=query.message.message_id,
        )
        payload["staff_reply_prompt_id"] = sent.message_id
        _PROMPT_TO_CASE[sent.message_id] = dict(payload)
        save_active_case(context, payload)
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
    staff_wrote = str(stored.get("staff_wrote", "") or "").strip()
    if not previous or not staff_wrote:
        await query.message.reply_text("Press ✍️ Staff Reply and type your answer first.")
        return

    await query.message.chat.send_action("typing")
    mode = "rewrite" if action == "rewrite" else "shorter"
    label = "Rewrite" if action == "rewrite" else "Shorter"

    draft = await asyncio.to_thread(
        draft_staff_translation,
        staff_wrote,
        customer_language=str(stored.get("detected_language", "") or ""),
        language_name=str(stored.get("language_name", "") or "Unknown"),
        customer_original=question,
        mode=mode,
        previous_reply=previous,
    )
    stored["customer_reply"] = draft.customer_reply
    stored["staff_reply_meaning"] = draft.staff_meaning
    card = format_reply_check_card(draft, mode_label=label)

    await send_stage2_reply(
        message=query.message,
        context=context,
        stored=stored,
        card=card,
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

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    persistence = PicklePersistence(filepath=str(STATE_PATH))

    app = (
        Application.builder()
        .token(token)
        .persistence(persistence)
        .concurrent_updates(True)
        .build()
    )
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
