# CHERRY SUPPORT AI — Unified Bot

บอท Telegram **ตัวเดียว** สำหรับ CHERRY Wash & Dry — แยกโหมดตามแชท

**Production:** https://cherry-support-ai.onrender.com

## โหมดการทำงาน

| แชท | โหมด | ทำอะไร |
|-----|------|--------|
| **กลุ่มแปล** (`STAFF_GROUP_ID` และ/หรือ `SUPPORT_AI_GROUP_ID`) | แปลภาษา | วางข้อความลูกค้า → Reply คำตอบ (แบบ Google Translate) |
| **แชทส่วนตัว / กลุ่มอื่น** | FAQ | เมนูคำตอบสำเร็จรูป (ไม่ใช้ AI ตอบอิสระ) |

**BOT_TOKEN ตัวเดียว** — ไม่ต้องแยก 2 บอท

## ไฟล์สำคัญ

| ไฟล์ | หน้าที่ |
|------|---------|
| `app.py` | รวมบอท + routing ตามกลุ่ม |
| `faq_content.py` | คำตอบ FAQ (แก้ที่นี่) |
| `faq_handlers.py` | ปุ่มเมนู FAQ |
| `staff_translate.py` | แปลภาษาพนักงาน (OpenAI) |

## Environment (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Token บอท CHERRY SUPPORT AI |
| `STAFF_GROUP_ID` | Yes* | กลุ่มแปล #1 |
| `SUPPORT_AI_GROUP_ID` | Yes* | กลุ่มแปล #2 (CHERRY_SUPPORT_AI) |
| `OPENAI_API_KEY` | Yes | สำหรับโหมดแปล |
| `WEBHOOK_URL` | Yes | `https://cherry-support-ai.onrender.com/telegram` |
| `ALLOWED_USER_IDS` | Optional | ทดสอบแปลใน DM |

## คำสั่ง

| Command | FAQ chat | Staff group |
|---------|----------|-------------|
| `/start` | เมนู FAQ | เมนูแปล |
| `/menu` | เมนู FAQ | เมนูแปล |
| `/language` | เปลี่ยนภาษา FAQ | — |
| `/lang` | เปลี่ยนภาษา FAQ | เปลี่ยนภาษาพนักงาน |
| `/group` | คำแนะนำ | แสดง group ID |
| `/health` | OK | OK + OpenAI |

## วิธีใช้ในกลุ่มแปล (Google Translate mode)

1. เลือกภาษาพนักงานครั้งเดียว (`/lang`) — Khmer / Thai / Indonesian
2. **วางข้อความลูกค้า** ในกลุ่ม → บอทอธิบายความหมาย (ไม่ต้องกดปุ่ม)
3. **Reply** ข้อความนั้น → พิมพ์คำตอบ → บอทแปลเป็นภาษาลูกค้า → Copy ส่ง

ปุ่ม 📩 / ✍️ ยังใช้ได้ แต่ไม่บังคับ

## Setup

1. Add บอทเข้า **กลุ่ม staff** (แปล)
2. ลูกค้า/พนักงานเปิด **แชทส่วนตัว** กับบอท → FAQ
3. BotFather `/setprivacy` → **Disable** (ให้เห็นข้อความในกลุ่ม staff)

## Tests

```bash
python -m unittest discover -s tests -v
```

## Deploy

```bash
git push origin main
```

**Not CHERRY BOT V3** — ไม่เชื่อม Google Sheet / ออเดอร์ / บิล
