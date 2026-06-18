"""Tests for owner reply management (add / edit / delete with JSON stores)."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import reply_button_store
import reply_button_store
import reply_store
from admin_reply_mgmt import validate_new_key
from quick_replies import (
    BTN_ADMIN_ADD,
    BTN_ADMIN_DELETE,
    BTN_ADMIN_EDIT,
    BTN_ADMIN_EDIT_BUTTON,
    BTN_ADMIN_SET_EMOJI,
    BTN_ADMIN_SET_IMAGE,
    BTN_REPLY_MGMT,
    OWNER_ACCESS_DENIED,
    admin_reply_mgmt_menu_rows,
    get_quick_replies,
    refresh_button_maps,
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
    assert BTN_ADMIN_EDIT_BUTTON in flat
    assert BTN_ADMIN_SET_EMOJI in flat
    assert BTN_ADMIN_SET_IMAGE in flat
    assert BTN_ADMIN_ADD in flat
    assert BTN_ADMIN_DELETE in flat


def test_update_button_label(tmp_work: Path | None = None) -> None:
    work = Path(tempfile.mkdtemp())
    try:
        root = Path(reply_button_store.ROOT)
        shutil.copy2(root / "quick_reply_buttons_seed.json", work / "quick_reply_buttons_seed.json")
        shutil.copy2(work / "quick_reply_buttons_seed.json", work / "quick_reply_buttons.json")
        reply_button_store.JSON_PATH = work / "quick_reply_buttons.json"
        reply_button_store.SEED_PATH = work / "quick_reply_buttons_seed.json"
        reply_button_store._cache = None
        refresh_button_maps()
        reply_button_store.update_button_label("delivery_fee", "th", "🚚 /ค่าจัดส่ง", backup=False)
        refresh_button_maps()
        from reply_button_store import button_label

        assert button_label("delivery_fee", "th") == "🚚 /ค่าจัดส่ง"
    finally:
        reply_button_store._cache = None
        reply_button_store.JSON_PATH = root / "quick_reply_buttons.json"
        reply_button_store.SEED_PATH = root / "quick_reply_buttons_seed.json"
        refresh_button_maps()
        shutil.rmtree(work, ignore_errors=True)


def test_update_button_custom_emoji_id() -> None:
    work = Path(tempfile.mkdtemp())
    try:
        root = Path(reply_button_store.ROOT)
        shutil.copy2(root / "quick_reply_buttons_seed.json", work / "quick_reply_buttons_seed.json")
        shutil.copy2(work / "quick_reply_buttons_seed.json", work / "quick_reply_buttons.json")
        reply_button_store.JSON_PATH = work / "quick_reply_buttons.json"
        reply_button_store.SEED_PATH = work / "quick_reply_buttons_seed.json"
        reply_button_store._cache = None
        refresh_button_maps()
        reply_button_store.update_button_custom_emoji_id(
            "price",
            "km",
            "5373141891321699086",
            backup=False,
        )
        refresh_button_maps()
        assert reply_button_store.button_custom_emoji_id("price", "km") == "5373141891321699086"
        reply_button_store.update_button_custom_emoji_id("price", "km", None, backup=False)
        refresh_button_maps()
        assert reply_button_store.button_custom_emoji_id("price", "km") is None
    finally:
        reply_button_store._cache = None
        reply_button_store.JSON_PATH = root / "quick_reply_buttons.json"
        reply_button_store.SEED_PATH = root / "quick_reply_buttons_seed.json"
        refresh_button_maps()
        shutil.rmtree(work, ignore_errors=True)


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


def test_new_replies_have_all_customer_languages() -> None:
    from quick_replies import get_quick_replies

    langs = ("th", "en", "km", "id", "cn")
    for key in ("wash_set_14kg", "wash_set_18kg", "orders_after_8pm", "inspect_laundry", "cannot_check_before_wash", "has_stains"):
        block = get_quick_replies()[key]
        for lang in langs:
            text = str(block.get(lang, "")).strip()
            assert text, f"missing {key}/{lang}"
            assert text != "TODO", f"placeholder {key}/{lang}"


def test_pack_button_specs_into_rows() -> None:
    from quick_replies import pack_button_specs_into_rows

    specs = [
        ("💰 ราคา", None),
        ("🚚 ค่าส่ง", None),
        ("⏰ เวลาเปิด", None),
        ("⚠️ ข้อควรทราบก่อนใช้บริการ", None),
        ("🧺 ซักรวม/ซักแยก", None),
    ]
    rows = pack_button_specs_into_rows(specs)
    assert len(rows[0]) == 3
    assert len(rows[1]) == 1
    assert "⚠️" in rows[1][0][0]
    assert rows[2][0][0].startswith("🧺")


def test_main_menu_hides_admin_tools_from_staff() -> None:
    from quick_replies import BTN_STAFF_MGMT, main_menu_rows

    staff_flat = [b for row in main_menu_rows("km") for b in row]
    assert BTN_REPLY_MGMT not in staff_flat
    assert BTN_STAFF_MGMT not in staff_flat

    owner_flat = [b for row in main_menu_rows("km", show_staff_management=True) for b in row]
    assert BTN_STAFF_MGMT in owner_flat
    assert BTN_REPLY_MGMT not in owner_flat


if __name__ == "__main__":
    test_reply_mgmt_menu_buttons()
    test_update_button_label()
    test_update_button_custom_emoji_id()
    test_validate_new_key_rules()
    test_add_and_delete_reply_roundtrip()
    test_timestamped_reply_backup()
    test_owner_access_denied_message()
    test_new_replies_have_all_customer_languages()
    test_pack_button_specs_into_rows()
    test_main_menu_hides_admin_tools_from_staff()
    print("ALL OK")
