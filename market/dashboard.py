"""
market/dashboard.py
Renders stock/dashboard_market.html from the same data used by report.py
(market_data, factors, outlook) — neumorphic theme matching the per-ticker
dashboards (stock/dashboard_<TICKER>.html). Always overwrites the single
stock/dashboard_market.html file (it represents "current" market state,
not a dated archive like market/summary_<DATE>.md).

Read-only research tooling. No order execution, no broker integration, no
scheduled/unattended automation, no live streaming.
"""

import os
import json
from datetime import datetime

import yfinance as yf
import pandas as pd

DIRECTION_COLOR = {'bullish': 'var(--green)', 'bearish': 'var(--terracotta)', 'neutral': 'var(--gold)'}
DIRECTION_TAG = {'bullish': 'bullish', 'bearish': 'bearish', 'neutral': 'neutral'}
OUTLOOK_TAG_TEXT = {'UP': ('bullish', 'UP'), 'DOWN': ('bearish', 'DOWN'), 'SIDEWAYS': ('neutral', 'SIDEWAYS')}

HERO_TICKER = 'GC=F'
HERO_LABEL = 'Gold Futures'


def fetch_hero_intraday(ticker=HERO_TICKER, period='1d', interval='5m'):
    """1-day intraday series for the hero chart, same pattern as the per-ticker dashboards."""
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if df.empty:
            return [], []
        times = [idx.strftime('%H:%M') for idx in df.index]
        closes = df['Close'].round(2).tolist()
        return times, closes
    except Exception:
        return [], []


def _index_series(market_data, ticker):
    info = market_data['indices'].get(ticker, {})
    df = info.get('data')
    if df is None:
        return None
    return df


def _stat_card(label, last, pct, unit=''):
    color = 'var(--green)' if pct is not None and pct >= 0 else 'var(--terracotta)'
    pct_str = f"{pct:+.2f}%" if pct is not None else "N/A"
    last_str = f"{last:,.2f}{unit}" if last is not None else "N/A"
    return f"""
      <div class="card">
        <div class="card-header"><span>{label}</span><span class="dot" style="background:{color};"></span></div>
        <div class="stat-value">{last_str}</div>
        <div style="font-size:13px;color:{color};margin-top:2px;">{pct_str} (1d)</div>
      </div>"""


def _watch_row(label, pct):
    if pct is None:
        return f'<div class="row"><span>{label}</span><span>N/A</span></div>'
    color = 'var(--green)' if pct >= 0 else 'var(--terracotta)'
    return f'<div class="row"><span>{label}</span><span style="color:{color};">{pct:+.2f}%</span></div>'


def _factor_row(factor):
    tag = DIRECTION_TAG.get(factor.get('direction'), 'neutral')
    return f"""
      <div class="factor-row">
        <span class="name">{factor['factor']}</span>
        <span class="tag {tag}">{factor.get('direction', 'neutral')}</span>
      </div>
      <div class="factor-row"><span class="detail">{factor['detail']}</span></div>"""


def render_dashboard_html(market_data, factors, outlook, manual_factors=None, generated_at=None):
    generated_at = generated_at or datetime.now()
    date_str = generated_at.strftime('%Y-%m-%d %H:%M')

    spx = _index_series(market_data, '^GSPC')
    ixic = _index_series(market_data, '^IXIC')
    dji = _index_series(market_data, '^DJI')
    xle = _index_series(market_data, 'XLE')
    xlk = _index_series(market_data, 'XLK')
    arkx = _index_series(market_data, 'ARKX')
    gold = _index_series(market_data, 'GC=F')
    tnx = _index_series(market_data, '^TNX')
    fed = market_data['fed_funds']

    def last_pct(df):
        if df is None or len(df) < 1:
            return None, None
        last = float(df['Close'].iloc[-1])
        if len(df) > 1:
            prev = float(df['Close'].iloc[-2])
            pct = (last / prev - 1) * 100
        else:
            pct = None
        return last, pct

    spx_last, spx_pct = last_pct(spx)
    ixic_last, ixic_pct = last_pct(ixic)
    dji_last, dji_pct = last_pct(dji)
    xle_last, xle_pct = last_pct(xle)
    xlk_last, xlk_pct = last_pct(xlk)
    arkx_last, arkx_pct = last_pct(arkx)
    gold_last, gold_pct = last_pct(gold)
    tnx_last, tnx_pct = last_pct(tnx)

    hero_times, hero_closes = fetch_hero_intraday()

    gold_dates = [d.strftime('%m-%d') for d in gold.index] if gold is not None else []
    gold_closes = gold['Close'].round(2).tolist() if gold is not None else []

    def mini_series(df):
        if df is None:
            return [], []
        return [d.strftime('%m-%d') for d in df.index], df['Close'].round(2).tolist()

    spx_dates, spx_closes = mini_series(spx)
    ixic_dates, ixic_closes = mini_series(ixic)
    dji_dates, dji_closes = mini_series(dji)
    xlk_dates, xlk_closes = mini_series(xlk)

    bm = outlook['broad_market']
    bm_tag, bm_text = OUTLOOK_TAG_TEXT.get(bm['direction'], ('neutral', bm['direction']))

    sector_cards = ""
    for tag, s in outlook['sectors'].items():
        s_tag, s_text = OUTLOOK_TAG_TEXT.get(s['direction'], ('neutral', s['direction']))
        sector_cards += f"""
    <div class="card">
      <div class="card-header"><span>{s['sector_name_th']} ({tag})</span><span class="tag {s_tag}">{s_text}</span></div>
      <div class="indicator-value">{s['score']:+d} pts</div>
      <div class="indicator-sub">Confidence: {s['confidence']} · {s['factor_count']} ปัจจัย</div>
    </div>"""

    quant_factors = [f for f in factors if f.get('tag') != 'qualitative']
    qual_factors = [f for f in factors if f.get('tag') == 'qualitative']

    factor_rows = "".join(_factor_row(f) for f in quant_factors)

    if qual_factors:
        qual_html = "".join(
            f'<div class="factor-row"><span class="detail">{f["detail"]}</span></div>'
            for f in qual_factors
        )
    else:
        qual_html = ('<div class="factor-row"><span class="detail">'
                     'ยังไม่มีการป้อนข่าวเชิงคุณภาพ (geopolitics/IPO/earnings) สำหรับรอบนี้</span></div>')

    fed_str = "N/A" if fed.get('error') else f"{fed['latest_rate']:.2f}%"
    fed_change_str = "" if fed.get('error') else f"({fed['change']:+.2f} จุด, {fed['latest_date']})"

    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Market Overview Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root{{
    --bg-color:#eef2f7;
    --text-color:#4a5568;
    --soft-shadow-dark: 8px 8px 16px rgba(163, 177, 198, 0.5);
    --soft-shadow-light: -8px -8px 16px rgba(255, 255, 255, 0.8);
    --soft-shadow-inset: inset 4px 4px 8px rgba(163, 177, 198, 0.5), inset -4px -4px 8px rgba(255, 255, 255, 0.8);
    --bg:var(--bg-color); --card:var(--bg-color); --text:var(--text-color);
    --muted:#8a94a6; --green:#5fae78; --gold:#cf9f4f; --terracotta:#bd6f42; --border:#d6dee8;
  }}
  *{{box-sizing:border-box;}}
  body{{margin:0;min-height:100vh;font-family:'Segoe UI', Tahoma, sans-serif;background:var(--bg-color);color:var(--text-color);display:flex;align-items:center;justify-content:center;padding:40px 20px;}}
  .dashboard{{width:100%;max-width:1080px;}}
  .title{{text-align:center;color:var(--text-color);letter-spacing:6px;font-size:13px;margin-bottom:4px;opacity:.65;}}
  .title.main{{font-size:26px;letter-spacing:8px;font-weight:600;margin-bottom:24px;}}
  .grid{{display:grid;grid-template-columns: 1fr 1.6fr 1fr;gap:16px;}}
  .col{{display:flex;flex-direction:column;gap:16px;}}
  .card{{background:var(--bg-color);border-radius:20px;padding:16px 18px;color:var(--text-color);box-shadow:var(--soft-shadow-dark), var(--soft-shadow-light);border:none;}}
  .card-header{{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--muted);letter-spacing:1px;margin-bottom:10px;text-transform:uppercase;}}
  .dot{{width:8px;height:8px;border-radius:50%;background:var(--green);}}
  .stat-value{{font-size:28px;font-weight:600;}}
  .chart-wrap{{position:relative;height:90px;}}
  .chart-wrap.tall{{height:120px;}}
  .center-card{{background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;gap:14px;}}
  .center-frame{{width:100%;max-width:380px;aspect-ratio:1/1;border-radius:24px;overflow:hidden;padding:14px 8px 6px;border:6px solid var(--bg-color);box-shadow:var(--soft-shadow-dark), var(--soft-shadow-light);position:relative;}}
  .center-frame canvas{{width:100% !important;height:100% !important;}}
  .center-frame .ring{{position:absolute;inset:-6px;border-radius:24px;border:2px dashed rgba(74,85,104,.15);pointer-events:none;}}
  .nav-pill{{display:flex;gap:6px;justify-content:center;margin-bottom:10px;}}
  .nav-pill span{{width:6px;height:6px;border-radius:50%;background:rgba(74,85,104,.3);}}
  .nav-pill span:first-child{{background:var(--text-color);}}
  .list-card .row{{display:flex;justify-content:space-between;align-items:center;font-size:12px;padding:6px 0;border-bottom:1px solid var(--border);}}
  .list-card .row:last-child{{border-bottom:none;}}
  .area-card{{grid-column: span 1;}}
  .section-label{{color:var(--text-color);opacity:.65;letter-spacing:3px;font-size:11px;text-transform:uppercase;margin:28px 0 12px 4px;}}
  .grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px;}}
  .grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px;}}
  .indicator-value{{font-size:22px;font-weight:600;}}
  .indicator-sub{{font-size:11px;color:var(--muted);margin-top:4px;}}
  .tag{{display:inline-block;font-size:10px;padding:2px 8px;border-radius:10px;text-transform:uppercase;letter-spacing:.5px;}}
  .tag.bullish{{background:rgba(95,174,120,.16);color:var(--green);}}
  .tag.bearish{{background:rgba(189,111,66,.16);color:var(--terracotta);}}
  .tag.neutral{{background:rgba(207,159,79,.16);color:var(--gold);}}
  .factor-row{{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;font-size:12px;padding:9px 0;border-bottom:1px solid var(--border);}}
  .factor-row:last-child{{border-bottom:none;}}
  .factor-row .name{{font-weight:600;white-space:nowrap;}}
  .factor-row .detail{{color:var(--muted);font-size:11px;line-height:1.5;}}
  .info-row{{display:flex;justify-content:space-between;font-size:12px;padding:6px 0;border-bottom:1px solid var(--border);}}
  .info-row:last-child{{border-bottom:none;}}
  .bottom-row{{display:grid;grid-template-columns: 1fr 2fr;gap:16px;margin-top:16px;}}
  @media (max-width:860px){{
    .grid{{grid-template-columns:1fr;}}
    .bottom-row{{grid-template-columns:1fr;}}
    .grid-4{{grid-template-columns:repeat(2,1fr);}}
    .grid-3{{grid-template-columns:1fr;}}
  }}
</style>
</head>
<body>
<div class="dashboard">
  <div class="title">U.S. MARKET &amp; GOLD · GENERATED {date_str}</div>
  <div class="title main">MARKET OVERVIEW</div>

  <div class="grid">
    <div class="col">
      {_stat_card('S&amp;P 500', spx_last, spx_pct)}
      {_stat_card('Nasdaq', ixic_last, ixic_pct)}
      {_stat_card('Dow Jones', dji_last, dji_pct)}
      <div class="card">
        <div class="card-header"><span>10Y Treasury Yield</span><span class="dot"></span></div>
        <div class="stat-value">{f"{tnx_last:.2f}%" if tnx_last is not None else "N/A"}</div>
        <div style="font-size:13px;color:var(--muted);margin-top:2px;">{f"{tnx_pct:+.2f}% (1d)" if tnx_pct is not None else ""}</div>
      </div>
    </div>

    <div class="col center-card">
      <div class="nav-pill"><span></span><span></span><span></span></div>
      <div class="center-frame" style="background:var(--card);display:flex;align-items:center;justify-content:center;">
        <canvas id="heroChart"></canvas>
        <div class="ring"></div>
      </div>
      <div class="card area-card" style="width:100%;">
        <div class="card-header"><span>Gold Closing Price</span><span>USD/oz · GC=F</span></div>
        <div class="chart-wrap tall"><canvas id="areaChart"></canvas></div>
      </div>
    </div>

    <div class="col">
      {_stat_card(HERO_LABEL, gold_last, gold_pct)}
      <div class="card list-card">
        <div class="card-header"><span>Sectors to Watch (1d %)</span><span class="dot" style="background:var(--terracotta);"></span></div>
        {_watch_row('XLE (Energy)', xle_pct)}
        {_watch_row('XLK (Technology)', xlk_pct)}
        {_watch_row('ARKX (Space)', arkx_pct)}
      </div>
      <div class="card">
        <div class="card-header"><span>Fed Funds Rate</span><span class="dot"></span></div>
        <div class="stat-value">{fed_str}</div>
        <div style="font-size:13px;color:var(--muted);margin-top:2px;">{fed_change_str}</div>
      </div>
    </div>
  </div>

  <div class="section-label">Index Snapshot</div>
  <div class="grid-4">
    <div class="card">
      <div class="card-header"><span>S&amp;P 500</span><span class="tag {DIRECTION_TAG.get('bullish' if (spx_pct or 0) >= 0 else 'bearish')}">{f"{spx_pct:+.2f}%" if spx_pct is not None else "N/A"}</span></div>
      <div class="chart-wrap"><canvas id="spxChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><span>Nasdaq</span><span class="tag {DIRECTION_TAG.get('bullish' if (ixic_pct or 0) >= 0 else 'bearish')}">{f"{ixic_pct:+.2f}%" if ixic_pct is not None else "N/A"}</span></div>
      <div class="chart-wrap"><canvas id="ixicChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><span>Dow Jones</span><span class="tag {DIRECTION_TAG.get('bullish' if (dji_pct or 0) >= 0 else 'bearish')}">{f"{dji_pct:+.2f}%" if dji_pct is not None else "N/A"}</span></div>
      <div class="chart-wrap"><canvas id="djiChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header"><span>XLK (Tech)</span><span class="tag {DIRECTION_TAG.get('bullish' if (xlk_pct or 0) >= 0 else 'bearish')}">{f"{xlk_pct:+.2f}%" if xlk_pct is not None else "N/A"}</span></div>
      <div class="chart-wrap"><canvas id="xlkChart"></canvas></div>
    </div>
  </div>

  <div class="section-label">1-3 Day Outlook</div>
  <div class="grid-3">
    <div class="card">
      <div class="card-header"><span>Broad Market</span><span class="tag {bm_tag}">{bm_text}</span></div>
      <div class="indicator-value">{bm['score']:+d} pts</div>
      <div class="indicator-sub">Confidence: {bm['confidence']} · {bm['factor_count']} ปัจจัย</div>
    </div>
    {sector_cards}
  </div>

  <div class="bottom-row">
    <div class="card">
      <div class="card-header"><span>Assumptions &amp; Kill Conditions</span><span class="dot"></span></div>
      {"".join(f'<div class="info-row"><span style="font-size:11px;">{a}</span></div>' for a in outlook['assumptions'][:2])}
      {"".join(f'<div class="info-row"><span style="font-size:11px;color:var(--terracotta);">{k}</span></div>' for k in outlook['kill_conditions'][:2])}
    </div>
    <div class="card">
      <div class="card-header"><span>Key Factors (Quantitative + Qualitative)</span><span class="dot"></span></div>
      {factor_rows}
      <div class="card-header" style="margin-top:14px;"><span>Qualitative (Manual)</span><span class="dot" style="background:var(--gold);"></span></div>
      {qual_html}
    </div>
  </div>
</div>

<script>
  const muted = '#8a94a6';
  Chart.defaults.color = muted;
  Chart.defaults.font.family = "Segoe UI";
  const noGrid = {{ grid:{{display:false}}, ticks:{{display:false}}, border:{{display:false}} }};

  const heroTimes = {json.dumps(hero_times)};
  const heroCloses = {json.dumps(hero_closes)};
  const goldDates = {json.dumps(gold_dates)};
  const goldCloses = {json.dumps(gold_closes)};
  const spxDates = {json.dumps(spx_dates)};
  const spxCloses = {json.dumps(spx_closes)};
  const ixicCloses = {json.dumps(ixic_closes)};
  const djiCloses = {json.dumps(dji_closes)};
  const xlkCloses = {json.dumps(xlk_closes)};

  new Chart(document.getElementById('heroChart'), {{
    type:'line',
    data:{{ labels:heroTimes, datasets:[{{ data:heroCloses, borderColor:'#bd6f42', backgroundColor:'rgba(207,159,79,0.22)', fill:true, tension:.35, pointRadius:0, borderWidth:3 }}] }},
    options:{{
      responsive:true, maintainAspectRatio:false,
      layout:{{padding:{{top:4,right:6,bottom:0,left:0}}}},
      plugins:{{legend:{{display:false}}, tooltip:{{enabled:false}}}},
      scales:{{
        x:{{ display:true, ticks:{{color:muted, font:{{size:9}}, maxTicksLimit:6, maxRotation:0}}, grid:{{display:false}}, border:{{color:'#d6dee8'}}, title:{{display:true, text:'เวลา', color:muted, font:{{size:9}}}} }},
        y:{{ display:true, position:'right', ticks:{{color:muted, font:{{size:9}}, maxTicksLimit:5, callback:v => '$'+v}}, grid:{{color:'#e4e9f0'}}, border:{{display:false}}, title:{{display:true, text:'ราคาทอง', color:muted, font:{{size:9}}}} }}
      }},
      elements:{{line:{{borderJoinStyle:'round'}}}}
    }}
  }});

  new Chart(document.getElementById('areaChart'), {{
    type:'line',
    data:{{ labels:goldDates, datasets:[{{ data:goldCloses, borderColor:'#bd6f42', backgroundColor:'rgba(189,111,66,0.25)', fill:true, tension:.4, pointRadius:0, borderWidth:2 }}] }},
    options:{{ responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{x:noGrid, y:noGrid}}, interaction:{{intersect:false}} }}
  }});

  function smallLine(id, data, color){{
    new Chart(document.getElementById(id), {{
      type:'line',
      data:{{ labels:spxDates, datasets:[{{ data:data, borderColor:color, backgroundColor:'transparent', tension:.4, pointRadius:0, borderWidth:2 }}] }},
      options:{{ responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{x:noGrid, y:noGrid}} }}
    }});
  }}
  smallLine('spxChart', spxCloses, '#5fae78');
  smallLine('ixicChart', ixicCloses, '#5fae78');
  smallLine('djiChart', djiCloses, '#5fae78');
  smallLine('xlkChart', xlkCloses, '#5fae78');
</script>
</body>
</html>
"""
    return html


def save_dashboard(html, out_path=None):
    """Always overwrites stock/dashboard_market.html — represents current state, not a dated archive."""
    if out_path is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_path = os.path.join(repo_root, 'stock', 'dashboard_market.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return out_path


if __name__ == "__main__":
    from data import fetch_market_data
    from factors import calculate_all_factors
    from forecast import build_outlook

    md = fetch_market_data()
    factors = calculate_all_factors(md, manual_factors=[])
    outlook = build_outlook(factors)
    html = render_dashboard_html(md, factors, outlook)
    path = save_dashboard(html)
    print(f"Saved dashboard to {path}")
