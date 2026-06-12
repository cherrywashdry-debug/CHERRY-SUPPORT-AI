# CHERRY Support AI

Separate Telegram bot for CHERRY staff — two-layer reply drafts (Khmer summary + customer-language reply).

**Production:** https://cherry-support-ai.onrender.com

## Render settings (pick ONE)

### Option A — Docker (recommended if exit status 127)

| Setting | Value |
|---------|-------|
| **Language / Runtime** | **Docker** |
| **Dockerfile Path** | `./Dockerfile` |
| **Root Directory** | *(empty)* |
| **Build Command** | *(empty)* |
| **Start Command** | *(empty)* |

### Option B — Native Python

| Setting | Value |
|---------|-------|
| **Language / Runtime** | **Python 3** (not Rust) |
| **Root Directory** | *(empty)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python3 app.py` |
| **Health Check** | `/health` |

`runtime.txt` pins Python 3.12.8.

If logs show `python: command not found` or **exit status 127** → Language is still Rust/wrong. **Use Option A (Docker).**

## Setup

1. Set Render env: `BOT_TOKEN`, `OPENAI_API_KEY`, `WEBHOOK_URL`
2. Deploy → send `/group` in staff Telegram group → copy `STAFF_GROUP_ID` → redeploy
3. BotFather `/setprivacy` → **Disable** for the support bot

## Commands

| Command | Purpose |
|---------|---------|
| `/group` | Show Telegram group ID for Render |
| `/start` | Usage |
| `/health` | Bot + knowledge check |

Paste customer messages in the staff group for AI draft replies.
