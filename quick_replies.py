"""Fixed quick replies for CHERRY Quick Reply Bot — edit approved text here only."""
from __future__ import annotations

from reply_button_store import category_buttons, category_key_order, load_button_config, reload_button_config
from reply_store import load_replies

STAFF_LANGS = frozenset({"km", "th", "id"})
CUSTOMER_LANGS = frozenset({"th", "en", "km", "id", "cn"})
DEFAULT_STAFF_LANG = "km"
DEFAULT_CUSTOMER_LANG = "en"

BTN_BACK = "Back/ត្រលប់់"  # legacy alias (km uses staff_ui back)

# Unicode emoji (avoid plain "?" display issues on some clients)
EMOJI_QUESTION = "\U00002753"  # ❓
EMOJI_CROSS = "\U0000274C"  # ❌
EMOJI_WARN = "\U000026A0\U0000FE0F"  # ⚠️
EMOJI_CHAT = "\U0001F4AC"  # 💬
EMOJI_MONEY = "\U0001F4B0"  # 💰
EMOJI_TRUCK = "\U0001F69A"  # 🚚
EMOJI_CLOCK = "\U000023F0"  # ⏰
EMOJI_HOURGLASS = "\U000023F3"  # ⏳
EMOJI_GIFT = "\U0001F381"  # 🎁
EMOJI_PACKAGE = "\U0001F4E6"  # 📦
EMOJI_SCOOTER = "\U0001F6F5"  # 🛵
EMOJI_PIN = "\U0001F4CD"  # 📍
EMOJI_HOUSE = "\U0001F3E0"  # 🏠
EMOJI_BAG = "\U0001F45C"  # 👜
EMOJI_CARD = "\U0001F4B3"  # 💳
EMOJI_BASKET = "\U0001F9FA"  # 🧺

# ── Staff UI labels (main menu, back, prompts) ────────────────────────────────
STAFF_UI: dict[str, dict[str, str]] = {
    "km": {
        "menu_questions": f"{EMOJI_QUESTION} សួរអតិថិជន",
        "menu_replies": f"{EMOJI_CHAT} ឆ្លើយអតិថិជន",
        "menu_change_customer": "🌐 ប្តូរភាសាអតិថិជន",
        "menu_change_staff": "👩‍💼 ប្តូរភាសាបុគ្គលិក",
        "menu_clear": "🧹 លុប Session",
        "menu_status": f"{EMOJI_TRUCK} Status Updates",
        "back": "ត្រឡប់",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nសូមជ្រើសរើសភាសាបុគ្គលិក:",
        "prompt_customer": "ភាសាបុគ្គលិក: {staff}\n\nសូមជ្រើសរើសភាសាអតិថិជន:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nភាសាអតិថិជន: {customer}\n\nចុចប៊ូតុងដើម្បី copy ឆ្លើយអតិថិជន:",
        "header_questions": f"{EMOJI_QUESTION} សួរអតិថិជន",
        "header_replies": f"{EMOJI_CHAT} ឆ្លើយអតិថិជន",
        "session_cleared": "លុប Session រួចរាល់",
        "customer_lang_set": "ភាសាអតិថិជន: {name}",
    },
    "th": {
        "menu_questions": f"{EMOJI_QUESTION} ถามลูกค้า",
        "menu_replies": f"{EMOJI_CHAT} ตอบลูกค้า",
        "menu_change_customer": "🌐 เปลี่ยนภาษาลูกค้า",
        "menu_change_staff": "👩‍💼 เปลี่ยนภาษาพนักงาน",
        "menu_clear": "🧹 ล้าง Session",
        "menu_status": f"{EMOJI_TRUCK} Status Updates",
        "back": "กลับ",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nกรุณาเลือกภาษาพนักงาน:",
        "prompt_customer": "ภาษาพนักงาน: {staff}\n\nกรุณาเลือกภาษาลูกค้า:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nภาษาลูกค้า: {customer}\n\nกดปุ่มเพื่อ copy ข้อความตอบลูกค้า:",
        "header_questions": f"{EMOJI_QUESTION} ถามลูกค้า",
        "header_replies": f"{EMOJI_CHAT} ตอบลูกค้า",
        "session_cleared": "ล้าง Session แล้ว",
        "customer_lang_set": "ภาษาลูกค้า: {name}",
    },
    "id": {
        "menu_questions": f"{EMOJI_QUESTION} Tanya Pelanggan",
        "menu_replies": f"{EMOJI_CHAT} Balas Pelanggan",
        "menu_change_customer": "🌐 Ganti Bahasa Pelanggan",
        "menu_change_staff": "👩‍💼 Ganti Bahasa Staff",
        "menu_clear": "🧹 Hapus Session",
        "menu_status": f"{EMOJI_TRUCK} Status Updates",
        "back": "Kembali",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nPilih bahasa staff:",
        "prompt_customer": "Bahasa staff: {staff}\n\nPilih bahasa pelanggan:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nBahasa pelanggan: {customer}\n\nTekan tombol untuk copy balasan pelanggan:",
        "header_questions": f"{EMOJI_QUESTION} Tanya Pelanggan",
        "header_replies": f"{EMOJI_CHAT} Balas Pelanggan",
        "session_cleared": "Session dihapus",
        "customer_lang_set": "Bahasa pelanggan: {name}",
    },
}

# Legacy constants (English — tests / fallback only)
BTN_MENU_QUESTIONS = STAFF_UI["km"]["menu_questions"]
BTN_MENU_REPLIES = STAFF_UI["km"]["menu_replies"]
BTN_MENU_CHANGE_CUSTOMER = STAFF_UI["km"]["menu_change_customer"]
BTN_MENU_CHANGE_STAFF = STAFF_UI["km"]["menu_change_staff"]
BTN_MENU_CLEAR = STAFF_UI["km"]["menu_clear"]
BTN_REPLY_MGMT = "🔧 Reply Mgmt"
BTN_REPLY_MGMT_LEGACY = "🔧 Reply Management"
BTN_EDIT_REPLIES_LEGACY = "🔧 Edit Replies"  # legacy cached keyboard label
BTN_EDIT_REPLIES = BTN_REPLY_MGMT
BTN_STAFF_MGMT = "👩‍💼 Staff Mgmt"
BTN_STAFF_MGMT_LEGACY = "👩‍💼 Staff Management"

KEYBOARD_SHORT_MAX_LEN = 18
KEYBOARD_LONG_MIN_LEN = 25
KEYBOARD_ROW_MAX_SHORT = 3
KEYBOARD_ROW_MAX_MEDIUM = 2

# Staff quick-reply keyboard row order (layout only — reply texts unchanged).
STAFF_KEYBOARD_KEY_ORDER: list[str] = [
    "price",
    "delivery_fee",
    "opening_hours",
    "processing_time",
    "points",
    "laundry_ready",
    "staff_on_the_way_delivery",
    "staff_on_the_way_pickup",
    "ask_location",
    "ask_home_photo",
    "ask_bag_photo",
    "payment_method",
    "ironing",
    "no_shoes",
    "ask_separate_or_together",
    "before_service",
]

BTN_ADMIN_EDIT = "✏️ Edit Reply"
BTN_ADMIN_EDIT_BUTTON = "🏷️ Edit Button"
BTN_ADMIN_SET_EMOJI = "✨ Set Premium Emoji"
BTN_ADMIN_SET_IMAGE = "🖼️ Set Reply Image"
BTN_ADMIN_ADD = "➕ Add Reply"
BTN_ADMIN_DELETE = "➖ Delete Reply"
BTN_ADMIN_BACK = "⬅️ Back"

EDIT_STAFF_LANG_LABELS: dict[str, str] = {
    "km": "🇰🇭 KH Button",
    "th": "🇹🇭 TH Button",
    "id": "🇮🇩 ID Button",
}
LABEL_TO_EDIT_STAFF_LANG: dict[str, str] = {
    label: code for code, label in EDIT_STAFF_LANG_LABELS.items()
}

BTN_CAT_QUESTIONS = "❓ Questions To Customer"
BTN_CAT_REPLIES = "💬 Replies To Customer"
BTN_CAT_STATUS = "🚚 Status Updates"

LABEL_TO_ADMIN_CATEGORY: dict[str, str] = {
    BTN_CAT_QUESTIONS: "questions_to_customer",
    BTN_CAT_REPLIES: "replies_to_customer",
    BTN_CAT_STATUS: "status_updates",
}

EDIT_LANG_LABELS: dict[str, str] = {
    "th": "🇹🇭 TH",
    "en": "🇬🇧 EN",
    "km": "🇰🇭 KH",
    "id": "🇮🇩 ID",
    "cn": "🇨🇳 CN",
}

LABEL_TO_EDIT_LANG: dict[str, str] = {label: code for code, label in EDIT_LANG_LABELS.items()}

OWNER_ACCESS_DENIED = "⛔ Access denied.\nOwner only."

# ── Button mappings loaded from quick_reply_buttons.json ─────────────────────
QUESTION_KEY_ORDER: list[str] = []
REPLY_KEY_ORDER: list[str] = []
STATUS_KEY_ORDER: list[str] = []
QUESTION_BUTTONS: dict[str, dict[str, str]] = {"km": {}, "th": {}, "id": {}}
REPLY_BUTTONS: dict[str, dict[str, str]] = {"km": {}, "th": {}, "id": {}}
STATUS_BUTTONS: dict[str, dict[str, str]] = {"km": {}, "th": {}, "id": {}}
EDIT_REPLY_KEY_LABELS: dict[str, str] = {}
LABEL_TO_EDIT_KEY: dict[str, str] = {}

# ── Staff / customer language pickers ─────────────────────────────────────────
STAFF_LANG_LABELS: dict[str, str] = {
    "km": "🇰🇭 Khmer Staff",
    "th": "🇹🇭 Thai Staff",
    "id": "🇮🇩 Indonesian Staff",
}

CUSTOMER_LANG_LABELS: dict[str, str] = {
    "th": "🇹🇭 Thai Customer",
    "en": "🇬🇧 English Customer",
    "km": "🇰🇭 Khmer Customer",
    "id": "🇮🇩 Indonesian Customer",
    "cn": "🇨🇳 Chinese Customer",
}

STAFF_LANG_ORDER = ["km", "th", "id"]
CUSTOMER_LANG_ORDER = ["th", "en", "km", "id", "cn"]


def lang_picker_rows(labels: dict[str, str], order: list[str]) -> list[list[str]]:
    """Two buttons per row so labels stay readable on mobile."""
    flat = [labels[code] for code in order]
    return [flat[i : i + 2] for i in range(0, len(flat), 2)]

# ── Question texts for customer ───────────────────────────────────────────────
def _customer_langs(
    th: str,
    en: str,
    km: str,
    id_: str,
    cn: str,
) -> dict[str, str]:
    return {"th": th, "en": en, "km": km, "id": id_, "cn": cn}


QUESTIONS: dict[str, dict[str, str]] = {
    "q_separate_wash": _customer_langs(
        th="ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
        en="Would you like separate wash or combined wash? Please let us know.",
        km="តើអ្នកចង់បោកឡែង ឬបោករួម? សូមជូនដំណឹងផងណា។",
        id_="Apakah Anda ingin cuci terpisah atau digabung? Mohon beri tahu kami.",
        cn="请问您要分开洗还是合并洗？请告知我们。",
    ),
    "q_location": _customer_langs(
        th="ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
        en="Please share your address/location.",
        km="សូមផ្ញើអាសយដ្ឋាន/ទីតាំងផងណា។",
        id_="Mohon kirim alamat/lokasi Anda.",
        cn="请发送您的地址/位置。",
    ),
    "q_house_photo": _customer_langs(
        th="กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        en="Please send a clear photo of your house or pickup point.",
        km="សូមផ្ញើរូបផ្ទះ ឬចំណុចទទួលអីវ៉ាត់ឲ្យច្បាស់ផងណា។",
        id_="Mohon kirim foto rumah atau titik penjemputan yang jelas.",
        cn="请发送清晰的门牌或取衣点照片。",
    ),
    "q_send_location": _customer_langs(
        th="กรุณาส่งโลเคชั่น (Location) ค่ะ",
        en="Please send your location (GPS pin).",
        km="សូមផ្ញើ Location (GPS) ផងណា។",
        id_="Mohon kirim lokasi (GPS) Anda.",
        cn="请发送您的位置（GPS）。",
    ),
    "q_delivery_time": _customer_langs(
        th="ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
        en="What time would you like us to deliver your laundry?",
        km="តើអ្នកចង់ឲ្យយើងដឹកអីវ៉ាត់ម៉ោងប៉ុន្មាន?",
        id_="Jam berapa Anda ingin kami antar cucian?",
        cn="您希望几点送达？",
    ),
    "q_pickup_time": _customer_langs(
        th="ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
        en="What time would you like us to pick up your laundry?",
        km="តើអ្នកចង់ឲ្យយើងមកយកអីវ៉ាត់ម៉ោងប៉ុន្មាន?",
        id_="Jam berapa Anda ingin kami jemput cucian?",
        cn="您希望几点上门取衣？",
    ),
    "q_payment": _customer_langs(
        th="ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
        en="How would you like to pay? (Cash/Transfer)",
        km="តើអ្នកចង់បង់ប្រាក់របបណា? (សាច់ប្រាក់/ផ្ទេរ)",
        id_="Bagaimana Anda ingin membayar? (Tunai/Transfer)",
        cn="您希望如何付款？（现金/转账）",
    ),
    "q_bag_photo": _customer_langs(
        th="กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
        en="Please send a photo of the laundry bag.",
        km="សូមផ្ញើរូបថង់អីវ៉ាត់ផងណា។",
        id_="Mohon kirim foto tas cucian.",
        cn="请发送洗衣袋照片。",
    ),
    "q_confirm_wash": _customer_langs(
        th="กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
        en="Please confirm the items you would like us to wash.",
        km="សូមបញ្ជាក់អីវ៉ាត់ដែលចង់បោកផងណា។",
        id_="Mohon konfirmasi item yang ingin dicuci.",
        cn="请确认需要清洗的衣物。",
    ),
}

# ── Reply texts loaded from quick_replies.json (see reply_store.py) ───────────
def get_quick_replies() -> dict[str, dict[str, str]]:
    return load_replies()


def reload_quick_replies() -> dict[str, dict[str, str]]:
    from reply_store import reload_replies

    return reload_replies()


# ── Lookups ───────────────────────────────────────────────────────────────────
LABEL_TO_QUESTION_KEY: dict[str, str] = {}
LABEL_TO_REPLY_KEY: dict[str, str] = {}
LABEL_TO_STATUS_KEY: dict[str, str] = {}
COMMAND_TO_QUESTION_KEY: dict[str, str] = {}
COMMAND_TO_REPLY_KEY: dict[str, str] = {}
COMMAND_TO_STATUS_KEY: dict[str, str] = {}


def _register_command(cmd_map: dict[str, str], label: str, key: str) -> None:
    cmd_map[label] = key
    cmd_map[label.strip()] = key
    raw = label.strip()
    if "/" in raw:
        token = raw[raw.index("/") :].split()[0].split("@")[0].lower()
        cmd_map[token] = key


def keyboard_button_display_text(key: str, full_label: str, *, custom_emoji_id: str | None) -> str:
    """Full button text for Reply Keyboard — never truncated."""
    text = str(full_label or "").strip()
    if custom_emoji_id:
        parts = text.split(None, 1)
        if len(parts) > 1:
            return parts[1].strip() or text
    return text


def keyboard_button_label(key: str, full_label: str) -> str:
    """Legacy compact alias for keyboard parsing (full label is shown on buttons)."""
    text = str(full_label or "").strip()
    parts = text.split(None, 1)
    emoji = parts[0] if parts else "📝"
    if len(parts) > 1:
        suffix = parts[1].split()[0]
        if suffix.startswith("/"):
            return f"{emoji} {suffix}"
    return text


def _is_solo_row_button(text: str) -> bool:
    raw = str(text or "").strip()
    if raw.startswith(EMOJI_WARN):
        return True
    return len(raw) >= KEYBOARD_LONG_MIN_LEN


def _button_width_class(text: str) -> str:
    if _is_solo_row_button(text):
        return "long"
    length = len(str(text or "").strip())
    if length <= KEYBOARD_SHORT_MAX_LEN:
        return "short"
    return "medium"


def pack_button_specs_into_rows(
    specs: list[tuple[str, str | None]],
) -> list[list[tuple[str, str | None]]]:
    """Short labels: up to 3 per row. Medium: up to 2. Long: one per row."""
    rows: list[list[tuple[str, str | None]]] = []
    bucket: list[tuple[str, str | None]] = []

    def flush() -> None:
        nonlocal bucket
        if bucket:
            rows.append(bucket)
            bucket = []

    def bucket_limit() -> int:
        if not bucket:
            return KEYBOARD_ROW_MAX_SHORT
        classes = {_button_width_class(text) for text, _ in bucket}
        if "medium" in classes:
            return KEYBOARD_ROW_MAX_MEDIUM
        return KEYBOARD_ROW_MAX_SHORT

    for spec in specs:
        text, _emoji_id = spec
        width = _button_width_class(text)
        if width == "long":
            flush()
            rows.append([spec])
            continue
        limit = KEYBOARD_ROW_MAX_MEDIUM if width == "medium" else KEYBOARD_ROW_MAX_SHORT
        if bucket:
            current_limit = bucket_limit()
            if len(bucket) >= current_limit or width == "medium" and "short" in {
                _button_width_class(t) for t, _ in bucket
            }:
                flush()
        bucket.append(spec)
        if len(bucket) >= limit:
            flush()

    flush()
    return rows


def _key_picker_label(key: str) -> str:
    for buttons in (REPLY_BUTTONS.get("km", {}), STATUS_BUTTONS.get("km", {}), QUESTION_BUTTONS.get("km", {})):
        raw = buttons.get(key)
        if raw:
            emoji = raw.split()[0] if raw.split() else "📝"
            return f"{emoji} {key}"
    return key


def _load_button_maps() -> None:
    global QUESTION_KEY_ORDER, REPLY_KEY_ORDER, STATUS_KEY_ORDER
    global QUESTION_BUTTONS, REPLY_BUTTONS, STATUS_BUTTONS
    global EDIT_REPLY_KEY_LABELS, LABEL_TO_EDIT_KEY
    global LABEL_TO_QUESTION_KEY, LABEL_TO_REPLY_KEY, LABEL_TO_STATUS_KEY
    global COMMAND_TO_QUESTION_KEY, COMMAND_TO_REPLY_KEY, COMMAND_TO_STATUS_KEY

    from reply_button_store import button_custom_emoji_id, load_button_config

    load_button_config()
    QUESTION_KEY_ORDER = category_key_order("questions_to_customer")
    REPLY_KEY_ORDER = category_key_order("replies_to_customer")
    STATUS_KEY_ORDER = category_key_order("status_updates")
    QUESTION_BUTTONS = {lang: category_buttons("questions_to_customer", lang) for lang in STAFF_LANGS}
    REPLY_BUTTONS = {lang: category_buttons("replies_to_customer", lang) for lang in STAFF_LANGS}
    STATUS_BUTTONS = {lang: category_buttons("status_updates", lang) for lang in STAFF_LANGS}

    reply_keys = sorted(get_quick_replies().keys())
    EDIT_REPLY_KEY_LABELS = {key: _key_picker_label(key) for key in reply_keys}
    LABEL_TO_EDIT_KEY = {label: key for key, label in EDIT_REPLY_KEY_LABELS.items()}

    LABEL_TO_QUESTION_KEY.clear()
    LABEL_TO_REPLY_KEY.clear()
    LABEL_TO_STATUS_KEY.clear()
    COMMAND_TO_QUESTION_KEY.clear()
    COMMAND_TO_REPLY_KEY.clear()
    COMMAND_TO_STATUS_KEY.clear()

    for _lang, buttons in QUESTION_BUTTONS.items():
        for key, label in buttons.items():
            _register_command(LABEL_TO_QUESTION_KEY, label, key)
            _register_command(COMMAND_TO_QUESTION_KEY, label, key)
            kb_label = keyboard_button_label(key, label)
            _register_command(LABEL_TO_QUESTION_KEY, kb_label, key)
            _register_command(COMMAND_TO_QUESTION_KEY, kb_label, key)
            emoji_id = button_custom_emoji_id(key, _lang)
            display = keyboard_button_display_text(key, label, custom_emoji_id=emoji_id)
            _register_command(LABEL_TO_QUESTION_KEY, display, key)
            _register_command(COMMAND_TO_QUESTION_KEY, display, key)

    for _lang, buttons in REPLY_BUTTONS.items():
        for key, label in buttons.items():
            _register_command(LABEL_TO_REPLY_KEY, label, key)
            _register_command(COMMAND_TO_REPLY_KEY, label, key)
            kb_label = keyboard_button_label(key, label)
            _register_command(LABEL_TO_REPLY_KEY, kb_label, key)
            _register_command(COMMAND_TO_REPLY_KEY, kb_label, key)
            emoji_id = button_custom_emoji_id(key, _lang)
            display = keyboard_button_display_text(key, label, custom_emoji_id=emoji_id)
            _register_command(LABEL_TO_REPLY_KEY, display, key)
            _register_command(COMMAND_TO_REPLY_KEY, display, key)

    for _lang, buttons in STATUS_BUTTONS.items():
        for key, label in buttons.items():
            _register_command(LABEL_TO_STATUS_KEY, label, key)
            _register_command(COMMAND_TO_STATUS_KEY, label, key)
            kb_label = keyboard_button_label(key, label)
            _register_command(LABEL_TO_STATUS_KEY, kb_label, key)
            _register_command(COMMAND_TO_STATUS_KEY, kb_label, key)
            emoji_id = button_custom_emoji_id(key, _lang)
            display = keyboard_button_display_text(key, label, custom_emoji_id=emoji_id)
            _register_command(LABEL_TO_STATUS_KEY, display, key)
            _register_command(COMMAND_TO_STATUS_KEY, display, key)


def refresh_button_maps() -> None:
    reload_button_config()
    _load_button_maps()


_load_button_maps()


def staff_ui(staff_lang: str, key: str) -> str:
    lang = normalize_staff_lang(staff_lang)
    return STAFF_UI[lang].get(key, STAFF_UI[DEFAULT_STAFF_LANG].get(key, ""))


def back_button(staff_lang: str) -> str:
    return staff_ui(staff_lang, "back")


def is_reply_management_main_label(text: str) -> bool:
    raw = str(text or "").strip()
    return raw in (BTN_REPLY_MGMT, BTN_REPLY_MGMT_LEGACY, BTN_EDIT_REPLIES_LEGACY)


def main_menu_action(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw == BTN_STAFF_MGMT or raw == BTN_STAFF_MGMT_LEGACY:
        return "staff_management"
    action_keys = (
        "menu_change_customer",
        "menu_change_staff",
        "menu_clear",
    )
    action_map = {
        "menu_change_customer": "change_customer",
        "menu_change_staff": "change_staff",
        "menu_clear": "clear",
    }
    for lang in STAFF_LANGS:
        ui = STAFF_UI[lang]
        for ui_key in action_keys:
            if raw == ui[ui_key]:
                return action_map[ui_key]
    return None


def normalize_staff_lang(code: str) -> str:
    key = str(code or "").strip().lower()
    return key if key in STAFF_LANGS else DEFAULT_STAFF_LANG


def normalize_customer_lang(code: str) -> str:
    key = str(code or "").strip().lower()
    return key if key in CUSTOMER_LANGS else DEFAULT_CUSTOMER_LANG


def staff_lang_from_label(label: str) -> str | None:
    text = str(label or "").strip()
    for code, btn in STAFF_LANG_LABELS.items():
        if text == btn:
            return code
    return None


def customer_lang_from_label(label: str) -> str | None:
    text = str(label or "").strip()
    for code, btn in CUSTOMER_LANG_LABELS.items():
        if text == btn:
            return code
    return None


def is_back_button(text: str, staff_lang: str | None = None) -> bool:
    raw = str(text or "").strip()
    if staff_lang:
        return raw == back_button(staff_lang)
    return any(raw == STAFF_UI[lang]["back"] for lang in STAFF_LANGS)


def is_main_menu_label(text: str) -> bool:
    return main_menu_action(text) is not None


def _rows_one_per_label(labels: list[str], staff_lang: str) -> list[list[str]]:
    rows = [labels[i : i + 2] for i in range(0, len(labels), 2)]
    rows.append([back_button(staff_lang)])
    return rows


def unified_reply_key_order() -> list[str]:
    reply_keys = set(get_quick_replies().keys())
    seen: set[str] = set()
    ordered: list[str] = []
    for key in STAFF_KEYBOARD_KEY_ORDER + REPLY_KEY_ORDER + STATUS_KEY_ORDER:
        if key in reply_keys and key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def unified_button_specs(staff_lang: str) -> list[tuple[str, str | None]]:
    from reply_button_store import button_custom_emoji_id

    lang = normalize_staff_lang(staff_lang)
    specs: list[tuple[str, str | None]] = []
    for key in unified_reply_key_order():
        label = REPLY_BUTTONS[lang].get(key) or STATUS_BUTTONS[lang].get(key)
        if not label:
            continue
        emoji_id = button_custom_emoji_id(key, lang)
        text = keyboard_button_display_text(key, label, custom_emoji_id=emoji_id)
        specs.append((text, emoji_id))
    return specs


def staff_quick_reply_keyboard_rows(
    staff_lang: str,
    *,
    show_staff_management: bool = False,
) -> list[list[tuple[str, str | None]]]:
    lang = normalize_staff_lang(staff_lang)
    ui = STAFF_UI[lang]
    specs = unified_button_specs(staff_lang)
    rows = pack_button_specs_into_rows(specs)
    rows.append([(ui["menu_change_staff"], None), (ui["menu_change_customer"], None)])
    rows.append([(ui["menu_clear"], None)])
    if show_staff_management:
        rows.append([(BTN_STAFF_MGMT, None)])
    return rows


def main_menu_rows(
    staff_lang: str,
    *,
    show_reply_management: bool = False,
    show_staff_management: bool = False,
) -> list[list[str]]:
    """Legacy string rows for tests — toolbar only (no reply buttons)."""
    lang = normalize_staff_lang(staff_lang)
    ui = STAFF_UI[lang]
    rows: list[list[str]] = [
        [ui["menu_change_staff"], ui["menu_change_customer"]],
        [ui["menu_clear"]],
    ]
    if show_staff_management:
        rows.append([BTN_STAFF_MGMT])
    return rows


def admin_reply_mgmt_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    return [
        [BTN_ADMIN_EDIT],
        [BTN_ADMIN_EDIT_BUTTON, BTN_ADMIN_SET_EMOJI],
        [BTN_ADMIN_SET_IMAGE],
        [BTN_ADMIN_ADD],
        [BTN_ADMIN_DELETE],
        [BTN_ADMIN_BACK, back_button(lang)],
    ]


def admin_category_menu_rows() -> list[list[str]]:
    return [
        [BTN_CAT_QUESTIONS],
        [BTN_CAT_REPLIES],
        [BTN_CAT_STATUS],
    ]


def edit_reply_key_menu_rows(staff_lang: str) -> list[list[str]]:
    rows = [
        [EDIT_REPLY_KEY_LABELS[key]]
        for key in REPLY_KEY_ORDER
        if key in EDIT_REPLY_KEY_LABELS
    ]
    lang = normalize_staff_lang(staff_lang)
    rows.append([BTN_ADMIN_BACK, back_button(lang)])
    return rows


def admin_key_menu_rows(staff_lang: str) -> list[list[str]]:
    rows = [[EDIT_REPLY_KEY_LABELS[key]] for key in sorted(get_quick_replies().keys())]
    lang = normalize_staff_lang(staff_lang)
    rows.append([BTN_ADMIN_BACK, back_button(lang)])
    return rows


def admin_button_key_menu_rows(staff_lang: str) -> list[list[str]]:
    from reply_button_store import all_managed_keys, button_label

    lang = normalize_staff_lang(staff_lang)
    rows: list[list[str]] = []
    for key in all_managed_keys():
        current = button_label(key, lang) or key
        rows.append([f"🏷️ {key} ({current})"])
    rows.append([BTN_ADMIN_BACK, back_button(lang)])
    return rows


def parse_admin_button_key(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw.startswith("🏷️ "):
        body = raw[2:].strip()
        key = body.split(" (", 1)[0].strip()
        return key or None
    return parse_edit_reply_key(raw)


def edit_staff_lang_menu_rows() -> list[list[str]]:
    return [
        [EDIT_STAFF_LANG_LABELS["km"]],
        [EDIT_STAFF_LANG_LABELS["th"], EDIT_STAFF_LANG_LABELS["id"]],
    ]


def parse_edit_staff_lang(text: str) -> str | None:
    return LABEL_TO_EDIT_STAFF_LANG.get(str(text or "").strip())


def parse_admin_category(text: str) -> str | None:
    return LABEL_TO_ADMIN_CATEGORY.get(str(text or "").strip())


def edit_lang_menu_rows() -> list[list[str]]:
    return [
        [EDIT_LANG_LABELS["th"], EDIT_LANG_LABELS["en"]],
        [EDIT_LANG_LABELS["km"], EDIT_LANG_LABELS["id"]],
        [EDIT_LANG_LABELS["cn"]],
    ]


def parse_edit_reply_key(text: str) -> str | None:
    return LABEL_TO_EDIT_KEY.get(str(text or "").strip())


def parse_edit_lang(text: str) -> str | None:
    return LABEL_TO_EDIT_LANG.get(str(text or "").strip())


def edit_lang_display(code: str) -> str:
    return EDIT_LANG_LABELS.get(normalize_customer_lang(code), code)


def _category_button_specs(staff_lang: str, category: str) -> list[tuple[str, str | None]]:
    from reply_button_store import button_custom_emoji_id

    lang = normalize_staff_lang(staff_lang)
    if category == "questions":
        order, buttons = QUESTION_KEY_ORDER, QUESTION_BUTTONS[lang]
    elif category == "replies":
        order, buttons = REPLY_KEY_ORDER, REPLY_BUTTONS[lang]
    else:
        order, buttons = STATUS_KEY_ORDER, STATUS_BUTTONS[lang]

    specs: list[tuple[str, str | None]] = []
    for key in order:
        if key not in buttons:
            continue
        label = buttons[key]
        emoji_id = button_custom_emoji_id(key, lang)
        text = keyboard_button_display_text(key, label, custom_emoji_id=emoji_id)
        specs.append((text, emoji_id))
    return specs


def category_menu_button_rows(staff_lang: str, category: str) -> list[list[tuple[str, str | None]]]:
    return pack_button_specs_into_rows(_category_button_specs(staff_lang, category))


def _category_keyboard_labels(staff_lang: str, category: str) -> list[str]:
    lang = normalize_staff_lang(staff_lang)
    if category == "questions":
        order, buttons = QUESTION_KEY_ORDER, QUESTION_BUTTONS[lang]
    elif category == "replies":
        order, buttons = REPLY_KEY_ORDER, REPLY_BUTTONS[lang]
    else:
        order, buttons = STATUS_KEY_ORDER, STATUS_BUTTONS[lang]
    return [keyboard_button_label(key, buttons[key]) for key in order if key in buttons]


def question_menu_rows(staff_lang: str) -> list[list[str]]:
    return _rows_one_per_label(_category_keyboard_labels(staff_lang, "questions"), normalize_staff_lang(staff_lang))


def reply_menu_rows(staff_lang: str) -> list[list[str]]:
    return _rows_one_per_label(_category_keyboard_labels(staff_lang, "replies"), normalize_staff_lang(staff_lang))


def status_menu_rows(staff_lang: str) -> list[list[str]]:
    return _rows_one_per_label(_category_keyboard_labels(staff_lang, "status"), normalize_staff_lang(staff_lang))


def parse_quick_reply_key(text: str) -> str | None:
    key = parse_reply_label(text)
    if key:
        return key
    return parse_status_label(text)


def parse_question_label(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw in LABEL_TO_QUESTION_KEY:
        return LABEL_TO_QUESTION_KEY[raw]
    if raw.startswith("/"):
        token = raw.split()[0].split("@")[0].lower()
        return COMMAND_TO_QUESTION_KEY.get(token)
    return None


def parse_reply_label(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw in LABEL_TO_REPLY_KEY:
        return LABEL_TO_REPLY_KEY[raw]
    if raw.startswith("/"):
        token = raw.split()[0].split("@")[0].lower()
        return COMMAND_TO_REPLY_KEY.get(token)
    return None


def parse_status_label(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw in LABEL_TO_STATUS_KEY:
        return LABEL_TO_STATUS_KEY[raw]
    if raw.startswith("/"):
        token = raw.split()[0].split("@")[0].lower()
        return COMMAND_TO_STATUS_KEY.get(token)
    return None


def question_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = get_quick_replies().get(key) or QUESTIONS.get(key, {})
    return block.get(lang, block.get("th", ""))


def quick_reply_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = get_quick_replies().get(key, {})
    return block.get(lang, block.get("th", ""))


def quick_reply_image_file_id(key: str, customer_lang: str) -> str:
    from reply_image_store import get_image_file_id

    lang = normalize_customer_lang(customer_lang)
    return get_image_file_id(key, lang)
