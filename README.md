# CHERRY Support AI

Separate Telegram bot for CHERRY staff — two-layer reply drafts (Khmer summary + customer-language reply).

**Production:** https://cherry-support-ai.onrender.com

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
