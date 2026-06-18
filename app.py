"""CHERRY QUICK REPLY BOT — fixed staff quick replies only.

Staff picks languages, then taps one button to copy approved customer reply text.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from quick_replies import (
    BTN_STAFF_MGMT,
    CUSTOMER_LANG_LABELS,
    CUSTOMER_LANG_ORDER,
    DEFAULT_CUSTOMER_LANG,
    DEFAULT_STAFF_LANG,
    OWNER_ACCESS_DENIED,
    STAFF_LANG_LABELS,
    STAFF_LANG_ORDER,
    customer_lang_from_label,
    get_quick_replies,
    is_back_button,
    is_main_menu_label,
    lang_picker_rows,
    main_menu_action,
    parse_quick_reply_key,
    quick_reply_text,
    quick_reply_image_file_id,
    staff_lang_from_label,
    staff_quick_reply_keyboard_rows,
    staff_ui,
)
from admin_reply_mgmt import (
    ADMIN_SCREENS,
    SCREEN_ADMIN_DELETE_KEYS,
    SCREEN_ADMIN_EDIT_KEYS,
    SCREEN_ADMIN_EDIT_LANG,
    SCREEN_REPLY_MGMT,
    admin_callback,
    clear_admin_state,
    handle_admin_photo,
    handle_admin_text,
    handle_reply_mgmt_screen,
    send_reply_mgmt_menu,
)
from reply_image_store import bundled_image_path

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("cherry.quick_reply")

VERSION = "CHERRY QUICK REPLY - SIMPLE-V5.27"
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "data" / "bot_state.pkl"

STAFF_LANG_KEY = "staff_lang"
CUSTOMER_LANG_KEY = "customer_lang"
STAFF_LANG_SET_KEY = "staff_lang_set"
CUSTOMER_LANG_SET_KEY = "customer_lang_set"
ACTIVE_SCREEN_KEY = "active_screen"

SCREEN_MAIN = "main"
SCREEN_STAFF_MGMT = "staff_mgmt"
SCREEN_REMOVE_STAFF = "remove_staff"

BTN_STAFF_LIST = "📋 Staff List"
BTN_REMOVE_STAFF = "➖ Remove Staff"
BTN_PENDING_REQUESTS = "🔄 Pending Requests"

ACCESS_GATE_TEXT = (
    "⛔ CHERRY STAFF ONLY\n\n"
    "This bot is for approved CHERRY staff only.\n\n"
    "Please press /register to request access."
)
ACCESS_APPROVED_TEXT = (
    "✅ Access approved.\n"
    "You can now use CHERRY Quick Reply Bot."
)
ACCESS_REJECTED_TEXT = (
    "❌ Access rejected.\n"
    "Please contact owner."
)


def owner_telegram_id() -> int | None:
    raw = os.getenv("OWNER_TELEGRAM_ID", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def is_owner(update: Update) -> bool:
    oid = owner_telegram_id()
    user = update.effective_user
    return oid is not None and user is not None and user.id == oid


def has_staff_access(update: Update) -> bool:
    user = update.effective_user
    if user is None:
        return False
    if is_owner(update):
        return True
    return staff_users.is_active_staff(user.id)


def user_label(user: Any) -> tuple[str, str, int]:
    if user is None:
        return "Unknown", "", 0
    name = user.full_name or user.first_name or "Unknown"
    username = f"@{user.username}" if user.username else "No username"
    return name, username, int(user.id)


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
    clear_admin_state(context)
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


def keyboard_button(text: str, *, custom_emoji_id: str | None = None) -> KeyboardButton | str:
    if custom_emoji_id:
        return KeyboardButton(text=text, icon_custom_emoji_id=custom_emoji_id)
    return text


def keyboard_from_specs(
    spec_rows: list[list[tuple[str, str | None]]],
    *,
    resize: bool = True,
) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton | str]] = [
        [keyboard_button(text, custom_emoji_id=emoji_id) for text, emoji_id in row]
        for row in spec_rows
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=resize)


def build_main_menu_keyboard(staff_lang: str, *, is_owner_user: bool) -> ReplyKeyboardMarkup:
    rows = staff_quick_reply_keyboard_rows(
        staff_lang,
        show_staff_management=is_owner_user,
    )
    return keyboard_from_specs(rows, resize=False)


def staff_lang_keyboard() -> ReplyKeyboardMarkup:
    return keyboard(lang_picker_rows(STAFF_LANG_LABELS, STAFF_LANG_ORDER))


def customer_lang_keyboard() -> ReplyKeyboardMarkup:
    return keyboard(lang_picker_rows(CUSTOMER_LANG_LABELS, CUSTOMER_LANG_ORDER))


def staff_lang_name(code: str) -> str:
    return STAFF_LANG_LABELS.get(get_staff_lang_from_code(code), code)


def get_staff_lang_from_code(code: str) -> str:
    from quick_replies import normalize_staff_lang

    return normalize_staff_lang(code)


def customer_lang_name(code: str) -> str:
    from quick_replies import normalize_customer_lang

    return CUSTOMER_LANG_LABELS.get(normalize_customer_lang(code), code)


async def deny_if_not_staff(update: Update) -> bool:
    if has_staff_access(update):
        return False
    message = update.effective_message
    if message:
        await message.reply_text(ACCESS_GATE_TEXT)
    return True


async def send_access_gate(update: Update) -> None:
    message = update.effective_message
    if message:
        await message.reply_text(ACCESS_GATE_TEXT, reply_markup=ReplyKeyboardRemove())


def staff_mgmt_menu_rows(staff_lang: str) -> list[list[str]]:
    from quick_replies import back_button

    return [
        [BTN_STAFF_LIST],
        [BTN_REMOVE_STAFF, BTN_PENDING_REQUESTS],
        [back_button(staff_lang)],
    ]


def remove_staff_menu_rows(staff_lang: str) -> tuple[list[list[str]], dict[str, int]]:
    from quick_replies import back_button

    label_to_id: dict[str, int] = {}
    rows: list[list[str]] = []
    for row in staff_users.list_active_staff():
        uid = int(row["user_id"])
        if uid == owner_telegram_id():
            continue
        label = staff_users.staff_display_name(row)
        label_to_id[label] = uid
        rows.append([label])
    rows.append([back_button(staff_lang)])
    return rows, label_to_id


def staff_request_keyboard(user_id: int) -> InlineKeyboardMarkup:
    uid = int(user_id)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"staff:approve:{uid}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"staff:reject:{uid}"),
            ]
        ]
    )


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


def clear_legacy_edit_persistence(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Drop pre-Reply-Management session keys/screens from persisted state."""
    for key in ("edit_awaiting", "edit_reply_key", "edit_reply_lang"):
        context.user_data.pop(key, None)
    if get_active_screen(context) in ("edit_keys", "edit_lang"):
        set_active_screen(context, SCREEN_MAIN)


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    message = update.effective_message
    if not message:
        return
    clear_legacy_edit_persistence(context)
    set_active_screen(context, SCREEN_MAIN)
    staff = get_staff_lang(context)
    customer = get_customer_lang(context)
    await message.reply_text(
        staff_ui(staff, "prompt_main").format(customer=customer_lang_name(customer)),
        reply_markup=build_main_menu_keyboard(staff, is_owner_user=is_owner(update)),
    )
    logger.info(
        "main menu staff=%s customer=%s user=%s",
        staff,
        customer,
        getattr(update.effective_user, "id", None),
    )


async def send_customer_quick_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    key: str,
    reply_markup: ReplyKeyboardMarkup | None = None,
) -> None:
    message = update.effective_message
    if not message:
        return
    await send_customer_quick_reply_message(message, context, key, reply_markup=reply_markup)


async def send_customer_quick_reply_message(
    message: Any,
    context: ContextTypes.DEFAULT_TYPE,
    key: str,
    *,
    reply_markup: ReplyKeyboardMarkup | None = None,
) -> None:
    customer = get_customer_lang(context)
    text = quick_reply_text(key, customer)
    file_id = quick_reply_image_file_id(key, customer)
    bundled = bundled_image_path(key)
    if file_id:
        if len(text) <= 1024:
            await message.reply_photo(file_id, caption=text, reply_markup=reply_markup)
        else:
            await message.reply_photo(file_id, reply_markup=reply_markup)
            await message.reply_text(text, reply_markup=reply_markup)
        return
    if bundled:
        with bundled.open("rb") as photo_fh:
            photo = InputFile(photo_fh, filename=bundled.name)
            if len(text) <= 1024:
                await message.reply_photo(photo, caption=text, reply_markup=reply_markup)
            else:
                await message.reply_photo(photo, reply_markup=reply_markup)
                await message.reply_text(text, reply_markup=reply_markup)
        return
    await message.reply_text(text, reply_markup=reply_markup)


async def send_staff_mgmt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    if not is_owner(update):
        await message.reply_text(OWNER_ACCESS_DENIED)
        return
    set_active_screen(context, SCREEN_STAFF_MGMT)
    staff = get_staff_lang(context)
    await message.reply_text(
        "👩‍💼 Staff Management",
        reply_markup=keyboard(staff_mgmt_menu_rows(staff)),
    )


async def send_staff_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not is_owner(update):
        return
    active = staff_users.list_active_staff()
    if not active:
        text = "📋 Staff List\n\nNo approved staff yet."
    else:
        lines = ["📋 Staff List", ""]
        for row in active:
            status = str(row.get("status", "unknown"))
            lines.append(f"• {staff_users.staff_display_name(row)} [{status}]")
        text = "\n".join(lines)
    staff = get_staff_lang(context)
    await message.reply_text(text, reply_markup=keyboard(staff_mgmt_menu_rows(staff)))


async def send_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not is_owner(update):
        return
    pending = staff_users.list_pending_requests()
    staff = get_staff_lang(context)
    if not pending:
        await message.reply_text(
            "🔄 Pending Requests\n\nNo pending requests.",
            reply_markup=keyboard(staff_mgmt_menu_rows(staff)),
        )
        return
    await message.reply_text(
        "🔄 Pending Requests",
        reply_markup=keyboard(staff_mgmt_menu_rows(staff)),
    )
    for row in pending:
        uid = int(row["user_id"])
        username = str(row.get("username") or "No username")
        if username and not username.startswith("@"):
            username = f"@{username.lstrip('@')}"
        text = (
            "📩 Pending Staff Access Request\n\n"
            f"Name: {row.get('name', 'Unknown')}\n"
            f"Username: {username}\n"
            f"Telegram ID: {uid}"
        )
        await message.reply_text(text, reply_markup=staff_request_keyboard(uid))


async def send_remove_staff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message or not is_owner(update):
        return
    staff = get_staff_lang(context)
    rows, label_to_id = remove_staff_menu_rows(staff)
    context.user_data["remove_staff_map"] = label_to_id
    set_active_screen(context, SCREEN_REMOVE_STAFF)
    if len(label_to_id) == 0:
        await message.reply_text(
            "➖ Remove Staff\n\nNo removable staff found.",
            reply_markup=keyboard(staff_mgmt_menu_rows(staff)),
        )
        set_active_screen(context, SCREEN_STAFF_MGMT)
        return
    await message.reply_text(
        "➖ Remove Staff\n\nSelect staff to disable:",
        reply_markup=keyboard(rows),
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


async def apply_customer_lang(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    code: str,
) -> None:
    set_customer_lang(context, code)
    await send_main_menu(update, context)


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    message = update.effective_message
    if not clear_admin_state(context):
        if message:
            await message.reply_text("Nothing to cancel.")
        return
    if message:
        await message.reply_text("Cancelled.")
    if await ensure_ready_for_main(update, context):
        await send_main_menu(update, context)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not has_staff_access(update):
        await send_access_gate(update)
        return
    clear_session(context)
    await send_staff_lang_menu(update)


async def notify_owner_access_request(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    name: str,
    username: str,
    uid: int,
) -> tuple[bool, str | None]:
    """Send inline Approve/Reject to owner. Returns (ok, error_message)."""
    oid = owner_telegram_id()
    if oid is None:
        return False, "owner_not_configured"

    owner_text = (
        "📩 New Staff Access Request\n\n"
        f"Name: {name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {uid}"
    )
    try:
        await context.bot.send_message(
            chat_id=oid,
            text=owner_text,
            reply_markup=staff_request_keyboard(uid),
        )
        return True, None
    except Exception as exc:
        logger.warning("notify owner failed oid=%s uid=%s err=%s", oid, uid, exc)
        return False, str(exc)


async def register_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if has_staff_access(update):
        await message.reply_text("You already have access. Press /start to continue.")
        return

    name, username, uid = user_label(user)
    already_pending = staff_users.has_pending_request(user.id)

    if not already_pending:
        try:
            staff_users.add_pending_request(uid, name, username)
        except ValueError as exc:
            await message.reply_text(str(exc))
            return

    ok, err = await notify_owner_access_request(
        context,
        name=name,
        username=username,
        uid=uid,
    )
    if ok:
        if already_pending:
            await message.reply_text(
                "Your access request is still pending.\n"
                "We re-sent the approval request to the owner.\n"
                "Please wait."
            )
        else:
            await message.reply_text(
                "Access request sent to owner. Please wait for approval."
            )
        return

    if err == "owner_not_configured":
        await message.reply_text(
            "⛔ Owner is not configured on the server.\n"
            f"Your Telegram ID: {uid}\n\n"
            "Please send this ID to the shop owner."
        )
        return

    await message.reply_text(
        "⛔ Could not notify the owner automatically.\n"
        f"Your Telegram ID: {uid}\n\n"
        "Please send this ID to the shop owner, or ask the owner to open the bot "
        "and check 👩‍💼 Staff Mgmt → 🔄 Pending Requests.\n\n"
        f"Error: {err}"
    )


async def staff_access_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    if not is_owner(update):
        await query.answer("Owner only.", show_alert=True)
        return
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 3 or parts[0] != "staff":
        return
    action, uid_raw = parts[1], parts[2]
    try:
        uid = int(uid_raw)
    except ValueError:
        return

    pending = next((r for r in staff_users.list_pending_requests() if int(r["user_id"]) == uid), None)
    name = str(pending.get("name", "Staff")) if pending else "Staff"
    username = str(pending.get("username", "")) if pending else ""

    if action == "approve":
        staff_users.approve_staff(uid, name=name, username=username)
        try:
            await context.bot.send_message(chat_id=uid, text=ACCESS_APPROVED_TEXT)
        except Exception as exc:
            logger.warning("notify approved staff failed uid=%s err=%s", uid, exc)
        if query.message:
            await query.message.reply_text(f"✅ Approved staff ID {uid}")
    elif action == "reject":
        staff_users.reject_staff(uid)
        try:
            await context.bot.send_message(chat_id=uid, text=ACCESS_REJECTED_TEXT)
        except Exception as exc:
            logger.warning("notify rejected staff failed uid=%s err=%s", uid, exc)
        if query.message:
            await query.message.reply_text(f"❌ Rejected staff ID {uid}")


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


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    if not is_owner(update):
        message = update.effective_message
        if message:
            await message.reply_text(OWNER_ACCESS_DENIED)
        return
    if not await ensure_ready_for_main(update, context):
        return
    await send_reply_mgmt_menu(update, context)


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
    if action == "staff_management":
        await send_staff_mgmt_menu(update, context)
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
        await apply_customer_lang(update, context, picked_customer)
        return

    if picked_staff and staff_lang_is_set(context) and not customer_lang_is_set(context):
        set_staff_lang(context, picked_staff)
        await send_customer_lang_menu(update, context)
        return

    if picked_customer and customer_lang_is_set(context):
        await apply_customer_lang(update, context, picked_customer)
        return

    if not await ensure_ready_for_main(update, context):
        return

    if await handle_admin_text(update, context, raw):
        return

    screen = get_active_screen(context)

    if screen in ADMIN_SCREENS:
        if await handle_reply_mgmt_screen(update, context, raw):
            return
        if not is_owner(update):
            await message.reply_text(OWNER_ACCESS_DENIED)
            await send_main_menu(update, context)
            return

    if is_back_button(raw):
        clear_admin_state(context)
        if screen in ADMIN_SCREENS:
            if await handle_reply_mgmt_screen(update, context, raw):
                return
        if screen in (SCREEN_STAFF_MGMT, SCREEN_REMOVE_STAFF):
            set_active_screen(context, SCREEN_MAIN)
            await send_main_menu(update, context)
            return
        await send_main_menu(update, context)
        return

    if screen == SCREEN_STAFF_MGMT and is_owner(update):
        if raw == BTN_STAFF_LIST:
            await send_staff_list(update, context)
            return
        if raw == BTN_REMOVE_STAFF:
            await send_remove_staff_menu(update, context)
            return
        if raw == BTN_PENDING_REQUESTS:
            await send_pending_requests(update, context)
            return
        await send_staff_mgmt_menu(update, context)
        return

    if screen == SCREEN_REMOVE_STAFF and is_owner(update):
        staff_map = context.user_data.get("remove_staff_map") or {}
        if raw in staff_map:
            uid = int(staff_map[raw])
            try:
                staff_users.disable_staff(uid)
                await message.reply_text(f"➖ Staff disabled: {uid}")
            except ValueError as exc:
                await message.reply_text(str(exc))
            context.user_data.pop("remove_staff_map", None)
            set_active_screen(context, SCREEN_STAFF_MGMT)
            await send_staff_mgmt_menu(update, context)
            return
        await send_remove_staff_menu(update, context)
        return

    reply_key = parse_quick_reply_key(raw)
    if reply_key and reply_key in get_quick_replies():
        set_active_screen(context, SCREEN_MAIN)
        staff = get_staff_lang(context)
        markup = build_main_menu_keyboard(staff, is_owner_user=is_owner(update))
        await send_customer_quick_reply(update, context, reply_key, reply_markup=markup)
        return

    if is_main_menu_label(raw):
        await handle_main_menu_choice(update, context, raw)
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


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await deny_if_not_staff(update):
        return
    if await handle_admin_photo(update, context):
        return


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
    app.add_handler(CommandHandler("register", register_cmd))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CommandHandler("lang", language_cmd))
    app.add_handler(CommandHandler("customer", customer_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("health", health_cmd))
    app.add_handler(CallbackQueryHandler(staff_access_callback, pattern=r"^staff:(approve|reject):\d+$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^admin:"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
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
