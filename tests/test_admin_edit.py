"""Tests for reply JSON store and owner edit helpers."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import reply_store
from quick_replies import (
    BTN_ADMIN_EDIT,
    EDIT_REPLY_KEY_LABELS,
    EDIT_LANG_LABELS,
    OWNER_ACCESS_DENIED,
    REPLY_KEY_ORDER,
    admin_reply_mgmt_menu_rows,
    get_quick_replies,
    parse_edit_lang,
    parse_edit_reply_key,
    quick_reply_text,
)


def test_json_has_all_reply_keys() -> None:
    data = get_quick_replies()
    for key in REPLY_KEY_ORDER:
        assert key in data
        assert set(data[key].keys()) == {"th", "en", "km", "id", "cn"}


def test_admin_menu_has_reply_tools() -> None:
    flat = [b for row in admin_reply_mgmt_menu_rows("km") for b in row]
    assert BTN_ADMIN_EDIT in flat


def test_edit_key_labels_count() -> None:
    assert len(EDIT_REPLY_KEY_LABELS) == len(get_quick_replies())


def test_parse_edit_reply_key_ironing() -> None:
    assert parse_edit_reply_key(EDIT_REPLY_KEY_LABELS["ironing"]) == "ironing"


def test_parse_edit_lang_th() -> None:
    assert parse_edit_lang(EDIT_LANG_LABELS["th"]) == "th"


def test_save_reply_with_backup(tmp_path: Path | None = None) -> None:
    work = Path(tempfile.mkdtemp())
    try:
        src = Path(reply_store.ROOT) / "quick_replies_seed.json"
        shutil.copy2(src, work / "quick_replies_seed.json")
        data = json.loads(src.read_text(encoding="utf-8"))
        json_path = work / "quick_replies.json"
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        reply_store.JSON_PATH = json_path
        reply_store.BACKUP_PATH = work / "quick_replies_backup.json"
        reply_store.SEED_PATH = work / "quick_replies_seed.json"
        reply_store._cache = None

        new_text = "TEST IRONING TH\n\nEdited by unit test."
        reply_store.save_reply("ironing", "th", new_text, backup=True)
        backups = list(work.glob("quick_replies_backup_*.json"))
        assert reply_store.BACKUP_PATH.is_file() or backups
        assert get_quick_replies()["ironing"]["th"] == new_text
        assert quick_reply_text("ironing", "th") == new_text
    finally:
        reply_store._cache = None
        reply_store.JSON_PATH = Path(reply_store.ROOT) / "quick_replies.json"
        reply_store.BACKUP_PATH = Path(reply_store.ROOT) / "quick_replies_backup.json"
        reply_store.SEED_PATH = Path(reply_store.ROOT) / "quick_replies_seed.json"
        shutil.rmtree(work, ignore_errors=True)


def test_owner_access_denied_message() -> None:
    assert "Access denied" in OWNER_ACCESS_DENIED


if __name__ == "__main__":
    test_json_has_all_reply_keys()
    test_admin_menu_has_reply_tools()
    test_edit_key_labels_count()
    test_parse_edit_reply_key_ironing()
    test_parse_edit_lang_th()
    test_save_reply_with_backup()
    test_owner_access_denied_message()
    print("ALL OK")
