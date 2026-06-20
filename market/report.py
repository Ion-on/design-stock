"""
market/report.py
Renders market/summary_<DATE>.md — a Thai-language daily market-condition
report combining quantitative factors (indices, gold, ^TNX, Fed Funds Rate)
with hand-supplied qualitative factors and a 1-3 day directional outlook.

Re-run behavior: overwrites market/summary_<DATE>.md if run again the same
day (no timestamped variants), matching the briefs/<TICKER>.md convention.

Read-only research tooling. No order execution, no broker integration, no
scheduled/unattended automation, no live streaming.
"""

import os
from datetime import datetime

DIRECTION_EMOJI = {'bullish': '🟢', 'bearish': '🔴', 'neutral': '🟡'}
OUTLOOK_EMOJI = {'UP': '🟢 UP', 'DOWN': '🔴 DOWN', 'SIDEWAYS': '🟡 SIDEWAYS'}


def _fmt_factor_line(f):
    emoji = DIRECTION_EMOJI.get(f.get('direction'), '⚪')
    return f"- {emoji} **{f['factor']}**: {f['detail']}"


def render_report(market_data, factors, outlook, manual_factors=None, report_date=None):
    """
    market_data: dict from data.fetch_market_data()
    factors: list from factors.calculate_all_factors()
    outlook: dict from forecast.build_outlook()
    manual_factors: list[str] as originally passed in (for the report header/context)
    report_date: datetime.date, defaults to today
    """
    report_date = report_date or datetime.now().date()
    date_str = report_date.strftime('%Y-%m-%d')

    fed = market_data['fed_funds']
    indices = market_data['indices']

    lines = []
    lines.append(f"# สรุปภาวะตลาดรายวัน — {date_str}")
    lines.append("")
    lines.append("กลยุทธ์อ้างอิง: ถือระยะสั้น 1-3 วัน เน้นหุ้นพลังงาน อวกาศ และเทคโนโลยี")
    lines.append("")

    # 1. Snapshot table
    lines.append("## 1. Snapshot ตลาด")
    lines.append("")
    lines.append("| สินทรัพย์ | ราคาล่าสุด | เปลี่ยนแปลง (1 วัน) |")
    lines.append("|---|---|---|")
    for ticker, info in indices.items():
        df = info.get('data')
        label = info.get('label', ticker)
        if df is None:
            lines.append(f"| {label} | N/A | ดึงข้อมูลไม่ได้: {info.get('error')} |")
            continue
        last = df['Close'].iloc[-1]
        if len(df) > 1:
            prev = df['Close'].iloc[-2]
            chg = ((last / prev) - 1) * 100
            chg_str = f"{chg:+.2f}%"
        else:
            chg_str = "N/A"
        unit = '%' if ticker == '^TNX' else ''
        lines.append(f"| {label} | {last:,.2f}{unit} | {chg_str} |")

    if fed.get('error'):
        lines.append(f"| Fed Funds Rate (FRED DFF) | N/A | ดึงข้อมูลไม่ได้: {fed['error']} |")
    else:
        lines.append(f"| Fed Funds Rate (FRED DFF, {fed['latest_date']}) | {fed['latest_rate']:.2f}% | {fed['change']:+.2f} จุด |")
    lines.append("")

    # 2. Factors
    lines.append("## 2. ปัจจัยที่ขับเคลื่อนตลาดวันนี้")
    lines.append("")
    quant_factors = [f for f in factors if f.get('tag') != 'qualitative']
    qual_factors = [f for f in factors if f.get('tag') == 'qualitative']

    lines.append("### ปัจจัยเชิงปริมาณ (Quantitative)")
    lines.append("")
    for f in quant_factors:
        lines.append(_fmt_factor_line(f))
    lines.append("")

    lines.append("### ปัจจัยเชิงคุณภาพ (Qualitative — ป้อนด้วยมือ)")
    lines.append("")
    if qual_factors:
        for f in qual_factors:
            lines.append(f"- {f['detail']}")
    else:
        lines.append("_ไม่มีการป้อนปัจจัยเชิงคุณภาพสำหรับรายงานนี้ (manual_factors ว่างเปล่า) — ควรให้ Claude ค้นข่าวล่าสุด (geopolitics, IPO, earnings shock) แล้วป้อนก่อนใช้ตัดสินใจจริง_")
    lines.append("")

    # 3. Outlook
    lines.append("## 3. ทิศทางตลาด 1-3 วันข้างหน้า")
    lines.append("")
    bm = outlook['broad_market']
    lines.append(f"**ตลาดกว้าง (Broad market):** {OUTLOOK_EMOJI.get(bm['direction'], bm['direction'])} "
                 f"(ความเชื่อมั่น: {bm['confidence']}, คะแนนรวม {bm['score']:+d} จาก {bm['factor_count']} ปัจจัย)")
    lines.append("")
    lines.append("**Sector exposure (พลังงาน / อวกาศ / เทคโนโลยี):**")
    lines.append("")
    lines.append("| Sector | ทิศทาง | ความเชื่อมั่น | คะแนน | จำนวนปัจจัย |")
    lines.append("|---|---|---|---|---|")
    for tag, s in outlook['sectors'].items():
        lines.append(f"| {s['sector_name_th']} ({tag}) | {OUTLOOK_EMOJI.get(s['direction'], s['direction'])} | "
                     f"{s['confidence']} | {s['score']:+d} | {s['factor_count']} |")
    lines.append("")

    # 4. Assumptions / kill conditions (per CLAUDE.md discipline)
    lines.append("## 4. ข้อสมมติฐานหลัก (Assumptions)")
    lines.append("")
    for a in outlook['assumptions']:
        lines.append(f"- {a}")
    lines.append("")

    lines.append("## 5. Kill conditions (เงื่อนไขที่ทำให้รายงานนี้ใช้ไม่ได้)")
    lines.append("")
    for k in outlook['kill_conditions']:
        lines.append(f"- {k}")
    lines.append("")

    lines.append("---")
    lines.append(f"*สร้างเมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                 f"ข้อมูลเชิงปริมาณจาก yfinance (ดัชนี/ETF/ทองคำ/^TNX) และ FRED (Fed Funds Rate, series DFF, no-key endpoint). "
                 f"รายงานนี้เป็นเครื่องมือวิจัยอย่างเดียว ไม่มีการส่งคำสั่งซื้อขายอัตโนมัติ ไม่เชื่อมต่อ broker "
                 f"และไม่มีการรันซ้ำแบบ scheduled — รันตามคำขอเท่านั้น*")

    return "\n".join(lines)


def save_report(content, report_date=None, out_dir=None):
    """
    Save the rendered report to market/summary_<DATE>.md, overwriting if it
    already exists for the same date (matches briefs/<TICKER>.md convention:
    no timestamped variants).
    """
    report_date = report_date or datetime.now().date()
    date_str = report_date.strftime('%Y-%m-%d')

    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"summary_{date_str}.md")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


if __name__ == "__main__":
    from data import fetch_market_data
    from factors import calculate_all_factors
    from forecast import build_outlook

    md = fetch_market_data()
    factors = calculate_all_factors(md, manual_factors=["ตัวอย่าง: ทดสอบ manual factor"])
    outlook = build_outlook(factors)
    content = render_report(md, factors, outlook)
    path = save_report(content)
    print(f"Saved to {path}")
