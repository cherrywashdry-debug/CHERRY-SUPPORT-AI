"""CHERRY Staff AI — translator only (V3 final).

AI does exactly 2 jobs:
  1) Explain customer message for staff (Meaning for Staff)
  2) Translate staff reply for customer (Customer Reply)

No suggested replies. No shop knowledge. No billing. No V3 logic.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import uuid
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

VERSION = "CHERRY STAFF AI - TRANSLATOR-V4-MENU-BUTTONS-R2"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"
KNOWLEDGE_PATH = ROOT / "CHERRY_KNOWLEDGE.md"
if not KNOWLEDGE_PATH.is_file():
    KNOWLEDGE_PATH = ROOT.parent / "CHERRY_KNOWLEDGE.md"
ACTIVE_CASE_KEY = "staff_ai_active_case"
STAFF_REPLY_GATE_KEY = "staff_ai_reply_gate"
STAFF_REPLY_HANDLED_MSG_KEY = "staff_ai_handled_message_id"
STAFF_LANG_USER_KEY = "staff_lang"
STAFF_LANG_SET_KEY = "staff_lang_set"
CUSTOMER_ASK_MODE_KEY = "customer_ask_mode"
DEFAULT_STAFF_LANG = "km"
STAFF_LANG_OPTIONS: dict[str, str] = {
    "km": "Khmer",
    "th": "Thai",
    "id": "Indonesian",
}
STAFF_LANG_LABELS: dict[str, str] = {
    "km": "🇰🇭 Khmer",
    "th": "🇹🇭 Thai",
    "id": "🇮🇩 Indonesian",
}
# In-memory fallback between webhook requests (same process).
_AWAITING_STAFF_REPLY: dict[str, dict[str, Any]] = {}
_STAFF_REPLY_GATE: dict[str, dict[str, Any]] = {}
_PROMPT_TO_CASE: dict[int, dict[str, Any]] = {}

FALLBACK_COPY = "(empty)"


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
    "✍️ Staff Reply — type your answer for the customer.\n"
    "Use Thai, Khmer, English, or Indonesian.\n"
    "AI translates only. It will not add new information."
)

CUSTOMER_ASK_PROMPT = (
    "📩 Customer Asked — paste the customer message below.\n"
    "Bot will detect customer language and explain in your language."
)

MENU_HINT = "Choose a button below:"

REPLY_CHECK_FOOTER = "⚠️ Please check carefully before sending."

KHMER_SCRIPT_RE = re.compile(r"[\u1780-\u17FF]")
THAI_SCRIPT_RE = re.compile(r"[\u0E00-\u0E7F]")


def looks_like_khmer(text: str) -> bool:
    return bool(KHMER_SCRIPT_RE.search(str(text or "")))


def looks_like_thai(text: str) -> bool:
    return bool(THAI_SCRIPT_RE.search(str(text or "")))


def normalize_staff_lang(code: str) -> str:
    key = str(code or "").strip().lower()
    return key if key in STAFF_LANG_OPTIONS else DEFAULT_STAFF_LANG


def get_staff_language(context: ContextTypes.DEFAULT_TYPE) -> tuple[str, str]:
    code = normalize_staff_lang(str(context.user_data.get(STAFF_LANG_USER_KEY, DEFAULT_STAFF_LANG)))
    return code, STAFF_LANG_OPTIONS[code]


def set_staff_language(context: ContextTypes.DEFAULT_TYPE, code: str) -> tuple[str, str]:
    normalized = normalize_staff_lang(code)
    context.user_data[STAFF_LANG_USER_KEY] = normalized
    context.user_data[STAFF_LANG_SET_KEY] = True
    return normalized, STAFF_LANG_OPTIONS[normalized]


def staff_language_is_set(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get(STAFF_LANG_SET_KEY))


def set_customer_ask_mode(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    context.user_data[CUSTOMER_ASK_MODE_KEY] = True
    context.user_data["customer_ask_user_id"] = int(user_id)


def clear_customer_ask_mode(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(CUSTOMER_ASK_MODE_KEY, None)
    context.user_data.pop("customer_ask_user_id", None)


def customer_ask_mode_active(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    if not context.user_data.get(CUSTOMER_ASK_MODE_KEY):
        return False
    stored_uid = _coerce_user_id(context.user_data.get("customer_ask_user_id"))
    return stored_uid is None or stored_uid == user_id


def staff_meaning_label(staff_lang_code: str) -> str:
    name = STAFF_LANG_OPTIONS.get(normalize_staff_lang(staff_lang_code), "Khmer")
    return f"👀 Meaning for Staff ({name})"


def staff_meaning_ok(text: str, staff_lang: str) -> bool:
    cleaned = str(text or "").strip()
    if not cleaned or cleaned == "—":
        return False
    lang = normalize_staff_lang(staff_lang)
    if lang == "km":
        return looks_like_khmer(cleaned)
    if lang == "th":
        return looks_like_thai(cleaned)
    if lang == "id":
        return not looks_like_khmer(cleaned) and not looks_like_thai(cleaned)
    return True


def google_translate_rules() -> str:
    return (
        "Translate like Google Translate.\n"
        "Use simple everyday words. Be direct and short.\n"
        "No formal language. No difficult words. No extra sentences.\n"
        "Do NOT add information that is not in the source text."
    )


def new_support_id() -> str:
    return uuid.uuid4().hex[:8]


def normalize_case(case: dict[str, Any], *, chat_id: int | None = None) -> dict[str, Any]:
    payload = dict(case)
    if not str(payload.get("support_id", "") or "").strip():
        payload["support_id"] = new_support_id()
    question = str(payload.get("question", "") or payload.get("original_customer_message", "") or "").strip()
    payload["question"] = question
    payload["original_customer_message"] = question
    if chat_id is not None:
        payload["chat_id"] = chat_id
    payload.setdefault("staff_reply_mode", False)
    payload.setdefault("awaiting_staff_reply", False)
    return payload


def _coerce_user_id(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _same_user(stored_id: Any, user_id: int) -> bool:
    left = _coerce_user_id(stored_id)
    right = _coerce_user_id(user_id)
    return left is not None and right is not None and left == right


def case_is_staff_reply_wait(case: dict[str, Any], *, user_id: int) -> bool:
    if not bool(case.get("staff_reply_mode") or case.get("awaiting_staff_reply")):
        return False
    stored_uid = case.get("staff_reply_user_id")
    if stored_uid is None:
        return True
    return _same_user(stored_uid, user_id)


def looks_like_staff_language(text: str) -> bool:
    raw = str(text or "")
    return looks_like_khmer(raw) or looks_like_thai(raw)


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


def build_understand_system_prompt(*, staff_language_name: str) -> str:
    return (
        "You are Google Translate for CHERRY Wash & Dry shop staff.\n"
        f"Staff read {staff_language_name}. Translate the customer message into {staff_language_name}.\n"
        "Your ONLY job: say what the customer means in simple words.\n"
        "Do NOT answer the customer. Do NOT suggest a reply. Do NOT add shop knowledge.\n\n"
        f"{google_translate_rules()}\n\n"
        "Detect the customer language from short, typo, or romanized text.\n\n"
        "Return JSON with exactly these keys:\n"
        "  detected_language — short code (en, th, km, id, tl, ms, zh, vi, ...)\n"
        "  language_name — readable name (e.g. English, Indonesian)\n"
        f"  staff_meaning — 1–2 SHORT lines in {staff_language_name} ONLY.\n"
        "    Plain words. Say what the customer asked or said.\n"
        "    Do NOT add price, time, policy, discount, promise, or apology.\n"
    )


def build_understand_user_prompt(customer_text: str, *, staff_language_name: str) -> str:
    lang_hints = language_hints_for_text(customer_text)
    hint_block = ""
    if lang_hints:
        hint_block = "Language hints:\n" + "\n".join(f"- {h}" for h in lang_hints) + "\n\n"
    return (
        f"{hint_block}"
        f"Customer message:\n{customer_text.strip() or '(empty)'}\n\n"
        f"Translate/explain in simple {staff_language_name} for staff. Do not draft a customer reply."
    )


def clamp_customer_reply(text: str, *, max_words: int = 40, max_chars: int = 240) -> str:
    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return ""
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


def draft_staff_reply_meaning(
    *,
    staff_wrote: str,
    customer_reply: str,
    staff_language_name: str,
) -> str:
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
                        f"Explain for shop staff in {staff_language_name} ONLY (1-2 short lines).\n"
                        "Summarize what the customer_reply will tell the customer.\n"
                        f"{google_translate_rules()}\n"
                        "Do NOT add price, time, policy, discount, promise, or apology."
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
        return str(parse_llm_json(raw).get("staff_meaning", "") or "").strip() or "—"
    except Exception:
        logger.exception("Staff reply meaning repair failed")
    return "—"


def ensure_staff_reply_meaning(
    draft: StaffTranslationDraft,
    *,
    staff_lang: str,
    staff_language_name: str,
) -> StaffTranslationDraft:
    if staff_meaning_ok(draft.staff_meaning, staff_lang):
        return draft
    repaired = draft_staff_reply_meaning(
        staff_wrote=draft.staff_wrote,
        customer_reply=draft.customer_reply,
        staff_language_name=staff_language_name,
    )
    return StaffTranslationDraft(
        staff_wrote=draft.staff_wrote,
        language_name=draft.language_name,
        customer_reply=draft.customer_reply,
        staff_meaning=repaired,
    )


def draft_understand(
    customer_text: str,
    *,
    staff_language: str,
    staff_language_name: str,
) -> StaffUnderstanding:
    client = openai_client()
    if not client:
        return StaffUnderstanding("?", "Unknown", "⚠️ OPENAI_API_KEY not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=140,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": build_understand_system_prompt(staff_language_name=staff_language_name),
                },
                {
                    "role": "user",
                    "content": build_understand_user_prompt(
                        customer_text,
                        staff_language_name=staff_language_name,
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        return understanding_from_payload(parse_llm_json(raw))
    except Exception as exc:
        logger.exception("OpenAI understand failed")
        return StaffUnderstanding("?", "Unknown", f"⚠️ {openai_error_hint(exc)}")


def build_translate_system_prompt() -> str:
    return (
        "You are Google Translate for CHERRY Wash & Dry customers.\n"
        "Translator only. Do NOT answer for staff. Do NOT add shop knowledge.\n\n"
        f"{google_translate_rules()}\n\n"
        "RULES:\n"
        "- translated_reply: customer language ONLY. Simple, direct, easy to copy.\n"
        "- staff_meaning: 1–2 short lines in the staff language — what the customer will read.\n"
        "- Keep the same meaning as staff wrote. Light grammar cleanup only.\n"
        "- Do NOT invent anything.\n"
        "- Do NOT add price, time, policy, discount, promise, or apology unless staff wrote it.\n"
        "- Never put staff-language text in translated_reply unless that IS the customer language.\n\n"
        "Return JSON keys: translated_reply, staff_meaning"
    )


def build_translate_user_prompt(
    staff_text: str,
    *,
    customer_language: str,
    language_name: str,
    staff_language_name: str,
    customer_original: str = "",
) -> str:
    context_block = ""
    if customer_original.strip():
        context_block = f"Original customer message (context only, do not answer it):\n{customer_original.strip()}\n\n"
    target = f"Target customer language: {language_name} ({customer_language})\n\n"
    lang_rule = (
        f"translated_reply MUST be in {language_name} only — simple everyday words.\n"
        "Do NOT output staff language unless that is the customer language.\n\n"
    )
    return (
        f"{context_block}{target}{lang_rule}"
        f"Staff wrote:\n{staff_text}\n\n"
        f"Translate to {language_name} for the customer.\n"
        f"staff_meaning in {staff_language_name} so staff can verify before sending."
    )


def translation_from_payload(payload: dict[str, Any]) -> str:
    return clamp_customer_reply(
        str(payload.get("translated_reply", "") or payload.get("customer_reply", "") or ""),
    )


def translation_draft_from_payload(
    payload: dict[str, Any],
    *,
    staff_text: str,
    language_name: str,
) -> StaffTranslationDraft:
    customer_reply = translation_from_payload(payload) or staff_text
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
    staff_language: str,
    staff_language_name: str,
    customer_original: str = "",
) -> StaffTranslationDraft:
    client = openai_client()
    if not client:
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            customer_reply=staff_text,
            staff_meaning="⚠️ OPENAI_API_KEY not set",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=220,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_translate_system_prompt()},
                {
                    "role": "user",
                    "content": build_translate_user_prompt(
                        staff_text,
                        customer_language=customer_language,
                        language_name=language_name,
                        staff_language_name=staff_language_name,
                        customer_original=customer_original,
                    ),
                },
            ],
        )
        raw = response.choices[0].message.content or "{}"
        draft = translation_draft_from_payload(
            parse_llm_json(raw),
            staff_text=staff_text,
            language_name=language_name,
        )
        if not draft.customer_reply:
            draft = StaffTranslationDraft(
                staff_wrote=staff_text,
                language_name=language_name,
                customer_reply=staff_text,
                staff_meaning=draft.staff_meaning,
            )
        return ensure_staff_reply_meaning(
            draft,
            staff_lang=staff_language,
            staff_language_name=staff_language_name,
        )
    except Exception as exc:
        logger.exception("OpenAI staff translation failed")
        return StaffTranslationDraft(
            staff_wrote=staff_text,
            language_name=language_name,
            customer_reply=f"⚠️ {openai_error_hint(exc)}",
            staff_meaning="—",
        )


def format_stage1_card(
    original_text: str,
    understanding: StaffUnderstanding,
    *,
    staff_lang_code: str,
) -> str:
    original_block = original_text.strip() or "(no text)"
    customer_lang = understanding.language_name.strip() or "Unknown"
    return "\n".join([
        "📩 Customer Message",
        original_block,
        "",
        f"🌐 Customer language: {customer_lang}",
        "",
        staff_meaning_label(staff_lang_code),
        understanding.staff_meaning,
    ])


def format_reply_check_card(draft: StaffTranslationDraft, *, staff_lang_code: str) -> str:
    return "\n".join([
        staff_meaning_label(staff_lang_code),
        draft.staff_meaning or "—",
        "",
        f"💬 Customer Reply ({draft.language_name})",
        draft.customer_reply,
        "",
        REPLY_CHECK_FOOTER,
    ])


def main_menu_keyboard(*, staff_lang_code: str) -> InlineKeyboardMarkup:
    lang_name = STAFF_LANG_OPTIONS.get(staff_lang_code, "Khmer")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"🌐 My Language: {lang_name}",
            callback_data="staffai:lang_menu",
        )],
        [InlineKeyboardButton(
            "📩 Customer Asked / អតិថិជនសួរ",
            callback_data="staffai:customer_ask",
        )],
        [InlineKeyboardButton(
            "✍️ Staff Reply / បុគ្គលិកឆ្លើយ",
            callback_data="staffai:staff_reply",
        )],
    ])


def stage1_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Staff Reply / បុគ្គលិកឆ្លើយ", callback_data="staffai:staff_reply")],
        [InlineKeyboardButton("📩 New Customer / អតិថិជនថ្មី", callback_data="staffai:customer_ask")],
        [InlineKeyboardButton("🏠 Menu / ម៉ឺនុយ", callback_data="staffai:main_menu")],
    ])


def staff_lang_keyboard(current_code: str, *, first_time: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for code, name in STAFF_LANG_OPTIONS.items():
        mark = " ✓" if code == current_code else ""
        label = STAFF_LANG_LABELS.get(code, name)
        rows.append([
            InlineKeyboardButton(
                f"{label}{mark}",
                callback_data=f"staffai:lang:{code}",
            ),
        ])
    if not first_time:
        rows.append([InlineKeyboardButton("🏠 Menu / ម៉ឺនុយ", callback_data="staffai:main_menu")])
    return InlineKeyboardMarkup(rows)


def copy_text_for_button(text: str, *, max_len: int = 256) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return FALLBACK_COPY
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 1].rstrip() + "…"


def stage2_keyboard(*, copy_text: str = "", show_send: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if copy_text.strip():
        rows.append([
            InlineKeyboardButton(
                "📋 Copy / ចម្លង",
                copy_text=CopyTextButton(text=copy_text_for_button(copy_text)),
            ),
        ])
    if show_send:
        rows.append([
            InlineKeyboardButton("✅ Send Customer / ផ្ញើអតិថិជន", callback_data="staffai:send"),
        ])
    rows.append([InlineKeyboardButton("❌ Cancel / បោះបង់", callback_data="staffai:cancel_reply")])
    return InlineKeyboardMarkup(rows)


USAGE_TEXT = (
    "CHERRY Staff AI — Google Translate for staff\n\n"
    "Step 1: Choose YOUR language (Khmer / Thai / Indonesian)\n"
    "Step 2: Press 📩 Customer Asked → paste customer message\n"
    "Step 3: Press ✍️ Staff Reply → type your answer\n"
    "Step 4: Check meaning + customer reply → Copy or Send\n\n"
    "Commands: /menu /lang /health\n"
    "AI only translates. Simple words. No invented answers."
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


async def send_lang_picker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    first_time: bool = False,
) -> None:
    code, _ = get_staff_language(context)
    text = (
        "Choose YOUR language first:\n"
        "Khmer / Thai / Indonesian"
        if first_time
        else f"Your language: {STAFF_LANG_OPTIONS[code]}\nChoose language for Meaning for Staff:"
    )
    target = update.message or update.callback_query.message
    if target:
        await target.reply_text(
            text,
            reply_markup=staff_lang_keyboard(code, first_time=first_time),
        )


async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not staff_language_is_set(context):
        await send_lang_picker(update, context, first_time=True)
        return
    code, name = get_staff_language(context)
    target = update.message or (update.callback_query.message if update.callback_query else None)
    if target:
        await target.reply_text(
            f"Your language: {name}\n{MENU_HINT}",
            reply_markup=main_menu_keyboard(staff_lang_code=code),
        )


async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update) or not update.message:
        return
    await send_lang_picker(update, context, first_time=not staff_language_is_set(context))


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        return
    await send_main_menu(update, context)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        await update.message.reply_text("This bot is for CHERRY staff only.")
        return
    if is_setup_mode():
        await update.message.reply_text(f"{SETUP_HINT}\n\n{USAGE_TEXT}")
    else:
        await update.message.reply_text(USAGE_TEXT)
    if not staff_language_is_set(context):
        await send_lang_picker(update, context, first_time=True)
    else:
        await send_main_menu(update, context)


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
    return f"{int(chat_id)}:{int(user_id)}"


def _reply_gate(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    return context.application.bot_data.setdefault(STAFF_REPLY_GATE_KEY, {})


def _set_reply_gate(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    case: dict[str, Any],
) -> None:
    key = _await_key(chat_id, user_id)
    payload = dict(case)
    _STAFF_REPLY_GATE[key] = payload
    _reply_gate(context)[key] = payload


def _pop_reply_gate(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> None:
    key = _await_key(chat_id, user_id)
    _STAFF_REPLY_GATE.pop(key, None)
    _reply_gate(context).pop(key, None)


def set_awaiting_staff_reply(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    case: dict[str, Any],
) -> dict[str, Any]:
    payload = normalize_case(case, chat_id=chat_id)
    payload["staff_reply_mode"] = True
    payload["awaiting_staff_reply"] = True
    payload["staff_reply_user_id"] = int(user_id)
    payload["active_support_id"] = payload.get("support_id")
    key = _await_key(chat_id, user_id)
    _AWAITING_STAFF_REPLY[key] = payload
    _set_reply_gate(context, chat_id, user_id, payload)
    logger.info(
        "STAFF_REPLY_MODE_ENTER chat=%s user=%s support_id=%s lang=%s gate=%s",
        chat_id,
        user_id,
        payload.get("support_id"),
        payload.get("language_name"),
        key,
    )
    return payload


def get_awaiting_staff_reply(chat_id: int, user_id: int) -> dict[str, Any] | None:
    pending = _AWAITING_STAFF_REPLY.get(_await_key(chat_id, user_id))
    return dict(pending) if isinstance(pending, dict) else None


def clear_awaiting_staff_reply(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> None:
    key = _await_key(chat_id, user_id)
    _AWAITING_STAFF_REPLY.pop(key, None)
    _STAFF_REPLY_GATE.pop(key, None)
    _reply_gate(context).pop(key, None)


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
    payload = set_awaiting_staff_reply(context, chat_id, user_id, case)
    context.user_data["staff_ai_awaiting"] = True
    context.user_data["staff_ai_case"] = payload
    awaiting = context.application.bot_data.setdefault("staff_ai_awaiting", {})
    awaiting[_await_key(chat_id, user_id)] = payload
    save_active_case(context, payload, chat_id=chat_id)
    return payload


def clear_staff_reply_wait(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
    *,
    prompt_id: int | None = None,
    log_exit: bool = True,
) -> None:
    key = _await_key(chat_id, user_id)
    gate_case = _STAFF_REPLY_GATE.get(key) or _reply_gate(context).get(key)
    clear_awaiting_staff_reply(context, chat_id, user_id)
    context.user_data.pop("staff_ai_awaiting", None)
    context.user_data.pop("staff_ai_case", None)
    awaiting = context.application.bot_data.get("staff_ai_awaiting", {})
    awaiting.pop(key, None)
    if prompt_id is not None:
        _PROMPT_TO_CASE.pop(prompt_id, None)
        context.application.bot_data.get("staff_ai_prompts", {}).pop(str(prompt_id), None)
    stored = context.chat_data.get(ACTIVE_CASE_KEY)
    if isinstance(stored, dict) and stored.get("chat_id") == chat_id:
        stored = dict(stored)
        stored["staff_reply_mode"] = False
        stored["awaiting_staff_reply"] = False
        stored["staff_reply_user_id"] = None
        save_active_case(context, stored, chat_id=chat_id)
    if log_exit:
        logger.info(
            "STAFF_REPLY_MODE_EXIT chat=%s user=%s support_id=%s",
            chat_id,
            user_id,
            (gate_case or {}).get("support_id"),
        )


def find_staff_reply_case(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> dict[str, Any] | None:
    key = _await_key(chat_id, user_id)

    gate = _STAFF_REPLY_GATE.get(key)
    if isinstance(gate, dict) and case_is_staff_reply_wait(gate, user_id=user_id):
        logger.info("staff reply gate=memory support_id=%s", gate.get("support_id"))
        return dict(gate)

    persisted_gate = _reply_gate(context).get(key)
    if isinstance(persisted_gate, dict) and case_is_staff_reply_wait(persisted_gate, user_id=user_id):
        logger.info("staff reply gate=bot_data support_id=%s", persisted_gate.get("support_id"))
        return dict(persisted_gate)

    pending = get_awaiting_staff_reply(chat_id, user_id)
    if pending and case_is_staff_reply_wait(pending, user_id=user_id):
        logger.info("staff reply gate=awaiting support_id=%s", pending.get("support_id"))
        return pending

    bot_awaiting = context.application.bot_data.get("staff_ai_awaiting", {})
    mem = bot_awaiting.get(key)
    if isinstance(mem, dict) and case_is_staff_reply_wait(mem, user_id=user_id):
        logger.info("staff reply gate=bot_awaiting support_id=%s", mem.get("support_id"))
        return dict(mem)

    stored = context.chat_data.get(ACTIVE_CASE_KEY)
    if isinstance(stored, dict) and case_is_staff_reply_wait(stored, user_id=user_id):
        logger.info("staff reply gate=chat_data support_id=%s", stored.get("support_id"))
        return dict(stored)

    by_chat = context.application.bot_data.get("staff_ai_by_chat", {})
    chat_case = by_chat.get(str(chat_id))
    if isinstance(chat_case, dict) and case_is_staff_reply_wait(chat_case, user_id=user_id):
        logger.info("staff reply gate=by_chat support_id=%s", chat_case.get("support_id"))
        return dict(chat_case)

    if context.user_data.get("staff_ai_awaiting") and isinstance(context.user_data.get("staff_ai_case"), dict):
        case = dict(context.user_data["staff_ai_case"])
        if case_is_staff_reply_wait(case, user_id=user_id):
            logger.info("staff reply gate=user_data support_id=%s", case.get("support_id"))
            return case

    return None


def get_active_case(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> dict[str, Any] | None:
    stored = context.chat_data.get(ACTIVE_CASE_KEY)
    if isinstance(stored, dict) and str(stored.get("question", "") or "").strip():
        return dict(stored)
    by_chat = context.application.bot_data.get("staff_ai_by_chat", {})
    fallback = by_chat.get(str(chat_id))
    if isinstance(fallback, dict) and str(fallback.get("question", "") or "").strip():
        return dict(fallback)
    return None


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
        case = dict(_PROMPT_TO_CASE[reply_to.message_id])
        logger.info(
            "staff reply matched prompt_id=%s user=%s support_id=%s",
            reply_to.message_id,
            user.id,
            case.get("support_id"),
        )
        return case

    prompts = context.application.bot_data.get("staff_ai_prompts", {})
    prompt_key = prompts.get(str(getattr(reply_to, "message_id", "")))
    if reply_to and prompt_key:
        awaiting = context.application.bot_data.get("staff_ai_awaiting", {})
        mem = awaiting.get(prompt_key)
        if isinstance(mem, dict) and case_is_staff_reply_wait(mem, user_id=user.id):
            logger.info("staff reply matched persisted prompt user=%s", user.id)
            return dict(mem)

    gate_case = find_staff_reply_case(context, chat.id, user.id)
    if gate_case:
        return gate_case

    return None


def save_active_case(
    context: ContextTypes.DEFAULT_TYPE,
    case: dict[str, Any],
    *,
    chat_id: int | None = None,
) -> None:
    cid = chat_id if chat_id is not None else case.get("chat_id")
    payload = normalize_case(case, chat_id=cid if isinstance(cid, int) else None)
    context.chat_data[ACTIVE_CASE_KEY] = payload
    if isinstance(cid, int):
        context.application.bot_data.setdefault("staff_ai_by_chat", {})[str(cid)] = payload
    uid = _coerce_user_id(payload.get("staff_reply_user_id"))
    if payload.get("staff_reply_mode") and isinstance(cid, int) and uid is not None:
        key = _await_key(cid, uid)
        context.application.bot_data.setdefault("staff_ai_awaiting", {})[key] = payload
        _set_reply_gate(context, cid, uid, payload)


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
    support_id = stored.get("support_id")
    logger.info(
        "STAFF_REPLY_INPUT_RECEIVED chat=%s user=%s support_id=%s text=%r lang=%s",
        getattr(chat, "id", None),
        getattr(user, "id", None),
        support_id,
        staff_text[:120],
        stored.get("language_name"),
    )

    stored = dict(stored)
    stored["staff_reply_mode"] = False
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
            log_exit=False,
        )

    customer_lang = str(stored.get("detected_language", "") or stored.get("detected_customer_language", "") or "")
    customer_lang_name = str(stored.get("language_name", "") or "Unknown")
    customer_original = str(
        stored.get("original_customer_message", "") or stored.get("question", "") or ""
    )
    staff_lang = normalize_staff_lang(str(stored.get("staff_lang", DEFAULT_STAFF_LANG)))
    staff_lang_name = str(stored.get("staff_lang_name", "") or STAFF_LANG_OPTIONS[staff_lang])
    if user:
        staff_lang, staff_lang_name = get_staff_language(context)
        stored["staff_lang"] = staff_lang
        stored["staff_lang_name"] = staff_lang_name

    try:
        await message.chat.send_action("typing")
        draft = await asyncio.to_thread(
            draft_staff_translation,
            staff_text,
            customer_language=customer_lang,
            language_name=customer_lang_name,
            staff_language=staff_lang,
            staff_language_name=staff_lang_name,
            customer_original=customer_original,
        )
        logger.info(
            "STAFF_REPLY_TRANSLATED support_id=%s customer_lang=%s reply=%r",
            support_id,
            customer_lang_name,
            draft.customer_reply[:120],
        )
        stored["customer_reply"] = draft.customer_reply
        stored["staff_reply_meaning"] = draft.staff_meaning
        card = format_reply_check_card(draft, staff_lang_code=staff_lang)
        await send_stage2_reply(message=message, context=context, stored=stored, card=card)
        if chat and user:
            logger.info(
                "STAFF_REPLY_MODE_EXIT chat=%s user=%s support_id=%s",
                chat.id,
                user.id,
                support_id,
            )
    except Exception:
        logger.exception("staff reply translation failed support_id=%s", support_id)
        await message.reply_text("⚠️ Could not translate. Try again or send /health.")


def new_case_payload(
    *,
    question: str,
    understanding: StaffUnderstanding,
    telegram_id: int | None,
    order_id: str,
    stage1_message_id: int,
    staff_lang: str,
    staff_lang_name: str,
) -> dict[str, Any]:
    return normalize_case({
        "question": question,
        "original_customer_message": question,
        "detected_language": understanding.detected_language,
        "detected_customer_language": understanding.detected_language,
        "language_name": understanding.language_name,
        "staff_meaning": understanding.staff_meaning,
        "staff_lang": staff_lang,
        "staff_lang_name": staff_lang_name,
        "staff_reply_meaning": "",
        "customer_reply": "",
        "reply_source": "staff",
        "staff_wrote": "",
        "staff_reply_mode": False,
        "awaiting_staff_reply": False,
        "staff_reply_user_id": None,
        "stage1_message_id": stage1_message_id,
        "reply_message_id": None,
        "telegram_id": telegram_id,
        "order_id": order_id,
    })


async def send_stage2_reply(
    *,
    message: Any,
    context: ContextTypes.DEFAULT_TYPE,
    stored: dict[str, Any],
    card: str,
) -> None:
    sent = await message.reply_text(
        card,
        reply_markup=stage2_keyboard(
            copy_text=str(stored.get("customer_reply", "") or ""),
            show_send=show_send_button(stored),
        ),
    )
    stored["reply_message_id"] = sent.message_id
    save_active_case(context, stored, chat_id=stored.get("chat_id"))


async def process_customer_ask_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    text: str,
    telegram_id: int | None,
    order_id: str,
) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return

    clear_customer_ask_mode(context)
    staff_lang, staff_lang_name = get_staff_language(context)

    try:
        await message.chat.send_action("typing")
        understanding = await asyncio.to_thread(
            draft_understand,
            text,
            staff_language=staff_lang,
            staff_language_name=staff_lang_name,
        )
        card = format_stage1_card(text, understanding, staff_lang_code=staff_lang)
        sent = await message.reply_text(card, reply_markup=stage1_keyboard())
        save_active_case(
            context,
            new_case_payload(
                question=text,
                understanding=understanding,
                telegram_id=telegram_id,
                order_id=order_id,
                stage1_message_id=sent.message_id,
                staff_lang=staff_lang,
                staff_lang_name=staff_lang_name,
            ),
            chat_id=chat.id,
        )
    except Exception:
        logger.exception("process_customer_ask_input failed for text=%r", text[:120])
        await message.reply_text("⚠️ Could not translate. Send /health to check OpenAI.")


async def handle_staff_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Only process text after staff pressed 📩 Customer Asked or ✍️ Staff Reply."""
    if not is_staff_chat(update):
        return
    message = update.effective_message
    if not message or not message.text:
        if message and message.caption:
            await message.reply_text("Please paste text, not photo.")
        return

    raw_text = message.text.strip()
    if raw_text.startswith("/"):
        return

    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return

    if not staff_language_is_set(context):
        await send_lang_picker(update, context, first_time=True)
        return

    pending = resolve_pending_staff_case(update, context)
    if pending:
        await process_staff_reply_input(
            update,
            context,
            stored=pending,
            staff_text=raw_text,
        )
        return

    if find_staff_reply_case(context, chat.id, user.id):
        return

    if customer_ask_mode_active(context, user.id):
        text, telegram_id, order_id = extract_message_context(message)
        if not text:
            await message.reply_text("Paste the customer message text.")
            return
        if is_setup_mode():
            await message.reply_text(SETUP_HINT)
            return
        await process_customer_ask_input(
            update,
            context,
            text=text,
            telegram_id=telegram_id,
            order_id=order_id,
        )
        return

    code, name = get_staff_language(context)
    await message.reply_text(
        f"Press a button first.\nYour language: {name}\n{MENU_HINT}",
        reply_markup=main_menu_keyboard(staff_lang_code=code),
    )


async def staff_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_staff_chat(update) or not query.message or not query.from_user:
        return

    action = (query.data or "").split(":", 1)[-1]
    chat_id = query.message.chat_id
    user_id = query.from_user.id

    if action == "main_menu":
        await send_main_menu(update, context)
        return

    if action == "lang_menu":
        await send_lang_picker(update, context, first_time=not staff_language_is_set(context))
        return

    if action.startswith("lang:"):
        picked = action.split(":", 1)[1]
        code, name = set_staff_language(context, picked)
        clear_customer_ask_mode(context)
        await query.message.reply_text(
            f"Your language: {name}\n{MENU_HINT}",
            reply_markup=main_menu_keyboard(staff_lang_code=code),
        )
        return

    if action == "customer_ask":
        if not staff_language_is_set(context):
            await send_lang_picker(update, context, first_time=True)
            return
        clear_staff_reply_wait(context, chat_id, user_id, log_exit=False)
        set_customer_ask_mode(context, user_id)
        code, _ = get_staff_language(context)
        await query.message.reply_text(
            CUSTOMER_ASK_PROMPT,
            reply_markup=main_menu_keyboard(staff_lang_code=code),
        )
        return

    if action == "cancel":
        clear_staff_reply_wait(context, chat_id, user_id)
        clear_customer_ask_mode(context)
        context.chat_data.pop(ACTIVE_CASE_KEY, None)
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        code, _ = get_staff_language(context)
        await query.message.reply_text(
            "Cancelled.",
            reply_markup=main_menu_keyboard(staff_lang_code=code),
        )
        return

    if action == "cancel_reply":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        code, _ = get_staff_language(context)
        await query.message.reply_text(
            "Reply dismissed.",
            reply_markup=main_menu_keyboard(staff_lang_code=code),
        )
        return

    stored = get_active_case(context, chat_id)
    if not isinstance(stored, dict) or not str(stored.get("question", "") or "").strip():
        await query.message.reply_text(
            "Press 📩 Customer Asked first, then paste the customer message."
        )
        return

    if action == "staff_reply":
        if not staff_language_is_set(context):
            await send_lang_picker(update, context, first_time=True)
            return
        clear_customer_ask_mode(context)
        payload = bind_staff_reply_wait(context, chat_id, user_id, stored)
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=STAFF_REPLY_PROMPT,
            reply_markup=ForceReply(selective=True),
            reply_to_message_id=query.message.message_id,
        )
        payload["staff_reply_prompt_id"] = sent.message_id
        _PROMPT_TO_CASE[sent.message_id] = dict(payload)
        prompts = context.application.bot_data.setdefault("staff_ai_prompts", {})
        prompts[str(sent.message_id)] = _await_key(chat_id, user_id)
        save_active_case(context, payload, chat_id=chat_id)
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


def build_persistence() -> PicklePersistence:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if STATE_PATH.is_file():
        try:
            with open(STATE_PATH, "rb") as fh:
                fh.read(16)
        except OSError as exc:
            logger.warning("Resetting unreadable bot state: %s", exc)
            STATE_PATH.unlink(missing_ok=True)
    return PicklePersistence(filepath=str(STATE_PATH))


def build_app() -> Application:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    persistence = build_persistence()

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
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(CallbackQueryHandler(staff_ai_callback, pattern=r"^staffai:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_staff_text))
    return app


def main() -> None:
    logger.info("Starting %s", VERSION)
    if not KNOWLEDGE_PATH.is_file():
        logger.warning("Missing knowledge file at %s", KNOWLEDGE_PATH)
    try:
        app = build_app()
    except Exception:
        logger.exception("build_app failed")
        raise
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
    try:
        main()
    except Exception:
        logger.exception("Fatal startup error")
        raise
