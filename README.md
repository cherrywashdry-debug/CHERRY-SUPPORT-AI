# CHERRY SUPPORT AI — Unified Bot

บอท Telegram **ตัวเดียว** บน service **cherry-support-ai** — แยกโหมดตามกลุ่ม

**Production:** https://cherry-support-ai.onrender.com

## โหมดการทำงาน

| แชท | Env | โหมด |
|-----|-----|------|
| **กลุ่มแปล** | `TRANSLATE_AI_GROUP_ID` | เลือกภาษา → ส่งข้อความ → **แปลอย่างเดียว** |
| **กลุ่ม FAQ** | `ANSWER_GROUP_ID` | เมนูคำตอบสำเร็จรูป |
| **แชทส่วนตัว** | — | FAQ |
| **DM ทดสอบแปล** | `ALLOWED_USER_IDS` | แปล (optional) |

**BOT_TOKEN ตัวเดียว** — ไม่ต้องแยก service

## Environment (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Token บอท CHERRY SUPPORT AI |
| `TRANSLATE_AI_GROUP_ID` | Yes | กลุ่มแปลภาษา |
| `ANSWER_GROUP_ID` | Yes | กลุ่ม FAQ |
| `OPENAI_API_KEY` | Yes | สำหรับโหมดแปล |
| `WEBHOOK_URL` | Yes | `https://cherry-support-ai.onrender.com/telegram` |
| `TZ` | Yes | `Asia/Phnom_Penh` |
| `ALLOWED_USER_IDS` | Optional | ทดสอบแปลใน DM |

ชื่อเก่ายังใช้ได้: `STAFF_GROUP_ID` → translate, `SUPPORT_AI_GROUP_ID` → answer

## คำสั่ง

| Command | FAQ | Translate group |
|---------|-----|-----------------|
| `/start` | เมนู FAQ | เมนูแปล |
| `/menu` | เมนู FAQ | เมนูแปล |
| `/language` | เปลี่ยนภาษา FAQ | — |
| `/lang` | เปลี่ยนภาษา FAQ | เปลี่ยนภาษาพนักงาน |
| `/group` | คำแนะนำ | แสดง group ID |
| `/health` | OK | OK + OpenAI |

## วิธีใช้ในกลุ่มแปล

1. `/start` หรือ `/menu` → เลือก **Translate To Thai / English / Khmer / Indonesian / Chinese**
2. ส่งข้อความที่ต้องการแปล
3. ได้คำแปล + ปุ่ม Copy (หรือเลือก **All 5 Languages**)

**แปลอย่างเดียว — ไม่ตอบคำถาม ไม่ถามกลับ**

## Setup

1. Add บอทเข้า **กลุ่มแปล** และ **กลุ่ม FAQ** (คนละกลุ่ม)
2. ส่ง `/group` ในแต่ละกลุ่ม → copy ID ไป Render
3. BotFather `/setprivacy` → **Disable** (กลุ่มแปล)

## Tests

```bash
python -m unittest discover -s tests -v
```

## Deploy

Push แล้ว **Manual Deploy** บน Render — ตรวจ `/health` ว่าเป็น `V5-GROUP-SPLIT`

**Not CHERRY BOT V3** — ไม่เชื่อม Google Sheet / ออเดอร์ / บิล
