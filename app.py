"""CHERRY Staff AI — separate bot for staff-only customer reply drafting.

Two-layer card:
  Layer 1 (Khmer) — what the customer message means / translation for Cambodian staff
  Layer 2 — suggested reply in the customer's language (copy to customer)

No Google Sheets, no billing, no V3 logic.
"""
from __future__ import annotations

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

VERSION = "CHERRY STAFF AI - TWO-LAYER-KM-V2"
ROOT = Path(__file__).resolve().parent
KNOWLEDGE_PATH = ROOT / "CHERRY_KNOWLEDGE.md"
if not KNOWLEDGE_PATH.is_file():
    KNOWLEDGE_PATH = ROOT.parent / "CHERRY_KNOWLEDGE.md"
LAST_QUESTION_KEY = "staff_ai_last_question"

FALLBACK_EN = (
    "Thank you for contacting CHERRY Wash & Dry. Our staff will assist you shortly."
)


@dataclass
class StaffAIResult:
    detected_language: str
    language_name: str
    staff_layer_km: str
    category: str
    risk: str
    customer_reply: str


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
    return OpenAI(api_key=key)


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
    if not chat or not user:
        return False
    if is_setup_mode():
        if chat.type in ("group", "supergroup"):
            return True
        return user.id in allowed_user_ids()
    group = staff_group_id()
    if group and chat.id == group:
        return True
    return user.id in allowed_user_ids() and chat.type == "private"


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
    return text


def build_system_prompt(knowledge: str) -> str:
    return (
        "You are CHERRY Wash & Dry Poipet staff assistant.\n"
        "Use ONLY facts from the knowledge base below. Never invent prices, promotions, or policies.\n"
        "Never promise refunds, compensation, point changes, or verified order status.\n"
        "If unsure, use a polite fallback that staff will help shortly (in the customer's language).\n\n"
        "Return a single JSON object with exactly these keys:\n"
        "  detected_language — short code (en, th, km, id, zh, ja, ko, ru, ...)\n"
        "  language_name — human-readable language name\n"
        "  staff_layer_km — Khmer (Cambodian) text for staff with TWO parts:\n"
        "    (1) បកប្រែសារអតិថិជនថាពួកគេនិយាយអ្វី\n"
        "    (2) សង្ខេបថាអតិថិជនសួរអ្វី\n"
        "  Write staff_layer_km ONLY in Khmer script — staff are Cambodian, not Thai.\n"
        "  category — one of: Price, Reward, Pickup, Policy, Order Status, Missing Item, Complaint, General\n"
        "  risk — Low, Medium, or High (High for missing items, damage, refund demands)\n"
        "  customer_reply — polite reply in THE CUSTOMER'S LANGUAGE, ready to copy-paste\n\n"
        "Knowledge base:\n"
        f"{knowledge}"
    )


def build_user_prompt(customer_text: str, *, mode: str = "normal", previous_reply: str = "") -> str:
    if mode == "shorter":
        return (
            f"Customer message:\n{customer_text}\n\n"
            "Make customer_reply shorter and clearer. Keep staff_layer_km updated if meaning changed.\n"
            f"Previous customer_reply:\n{previous_reply}"
        )
    if mode == "rewrite":
        return (
            f"Customer message:\n{customer_text}\n\n"
            "Rewrite customer_reply with different wording. Keep facts identical.\n"
            f"Previous customer_reply:\n{previous_reply}"
        )
    return f"Customer message:\n{customer_text}"


def parse_llm_json(raw: str) -> dict[str, Any]:
    text = str(raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("LLM response is not a JSON object")
    return data


def result_from_payload(payload: dict[str, Any]) -> StaffAIResult:
    return StaffAIResult(
        detected_language=str(payload.get("detected_language", "") or "unknown").strip(),
        language_name=str(payload.get("language_name", "") or "Unknown").strip(),
        staff_layer_km=str(
            payload.get("staff_layer_km") or payload.get("staff_layer_th") or ""
        ).strip(),
        category=str(payload.get("category", "") or "General").strip(),
        risk=str(payload.get("risk", "") or "Low").strip(),
        customer_reply=str(payload.get("customer_reply", "") or FALLBACK_EN).strip() or FALLBACK_EN,
    )


def draft_staff_reply(
    customer_text: str,
    *,
    mode: str = "normal",
    previous_reply: str = "",
    knowledge: str = "",
) -> StaffAIResult:
    client = openai_client()
    if not client:
        return StaffAIResult(
            detected_language="?",
            language_name="Unknown",
            staff_layer_km=(
                "⚠️ មិនទាន់បានកំណត់ OPENAI_API_KEY\n"
                f"សារអតិថិជន (ដើម): {customer_text}"
            ),
            category="General",
            risk="Low",
            customer_reply=FALLBACK_EN,
        )

    kb = knowledge or load_knowledge()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        temperature=0.3 if mode == "normal" else 0.5,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt(kb)},
            {"role": "user", "content": build_user_prompt(customer_text, mode=mode, previous_reply=previous_reply)},
        ],
    )
    raw = response.choices[0].message.content or "{}"
    return result_from_payload(parse_llm_json(raw))


def format_two_layer_card(
    result: StaffAIResult,
    *,
    original_text: str,
    mode_label: str = "",
) -> str:
    header = "🤖 CHERRY Staff AI"
    if mode_label:
        header = f"{header} · {mode_label}"

    original_block = original_text.strip() or "(no text)"
    lines = [
        header,
        "",
        "📩 Customer Message (original) / សារអតិថិជន (ដើម)",
        "────────────────",
        original_block,
        "",
        f"🌍 Language / ភាសា: {result.language_name} ({result.detected_language})",
        f"📂 Category / ប្រភេទ: {result.category}  ·  ⚠️ Risk: {result.risk}",
        "",
        "👀 Layer 1 — For Staff (translate / summary) / សម្រាប់បុគ្គលិក (បកប្រែ / សង្ខេប)",
        "────────────────",
        result.staff_layer_km,
        "",
        f"✉️ Layer 2 — Suggested reply (copy to customer · {result.language_name})",
        f"ចម្លើយសំណើ (copy ផ្ញើអតិថិជន · {result.language_name})",
        "────────────────",
        result.customer_reply,
        "",
        "━━━━━━━━━━━━━━",
        "⚠️ Review before sending — AI may be wrong",
        "សូមពិនិត្យមុនផ្ញើ — AI អាចខុសបាន",
        "Staff may edit, shorten, or rewrite before replying to the customer.",
    ]
    return "\n".join(lines)


def staff_ai_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Rewrite", callback_data="staffai:rewrite"),
            InlineKeyboardButton("✂️ Shorter", callback_data="staffai:shorter"),
        ],
    ])


USAGE_TEXT = (
    "CHERRY Staff AI — 2-layer reply helper\n"
    "ជំនួយឆ្លើយ 2 ជាន់\n\n"
    "Paste or forward any customer message in this group.\n"
    "ចម្លង ឬ forward សារអតិថិជនមកក្នុងក្រុមនេះ\n\n"
    "Layer 1 — Khmer translation/summary for staff\n"
    "ជាន់ 1 — បកប្រែ/សង្ខេបជាភាសាខ្មែរសម្រាប់បុគ្គលិក\n\n"
    "Layer 2 — suggested reply in the customer's language (copy to customer)\n"
    "ជាន់ 2 — ចម្លើយសំណើជាភាសាអតិថិជន (copy ផ្ញើ)\n\n"
    "Optional prefix: Customer: ... / អតិថិជន: ...\n"
    "Buttons: Rewrite · Shorter\n\n"
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
    llm = "OK" if openai_client() else "NO KEY"
    await update.message.reply_text(f"{VERSION}\nKnowledge: {kb}\nOpenAI: {llm}")


async def handle_staff_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        return
    message = update.effective_message
    if not message or not message.text:
        if message and message.caption:
            await message.reply_text("Photo received — please paste the customer's text question as well.")
        return

    text = extract_customer_text(message.text)
    if not text or text.startswith("/"):
        return

    if is_setup_mode():
        await message.reply_text(SETUP_HINT)
        return

    await message.chat.send_action("typing")
    knowledge = load_knowledge()
    result = draft_staff_reply(text, knowledge=knowledge)
    card = format_two_layer_card(result, original_text=text)
    sent = await message.reply_text(card, reply_markup=staff_ai_keyboard())

    context.chat_data[LAST_QUESTION_KEY] = {
        "question": text,
        "customer_reply": result.customer_reply,
        "reply_message_id": sent.message_id,
    }


async def staff_ai_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_staff_chat(update):
        return

    action = (query.data or "").split(":", 1)[-1]
    if action not in ("rewrite", "shorter"):
        return

    stored = context.chat_data.get(LAST_QUESTION_KEY)
    if not isinstance(stored, dict):
        await query.message.reply_text("Paste a customer message first.")
        return

    question = str(stored.get("question", "") or "").strip()
    previous = str(stored.get("customer_reply", "") or "").strip()
    if not question:
        await query.message.reply_text("Paste a customer message first.")
        return

    await query.message.chat.send_action("typing")
    mode = "rewrite" if action == "rewrite" else "shorter"
    label = "Rewrite" if action == "rewrite" else "Shorter"
    result = draft_staff_reply(question, mode=mode, previous_reply=previous, knowledge=load_knowledge())
    card = format_two_layer_card(result, original_text=question, mode_label=label)

    stored["customer_reply"] = result.customer_reply
    context.chat_data[LAST_QUESTION_KEY] = stored

    await query.message.reply_text(card, reply_markup=staff_ai_keyboard())


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


def build_app() -> Application:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    app = Application.builder().token(token).build()
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
