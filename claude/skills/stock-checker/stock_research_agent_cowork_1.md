# 📊 Stock Research Agent — Claude Cowork Setup Guide

> คู่มือตั้งค่า Agent วิเคราะห์หุ้นใน Claude Cowork  
> สำหรับนักลงทุนและนักวิเคราะห์ที่ต้องการ Research อัตโนมัติ

---

## ⚙️ ความต้องการระบบ

| รายการ | รายละเอียด |
|--------|-----------|
| แอป | Claude Desktop (macOS หรือ Windows) |
| แผน | Pro / Max / Team / Enterprise |
| อินเทอร์เน็ต | จำเป็นตลอดการทำงาน |
| Web Search | เปิดใช้งาน (ค่าเริ่มต้น) |

---

## 🚀 วิธีตั้งค่า Agent

### ขั้นตอนที่ 1 — ตั้ง Global Instructions (ทำครั้งเดียว)

เปิด Claude Desktop → **Settings → Cowork → Global Instructions → Edit**

วางข้อความนี้:

```
คุณคือ Stock Research Analyst ผู้เชี่ยวชาญด้านการวิเคราะห์หุ้นสหรัฐ ไทย และตลาดโลก

สไตล์การวิเคราะห์:
- ใช้ทั้ง Technical Analysis (TA) และ Fundamental Analysis (FA)
- อ้างอิง Macro Theme เสมอ (Fed Policy, เศรษฐกิจโลก, Sector Rotation)
- ระบุ Support/Resistance และ Price Target ที่ชัดเจน
- ประเมิน Risk/Reward Ratio ทุกครั้ง
- สรุปเป็น Bullet Point อ่านง่าย

รูปแบบ Output:
- บันทึกไฟล์เป็น Markdown (.md) ที่โฟลเดอร์ /StockResearch/
- สร้าง HTML Dashboard เมื่อต้องการ Visualize ข้อมูล
- ใช้ภาษาไทยเป็นหลัก ยกเว้นคำศัพท์เทคนิคที่เป็น English

คำเตือน:
- ระบุ Disclaimer การลงทุนทุกรายงาน
- ไม่แนะนำให้ซื้อ/ขายโดยตรง — แสดงข้อมูลเพื่อการตัดสินใจเท่านั้น
```

---

### ขั้นตอนที่ 2 — สร้าง Project สำหรับ Stock Research

1. เปิด Cowork Tab → คลิก **New Project**
2. ตั้งชื่อ: `📈 Stock Research Hub`
3. เพิ่ม Project Instructions:

```
Project: Stock Research Hub
โฟลเดอร์ทำงาน: /StockResearch/

โครงสร้างโฟลเดอร์:
- /StockResearch/Reports/        ← รายงานวิเคราะห์รายหุ้น
- /StockResearch/Watchlist/      ← Watchlist และ Tracking
- /StockResearch/Screener/       ← ผลการ Screen หุ้น
- /StockResearch/Macro/          ← วิเคราะห์ภาพรวมตลาด
- /StockResearch/Dashboards/     ← HTML Dashboards

ก่อนเริ่มงานทุกครั้ง ให้ค้นหาข้อมูลล่าสุดจากอินเทอร์เน็ตก่อนเสมอ
```

---

## 📋 Prompt Templates พร้อมใช้

### 🔍 Template 1: วิเคราะห์หุ้นรายตัว (Deep Dive)

```
วิเคราะห์หุ้น [TICKER] อย่างละเอียด โดย:

1. FUNDAMENTAL ANALYSIS
   - Revenue Growth YoY / QoQ (3 ปีล่าสุด)
   - Gross Margin, Operating Margin, Net Margin
   - P/E, P/S, EV/EBITDA เทียบ Sector Average
   - Free Cash Flow และ Debt/Equity
   - Analyst Consensus และ Price Target
   
2. TECHNICAL ANALYSIS (Daily + Weekly Chart)
   - Trend Direction (EMA 20/50/200)
   - RSI, MACD Signal
   - Support: S1, S2, S3
   - Resistance: R1, R2, R3
   - Volume Pattern

3. CATALYST & RISK
   - Upcoming Earnings Date
   - Key Catalysts ที่จะ Drive ราคา
   - Major Risks / Headwinds
   
4. MACRO THEME
   - หุ้นนี้เกี่ยวข้องกับ Theme อะไร
   - Fed Policy ส่งผลอย่างไร
   
5. สรุป: Bull Case / Base Case / Bear Case พร้อม Price Target แต่ละ Scenario

บันทึกรายงานเป็น: /StockResearch/Reports/[TICKER]_[วันที่].md
สร้าง HTML Dashboard ที่: /StockResearch/Dashboards/[TICKER]_dashboard.html
```

---

### 📰 Template 2: Market Morning Briefing (ตั้งเวลาทุกเช้า)

```
สร้าง Morning Market Briefing สำหรับวันนี้ โดย:

1. OVERNIGHT MARKET
   - Futures (S&P500, Nasdaq, DOW)
   - ตลาดเอเชีย (Nikkei, HSI, SET50)
   - Dollar Index (DXY), VIX
   
2. KEY NEWS TODAY
   - ข่าวสำคัญที่กระทบตลาด (ค้นหาล่าสุด)
   - Economic Data ที่จะประกาศวันนี้
   - Earnings Releases วันนี้

3. SECTOR ROTATION
   - Sector ไหนแข็งแกร่ง / อ่อนแอ
   - Money Flow วันนี้

4. WATCHLIST UPDATE
   - อ่านไฟล์ /StockResearch/Watchlist/my_watchlist.md
   - อัปเดตราคาและ Signal ล่าสุดของแต่ละตัว

5. TRADING IDEA ประจำวัน
   - 2-3 หุ้นที่น่าสนใจวันนี้พร้อมเหตุผล

บันทึก: /StockResearch/Macro/briefing_[วันที่].md
```

---

### 🔎 Template 3: Sector Screener

```
Screen หุ้นใน Sector [ชื่อ Sector เช่น AI, Space, Energy, Biotech] โดย:

เกณฑ์การ Screen:
- Market Cap: [ระบุ เช่น >$1B]
- Revenue Growth > [ระบุ เช่น 20%] YoY
- Gross Margin > [ระบุ เช่น 40%]
- RSI ไม่ Overbought (< 75)
- Price > EMA 50

ขั้นตอน:
1. ค้นหาหุ้น Top ใน Sector นี้
2. วิเคราะห์แต่ละตัวตามเกณฑ์ข้างต้น
3. จัดอันดับตาม Risk/Reward
4. สรุปตารางเปรียบเทียบ

บันทึก: /StockResearch/Screener/[Sector]_screen_[วันที่].md
```

---

### 📊 Template 4: Earnings Preview & Review

```
วิเคราะห์ Earnings ของ [TICKER] โดย:

PRE-EARNINGS (ก่อนประกาศ):
- EPS Estimate vs. Last Quarter
- Revenue Estimate
- Analyst Expectations
- Implied Move จาก Options Market (IV)
- Historical Earnings Reaction (5 Quarter ล่าสุด)
- Key Metrics ที่ต้องดู

POST-EARNINGS (หลังประกาศ):
- Actual vs. Estimate (EPS และ Revenue)
- Guidance ที่ Management ให้
- Key Highlights จาก Earnings Call
- ราคาหุ้น Reaction
- การปรับ Price Target ของ Analyst

บันทึก: /StockResearch/Reports/[TICKER]_earnings_[Quarter].md
```

---

### 🌐 Template 5: Macro & Fed Analysis

```
วิเคราะห์ภาพรวม Macro เดือน[ระบุเดือน] โดย:

1. FED POLICY
   - อัตราดอกเบี้ยปัจจุบันและทิศทาง
   - Fed Dot Plot และ Market Expectation
   - Timeline การปรับอัตราดอกเบี้ย

2. ECONOMIC DATA
   - GDP Growth
   - CPI / PCE Inflation
   - Jobs Report (NFP, Unemployment)
   - PMI Manufacturing & Services

3. ผลกระทบต่อ Asset Classes
   - หุ้น Growth vs. Value
   - Gold, Bitcoin
   - Bond Yields

4. GEOPOLITICAL RISK
   - ความเสี่ยงที่กระทบตลาด

5. สรุป Playbook: ควร Overweight Sector ไหน

บันทึก: /StockResearch/Macro/macro_[เดือน]_[ปี].md
```

---

### ⏰ Template 6: Scheduled Weekly Report (ตั้งเวลาทุกวันอาทิตย์)

```
สร้าง Weekly Portfolio Review ประจำสัปดาห์ โดย:

1. MARKET PERFORMANCE THIS WEEK
   - ผลตอบแทน S&P500, Nasdaq, SET
   - หุ้นขึ้น/ลงมากที่สุดใน Watchlist

2. TECHNICAL SETUP NEXT WEEK
   - หุ้นที่ Setup น่าสนใจสำหรับสัปดาห์หน้า
   - Key Level ที่ต้องจับตา

3. UPCOMING CATALYSTS NEXT WEEK
   - Earnings releases
   - Economic data
   - Fed speeches

4. PORTFOLIO HEAT MAP
   - สรุปสถานะแต่ละตัวใน Watchlist
   - สัญญาณ Buy/Hold/Watch

อ่านไฟล์ใน /StockResearch/Watchlist/ เพื่อดู Watchlist ปัจจุบัน
บันทึก: /StockResearch/Reports/weekly_review_[วันที่].md
สร้าง HTML Summary: /StockResearch/Dashboards/weekly_heatmap.html
```

---

## 📁 วิธีตั้งค่า Scheduled Tasks

### ตั้งเวลา Morning Briefing (ทุกวันจันทร์-ศุกร์ 7:00 น.)

1. เปิด Cowork → New Task
2. วาง Template 2 (Morning Briefing)
3. คลิก **Schedule** → เลือก **Daily (Weekdays)** → เวลา 7:00 AM
4. บันทึก Task

### ตั้งเวลา Weekly Review (ทุกวันอาทิตย์ 20:00 น.)

1. เปิด Cowork → New Task
2. วาง Template 6 (Weekly Review)  
3. คลิก **Schedule** → เลือก **Weekly (Sunday)** → เวลา 8:00 PM
4. บันทึก Task

---

## 💡 Tips & Best Practices

### ✅ ทำให้ได้ผลดีที่สุด

- **ระบุ Ticker ให้ชัดเจน** เช่น `NVDA (NASDAQ)`, `PTT (SET)`, `RKLB (NYSE)`
- **ให้ Context เพิ่ม** เช่น "วิเคราะห์เพื่อ Swing Trade 2-4 สัปดาห์"
- **อ้างอิงไฟล์เก่า** เช่น "เปรียบเทียบกับรายงานเดือนที่แล้วใน /StockResearch/Reports/"
- **ขอ Multiple Outputs** เช่น ทั้ง .md และ .html ในครั้งเดียว

### ⚡ Batch Tasks ที่แนะนำ

```
วิเคราะห์หุ้น 5 ตัวในพอร์ตของฉันพร้อมกัน: NVDA, TSLA, RKLB, ASTS, GOOGL
สร้างรายงานแยกไฟล์สำหรับแต่ละตัว และสร้าง Comparison Dashboard รวม
บันทึกทั้งหมดไว้ใน /StockResearch/
```

---

## ⚠️ Disclaimer

> รายงานและการวิเคราะห์ที่สร้างโดย Agent นี้เป็นเพียงข้อมูลเพื่อการศึกษาและประกอบการตัดสินใจ ไม่ใช่คำแนะนำการลงทุน การลงทุนมีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลอย่างรอบคอบและรับผิดชอบการตัดสินใจด้วยตนเอง

---

*สร้างโดย Claude | อัปเดต: มิถุนายน 2026*
