#!/usr/bin/env python3
"""
Daily Market Condition Report CLI
ดึงข้อมูลตลาดวันนี้ (ดัชนีหลัก, พลังงาน/อวกาศ/เทคโนโลยี, ทองคำ, 10Y yield, Fed Funds Rate)
ผสมกับปัจจัยเชิงคุณภาพที่ป้อนด้วยมือ แล้วสร้างรายงาน market/summary_<DATE>.md

Usage:
    python market/cli.py
    python market/cli.py --save
    python market/cli.py --factor "Fed เลื่อนประชุมกะทันหัน" --factor "IPO ใหญ่ของหุ้นอวกาศสัปดาห์นี้"
    python market/cli.py --save --factor "..." --factor "..."

Notes:
  - This is read-only research tooling: no order execution, no broker
    integration, no scheduled/unattended automation, no live streaming.
  - Re-running on the same day overwrites market/summary_<DATE>.md (same
    convention as briefs/<TICKER>.md) — no timestamped variants.
  - Manual/qualitative factors (geopolitics, IPOs, earnings shocks) are NOT
    scraped automatically. Pass them by hand via repeated --factor flags;
    typically a human (Claude, in the main session) runs a web search first
    and supplies the day's qualitative factors this way.
"""

import sys
import argparse

from data import fetch_market_data
from factors import calculate_all_factors
from forecast import build_outlook
from report import render_report, save_report
from dashboard import render_dashboard_html, save_dashboard


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate the daily market-condition summary report."
    )
    parser.add_argument(
        '--factor', '-f', action='append', dest='manual_factors', default=[],
        help='A manual/qualitative factor (geopolitics, IPO, earnings shock, etc). '
             'Repeat the flag for multiple factors.'
    )
    parser.add_argument(
        '--save', action='store_true',
        help='Save the report to market/summary_<DATE>.md (overwrites if run again same day).'
    )
    parser.add_argument(
        '--period', default='1mo',
        help='yfinance period for index history (default: 1mo).'
    )
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    print("\nFetching market data (indices, sector ETFs, gold, ^TNX, Fed Funds Rate)...")
    market_data = fetch_market_data(period=args.period)

    factors = calculate_all_factors(market_data, manual_factors=args.manual_factors)
    outlook = build_outlook(factors)
    content = render_report(market_data, factors, outlook, manual_factors=args.manual_factors)

    if args.save:
        path = save_report(content)

    dashboard_html = render_dashboard_html(market_data, factors, outlook, manual_factors=args.manual_factors)
    dashboard_path = save_dashboard(dashboard_html)

    # Console output: some Windows terminals use a legacy codepage (e.g. cp874)
    # that can't encode emoji used in the markdown. Print defensively so the
    # report (already saved as UTF-8) is never lost to a console encoding error.
    try:
        print(content)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        sys.stdout.write(content.encode(encoding, errors='replace').decode(encoding) + "\n")

    if args.save:
        print(f"\nSaved to: {path}")
    print(f"Dashboard updated: {dashboard_path}")


if __name__ == "__main__":
    main()
