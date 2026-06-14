"""FAQ handlers — used in private chat and non-staff groups."""
from __future__ import annotations

import logging
from typing import Any

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from faq_content import (
    BTN_BACK,
    BTN_CHANGE_LANG,
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
    faq_answer,
    normalize_lang,
    submenu_intro,
    ui_text,
)

logger = logging.getLogger("cherry.support_faq")

USER_LANG_KEY = "faq_lang"

ALL_KNOWN_BUTTONS = frozenset(
    {BTN_BACK, BTN_CHANGE_LANG, *LANG_BUTTONS.keys()}
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
        await message.reply_text("OK CHERRY SUPPORT AI — FAQ mode")


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
    elif action_type == "language_menu":
        await send_language_menu(update, context)
    elif action_type == "set_language":
        lang = set_user_lang(context, action["lang"])
        confirm = LANGUAGE_SET_MESSAGES.get(lang, LANGUAGE_SET_MESSAGES[DEFAULT_LANG])
        await send_main_menu(update, context, prefix=confirm)
    elif action_type == "submenu":
        await send_submenu(update, context, action["submenu"])
    elif action_type == "answer":
        await send_faq_answer(update, context, action["content_key"])
