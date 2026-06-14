"""Tests for CHERRY Quick Reply Bot — two-menu fixed replies, no AI."""
from __future__ import annotations

from quick_replies import (
    BTN_BACK,
    BTN_MENU_QUESTIONS,
    BTN_MENU_REPLIES,
    QUESTION_BUTTONS,
    QUESTION_KEY_ORDER,
    QUESTIONS,
    QUICK_REPLIES,
    REPLY_BUTTONS,
    REPLY_KEY_ORDER,
    parse_question_label,
    parse_reply_label,
    question_menu_rows,
    question_text,
    quick_reply_text,
    reply_menu_rows,
)


def test_question_buttons_separate_from_replies() -> None:
    q_cmds = {QUESTION_BUTTONS["km"][k] for k in QUESTION_KEY_ORDER}
    r_cmds = {REPLY_BUTTONS["km"][k] for k in REPLY_KEY_ORDER}
    assert q_cmds.isdisjoint(r_cmds)


def test_all_question_keys_have_five_languages() -> None:
    for key in QUESTION_KEY_ORDER:
        block = QUESTIONS[key]
        assert set(block.keys()) == {"th", "en", "km", "id", "cn"}


def test_all_reply_keys_have_five_languages() -> None:
    for key in REPLY_KEY_ORDER:
        block = QUICK_REPLIES[key]
        assert set(block.keys()) == {"th", "en", "km", "id", "cn"}


def test_khmer_reply_ironing() -> None:
    assert parse_reply_label("❌ /មិនមានអ៊ុត") == "ironing"
    text = quick_reply_text("ironing", "th")
    assert "ไม่มีบริการรีดผ้า" in text
    assert "CHERRY Wash & Dry" in text


def test_khmer_reply_no_shoes() -> None:
    assert parse_reply_label("❌ /មិនមានស្បែកជើង") == "no_shoes"
    text = quick_reply_text("no_shoes", "th")
    assert "ไม่มีบริการซักรองเท้า" in text


def test_khmer_reply_before_service() -> None:
    assert parse_reply_label("⚠️ /មុនប្រើសេវា") == "before_service"
    text = quick_reply_text("before_service", "th")
    assert "ข้อควรทราบก่อนใช้บริการ" in text
    assert "1 ออเดอร์ = 1 เครื่อง" in text


def test_question_label_parsing() -> None:
    assert parse_question_label("❓ /បោករួមរឺបោកផ្សេង") == "q_separate_wash"
    assert parse_question_label("❓ /សូមផ្ញើរូបផ្ទះ") == "q_house_photo"


def test_submenu_has_back() -> None:
    assert question_menu_rows("km")[-1] == [BTN_BACK]
    assert reply_menu_rows("th")[-1] == [BTN_BACK]


def test_main_menu_labels() -> None:
    assert BTN_MENU_QUESTIONS.startswith("❓")
    assert BTN_MENU_REPLIES.startswith("💬")


def test_reply_command_without_emoji() -> None:
    assert parse_reply_label("/មិនមានអ៊ុត") == "ironing"
    assert parse_reply_label("/ไม่มีรีดผ้า") == "ironing"


if __name__ == "__main__":
    test_question_buttons_separate_from_replies()
    test_all_question_keys_have_five_languages()
    test_all_reply_keys_have_five_languages()
    test_khmer_reply_ironing()
    test_khmer_reply_no_shoes()
    test_khmer_reply_before_service()
    test_question_label_parsing()
    test_submenu_has_back()
    test_main_menu_labels()
    test_reply_command_without_emoji()
    print("ALL OK")
