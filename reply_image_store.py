"""Optional reply images (Telegram file_id) per key and customer language."""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("cherry.quick_reply.images")

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "quick_reply_images.json"
SEED_PATH = ROOT / "quick_reply_images_seed.json"

CUSTOMER_LANGS = frozenset({"th", "en", "km", "id", "cn"})

_cache: dict[str, dict[str, str]] | None = None


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def backup_images_file() -> Path | None:
    if not JSON_PATH.is_file():
        return None
    dest = ROOT / f"quick_reply_images_backup_{_timestamp()}.json"
    shutil.copy2(JSON_PATH, dest)
    logger.info("Backed up images to %s", dest.name)
    return dest


def _validate_images(data: Any) -> dict[str, dict[str, str]]:
    if not isinstance(data, dict):
        raise ValueError("quick_reply_images.json must be a JSON object")
    out: dict[str, dict[str, str]] = {}
    for key, block in data.items():
        if not isinstance(key, str) or not isinstance(block, dict):
            raise ValueError(f"invalid image block: {key!r}")
        langs: dict[str, str] = {}
        for lang, file_id in block.items():
            if lang not in CUSTOMER_LANGS:
                raise ValueError(f"invalid language {lang!r} for key {key!r}")
            if not isinstance(file_id, str):
                raise ValueError(f"invalid file_id for {key}/{lang}")
            langs[lang] = file_id.strip()
        out[key] = langs
    return out


def _write_json(path: Path, data: dict[str, dict[str, str]]) -> None:
    validated = _validate_images(data)
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


def ensure_images_file() -> None:
    if JSON_PATH.is_file():
        return
    if SEED_PATH.is_file():
        shutil.copy2(SEED_PATH, JSON_PATH)
        logger.info("Initialized %s from seed", JSON_PATH.name)
        return
    _write_json(JSON_PATH, {})


def load_images(*, force: bool = False) -> dict[str, dict[str, str]]:
    global _cache
    if _cache is not None and not force:
        return _cache
    ensure_images_file()
    with open(JSON_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)
    _cache = _validate_images(raw if raw else {})
    return _cache


def reload_images() -> dict[str, dict[str, str]]:
    return load_images(force=True)


def get_image_file_id(key: str, lang: str) -> str:
    lang_key = str(lang).strip().lower()
    block = load_images().get(key, {})
    return str(block.get(lang_key, "")).strip()


def save_image(key: str, lang: str, file_id: str, *, backup: bool = True) -> None:
    lang_key = str(lang).strip().lower()
    if lang_key not in CUSTOMER_LANGS:
        raise ValueError(f"unsupported language: {lang}")
    fid = str(file_id).strip()
    if not fid:
        raise ValueError("file_id cannot be empty")

    current = load_images()
    updated = {k: dict(v) for k, v in current.items()}
    updated.setdefault(key, {})
    updated[key][lang_key] = fid

    if backup:
        backup_images_file()

    _write_json(JSON_PATH, updated)
    global _cache
    _cache = updated
    logger.info("Saved reply image key=%s lang=%s", key, lang_key)


def remove_image(key: str, lang: str, *, backup: bool = True) -> None:
    lang_key = str(lang).strip().lower()
    if lang_key not in CUSTOMER_LANGS:
        raise ValueError(f"unsupported language: {lang}")

    current = load_images()
    if key not in current or lang_key not in current[key]:
        return

    updated = {k: dict(v) for k, v in current.items()}
    updated[key].pop(lang_key, None)
    if not updated[key]:
        updated.pop(key, None)

    if backup:
        backup_images_file()

    _write_json(JSON_PATH, updated)
    global _cache
    _cache = updated
    logger.info("Removed reply image key=%s lang=%s", key, lang_key)


def remove_key_images(key: str, *, backup: bool = True) -> None:
    current = load_images()
    if key not in current:
        return
    if backup:
        backup_images_file()
    updated = {k: dict(v) for k, v in current.items() if k != key}
    _write_json(JSON_PATH, updated)
    global _cache
    _cache = updated
    logger.info("Removed all reply images for key=%s", key)
