"""
market/factors.py
Factor-scoring for the daily market-condition summary, in the same style as
analysis.py's calculate_factors() (list of {'factor', 'direction', 'detail'} dicts,
each with a directional bullish/bearish/neutral read and a Thai-language detail).

Quantitative factors come from market/data.py (indices, gold, ^TNX, Fed Funds Rate).
Qualitative/manual factors (geopolitics, IPOs, earnings shocks, etc.) are NOT
scraped — they are passed in by hand as `manual_factors: list[str]` after a
human (Claude, in the main session) runs a web search for the day's news.
"""

import numpy as np


def _pct_change(df, periods=1):
    """Simple % change over N periods using Close, mirroring analysis.py's return calcs."""
    if df is None or len(df) <= periods:
        return None
    return ((df['Close'].iloc[-1] / df['Close'].iloc[-1 - periods]) - 1) * 100


def calculate_index_factors(indices):
    """
    Build factor entries from the index/asset snapshot (dict from data.fetch_index_snapshot).
    Mirrors analysis.py's calculate_factors() shape and tone.
    """
    factors = []

    for ticker, info in indices.items():
        df = info.get('data')
        label = info.get('label', ticker)
        tag = info.get('tag', 'macro')

        if df is None:
            factors.append({
                'factor': label,
                'direction': 'neutral',
                'tag': tag,
                'detail': f"ไม่สามารถดึงข้อมูล {label} ได้ ({info.get('error', 'unknown error')})",
            })
            continue

        chg_1d = _pct_change(df, 1)
        chg_5d = _pct_change(df, 5)
        if chg_1d is None:
            continue

        price = df['Close'].iloc[-1]

        # ^TNX (10Y yield) and gold get macro-specific framing; equities/ETFs get trend framing
        if ticker == '^TNX':
            if chg_5d is not None and chg_5d > 3:
                factors.append({'factor': label, 'direction': 'bearish', 'tag': tag,
                                 'detail': f'อัตราผลตอบแทนพันธบัตร 10 ปี อยู่ที่ {price:.2f}% เพิ่มขึ้น {chg_5d:+.1f}% ใน 5 วัน — ต้นทุนเงินทุนสูงขึ้น กดดันหุ้นเติบโต/หุ้นเทคโดยเฉพาะ'})
            elif chg_5d is not None and chg_5d < -3:
                factors.append({'factor': label, 'direction': 'bullish', 'tag': tag,
                                 'detail': f'อัตราผลตอบแทนพันธบัตร 10 ปี อยู่ที่ {price:.2f}% ลดลง {chg_5d:+.1f}% ใน 5 วัน — ต้นทุนเงินทุนผ่อนคลายลง เป็นบวกต่อหุ้นเติบโต/หุ้นเทค'})
            else:
                factors.append({'factor': label, 'direction': 'neutral', 'tag': tag,
                                 'detail': f'อัตราผลตอบแทนพันธบัตร 10 ปี อยู่ที่ {price:.2f}% ค่อนข้างทรงตัว ({chg_5d:+.1f}% ใน 5 วัน)'})
            continue

        if ticker == 'GC=F':
            if chg_1d is not None and chg_1d > 1:
                factors.append({'factor': label, 'direction': 'bearish', 'tag': tag,
                                 'detail': f'ทองคำ +{chg_1d:.1f}% ในวันเดียว — สัญญาณ risk-off/หาสินทรัพย์ปลอดภัย นักลงทุนอาจกังวลความเสี่ยงในตลาดหุ้น'})
            elif chg_1d is not None and chg_1d < -1:
                factors.append({'factor': label, 'direction': 'bullish', 'tag': tag,
                                 'detail': f'ทองคำ {chg_1d:.1f}% ในวันเดียว — สัญญาณ risk-on เม็ดเงินไหลกลับเข้าสินทรัพย์เสี่ยง'})
            else:
                factors.append({'factor': label, 'direction': 'neutral', 'tag': tag,
                                 'detail': f'ทองคำเคลื่อนไหว {chg_1d:+.1f}% ในวันเดียว ยังไม่มีสัญญาณ risk-on/off ชัดเจน'})
            continue

        # Equity indices / sector ETFs — trend + magnitude framing
        if chg_1d > 1:
            direction = 'bullish'
            detail = f'{label} +{chg_1d:.1f}% ในวันเดียว'
        elif chg_1d < -1:
            direction = 'bearish'
            detail = f'{label} {chg_1d:.1f}% ในวันเดียว'
        else:
            direction = 'neutral'
            detail = f'{label} ขยับ {chg_1d:+.1f}% ในวันเดียว ใกล้เคียงทรงตัว'

        if chg_5d is not None:
            detail += f' (5 วัน: {chg_5d:+.1f}%)'

        factors.append({'factor': label, 'direction': direction, 'tag': tag, 'detail': detail})

    return factors


def calculate_fed_funds_factor(fed_funds):
    """Build a single factor entry from the FRED Fed Funds Rate fetch result."""
    if fed_funds.get('error'):
        return {
            'factor': 'Fed Funds Rate (FRED, DFF)',
            'direction': 'neutral',
            'tag': 'macro',
            'detail': f"ไม่สามารถดึงข้อมูล Fed Funds Rate จาก FRED ได้ ({fed_funds['error']})",
        }

    rate = fed_funds['latest_rate']
    change = fed_funds['change']
    date = fed_funds['latest_date']

    if change > 0:
        direction = 'bearish'
        detail = (f"Effective Fed Funds Rate ล่าสุด ({date}) อยู่ที่ {rate:.2f}% "
                   f"ปรับขึ้นจากวันก่อนหน้า {change:+.2f} จุด — นโยบายการเงินเข้มงวดขึ้น กดดันสินทรัพย์เสี่ยง")
    elif change < 0:
        direction = 'bullish'
        detail = (f"Effective Fed Funds Rate ล่าสุด ({date}) อยู่ที่ {rate:.2f}% "
                   f"ปรับลงจากวันก่อนหน้า {change:+.2f} จุด — นโยบายการเงินผ่อนคลายลง เป็นบวกต่อสินทรัพย์เสี่ยง")
    else:
        direction = 'neutral'
        detail = (f"Effective Fed Funds Rate ล่าสุด ({date}) อยู่ที่ {rate:.2f}% ทรงตัวจากวันก่อนหน้า "
                   f"— ยังไม่มีการเปลี่ยนแปลงนโยบายการเงินอย่างมีนัยสำคัญในระยะนี้")

    return {'factor': 'Fed Funds Rate (FRED, DFF)', 'direction': direction, 'tag': 'macro', 'detail': detail}


def build_manual_factors(manual_factors):
    """
    Wrap user/Claude-supplied qualitative factors (geopolitics, IPOs, earnings
    shocks, etc.) into the same factor dict shape. Direction defaults to
    'neutral' since these are plain free-text notes, not scored signals —
    the human supplying them should phrase the bullish/bearish read into the text.

    manual_factors: list[str] (plain text). No scraping/automation here by design.
    """
    factors = []
    if not manual_factors:
        return factors

    for note in manual_factors:
        note = note.strip()
        if not note:
            continue
        factors.append({
            'factor': 'Manual/Qualitative Input',
            'direction': 'neutral',
            'tag': 'qualitative',
            'detail': note,
        })
    return factors


def calculate_all_factors(market_data, manual_factors=None):
    """
    market_data: dict from data.fetch_market_data() -> {'indices': ..., 'fed_funds': ...}
    manual_factors: list[str] passed by hand, see build_manual_factors()
    """
    factors = []
    factors.extend(calculate_index_factors(market_data['indices']))
    factors.append(calculate_fed_funds_factor(market_data['fed_funds']))
    factors.extend(build_manual_factors(manual_factors))
    return factors


if __name__ == "__main__":
    import json
    from data import fetch_market_data

    md = fetch_market_data()
    factors = calculate_all_factors(md, manual_factors=["ตัวอย่าง: ทดสอบ manual factor"])
    print(json.dumps(factors, indent=2, ensure_ascii=False))
