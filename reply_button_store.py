"""Load and save quick reply button mappings from quick_reply_buttons.json."""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("cherry.quick_reply.buttons")

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "quick_reply_buttons.json"
SEED_PATH = ROOT / "quick_reply_buttons_seed.json"

CATEGORIES = (
    "questions_to_customer",
    "replies_to_customer",
    "status_updates",
)
STAFF_LANGS = frozenset({"km", "th", "id"})

_cache: dict[str, Any] | None = None


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def backup_buttons_file() -> Path | None:
    if not JSON_PATH.is_file():
        return None
    dest = ROOT / f"quick_reply_buttons_backup_{_timestamp()}.json"
    shutil.copy2(JSON_PATH, dest)
    logger.info("Backed up buttons to %s", dest.name)
    return dest


def _empty_category() -> dict[str, Any]:
    return {
        "key_order": [],
        "buttons": {lang: {} for lang in STAFF_LANGS},
    }


def _validate_config(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("quick_reply_buttons.json must be a JSON object")
    categories = data.get("categories")
    if not isinstance(categories, dict):
        raise ValueError("missing categories object")
    out_cats: dict[str, Any] = {}
    for cat in CATEGORIES:
        block = categories.get(cat)
        if not isinstance(block, dict):
            block = _empty_category()
        key_order = block.get("key_order")
        if not isinstance(key_order, list):
            raise ValueError(f"invalid key_order for {cat}")
        buttons = block.get("buttons")
        if not isinstance(buttons, dict):
            raise ValueError(f"invalid buttons for {cat}")
        norm_buttons: dict[str, dict[str, str]] = {}
        for lang in STAFF_LANGS:
            lang_map = buttons.get(lang, {})
            if not isinstance(lang_map, dict):
                raise ValueError(f"invalid buttons.{lang} for {cat}")
            norm_buttons[lang] = {str(k): str(v) for k, v in lang_map.items()}
        for key in key_order:
            if not isinstance(key, str):
                raise ValueError(f"invalid key in {cat}: {key!r}")
            for lang in STAFF_LANGS:
                if key not in norm_buttons[lang]:
                    raise ValueError(f"missing button label {cat}/{lang}/{key}")
        out_cats[cat] = {"key_order": list(key_order), "buttons": norm_buttons}
    return {"categories": out_cats}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    validated = _validate_config(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".json")
    tmp_path = Path(tmp_name)
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            json.dump(validated, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        tmp_path.replace(path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def ensure_buttons_file() -> None:
    if JSON_PATH.is_file():
        return
    if SEED_PATH.is_file():
        shutil.copy2(SEED_PATH, JSON_PATH)
        logger.info("Initialized %s from seed", JSON_PATH.name)
        return
    raise FileNotFoundError(f"Missing {SEED_PATH.name} seed file")


def load_button_config(*, force: bool = False) -> dict[str, Any]:
    global _cache
    if _cache is not None and not force:
        return _cache
    ensure_buttons_file()
    with open(JSON_PATH, encoding="utf-8") as fh:
        _cache = _validate_config(json.load(fh))
    return _cache


def reload_button_config() -> dict[str, Any]:
    return load_button_config(force=True)


def category_key_order(category: str) -> list[str]:
    cfg = load_button_config()
    return list(cfg["categories"][category]["key_order"])


def category_buttons(category: str, staff_lang: str) -> dict[str, str]:
    lang = staff_lang if staff_lang in STAFF_LANGS else "km"
    cfg = load_button_config()
    return dict(cfg["categories"][category]["buttons"][lang])


def all_managed_keys() -> list[str]:
    cfg = load_button_config()
    keys: list[str] = []
    seen: set[str] = set()
    for cat in CATEGORIES:
        for key in cfg["categories"][cat]["key_order"]:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def key_category(key: str) -> str | None:
    cfg = load_button_config()
    for cat in CATEGORIES:
        if key in cfg["categories"][cat]["key_order"]:
            return cat
    return None


def add_button_mapping(
    category: str,
    key: str,
    labels: dict[str, str],
) -> None:
    if category not in CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    cfg = load_button_config()
    cat_block = cfg["categories"][category]
    if key in cat_block["key_order"]:
        raise ValueError(f"key already exists in {category}: {key}")
    for other in CATEGORIES:
        if other != category and key in cfg["categories"][other]["key_order"]:
            raise ValueError(f"key already exists in {other}: {key}")

    backup_buttons_file()
    updated = json.loads(json.dumps(cfg))
    cat = updated["categories"][category]
    cat["key_order"].append(key)
    for lang in STAFF_LANGS:
        label = labels.get(lang, labels.get("km", ""))
        if not str(label).strip():
            raise ValueError(f"missing staff button label for {lang}")
        cat["buttons"][lang][key] = str(label)

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        raise

    global _cache
    _cache = _validate_config(updated)
    logger.info("Added button mapping key=%s category=%s", key, category)


def remove_button_mapping(key: str) -> None:
    cfg = load_button_config()
    category = key_category(key)
    if category is None:
        return

    backup_buttons_file()
    updated = json.loads(json.dumps(cfg))
    cat = updated["categories"][category]
    cat["key_order"] = [k for k in cat["key_order"] if k != key]
    for lang in STAFF_LANGS:
        cat["buttons"][lang].pop(key, None)

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        raise

    global _cache
    _cache = _validate_config(updated)
    logger.info("Removed button mapping key=%s category=%s", key, category)


def button_label(key: str, staff_lang: str) -> str | None:
    category = key_category(key)
    if category is None:
        return None
    lang = staff_lang if staff_lang in STAFF_LANGS else "km"
    return category_buttons(category, lang).get(key)


def update_button_label(key: str, staff_lang: str, label: str, *, backup: bool = True) -> None:
    category = key_category(key)
    if category is None:
        raise ValueError(f"unknown button key: {key}")
    lang = str(staff_lang).strip().lower()
    if lang not in STAFF_LANGS:
        raise ValueError(f"unsupported staff language: {staff_lang}")
    new_label = str(label).strip()
    if not new_label:
        raise ValueError("button label cannot be empty")

    cfg = load_button_config()
    if key not in cfg["categories"][category]["key_order"]:
        raise ValueError(f"key not in category: {key}")

    if backup:
        backup_buttons_file()

    updated = json.loads(json.dumps(cfg))
    updated["categories"][category]["buttons"][lang][key] = new_label

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        raise

    global _cache
    _cache = _validate_config(updated)
    logger.info("Updated button label key=%s lang=%s", key, lang)
