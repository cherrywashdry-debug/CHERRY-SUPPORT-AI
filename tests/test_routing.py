"""Tests for translate vs FAQ group routing."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402
import staff_translate as staff  # noqa: E402

TRANSLATE_GID = -1003860053672
ANSWER_GID = -1003832672134
ALLOWED_UID = 1087968824


def _update(chat_id: int, chat_type: str = "supergroup", user_id: int = 999) -> SimpleNamespace:
    return SimpleNamespace(
        effective_chat=SimpleNamespace(id=chat_id, type=chat_type),
        effective_user=SimpleNamespace(id=user_id),
    )


@patch.dict(
    os.environ,
    {
        "TRANSLATE_AI_GROUP_ID": str(TRANSLATE_GID),
        "ANSWER_GROUP_ID": str(ANSWER_GID),
        "ALLOWED_USER_IDS": str(ALLOWED_UID),
    },
    clear=False,
)
class TestGroupRouting(unittest.TestCase):
    def test_translate_group_is_translate_not_faq(self) -> None:
        upd = _update(TRANSLATE_GID)
        self.assertTrue(staff.is_translate_chat(upd))
        self.assertFalse(app.is_faq_chat(upd))

    def test_answer_group_is_faq_not_translate(self) -> None:
        upd = _update(ANSWER_GID)
        self.assertFalse(staff.is_translate_chat(upd))
        self.assertTrue(app.is_faq_chat(upd))

    def test_allowed_dm_is_translate(self) -> None:
        upd = _update(ALLOWED_UID, chat_type="private", user_id=ALLOWED_UID)
        self.assertTrue(staff.is_translate_chat(upd))
        self.assertFalse(app.is_faq_chat(upd))

    def test_private_non_allowed_is_faq(self) -> None:
        upd = _update(12345, chat_type="private", user_id=777)
        self.assertFalse(staff.is_translate_chat(upd))
        self.assertTrue(app.is_faq_chat(upd))

    def test_random_group_is_not_faq_when_answer_group_set(self) -> None:
        upd = _update(-1001111111111)
        self.assertFalse(staff.is_translate_chat(upd))
        self.assertFalse(app.is_faq_chat(upd))


if __name__ == "__main__":
    unittest.main()
