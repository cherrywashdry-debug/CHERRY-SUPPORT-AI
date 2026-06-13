"""Locked FAQ content for CHERRY SUPPORT AI — edit answers here only.

Structure: FAQ_CONTENT[language][content_key]
Khmer (km) and Indonesian (id) fall back to English until translated.
"""
from __future__ import annotations

SUPPORTED_LANGS = frozenset({"en", "th", "km", "id"})
DEFAULT_LANG = "en"
CONTENT_LANGS = frozenset({"en", "th"})  # km/id use English content fallback

# ── Main menu buttons (same labels for all users) ──────────────────────────────
BTN_PRICE_DELIVERY = "💰 Price / Delivery"
BTN_OPENING_HOURS = "🕒 Opening Hours"
BTN_LAUNDRY = "🧺 Laundry Service"
BTN_PICKUP_DELIVERY = "🚚 Pickup & Delivery"
BTN_REWARDS = "🎁 Rewards / Member"
BTN_READ_BEFORE = "⚠️ Read Before Use Service"
BTN_LOCATION = "📍 Location"
BTN_CONTACT = "☎️ Contact Us"
BTN_CHANGE_LANG = "🌐 Change Language"
BTN_BACK = "⬅️ Back to Menu"

# ── Price / Delivery submenu ───────────────────────────────────────────────────
BTN_LAUNDRY_PRICE = "🧺 Laundry Price"
BTN_DELIVERY_FEE = "🚚 Delivery Fee"

# ── Laundry Service submenu ────────────────────────────────────────────────────
BTN_SEPARATE_MIXED = "🧺 Separate or Mixed?"
BTN_PROCESSING_TIME = "⏳ Processing Time"
BTN_DETERGENT = "🧴 Detergent / Softener"
BTN_NO_IRONING = "❌ No Ironing / No Shoes"

# ── Pickup & Delivery submenu ──────────────────────────────────────────────────
BTN_HOW_PICKUP = "🚚 How to Request Pickup"
BTN_PICKUP_TIME = "🕘 Pickup Time"
BTN_DELIVERY_BACK = "📦 Delivery Back"

# ── Read Before Use submenu ────────────────────────────────────────────────────
BTN_SPECIAL_ITEMS = "⚠️ Special Items"
BTN_VALUABLE = "💎 Valuable Items"
BTN_LAUNDRY_BAG = "🧺 Laundry Bag"
BTN_3DAY = "🕒 3-Day Checking Policy"
BTN_SHOP_RESP = "❌ Shop Responsibility"

# ── Language picker ────────────────────────────────────────────────────────────
BTN_LANG_EN = "🇬🇧 English"
BTN_LANG_TH = "🇹🇭 Thai"
BTN_LANG_KM = "🇰🇭 Khmer"
BTN_LANG_ID = "🇮🇩 Indonesia"

LANG_BUTTONS: dict[str, str] = {
    BTN_LANG_EN: "en",
    BTN_LANG_TH: "th",
    BTN_LANG_KM: "km",
    BTN_LANG_ID: "id",
}

MAIN_MENU_ROWS = [
    [BTN_PRICE_DELIVERY, BTN_OPENING_HOURS],
    [BTN_LAUNDRY, BTN_PICKUP_DELIVERY],
    [BTN_REWARDS, BTN_READ_BEFORE],
    [BTN_LOCATION, BTN_CONTACT],
    [BTN_CHANGE_LANG],
]

PRICE_SUBMENU_ROWS = [
    [BTN_LAUNDRY_PRICE, BTN_DELIVERY_FEE],
    [BTN_BACK],
]

LAUNDRY_SUBMENU_ROWS = [
    [BTN_SEPARATE_MIXED, BTN_PROCESSING_TIME],
    [BTN_DETERGENT, BTN_NO_IRONING],
    [BTN_BACK],
]

PICKUP_SUBMENU_ROWS = [
    [BTN_HOW_PICKUP, BTN_PICKUP_TIME],
    [BTN_DELIVERY_BACK],
    [BTN_BACK],
]

READ_BEFORE_SUBMENU_ROWS = [
    [BTN_SPECIAL_ITEMS, BTN_VALUABLE],
    [BTN_LAUNDRY_BAG, BTN_3DAY],
    [BTN_SHOP_RESP],
    [BTN_BACK],
]

LANG_MENU_ROWS = [
    [BTN_LANG_EN],
    [BTN_LANG_TH],
    [BTN_LANG_KM],
    [BTN_LANG_ID],
    [BTN_BACK],
]

# Maps button label → content key
BUTTON_CONTENT_KEYS: dict[str, str] = {
    BTN_LAUNDRY_PRICE: "price_laundry",
    BTN_DELIVERY_FEE: "price_delivery_fee",
    BTN_OPENING_HOURS: "opening_hours",
    BTN_REWARDS: "rewards",
    BTN_LOCATION: "location",
    BTN_CONTACT: "contact",
    BTN_SEPARATE_MIXED: "laundry_separate",
    BTN_PROCESSING_TIME: "laundry_processing",
    BTN_DETERGENT: "laundry_detergent",
    BTN_NO_IRONING: "laundry_no_ironing",
    BTN_HOW_PICKUP: "pickup_how",
    BTN_PICKUP_TIME: "pickup_time",
    BTN_DELIVERY_BACK: "pickup_delivery_back",
    BTN_SPECIAL_ITEMS: "read_special",
    BTN_VALUABLE: "read_valuable",
    BTN_LAUNDRY_BAG: "read_bag",
    BTN_3DAY: "read_3day",
    BTN_SHOP_RESP: "read_shop_resp",
}

# Category buttons that open a submenu (no direct answer)
SUBMENU_TRIGGERS = frozenset({
    BTN_PRICE_DELIVERY,
    BTN_LAUNDRY,
    BTN_PICKUP_DELIVERY,
    BTN_READ_BEFORE,
})

SUBMENU_FOR_BUTTON: dict[str, str] = {
    BTN_PRICE_DELIVERY: "price",
    BTN_LAUNDRY: "laundry",
    BTN_PICKUP_DELIVERY: "pickup",
    BTN_READ_BEFORE: "read_before",
}

# ── UI strings (welcome, language messages) ───────────────────────────────────
UI_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "welcome": (
            "🍒 CHERRY SUPPORT AI\n\n"
            "Welcome to CHERRY Wash & Dry.\n"
            "Please choose a topic below:"
        ),
        "choose_language": "Please choose your language:",
        "language_set": "Language set to English.",
        "unknown_input": "Please choose a topic from the menu below:",
        "menu_hint": "Main menu:",
    },
    "th": {
        "welcome": (
            "🍒 CHERRY SUPPORT AI\n\n"
            "ยินดีต้อนรับสู่ CHERRY Wash & Dry\n"
            "กรุณาเลือกหัวข้อด้านล่างค่ะ:"
        ),
        "choose_language": "กรุณาเลือกภาษา:",
        "language_set": "ตั้งภาษาเป็นไทยแล้วค่ะ",
        "unknown_input": "กรุณาเลือกหัวข้อจากเมนูด้านล่างค่ะ:",
        "menu_hint": "เมนูหลัก:",
    },
    # TODO: Khmer UI translations
    "km": {
        "welcome": (
            "🍒 CHERRY SUPPORT AI\n\n"
            "Welcome to CHERRY Wash & Dry.\n"
            "Please choose a topic below:"
        ),
        "choose_language": "Please choose your language:",
        "language_set": "Language set to Khmer. (Content in English until translated.)",
        "unknown_input": "Please choose a topic from the menu below:",
        "menu_hint": "Main menu:",
    },
    # TODO: Indonesian UI translations
    "id": {
        "welcome": (
            "🍒 CHERRY SUPPORT AI\n\n"
            "Welcome to CHERRY Wash & Dry.\n"
            "Please choose a topic below:"
        ),
        "choose_language": "Please choose your language:",
        "language_set": "Language set to Indonesian. (Content in English until translated.)",
        "unknown_input": "Please choose a topic from the menu below:",
        "menu_hint": "Main menu:",
    },
}

LANGUAGE_SET_MESSAGES: dict[str, str] = {
    "en": "Language set to English.",
    "th": "ตั้งภาษาเป็นไทยแล้วค่ะ",
    "km": "Language set to Khmer. (FAQ answers in English until Khmer is added.)",
    "id": "Language set to Indonesian. (FAQ answers in English until Indonesian is added.)",
}

# ── FAQ answers ────────────────────────────────────────────────────────────────
FAQ_CONTENT: dict[str, dict[str, str]] = {
    "en": {
        "price_laundry": (
            "💰 CHERRY PRICE LIST\n\n"
            "🧺 14kg Package\n"
            "210 B\n\n"
            "🧺 14kg Premium\n"
            "240 B\n\n"
            "🧺 18kg Package\n"
            "270 B\n\n"
            "🧺 18kg Premium + Extra Dry\n"
            "300 B\n\n"
            "🚚 Delivery fee depends on distance.\n\n"
            "Thank you ❤️"
        ),
        "price_delivery_fee": (
            "🚚 Delivery Fee\n\n"
            "Delivery fee depends on distance from CHERRY Wash & Dry.\n\n"
            "Approximate guide:\n"
            "0–2 km = 10 B\n"
            "2–4 km = 20 B\n"
            "4–6 km = 30 B\n"
            "6–8 km = 40 B\n\n"
            "The bot can calculate the exact delivery fee after customer sends location."
        ),
        "opening_hours": (
            "🕒 Opening Hours\n\n"
            "CHERRY Wash & Dry is open every day.\n\n"
            "Service Hours:\n"
            "09:30 AM – 12:00 AM midnight\n\n"
            "Pickup service starts from:\n"
            "09:30 AM\n\n"
            "If you request pickup after midnight, we will receive your request first "
            "and staff will start pickup from 09:30 AM.\n\n"
            "Thank you ❤️"
        ),
        "rewards": (
            "🎁 Reward Program\n\n"
            "Minimum bill for points:\n"
            "240 B\n\n"
            "1 qualifying order = 1 point\n\n"
            "When you reach 13 points, you are eligible for 200 B reward credit.\n\n"
            "The reward is applied on the next invoice, not the 13th invoice."
        ),
        "location": (
            "📍 CHERRY Wash & Dry Location\n\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7\n\n"
            "Please use the map link to find our shop or send your pickup location."
        ),
        "contact": (
            "☎️ Contact CHERRY Wash & Dry\n\n"
            "WhatsApp:\n"
            "https://wa.me/66942839236\n\n"
            "Phone:\n"
            "+66 94 283 9236\n\n"
            "Opening Hours:\n"
            "09:30 AM – 12:00 AM"
        ),
        "laundry_separate": (
            "🧺 Separate or Mixed?\n\n"
            "Customer 1 order = 1 machine.\n\n"
            "We do not mix your laundry with other customers' laundry in the same machine.\n\n"
            "Your laundry is washed separately for your order."
        ),
        "laundry_processing": (
            "⏳ Processing Time\n\n"
            "Normal processing time:\n"
            "3–4 hours\n\n"
            "Time may be faster or slower depending on laundry amount and queue."
        ),
        "laundry_detergent": (
            "🧴 Detergent & Softener\n\n"
            "We use quality detergent and softener.\n\n"
            "If you have sensitive skin, allergy, or special laundry requirements, "
            "please inform staff before washing."
        ),
        "laundry_no_ironing": (
            "❌ Service Notice\n\n"
            "We do not provide:\n"
            "❌ Ironing\n"
            "❌ Shoe washing\n\n"
            "Thank you for understanding ❤️"
        ),
        "pickup_how": (
            "🚚 How to Request Pickup\n\n"
            "1. Press Express Pickup\n"
            "2. Send your location\n"
            "3. Send a clear home / pickup point photo\n"
            "4. Send a laundry bag photo\n"
            "5. Choose payment method\n"
            "6. Wait for staff confirmation"
        ),
        "pickup_time": (
            "🕘 Pickup Time\n\n"
            "Pickup service starts from 09:30 AM every day.\n\n"
            "If you request pickup between 12:00 AM and 09:29 AM, we will receive your request first.\n\n"
            "Staff will start pickup from 09:30 AM."
        ),
        "pickup_delivery_back": (
            "📦 Delivery Back\n\n"
            "When your laundry is ready, you can request delivery back through the bot.\n\n"
            "Only ready invoices that have not been requested for delivery will be shown."
        ),
        "read_special": (
            "⚠️ Special Items\n\n"
            "Please inform staff before washing if your laundry includes:\n"
            "• Delicate fabric\n"
            "• Expensive clothes\n"
            "• Brand-name clothes\n"
            "• Silk\n"
            "• Lace\n"
            "• Items that may bleed color\n"
            "• Special-care laundry"
        ),
        "read_valuable": (
            "💎 Valuable Items\n\n"
            "Please check your pockets before sending laundry.\n\n"
            "The shop is not responsible for money, jewelry, documents, "
            "or valuable items left inside laundry."
        ),
        "read_bag": (
            "🧺 Laundry Bag\n\n"
            "Small items should be placed inside a laundry bag.\n\n"
            "Underwear and delicate small items should also be placed inside a laundry bag."
        ),
        "read_3day": (
            "🕒 3-Day Checking Policy\n\n"
            "Please check your laundry within 3 days after receiving it.\n\n"
            "If there is any issue, please contact us within 3 days with invoice, "
            "photo, or video if available."
        ),
        "read_shop_resp": (
            "❌ Shop Responsibility\n\n"
            "The shop is not responsible for:\n"
            "• Old stains\n"
            "• Color bleeding / fading\n"
            "• Shrinking from fabric condition\n"
            "• Old or worn fabric\n"
            "• Old zippers\n"
            "• Old buttons\n"
            "• Decorations on clothes\n"
            "• Undeclared special items"
        ),
    },
    "th": {
        "price_laundry": (
            "💰 ราคา CHERRY\n\n"
            "🧺 14kg Package\n"
            "210 บาท\n\n"
            "🧺 14kg Premium\n"
            "240 บาท\n\n"
            "🧺 18kg Package\n"
            "270 บาท\n\n"
            "🧺 18kg Premium + Extra Dry\n"
            "300 บาท\n\n"
            "🚚 ค่าส่งขึ้นอยู่กับระยะทางค่ะ\n\n"
            "ขอบคุณค่ะ ❤️"
        ),
        "price_delivery_fee": (
            "🚚 ค่าส่ง\n\n"
            "ค่าส่งขึ้นอยู่กับระยะทางจากร้าน CHERRY Wash & Dry\n\n"
            "โดยประมาณ:\n"
            "0–2 km = 10 บาท\n"
            "2–4 km = 20 บาท\n"
            "4–6 km = 30 บาท\n"
            "6–8 km = 40 บาท\n\n"
            "ระบบสามารถคำนวณค่าส่งจริงได้หลังลูกค้าส่งโลเคชั่นค่ะ"
        ),
        "opening_hours": (
            "🕒 เวลาเปิดบริการ\n\n"
            "CHERRY Wash & Dry เปิดทุกวัน\n\n"
            "เวลาให้บริการ:\n"
            "09:30 AM – 12:00 AM เที่ยงคืน\n\n"
            "บริการรับผ้าเริ่มตั้งแต่:\n"
            "09:30 AM\n\n"
            "หากลูกค้าส่งคำขอรับผ้าหลังเที่ยงคืน ระบบจะรับคำขอไว้ก่อน "
            "และพนักงานจะเริ่มไปรับผ้าตั้งแต่ 09:30 AM ค่ะ\n\n"
            "ขอบคุณค่ะ ❤️"
        ),
        "rewards": (
            "🎁 ระบบสะสมแต้ม\n\n"
            "ยอดขั้นต่ำสำหรับสะสมแต้ม:\n"
            "240 บาท\n\n"
            "1 ออเดอร์ที่เข้าเงื่อนไข = 1 แต้ม\n\n"
            "เมื่อครบ 13 แต้ม ลูกค้าจะได้รับสิทธิ์เครดิตส่วนลด 200 บาท\n\n"
            "ส่วนลดจะใช้ในบิลถัดไป ไม่ใช่บิลที่ครบ 13 แต้มค่ะ"
        ),
        "location": (
            "📍 โลเคชั่นร้าน CHERRY Wash & Dry\n\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7\n\n"
            "ลูกค้าสามารถใช้ลิงก์นี้เพื่อดูแผนที่ร้าน หรือส่งโลเคชั่นรับผ้าได้ค่ะ"
        ),
        "contact": (
            "☎️ ติดต่อ CHERRY Wash & Dry\n\n"
            "WhatsApp:\n"
            "https://wa.me/66942839236\n\n"
            "โทร:\n"
            "+66 94 283 9236\n\n"
            "เวลาเปิดบริการ:\n"
            "09:30 AM – 12:00 AM"
        ),
        "laundry_separate": (
            "🧺 ซักแยกหรือซักรวม?\n\n"
            "ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n\n"
            "ทางร้านไม่รวมผ้าของลูกค้าคนอื่นในเครื่องเดียวกัน\n\n"
            "ผ้าของคุณจะซักแยกเฉพาะออเดอร์ของคุณค่ะ"
        ),
        "laundry_processing": (
            "⏳ ระยะเวลาดำเนินการ\n\n"
            "โดยปกติใช้เวลา:\n"
            "3–4 ชั่วโมง\n\n"
            "อาจเร็วหรือช้ากว่านี้ขึ้นอยู่กับจำนวนผ้าและคิวงานค่ะ"
        ),
        "laundry_detergent": (
            "🧴 ผงซักฟอก / น้ำยาปรับผ้านุ่ม\n\n"
            "ทางร้านใช้ผงซักฟอกและน้ำยาปรับผ้านุ่มคุณภาพดี\n\n"
            "หากลูกค้าแพ้น้ำหอม ผิวแพ้ง่าย หรือมีความต้องการพิเศษ "
            "กรุณาแจ้งพนักงานก่อนซักค่ะ"
        ),
        "laundry_no_ironing": (
            "❌ ข้อจำกัดบริการ\n\n"
            "ทางร้านไม่มีบริการ:\n"
            "❌ รีดผ้า\n"
            "❌ ซักรองเท้า\n\n"
            "ขอบคุณค่ะ ❤️"
        ),
        "pickup_how": (
            "🚚 วิธีเรียกรับผ้า\n\n"
            "1. กด Express Pickup\n"
            "2. ส่งโลเคชั่น\n"
            "3. ส่งรูปหน้าบ้าน / จุดรับผ้าให้ชัดเจน\n"
            "4. ส่งรูปถุงผ้า\n"
            "5. เลือกวิธีชำระเงิน\n"
            "6. รอพนักงานยืนยันค่ะ"
        ),
        "pickup_time": (
            "🕘 เวลารับผ้า\n\n"
            "บริการรับผ้าเริ่มตั้งแต่ 09:30 AM ทุกวัน\n\n"
            "หากลูกค้าส่งคำขอช่วง 12:00 AM – 09:29 AM ระบบจะรับคำขอไว้ก่อน\n\n"
            "พนักงานจะเริ่มไปรับผ้าตั้งแต่ 09:30 AM ค่ะ"
        ),
        "pickup_delivery_back": (
            "📦 ส่งผ้ากลับ\n\n"
            "เมื่อผ้าของลูกค้าพร้อมแล้ว ลูกค้าสามารถเรียกส่งกลับผ่านบอทได้ค่ะ\n\n"
            "ระบบจะแสดงเฉพาะบิลที่พร้อมส่งกลับ และยังไม่เคยกดเรียกส่งกลับเท่านั้น"
        ),
        "read_special": (
            "⚠️ ผ้าพิเศษ\n\n"
            "กรุณาแจ้งพนักงานก่อนซัก หากมี:\n"
            "• ผ้าบอบบาง\n"
            "• ผ้าราคาแพง\n"
            "• ผ้าแบรนด์เนม\n"
            "• ผ้าไหม\n"
            "• ผ้าลูกไม้\n"
            "• ผ้าที่อาจตกสี\n"
            "• ผ้าที่ต้องดูแลพิเศษ"
        ),
        "read_valuable": (
            "💎 ของมีค่า\n\n"
            "กรุณาตรวจสอบกระเป๋าเสื้อผ้าก่อนส่งซักทุกครั้ง\n\n"
            "ทางร้านไม่รับผิดชอบเงินสด เครื่องประดับ เอกสาร หรือของมีค่าที่อยู่ในผ้าค่ะ"
        ),
        "read_bag": (
            "🧺 ถุงซักผ้า\n\n"
            "ของชิ้นเล็กควรใส่ถุงซักผ้า\n\n"
            "ชุดชั้นในและผ้าชิ้นเล็กที่บอบบาง ควรใส่ถุงซักผ้าก่อนส่งซักค่ะ"
        ),
        "read_3day": (
            "🕒 นโยบายตรวจสอบภายใน 3 วัน\n\n"
            "กรุณาตรวจสอบผ้าภายใน 3 วันหลังได้รับผ้าคืน\n\n"
            "หากมีปัญหา กรุณาติดต่อร้านภายใน 3 วัน พร้อมบิล รูปภาพ หรือวิดีโอ หากมีค่ะ"
        ),
        "read_shop_resp": (
            "❌ สิ่งที่ร้านไม่รับผิดชอบ\n\n"
            "ทางร้านไม่รับผิดชอบ:\n"
            "• คราบเก่า\n"
            "• สีตก / สีซีด\n"
            "• ผ้าหดจากสภาพผ้าเดิม\n"
            "• ผ้าเก่า / ผ้าเสื่อมสภาพ\n"
            "• ซิปเก่า\n"
            "• กระดุมเก่า\n"
            "• ของตกแต่งบนเสื้อผ้า\n"
            "• ผ้าพิเศษที่ไม่ได้แจ้งก่อนซัก"
        ),
    },
    # TODO: Khmer FAQ translations — currently falls back to English
    # TODO: Indonesian FAQ translations — currently falls back to English
}


def normalize_lang(code: str) -> str:
    key = str(code or "").strip().lower()
    return key if key in SUPPORTED_LANGS else DEFAULT_LANG


def content_lang(user_lang: str) -> str:
    """Return language key used for FAQ answer lookup (km/id → en)."""
    lang = normalize_lang(user_lang)
    return lang if lang in CONTENT_LANGS else DEFAULT_LANG


def ui_text(user_lang: str, key: str) -> str:
    lang = normalize_lang(user_lang)
    return UI_LABELS.get(lang, UI_LABELS[DEFAULT_LANG]).get(
        key,
        UI_LABELS[DEFAULT_LANG].get(key, ""),
    )


SUBMENU_INTRO: dict[str, dict[str, str]] = {
    "price": {
        "en": "💰 Price / Delivery — choose a topic:",
        "th": "💰 ราคา / ค่าส่ง — เลือกหัวข้อ:",
        "km": "💰 Price / Delivery — choose a topic:",
        "id": "💰 Price / Delivery — choose a topic:",
    },
    "laundry": {
        "en": "🧺 Laundry Service — choose a topic:",
        "th": "🧺 บริการซักผ้า — เลือกหัวข้อ:",
        "km": "🧺 Laundry Service — choose a topic:",
        "id": "🧺 Laundry Service — choose a topic:",
    },
    "pickup": {
        "en": "🚚 Pickup & Delivery — choose a topic:",
        "th": "🚚 รับ-ส่งผ้า — เลือกหัวข้อ:",
        "km": "🚚 Pickup & Delivery — choose a topic:",
        "id": "🚚 Pickup & Delivery — choose a topic:",
    },
    "read_before": {
        "en": "⚠️ Read Before Use Service — choose a topic:",
        "th": "⚠️ อ่านก่อนใช้บริการ — เลือกหัวข้อ:",
        "km": "⚠️ Read Before Use Service — choose a topic:",
        "id": "⚠️ Read Before Use Service — choose a topic:",
    },
}


def submenu_intro(user_lang: str, submenu: str) -> str:
    lang = normalize_lang(user_lang)
    block = SUBMENU_INTRO.get(submenu, {})
    return block.get(lang, block.get(DEFAULT_LANG, ui_text(lang, "menu_hint")))


def faq_answer(user_lang: str, content_key: str) -> str:
    lang = content_lang(user_lang)
    answers = FAQ_CONTENT.get(lang, FAQ_CONTENT[DEFAULT_LANG])
    return answers.get(content_key, FAQ_CONTENT[DEFAULT_LANG].get(content_key, ""))
