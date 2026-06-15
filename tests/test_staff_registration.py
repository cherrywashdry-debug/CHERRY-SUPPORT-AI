"""Tests for private staff registration (staff_users.json)."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import staff_users


def test_approve_and_disable_staff() -> None:
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
        staff_users.add_pending_request(999001, "Test Staff", "@teststaff")
        assert staff_users.has_pending_request(999001)
        staff_users.approve_staff(999001, name="Test Staff", username="@teststaff")
        assert staff_users.is_active_staff(999001)
        assert not staff_users.has_pending_request(999001)
        staff_users.disable_staff(999001)
        assert not staff_users.is_active_staff(999001)
    finally:
        staff_users._cache = None
        staff_users.JSON_PATH = Path(staff_users.ROOT) / "staff_users.json"
        staff_users.BACKUP_PATH = Path(staff_users.ROOT) / "staff_users_backup.json"
        staff_users.SEED_PATH = Path(staff_users.ROOT) / "staff_users_seed.json"
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    test_approve_and_disable_staff()
    print("ALL OK")
