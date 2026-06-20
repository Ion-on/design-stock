# MU — Micron Technology Research Brief

### 1. Company snapshot

Micron Technology เป็นผู้ผลิตชิปความจำ (memory chip) รายใหญ่ของโลก ทำธุรกิจหลักสองกลุ่มคือ DRAM (หน่วยความจำสำหรับประมวลผลชั่วคราว ใช้ในคอมพิวเตอร์ เซิร์ฟเวอร์ และ GPU AI) และ NAND flash (หน่วยความจำสำหรับเก็บข้อมูลถาวร ใช้ใน SSD และอุปกรณ์มือถือ) ลูกค้าหลักคือผู้ผลิตอุปกรณ์อิเล็กทรอนิกส์ (PC, สมาร์ทโฟน, รถยนต์) และผู้ให้บริการ data center/cloud รายใหญ่ที่ซื้อชิปความจำไปประกอบกับเซิร์ฟเวอร์และระบบ AI รายได้ส่วนใหญ่มาจากการขายชิปเป็นสินค้าโภคภัณฑ์ (commodity) ที่ราคาผันผวนตามวงจรอุปสงค์-อุปทานของตลาดโลก โดยช่วงหลังสัดส่วนรายได้จากกลุ่ม data center/HBM (High Bandwidth Memory สำหรับ AI) เพิ่มน้ำหนักขึ้นต่อเนื่อง (ตรวจสอบข้อมูลล่าสุด)

### 2. Fundamentals signal

- รายได้และอัตรากำไรของ Micron เคลื่อนไหวเป็นวงจรชัดเจนตามราคา DRAM/NAND ในตลาดโลก ช่วงที่ supply ล้นตลาดบริษัทอาจขาดทุนระดับ operating margin ติดลบได้ ส่วนช่วงที่ demand ตึงตัว (เช่นรอบ AI/HBM ปัจจุบัน) margin จะดีดตัวขึ้นเร็วมาก — นี่คือธรรมชาติของธุรกิจ ไม่ใช่ความผิดปกติ (ตัวเลข margin ที่แน่นอน ตรวจสอบใน 10-K ล่าสุด)
- Capital intensity สูงมาก เพราะการอัพเกรดเทคโนโลยี node และขยาย fab ต้องใช้ capex หลักหมื่นล้านดอลลาร์ต่อปีต่อเนื่อง ทำให้ free cash flow ในช่วง downcycle อาจติดลบหรือบางหรือต่ำกว่ากำไรทางบัญชีมาก แม้ในช่วง upcycle ก็ตาม (ตัวเลข capex/FCF เป๊ะ ตรวจสอบใน 10-K ล่าสุด)
- Balance sheet มีหนี้ระดับที่ต้องจับตา เพราะบริษัทมักกู้เพิ่มหรือออกตราสารทุนในช่วง downcycle เพื่อพยุง capex และสภาพคล่อง แล้วค่อยลดหนี้คืนตอน upcycle — โครงสร้างนี้ทำให้ leverage ขึ้นๆลงๆ ตามวงจร ไม่ใช่แนวโน้มลดหนี้แบบบริษัทที่โตสม่ำเสมอ (ตัวเลข net debt/leverage ตรวจสอบใน 10-K ล่าสุด)
- Capital allocation เน้นนำเงินกลับไปลงทุนขยายกำลังผลิตและ R&D เพื่อรักษาความสามารถในการแข่งขันด้าน process node เป็นหลัก ส่วนการคืนเงินผู้ถือหุ้น (buyback/dividend) มีแต่ในระดับที่ค่อนข้างจำกัดเทียบกับขนาดบริษัท เพราะเงินสดส่วนใหญ่ถูกผูกไว้กับวงจร capex
- ความได้เปรียบเชิงโครงสร้างของ Micron มาจาก Scale Economies เป็นหลัก — การผลิตชิปความจำต้องใช้ fab ขนาดใหญ่และเงินทุนมหาศาล ทำให้เหลือผู้เล่นไม่กี่รายในตลาดโลก (หลักๆ คือ Samsung, SK Hynix, Micron) และมี Process Power ระดับหนึ่งจากการสะสมความรู้ในการลด node size และเพิ่ม yield การผลิต แต่ไม่ใช่ Switching Costs หรือ Branding ที่แข็งแรงนัก เพราะ DRAM/NAND ส่วนใหญ่ยังเป็นสินค้าที่แทนกันได้ในตลาด (commodity-like) ยกเว้นในกลุ่ม HBM ที่เริ่มมี Cornered Resource บางส่วนจากความสัมพันธ์กับลูกค้า AI รายใหญ่

### 3. Latest earnings

ไม่มีไฟล์ earnings transcript สำหรับ MU อยู่ใน `sources/MU/` (โฟลเดอร์นี้ยังไม่ถูกสร้าง) ดังนั้นจึงไม่สามารถสรุปผลประกอบการล่าสุดได้ในตอนนี้ — ขอข้ามส่วนนี้ไปก่อน เพื่อป้องกันการหยิบตัวเลขจากความจำซึ่งอาจผิดพลาดหรือล้าสมัย และไม่สามารถตรวจสอบย้อนกลับ (traceability) ไปยังแหล่งข้อมูลจริงได้

หากต้องการให้ทำ section นี้ กรุณาเพิ่มไฟล์ earnings transcript หรือเอกสารที่เกี่ยวข้องไว้ที่ `sources/MU/` ก่อน แล้วค่อยรันใหม่

### 4. Bull case / Bear case

**Bull case**
- HBM (High Bandwidth Memory) เป็น key driver ใหม่ที่มี margin สูงกว่า DRAM ทั่วไปมาก และ Micron มีสถานะเป็นหนึ่งในผู้เล่นหลักที่ qualify เข้า supply chain ของ AI accelerator ทำให้ได้รับประโยชน์โดยตรงจาก capex ของ hyperscaler และ GPU maker ที่ลงทุนด้าน AI infrastructure ต่อเนื่อง
- วงจรราคา DRAM/NAND กำลังอยู่ในช่วง upcycle จาก supply discipline ของผู้ผลิตทั้งอุตสาหกรรม (ลด capex, เลื่อนโรงงานใหม่) บวกกับ demand จาก AI server และ data center ที่ต้องการ memory content ต่อเครื่องสูงขึ้นมาก เทียบกับ server ทั่วไป
- โครงสร้างอุตสาหกรรม DRAM เป็น oligopoly ที่เหลือผู้เล่นหลักไม่กี่ราย (Samsung, SK Hynix, Micron) ทำให้ rational pricing behavior ง่ายกว่าตลาด fragmented และ Micron มีพันธมิตรเชิงนโยบายกับรัฐบาลสหรัฐฯ (CHIPS Act funding) ที่ช่วยหนุน capacity expansion ในประเทศ

**Bear case**
- DRAM/NAND เป็น commodity cycle ที่ผันผวนรุนแรงและคาดเดายาก ประวัติศาสตร์ของ Micron เต็มไปด้วยช่วง oversupply ที่ราคาตกฮวบและบริษัทขาดทุนหนัก หาก hyperscaler ชะลอ capex หรือ AI demand ไม่โตตามคาด อุตสาหกรรมอาจกลับเข้าสู่ oversupply cycle ได้เร็วกว่าที่ตลาดคาด
- คู่แข่งจีน (CXMT ด้าน DRAM, YMTC ด้าน NAND) กำลังเร่ง ramp capacity และไล่ตาม technology node ด้วยการสนับสนุนจากรัฐบาลจีนอย่างหนัก ซึ่งในระยะยาวอาจกดราคาตลาดโลกและกัดกร่อน market share ของ Micron โดยเฉพาะใน legacy node ที่ margin ต่ำอยู่แล้ว
- ธุรกิจเป็น capex-intensive สูงมาก (หลายหมื่นล้านดอลลาร์ต่อปีสำหรับ fab ใหม่และ HBM capacity) ทำให้ free cash flow ผันผวนตามวงจรราคา และมี customer concentration risk สูงในกลุ่ม HBM เพราะพึ่งพา hyperscaler/GPU maker จำนวนน้อยรายเป็นสัดส่วนใหญ่ของ revenue growth ใหม่

### 5. Kill conditions

- ถ้าเห็น DRAM/NAND ASP (average selling price) ปรับตัวลงต่อเนื่อง 2-3 quarter ติดพร้อม gross margin หดตัวแรงกว่าที่ guidance บอกไว้ — สัญญาณว่าวงจร upcycle จบเร็วกว่าคาดและกำลังเข้าสู่ oversupply
- ถ้า Micron เสีย hyperscaler หรือ GPU maker รายใหญ่ในกลุ่ม HBM customer ไป (เช่น ลูกค้าเปลี่ยนไปใช้ Samsung/SK Hynix เป็นหลัก หรือสัญญา design-win รอบใหม่หลุดมือ) — เพราะ HBM คือ growth driver หลักของ thesis นี้
- ถ้ามีหลักฐานชัดว่า CXMT หรือผู้ผลิตจีนสามารถผลิต DRAM node ที่ทันสมัย (เช่น 1-beta หรือต่ำกว่า) ได้ในปริมาณมากและเริ่มขายตัดราคาในตลาดโลก หรือสหรัฐฯ/พันธมิตรผ่อนคลาย export control จนจีนเข้าถึง equipment ได้ง่ายขึ้น — เพราะกระทบ pricing power และ TAM ระยะยาวของ Micron โดยตรง

### 6. What to ask before owning it

- ผมเข้าใจตำแหน่งของ Micron ใน DRAM/NAND cycle ตอนนี้หรือยังว่าอยู่ช่วง upcycle หรือใกล้ peak แล้ว และผมรับความผันผวนของราคาหุ้นช่วง downcycle ได้จริงหรือไม่
- สัดส่วนรายได้จาก HBM ของ Micron เทียบกับ DRAM/NAND ทั่วไปเป็นอย่างไร และ customer concentration ในกลุ่ม HBM กระจุกตัวอยู่กับลูกค้ารายไหนบ้าง
- แผน capex และ capacity expansion ของ Micron ในช่วง 1-2 ปีข้างหน้าเป็นอย่างไร และบริษัทมีกระแสเงินสดเพียงพอรองรับโดยไม่ต้องเพิ่มหนี้หรือ dilute ผู้ถือหุ้นมากแค่ไหน
- ความคืบหน้าของคู่แข่งจีน (CXMT, YMTC) ในการไล่ตาม technology node ตอนนี้อยู่ระดับไหน และมีความเสี่ยงด้าน export control หรือ geopolitics ที่กระทบ supply chain ของ Micron บ้างหรือไม่
- ผมตั้งใจถือ Micron ในกรอบเวลาสั้น (1-3 วัน ตามสไตล์การลงทุนของผม) หรือยาวกว่านั้น และจุดที่ผมจะยอมรับว่า thesis ผิดคืออะไรกันแน่
