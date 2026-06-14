"""Fixed quick replies for CHERRY Quick Reply Bot — edit approved text here only."""
from __future__ import annotations

STAFF_LANGS = frozenset({"km", "th", "id"})
CUSTOMER_LANGS = frozenset({"th", "en", "km", "id", "cn"})
DEFAULT_STAFF_LANG = "km"
DEFAULT_CUSTOMER_LANG = "en"

BTN_BACK = "Back/ត្រលប់់"

# Unicode emoji (avoid plain "?" display issues on some clients)
EMOJI_QUESTION = "\U00002753"  # ❓
EMOJI_CROSS = "\U0000274C"  # ❌
EMOJI_WARN = "\U000026A0\U0000FE0F"  # ⚠️

# ── Main menu (same labels for all staff) ─────────────────────────────────────
BTN_MENU_QUESTIONS = f"{EMOJI_QUESTION} Questions To Customer"
BTN_MENU_REPLIES = "\U0001F4AC Replies To Customer"  # 💬
BTN_MENU_CHANGE_CUSTOMER = "🌐 Change Customer Language"
BTN_MENU_CHANGE_STAFF = "👩‍💼 Change Staff Language"
BTN_MENU_CLEAR = "🧹 Clear Session"

MAIN_MENU_ROWS: list[list[str]] = [
    [BTN_MENU_QUESTIONS],
    [BTN_MENU_REPLIES],
    [BTN_MENU_CHANGE_CUSTOMER, BTN_MENU_CHANGE_STAFF],
    [BTN_MENU_CLEAR],
]

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

# ── Menu 1: Questions to customer (staff buttons) ─────────────────────────────
QUESTION_KEY_ORDER: list[str] = [
    "q_separate_wash",
    "q_location",
    "q_house_photo",
    "q_send_location",
    "q_delivery_time",
    "q_pickup_time",
    "q_payment",
    "q_bag_photo",
    "q_confirm_wash",
]

# ── Approved staff buttons (same Khmer labels for all staff languages) ────────
APPROVED_QUESTION_BUTTONS: dict[str, str] = {
    "q_separate_wash": f"{EMOJI_QUESTION} /បោករួមរឺបោកផ្សេង",
    "q_location": f"{EMOJI_QUESTION} /ទីតាំង",
    "q_house_photo": f"{EMOJI_QUESTION} /សូមផ្ញើរូបផ្ទះ",
    "q_send_location": f"{EMOJI_QUESTION} /សូមផ្ញើទីតាំង",
    "q_delivery_time": f"{EMOJI_QUESTION} /ឲ្យបុគ្គលិកដឹកអោយម៉ោងប៉ុន្មាន",
    "q_pickup_time": f"{EMOJI_QUESTION} /ឱ្យបុគ្គលិកទៅយកម៉ោងប៉ុន្មាន",
    "q_payment": f"{EMOJI_QUESTION} /បង់ប្រាក់",
    "q_bag_photo": f"{EMOJI_QUESTION} /សូមផ្ញើរូបកាបូប",
    "q_confirm_wash": f"{EMOJI_QUESTION} /បញ្ជាក់ការបោក",
}

APPROVED_REPLY_BUTTONS: dict[str, str] = {
    "ironing": f"{EMOJI_CROSS} /មិនមានអ៊ុត",
    "no_shoes": f"{EMOJI_CROSS} /មិនមានស្បែកជើង",
    "before_service": f"{EMOJI_WARN} /មុនប្រើសេវា",
}

# Same approved labels regardless of staff language (km/th/id)
QUESTION_BUTTONS: dict[str, dict[str, str]] = {
    lang: dict(APPROVED_QUESTION_BUTTONS) for lang in STAFF_LANGS
}
REPLY_BUTTONS: dict[str, dict[str, str]] = {
    lang: dict(APPROVED_REPLY_BUTTONS) for lang in STAFF_LANGS
}

REPLY_KEY_ORDER: list[str] = [
    "ironing",
    "no_shoes",
    "before_service",
]

# ── Question texts for customer (Thai first; others TODO) ─────────────────────
QUESTIONS: dict[str, dict[str, str]] = {
    "q_separate_wash": {
        "th": "ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
        # TODO: translate EN/KH/ID/CN
        "en": "ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
        "km": "ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
        "id": "ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
        "cn": "ลูกค้าซักแยกหรือซักรวมคะ? ช่วยแจ้งให้ทราบด้วยนะคะ",
    },
    "q_location": {
        "th": "ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
        "en": "ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
        "km": "ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
        "id": "ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
        "cn": "ขอทราบที่อยู่/โลเคชั่นด้วยค่ะ",
    },
    "q_house_photo": {
        "th": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        "en": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        "km": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        "id": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        "cn": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
    },
    "q_send_location": {
        "th": "กรุณาส่งโลเคชั่น (Location) ค่ะ",
        "en": "กรุณาส่งโลเคชั่น (Location) ค่ะ",
        "km": "กรุณาส่งโลเคชั่น (Location) ค่ะ",
        "id": "กรุณาส่งโลเคชั่น (Location) ค่ะ",
        "cn": "กรุณาส่งโลเคชั่น (Location) ค่ะ",
    },
    "q_delivery_time": {
        "th": "ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
        "en": "ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
        "km": "ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
        "id": "ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
        "cn": "ต้องการให้พนักงานส่งผ้ากลับกี่โมงคะ?",
    },
    "q_pickup_time": {
        "th": "ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
        "en": "ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
        "km": "ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
        "id": "ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
        "cn": "ต้องการให้พนักงานไปรับผ้ากี่โมงคะ?",
    },
    "q_payment": {
        "th": "ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
        "en": "ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
        "km": "ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
        "id": "ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
        "cn": "ลูกค้าต้องการชำระเงินแบบไหนคะ? (เงินสด/โอน)",
    },
    "q_bag_photo": {
        "th": "กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
        "en": "กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
        "km": "กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
        "id": "กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
        "cn": "กรุณาส่งรูปถุงผ้า/รูปกระเป๋าค่ะ",
    },
    "q_confirm_wash": {
        "th": "กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
        "en": "กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
        "km": "กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
        "id": "กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
        "cn": "กรุณายืนยันรายการผ้าที่ต้องการซักค่ะ",
    },
}

# ── Approved reply texts (Thai first; others TODO) ────────────────────────────
QUICK_REPLIES: dict[str, dict[str, str]] = {
    "ironing": {
        "th": (
            "❌ ไม่มีบริการรีดผ้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        # TODO: translate EN/KH/ID/CN
        "en": (
            "❌ ไม่มีบริการรีดผ้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "km": (
            "❌ ไม่มีบริการรีดผ้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "id": (
            "❌ ไม่มีบริการรีดผ้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "cn": (
            "❌ ไม่มีบริการรีดผ้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
    },
    "no_shoes": {
        "th": (
            "❌ ไม่มีบริการซักรองเท้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "en": (
            "❌ ไม่มีบริการซักรองเท้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "km": (
            "❌ ไม่มีบริการซักรองเท้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "id": (
            "❌ ไม่มีบริการซักรองเท้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "cn": (
            "❌ ไม่มีบริการซักรองเท้า\n\n"
            "ขออภัยค่ะ\n"
            "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
            "🧺 ซัก\n"
            "🌬️ อบ\n"
            "📦 พับ\n"
            "🚚 รับ-ส่งถึงบ้าน\n\n"
            "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
    },
    "before_service": {
        "th": (
            "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
            "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
            "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
            "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
            "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
            "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซักนะคะ\n\n"
            "🧦 ถุงเท้า\n"
            "🩲 กางเกงใน\n"
            "👶 เสื้อผ้าเด็ก\n"
            "หรือเสื้อผ้าชิ้นเล็ก\n"
            "แนะนำให้ใส่ถุงซักก่อนส่งซัก เพื่อป้องกันการสูญหายหรือปะปนระหว่างการซักค่ะ\n\n"
            "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
            "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
            "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
            "กรุณาแจ้งพนักงานก่อนส่งซักค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "en": (
            "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
            "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
            "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
            "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
            "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
            "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซักนะคะ\n\n"
            "🧦 ถุงเท้า\n"
            "🩲 กางเกงใน\n"
            "👶 เสื้อผ้าเด็ก\n"
            "หรือเสื้อผ้าชิ้นเล็ก\n"
            "แนะนำให้ใส่ถุงซักก่อนส่งซัก เพื่อป้องกันการสูญหายหรือปะปนระหว่างการซักค่ะ\n\n"
            "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
            "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
            "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
            "กรุณาแจ้งพนักงานก่อนส่งซักค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "km": (
            "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
            "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
            "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
            "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
            "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
            "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซักนะคะ\n\n"
            "🧦 ถุงเท้า\n"
            "🩲 กางเกงใน\n"
            "👶 เสื้อผ้าเด็ก\n"
            "หรือเสื้อผ้าชิ้นเล็ก\n"
            "แนะนำให้ใส่ถุงซักก่อนส่งซัก เพื่อป้องกันการสูญหายหรือปะปนระหว่างการซักค่ะ\n\n"
            "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
            "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
            "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
            "กรุณาแจ้งพนักงานก่อนส่งซักค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "id": (
            "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
            "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
            "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
            "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
            "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
            "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซักนะคะ\n\n"
            "🧦 ถุงเท้า\n"
            "🩲 กางเกงใน\n"
            "👶 เสื้อผ้าเด็ก\n"
            "หรือเสื้อผ้าชิ้นเล็ก\n"
            "แนะนำให้ใส่ถุงซักก่อนส่งซัก เพื่อป้องกันการสูญหายหรือปะปนระหว่างการซักค่ะ\n\n"
            "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
            "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
            "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
            "กรุณาแจ้งพนักงานก่อนส่งซักค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
        "cn": (
            "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
            "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
            "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
            "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
            "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
            "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซักนะคะ\n\n"
            "🧦 ถุงเท้า\n"
            "🩲 กางเกงใน\n"
            "👶 เสื้อผ้าเด็ก\n"
            "หรือเสื้อผ้าชิ้นเล็ก\n"
            "แนะนำให้ใส่ถุงซักก่อนส่งซัก เพื่อป้องกันการสูญหายหรือปะปนระหว่างการซักค่ะ\n\n"
            "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
            "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
            "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
            "กรุณาแจ้งพนักงานก่อนส่งซักค่ะ\n\n"
            "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
        ),
    },
}

# ── Lookups ───────────────────────────────────────────────────────────────────
LABEL_TO_QUESTION_KEY: dict[str, str] = {}
LABEL_TO_REPLY_KEY: dict[str, str] = {}
COMMAND_TO_QUESTION_KEY: dict[str, str] = {}
COMMAND_TO_REPLY_KEY: dict[str, str] = {}


def _register_command(cmd_map: dict[str, str], label: str, key: str) -> None:
    cmd_map[label] = key
    cmd_map[label.strip()] = key
    raw = label.strip()
    if "/" in raw:
        token = raw[raw.index("/") :].split()[0].split("@")[0].lower()
        cmd_map[token] = key


for key, label in APPROVED_QUESTION_BUTTONS.items():
    _register_command(LABEL_TO_QUESTION_KEY, label, key)
    _register_command(COMMAND_TO_QUESTION_KEY, label, key)

for key, label in APPROVED_REPLY_BUTTONS.items():
    _register_command(LABEL_TO_REPLY_KEY, label, key)
    _register_command(COMMAND_TO_REPLY_KEY, label, key)


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


def is_back_button(text: str) -> bool:
    return str(text or "").strip() == BTN_BACK


def is_main_menu_label(text: str) -> bool:
    return str(text or "").strip() in {
        BTN_MENU_QUESTIONS,
        BTN_MENU_REPLIES,
        BTN_MENU_CHANGE_CUSTOMER,
        BTN_MENU_CHANGE_STAFF,
        BTN_MENU_CLEAR,
    }


def _rows_one_per_label(labels: list[str]) -> list[list[str]]:
    rows = [[label] for label in labels]
    rows.append([BTN_BACK])
    return rows


def main_menu_rows() -> list[list[str]]:
    return MAIN_MENU_ROWS


def question_menu_rows(staff_lang: str) -> list[list[str]]:
    labels = [APPROVED_QUESTION_BUTTONS[key] for key in QUESTION_KEY_ORDER]
    return _rows_one_per_label(labels)


def reply_menu_rows(staff_lang: str) -> list[list[str]]:
    labels = [APPROVED_REPLY_BUTTONS[key] for key in REPLY_KEY_ORDER]
    return _rows_one_per_label(labels)


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


def question_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = QUESTIONS.get(key, {})
    return block.get(lang, block.get("th", ""))


def quick_reply_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = QUICK_REPLIES.get(key, {})
    return block.get(lang, block.get("th", ""))
