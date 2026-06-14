"""Tests for CHERRY Quick Reply Bot — fixed replies, no AI."""
from __future__ import annotations

from quick_replies import (
    BTN_BACK,
    COMMAND_TO_KEY,
    QUICK_REPLIES,
    REPLY_KEY_ORDER,
    STAFF_BUTTONS,
    customer_lang_from_label,
    menu_rows,
    parse_command,
    quick_reply_text,
    staff_lang_from_label,
)


def test_all_staff_buttons_map_to_same_keys() -> None:
    km_keys = set(STAFF_BUTTONS["km"].keys())
    th_keys = set(STAFF_BUTTONS["th"].keys())
    id_keys = set(STAFF_BUTTONS["id"].keys())
    assert km_keys == th_keys == id_keys
    assert km_keys == set(REPLY_KEY_ORDER)


def test_all_replies_have_five_customer_languages() -> None:
    for key in REPLY_KEY_ORDER:
        block = QUICK_REPLIES[key]
        assert set(block.keys()) == {"th", "en", "km", "id", "cn"}
        for lang, text in block.items():
            assert text.strip(), f"{key}/{lang} is empty"


def test_khmer_staff_english_customer_ironing() -> None:
    assert parse_command("/អ៊ុត") == "ironing"
    reply = quick_reply_text("ironing", "en")
    assert reply == "Sorry bong, we do not have ironing service."


def test_thai_staff_khmer_customer_ironing() -> None:
    assert parse_command("/รีดผ้า") == "ironing"
    reply = quick_reply_text("ironing", "km")
    assert "អ៊ុត" in reply or "មិនមាន" in reply


def test_indonesian_staff_chinese_customer_ironing() -> None:
    assert parse_command("/setrika") == "ironing"
    reply = quick_reply_text("ironing", "cn")
    assert reply == "不好意思，我们没有熨烫服务。"


def test_separate_reply_examples() -> None:
    assert quick_reply_text("separate", "en").startswith("We wash each customer")
    assert "ไม่ซักรวม" in quick_reply_text("separate", "th")
    assert "Maaf bong" in quick_reply_text("shoes", "id")


def test_staff_language_labels() -> None:
    assert staff_lang_from_label("🇰🇭 Khmer Staff") == "km"
    assert staff_lang_from_label("🇹🇭 Thai Staff") == "th"
    assert staff_lang_from_label("🇮🇩 Indonesian Staff") == "id"


def test_customer_language_labels() -> None:
    assert customer_lang_from_label("🇬🇧 English Customer") == "en"
    assert customer_lang_from_label("🇨🇳 Chinese Customer") == "cn"


def test_menu_rows_count() -> None:
    rows = menu_rows("th")
    flat = [btn for row in rows for btn in row]
    assert len(flat) == len(REPLY_KEY_ORDER) + 1
    assert flat[-1] == BTN_BACK


def test_back_button_label() -> None:
    from quick_replies import is_back_button

    assert is_back_button("Back/ត្រលប់់")
    assert not is_back_button("/ราคา")


def test_command_lookup_case_insensitive_bot_suffix() -> None:
    assert parse_command("/setrika@cherrybot") == "ironing"
    assert COMMAND_TO_KEY["/harga"] == "price"
