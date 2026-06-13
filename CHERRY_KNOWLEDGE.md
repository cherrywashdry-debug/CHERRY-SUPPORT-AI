# CHERRY_KNOWLEDGE.md
## CHERRY WASH & DRY POIPET 24HR — Customer AI Knowledge Base

**Source:** V3 locked rules (`PROJECT_MEMORY.md`, `V3_REWARD_RULE_FINAL_LOCK.md`, `app.py` customer copy)  
**Purpose:** Separate customer-support bot (own Render service) — answer FAQs only; no billing/system actions  
**Last synced:** 2026-06-12

---

## Business Information

| Field | Value |
|-------|-------|
| Business Name | CHERRY WASH & DRY POIPET 24HR |
| Location | Poipet |
| Map | https://maps.app.goo.gl/479dbVxTmHu6k7Qx7 |
| Telegram | https://t.me/Cherrywashanddry |
| WhatsApp | +855 97 888 6689 |

**Service types:**
- Self-service laundry (walk-in at shop)
- Wash & Dry service (industrial machines)
- Pickup & Delivery service

**Shop open:** 24 hours daily (walk-in)

**Pickup & delivery service hours:** 09:30 – 00:00 (local time, UTC+7)  
Orders placed between 00:00–09:29 are queued; staff start pickups from 09:30.

**Supported languages:** Thai, English, Khmer, Indonesian, Chinese

---

## Laundry Packages (Locked V3 Pricing)

Pricing is **per machine package only** — not per kg, not per piece, not by clothing quantity.

Approximation: **1 CHERRY laundry basket ≈ 1 small (14 kg) machine load**

### 14 kg Standard Package — 210 Baht

Includes:
- Wash & Dry
- Detergent
- Softener

Reward points: **0 points**

### 14 kg Premium Package — 240 Baht

Includes:
- Wash & Dry
- Premium Detergent
- Premium Softener

Reward points: **+1 point per machine**

### 18 kg Package — 270 Baht

Includes:
- Large machine (18 kg)
- Wash & Dry
- Detergent
- Softener

Reward points: **+1 point per machine**

### 18 kg Package + Extra Dry — 300 Baht

Includes:
- Large machine (18 kg)
- Wash & Dry
- Detergent
- Softener
- Extra Dry 30 minutes

Reward points: **+1 point per machine**

### Included in all packages (customer-facing)

- Premium laundry detergent
- Premium fabric softener
- Folding & packing
- Premium fabric spray
- Home pickup & delivery available (fee by distance — see below)

---

## Pricing Rules

The shop charges by **machine package only**.

The shop does **NOT** charge:
- By clothing quantity
- By piece
- By actual weight (kg)

Delivery fee and other fees are **separate line items** on the invoice — they are **not** part of package pricing and do **not** earn reward points.

---

## Delivery Fee (Pickup & Deliver Back)

Distance is measured from the shop to the customer location.

| Distance | Fee |
|----------|-----|
| Less than 1 km | **Free** |
| 1 km up to 2.5 km | **10 Baht** |
| More than 2.5 km up to 3 km | **20 Baht** |
| More than 3 km up to 4 km | **50 Baht** |
| More than 4 km | **70 Baht** |

If distance cannot be calculated automatically, staff will confirm the fee.

Walk-in invoices: staff may add a custom delivery fee amount.  
Pickup orders (Order ID): delivery fee comes from the order — staff cannot override it on the bill.

---

## Pickup & Delivery Service

**How to order pickup:**
1. Use the CHERRY bot menu → Express Pickup
2. Provide location (GPS pin or address)
3. Provide home photo and laundry bag photo when requested
4. Choose payment method (cash or bank transfer after invoice)
5. Staff arrange pickup and delivery

**Customer should provide:**
- Location
- Laundry bag photo (when requested)
- Home photo (when requested; saved location may skip repeat home photo)

**Payment before service** — pay after staff check items and issue invoice, or cash at pickup.

---

## Estimated Ready Time

**Pickup & delivery orders:** approximately **3–4 hours** after:
- Laundry is collected
- Staff have checked items
- Invoice is issued

**Walk-in (customer brings to shop):** approximately **2–3 hours** after staff check and issue invoice.

**Orders collected after 20:00:** shop tries same-night delivery if workload allows; otherwise next day from 09:30.

Times are **estimates** — may vary by volume, weather, power outages, and daily order load.

**My Order / ready status (in main bot):** customer sees "processing" until **3 hours** after invoice time, then "ready for pickup/delivery".

---

## Payment Methods

- **Cash** — pay staff at pickup, or leave in laundry bag
- **Bank transfer after invoice** — staff send invoice and total after checking items

Accepted transfer channels: **ABA • ACLEDA • INDO BANK • THAI BANK**

Rule: **Pay before service** (after invoice is issued for transfer customers).

---

## Membership & Rewards (Locked V3)

### How points are earned

Points are calculated **per eligible package line** — not by invoice total.

| Package | Points per machine |
|---------|-------------------|
| 14 kg (210 Baht) | **0** |
| 14 kg (240 Baht) | **+1** |
| 18 kg (270 Baht) | **+1** |
| 18 kg (300 Baht) | **+1** |

**Never earn points from:**
- Delivery fee
- Other fees
- Invoice total amount
- 210 Baht tier — even if total bill exceeds 240 Baht

**Example:** 14 kg (210) × 2 + 70 B delivery = **0 points** (not 1).

**When points apply:**

| Order type | Requirement |
|------------|-------------|
| Walk-in (at shop) | Valid Member ID (`CWD-xxx`) — **no `/start` required** for points at store billing |
| Pickup (Order ID) | Customer must press **`/start`** on the bot (`BOT_STARTED=YES`) |

To check points anytime: use **🎁 Rewards / Member** menu in the main CHERRY bot.

### Redemption cycle

| Rule | Value |
|------|-------|
| Target | **13 points** |
| Reward | **200 Baht laundry credit** |
| When credit applies | On the **NEXT laundry invoice after** reaching 13/13 — **not** on the invoice that completes 13 points |
| After redemption | New cycle starts at **1/13** (not 0/13); credit is auto-applied on the redeem invoice |

---

## Shop Policies

### Services NOT provided

- Ironing service
- Shoe washing service

### Before washing — customer must inform staff if laundry contains

- Delicate items
- Luxury / designer items
- Expensive items
- Special care items

### Small & delicate items

Underwear, socks, children's clothes, fabric masks, and other small items should be placed in a **laundry bag** before sending.  
Shop is not responsible for lost or damaged small items if no laundry bag was used.

---

## Liability Policy

The shop is **not responsible** for:

- Old stains
- Deep or mold stains that cannot be fully removed
- Color fading
- Color bleeding (especially dark, new, or denim fabrics)
- Shrinkage
- Worn fabric damage
- Tears, stretching, or further damage on old or pre-damaged garments
- Zippers, buttons, decorations
- Pre-existing damage
- Lost cash, documents, or valuables left in laundry

---

## Missing Item Policy

Missing item reports must be submitted **within 3 days** after receiving laundry.

Supporting evidence is recommended:
- Invoice
- Photos
- Videos

---

## Order & Invoice IDs (for customer reference)

| ID | Format | Used for |
|----|--------|----------|
| Member ID | `CWD-xxx` | Membership, walk-in billing |
| Order ID | `CR-xxxx` | Pickup/delivery job tracking |
| Invoice ID | `IV-xxxx` | Bill reference |

Walk-in customer bills show Member ID — Order ID is not shown on walk-in customer invoice.  
Pickup orders use Order ID for tracking in the bot.

---

## AI Support Bot — Allowed Actions

The support bot **MAY**:

- Answer package prices
- Answer delivery fee tiers
- Answer shop policies and liability
- Answer reward rules (as documented above)
- Answer pickup/delivery service and hours
- Answer opening hours and estimated ready times
- Answer payment methods
- Provide contact info and map link
- Translate messages
- Draft suggested replies for staff review (if wired to Support Desk)
- Ask customer for Order ID (`CR-xxxx`) or Invoice ID (`IV-xxxx`) when order-specific help is needed

---

## AI Support Bot — Prohibited Actions

The support bot **MUST NOT**:

- Create or modify invoices
- Modify customer information in the system
- Add or remove reward points
- Promise refunds or compensation
- Change prices or invent promotions
- Change reward rules
- Guess order status without Order ID — direct customer to main bot **My Order** or staff
- Guess Telegram identity or send messages as if it were the billing bot
- Access Google Sheets or perform staff-only actions

If unsure, or question needs order lookup / staff decision:

> Thank you for contacting CHERRY Wash & Dry. Our staff will assist you shortly.

Thai fallback:

> ขอบคุณที่ติดต่อ CHERRY Wash & Dry ค่ะ ทีมงานจะช่วยเหลือคุณในไม่ช้า

---

## Common Customer Questions — Quick Answers

**Are you open?**  
Yes — shop is open **24 hours**. Pickup/delivery runs **09:30–00:00**.

**How much for one bag?**  
Depends on machine size: small 14 kg **210–240 B**, large 18 kg **270–300 B** per machine — not by weight.

**I only have a little / sedikit / not much laundry — is it cheaper?**  
No — CHERRY charges **per machine package**, not by clothing amount. Even a small load uses one full machine: minimum **210 B** (14 kg standard). Options: 14 kg 210/240 B, 18 kg 270/300 B.

**Do I get points on 210 Baht package?**  
No — only **240 / 270 / 300** tiers earn **+1 point per machine**.

**Do delivery fees give points?**  
No — points are from eligible packages only.

**When do I get the 200 Baht credit?**  
After reaching **13/13 points**, credit applies on your **next** laundry order — not the order that hit 13.

**Do you iron clothes?**  
No ironing service.

**How long until ready?**  
Walk-in ~2–3 hours; pickup/delivery ~3–4 hours after collection and invoice — estimates only.

**How do I track my order?**  
Use the main `@CherryWashDryPoipetBot` → **My Order** menu, or contact staff with your Order ID.

**I lost an item**  
Report within **3 days** with invoice and photos; staff will investigate.

---

## Relationship to Main V3 Bot

| System | Role |
|--------|------|
| `@CherryWashDryPoipetBot` (V3) | Invoices, rewards, pickup orders, delivery, My Order |
| Separate support bot (planned) | FAQ + policy answers only — read this file |

Do not duplicate billing logic in the support bot. When customer needs invoice, points update, or delivery action → direct them to main bot or staff contact channels above.
