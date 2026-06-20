"""
market/data.py
Read-only data fetchers for the daily market-condition summary.

Sources:
  - yfinance: major indices, gold, ^TNX (10Y Treasury yield) — same lib/pattern as analysis.py
  - FRED (St. Louis Fed) no-key CSV endpoint: real Fed Funds Rate (DFF series)

No order execution, no broker integration, no scheduled automation, no live
streaming. This module only fetches a snapshot of public market data on demand.
"""

import yfinance as yf
import pandas as pd
import requests
from io import StringIO

# Index/asset tickers tracked for the daily market snapshot.
# Tags map each ticker to the sector lens this tool cares about
# (energy / space / tech) per CLAUDE.md investing focus.
INDEX_TICKERS = {
    '^GSPC': {'label': 'S&P 500', 'tag': 'broad'},
    '^IXIC': {'label': 'Nasdaq Composite', 'tag': 'tech'},
    '^DJI': {'label': 'Dow Jones Industrial Average', 'tag': 'broad'},
    'XLE': {'label': 'Energy Select Sector SPDR (XLE)', 'tag': 'energy'},
    'XLK': {'label': 'Technology Select Sector SPDR (XLK)', 'tag': 'tech'},
    'ARKX': {'label': 'ARK Space Exploration & Innovation ETF', 'tag': 'space'},
    'GC=F': {'label': 'Gold Futures', 'tag': 'macro'},
    '^TNX': {'label': 'US 10-Year Treasury Yield', 'tag': 'macro'},
}

FRED_FEDFUNDS_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"
FRED_TIMEOUT_SEC = 10


def fetch_index_snapshot(period='1mo', interval='1d'):
    """
    Fetch recent daily history for tracked indices/assets.

    Returns: dict ticker -> {'label', 'tag', 'data': DataFrame or None, 'error': str or None}
    Uses the same .dropna() guard pattern as analysis.py to avoid NaN rows
    from holidays/missing sessions breaking downstream calculations.
    """
    results = {}
    for ticker, meta in INDEX_TICKERS.items():
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.dropna()
            if df.empty:
                results[ticker] = {**meta, 'data': None, 'error': 'No data returned'}
            else:
                results[ticker] = {**meta, 'data': df, 'error': None}
        except Exception as e:
            results[ticker] = {**meta, 'data': None, 'error': str(e)}
    return results


def fetch_fed_funds_rate():
    """
    Fetch the real (effective) Fed Funds Rate from FRED's no-key CSV endpoint
    (series DFF — Effective Federal Funds Rate, daily).

    Returns: dict {'latest_date', 'latest_rate', 'prior_rate', 'change', 'series': DataFrame, 'error'}
    """
    try:
        resp = requests.get(FRED_FEDFUNDS_URL, timeout=FRED_TIMEOUT_SEC)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        # FRED csv columns: observation_date, DFF (column name varies by series id casing)
        df.columns = [c.strip() for c in df.columns]
        date_col = df.columns[0]
        rate_col = df.columns[1]
        df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce')
        df = df.dropna()
        df[date_col] = pd.to_datetime(df[date_col])

        if df.empty:
            return {'error': 'FRED returned no usable rows', 'series': None}

        latest = df.iloc[-1]
        prior = df.iloc[-2] if len(df) > 1 else latest

        return {
            'latest_date': latest[date_col].strftime('%Y-%m-%d'),
            'latest_rate': round(float(latest[rate_col]), 2),
            'prior_rate': round(float(prior[rate_col]), 2),
            'change': round(float(latest[rate_col]) - float(prior[rate_col]), 2),
            'series': df,
            'error': None,
        }
    except Exception as e:
        return {'error': str(e), 'series': None}


def fetch_market_data(period='1mo', interval='1d'):
    """Convenience wrapper: fetch both index snapshot and Fed Funds Rate together."""
    return {
        'indices': fetch_index_snapshot(period=period, interval=interval),
        'fed_funds': fetch_fed_funds_rate(),
    }


if __name__ == "__main__":
    import json
    data = fetch_market_data()
    summary = {}
    for ticker, info in data['indices'].items():
        if info['data'] is not None:
            last = info['data']['Close'].iloc[-1]
            summary[ticker] = {'label': info['label'], 'tag': info['tag'], 'last_close': round(float(last), 2)}
        else:
            summary[ticker] = {'label': info['label'], 'tag': info['tag'], 'error': info['error']}
    summary['fed_funds_rate'] = {
        k: v for k, v in data['fed_funds'].items() if k != 'series'
    }
    print(json.dumps(summary, indent=2, default=str))
