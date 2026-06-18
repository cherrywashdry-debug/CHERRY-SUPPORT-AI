"""Approved staff registry — staff_users.json (private chat access control)."""
from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("cherry.quick_reply.staff")

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "staff_users.json"
BACKUP_PATH = ROOT / "staff_users_backup.json"
SEED_PATH = ROOT / "staff_users_seed.json"

_cache: dict[str, Any] | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _empty_data() -> dict[str, Any]:
    return {"approved_staff": [], "pending_requests": []}


def _parse_allowed_env() -> list[int]:
    ids: list[int] = []
    for part in str(os.getenv("ALLOWED_USER_IDS", "")).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids


def allowed_user_ids() -> list[int]:
    return _parse_allowed_env()


def _validate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("staff_users.json must be a JSON object")
    approved = data.get("approved_staff", [])
    pending = data.get("pending_requests", [])
    if not isinstance(approved, list) or not isinstance(pending, list):
        raise ValueError("invalid staff_users.json structure")
    for row in approved:
        if not isinstance(row, dict) or "user_id" not in row:
            raise ValueError("invalid approved_staff row")
    for row in pending:
        if not isinstance(row, dict) or "user_id" not in row:
            raise ValueError("invalid pending_requests row")
    return {"approved_staff": approved, "pending_requests": pending}


def _write_json(path: Path, data: dict[str, Any]) -> None:
    validated = _validate(data)
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


def ensure_staff_file() -> None:
    if JSON_PATH.is_file():
        data = _read_json_file()
        migrated = _import_legacy_staff_if_empty(data)
        if migrated is not data:
            _write_json(JSON_PATH, migrated)
            global _cache
            _cache = migrated
        return
    if SEED_PATH.is_file():
        shutil.copy2(SEED_PATH, JSON_PATH)
        data = _read_json_file()
        migrated = _import_legacy_staff_if_empty(data)
        if migrated is not data:
            _write_json(JSON_PATH, migrated)
        logger.info("Initialized %s from seed", JSON_PATH)
        return
    data = _empty_data()
    data = _import_legacy_staff_if_empty(data)
    _write_json(JSON_PATH, data)
    logger.info("Initialized %s", JSON_PATH)


def _read_json_file() -> dict[str, Any]:
    with open(JSON_PATH, encoding="utf-8") as fh:
        return _validate(json.load(fh))


def _import_legacy_staff_if_empty(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("approved_staff"):
        return data
    legacy_ids = _parse_allowed_env()
    if not legacy_ids:
        return data
    out = dict(data)
    out["approved_staff"] = [
        {
            "user_id": uid,
            "name": "Legacy Staff",
            "username": "",
            "status": "active",
            "approved_at": _now_iso(),
        }
        for uid in legacy_ids
    ]
    return out


def load_staff_data(*, force: bool = False) -> dict[str, Any]:
    global _cache
    if _cache is not None and not force:
        return _cache
    ensure_staff_file()
    with open(JSON_PATH, encoding="utf-8") as fh:
        _cache = _validate(json.load(fh))
    return _cache


def reload_staff_data() -> dict[str, Any]:
    return load_staff_data(force=True)


def _save(data: dict[str, Any]) -> None:
    if JSON_PATH.is_file():
        shutil.copy2(JSON_PATH, BACKUP_PATH)
    try:
        _write_json(JSON_PATH, data)
    except Exception:
        if BACKUP_PATH.is_file() and not JSON_PATH.is_file():
            shutil.copy2(BACKUP_PATH, JSON_PATH)
        raise
    global _cache
    _cache = _validate(data)


def find_approved(user_id: int) -> dict[str, Any] | None:
    for row in load_staff_data()["approved_staff"]:
        if int(row.get("user_id", 0)) == int(user_id):
            return row
    return None


def is_active_staff(user_id: int) -> bool:
    row = find_approved(user_id)
    return row is not None and str(row.get("status", "")).lower() == "active"


def has_pending_request(user_id: int) -> bool:
    for row in load_staff_data()["pending_requests"]:
        if int(row.get("user_id", 0)) == int(user_id):
            return True
    return False


def list_active_staff() -> list[dict[str, Any]]:
    return [
        row
        for row in load_staff_data()["approved_staff"]
        if str(row.get("status", "")).lower() == "active"
    ]


def list_pending_requests() -> list[dict[str, Any]]:
    return list(load_staff_data()["pending_requests"])


def add_pending_request(user_id: int, name: str, username: str) -> None:
    data = reload_staff_data()
    if is_active_staff(user_id):
        raise ValueError("user already approved")
    pending = [row for row in data["pending_requests"] if int(row["user_id"]) != int(user_id)]
    pending.append(
        {
            "user_id": int(user_id),
            "name": name or "Unknown",
            "username": username or "",
            "requested_at": _now_iso(),
        }
    )
    data["pending_requests"] = pending
    _save(data)


def approve_staff(user_id: int, name: str = "", username: str = "") -> None:
    data = reload_staff_data()
    uid = int(user_id)
    pending = [row for row in data["pending_requests"] if int(row["user_id"]) != uid]
    existing = find_approved(uid)
    approved = [row for row in data["approved_staff"] if int(row.get("user_id", 0)) != uid]
    if existing:
        existing = dict(existing)
        existing["status"] = "active"
        existing["approved_at"] = _now_iso()
        if name:
            existing["name"] = name
        if username:
            existing["username"] = username
        approved.append(existing)
    else:
        approved.append(
            {
                "user_id": uid,
                "name": name or "Staff",
                "username": username or "",
                "status": "active",
                "approved_at": _now_iso(),
            }
        )
    data["approved_staff"] = approved
    data["pending_requests"] = pending
    _save(data)


def reject_staff(user_id: int) -> None:
    data = reload_staff_data()
    uid = int(user_id)
    data["pending_requests"] = [
        row for row in data["pending_requests"] if int(row["user_id"]) != uid
    ]
    _save(data)


def disable_staff(user_id: int) -> None:
    data = reload_staff_data()
    uid = int(user_id)
    updated: list[dict[str, Any]] = []
    found = False
    for row in data["approved_staff"]:
        if int(row.get("user_id", 0)) == uid:
            found = True
            item = dict(row)
            item["status"] = "disabled"
            updated.append(item)
        else:
            updated.append(row)
    if not found:
        raise ValueError("staff not found")
    data["approved_staff"] = updated
    _save(data)


def staff_display_name(row: dict[str, Any]) -> str:
    name = str(row.get("name") or "Staff")
    username = str(row.get("username") or "").strip()
    uid = int(row.get("user_id", 0))
    if username and not username.startswith("@"):
        username = f"@{username}"
    if username:
        return f"{name} ({username}) — {uid}"
    return f"{name} — {uid}"
