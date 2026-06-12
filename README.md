# CHERRY Support AI

Separate Telegram bot for CHERRY staff — two-layer reply drafts (Khmer summary + customer-language reply).

**Production:** https://cherry-support-ai.onrender.com

## Render settings

| Setting | Value |
|---------|-------|
| **Language / Runtime** | **Python 3** (not Rust) |
| **Root Directory** | *(empty)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python3 app.py` |
| **Health Check** | `/health` |

`runtime.txt` pins Python 3.12.8.
2. Deploy → send `/group` in staff Telegram group → copy `STAFF_GROUP_ID` → redeploy
3. BotFather `/setprivacy` → **Disable** for the support bot

## Commands

| Command | Purpose |
|---------|---------|
| `/group` | Show Telegram group ID for Render |
| `/start` | Usage |
| `/health` | Bot + knowledge check |

Paste customer messages in the staff group for AI draft replies.
