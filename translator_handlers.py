"""Pure translator for translate group — pick language, send text, get translation."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from staff_translate import is_translate_chat
from translator_content import (
    LANG_NAMES,
    MODE_ALL,
    MODE_PROMPT,
    SESSION_MODE_KEY,
    SINGLE_LANG_ORDER,
    TRANSLATE_FAIL,
    WELCOME,
    EMPTY_INPUT,
    format_all_results,
    lang_label,
    single_mode_prompt,
    single_result_header,
)

logger = logging.getLogger("cherry.translator")

VERSION = "CHERRY TRANSLATOR - V6-TRANSLATE-ONLY"


def get_mode(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    mode = str(context.user_data.get(SESSION_MODE_KEY, "") or "").strip()
    return mode if mode else None


def set_mode(context: ContextTypes.DEFAULT_TYPE, mode: str | None) -> None:
    if mode:
        context.user_data[SESSION_MODE_KEY] = mode
    else:
        context.user_data.pop(SESSION_MODE_KEY, None)


def openai_client() -> Any | None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    timeout = float(os.getenv("OPENAI_TIMEOUT_SEC", "60") or "60")
    return OpenAI(api_key=key, timeout=timeout, max_retries=2)


def translate_system_prompt() -> str:
    return (
        "You are a professional translator for CHERRY Wash & Dry staff.\n"
        "Translate ONLY. Do not answer questions. Do not add business facts.\n"
        "Use polite customer-service style. Natural grammar.\n"
        "Preserve full meaning. Return ONLY the translated text."
    )


def translate_to_language(text: str, target_code: str, target_name: str) -> str:
    client = openai_client()
    if not client:
        return ""
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=800,
        messages=[
            {"role": "system", "content": translate_system_prompt()},
            {"role": "user", "content": f"Translate to {target_name}:\n\n{text.strip()}"},
        ],
    )
    return str(response.choices[0].message.content or "").strip()


def translate_all_languages(text: str) -> dict[str, str]:
    results: dict[str, str] = {}
    for code in SINGLE_LANG_ORDER:
        translated = translate_to_language(text, code, LANG_NAMES[code])
        results[code] = translated or "—"
    return results


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("🇹🇭 Thai", callback_data="translator:mode:th"),
            InlineKeyboardButton("🇬🇧 English", callback_data="translator:mode:en"),
        ],
        [
            InlineKeyboardButton("🇰🇭 Khmer", callback_data="translator:mode:km"),
            InlineKeyboardButton("🇮🇩 Indonesian", callback_data="translator:mode:id"),
        ],
        [InlineKeyboardButton("🇨🇳 Chinese", callback_data="translator:mode:zh")],
        [InlineKeyboardButton("🔁 All 5 Languages", callback_data="translator:mode:all")],
    ]
    return InlineKeyboardMarkup(rows)


def after_translate_keyboard(*, copy_text: str = "") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if copy_text.strip():
        clipped = copy_text.strip()
        if len(clipped) > 256:
            clipped = clipped[:255].rstrip() + "…"
        rows.append([
            InlineKeyboardButton(
                "📋 Copy",
                copy_text=CopyTextButton(text=clipped),
            ),
        ])
    rows.append([
        InlineKeyboardButton("🔄 Translate Another", callback_data="translator:another"),
        InlineKeyboardButton("🌐 Change Language", callback_data="translator:menu"),
    ])
    return InlineKeyboardMarkup(rows)


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    prefix: str | None = None,
) -> None:
    target = update.effective_message or (
        update.callback_query.message if update.callback_query else None
    )
    if not target:
        return
    # Remove stale FAQ reply keyboard from this chat
    await target.reply_text("🌐", reply_markup=ReplyKeyboardRemove())
    await target.reply_text(prefix or WELCOME, reply_markup=main_menu_keyboard())


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_translate_chat(update):
        return
    set_mode(context, None)
    await send_main_menu(update, context)


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_cmd(update, context)


async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_translate_chat(update):
        return
    set_mode(context, None)
    await send_main_menu(update, context, prefix="🌐 Choose translation language:")


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_translate_chat(update) or not update.message:
        return
    ok = openai_client() is not None
    await update.message.reply_text(f"{VERSION}\nOpenAI: {'OK' if ok else 'NO KEY'}")


async def translate_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    raw: str,
    mode: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    if not raw:
        await message.reply_text(EMPTY_INPUT, reply_markup=after_translate_keyboard())
        return
    try:
        await message.chat.send_action("typing")
        if mode == MODE_ALL:
            results = await asyncio.to_thread(translate_all_languages, raw)
            if all(v == "—" for v in results.values()):
                await message.reply_text(TRANSLATE_FAIL, reply_markup=after_translate_keyboard())
                return
            body = format_all_results(results)
            await message.reply_text(body, reply_markup=after_translate_keyboard(copy_text=body))
            return
        translated = await asyncio.to_thread(
            translate_to_language,
            raw,
            mode,
            LANG_NAMES.get(mode, mode),
        )
        if not translated:
            await message.reply_text(TRANSLATE_FAIL, reply_markup=after_translate_keyboard())
            return
        body = f"{single_result_header(mode)}\n\n{translated}"
        await message.reply_text(body, reply_markup=after_translate_keyboard(copy_text=translated))
    except Exception:
        logger.exception("translation failed")
        await message.reply_text(TRANSLATE_FAIL, reply_markup=after_translate_keyboard())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_translate_chat(update):
        return
    message = update.effective_message
    if not message or not message.text:
        return
    raw = message.text.strip()
    if raw.startswith("/"):
        return

    mode = get_mode(context)
    if not mode:
        await message.reply_text(
            "Choose a language first 👇",
            reply_markup=main_menu_keyboard(),
        )
        return
    await translate_message(update, context, raw=raw, mode=mode)


async def translator_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    if not is_translate_chat(update) or not query.message:
        return

    data = query.data or ""
    if data == "translator:menu":
        set_mode(context, None)
        await query.message.reply_text(WELCOME, reply_markup=main_menu_keyboard())
        return

    if data == "translator:another":
        mode = get_mode(context)
        if not mode:
            await query.message.reply_text(WELCOME, reply_markup=main_menu_keyboard())
            return
        prompt = MODE_PROMPT if mode == MODE_ALL else single_mode_prompt(mode)
        await query.message.reply_text(prompt, reply_markup=after_translate_keyboard())
        return

    if data.startswith("translator:mode:"):
        picked = data.split(":", 2)[2]
        if picked not in SINGLE_LANG_ORDER and picked != MODE_ALL:
            return
        set_mode(context, picked)
        prompt = MODE_PROMPT if picked == MODE_ALL else single_mode_prompt(picked)
        await query.message.reply_text(prompt, reply_markup=after_translate_keyboard())
