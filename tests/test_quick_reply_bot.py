"""Tests for CHERRY Quick Reply Bot — Reply Pack V1 + V2."""
from __future__ import annotations

from quick_replies import (
    REPLY_BUTTONS,
    REPLY_KEY_ORDER,
    get_quick_replies,
    parse_reply_label,
    question_text,
    quick_reply_text,
    reply_menu_rows,
)

REPLY_PACK_V1 = [
    "price",
    "delivery_fee",
    "opening_hours",
    "processing_time",
    "points",
    "ironing",
    "no_shoes",
    "before_service",
]

REPLY_PACK_V2 = [
    "laundry_ready",
    "staff_on_the_way_delivery",
    "staff_on_the_way_pickup",
    "ask_location",
    "ask_home_photo",
    "ask_bag_photo",
    "payment_method",
    "ask_separate_or_together",
]


def test_reply_menu_has_sixteen_buttons() -> None:
    flat = [b for row in reply_menu_rows("km") for b in row]
    assert len(flat) == len(REPLY_KEY_ORDER) + 1  # + back
    assert len(REPLY_KEY_ORDER) == 16


def test_reply_key_order() -> None:
    assert REPLY_KEY_ORDER == REPLY_PACK_V1 + REPLY_PACK_V2


def test_v2_khmer_reply_buttons() -> None:
    km = REPLY_BUTTONS["km"]
    assert km["laundry_ready"] == "📦 /រួចរាល់"
    assert parse_reply_label("/រួចរាល់") == "laundry_ready"
    assert parse_reply_label("/កំពុងទៅ") == "staff_on_the_way_delivery"
    assert parse_reply_label("/កំពុងទៅយក") == "staff_on_the_way_pickup"
    assert parse_reply_label("/បង់ប្រាក់") == "payment_method"


def test_laundry_ready_reply_thai_exact() -> None:
    text = quick_reply_text("laundry_ready", "th")
    assert "ผ้าของคุณซักเสร็จแล้วค่ะ" in text
    assert "เวลาจัดส่งเป็นไปตามรอบจัดส่งของทางร้าน" in text
    assert "ขอบคุณที่ใช้บริการ CHERRY Wash & Dry ❤️" in text


def test_staff_on_the_way_delivery_thai() -> None:
    text = quick_reply_text("staff_on_the_way_delivery", "th")
    assert "พนักงานกำลังนำผ้าไปส่งให้ลูกค้าค่ะ" in text


def test_ask_separate_or_together_thai() -> None:
    text = quick_reply_text("ask_separate_or_together", "th")
    assert "ลูกค้าต้องการซักแยก หรือซักรวมกันคะ?" in text


def test_question_english_not_thai() -> None:
    text = question_text("q_separate_wash", "en")
    assert "Would you like separate wash" in text
    assert "ลูกค้า" not in text


def test_reply_english_not_thai() -> None:
    text = quick_reply_text("price", "en")
    assert "SERVICE PRICE" in text
    assert "210–240 Baht" in text
    assert "INCLUDED IN SERVICE" in text
    assert "บาท" not in text


def test_reply_khmer_not_thai() -> None:
    text = quick_reply_text("price", "km")
    assert "តម្លៃ" in text
    assert "บาท" not in text


def test_reply_indonesian_not_thai() -> None:
    text = quick_reply_text("price", "id")
    assert "Harga" in text
    assert "บาท" not in text


def test_reply_chinese_not_thai() -> None:
    text = quick_reply_text("price", "cn")
    assert "价格" in text
    assert "บาท" not in text


def test_question_khmer_customer() -> None:
    text = question_text("q_separate_wash", "km")
    assert "បោក" in text
    assert "ลูกค้า" not in text


def test_all_reply_keys_in_quick_replies() -> None:
    data = get_quick_replies()
    for key in REPLY_KEY_ORDER:
        assert key in data
        assert set(data[key].keys()) == {"th", "en", "km", "id", "cn"}


if __name__ == "__main__":
    test_reply_menu_has_sixteen_buttons()
    test_reply_key_order()
    test_v2_khmer_reply_buttons()
    test_laundry_ready_reply_thai_exact()
    test_staff_on_the_way_delivery_thai()
    test_ask_separate_or_together_thai()
    test_question_english_not_thai()
    test_reply_english_not_thai()
    test_reply_khmer_not_thai()
    test_reply_indonesian_not_thai()
    test_reply_chinese_not_thai()
    test_question_khmer_customer()
    test_all_reply_keys_in_quick_replies()
    print("ALL OK")
