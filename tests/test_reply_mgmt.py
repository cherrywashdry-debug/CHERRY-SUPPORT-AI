"""Tests for owner reply management (add / edit / delete with JSON stores)."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import reply_button_store
import reply_store
from admin_reply_mgmt import validate_new_key
from quick_replies import (
    BTN_ADMIN_ADD,
    BTN_ADMIN_DELETE,
    BTN_ADMIN_EDIT,
    BTN_REPLY_MGMT,
    OWNER_ACCESS_DENIED,
    admin_reply_mgmt_menu_rows,
    get_quick_replies,
    refresh_button_maps,
    reload_quick_replies,
)


def _setup_tmp_stores(work: Path) -> None:
    root = Path(reply_store.ROOT)
    shutil.copy2(root / "quick_replies_seed.json", work / "quick_replies_seed.json")
    shutil.copy2(root / "quick_reply_buttons_seed.json", work / "quick_reply_buttons_seed.json")
    shutil.copy2(work / "quick_replies_seed.json", work / "quick_replies.json")
    shutil.copy2(work / "quick_reply_buttons_seed.json", work / "quick_reply_buttons.json")

    reply_store.JSON_PATH = work / "quick_replies.json"
    reply_store.BACKUP_PATH = work / "quick_replies_backup.json"
    reply_store.SEED_PATH = work / "quick_replies_seed.json"
    reply_store._cache = None

    reply_button_store.JSON_PATH = work / "quick_reply_buttons.json"
    reply_button_store.SEED_PATH = work / "quick_reply_buttons_seed.json"
    reply_button_store._cache = None


def _restore_stores() -> None:
    root = Path(reply_store.ROOT)
    reply_store._cache = None
    reply_store.JSON_PATH = root / "quick_replies.json"
    reply_store.BACKUP_PATH = root / "quick_replies_backup.json"
    reply_store.SEED_PATH = root / "quick_replies_seed.json"
    reply_button_store._cache = None
    reply_button_store.JSON_PATH = root / "quick_reply_buttons.json"
    reply_button_store.SEED_PATH = root / "quick_reply_buttons_seed.json"
    refresh_button_maps()
    reload_quick_replies()


def test_reply_mgmt_menu_buttons() -> None:
    flat = [b for row in admin_reply_mgmt_menu_rows("km") for b in row]
    assert BTN_ADMIN_EDIT in flat
    assert BTN_ADMIN_ADD in flat
    assert BTN_ADMIN_DELETE in flat


def test_validate_new_key_rules() -> None:
    assert validate_new_key("Bad Key") is not None
    assert validate_new_key("price") is not None
    assert validate_new_key("night_delivery") is None


def test_add_and_delete_reply_roundtrip() -> None:
    work = Path(tempfile.mkdtemp())
    try:
        _setup_tmp_stores(work)
        refresh_button_maps()

        reply_store.backup_replies_file()
        reply_store.add_reply(
            "night_delivery",
            {
                "th": "TH night delivery",
                "en": "TODO",
                "km": "TODO",
                "id": "TODO",
                "cn": "TODO",
            },
            backup=False,
        )
        reply_button_store.add_button_mapping(
            "status_updates",
            "night_delivery",
            {"km": "🚚 /night", "th": "🚚 /night", "id": "🚚 /night"},
        )
        refresh_button_maps()

        assert "night_delivery" in get_quick_replies()
        assert "night_delivery" in reply_button_store.category_key_order("status_updates")

        reply_store.delete_reply("night_delivery", backup=False)
        reply_button_store.remove_button_mapping("night_delivery")
        refresh_button_maps()

        assert "night_delivery" not in get_quick_replies()
        assert "night_delivery" not in reply_button_store.all_managed_keys()
    finally:
        _restore_stores()
        shutil.rmtree(work, ignore_errors=True)


def test_timestamped_reply_backup() -> None:
    work = Path(tempfile.mkdtemp())
    try:
        _setup_tmp_stores(work)
        path = reply_store.backup_replies_file()
        assert path is not None
        assert path.name.startswith("quick_replies_backup_")
    finally:
        _restore_stores()
        shutil.rmtree(work, ignore_errors=True)


def test_owner_access_denied_message() -> None:
    assert "Owner only" in OWNER_ACCESS_DENIED


def test_main_menu_reply_management_label() -> None:
    from quick_replies import main_menu_rows

    flat = [b for row in main_menu_rows("km") for b in row]
    assert BTN_REPLY_MGMT == "🔧 Reply Management"
    assert BTN_REPLY_MGMT in flat


if __name__ == "__main__":
    test_reply_mgmt_menu_buttons()
    test_validate_new_key_rules()
    test_add_and_delete_reply_roundtrip()
    test_timestamped_reply_backup()
    test_owner_access_denied_message()
    test_main_menu_reply_management_label()
    print("ALL OK")
