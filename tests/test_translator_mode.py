"""Group mode persistence for anonymous Telegram posts."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import translator_handlers as tr  # noqa: E402
from translator_content import SESSION_MODE_KEY  # noqa: E402


class TestGroupModePersistence(unittest.TestCase):
    def setUp(self) -> None:
        tr._CHAT_MODES.clear()

    def test_group_mode_uses_chat_data_not_user(self) -> None:
        chat_id = -1003860053672
        context = SimpleNamespace(
            chat_data={},
            user_data={},
        )
        callback_update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=chat_id, type="supergroup"),
        )
        anonymous_update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=chat_id, type="supergroup"),
            effective_user=SimpleNamespace(id=1087968824),
        )

        tr.set_mode(context, "id", callback_update)
        self.assertEqual(tr.get_mode(context, callback_update), "id")
        self.assertEqual(context.chat_data.get(SESSION_MODE_KEY), "id")

        # Anonymous post uses different user_id but same chat — mode must remain.
        self.assertEqual(tr.get_mode(context, anonymous_update), "id")


if __name__ == "__main__":
    unittest.main()
