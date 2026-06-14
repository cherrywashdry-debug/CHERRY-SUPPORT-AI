"""Tests for CHERRY Quick Reply Bot — two-menu fixed replies, no AI."""
from __future__ import annotations

from quick_replies import (
    APPROVED_QUESTION_BUTTONS,
    APPROVED_REPLY_BUTTONS,
    BTN_BACK,
    BTN_MENU_QUESTIONS,
    BTN_MENU_REPLIES,
    EMOJI_QUESTION,
    QUESTION_KEY_ORDER,
    QUESTIONS,
    QUICK_REPLIES,
    REPLY_KEY_ORDER,
    parse_question_label,
    parse_reply_label,
    question_menu_rows,
    quick_reply_text,
    reply_menu_rows,
)


def test_question_buttons_separate_from_replies() -> None:
    q_cmds = set(APPROVED_QUESTION_BUTTONS.values())
    r_cmds = set(APPROVED_REPLY_BUTTONS.values())
    assert q_cmds.isdisjoint(r_cmds)


def test_all_staff_langs_use_approved_khmer_buttons() -> None:
    th_q = question_menu_rows("th")
    id_q = question_menu_rows("id")
    km_q = question_menu_rows("km")
    assert th_q == km_q == id_q
    th_r = reply_menu_rows("th")
    assert th_r == reply_menu_rows("km") == reply_menu_rows("id")


def test_question_buttons_use_red_question_emoji() -> None:
    for key in QUESTION_KEY_ORDER:
        label = APPROVED_QUESTION_BUTTONS[key]
        assert label.startswith(EMOJI_QUESTION), f"{key} missing ❓: {label!r}"
        assert not label.startswith("?")


def test_question_menu_has_all_nine_buttons() -> None:
    flat = [btn for row in question_menu_rows("km") for btn in row]
    assert len(flat) == len(QUESTION_KEY_ORDER) + 1
    assert flat[-1] == BTN_BACK
    for key in QUESTION_KEY_ORDER:
        assert APPROVED_QUESTION_BUTTONS[key] in flat


def test_reply_menu_has_all_three_buttons() -> None:
    flat = [btn for row in reply_menu_rows("km") for btn in row]
    assert len(flat) == len(REPLY_KEY_ORDER) + 1
    assert APPROVED_REPLY_BUTTONS["ironing"] in flat
    assert APPROVED_REPLY_BUTTONS["no_shoes"] in flat
    assert APPROVED_REPLY_BUTTONS["before_service"] in flat


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


def test_khmer_reply_no_shoes() -> None:
    assert parse_reply_label("❌ /មិនមានស្បែកជើង") == "no_shoes"
    text = quick_reply_text("no_shoes", "th")
    assert "ไม่มีบริการซักรองเท้า" in text


def test_khmer_reply_before_service() -> None:
    assert parse_reply_label("⚠️ /មុនប្រើសេវា") == "before_service"
    text = quick_reply_text("before_service", "th")
    assert "ข้อควรทราบก่อนใช้บริการ" in text


def test_question_label_parsing() -> None:
    assert parse_question_label("❓ /បោករួមរឺបោកផ្សេង") == "q_separate_wash"
    assert parse_question_label("❓ /សូមផ្ញើរូបផ្ទះ") == "q_house_photo"


def test_reply_command_without_emoji() -> None:
    assert parse_reply_label("/មិនមានអ៊ុត") == "ironing"


def test_main_menu_labels() -> None:
    assert BTN_MENU_QUESTIONS.startswith(EMOJI_QUESTION)
    assert BTN_MENU_REPLIES.startswith("💬")


if __name__ == "__main__":
    test_question_buttons_separate_from_replies()
    test_all_staff_langs_use_approved_khmer_buttons()
    test_question_buttons_use_red_question_emoji()
    test_question_menu_has_all_nine_buttons()
    test_reply_menu_has_all_three_buttons()
    test_all_question_keys_have_five_languages()
    test_all_reply_keys_have_five_languages()
    test_khmer_reply_ironing()
    test_khmer_reply_no_shoes()
    test_khmer_reply_before_service()
    test_question_label_parsing()
    test_reply_command_without_emoji()
    test_main_menu_labels()
    print("ALL OK")
