"""CHERRY QUICK REPLY BOT — fixed staff quick replies only.

Not a translator. Not AI chat. Not customer FAQ. Not CHERRY BOT V3.
Staff picks languages, chooses Questions or Replies menu, presses a button,
bot sends fixed approved text in the customer language.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from quick_replies import (
    CUSTOMER_LANG_LABELS,
    DEFAULT_CUSTOMER_LANG,
    DEFAULT_STAFF_LANG,
    STAFF_LANG_LABELS,
    customer_lang_from_label,
    is_back_button,
    is_main_menu_label,
    main_menu_action,
    main_menu_rows,
    parse_question_label,
    parse_reply_label,
    question_menu_rows,
    question_text,
    quick_reply_text,
    reply_menu_rows,
    staff_lang_from_label,
    staff_ui,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.quick_reply")

VERSION = "CHERRY QUICK REPLY - FIXED-V2.2"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"

STAFF_LANG_KEY = "staff_lang"
CUSTOMER_LANG_KEY = "customer_lang"
STAFF_LANG_SET_KEY = "staff_lang_set"
CUSTOMER_LANG_SET_KEY = "customer_lang_set"
ACTIVE_SCREEN_KEY = "active_screen"  # main | questions | replies

SCREEN_MAIN = "main"
SCREEN_QUESTIONS = "questions"
SCREEN_REPLIES = "replies"


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


def allowed_user_ids() -> frozenset[int]:
    return parse_allowed_user_ids(os.getenv("ALLOWED_USER_IDS", ""))


def is_staff_user(update: Update) -> bool:
    user = update.effective_user
    allowed = allowed_user_ids()
    if not allowed:
        return user is not None
    return user is not None and user.id in allowed


def get_staff_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    from quick_replies import normalize_staff_lang

    return normalize_staff_lang(str(context.user_data.get(STAFF_LANG_KEY, DEFAULT_STAFF_LANG)))


def get_customer_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    from quick_replies import normalize_customer_lang

    return normalize_customer_lang(
        str(context.user_data.get(CUSTOMER_LANG_KEY, DEFAULT_CUSTOMER_LANG))
    )


def get_active_screen(context: ContextTypes.DEFAULT_TYPE) -> str:
    return str(context.user_data.get(ACTIVE_SCREEN_KEY, SCREEN_MAIN))


def set_active_screen(context: ContextTypes.DEFAULT_TYPE, screen: str) -> None:
    context.user_data[ACTIVE_SCREEN_KEY] = screen


def staff_lang_is_set(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get(STAFF_LANG_SET_KEY))


def customer_lang_is_set(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get(CUSTOMER_LANG_SET_KEY))


def set_staff_lang(context: ContextTypes.DEFAULT_TYPE, code: str) -> str:
    from quick_replies import normalize_staff_lang

    normalized = normalize_staff_lang(code)
    context.user_data[STAFF_LANG_KEY] = normalized
    context.user_data[STAFF_LANG_SET_KEY] = True
    return normalized


def set_customer_lang(context: ContextTypes.DEFAULT_TYPE, code: str) -> str:
    from quick_replies import normalize_customer_lang

    normalized = normalize_customer_lang(code)
    context.user_data[CUSTOMER_LANG_KEY] = normalized
    context.user_data[CUSTOMER_LANG_SET_KEY] = True
    return normalized


def clear_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in (
        STAFF_LANG_KEY,
        CUSTOMER_LANG_KEY,
        STAFF_LANG_SET_KEY,
        CUSTOMER_LANG_SET_KEY,
        ACTIVE_SCREEN_KEY,
    ):
        context.user_data.pop(key, None)


def keyboard(rows: list[list[str]], *, resize: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(rows, resize_keyboard=resize)


def staff_lang_keyboard() -> ReplyKeyboardMarkup:
    return keyboard([[STAFF_LANG_LABELS["km"]], [STAFF_LANG_LABELS["th"]], [STAFF_LANG_LABELS["id"]]])


def customer_lang_keyboard() -> ReplyKeyboardMarkup:
    return keyboard(
        [
            [CUSTOMER_LANG_LABELS["th"], CUSTOMER_LANG_LABELS["en"]],
            [CUSTOMER_LANG_LABELS["km"], CUSTOMER_LANG_LABELS["id"]],
            [CUSTOMER_LANG_LABELS["cn"]],
        ]
    )


def staff_lang_name(code: str) -> str:
    return STAFF_LANG_LABELS.get(get_staff_lang_from_code(code), code)


def get_staff_lang_from_code(code: str) -> str:
    from quick_replies import normalize_staff_lang

    return normalize_staff_lang(code)


def customer_lang_name(code: str) -> str:
    from quick_replies import normalize_customer_lang

    return CUSTOMER_LANG_LABELS.get(normalize_customer_lang(code), code)


async def deny_if_not_staff(update: Update) -> bool:
    if is_staff_user(update):
        return False
    message = update.effective_message
    if message:
        await message.reply_text("This bot is for CHERRY staff only.")
    return True


async def send_staff_lang_menu(update: Update) -> None:
    message = update.effective_message
    if not message:
        return
    await message.reply_text(
        staff_ui(DEFAULT_STAFF_LANG, "prompt_start"),
        reply_markup=staff_lang_keyboard(),
    )


async def send_customer_lang_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message
    if not message:
        return
    staff = get_staff_lang(context)
    await message.reply_text(
        staff_ui(staff, "prompt_customer").format(staff=staff_lang_name(staff)),
        reply_markup=customer_lang_keyboard(),
    )


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message
    if not message:
        return
    set_active_screen(context, SCREEN_MAIN)
    staff = get_staff_lang(context)
    customer = get_customer_lang(context)
    await message.reply_text(
        staff_ui(staff, "prompt_main"),
        reply_markup=keyboard(main_menu_rows(staff)),
    )
    logger.info(
        "main menu staff=%s customer=%s user=%s",
        staff,
        customer,
        getattr(update.effective_user, "id", None),
    )


async def send_questions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    set_active_screen(context, SCREEN_QUESTIONS)
    staff = get_staff_lang(context)
    await message.reply_text(
        staff_ui(staff, "header_questions"),
        reply_markup=keyboard(question_menu_rows(staff)),
    )


async def send_replies_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    set_active_screen(context, SCREEN_REPLIES)
    staff = get_staff_lang(context)
    await message.reply_text(
        staff_ui(staff, "header_replies"),
        reply_markup=keyboard(reply_menu_rows(staff)),
    )


async def ensure_ready_for_main(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    if not staff_lang_is_set(context):
        await send_staff_lang_menu(update)
        return False
    if not customer_lang_is_set(context):
        await send_customer_lang_menu(update, context)
        return False
    return True


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    clear_session(context)
    await send_staff_lang_menu(update)


async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    context.user_data.pop(STAFF_LANG_SET_KEY, None)
    context.user_data.pop(CUSTOMER_LANG_SET_KEY, None)
    context.user_data.pop(ACTIVE_SCREEN_KEY, None)
    await send_staff_lang_menu(update)


async def customer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    if not staff_lang_is_set(context):
        await send_staff_lang_menu(update)
        return
    context.user_data.pop(CUSTOMER_LANG_SET_KEY, None)
    await send_customer_lang_menu(update, context)


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    if not await ensure_ready_for_main(update, context):
        return
    await send_main_menu(update, context)


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    clear_session(context)
    message = update.effective_message
    if message:
        await message.reply_text(
            staff_ui(DEFAULT_STAFF_LANG, "session_cleared"),
            reply_markup=ReplyKeyboardRemove(),
        )
    await send_staff_lang_menu(update)


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    message = update.effective_message
    if message:
        await message.reply_text(f"OK {VERSION}")


async def handle_main_menu_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raw: str,
) -> bool:
    action = main_menu_action(raw)
    if action == "questions":
        await send_questions_menu(update, context)
        return True
    if action == "replies":
        await send_replies_menu(update, context)
        return True
    if action == "change_customer":
        context.user_data.pop(CUSTOMER_LANG_SET_KEY, None)
        await send_customer_lang_menu(update, context)
        return True
    if action == "change_staff":
        context.user_data.pop(STAFF_LANG_SET_KEY, None)
        context.user_data.pop(CUSTOMER_LANG_SET_KEY, None)
        context.user_data.pop(ACTIVE_SCREEN_KEY, None)
        await send_staff_lang_menu(update)
        return True
    if action == "clear":
        await clear_cmd(update, context)
        return True
    return False


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    message = update.effective_message
    if not message or not message.text:
        return

    raw = message.text.strip()
    if not raw:
        return

    picked_staff = staff_lang_from_label(raw)
    if picked_staff and not staff_lang_is_set(context):
        set_staff_lang(context, picked_staff)
        await send_customer_lang_menu(update, context)
        return

    picked_customer = customer_lang_from_label(raw)
    if picked_customer and staff_lang_is_set(context) and not customer_lang_is_set(context):
        set_customer_lang(context, picked_customer)
        await send_main_menu(update, context)
        return

    if picked_staff and staff_lang_is_set(context) and not customer_lang_is_set(context):
        set_staff_lang(context, picked_staff)
        await send_customer_lang_menu(update, context)
        return

    if picked_customer and customer_lang_is_set(context):
        set_customer_lang(context, picked_customer)
        await send_main_menu(update, context)
        return

    if not await ensure_ready_for_main(update, context):
        return

    if is_back_button(raw):
        await send_main_menu(update, context)
        return

    screen = get_active_screen(context)

    if screen == SCREEN_MAIN or is_main_menu_label(raw):
        if is_main_menu_label(raw):
            await handle_main_menu_choice(update, context, raw)
            return
        await send_main_menu(update, context)
        return

    if screen == SCREEN_QUESTIONS:
        q_key = parse_question_label(raw)
        if not q_key:
            await send_questions_menu(update, context)
            return
        answer = question_text(q_key, get_customer_lang(context))
        await message.reply_text(
            answer,
            reply_markup=keyboard(question_menu_rows(get_staff_lang(context))),
        )
        return

    if screen == SCREEN_REPLIES:
        r_key = parse_reply_label(raw)
        if not r_key:
            await send_replies_menu(update, context)
            return
        answer = quick_reply_text(r_key, get_customer_lang(context))
        await message.reply_text(
            answer,
            reply_markup=keyboard(reply_menu_rows(get_staff_lang(context))),
        )
        return

    await send_main_menu(update, context)


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
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CommandHandler("lang", language_cmd))
    app.add_handler(CommandHandler("customer", customer_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.COMMAND, handle_text))
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
