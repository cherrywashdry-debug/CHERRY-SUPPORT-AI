"""CHERRY SUPPORT AI — one bot, two modes by chat.

Staff group (STAFF_GROUP_ID): translation for staff.
Everywhere else (private chat, other groups): FAQ menu.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

import faq_handlers as faq
import staff_translate as staff
from staff_translate import is_staff_chat

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.support_ai")

VERSION = "CHERRY SUPPORT AI - UNIFIED-FAQ-STAFF-V1"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"


async def route_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.start_cmd(update, context)
    else:
        await faq.start_cmd(update, context)


async def route_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.menu_cmd(update, context)
    else:
        await faq.menu_cmd(update, context)


async def route_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.lang_cmd(update, context)
    else:
        await faq.language_cmd(update, context)


async def route_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await route_lang(update, context)


async def route_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.group_cmd(update, context)
        return
    message = update.effective_message
    if message:
        await message.reply_text(
            "โหมด FAQ ค่ะ\n\n"
            "สำหรับตั้งค่ากลุ่มแปล: ส่ง /group ในกลุ่ม staff ที่ตั้ง STAFF_GROUP_ID"
        )


async def route_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.health_cmd(update, context)
    else:
        await faq.health_cmd(update, context)


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if is_staff_chat(update):
        await staff.handle_staff_text(update, context)
    else:
        await faq.handle_text(update, context)


async def route_staff_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_staff_chat(update):
        query = update.callback_query
        if query:
            await query.answer()
        return
    await staff.staff_ai_callback(update, context)


def build_health_response() -> str:
    return f"OK {VERSION}\n"


def _install_health_route() -> None:
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
    app.add_error_handler(staff.on_error)
    app.add_handler(CommandHandler("start", route_start))
    app.add_handler(CommandHandler("menu", route_menu))
    app.add_handler(CommandHandler("lang", route_lang))
    app.add_handler(CommandHandler("language", route_language))
    app.add_handler(CommandHandler("group", route_group))
    app.add_handler(CommandHandler("chatid", route_group))
    app.add_handler(CommandHandler("id", route_group))
    app.add_handler(CommandHandler("health", route_health))
    app.add_handler(CallbackQueryHandler(route_staff_callback, pattern=r"^staffai:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text))
    return app


def main() -> None:
    logger.info("Starting %s", VERSION)
    if not staff.KNOWLEDGE_PATH.is_file():
        logger.warning("Missing knowledge file at %s", staff.KNOWLEDGE_PATH)
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
