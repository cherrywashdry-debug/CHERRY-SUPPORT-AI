"""Fixed quick replies for CHERRY Quick Reply Bot — edit approved text here only."""
from __future__ import annotations

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
        "back": "ត្រឡប់",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nសូមជ្រើសរើសភាសាបុគ្គលិក:",
        "prompt_customer": "ភាសាបុគ្គលិក: {staff}\n\nសូមជ្រើសរើសភាសាអតិថិជន:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nសូមជ្រើសរើសម៉ឺនុយ:",
        "header_questions": f"{EMOJI_QUESTION} សួរអតិថិជន",
        "header_replies": f"{EMOJI_CHAT} ឆ្លើយអតិថិជន",
        "session_cleared": "លុប Session រួចរាល់",
    },
    "th": {
        "menu_questions": f"{EMOJI_QUESTION} ถามลูกค้า",
        "menu_replies": f"{EMOJI_CHAT} ตอบลูกค้า",
        "menu_change_customer": "🌐 เปลี่ยนภาษาลูกค้า",
        "menu_change_staff": "👩‍💼 เปลี่ยนภาษาพนักงาน",
        "menu_clear": "🧹 ล้าง Session",
        "back": "กลับ",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nกรุณาเลือกภาษาพนักงาน:",
        "prompt_customer": "ภาษาพนักงาน: {staff}\n\nกรุณาเลือกภาษาลูกค้า:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nกรุณาเลือกเมนู:",
        "header_questions": f"{EMOJI_QUESTION} ถามลูกค้า",
        "header_replies": f"{EMOJI_CHAT} ตอบลูกค้า",
        "session_cleared": "ล้าง Session แล้ว",
    },
    "id": {
        "menu_questions": f"{EMOJI_QUESTION} Tanya Pelanggan",
        "menu_replies": f"{EMOJI_CHAT} Balas Pelanggan",
        "menu_change_customer": "🌐 Ganti Bahasa Pelanggan",
        "menu_change_staff": "👩‍💼 Ganti Bahasa Staff",
        "menu_clear": "🧹 Hapus Session",
        "back": "Kembali",
        "prompt_start": "🍒 CHERRY QUICK REPLY\n\nPilih bahasa staff:",
        "prompt_customer": "Bahasa staff: {staff}\n\nPilih bahasa pelanggan:",
        "prompt_main": "🍒 CHERRY QUICK REPLY\n\nPilih menu:",
        "header_questions": f"{EMOJI_QUESTION} Tanya Pelanggan",
        "header_replies": f"{EMOJI_CHAT} Balas Pelanggan",
        "session_cleared": "Session dihapus",
    },
}

# Legacy constants (English — tests / fallback only)
BTN_MENU_QUESTIONS = STAFF_UI["km"]["menu_questions"]
BTN_MENU_REPLIES = STAFF_UI["km"]["menu_replies"]
BTN_MENU_CHANGE_CUSTOMER = STAFF_UI["km"]["menu_change_customer"]
BTN_MENU_CHANGE_STAFF = STAFF_UI["km"]["menu_change_staff"]
BTN_MENU_CLEAR = STAFF_UI["km"]["menu_clear"]

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
    "price": f"{EMOJI_MONEY} /តម្លៃ",
    "delivery_fee": f"{EMOJI_TRUCK} /ថ្លៃដឹក",
    "opening_hours": f"{EMOJI_CLOCK} /ម៉ោងបើក",
    "processing_time": f"{EMOJI_HOURGLASS} /រយៈពេល",
    "points": f"{EMOJI_GIFT} /ពិន្ទុ",
    "ironing": f"{EMOJI_CROSS} /មិនមានអ៊ុត",
    "no_shoes": f"{EMOJI_CROSS} /មិនមានស្បែកជើង",
    "before_service": f"{EMOJI_WARN} /មុនប្រើសេវា",
    # Reply Pack V2
    "laundry_ready": f"{EMOJI_PACKAGE} /រួចរាល់",
    "staff_on_the_way_delivery": f"{EMOJI_TRUCK} /កំពុងទៅ",
    "staff_on_the_way_pickup": f"{EMOJI_SCOOTER} /កំពុងទៅយក",
    "ask_location": f"{EMOJI_PIN} /សូមផ្ញើទីតាំង",
    "ask_home_photo": f"{EMOJI_HOUSE} /សូមផ្ញើរូបផ្ទះ",
    "ask_bag_photo": f"{EMOJI_BAG} /សូមផ្ញើរូបកាបូប",
    "payment_method": f"{EMOJI_CARD} /បង់ប្រាក់",
    "ask_separate_or_together": f"{EMOJI_BASKET} /បោករួមរឺបោកផ្សេង",
}

REPLY_KEY_ORDER: list[str] = [
    "price",
    "delivery_fee",
    "opening_hours",
    "processing_time",
    "points",
    "ironing",
    "no_shoes",
    "before_service",
    # Reply Pack V2
    "laundry_ready",
    "staff_on_the_way_delivery",
    "staff_on_the_way_pickup",
    "ask_location",
    "ask_home_photo",
    "ask_bag_photo",
    "payment_method",
    "ask_separate_or_together",
]

QUESTION_BUTTONS: dict[str, dict[str, str]] = {
    "km": dict(APPROVED_QUESTION_BUTTONS),
    "th": {
        "q_separate_wash": f"{EMOJI_QUESTION} /ซักรวมไหม",
        "q_location": f"{EMOJI_QUESTION} /โลเคชั่น",
        "q_house_photo": f"{EMOJI_QUESTION} /ส่งรูปบ้าน",
        "q_send_location": f"{EMOJI_QUESTION} /ส่งโลเคชั่น",
        "q_delivery_time": f"{EMOJI_QUESTION} /ส่งกี่โมง",
        "q_pickup_time": f"{EMOJI_QUESTION} /รับกี่โมง",
        "q_payment": f"{EMOJI_QUESTION} /ชำระเงิน",
        "q_bag_photo": f"{EMOJI_QUESTION} /ส่งรูปถุงผ้า",
        "q_confirm_wash": f"{EMOJI_QUESTION} /ยืนยันการซัก",
    },
    "id": {
        "q_separate_wash": f"{EMOJI_QUESTION} /campuratauterpisah",
        "q_location": f"{EMOJI_QUESTION} /lokasi",
        "q_house_photo": f"{EMOJI_QUESTION} /fotorumah",
        "q_send_location": f"{EMOJI_QUESTION} /kirimlokasi",
        "q_delivery_time": f"{EMOJI_QUESTION} /antarjamberapa",
        "q_pickup_time": f"{EMOJI_QUESTION} /jemputjamberapa",
        "q_payment": f"{EMOJI_QUESTION} /pembayaran",
        "q_bag_photo": f"{EMOJI_QUESTION} /fototas",
        "q_confirm_wash": f"{EMOJI_QUESTION} /konfirmasicuci",
    },
}

REPLY_BUTTONS: dict[str, dict[str, str]] = {
    "km": dict(APPROVED_REPLY_BUTTONS),
    "th": {
        "price": f"{EMOJI_MONEY} /ราคา",
        "delivery_fee": f"{EMOJI_TRUCK} /ค่าส่ง",
        "opening_hours": f"{EMOJI_CLOCK} /เวลาเปิด",
        "processing_time": f"{EMOJI_HOURGLASS} /ระยะเวลา",
        "points": f"{EMOJI_GIFT} /แต้ม",
        "ironing": f"{EMOJI_CROSS} /ไม่มีรีดผ้า",
        "no_shoes": f"{EMOJI_CROSS} /ไม่มีซักรองเท้า",
        "before_service": f"{EMOJI_WARN} /ก่อนใช้บริการ",
        "laundry_ready": f"{EMOJI_PACKAGE} /พร้อมแล้ว",
        "staff_on_the_way_delivery": f"{EMOJI_TRUCK} /กำลังไปส่ง",
        "staff_on_the_way_pickup": f"{EMOJI_SCOOTER} /กำลังไปรับ",
        "ask_location": f"{EMOJI_PIN} /ส่งโลเคชั่น",
        "ask_home_photo": f"{EMOJI_HOUSE} /ส่งรูปบ้าน",
        "ask_bag_photo": f"{EMOJI_BAG} /ส่งรูปถุงผ้า",
        "payment_method": f"{EMOJI_CARD} /ชำระเงิน",
        "ask_separate_or_together": f"{EMOJI_BASKET} /ซักแยกหรือรวม",
    },
    "id": {
        "price": f"{EMOJI_MONEY} /harga",
        "delivery_fee": f"{EMOJI_TRUCK} /ongkir",
        "opening_hours": f"{EMOJI_CLOCK} /jambuka",
        "processing_time": f"{EMOJI_HOURGLASS} /waktu",
        "points": f"{EMOJI_GIFT} /poin",
        "ironing": f"{EMOJI_CROSS} /tidaksetrika",
        "no_shoes": f"{EMOJI_CROSS} /tidakcucisepatu",
        "before_service": f"{EMOJI_WARN} /sebelumlayanan",
        "laundry_ready": f"{EMOJI_PACKAGE} /sudahsiap",
        "staff_on_the_way_delivery": f"{EMOJI_TRUCK} /sedangantar",
        "staff_on_the_way_pickup": f"{EMOJI_SCOOTER} /sedangjemput",
        "ask_location": f"{EMOJI_PIN} /kirimlokasi",
        "ask_home_photo": f"{EMOJI_HOUSE} /fotorumah",
        "ask_bag_photo": f"{EMOJI_BAG} /fototas",
        "payment_method": f"{EMOJI_CARD} /pembayaran",
        "ask_separate_or_together": f"{EMOJI_BASKET} /campuratauterpisah",
    },
}

# ── Question texts for customer ───────────────────────────────────────────────
def _customer_langs(
    th: str,
    en: str,
    km: str | None = None,
    id_: str | None = None,
    cn: str | None = None,
) -> dict[str, str]:
    return {
        "th": th,
        "en": en,
        "km": km if km is not None else th,  # TODO: approved KH
        "id": id_ if id_ is not None else th,  # TODO: approved ID
        "cn": cn if cn is not None else th,  # TODO: approved CN
    }


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

# ── Approved reply texts by KEY (edit here only) ──────────────────────────────
_REPLY_PRICE_TH = (
    "💰 ราคา\n\n"
    "CHERRY WASH & DRY POIPET 24HR\n\n"
    "🧺 เครื่องเล็ก (14 KG) ราคา 210–240 บาท\n"
    "🧺 เครื่องใหญ่ (18 KG) ราคา 270–300 บาท\n\n"
    "⚠️ คิดราคาต่อเครื่อง\n"
    "❌ ไม่คิดราคาตามกิโลกรัม\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_DELIVERY_FEE_TH = (
    "🚚 ค่าส่ง\n\n"
    "🆓 ไม่เกิน 1 กิโลเมตร ฟรี\n"
    "💵 1–2.5 กิโลเมตร 10 บาท\n"
    "💵 2.5–3 กิโลเมตร 20 บาท\n"
    "💵 มากกว่า 3 กิโลเมตร 50 บาท\n"
    "💵 มากกว่า 4 กิโลเมตร 70 บาท\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_OPENING_HOURS_TH = (
    "⏰ เวลาเปิด\n\n"
    "CHERRY Wash & Dry เปิดบริการ 24 ชั่วโมง\n\n"
    "🚚 รับ-ส่งผ้า\n"
    "เวลา 09:30 – 00:00 น.\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_PROCESSING_TIME_TH = (
    "⏳ ระยะเวลาดำเนินการ\n\n"
    "🚚 รับ-ส่งผ้า\n"
    "โดยปกติใช้เวลาประมาณ 3–4 ชั่วโมง\n"
    "เริ่มนับเวลาหลังจาก\n"
    "✅ รับผ้าเรียบร้อย\n"
    "✅ ตรวจสอบรายการเรียบร้อย\n"
    "✅ ออกบิลเรียบร้อย\n\n"
    "🏪 ลูกค้า Walk-in\n"
    "โดยปกติใช้เวลาประมาณ 2–3 ชั่วโมง\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_POINTS_TH = (
    "🎁 สะสมแต้ม\n\n"
    "🧺 ทุกการใช้บริการที่มียอดตั้งแต่ 240 บาทขึ้นไป\n"
    "ได้รับ 1 แต้ม ต่อ 1 เครื่อง\n\n"
    "🎁 สะสมครบ 13 แต้ม\n"
    "รับเครดิตส่วนลด 200 บาท สำหรับการใช้บริการครั้งถัดไป\n\n"
    "ขอบคุณที่ใช้บริการ CHERRY Wash & Dry ❤️"
)

_REPLY_IRONING_TH = (
    "❌ ไม่มีบริการรีดผ้า\n\n"
    "ขออภัยค่ะ\n"
    "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
    "🧺 ซัก\n"
    "🌬️ อบ\n"
    "📦 พับ\n"
    "🚚 รับ-ส่งถึงบ้าน\n\n"
    "ทางร้านยังไม่มีบริการรีดผ้าค่ะ\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_NO_SHOES_TH = (
    "❌ ไม่มีบริการซักรองเท้า\n\n"
    "ขออภัยค่ะ\n"
    "ปัจจุบัน CHERRY Wash & Dry ให้บริการเฉพาะ\n"
    "🧺 ซัก\n"
    "🌬️ อบ\n"
    "📦 พับ\n"
    "🚚 รับ-ส่งถึงบ้าน\n\n"
    "ทางร้านยังไม่มีบริการซักรองเท้าค่ะ\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_BEFORE_SERVICE_TH = (
    "⚠️ ข้อควรทราบก่อนใช้บริการ\n\n"
    "CHERRY Wash & Dry ให้บริการซักและอบด้วยเครื่องซักผ้าอุตสาหกรรม\n\n"
    "🧺 ลูกค้า 1 ออเดอร์ = 1 เครื่อง\n"
    "❌ ทางร้านไม่ซักรวมกับผ้าของลูกค้าท่านอื่น\n\n"
    "หากลูกค้าต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
    "กรุณาแจ้งพนักงานล่วงหน้าก่อนเริ่มซัก\n\n"
    "🧦 ถุงเท้า\n"
    "🩲 กางเกงใน\n"
    "👶 เสื้อผ้าเด็ก\n"
    "หรือเสื้อผ้าชิ้นเล็ก\n"
    "แนะนำให้ใส่ถุงซักก่อนส่งซัก\n\n"
    "เสื้อผ้าบางชนิดอาจเกิดการหด ย้วย สีซีด สีตก หรือเกิดความเสียหายได้"
    "ตามสภาพเนื้อผ้า อายุการใช้งาน และคุณภาพของวัสดุเดิม\n\n"
    "หากมีเสื้อผ้าพิเศษ เสื้อผ้าราคาแพง หรือผ้าบอบบาง "
    "กรุณาแจ้งพนักงานก่อนส่งซัก\n\n"
    "ขอบคุณที่สอบถาม CHERRY Wash & Dry ❤️"
)

_REPLY_PRICE_EN = (
    "💰 Price\n\n"
    "CHERRY WASH & DRY POIPET 24HR\n\n"
    "🧺 Small machine (14 KG) 210–240 THB\n"
    "🧺 Large machine (18 KG) 270–300 THB\n\n"
    "⚠️ Priced per machine\n"
    "❌ Not priced per kilogram\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_DELIVERY_FEE_EN = (
    "🚚 Delivery Fee\n\n"
    "🆓 Within 1 km — free\n"
    "💵 1–2.5 km — 10 THB\n"
    "💵 2.5–3 km — 20 THB\n"
    "💵 Over 3 km — 50 THB\n"
    "💵 Over 4 km — 70 THB\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_OPENING_HOURS_EN = (
    "⏰ Opening Hours\n\n"
    "CHERRY Wash & Dry is open 24 hours\n\n"
    "🚚 Pickup & delivery\n"
    "09:30 – 00:00\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_PROCESSING_TIME_EN = (
    "⏳ Processing Time\n\n"
    "🚚 Pickup & delivery\n"
    "Usually about 3–4 hours\n"
    "Timing starts after:\n"
    "✅ Laundry received\n"
    "✅ Items checked\n"
    "✅ Invoice issued\n\n"
    "🏪 Walk-in customers\n"
    "Usually about 2–3 hours\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_POINTS_EN = (
    "🎁 Reward Points\n\n"
    "🧺 Every service of 240 THB or more\n"
    "earns 1 point per machine\n\n"
    "🎁 Collect 13 points\n"
    "Get 200 THB credit for your next visit\n\n"
    "Thank you for using CHERRY Wash & Dry ❤️"
)

_REPLY_IRONING_EN = (
    "❌ No ironing service\n\n"
    "Sorry,\n"
    "CHERRY Wash & Dry currently offers:\n"
    "🧺 Wash\n"
    "🌬️ Dry\n"
    "📦 Fold\n"
    "🚚 Home pickup & delivery\n\n"
    "We do not offer ironing at this time.\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_NO_SHOES_EN = (
    "❌ No shoe washing service\n\n"
    "Sorry,\n"
    "CHERRY Wash & Dry currently offers:\n"
    "🧺 Wash\n"
    "🌬️ Dry\n"
    "📦 Fold\n"
    "🚚 Home pickup & delivery\n\n"
    "We do not offer shoe washing at this time.\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

_REPLY_BEFORE_SERVICE_EN = (
    "⚠️ Before using our service\n\n"
    "CHERRY Wash & Dry uses industrial washing machines.\n\n"
    "🧺 1 order = 1 machine\n"
    "❌ We never mix your laundry with other customers\n\n"
    "If you need separate loads for whites, colors, or special items, "
    "please tell staff before washing starts.\n\n"
    "🧦 Socks\n"
    "🩲 Underwear\n"
    "👶 Baby clothes\n"
    "or small items — use a laundry bag before sending.\n\n"
    "Some fabrics may shrink, stretch, fade, or bleed depending on "
    "material, age, and quality.\n\n"
    "For delicate, expensive, or special items, please inform staff "
    "before washing.\n\n"
    "Thank you for asking CHERRY Wash & Dry ❤️"
)

# Reply Pack V2
_REPLY_LAUNDRY_READY_TH = (
    "📦 ผ้าของลูกค้าพร้อมแล้วค่ะ\n\n"
    "ลูกค้าสามารถเข้ามารับที่ร้าน หรือแจ้งให้ทางร้านจัดส่งกลับได้ค่ะ\n\n"
    "ขอบคุณที่ใช้บริการ CHERRY Wash & Dry ❤️"
)

_REPLY_STAFF_ON_THE_WAY_DELIVERY_TH = (
    "🚚 พนักงานกำลังนำผ้าไปส่งให้ลูกค้าค่ะ\n\n"
    "กรุณารอสักครู่ และเตรียมรับผ้าตามโลเคชั่นที่แจ้งไว้ค่ะ\n\n"
    "ขอบคุณที่ไว้วางใจ CHERRY Wash & Dry ❤️"
)

_REPLY_STAFF_ON_THE_WAY_PICKUP_TH = (
    "🛵 พนักงานกำลังไปรับผ้าของลูกค้าค่ะ\n\n"
    "กรุณารอสักครู่ และเตรียมถุงผ้าไว้ที่จุดรับผ้าที่แจ้งไว้ค่ะ\n\n"
    "ขอบคุณที่ไว้วางใจ CHERRY Wash & Dry ❤️"
)

_REPLY_ASK_LOCATION_TH = (
    "📍 กรุณาส่งโลเคชั่นให้ทางร้านด้วยนะคะ\n\n"
    "เพื่อให้พนักงานสามารถตรวจสอบระยะทาง คำนวณค่าส่ง "
    "และเดินทางไปได้ถูกต้องค่ะ ❤️"
)

_REPLY_ASK_HOME_PHOTO_TH = (
    "🏠 กรุณาส่งรูปหน้าบ้าน หรือจุดรับผ้าให้ชัดเจนด้วยนะคะ\n\n"
    "เพื่อให้พนักงานสามารถหาสถานที่รับผ้าได้ง่ายและถูกต้องค่ะ ❤️"
)

_REPLY_ASK_BAG_PHOTO_TH = (
    "👜 กรุณาส่งรูปถุงผ้า หรือกระเป๋าผ้าที่ต้องการให้พนักงานไปรับด้วยนะคะ\n\n"
    "เพื่อให้พนักงานสามารถตรวจสอบและรับผ้าได้ถูกต้องค่ะ ❤️"
)

_REPLY_PAYMENT_METHOD_TH = (
    "💳 ลูกค้าต้องการชำระเงินช่องทางไหนคะ?\n\n"
    "สามารถแจ้งช่องทางที่สะดวกให้ทางร้านทราบได้เลยค่ะ ❤️"
)

_REPLY_ASK_SEPARATE_OR_TOGETHER_TH = (
    "🧺 ลูกค้าต้องการซักแยก หรือซักรวมกันคะ?\n\n"
    "หากต้องการแยกซักผ้าขาว ผ้าสี หรือผ้าประเภทพิเศษ "
    "กรุณาแจ้งให้ทางร้านทราบล่วงหน้าด้วยนะคะ ❤️"
)

_REPLY_LAUNDRY_READY_EN = (
    "📦 Your laundry is ready\n\n"
    "You may pick up at the shop or ask us to deliver it back.\n\n"
    "Thank you for using CHERRY Wash & Dry ❤️"
)

_REPLY_STAFF_ON_THE_WAY_DELIVERY_EN = (
    "🚚 Our staff is on the way to deliver your laundry\n\n"
    "Please wait a moment and be ready to receive it at the location you shared.\n\n"
    "Thank you for trusting CHERRY Wash & Dry ❤️"
)

_REPLY_STAFF_ON_THE_WAY_PICKUP_EN = (
    "🛵 Our staff is on the way to pick up your laundry\n\n"
    "Please wait a moment and have the laundry bag ready at the pickup point you shared.\n\n"
    "Thank you for trusting CHERRY Wash & Dry ❤️"
)

_REPLY_ASK_LOCATION_EN = (
    "📍 Please send your location to us\n\n"
    "So our staff can check the distance, calculate the delivery fee, "
    "and navigate correctly ❤️"
)

_REPLY_ASK_HOME_PHOTO_EN = (
    "🏠 Please send a clear photo of your house or pickup point\n\n"
    "So our staff can find the location easily and correctly ❤️"
)

_REPLY_ASK_BAG_PHOTO_EN = (
    "👜 Please send a photo of the laundry bag you want us to pick up\n\n"
    "So our staff can verify and collect it correctly ❤️"
)

_REPLY_PAYMENT_METHOD_EN = (
    "💳 How would you like to pay?\n\n"
    "Please tell us your preferred payment method ❤️"
)

_REPLY_ASK_SEPARATE_OR_TOGETHER_EN = (
    "🧺 Would you like separate wash or combined wash?\n\n"
    "If you need separate loads for whites, colors, or special items, "
    "please let us know in advance ❤️"
)

QUICK_REPLIES: dict[str, dict[str, str]] = {
    "price": _customer_langs(_REPLY_PRICE_TH, _REPLY_PRICE_EN),
    "delivery_fee": _customer_langs(_REPLY_DELIVERY_FEE_TH, _REPLY_DELIVERY_FEE_EN),
    "opening_hours": _customer_langs(_REPLY_OPENING_HOURS_TH, _REPLY_OPENING_HOURS_EN),
    "processing_time": _customer_langs(_REPLY_PROCESSING_TIME_TH, _REPLY_PROCESSING_TIME_EN),
    "points": _customer_langs(_REPLY_POINTS_TH, _REPLY_POINTS_EN),
    "ironing": _customer_langs(_REPLY_IRONING_TH, _REPLY_IRONING_EN),
    "no_shoes": _customer_langs(_REPLY_NO_SHOES_TH, _REPLY_NO_SHOES_EN),
    "before_service": _customer_langs(_REPLY_BEFORE_SERVICE_TH, _REPLY_BEFORE_SERVICE_EN),
    "laundry_ready": _customer_langs(_REPLY_LAUNDRY_READY_TH, _REPLY_LAUNDRY_READY_EN),
    "staff_on_the_way_delivery": _customer_langs(
        _REPLY_STAFF_ON_THE_WAY_DELIVERY_TH, _REPLY_STAFF_ON_THE_WAY_DELIVERY_EN
    ),
    "staff_on_the_way_pickup": _customer_langs(
        _REPLY_STAFF_ON_THE_WAY_PICKUP_TH, _REPLY_STAFF_ON_THE_WAY_PICKUP_EN
    ),
    "ask_location": _customer_langs(_REPLY_ASK_LOCATION_TH, _REPLY_ASK_LOCATION_EN),
    "ask_home_photo": _customer_langs(_REPLY_ASK_HOME_PHOTO_TH, _REPLY_ASK_HOME_PHOTO_EN),
    "ask_bag_photo": _customer_langs(_REPLY_ASK_BAG_PHOTO_TH, _REPLY_ASK_BAG_PHOTO_EN),
    "payment_method": _customer_langs(_REPLY_PAYMENT_METHOD_TH, _REPLY_PAYMENT_METHOD_EN),
    "ask_separate_or_together": _customer_langs(
        _REPLY_ASK_SEPARATE_OR_TOGETHER_TH, _REPLY_ASK_SEPARATE_OR_TOGETHER_EN
    ),
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


for _lang, buttons in QUESTION_BUTTONS.items():
    for key, label in buttons.items():
        _register_command(LABEL_TO_QUESTION_KEY, label, key)
        _register_command(COMMAND_TO_QUESTION_KEY, label, key)

for _lang, buttons in REPLY_BUTTONS.items():
    for key, label in buttons.items():
        _register_command(LABEL_TO_REPLY_KEY, label, key)
        _register_command(COMMAND_TO_REPLY_KEY, label, key)


def staff_ui(staff_lang: str, key: str) -> str:
    lang = normalize_staff_lang(staff_lang)
    return STAFF_UI[lang].get(key, STAFF_UI[DEFAULT_STAFF_LANG].get(key, ""))


def back_button(staff_lang: str) -> str:
    return staff_ui(staff_lang, "back")


def main_menu_action(text: str) -> str | None:
    raw = str(text or "").strip()
    action_keys = (
        "menu_questions",
        "menu_replies",
        "menu_change_customer",
        "menu_change_staff",
        "menu_clear",
    )
    action_map = {
        "menu_questions": "questions",
        "menu_replies": "replies",
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


def main_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    ui = STAFF_UI[lang]
    return [
        [ui["menu_questions"]],
        [ui["menu_replies"]],
        [ui["menu_change_customer"], ui["menu_change_staff"]],
        [ui["menu_clear"]],
    ]


def question_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    labels = [QUESTION_BUTTONS[lang][key] for key in QUESTION_KEY_ORDER]
    return _rows_one_per_label(labels, lang)


def reply_menu_rows(staff_lang: str) -> list[list[str]]:
    lang = normalize_staff_lang(staff_lang)
    labels = [REPLY_BUTTONS[lang][key] for key in REPLY_KEY_ORDER]
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


def question_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = QUESTIONS.get(key, {})
    return block.get(lang, block.get("th", ""))


def quick_reply_text(key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = QUICK_REPLIES.get(key, {})
    return block.get(lang, block.get("th", ""))
