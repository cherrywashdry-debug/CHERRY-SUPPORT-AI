"""Fixed quick replies for CHERRY Quick Reply Bot — edit approved text here only."""
from __future__ import annotations

STAFF_LANGS = frozenset({"km", "th", "id"})
CUSTOMER_LANGS = frozenset({"th", "en", "km", "id", "cn"})
DEFAULT_STAFF_LANG = "km"
DEFAULT_CUSTOMER_LANG = "en"

# ── Staff language picker ──────────────────────────────────────────────────────
STAFF_LANG_LABELS: dict[str, str] = {
    "km": "🇰🇭 Khmer Staff",
    "th": "🇹🇭 Thai Staff",
    "id": "🇮🇩 Indonesian Staff",
}

# ── Customer language picker ───────────────────────────────────────────────────
CUSTOMER_LANG_LABELS: dict[str, str] = {
    "th": "🇹🇭 Thai Customer",
    "en": "🇬🇧 English Customer",
    "km": "🇰🇭 Khmer Customer",
    "id": "🇮🇩 Indonesian Customer",
    "cn": "🇨🇳 Chinese Customer",
}

# ── Staff command buttons per language ─────────────────────────────────────────
STAFF_BUTTONS: dict[str, dict[str, str]] = {
    "km": {
        "price": "/តម្លៃ",
        "delivery_fee": "/ថ្លៃដឹក",
        "opening_hours": "/ម៉ោងបើក",
        "processing_time": "/រយៈពេល",
        "separate": "/បោករួម",
        "pickup_delivery": "/ដឹកជញ្ជូន",
        "ironing": "/អ៊ុត",
        "shoes": "/ស្បែកជើង",
        "points": "/ពិន្ទុ",
        "ready": "/រួចរាល់",
        "on_the_way": "/កំពុងទៅ",
        "location": "/ទីតាំង",
        "house_photo": "/រូបផ្ទះ",
        "bag_photo": "/រូបថង់",
        "problem": "/បញ្ហា",
        "policy": "/គោលការណ៍",
    },
    "th": {
        "price": "/ราคา",
        "delivery_fee": "/ค่าส่ง",
        "opening_hours": "/เวลาเปิด",
        "processing_time": "/ระยะเวลา",
        "separate": "/ซักรวมไหม",
        "pickup_delivery": "/รับส่ง",
        "ironing": "/รีดผ้า",
        "shoes": "/รองเท้า",
        "points": "/แต้ม",
        "ready": "/ผ้าพร้อมแล้ว",
        "on_the_way": "/กำลังไป",
        "location": "/โลเคชั่น",
        "house_photo": "/รูปบ้าน",
        "bag_photo": "/รูปถุงผ้า",
        "problem": "/ปัญหา",
        "policy": "/นโยบาย",
    },
    "id": {
        "price": "/harga",
        "delivery_fee": "/ongkir",
        "opening_hours": "/jambuka",
        "processing_time": "/waktu",
        "separate": "/campur",
        "pickup_delivery": "/antarjemput",
        "ironing": "/setrika",
        "shoes": "/sepatu",
        "points": "/poin",
        "ready": "/siap",
        "on_the_way": "/otw",
        "location": "/lokasi",
        "house_photo": "/fotorumah",
        "bag_photo": "/fototas",
        "problem": "/masalah",
        "policy": "/kebijakan",
    },
}

# ── Fixed customer replies (TH, EN, KH, ID, CN) ────────────────────────────────
QUICK_REPLIES: dict[str, dict[str, str]] = {
    "price": {
        "en": (
            "💰 CHERRY Price\n\n"
            "14kg Package — 210 B\n"
            "14kg Premium — 240 B\n"
            "18kg Package — 270 B\n"
            "18kg Premium + Extra Dry — 300 B\n\n"
            "Delivery fee depends on distance. Thank you ❤️"
        ),
        "th": (
            "💰 ราคา CHERRY\n\n"
            "14kg Package — 210 บาท\n"
            "14kg Premium — 240 บาท\n"
            "18kg Package — 270 บาท\n"
            "18kg Premium + Extra Dry — 300 บาท\n\n"
            "ค่าส่งขึ้นอยู่กับระยะทางค่ะ ขอบคุณค่ะ ❤️"
        ),
        "km": (
            "💰 តម្លៃ CHERRY\n\n"
            "14kg Package — 210 B\n"
            "14kg Premium — 240 B\n"
            "18kg Package — 270 B\n"
            "18kg Premium + Extra Dry — 300 B\n\n"
            "ថ្លៃដឹកផ្អែកលើចម្ងាយ។ អរគុណបង ❤️"
        ),
        "id": (
            "💰 Harga CHERRY\n\n"
            "14kg Package — 210 B\n"
            "14kg Premium — 240 B\n"
            "18kg Package — 270 B\n"
            "18kg Premium + Extra Dry — 300 B\n\n"
            "Ongkir tergantung jarak. Terima kasih ❤️"
        ),
        "cn": (
            "💰 CHERRY 价格\n\n"
            "14kg 套餐 — 210 泰铢\n"
            "14kg 高级 — 240 泰铢\n"
            "18kg 套餐 — 270 泰铢\n"
            "18kg 高级 + 额外烘干 — 300 泰铢\n\n"
            "配送费按距离计算。谢谢 ❤️"
        ),
    },
    "delivery_fee": {
        "en": (
            "🚚 Delivery fee depends on distance from CHERRY Wash & Dry.\n\n"
            "Approximate guide:\n"
            "0–2 km = 10 B\n"
            "2–4 km = 20 B\n"
            "4–6 km = 30 B\n"
            "6–8 km = 40 B\n\n"
            "Send your location for the exact fee."
        ),
        "th": (
            "🚚 ค่าส่งขึ้นอยู่กับระยะทางจากร้าน CHERRY Wash & Dry\n\n"
            "โดยประมาณ:\n"
            "0–2 km = 10 บาท\n"
            "2–4 km = 20 บาท\n"
            "4–6 km = 30 บาท\n"
            "6–8 km = 40 บาท\n\n"
            "ส่งโลเคชั่นเพื่อคำนวณค่าส่งจริงได้ค่ะ"
        ),
        "km": (
            "🚚 ថ្លៃដឹកផ្អែកលើចម្ងាយពី CHERRY Wash & Dry\n\n"
            "ប៉ាន់ស្មាន:\n"
            "0–2 km = 10 B\n"
            "2–4 km = 20 B\n"
            "4–6 km = 30 B\n"
            "6–8 km = 40 B\n\n"
            "សូមផ្ញើទីតាំងដើម្បីគណនាថ្លៃដឹកពិតប្រាកដ។"
        ),
        "id": (
            "🚚 Ongkir tergantung jarak dari CHERRY Wash & Dry.\n\n"
            "Perkiraan:\n"
            "0–2 km = 10 B\n"
            "2–4 km = 20 B\n"
            "4–6 km = 30 B\n"
            "6–8 km = 40 B\n\n"
            "Kirim lokasi untuk ongkir pasti."
        ),
        "cn": (
            "🚚 配送费按与 CHERRY Wash & Dry 的距离计算。\n\n"
            "参考:\n"
            "0–2 km = 10 泰铢\n"
            "2–4 km = 20 泰铢\n"
            "4–6 km = 30 泰铢\n"
            "6–8 km = 40 泰铢\n\n"
            "请发送位置以计算准确配送费。"
        ),
    },
    "opening_hours": {
        "en": (
            "🕒 CHERRY Wash & Dry is open every day.\n\n"
            "Service hours: 09:30 AM – 12:00 AM midnight\n"
            "Pickup starts from 09:30 AM.\n\n"
            "Requests after midnight are received first; pickup starts at 09:30 AM."
        ),
        "th": (
            "🕒 CHERRY Wash & Dry เปิดทุกวันค่ะ\n\n"
            "เวลาให้บริการ: 09:30 – 00:00\n"
            "รับผ้าเริ่ม 09:30 น.\n\n"
            "หลังเที่ยงคืนระบบรับคำขอไว้ก่อน พนักงานเริ่มรับ 09:30 น."
        ),
        "km": (
            "🕒 CHERRY Wash & Dry បើករាល់ថ្ងៃ\n\n"
            "ម៉ោងសេវា: 09:30 AM – 12:00 AM\n"
            "ទទួលខោអាវចាប់ផ្តើម 09:30 AM\n\n"
            "ក្រោយពេលកណ្តាលយប់ យើងទទួលសំណើមុន ហើយចាប់ផ្តើមទៅយក 09:30 AM។"
        ),
        "id": (
            "🚪 CHERRY Wash & Dry buka setiap hari.\n\n"
            "Jam layanan: 09:30 – 00:00\n"
            "Pickup mulai 09:30.\n\n"
            "Permintaan setelah tengah malam diterima dulu; pickup mulai 09:30."
        ),
        "cn": (
            "🕒 CHERRY Wash & Dry 每天营业。\n\n"
            "服务时间: 09:30 – 00:00\n"
            "取件从 09:30 开始。\n\n"
            "午夜后的请求会先受理，取件从 09:30 开始。"
        ),
    },
    "processing_time": {
        "en": "Normal processing time is 3–4 hours, depending on laundry amount and queue.",
        "th": "ระยะเวลาซักปกติ 3–4 ชั่วโมง ขึ้นอยู่กับจำนวนผ้าและคิวงานค่ะ",
        "km": "រយៈពេលបោកធម្មតា 3–4 ម៉ោង អាស្រ័យលើបរិមាណខោអាវ និងជួរ។",
        "id": "Waktu proses normal 3–4 jam, tergantung jumlah laundry dan antrian.",
        "cn": "正常洗涤时间约 3–4 小时，视衣物数量和排队情况而定。",
    },
    "separate": {
        "en": (
            "We wash each customer's laundry separately, bong. "
            "We do not mix your laundry with other customers' laundry."
        ),
        "th": "ทางร้านซักแยกตามออเดอร์ลูกค้า ไม่ซักรวมกับผ้าของลูกค้าท่านอื่นค่ะ",
        "km": (
            "ហាងយើងបោកខោអាវដាច់ដោយឡែកតាមអតិថិជនម្នាក់ៗ "
            "មិនបោករួមជាមួយអតិថិជនផ្សេងទេ។"
        ),
        "id": (
            "Kami mencuci laundry setiap pelanggan secara terpisah. "
            "Tidak dicampur dengan laundry pelanggan lain."
        ),
        "cn": "我们会分开清洗每位客人的衣物，不会和其他客人的衣物混洗。",
    },
    "pickup_delivery": {
        "en": (
            "🚚 Pickup & delivery:\n"
            "1) Send location\n"
            "2) Send clear house/pickup photo\n"
            "3) Send laundry bag photo\n"
            "4) Choose payment method\n"
            "5) Wait for staff confirmation"
        ),
        "th": (
            "🚚 รับ-ส่งผ้า:\n"
            "1) ส่งโลเคชั่น\n"
            "2) ส่งรูปหน้าบ้าน/จุดรับให้ชัด\n"
            "3) ส่งรูปถุงผ้า\n"
            "4) เลือกวิธีชำระเงิน\n"
            "5) รอพนักงานยืนยันค่ะ"
        ),
        "km": (
            "🚚 ទទួល-ដឹក:\n"
            "1) ផ្ញើទីតាំង\n"
            "2) ផ្ញើរូបផ្ទះ/ចំណុចទទួលច្បាស់\n"
            "3) ផ្ញើរូបថង់ខោអាវ\n"
            "4) ជ្រើសរើសវិធីបង់ប្រាក់\n"
            "5) រង់ចាំបុគ្គលិកបញ្ជាក់"
        ),
        "id": (
            "🚚 Antar-jemput:\n"
            "1) Kirim lokasi\n"
            "2) Kirim foto rumah/titik pickup jelas\n"
            "3) Kirim foto tas laundry\n"
            "4) Pilih metode bayar\n"
            "5) Tunggu konfirmasi staff"
        ),
        "cn": (
            "🚚 取送服务:\n"
            "1) 发送位置\n"
            "2) 发送清晰的门牌/取件点照片\n"
            "3) 发送洗衣袋照片\n"
            "4) 选择付款方式\n"
            "5) 等待员工确认"
        ),
    },
    "ironing": {
        "en": "Sorry bong, we do not have ironing service.",
        "th": "ขออภัยค่ะ ทางร้านไม่มีบริการรีดผ้า",
        "km": "សូមអភ័យទោសបង ហាងយើងមិនមានសេវាអ៊ុតខោអាវទេ។",
        "id": "Maaf bong, kami tidak menyediakan layanan setrika.",
        "cn": "不好意思，我们没有熨烫服务。",
    },
    "shoes": {
        "en": "Sorry bong, we do not have shoe washing service.",
        "th": "ขออภัยค่ะ ทางร้านไม่มีบริการซักรองเท้า",
        "km": "សូមអភ័យទោសបង ហាងយើងមិនមានសេវាបោកស្បែកជើងទេ។",
        "id": "Maaf bong, kami tidak menyediakan layanan cuci sepatu.",
        "cn": "不好意思，我们没有洗鞋服务。",
    },
    "points": {
        "en": (
            "🎁 Rewards: minimum bill 240 B = 1 point.\n"
            "At 13 points you get 200 B credit on the next invoice."
        ),
        "th": (
            "🎁 แต้ม: ยอดขั้นต่ำ 240 บาท = 1 แต้ม\n"
            "ครบ 13 แต้ม ได้เครดิต 200 บาทในบิลถัดไปค่ะ"
        ),
        "km": (
            "🎁 ពិន្ទុ: វិក្កយបត្រអប្បបរមា 240 B = 1 ពិន្ទុ\n"
            "គ្រប់ 13 ពិន្ទុ ទទួលបាន 200 B ក្នុងវិក្កយបត្របន្ទាប់។"
        ),
        "id": (
            "🎁 Poin: minimum bill 240 B = 1 poin.\n"
            "13 poin = kredit 200 B di invoice berikutnya."
        ),
        "cn": (
            "🎁 积分: 最低消费 240 泰铢 = 1 分。\n"
            "积满 13 分，下一单可获 200 泰铢抵扣。"
        ),
    },
    "ready": {
        "en": "Your laundry is ready, bong. You can request delivery back in the bot.",
        "th": "ผ้าของคุณพร้อมแล้วค่ะ สามารถกดเรียกส่งกลับในบอทได้เลยค่ะ",
        "km": "ខោអាវរបស់បងរួចរាល់ហើយ។ អាចស្នើដឹកត្រឡប់ក្នុង bot បាន។",
        "id": "Laundry Anda sudah siap. Bisa minta antar kembali lewat bot.",
        "cn": "您的衣物已洗好，可在机器人里申请送回。",
    },
    "on_the_way": {
        "en": "Staff is on the way to you now, bong. Please wait a moment.",
        "th": "พนักงานกำลังไปหาคุณแล้วค่ะ รอสักครู่นะคะ",
        "km": "បុគ្គលិកកំពុងទៅរកបងហើយ។ សូមរង់ចាំបន្តិច។",
        "id": "Staff sedang OTW ke lokasi Anda. Mohon tunggu sebentar.",
        "cn": "员工正在前往您的位置，请稍等。",
    },
    "location": {
        "en": (
            "📍 CHERRY Wash & Dry\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7"
        ),
        "th": (
            "📍 CHERRY Wash & Dry\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7"
        ),
        "km": (
            "📍 CHERRY Wash & Dry\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7"
        ),
        "id": (
            "📍 CHERRY Wash & Dry\n"
            "Google Maps:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7"
        ),
        "cn": (
            "📍 CHERRY Wash & Dry\n"
            "Google 地图:\n"
            "https://maps.app.goo.gl/479dbVxTmHu6k7Qx7"
        ),
    },
    "house_photo": {
        "en": "Please send a clear photo of your house or pickup point, bong.",
        "th": "กรุณาส่งรูปหน้าบ้านหรือจุดรับผ้าให้ชัดเจนค่ะ",
        "km": "សូមផ្ញើរូបផ្ទះ ឬចំណុចទទួលខោអាវឱ្យច្បាស់បង។",
        "id": "Tolong kirim foto rumah atau titik pickup yang jelas.",
        "cn": "请发送清晰的门牌或取件点照片。",
    },
    "bag_photo": {
        "en": "Please send a photo of your laundry bag, bong.",
        "th": "กรุณาส่งรูปถุงผ้าค่ะ",
        "km": "សូមផ្ញើរូបថង់ខោអាវបង។",
        "id": "Tolong kirim foto tas laundry.",
        "cn": "请发送洗衣袋照片。",
    },
    "problem": {
        "en": (
            "If there is any problem, please contact us within 3 days with invoice "
            "and photo or video if available."
        ),
        "th": (
            "หากมีปัญหา กรุณาติดต่อภายใน 3 วัน พร้อมบิล "
            "และรูปหรือวิดีโอ หากมีค่ะ"
        ),
        "km": (
            "បើមានបញ្ហា សូមទាក់ទងក្នុង 3 ថ្ងៃ ជាមួយវិក្កយបត្រ "
            "និងរូប ឬវីដេអូ បើមាន។"
        ),
        "id": (
            "Jika ada masalah, hubungi kami dalam 3 hari dengan invoice "
            "dan foto/video jika ada."
        ),
        "cn": "如有问题，请在 3 天内联系我们，并提供账单及照片或视频（如有）。",
    },
    "policy": {
        "en": (
            "Please check your laundry within 3 days after receiving it. "
            "The shop is not responsible for old stains, color bleeding, or undeclared special items."
        ),
        "th": (
            "กรุณาตรวจสอบผ้าภายใน 3 วันหลังได้รับคืนค่ะ "
            "ร้านไม่รับผิดชอบคราบเก่า สีตก หรือผ้าพิเศษที่ไม่ได้แจ้ง"
        ),
        "km": (
            "សូមពិនិត្យខោអាវក្នុង 3 ថ្ងៃបន្ទាប់ពីទទួល។ "
            "ហាងមិនទទួលខុសត្រូវលើស្លាកចាស់ រលាយពណ៌ ឬខោអាវពិសេសដែលមិនបានជូនដំណឹង។"
        ),
        "id": (
            "Periksa laundry dalam 3 hari setelah diterima. "
            "Toko tidak bertanggung jawab atas noda lama, luntur warna, atau barang khusus tanpa pemberitahuan."
        ),
        "cn": (
            "收到衣物后请在 3 天内检查。"
            "本店不对旧污渍、掉色或未告知的特殊衣物负责。"
        ),
    },
}

# Build reverse lookup: command text (with or without @bot) → reply key
COMMAND_TO_KEY: dict[str, str] = {}
for _staff_lang, buttons in STAFF_BUTTONS.items():
    for key, cmd in buttons.items():
        COMMAND_TO_KEY[cmd.lower()] = key
        COMMAND_TO_KEY[cmd.split("@")[0].lower()] = key

REPLY_KEY_ORDER: list[str] = [
    "price",
    "delivery_fee",
    "opening_hours",
    "processing_time",
    "separate",
    "pickup_delivery",
    "ironing",
    "shoes",
    "points",
    "ready",
    "on_the_way",
    "location",
    "house_photo",
    "bag_photo",
    "problem",
    "policy",
]


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


def menu_rows(staff_lang: str) -> list[list[str]]:
    """Quick reply keyboard rows in staff language."""
    lang = normalize_staff_lang(staff_lang)
    buttons = STAFF_BUTTONS[lang]
    labels = [buttons[key] for key in REPLY_KEY_ORDER]
    rows: list[list[str]] = []
    for i in range(0, len(labels), 2):
        rows.append(labels[i : i + 2])
    return rows


def parse_command(text: str) -> str | None:
    """Return reply key for a /command message, or None."""
    raw = str(text or "").strip()
    if not raw.startswith("/"):
        return None
    token = raw.split()[0].split("@")[0].lower()
    return COMMAND_TO_KEY.get(token)


def quick_reply_text(reply_key: str, customer_lang: str) -> str:
    lang = normalize_customer_lang(customer_lang)
    block = QUICK_REPLIES.get(reply_key, {})
    return block.get(lang, block.get(DEFAULT_CUSTOMER_LANG, ""))
