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
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nសូមជ្រើសរើសម៉ឺនុយ:",
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
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nกรุณาเลือกเมนู:",
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
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nPilih menu:",
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
BTN_REPLY_MGMT = "🔧 Reply Management"
BTN_EDIT_REPLIES_LEGACY = "🔧 Edit Replies"  # legacy cached keyboard label
BTN_EDIT_REPLIES = BTN_REPLY_MGMT

BTN_ADMIN_EDIT = "✏️ Edit Reply"
BTN_ADMIN_ADD = "➕ Add Reply"
BTN_ADMIN_DELETE = "➖ Delete Reply"
BTN_ADMIN_BACK = "⬅️ Back"

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

    for _lang, buttons in REPLY_BUTTONS.items():
        for key, label in buttons.items():
            _register_command(LABEL_TO_REPLY_KEY, label, key)
            _register_command(COMMAND_TO_REPLY_KEY, label, key)

    for _lang, buttons in STATUS_BUTTONS.items():
        for key, label in buttons.items():
            _register_command(LABEL_TO_STATUS_KEY, label, key)
            _register_command(COMMAND_TO_STATUS_KEY, label, key)


def refresh_button_maps() -> None:
    reload_button_config()
    _load_button_maps()


_load_button_maps()


def staff_ui(staff_lang: str, key: str) -> str:
    lang = normalize_staff_lang(staff_lang)
    return STAFF_UI[lang].get(key, STAFF_UI[DEFAULT_STAFF_LANG].get(key, ""))


def back_button(staff_lang: str) -> str:
    return staff_ui(staff_lang, "back")


def main_menu_action(text: str) -> str | None:
    raw = str(text or "").strip()
    if raw in (BTN_REPLY_MGMT, BTN_EDIT_REPLIES_LEGACY):
        return "reply_management"
    action_keys = (
        "menu_questions",
        "menu_replies",
        "menu_status",
        "menu_change_customer",
        "menu_change_staff",
        "menu_clear",
    )
    action_map = {
        "menu_questions": "questions",
        "menu_replies": "replies",
        "menu_status": "status",
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
    rows = [[label] for label in labels]
    rows.append([back_button(staff_lang)])
    return rows


def main_menu_rows(staff_lang: str, *, show_reply_management: bool = False) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    ui = STAFF_UI[lang]
    rows = [
        [ui["menu_questions"]],
        [ui["menu_replies"]],
    ]
    if STATUS_KEY_ORDER:
        rows.append([ui["menu_status"]])
    if show_reply_management:
        rows.append([BTN_REPLY_MGMT])
    rows.extend(
        [
            [ui["menu_change_customer"], ui["menu_change_staff"]],
            [ui["menu_clear"]],
        ]
    )
    return rows


def admin_reply_mgmt_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    return [
        [BTN_ADMIN_EDIT],
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


def question_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    labels = [QUESTION_BUTTONS[lang][key] for key in QUESTION_KEY_ORDER]
    return _rows_one_per_label(labels, lang)


def reply_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    labels = [REPLY_BUTTONS[lang][key] for key in REPLY_KEY_ORDER]
    return _rows_one_per_label(labels, lang)


def status_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    labels = [STATUS_BUTTONS[lang][key] for key in STATUS_KEY_ORDER]
    return _rows_one_per_label(labels, lang)


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
