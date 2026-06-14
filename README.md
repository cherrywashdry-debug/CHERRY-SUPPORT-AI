# CHERRY SUPPORT AI — FAQ Bot

บอท Telegram FAQ แยกจาก CHERRY BOT V3 สำหรับ CHERRY Wash & Dry

**Production:** https://cherry-support-ai.onrender.com

## วัตถุประสงค์

ลูกค้าและพนักงานกดปุ่มเพื่อดูคำตอบ FAQ ที่เตรียมไว้แล้ว ไม่มี AI ตอบอิสระ ไม่เชื่อมออเดอร์/บิล/แต้ม

## ฟีเจอร์

- เมนูหลัก 8 หัวข้อ + เปลี่ยนภาษา
- เมนูย่อย: ราคา/ค่าส่ง, บริการซัก, รับ-ส่ง, อ่านก่อนใช้บริการ
- ภาษา: English (ค่าเริ่มต้น), ไทย, Khmer, Indonesia
- Khmer / Indonesia ใช้ข้อความ EN แทนจนกว่าจะแปล (TODO ใน `faq_content.py`)
- คำสั่ง: `/start`, `/menu`, `/language`, `/health`

## แก้คำตอบ FAQ

แก้ที่ `faq_content.py` เท่านั้น:

```python
FAQ_CONTENT["en"]["opening_hours"] = "..."
FAQ_CONTENT["th"]["opening_hours"] = "..."
```

## Render settings

### Option A — Docker (แนะนำ)

| Setting | Value |
|---------|-------|
| Language | Docker |
| Dockerfile Path | `./Dockerfile` |

### Option B — Native Python

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python3 app.py` |
| Health Check | `/health` |

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Token จาก BotFather (บอท CHERRY SUPPORT AI) |
| `WEBHOOK_URL` | Yes on Render | `https://cherry-support-ai.onrender.com/telegram` |

## Local run

```bash
pip install -r requirements.txt
cp .env.example .env
# ใส่ BOT_TOKEN
python app.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Deploy

```bash
git push origin main
```

Render จะ deploy อัตโนมัติจาก repo นี้

**Not CHERRY BOT V3** — ใช้ BOT_TOKEN แยก ไม่เชื่อม Google Sheet

---

## แยกจากบอทแปลภาษา (Staff AI)

| บอท | Repo | Render | ใช้ที่ไหน |
|-----|------|--------|-----------|
| **FAQ (ตัวนี้)** | CHERRY-SUPPORT-AI | `cherry-support-ai` | แชทส่วนตัว — เมนู FAQ |
| **Staff AI แปลภาษา** | CHERRY-STAFF-AI | `cherry-staff-ai` | กลุ่ม staff เท่านั้น |

ห้ามใช้ BOT_TOKEN ร่วมกันระหว่างสองบอท
