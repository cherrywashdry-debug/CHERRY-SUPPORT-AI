"""Tests for CHERRY Quick Reply Bot — 8 reply buttons, fixed texts."""
from __future__ import annotations

from quick_replies import (
    APPROVED_REPLY_BUTTONS,
    QUICK_REPLIES,
    REPLY_KEY_ORDER,
    parse_reply_label,
    quick_reply_text,
    reply_menu_rows,
)


def test_reply_menu_has_eight_buttons() -> None:
    flat = [b for row in reply_menu_rows("km") for b in row]
    assert len(flat) == len(REPLY_KEY_ORDER) + 1  # + back


def test_reply_key_order() -> None:
    assert REPLY_KEY_ORDER == [
        "price",
        "delivery_fee",
        "opening_hours",
        "processing_time",
        "points",
        "ironing",
        "no_shoes",
        "before_service",
    ]


def test_khmer_reply_buttons() -> None:
    assert APPROVED_REPLY_BUTTONS["price"] == "💰 /តម្លៃ"
    assert parse_reply_label("/តម្លៃ") == "price"
    assert parse_reply_label("/ថ្លៃដឹក") == "delivery_fee"
    assert parse_reply_label("/មិនមានអ៊ុត") == "ironing"


def test_price_reply_thai_exact() -> None:
    text = quick_reply_text("price", "th")
    assert "CHERRY WASH & DRY POIPET 24HR" in text
    assert "210–240 บาท" in text
    assert "ไม่คิดราคาตามกิโลกรัม" in text


def test_delivery_fee_reply_thai() -> None:
    text = quick_reply_text("delivery_fee", "th")
    assert "ไม่เกิน 1 กิโลเมตร ฟรี" in text
    assert "มากกว่า 4 กิโลเมตร 70 บาท" in text


def test_all_reply_keys_in_quick_replies() -> None:
    for key in REPLY_KEY_ORDER:
        assert key in QUICK_REPLIES
        assert set(QUICK_REPLIES[key].keys()) == {"th", "en", "km", "id", "cn"}


if __name__ == "__main__":
    test_reply_menu_has_eight_buttons()
    test_reply_key_order()
    test_khmer_reply_buttons()
    test_price_reply_thai_exact()
    test_delivery_fee_reply_thai()
    test_all_reply_keys_in_quick_replies()
    print("ALL OK")
