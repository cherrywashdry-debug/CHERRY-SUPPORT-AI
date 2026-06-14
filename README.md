# CHERRY Quick Reply Bot

Staff-only Telegram bot for **fixed approved customer replies**. Deploys to Render as `cherry-support-ai`.

**Not** a translator, AI chat, customer FAQ, or CHERRY BOT V3.

## Flow

1. Staff chooses staff language (Khmer / Thai / Indonesian)
2. Staff chooses customer reply language (Thai / English / Khmer / Indonesian / Chinese)
3. Staff sees quick-reply buttons in their language
4. Press a button → bot sends the fixed reply in the customer language

## Commands

| Command | Action |
|---------|--------|
| `/start` | Choose staff language |
| `/language` | Change staff language |
| `/customer` | Change customer language |
| `/menu` | Quick reply menu |
| `/clear` | Reset session |

## Edit replies

All approved text lives in **`quick_replies.py`** only. Each reply key has 5 languages: `TH`, `EN`, `KH`, `ID`, `CN`.

## Render env

| Key | Required |
|-----|----------|
| `BOT_TOKEN` | Yes |
| `ALLOWED_USER_IDS` | Yes (comma-separated Telegram user IDs) |
| `WEBHOOK_URL` | Yes |
| `TZ` | Optional (`Asia/Phnom_Penh`) |

No OpenAI keys needed.

## Local test

```bash
pip install -r requirements.txt
python -m tests.test_quick_reply_bot
```

## Deploy

Push `_support_ai_deploy` to its Render repo and **Manual Deploy**. Remove unused `OPENAI_API_KEY` / `OPENAI_MODEL` from Render if still set.
