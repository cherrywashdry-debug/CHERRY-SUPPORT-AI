"""Owner-only admin reply management (edit / add / delete with confirmation)."""
from __future__ import annotations

import logging
import re
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from quick_replies import (
    BTN_ADMIN_ADD,
    BTN_ADMIN_BACK,
    BTN_ADMIN_DELETE,
    BTN_ADMIN_EDIT,
    BTN_ADMIN_EDIT_BUTTON,
    BTN_ADMIN_SET_IMAGE,
    BTN_EDIT_REPLIES_LEGACY,
    BTN_REPLY_MGMT,
    BTN_REPLY_MGMT_LEGACY,
    EDIT_LANG_LABELS,
    EDIT_STAFF_LANG_LABELS,
    OWNER_ACCESS_DENIED,
    admin_button_key_menu_rows,
    admin_category_menu_rows,
    admin_key_menu_rows,
    admin_reply_mgmt_menu_rows,
    back_button,
    edit_lang_display,
    edit_lang_menu_rows,
    edit_staff_lang_menu_rows,
    get_quick_replies,
    parse_admin_button_key,
    parse_admin_category,
    parse_edit_lang,
    parse_edit_reply_key,
    parse_edit_staff_lang,
    refresh_button_maps,
    reload_quick_replies,
)
from reply_button_store import (
    CATEGORIES,
    add_button_mapping,
    all_managed_keys,
    button_label,
    key_category,
    remove_button_mapping,
    update_button_label,
)
from reply_image_store import backup_images_file, remove_image, save_image
from reply_store import TODO_TEXT, add_reply, backup_replies_file, delete_reply, save_reply

logger = logging.getLogger("cherry.quick_reply.admin")

ADMIN_MODE = "admin_mode"
ADMIN_AWAITING = "admin_awaiting"
ADMIN_DRAFT = "admin_draft"
ADMIN_PENDING = "admin_pending"

SCREEN_REPLY_MGMT = "reply_mgmt"
SCREEN_ADMIN_EDIT_KEYS = "admin_edit_keys"
SCREEN_ADMIN_EDIT_LANG = "admin_edit_lang"
SCREEN_ADMIN_DELETE_KEYS = "admin_delete_keys"
SCREEN_ADMIN_EDIT_BUTTON_KEYS = "admin_edit_button_keys"
SCREEN_ADMIN_EDIT_BUTTON_LANG = "admin_edit_button_lang"
SCREEN_ADMIN_IMAGE_KEYS = "admin_image_keys"
SCREEN_ADMIN_IMAGE_LANG = "admin_image_lang"

ADMIN_SCREENS = (
    SCREEN_REPLY_MGMT,
    SCREEN_ADMIN_EDIT_KEYS,
    SCREEN_ADMIN_EDIT_LANG,
    SCREEN_ADMIN_DELETE_KEYS,
    SCREEN_ADMIN_EDIT_BUTTON_KEYS,
    SCREEN_ADMIN_EDIT_BUTTON_LANG,
    SCREEN_ADMIN_IMAGE_KEYS,
    SCREEN_ADMIN_IMAGE_LANG,
)

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

CAT_LABEL_TO_ID = {
    "❓ Questions To Customer": "questions_to_customer",
    "💬 Replies To Customer": "replies_to_customer",
    "🚚 Status Updates": "status_updates",
}
CAT_ID_TO_LABEL = {v: k for k, v in CAT_LABEL_TO_ID.items()}


def clear_admin_state(context: ContextTypes.DEFAULT_TYPE) -> bool:
    had = any(
        context.user_data.pop(key, None) is not None
        for key in (ADMIN_MODE, ADMIN_AWAITING, ADMIN_DRAFT, ADMIN_PENDING)
    )
    screen = str(context.user_data.get("active_screen", ""))
    if screen in ADMIN_SCREENS:
        context.user_data.pop("active_screen", None)
        had = True
    return had


def _set_screen(context: ContextTypes.DEFAULT_TYPE, screen: str) -> None:
    context.user_data["active_screen"] = screen


def _owner_only(update: Update) -> bool:
    from app import is_owner

    return is_owner(update)


def validate_new_key(key: str) -> str | None:
    raw = str(key or "").strip().lower()
    if not raw:
        return "Key cannot be empty."
    if " " in raw:
        return "Key must not contain spaces."
    if not KEY_PATTERN.match(raw):
        return "Key must be lowercase English with underscores only."
    if raw in get_quick_replies():
        return "Key already exists."
    if raw in all_managed_keys():
        return "Key already exists in button mapping."
    return None


def admin_key_label(key: str) -> str:
    return key.replace("_", " ")


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    if action == "add":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Confirm Add", callback_data="admin:confirm_add"),
                    InlineKeyboardButton("❌ Cancel", callback_data="admin:cancel_add"),
                ]
            ]
        )
    if action == "delete":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Confirm Delete", callback_data="admin:confirm_delete"),
                    InlineKeyboardButton("❌ Cancel", callback_data="admin:cancel_delete"),
                ]
            ]
        )
    raise ValueError(f"unknown confirm action: {action}")


async def send_reply_mgmt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    if not _owner_only(update):
        await message.reply_text(OWNER_ACCESS_DENIED)
        return
    clear_admin_state(context)
    _set_screen(context, SCREEN_REPLY_MGMT)
    from app import get_staff_lang, keyboard

    staff = get_staff_lang(context)
    await message.reply_text(
        "🔧 Reply Management\n\nPlease choose an action:",
        reply_markup=keyboard(admin_reply_mgmt_menu_rows(staff)),
    )


async def send_admin_edit_button_keys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not _owner_only(update):
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    context.user_data[ADMIN_MODE] = "edit_button"
    context.user_data.pop(ADMIN_AWAITING, None)
    context.user_data.pop(ADMIN_DRAFT, None)
    _set_screen(context, SCREEN_ADMIN_EDIT_BUTTON_KEYS)
    from app import get_staff_lang, keyboard

    staff = get_staff_lang(context)
    await message.reply_text(
        "🏷️ Edit Button\n\nSelect button key:",
        reply_markup=keyboard(admin_button_key_menu_rows(staff)),
    )


async def send_admin_edit_button_lang_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    context.user_data[ADMIN_DRAFT] = {"key": reply_key}
    context.user_data.pop(ADMIN_AWAITING, None)
    _set_screen(context, SCREEN_ADMIN_EDIT_BUTTON_LANG)
    from app import keyboard

    await message.reply_text(
        "Choose staff language for this button label:",
        reply_markup=keyboard(edit_staff_lang_menu_rows()),
    )


async def prompt_admin_edit_button_label(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
    staff_lang: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
    draft.update({"key": reply_key, "staff_lang": staff_lang})
    context.user_data[ADMIN_DRAFT] = draft
    context.user_data[ADMIN_AWAITING] = "edit_button_text"
    current = button_label(reply_key, staff_lang) or "(none)"
    await message.reply_text(
        f"Current button label ({staff_lang}):\n\n{current}\n\n"
        "Send new button label now.\nExample: 🚚 /ค่าจัดส่ง\nSend /cancel to cancel.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def send_admin_image_keys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not _owner_only(update):
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    context.user_data[ADMIN_MODE] = "set_image"
    context.user_data.pop(ADMIN_AWAITING, None)
    context.user_data.pop(ADMIN_DRAFT, None)
    _set_screen(context, SCREEN_ADMIN_IMAGE_KEYS)
    from app import get_staff_lang, keyboard
    from quick_replies import edit_reply_key_menu_rows

    staff = get_staff_lang(context)
    await message.reply_text(
        "🖼️ Set Reply Image\n\nSelect reply key:",
        reply_markup=keyboard(edit_reply_key_menu_rows(staff)),
    )


async def send_admin_image_lang_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    from reply_image_store import get_image_file_id
    from app import keyboard

    context.user_data[ADMIN_DRAFT] = {"key": reply_key}
    context.user_data.pop(ADMIN_AWAITING, None)
    _set_screen(context, SCREEN_ADMIN_IMAGE_LANG)
    has_image = any(get_image_file_id(reply_key, lang) for lang in EDIT_LANG_LABELS)
    status = "Image is set for at least one language." if has_image else "No image set yet."
    await message.reply_text(
        f"🖼️ Set Reply Image\nKey: {reply_key}\n\n{status}\n\n"
        "Please choose customer language:",
        reply_markup=keyboard(edit_lang_menu_rows()),
    )


async def prompt_admin_image_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
    lang: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    from reply_image_store import get_image_file_id

    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
    draft.update({"key": reply_key, "lang": lang})
    context.user_data[ADMIN_DRAFT] = draft
    context.user_data[ADMIN_AWAITING] = "image_wait_photo"
    current = get_image_file_id(reply_key, lang)
    if current:
        note = "Current: image saved.\nSend a new photo to replace.\nSend /remove to clear image."
    else:
        note = "No image for this language.\nSend photo now."
    await message.reply_text(
        f"{note}\nSend /cancel to cancel.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def handle_admin_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not _owner_only(update):
        return False
    if context.user_data.get(ADMIN_AWAITING) != "image_wait_photo":
        return False
    message = update.effective_message
    if not message or not message.photo:
        return False

    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
    reply_key = str(draft.get("key", ""))
    lang = str(draft.get("lang", ""))
    if reply_key not in get_quick_replies() or lang not in EDIT_LANG_LABELS:
        clear_admin_state(context)
        return True

    photo = message.photo[-1]
    file_id = str(photo.file_id)
    try:
        backup_images_file()
        save_image(reply_key, lang, file_id, backup=False)
    except Exception as exc:
        logger.exception("save image failed")
        await message.reply_text(f"Save failed: {exc}")
        return True

    clear_admin_state(context)
    await message.reply_text(
        "✅ Reply image saved.\n"
        f"Key: {reply_key}\n"
        f"Language: {edit_lang_display(lang)}",
    )
    from app import send_main_menu

    await send_main_menu(update, context)
    return True


async def send_admin_edit_keys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not _owner_only(update):
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    context.user_data[ADMIN_MODE] = "edit"
    context.user_data.pop(ADMIN_AWAITING, None)
    context.user_data.pop(ADMIN_DRAFT, None)
    context.user_data.pop(ADMIN_PENDING, None)
    _set_screen(context, SCREEN_ADMIN_EDIT_KEYS)
    from app import get_staff_lang, keyboard

    staff = get_staff_lang(context)
    from quick_replies import edit_reply_key_menu_rows

    await message.reply_text(
        "✏️ Edit Reply\n\nSelect reply key:",
        reply_markup=keyboard(edit_reply_key_menu_rows(staff)),
    )


async def send_admin_delete_keys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not _owner_only(update):
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    context.user_data[ADMIN_MODE] = "delete"
    context.user_data.pop(ADMIN_AWAITING, None)
    context.user_data.pop(ADMIN_DRAFT, None)
    context.user_data.pop(ADMIN_PENDING, None)
    _set_screen(context, SCREEN_ADMIN_DELETE_KEYS)
    from app import get_staff_lang, keyboard

    staff = get_staff_lang(context)
    await message.reply_text(
        "➖ Delete Reply\n\nSelect reply key:",
        reply_markup=keyboard(admin_key_menu_rows(staff)),
    )


async def send_admin_edit_lang_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    context.user_data[ADMIN_DRAFT] = {"key": reply_key}
    context.user_data.pop(ADMIN_AWAITING, None)
    _set_screen(context, SCREEN_ADMIN_EDIT_LANG)
    from app import keyboard

    await message.reply_text(
        "Please choose language to edit:",
        reply_markup=keyboard(edit_lang_menu_rows()),
    )


async def prompt_admin_edit_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
    lang: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
    draft.update({"key": reply_key, "lang": lang})
    context.user_data[ADMIN_DRAFT] = draft
    context.user_data[ADMIN_AWAITING] = "edit_text"
    current = get_quick_replies()[reply_key][lang]
    await message.reply_text(
        f"Current text:\n\n{current}\n\nSend new reply text now.\nSend /cancel to cancel.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def start_add_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not _owner_only(update):
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    context.user_data[ADMIN_MODE] = "add"
    context.user_data[ADMIN_DRAFT] = {}
    context.user_data[ADMIN_AWAITING] = "add_key"
    context.user_data.pop(ADMIN_PENDING, None)
    _set_screen(context, SCREEN_REPLY_MGMT)
    await message.reply_text(
        "➕ Add Reply\n\nSend new reply KEY.\nExample:\nperfume\nnight_delivery\ncash_payment\n\n"
        "Rules:\n• lowercase English only\n• no spaces\n• use underscore only\n• must not already exist\n\n"
        "Send /cancel to cancel.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def show_delete_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reply_key: str,
) -> None:
    message = update.effective_message
    if not message:
        return
    context.user_data[ADMIN_PENDING] = {"action": "delete", "key": reply_key}
    await message.reply_text(
        "⚠️ Confirm Delete Reply\n\n"
        f"Key: {reply_key}\n\n"
        "This will remove this reply button and text from the bot.",
        reply_markup=confirm_keyboard("delete"),
    )


def _format_add_confirmation(draft: dict[str, Any]) -> str:
    cat = CAT_ID_TO_LABEL.get(str(draft.get("category", "")), draft.get("category", ""))
    lines = [
        "⚠️ Confirm Add Reply",
        "",
        f"Key: {draft.get('key', '')}",
        f"Category: {cat}",
        "",
        "Buttons:",
        f"KH: {draft.get('btn_km', '')}",
        f"TH: {draft.get('btn_th', '')}",
        f"ID: {draft.get('btn_id', '')}",
        "",
        f"TH:\n{draft.get('text_th', '')}",
        "",
        f"EN:\n{draft.get('text_en', '')}",
        "",
        f"KH:\n{draft.get('text_km', '')}",
        "",
        f"ID:\n{draft.get('text_id', '')}",
        "",
        f"CN:\n{draft.get('text_cn', '')}",
    ]
    return "\n".join(lines)


async def show_add_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
    context.user_data[ADMIN_PENDING] = {"action": "add", "draft": draft}
    context.user_data.pop(ADMIN_AWAITING, None)
    await message.reply_text(
        _format_add_confirmation(draft),
        reply_markup=confirm_keyboard("add"),
    )


async def handle_admin_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raw: str,
) -> bool:
    """Return True if message was handled by admin flow."""
    if not _owner_only(update):
        if context.user_data.get(ADMIN_MODE) or context.user_data.get(ADMIN_AWAITING):
            clear_admin_state(context)
            message = update.effective_message
            if message:
                await message.reply_text(OWNER_ACCESS_DENIED)
            from app import send_main_menu

            await send_main_menu(update, context)
            return True
        return False

    awaiting = context.user_data.get(ADMIN_AWAITING)
    if not awaiting:
        return False

    message = update.effective_message
    if not message:
        return True

    draft = dict(context.user_data.get(ADMIN_DRAFT) or {})

    if awaiting == "edit_text":
        reply_key = str(draft.get("key", ""))
        lang = str(draft.get("lang", ""))
        if reply_key not in get_quick_replies() or lang not in EDIT_LANG_LABELS:
            clear_admin_state(context)
            from app import send_main_menu

            await send_main_menu(update, context)
            return True
        try:
            backup_replies_file()
            save_reply(reply_key, lang, raw, backup=False)
        except Exception as exc:
            logger.exception("edit save failed")
            await message.reply_text(f"Save failed: {exc}\nPrevious reply kept.")
            return True
        clear_admin_state(context)
        await message.reply_text(
            "✅ Reply updated successfully.\n"
            f"Key: {reply_key}\n"
            f"Language: {edit_lang_display(lang)}",
        )
        from app import send_main_menu

        await send_main_menu(update, context)
        return True

    if awaiting == "edit_button_text":
        reply_key = str(draft.get("key", ""))
        staff_lang = str(draft.get("staff_lang", ""))
        if not key_category(reply_key) or staff_lang not in EDIT_STAFF_LANG_LABELS:
            clear_admin_state(context)
            from app import send_main_menu

            await send_main_menu(update, context)
            return True
        try:
            update_button_label(reply_key, staff_lang, raw, backup=True)
            refresh_button_maps()
        except Exception as exc:
            logger.exception("edit button label failed")
            await message.reply_text(f"Save failed: {exc}\nPrevious label kept.")
            return True
        clear_admin_state(context)
        await message.reply_text(
            "✅ Button label updated.\n"
            f"Key: {reply_key}\n"
            f"Staff language: {staff_lang}\n"
            f"New label: {raw}",
        )
        from app import send_main_menu

        await send_main_menu(update, context)
        return True

    if awaiting == "image_wait_photo" and raw.strip().lower() == "/remove":
        reply_key = str(draft.get("key", ""))
        lang = str(draft.get("lang", ""))
        if reply_key in get_quick_replies() and lang in EDIT_LANG_LABELS:
            try:
                backup_images_file()
                remove_image(reply_key, lang, backup=False)
            except Exception as exc:
                logger.exception("remove image failed")
                await message.reply_text(f"Remove failed: {exc}")
                return True
        clear_admin_state(context)
        await message.reply_text("✅ Reply image removed.")
        from app import send_main_menu

        await send_main_menu(update, context)
        return True

    if awaiting == "add_key":
        err = validate_new_key(raw)
        if err:
            await message.reply_text(f"{err}\n\nSend another KEY or /cancel.")
            return True
        draft["key"] = raw.strip().lower()
        context.user_data[ADMIN_DRAFT] = draft
        context.user_data[ADMIN_AWAITING] = "add_category"
        from app import keyboard

        await message.reply_text(
            "Select category:",
            reply_markup=keyboard(admin_category_menu_rows()),
        )
        return True

    if awaiting == "add_category":
        category = parse_admin_category(raw)
        if not category:
            from app import keyboard

            await message.reply_text(
                "Please choose a category from the buttons.",
                reply_markup=keyboard(admin_category_menu_rows()),
            )
            return True
        draft["category"] = category
        context.user_data[ADMIN_DRAFT] = draft
        context.user_data[ADMIN_AWAITING] = "add_btn_km"
        await message.reply_text(
            "KH button label:\nExample:\n🌸 /ក្លិនក្រអូប\n\nSend /cancel to cancel.",
        )
        return True

    btn_prompts = {
        "add_btn_km": ("add_btn_th", "TH button label:\nExample:\n🌸 /น้ำหอม\n\nSend /cancel to cancel."),
        "add_btn_th": ("add_btn_id", "ID button label:\nExample:\n🌸 /parfum\n\nSend /cancel to cancel."),
        "add_btn_id": ("add_text_th", "Send TH reply text.\nSend /cancel to cancel."),
    }
    for step, (nxt, prompt) in btn_prompts.items():
        if awaiting == step:
            draft[step.replace("add_btn_", "btn_")] = raw
            context.user_data[ADMIN_DRAFT] = draft
            context.user_data[ADMIN_AWAITING] = nxt
            await message.reply_text(prompt)
            return True

    text_steps = (
        ("add_text_th", "add_text_en", "TH reply text"),
        ("add_text_en", "add_text_km", "EN reply text"),
        ("add_text_km", "add_text_id", "KH reply text"),
        ("add_text_id", "add_text_cn", "ID reply text"),
        ("add_text_cn", None, "CN reply text"),
    )
    for step, nxt, label in text_steps:
        if awaiting != step:
            continue
        if step == "add_text_th":
            if not raw.strip():
                await message.reply_text("TH reply text is required.")
                return True
            draft["text_th"] = raw
        else:
            draft[f"text_{step.split('_')[-1]}"] = raw if raw.strip().lower() != "/skip" else TODO_TEXT
        context.user_data[ADMIN_DRAFT] = draft
        if nxt is None:
            await show_add_confirmation(update, context)
            return True
        context.user_data[ADMIN_AWAITING] = nxt
        hint = f"Send {label}."
        if step != "add_text_th":
            hint += "\nAllow /skip to save TODO."
        hint += "\nSend /cancel to cancel."
        await message.reply_text(hint)
        return True

    return False


async def handle_reply_mgmt_screen(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    raw: str,
) -> bool:
    """Handle reply-keyboard navigation inside admin screens."""
    from app import get_staff_lang, keyboard, send_main_menu

    message = update.effective_message
    staff = get_staff_lang(context)
    screen = str(context.user_data.get("active_screen", ""))

    if raw in (BTN_REPLY_MGMT, BTN_REPLY_MGMT_LEGACY, BTN_EDIT_REPLIES_LEGACY):
        await send_reply_mgmt_menu(update, context)
        return True

    if screen == SCREEN_REPLY_MGMT:
        owner_actions = (
            BTN_ADMIN_EDIT,
            BTN_ADMIN_EDIT_BUTTON,
            BTN_ADMIN_SET_IMAGE,
            BTN_ADMIN_ADD,
            BTN_ADMIN_DELETE,
        )
        if raw in owner_actions and not _owner_only(update):
            if message:
                await message.reply_text(OWNER_ACCESS_DENIED)
            return True
        if raw == BTN_ADMIN_EDIT:
            await send_admin_edit_keys_menu(update, context)
            return True
        if raw == BTN_ADMIN_EDIT_BUTTON:
            await send_admin_edit_button_keys_menu(update, context)
            return True
        if raw == BTN_ADMIN_SET_IMAGE:
            await send_admin_image_keys_menu(update, context)
            return True
        if raw == BTN_ADMIN_ADD:
            await start_add_reply(update, context)
            return True
        if raw == BTN_ADMIN_DELETE:
            await send_admin_delete_keys_menu(update, context)
            return True
        if raw == BTN_ADMIN_BACK or raw == back_button(staff):
            clear_admin_state(context)
            await send_main_menu(update, context)
            return True
        await send_reply_mgmt_menu(update, context)
        return True

    if screen == SCREEN_ADMIN_EDIT_KEYS:
        if raw in (BTN_ADMIN_BACK, back_button(staff)):
            await send_reply_mgmt_menu(update, context)
            return True
        edit_key = parse_edit_reply_key(raw)
        if edit_key and edit_key in get_quick_replies():
            await send_admin_edit_lang_menu(update, context, edit_key)
            return True
        await send_admin_edit_keys_menu(update, context)
        return True

    if screen == SCREEN_ADMIN_EDIT_LANG:
        edit_lang = parse_edit_lang(raw)
        draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
        reply_key = str(draft.get("key", ""))
        if edit_lang and reply_key in get_quick_replies():
            await prompt_admin_edit_text(update, context, reply_key, edit_lang)
            return True
        await send_admin_edit_lang_menu(update, context, reply_key)
        return True

    if screen == SCREEN_ADMIN_EDIT_BUTTON_KEYS:
        if raw in (BTN_ADMIN_BACK, back_button(staff)):
            await send_reply_mgmt_menu(update, context)
            return True
        btn_key = parse_admin_button_key(raw)
        if btn_key and key_category(btn_key):
            await send_admin_edit_button_lang_menu(update, context, btn_key)
            return True
        await send_admin_edit_button_keys_menu(update, context)
        return True

    if screen == SCREEN_ADMIN_EDIT_BUTTON_LANG:
        staff_lang = parse_edit_staff_lang(raw)
        draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
        reply_key = str(draft.get("key", ""))
        if staff_lang and key_category(reply_key):
            await prompt_admin_edit_button_label(update, context, reply_key, staff_lang)
            return True
        await send_admin_edit_button_lang_menu(update, context, reply_key)
        return True

    if screen == SCREEN_ADMIN_IMAGE_KEYS:
        if raw in (BTN_ADMIN_BACK, back_button(staff)):
            await send_reply_mgmt_menu(update, context)
            return True
        img_key = parse_edit_reply_key(raw)
        if img_key and img_key in get_quick_replies():
            await send_admin_image_lang_menu(update, context, img_key)
            return True
        await send_admin_image_keys_menu(update, context)
        return True

    if screen == SCREEN_ADMIN_IMAGE_LANG:
        img_lang = parse_edit_lang(raw)
        draft = dict(context.user_data.get(ADMIN_DRAFT) or {})
        reply_key = str(draft.get("key", ""))
        if img_lang and reply_key in get_quick_replies():
            await prompt_admin_image_upload(update, context, reply_key, img_lang)
            return True
        await send_admin_image_lang_menu(update, context, reply_key)
        return True

    if screen == SCREEN_ADMIN_DELETE_KEYS:
        if raw in (BTN_ADMIN_BACK, back_button(staff)):
            await send_reply_mgmt_menu(update, context)
            return True
        del_key = parse_edit_reply_key(raw)
        if del_key and del_key in get_quick_replies():
            await show_delete_confirmation(update, context, del_key)
            return True
        await send_admin_delete_keys_menu(update, context)
        return True

    return False


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    if not _owner_only(update):
        await query.answer("Owner only.", show_alert=True)
        return
    await query.answer()

    pending = dict(context.user_data.get(ADMIN_PENDING) or {})
    data = query.data
    from app import send_main_menu

    if data == "admin:cancel_add":
        context.user_data.pop(ADMIN_PENDING, None)
        clear_admin_state(context)
        if query.message:
            await query.message.reply_text("❌ Add reply cancelled.")
        await send_main_menu(update, context)
        return

    if data == "admin:confirm_add":
        if pending.get("action") != "add":
            return
        draft = dict(pending.get("draft") or {})
        key = str(draft.get("key", ""))
        category = str(draft.get("category", ""))
        texts = {
            "th": str(draft.get("text_th", "")),
            "en": str(draft.get("text_en", TODO_TEXT)),
            "km": str(draft.get("text_km", TODO_TEXT)),
            "id": str(draft.get("text_id", TODO_TEXT)),
            "cn": str(draft.get("text_cn", TODO_TEXT)),
        }
        labels = {
            "km": str(draft.get("btn_km", "")),
            "th": str(draft.get("btn_th", "")),
            "id": str(draft.get("btn_id", "")),
        }
        try:
            backup_replies_file()
            add_reply(key, texts, backup=False)
            add_button_mapping(category, key, labels)
            refresh_button_maps()
            reload_quick_replies()
        except Exception as exc:
            logger.exception("confirm add failed")
            if query.message:
                await query.message.reply_text(f"Save failed: {exc}\nNo changes kept.")
            return
        context.user_data.pop(ADMIN_PENDING, None)
        clear_admin_state(context)
        if query.message:
            await query.message.reply_text("✅ New reply added successfully.")
        await send_main_menu(update, context)
        return

    if data == "admin:cancel_delete":
        context.user_data.pop(ADMIN_PENDING, None)
        if query.message:
            await query.message.reply_text("❌ Delete cancelled.")
        return

    if data == "admin:confirm_delete":
        if pending.get("action") != "delete":
            return
        key = str(pending.get("key", ""))
        try:
            backup_replies_file()
            delete_reply(key, backup=False)
            remove_button_mapping(key)
            from reply_image_store import remove_key_images

            remove_key_images(key, backup=False)
            refresh_button_maps()
            reload_quick_replies()
        except Exception as exc:
            logger.exception("confirm delete failed")
            if query.message:
                await query.message.reply_text(f"Delete failed: {exc}\nPrevious data kept.")
            return
        context.user_data.pop(ADMIN_PENDING, None)
        clear_admin_state(context)
        if query.message:
            await query.message.reply_text("✅ Reply deleted successfully.")
        await send_main_menu(update, context)
        return
