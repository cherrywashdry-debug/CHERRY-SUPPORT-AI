"""Load and save quick reply texts from quick_replies.json (with backup)."""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("cherry.quick_reply.store")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
JSON_PATH = ROOT / "quick_replies.json"
BACKUP_PATH = ROOT / "quick_replies_backup.json"
SEED_PATH = ROOT / "quick_replies_seed.json"

CUSTOMER_LANGS = frozenset({"th", "en", "km", "id", "cn"})
TODO_TEXT = "TODO"

_cache: dict[str, dict[str, str]] | None = None


def _validate_replies(data: Any) -> dict[str, dict[str, str]]:
    if not isinstance(data, dict):
        raise ValueError("quick_replies.json must be a JSON object")
    out: dict[str, dict[str, str]] = {}
    for key, block in data.items():
        if not isinstance(key, str) or not isinstance(block, dict):
            raise ValueError(f"invalid reply key block: {key!r}")
        langs: dict[str, str] = {}
        for lang, text in block.items():
            if lang not in CUSTOMER_LANGS:
                raise ValueError(f"invalid language {lang!r} for key {key!r}")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"empty text for {key}/{lang}")
            langs[lang] = text
        if set(langs.keys()) != CUSTOMER_LANGS:
            raise ValueError(f"missing languages for key {key!r}")
        out[key] = langs
    if not out:
        raise ValueError("quick_replies.json is empty")
    return out


def _read_json(path: Path) -> dict[str, dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return _validate_replies(json.load(fh))


def _write_json(path: Path, data: dict[str, dict[str, str]]) -> None:
    validated = _validate_replies(data)
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


def ensure_replies_file() -> None:
    if JSON_PATH.is_file():
        return
    if SEED_PATH.is_file():
        shutil.copy2(SEED_PATH, JSON_PATH)
        logger.info("Initialized %s from seed file", JSON_PATH)
        return
    from reply_defaults import build_default_replies

    data = build_default_replies()
    _write_json(JSON_PATH, data)
    logger.info("Initialized %s from built-in defaults", JSON_PATH)


def load_replies(*, force: bool = False) -> dict[str, dict[str, str]]:
    global _cache
    if _cache is not None and not force:
        return _cache
    ensure_replies_file()
    _cache = _read_json(JSON_PATH)
    return _cache


def reload_replies() -> dict[str, dict[str, str]]:
    return load_replies(force=True)


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def backup_replies_file() -> Path | None:
    if not JSON_PATH.is_file():
        return None
    dest = ROOT / f"quick_replies_backup_{_timestamp()}.json"
    shutil.copy2(JSON_PATH, dest)
    shutil.copy2(JSON_PATH, BACKUP_PATH)
    logger.info("Backed up replies to %s", dest.name)
    return dest


def save_reply(key: str, lang: str, text: str, *, backup: bool = True) -> None:
    lang_key = str(lang).strip().lower()
    if lang_key not in CUSTOMER_LANGS:
        raise ValueError(f"unsupported language: {lang}")
    new_text = str(text)
    if not new_text.strip():
        raise ValueError("reply text cannot be empty")

    current = load_replies()
    if key not in current:
        raise ValueError(f"unknown reply key: {key}")

    updated = {k: dict(v) for k, v in current.items()}
    updated[key][lang_key] = new_text

    if backup:
        backup_replies_file()

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        if BACKUP_PATH.is_file() and not JSON_PATH.is_file():
            shutil.copy2(BACKUP_PATH, JSON_PATH)
        raise

    global _cache
    _cache = updated
    logger.info("Updated reply key=%s lang=%s", key, lang_key)


def add_reply(key: str, texts: dict[str, str], *, backup: bool = True) -> None:
    key_name = str(key).strip().lower()
    if not key_name:
        raise ValueError("reply key cannot be empty")
    current = load_replies()
    if key_name in current:
        raise ValueError(f"reply key already exists: {key_name}")

    block: dict[str, str] = {}
    for lang in CUSTOMER_LANGS:
        raw = str(texts.get(lang, TODO_TEXT))
        if not raw.strip():
            raw = TODO_TEXT
        block[lang] = raw

    updated = {k: dict(v) for k, v in current.items()}
    updated[key_name] = block

    if backup:
        backup_replies_file()

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        if BACKUP_PATH.is_file() and not JSON_PATH.is_file():
            shutil.copy2(BACKUP_PATH, JSON_PATH)
        raise

    global _cache
    _cache = updated
    logger.info("Added reply key=%s", key_name)


def delete_reply(key: str, *, backup: bool = True) -> None:
    key_name = str(key).strip()
    current = load_replies()
    if key_name not in current:
        raise ValueError(f"unknown reply key: {key_name}")

    updated = {k: dict(v) for k, v in current.items() if k != key_name}

    if backup:
        backup_replies_file()

    try:
        _write_json(JSON_PATH, updated)
    except Exception:
        if BACKUP_PATH.is_file() and not JSON_PATH.is_file():
            shutil.copy2(BACKUP_PATH, JSON_PATH)
        raise

    global _cache
    _cache = updated
    logger.info("Deleted reply key=%s", key_name)
