"""Regression: /register must not crash (staff_users import + pending save)."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import staff_users


async def test_register_cmd_saves_pending_and_replies() -> None:
    import app as bot

    work = Path(tempfile.mkdtemp())
    try:
        staff_users.JSON_PATH = work / "staff_users.json"
        staff_users.BACKUP_PATH = work / "staff_users_backup.json"
        staff_users.SEED_PATH = work / "staff_users_seed.json"
        staff_users._cache = None
        (work / "staff_users_seed.json").write_text(
            json.dumps({"approved_staff": [], "pending_requests": []}),
            encoding="utf-8",
        )

        message = SimpleNamespace(
            reply_text=AsyncMock(),
        )
        user = SimpleNamespace(
            id=777001,
            full_name="Test Staff",
            first_name="Test",
            username="newstaff",
        )
        update = SimpleNamespace(effective_message=message, effective_user=user)
        context = SimpleNamespace(
            bot=SimpleNamespace(send_message=AsyncMock(return_value=None)),
            user_data={},
        )

        with patch.dict(
            "os.environ",
            {"OWNER_TELEGRAM_ID": "5253532289", "ALLOWED_USER_IDS": ""},
            clear=False,
        ):
            await bot.register_cmd(update, context)

        assert staff_users.has_pending_request(777001)
        message.reply_text.assert_awaited()
        context.bot.send_message.assert_awaited()
    finally:
        staff_users._cache = None
        staff_users.JSON_PATH = Path(staff_users.ROOT) / "staff_users.json"
        staff_users.BACKUP_PATH = Path(staff_users.ROOT) / "staff_users_backup.json"
        staff_users.SEED_PATH = Path(staff_users.ROOT) / "staff_users_seed.json"
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_register_cmd_saves_pending_and_replies())
    print("ALL OK")
