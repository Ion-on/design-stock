#!/usr/bin/env python3
"""
Stock Brief CLI Tool
เพียงใส่ชื่อหุ้น แล้วได้ Brief อย่างละเอียด
"""

import sys
import json
from datetime import datetime
from analysis import StockAnalyzer


def format_brief(analysis):
    """Format analysis into a detailed brief"""

    ticker = analysis['ticker']
    info = analysis['info']
    perf = analysis['performance']
    momentum = analysis['momentum']
    sr = analysis['support_resistance']
    signal = analysis['signal']

    brief = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           {ticker} INVESTMENT BRIEF
╚══════════════════════════════════════════════════════════════════════════════╝

📊 STOCK INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Name:          {info['name']}
  Sector:        {info['sector']}
  Industry:      {info['industry']}
  Market Cap:    {info['market_cap']}
  P/E Ratio:     {info['pe_ratio']}
  Dividend:      {info['dividend_yield']}

💰 PERFORMANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Current Price:      ${perf['current_price']}
  1-Day Return:       {perf['return_1d']:+.2f}%
  5-Day Return:       {perf['return_5d']:+.2f}%
  1-Month Return:     {perf['return_1m']:+.2f}%
  Volatility (Ann.):  {perf['volatility']:.2f}%
  52W High:           ${perf['high_52w']}
  52W Low:            ${perf['low_52w']}

📈 TECHNICAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RSI (14):           {momentum['rsi']:.2f} {"(OVERBOUGHT)" if momentum['rsi'] > 70 else "(OVERSOLD)" if momentum['rsi'] < 30 else "(Normal)"}
  MACD:               {momentum['macd']:.4f}
  MACD Signal:        {momentum['macd_signal']:.4f}
  MACD Histogram:     {momentum['macd_hist']:.4f}

  Bollinger Bands:
    Upper:            ${momentum['bb_upper']:.2f}
    Middle (SMA20):   ${momentum['bb_middle']:.2f}
    Lower:            ${momentum['bb_lower']:.2f}

  Stochastic:
    %K:               {momentum['stoch_k']:.2f}
    %D:               {momentum['stoch_d']:.2f}

🎯 SUPPORT & RESISTANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Resistance 2:       ${sr['resistance_2']}
  Resistance 1:       ${sr['resistance_1']}
  Pivot Point:        ${sr['pivot']}
  Support 1:          ${sr['support_1']}
  Support 2:          ${sr['support_2']}

⚡ TRADING SIGNALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for sig in signal['signals']:
        brief += f"  • {sig}\n"

    brief += f"""
RECOMMENDATION:     {signal['recommendation']}
Signal Score:       {signal['score']}/3

📋 BUSINESS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{info['description']}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Strategy: Short-term (1-3 Days) | Swing Trading Focus
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return brief


def save_brief(ticker, analysis):
    """Save brief to markdown file"""
    brief_text = format_brief(analysis)

    filename = f"briefs/{ticker.upper()}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(brief_text)

    return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python brief_cli.py TICKER [--save]")
        print("Example: python brief_cli.py AAPL --save")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    save_flag = '--save' in sys.argv

    print(f"\n🔍 Analyzing {ticker}...")

    analyzer = StockAnalyzer(ticker)
    analysis = analyzer.get_full_analysis()

    brief = format_brief(analysis)
    print(brief)

    if save_flag:
        filename = save_brief(ticker, analysis)
        print(f"\n✅ Brief saved to: {filename}")


if __name__ == "__main__":
    main()
