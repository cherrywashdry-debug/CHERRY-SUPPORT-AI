"""Tests for CHERRY Quick Reply Bot — staff-language UI, fixed replies."""
from __future__ import annotations

from quick_replies import (
    APPROVED_QUESTION_BUTTONS,
    EMOJI_QUESTION,
    QUESTION_BUTTONS,
    QUESTION_KEY_ORDER,
    QUESTIONS,
    QUICK_REPLIES,
    REPLY_BUTTONS,
    REPLY_KEY_ORDER,
    STAFF_UI,
    back_button,
    main_menu_action,
    main_menu_rows,
    parse_question_label,
    parse_reply_label,
    question_menu_rows,
    quick_reply_text,
    reply_menu_rows,
    staff_ui,
)


def test_staff_ui_main_menu_differs_by_language() -> None:
    km = main_menu_rows("km")[0][0]
    th = main_menu_rows("th")[0][0]
    id_ = main_menu_rows("id")[0][0]
    assert km != th != id_
    assert "ถามลูกค้า" in th
    assert "Tanya Pelanggan" in id_


def test_back_button_by_staff_language() -> None:
    assert back_button("km") == "ត្រឡប់"
    assert back_button("th") == "กลับ"
    assert back_button("id") == "Kembali"


def test_question_buttons_differ_by_staff_language() -> None:
    km = question_menu_rows("km")[0][0]
    th = question_menu_rows("th")[0][0]
    assert km != th
    assert km == APPROVED_QUESTION_BUTTONS["q_separate_wash"]
    assert "/ซักรวมไหม" in th


def test_reply_buttons_differ_by_staff_language() -> None:
    assert "/មិនមានអ៊ុត" in reply_menu_rows("km")[0][0]
    assert "/ไม่มีรีดผ้า" in reply_menu_rows("th")[0][0]
    assert "/tidaksetrika" in reply_menu_rows("id")[0][0]


def test_question_buttons_use_red_question_emoji() -> None:
    for lang in ("km", "th", "id"):
        for key in QUESTION_KEY_ORDER:
            label = QUESTION_BUTTONS[lang][key]
            assert label.startswith(EMOJI_QUESTION), f"{lang}/{key}"


def test_main_menu_action_all_languages() -> None:
    assert main_menu_action(STAFF_UI["th"]["menu_questions"]) == "questions"
    assert main_menu_action(STAFF_UI["id"]["menu_replies"]) == "replies"
    assert main_menu_action(STAFF_UI["km"]["menu_clear"]) == "clear"


def test_khmer_reply_ironing() -> None:
    assert parse_reply_label("❌ /មិនមានអ៊ុត") == "ironing"
    assert parse_reply_label("/ไม่มีรีดผ้า") == "ironing"
    assert "ไม่มีบริการรีดผ้า" in quick_reply_text("ironing", "th")


def test_question_menu_has_nine_plus_back() -> None:
    flat = [b for row in question_menu_rows("km") for b in row]
    assert len(flat) == 10


if __name__ == "__main__":
    test_staff_ui_main_menu_differs_by_language()
    test_back_button_by_staff_language()
    test_question_buttons_differ_by_staff_language()
    test_reply_buttons_differ_by_staff_language()
    test_question_buttons_use_red_question_emoji()
    test_main_menu_action_all_languages()
    test_khmer_reply_ironing()
    test_question_menu_has_nine_plus_back()
    print("ALL OK")
