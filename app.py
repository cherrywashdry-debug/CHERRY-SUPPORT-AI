"""CHERRY SUPPORT AI — standalone FAQ Telegram bot.

Not connected to CHERRY BOT V3. No orders, invoices, rewards, or delivery logic.
Answers come only from locked FAQ content in faq_content.py.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from faq_content import (
    BTN_BACK,
    BTN_CHANGE_LANG,
    BTN_CONTACT,
    BTN_DELIVERY_BACK,
    BTN_DELIVERY_FEE,
    BTN_DETERGENT,
    BTN_HOW_PICKUP,
    BTN_LAUNDRY,
    BTN_LAUNDRY_BAG,
    BTN_LAUNDRY_PRICE,
    BTN_LANG_EN,
    BTN_LANG_ID,
    BTN_LANG_KM,
    BTN_LANG_TH,
    BTN_LOCATION,
    BTN_NO_IRONING,
    BTN_OPENING_HOURS,
    BTN_PICKUP_DELIVERY,
    BTN_PICKUP_TIME,
    BTN_PRICE_DELIVERY,
    BTN_PROCESSING_TIME,
    BTN_READ_BEFORE,
    BTN_REWARDS,
    BTN_SEPARATE_MIXED,
    BTN_SHOP_RESP,
    BTN_SPECIAL_ITEMS,
    BTN_3DAY,
    BTN_VALUABLE,
    BUTTON_CONTENT_KEYS,
    DEFAULT_LANG,
    LANG_BUTTONS,
    LANG_MENU_ROWS,
    LAUNDRY_SUBMENU_ROWS,
    MAIN_MENU_ROWS,
    PICKUP_SUBMENU_ROWS,
    PRICE_SUBMENU_ROWS,
    READ_BEFORE_SUBMENU_ROWS,
    SUBMENU_FOR_BUTTON,
    SUBMENU_TRIGGERS,
    LANGUAGE_SET_MESSAGES,
    SUPPORTED_LANGS,
    faq_answer,
    normalize_lang,
    submenu_intro,
    ui_text,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.support_faq")

VERSION = "CHERRY SUPPORT AI - FAQ-V1"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"
USER_LANG_KEY = "faq_lang"

ALL_KNOWN_BUTTONS = frozenset(
    {BTN_BACK, BTN_CHANGE_LANG, BTN_LANG_EN, BTN_LANG_TH, BTN_LANG_KM, BTN_LANG_ID}
    | set(BUTTON_CONTENT_KEYS)
    | SUBMENU_TRIGGERS
)


def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return normalize_lang(str(context.user_data.get(USER_LANG_KEY, DEFAULT_LANG)))


def set_user_lang(context: ContextTypes.DEFAULT_TYPE, lang: str) -> str:
    normalized = normalize_lang(lang)
    context.user_data[USER_LANG_KEY] = normalized
    return normalized


def keyboard(rows: list[list[str]], *, resize: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(rows, resize_keyboard=resize)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return keyboard(MAIN_MENU_ROWS)


def lang_menu_keyboard() -> ReplyKeyboardMarkup:
    return keyboard(LANG_MENU_ROWS)


def submenu_keyboard(submenu: str) -> ReplyKeyboardMarkup:
    mapping = {
        "price": PRICE_SUBMENU_ROWS,
        "laundry": LAUNDRY_SUBMENU_ROWS,
        "pickup": PICKUP_SUBMENU_ROWS,
        "read_before": READ_BEFORE_SUBMENU_ROWS,
    }
    return keyboard(mapping[submenu])


def resolve_button_action(text: str) -> dict[str, Any] | None:
    """Map pressed button label to bot action. Pure function for testing."""
    label = str(text or "").strip()
    if not label:
        return None

    if label == BTN_BACK:
        return {"type": "main_menu"}

    if label == BTN_CHANGE_LANG:
        return {"type": "language_menu"}

    if label in LANG_BUTTONS:
        return {"type": "set_language", "lang": LANG_BUTTONS[label]}

    if label in SUBMENU_TRIGGERS:
        return {"type": "submenu", "submenu": SUBMENU_FOR_BUTTON[label]}

    if label in BUTTON_CONTENT_KEYS:
        return {"type": "answer", "content_key": BUTTON_CONTENT_KEYS[label]}

    return None


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    prefix: str | None = None,
) -> None:
    message = update.effective_message
    if not message:
        return
    lang = get_user_lang(context)
    body = prefix or ui_text(lang, "welcome")
    await message.reply_text(body, reply_markup=main_menu_keyboard())


async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    lang = get_user_lang(context)
    await message.reply_text(
        ui_text(lang, "choose_language"),
        reply_markup=lang_menu_keyboard(),
    )


async def send_submenu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    submenu: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    lang = get_user_lang(context)
    await message.reply_text(
        submenu_intro(lang, submenu),
        reply_markup=submenu_keyboard(submenu),
    )


async def send_faq_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    content_key: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    lang = get_user_lang(context)
    answer = faq_answer(lang, content_key)
    if not answer:
        await message.reply_text(
            ui_text(lang, "unknown_input"),
            reply_markup=main_menu_keyboard(),
        )
        return
    await message.reply_text(answer, reply_markup=main_menu_keyboard())


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_main_menu(update, context)


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = get_user_lang(context)
    await send_main_menu(update, context, prefix=ui_text(lang, "menu_hint"))


async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_language_menu(update, context)


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message:
        await message.reply_text(f"OK {VERSION}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not message.text:
        return

    raw = message.text.strip()
    if raw.startswith("/"):
        return

    action = resolve_button_action(raw)
    if not action:
        lang = get_user_lang(context)
        await message.reply_text(
            ui_text(lang, "unknown_input"),
            reply_markup=main_menu_keyboard(),
        )
        return

    action_type = action["type"]
    if action_type == "main_menu":
        await send_main_menu(update, context)
        return

    if action_type == "language_menu":
        await send_language_menu(update, context)
        return

    if action_type == "set_language":
        lang = set_user_lang(context, action["lang"])
        confirm = LANGUAGE_SET_MESSAGES.get(lang, LANGUAGE_SET_MESSAGES[DEFAULT_LANG])
        await send_main_menu(update, context, prefix=confirm)
        return

    if action_type == "submenu":
        await send_submenu(update, context, action["submenu"])
        return

    if action_type == "answer":
        await send_faq_answer(update, context, action["content_key"])
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


def resolve_webhook_url() -> str:
    explicit = os.getenv("WEBHOOK_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    render = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if render:
        return f"{render.rstrip('/')}/telegram"
    return ""


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

    app = (
        Application.builder()
        .token(token)
        .persistence(build_persistence())
        .concurrent_updates(True)
        .build()
    )
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CommandHandler("lang", language_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app


def main() -> None:
    logger.info("Starting %s", VERSION)
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
