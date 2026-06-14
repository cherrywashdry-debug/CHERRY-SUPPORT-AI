#!/usr/bin/env python3
"""One-shot fix + deploy cherry-support-ai on Render via API.

Requires env:
  RENDER_API_KEY   — https://dashboard.render.com/u/settings#api-keys
  BOT_TOKEN        — Support AI bot (optional if already on Render)
  OPENAI_API_KEY   — optional if already on Render

Usage:
  python deploy_render.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.render.com/v1"
SERVICE_ID = os.getenv("RENDER_SERVICE_ID", "srv-d8lt22d7vvec73f5fa3g").strip()
SERVICE_NAME = os.getenv("RENDER_SERVICE_NAME", "cherry-support-ai").strip()
WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://cherry-support-ai.onrender.com/telegram",
).strip()
TRANSLATE_GROUP_ID = os.getenv("TRANSLATE_AI_GROUP_ID", "-1003860053672").strip()
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS", "1087968824").strip()
EXPECTED_HEALTH = "V6.2-GROUP-MODE-FIX"
HEALTH_URL = "https://cherry-support-ai.onrender.com/health"


def api_key() -> str:
    key = os.getenv("RENDER_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "Missing RENDER_API_KEY.\n"
            "Create at https://dashboard.render.com/u/settings#api-keys\n"
            "Then run: set RENDER_API_KEY=rnd_... && python deploy_render.py"
        )
    return key


def request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{API}{path}"
    headers = {
        "Authorization": f"Bearer {api_key()}",
        "Accept": "application/json",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Render API {method} {path} failed ({exc.code}): {detail}") from exc


def get_service(service_id: str) -> dict:
    payload = request("GET", f"/services/{service_id}")
    return payload.get("service") or payload


def patch_service_docker(service_id: str) -> dict:
    body = {
        "rootDir": "",
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "runtime": "docker",
            "healthCheckPath": "/health",
            "envSpecificDetails": {
                "dockerfilePath": "./Dockerfile",
                "dockerContext": ".",
                "dockerCommand": "",
            },
        },
    }
    payload = request("PATCH", f"/services/{service_id}", body)
    return payload.get("service") or payload


def list_env_vars(service_id: str) -> dict[str, str]:
    payload = request("GET", f"/services/{service_id}/env-vars?limit=100")
    if isinstance(payload, list):
        rows = payload
    else:
        rows = payload.get("envVars") or []
    out: dict[str, str] = {}
    for item in rows:
        row = item.get("envVar") or item
        key = str(row.get("key", "") or "").strip()
        if key:
            out[key] = str(row.get("value", "") or "")
    return out


def upsert_env_var(service_id: str, key: str, value: str) -> None:
    encoded = urllib.parse.quote(key, safe="")
    request("PUT", f"/services/{service_id}/env-vars/{encoded}", {"value": value})


def ensure_env_vars(service_id: str) -> None:
    desired = {
        "WEBHOOK_URL": WEBHOOK_URL,
        "TZ": "Asia/Phnom_Penh",
        "OPENAI_MODEL": "gpt-4o-mini",
        "STAFF_GROUP_ID": TRANSLATE_GROUP_ID,
        "TRANSLATE_AI_GROUP_ID": TRANSLATE_GROUP_ID,
        "ALLOWED_USER_IDS": ALLOWED_USER_IDS,
    }
    bot = os.getenv("BOT_TOKEN", "").strip()
    if bot:
        desired["BOT_TOKEN"] = bot
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        desired["OPENAI_API_KEY"] = openai_key

    existing = list_env_vars(service_id)
    for key, value in desired.items():
        if not value:
            continue
        if existing.get(key) == value:
            print(f"env OK: {key}")
            continue
        upsert_env_var(service_id, key, value)
        print(f"env set: {key}")

    if not existing.get("BOT_TOKEN") and not bot:
        print("WARN: BOT_TOKEN not on Render and not in local env — set in Render after deploy")


def trigger_deploy(service_id: str) -> dict:
    body = {"clearCache": "clear"}
    payload = request("POST", f"/services/{service_id}/deploys", body)
    return payload.get("deploy") or payload


def wait_deploy(service_id: str, deploy_id: str, timeout_sec: int = 900) -> dict:
    deadline = time.time() + timeout_sec
    last: dict = {}
    while time.time() < deadline:
        payload = request("GET", f"/services/{service_id}/deploys/{deploy_id}")
        last = payload.get("deploy") or payload
        status = str(last.get("status", "") or "").lower()
        print(f"deploy status: {status}")
        if status in {"live", "deactivated"}:
            return last
        if status in {"build_failed", "update_failed", "canceled", "cancelled"}:
            raise SystemExit(f"Deploy failed: {json.dumps(last, indent=2)}")
        time.sleep(10)
    raise SystemExit(f"Deploy timed out: {json.dumps(last, indent=2)}")


def resolve_service_id() -> str:
    if SERVICE_ID:
        return SERVICE_ID
    payload = request("GET", "/services?limit=100")
    services = payload if isinstance(payload, list) else payload.get("services") or []
    for item in services:
        svc = item.get("service") or item
        if str(svc.get("name", "")).strip() == SERVICE_NAME:
            return str(svc["id"])
    raise SystemExit(f"Service {SERVICE_NAME} not found")


def wait_health(expected: str = EXPECTED_HEALTH, timeout_sec: int = 120) -> str:
    deadline = time.time() + timeout_sec
    last = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=20) as resp:
                last = resp.read().decode("utf-8", errors="replace").strip()
                print(f"health: {last}")
                if expected in last:
                    return last
        except Exception as exc:
            print(f"health check: {exc}")
        time.sleep(8)
    raise SystemExit(f"Health never showed {expected!r}. Last: {last!r}")


def main() -> int:
    service_id = resolve_service_id()
    print(f"Service: {SERVICE_NAME} ({service_id})")

    before = get_service(service_id)
    runtime = (
        (before.get("serviceDetails") or {}).get("runtime")
        or "unknown"
    )
    root = before.get("rootDir") or "(empty)"
    print(f"Before: runtime={runtime} rootDir={root!r}")

    patched = patch_service_docker(service_id)
    runtime_after = (patched.get("serviceDetails") or {}).get("runtime")
    print(f"Patched: runtime={runtime_after} rootDir={patched.get('rootDir')!r}")

    ensure_env_vars(service_id)

    deploy = trigger_deploy(service_id)
    deploy_id = str(deploy.get("id", "") or "")
    print(f"Deploy triggered: {deploy_id}")
    print(f"Dashboard: https://dashboard.render.com/web/{service_id}")

    if deploy_id:
        final = wait_deploy(service_id, deploy_id)
        print(f"Done: {final.get('status')} commit={final.get('commit', {}).get('id', '')}")

    health = wait_health()
    print(f"OK — live health: {health}")
    print("Telegram: /start in TRANSLATE_AI_GROUP -> 5 language buttons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
