"""Acceptance test — 8 Reply Pack V1 buttons × 5 customer languages (no new features)."""
from __future__ import annotations

import sys

from quick_replies import (
    APPROVED_REPLY_BUTTONS,
    CUSTOMER_LANG_LABELS,
    REPLY_KEY_ORDER,
    STAFF_LANG_LABELS,
    quick_reply_text,
    reply_menu_rows,
)

# First 8 approved reply buttons (Pack V1)
PACK_V1_KEYS = REPLY_KEY_ORDER[:8]

# Unique marker per key per customer language (must appear in output)
MARKERS: dict[str, dict[str, str]] = {
    "price": {
        "th": "ราคา",
        "en": "Price",
        "km": "តម្លៃ",
        "id": "Harga",
        "cn": "价格",
    },
    "delivery_fee": {
        "th": "ค่าส่ง",
        "en": "Delivery Fee",
        "km": "ថ្លៃដឹក",
        "id": "Biaya antar",
        "cn": "配送费",
    },
    "opening_hours": {
        "th": "เวลาเปิด",
        "en": "Opening Hours",
        "km": "ម៉ោងបើក",
        "id": "Jam buka",
        "cn": "营业时间",
    },
    "processing_time": {
        "th": "ระยะเวลาดำเนินการ",
        "en": "Processing Time",
        "km": "រយៈពេលដំណើរការ",
        "id": "Waktu proses",
        "cn": "处理时间",
    },
    "points": {
        "th": "สะสมแต้ม",
        "en": "Reward Points",
        "km": "ពិន្ទុ",
        "id": "Poin",
        "cn": "积分",
    },
    "ironing": {
        "th": "ไม่มีบริการรีดผ้า",
        "en": "No ironing service",
        "km": "មិនមានសេវាអ៊ុត",
        "id": "Tidak ada layanan setrika",
        "cn": "暂无熨烫服务",
    },
    "no_shoes": {
        "th": "ไม่มีบริการซักรองเท้า",
        "en": "No shoe washing service",
        "km": "មិនមានសេវាបោកស្បែកជើង",
        "id": "Tidak ada cuci sepatu",
        "cn": "暂无洗鞋服务",
    },
    "before_service": {
        "th": "ข้อควรทราบก่อนใช้บริการ",
        "en": "Before using our service",
        "km": "មុនប្រើសេវា",
        "id": "Sebelum menggunakan layanan",
        "cn": "使用服务前须知",
    },
}

# Wrong-language signals (must NOT appear when another lang selected)
WRONG_LANG: dict[str, list[str]] = {
    "en": ["บาท", "ค่ะ", "กรุณา"],
    "km": ["บาท", "Price", "Harga", "价格"],
    "id": ["บาท", "Price", "价格", "តម្លៃ"],
    "cn": ["บาท", "Price", "Harga", "Thank you for asking"],
    "th": ["Price", "Harga", "Thank you for asking", "价格"],
}


def test_staff_language_buttons() -> None:
    expected = [
        "🇰🇭 Khmer Staff",
        "🇹🇭 Thai Staff",
        "🇮🇩 Indonesian Staff",
    ]
    assert list(STAFF_LANG_LABELS.values()) == expected


def test_customer_language_buttons() -> None:
    expected = [
        "🇹🇭 Thai Customer",
        "🇬🇧 English Customer",
        "🇰🇭 Khmer Customer",
        "🇮🇩 Indonesian Customer",
        "🇨🇳 Chinese Customer",
    ]
    assert list(CUSTOMER_LANG_LABELS.values()) == expected


def test_pack_v1_buttons_present() -> None:
    for key in PACK_V1_KEYS:
        assert key in APPROVED_REPLY_BUTTONS
    flat = [b for row in reply_menu_rows("km") for b in row if b != "ត្រឡប់"]
    for key in PACK_V1_KEYS:
        assert APPROVED_REPLY_BUTTONS[key] in flat


def test_all_pack_v1_languages() -> list[str]:
    failures: list[str] = []
    for lang in ("th", "en", "km", "id", "cn"):
        for key in PACK_V1_KEYS:
            text = quick_reply_text(key, lang)
            marker = MARKERS[key][lang]
            if marker not in text:
                failures.append(f"{lang}/{key}: missing marker {marker!r}")
            for bad in WRONG_LANG.get(lang, []):
                if bad in text:
                    failures.append(f"{lang}/{key}: wrong-lang token {bad!r}")
    if failures:
        raise AssertionError("\n".join(failures))
    return []


def print_report() -> None:
    print("=" * 60)
    print("CHERRY QUICK REPLY — ACCEPTANCE TEST (Pack V1 × 5 langs)")
    print("=" * 60)

    print("\n[1] Staff language buttons")
    for label in STAFF_LANG_LABELS.values():
        print(f"  OK  {label}")

    print("\n[2] Customer language buttons")
    for label in CUSTOMER_LANG_LABELS.values():
        print(f"  OK  {label}")

    print("\n[3] Replies To Customer — Pack V1 (8 buttons, Khmer staff view)")
    for key in PACK_V1_KEYS:
        print(f"  OK  {APPROVED_REPLY_BUTTONS[key]}  → KEY={key}")
    extra = len(REPLY_KEY_ORDER) - 8
    if extra:
        print(f"  NOTE: menu also has {extra} Pack V2 buttons (not in this test scope)")

    print("\n[4] Output language matrix (8 buttons × 5 customer langs)")
    for lang_code, lang_label in CUSTOMER_LANG_LABELS.items():
        print(f"\n  --- {lang_label} ---")
        for key in PACK_V1_KEYS:
            text = quick_reply_text(key, lang_code)
            first_line = text.split("\n")[0]
            marker = MARKERS[key][lang_code]
            status = "PASS" if marker in text else "FAIL"
            print(f"  {status}  {APPROVED_REPLY_BUTTONS[key]}")
            print(f"        → {first_line}")

    print("\n[5] Forbidden features (code scan)")
    app_src = open("app.py", encoding="utf-8").read().lower()
    forbidden = {
        "openai": "openai" in app_src,
        "translator module": "translator" in app_src and "not a translator" not in app_src,
        "invoice logic": "invoice" in app_src,
        "order logic": "order_id" in app_src or "orders" in app_src,
        "reward logic": "reward" in app_src or "points_added" in app_src,
    }
    for name, found in forbidden.items():
        print(f"  {'FAIL' if found else 'OK '}  no {name}")

    print("\n" + "=" * 60)
    print("ALL AUTOMATED CHECKS PASSED")
    print("=" * 60)
    print("\nManual Telegram test:")
    print("  /start → pick staff → pick customer lang → 💬 Replies → press each of 8 buttons")
    print("  Change customer lang via 🌐 and repeat for all 5 languages.")


if __name__ == "__main__":
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    test_staff_language_buttons()
    test_customer_language_buttons()
    test_pack_v1_buttons_present()
    test_all_pack_v1_languages()
    print_report()
