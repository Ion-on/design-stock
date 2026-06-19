---
name: company-brief
description: Use when the user asks for a research brief on a public stock (e.g. "/brief AAPL", "ทำ brief NVDA ให้หน่อย", "research TSLA"). Outputs a 6-section markdown brief saved to briefs/<TICKER>.md.
---

# company-brief SOP

## When to use this

ผู้ใช้ขอ research brief ของหุ้น 1 ตัว Trigger ทั่วไป:
- `/brief <TICKER>` slash command
- "ทำ brief หุ้น X ให้หน่อย"
- "ขอข้อมูลย่อๆ ของ <ticker>"

## Inputs you need

- 1 stock ticker (เช่น AAPL, NVDA, GOOGL)
- ถ้าไม่มี ticker ให้ ask before doing anything else

## Steps
1. Confirm the ticker. ถ้า ambiguous ให้ถาม user ก่อน
2. Read `CLAUDE.md` เพื่อดึงสไตล์การลงทุนและน้ำเสียง (Voice) ของ user มาใช้ครอบคลุมทุก Sub-agent
3. แตกงานออกเป็น 3 Sub-agents ให้ทำงานขนานกันในบริบท (Context) ของตัวเอง:
   - **Sub-agent A (Fundamentalist):** วิเคราะห์ข้อ 1 (Snapshot) และข้อ 2 (Fundamentals) เจาะลึกโครงสร้างธุรกิจและความได้เปรียบ
   - **Sub-agent B (Earnings Tracker):** อ่านไฟล์ทั้งหมดใน sources/<TICKER>/ เพื่อสรุปข้อ 3 (Latest earnings) โดยระบุแหล่งที่มา (Traceability) อย่างเคร่งครัดตามกฎเดิม
   - **Sub-agent C (Risk Analyst):** วิเคราะห์ข้อ 4 (Bull/Bear), ข้อ 5 (Kill conditions) และข้อ 6 (What to ask) โดยเน้นความเสี่ยงเชิงโครงสร้างตามสไตล์ของ user
4. นำผลลัพธ์จาก Sub-agent A, B และ C มารวบรวมและเกลาภาษา (Synthesize) ให้กลมกลืนกันตามสไตล์ที่กำหนดใน CLAUDE.md
5. บันทึกไฟล์ไปที่ briefs/<TICKER>.md และแสดงผลใน chat

## Output format (6 sections, required, no skipping)

ใช้ markdown headings ทั้ง 6 section ต้องมี ครบทุก brief

### 1. Company snapshot (3-4 ประโยคไทย)
บริษัททำอะไร, ขายให้ใคร, รายได้หลักมาจากไหน ภาษาคนปกติ ไม่เอาคำตลาด

### 2. Fundamentals signal (3-5 bullets)
Revenue trend, margin trend, balance sheet feel, capital allocation pattern **เน้น direction มากกว่าตัวเลข** เพราะตัวเลขเฉพาะอาจเก่า ถ้า ratio/margin specific ที่ไม่แน่ใจ ให้ใส่ "(ตัวเลข ตรวจสอบใน 10-K ล่าสุด)" ต่อท้าย

### 3. Latest earnings
3-5 bullets **Source:** อ่านทุกไฟล์ใน sources/<TICKER>/ ก่อนเขียน ถ้า folder ว่างหรือไม่มี เขียนตรงๆ: "ไม่มี earnings transcript ใน sources/<TICKER>/ skip section นี้หรือ user ใส่ source ก่อน" ห้ามแต่งตัวเลขจากความจำ ทุก bullet ในนี้ต้อง trace กลับไปที่ไฟล์ใน sources/ ได้ และระบุไฟล์ต้นทางใน parens ท้าย bullet เช่น (source: sources/AAPL/q1-2026-call.md) หรือถ้าเป็น Placeholder ให้ระบุตรงๆ ว่าเป็น Placeholder ไม่มีข้อมูลจริง

### 4. Bull case / Bear case
2-3 bullets แต่ละข้าง Bear case ต้อง substantive ไม่ใช่ "เศรษฐกิจไม่ดี" ต้องเป็นเหตุผลที่ specific to บริษัทนี้

### 5. Kill conditions (สำคัญ อย่าข้าม)
2-3 bullets "ถ้าเห็นอะไรเกิดขึ้น ผม/คุณควรเลิกถือ" ตัวอย่าง: "margin ลดลง 3 quarter ติด", "ลูกค้า top-3 หายไป 1 ราย", "CEO ออก + replacement weak" Kill conditions เป็นข้อเดียวที่กันให้ thesis ไม่กลายเป็น religion

### 6. What to ask before owning it (3-5 questions)
คำถามที่ beginner ควรตอบให้ได้ก่อนกดซื้อ ไม่ใช่คำตอบ เป็น question prompt

## Voice rules

- Tone reflect investing voice ใน `CLAUDE.md` ของ project ถ้า CLAUDE.md บอก "long-term focus" ห้าม brief เน้น short-term trading angle
- **ห้าม** ออก buy/sell recommendation นี่คือ research summary ไม่ใช่คำแนะนำ
- **ห้าม** แต่ง verbatim quote ของ executive ใส่ blockquote ถ้าจะอ้างคำผู้บริหาร ใช้ indirect speech ("CEO กรอบ message ว่า...") ห้ามใส่ `>` quote ที่ verify ไม่ได้
- **ห้าม** ใช้คำว่า "moat" ตรงๆ ใช้ Helmer's 7 Powers ที่ specific (Scale Economies, Network Economies, Switching Costs, Branding, Counter-Positioning, Cornered Resource, Process Power) ถ้าจะพูดเรื่องความได้เปรียบ
- **ห้าม** บอกว่า "ตลาดยังไม่ price in" หรือทำนายว่านักลงทุนคนอื่นคิดอะไร

## When unsure

Honest > confident ถ้าข้อมูลไม่พอ พูดว่า "ผมไม่แน่ใจ ลองดูใน [source ที่ user ใช้]" ดีกว่าแต่ง
