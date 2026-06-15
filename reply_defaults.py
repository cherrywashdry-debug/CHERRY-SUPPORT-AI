"""Built-in default replies — used only when quick_replies.json is missing."""
from __future__ import annotations

import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parent / "quick_replies_seed.json"


def build_default_replies() -> dict[str, dict[str, str]]:
    if not SEED_PATH.is_file():
        raise RuntimeError(f"missing seed file: {SEED_PATH}")
    with open(SEED_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise RuntimeError("invalid quick_replies_seed.json")
    return data
