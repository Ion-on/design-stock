"""
market/forecast.py
1-3 day directional outlook for the broad market plus sector exposure tags for
energy / space / tech (the focus sectors per CLAUDE.md). Read-only research
output only — no order execution, no automation.

This is a composite heuristic score over the factor list built in factors.py,
similar in spirit to analysis.py's generate_signal()/predict_next_day(), but
applied to market-wide indices/macro factors instead of a single stock.
"""

DIRECTION_SCORE = {'bullish': 1, 'bearish': -1, 'neutral': 0}


def _score_factors(factors, tags=None):
    """Sum direction scores for factors matching any of `tags` (None = all)."""
    score = 0
    n = 0
    for f in factors:
        if tags is not None and f.get('tag') not in tags:
            continue
        score += DIRECTION_SCORE.get(f.get('direction'), 0)
        n += 1
    return score, n


def _label_from_score(score):
    if score >= 2:
        return 'UP', 'High' if score >= 3 else 'Medium'
    elif score <= -2:
        return 'DOWN', 'High' if score <= -3 else 'Medium'
    elif score > 0:
        return 'UP', 'Low'
    elif score < 0:
        return 'DOWN', 'Low'
    else:
        return 'SIDEWAYS', 'Low'


def build_outlook(factors):
    """
    Build the 1-3 day directional outlook for the broad market and for each
    focus sector (energy, space, tech), based on the factor list from
    factors.calculate_all_factors() (quant factors + Fed Funds Rate + any
    manual/qualitative notes passed in by hand).
    """
    broad_score, broad_n = _score_factors(factors, tags={'broad', 'macro'})
    direction, confidence = _label_from_score(broad_score)

    sector_outlook = {}
    for sector_tag, sector_name in (('energy', 'พลังงาน'), ('space', 'อวกาศ'), ('tech', 'เทคโนโลยี')):
        s_score, s_n = _score_factors(factors, tags={sector_tag, 'macro'})
        s_dir, s_conf = _label_from_score(s_score)
        sector_outlook[sector_tag] = {
            'sector_name_th': sector_name,
            'direction': s_dir,
            'confidence': s_conf,
            'score': s_score,
            'factor_count': s_n,
        }

    qualitative_notes = [f['detail'] for f in factors if f.get('tag') == 'qualitative']

    assumptions = [
        'คะแนนสะสมจากทิศทาง (bullish/bearish/neutral) ของปัจจัยเชิงปริมาณ (ดัชนีหลัก, XLE/XLK/ARKX, ทองคำ, 10Y yield, Fed Funds Rate) เป็นตัวแทนภาวะตลาดกว้าง ไม่ใช่การพยากรณ์ราคาที่แม่นยำ',
        'ปัจจัยเชิงคุณภาพ (ภูมิรัฐศาสตร์, IPO, earnings shock) ต้องถูกป้อนเข้ามาด้วยมือผ่าน manual_factors — หากไม่ได้ป้อน outlook นี้จะไม่สะท้อนข่าวของวันนั้น',
        'กรอบเวลา 1-3 วัน เท่านั้น ไม่ใช่มุมมองระยะกลาง-ยาว',
        'ไม่มีการสั่งซื้อขายอัตโนมัติ และไม่มีการรันซ้ำแบบ scheduled — เป็นรายงานวิจัยที่สร้างตามคำขอเท่านั้น',
    ]

    kill_conditions = [
        'หาก Fed Funds Rate หรือ 10Y yield พลิกทิศทางอย่างรุนแรงระหว่างวัน (เช่น มีถ้อยแถลง Fed แบบ surprise) outlook นี้ใช้ไม่ได้ทันที ต้องรันใหม่',
        'หากมีปัจจัยเชิงคุณภาพสำคัญเกิดขึ้นภายหลังการรันรายงาน (geopolitical shock, IPO ขนาดใหญ่, earnings shock ของหุ้นนำตลาด) ที่ไม่ได้รวมอยู่ใน manual_factors รายงานนี้ถือว่าล้าสมัยทันที',
        'หากจำนวนปัจจัยที่ใช้คำนวณ (factor_count) ของ sector ใด sector หนึ่งต่ำเกินไป (เช่น <=1) ความเชื่อมั่นของ sector นั้นต่ำมาก ไม่ควรใช้ตัดสินใจเดี่ยวๆ',
    ]

    return {
        'broad_market': {
            'direction': direction,
            'confidence': confidence,
            'score': broad_score,
            'factor_count': broad_n,
        },
        'sectors': sector_outlook,
        'qualitative_notes': qualitative_notes,
        'assumptions': assumptions,
        'kill_conditions': kill_conditions,
    }


if __name__ == "__main__":
    import json
    from data import fetch_market_data
    from factors import calculate_all_factors

    md = fetch_market_data()
    factors = calculate_all_factors(md, manual_factors=["ตัวอย่าง manual factor สำหรับทดสอบ"])
    outlook = build_outlook(factors)
    print(json.dumps(outlook, indent=2, ensure_ascii=False))
