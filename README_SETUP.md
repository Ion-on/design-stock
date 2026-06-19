# NOOTTOIN - Premium Stock Analysis Platform

ระบบวิเคราะห์หุ้นสำหรับการลงทุนระยะสั้น (1-3 วัน) ที่เน้นหุ้นพลังงาน อวกาศ และเทคโนโลยี

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask backend:**
   ```bash
   python app.py
   ```
   
   Dashboard will be available at: `http://localhost:5000`

### Quick CLI Analysis

**Get detailed stock brief via command line:**

```bash
# Display analysis in terminal
python brief_cli.py AAPL

# Save analysis to file
python brief_cli.py TSLA --save
```

Saved briefs are stored in `briefs/` folder as markdown files.

---

## 📊 Features

### Premium Dashboard (`dashboard_premium.html` + `app.py`)
- **Real-time Analysis**: Input any ticker and get instant analysis
- **Beautiful UI**: Dark theme with gold/green accents (NOOTTOIN style)
- **Central Price Chart**: Circular visualization with 52W range
- **Performance Cards**: 1-day, 5-day, 1-month returns
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Stochastic
- **Support & Resistance**: Pivot point levels (R2, R1, Pivot, S1, S2)
- **Trading Signal**: AI-generated BUY/SELL/HOLD recommendations
- **Responsive Design**: Works on desktop and tablet

### CLI Brief Tool (`brief_cli.py`)
- **Single-Ticker Input**: Just provide the ticker symbol
- **Detailed Analysis**: Comprehensive formatted brief
- **File Export**: Save analysis to markdown format
- **Beautiful Formatting**: ASCII box styling with emoji indicators

### Analysis Engine (`analysis.py`)
- **StockAnalyzer Class**: Modular analysis system
- **Momentum Indicators**: RSI(14), MACD(12,26,9), Bollinger Bands, Stochastic
- **Performance Metrics**: Daily/5-day/monthly returns, volatility, 52-week range
- **Support/Resistance**: Pivot point analysis with 5 levels
- **Trading Signals**: Scoring system with clear recommendations
- **JSON Export**: Full analysis export capability

---

## 📌 Project Structure

```
.
├── app.py                      # Flask backend server
├── analysis.py                 # Core analysis engine (StockAnalyzer class)
├── brief_cli.py                # CLI tool for detailed briefs
├── dashboard_premium.html      # Premium dashboard UI
├── get_stock.py                # Simple stock data fetcher
├── dashboard.py                # Legacy Streamlit dashboard
├── briefs/                      # Saved brief files (auto-created)
├── requirements.txt            # Python dependencies
└── README_SETUP.md             # This file
```

---

## 🔗 API Endpoints

### Dashboard
```
GET http://localhost:5000/
```
Opens the premium NOOTTOIN dashboard in your browser.

### Stock Analysis API
```
GET http://localhost:5000/api/analyze/<TICKER>
```
Returns comprehensive analysis JSON.

**Example:**
```bash
curl http://localhost:5000/api/analyze/AAPL
```

**Response:**
```json
{
  "ticker": "AAPL",
  "timestamp": "2026-06-19T...",
  "performance": {
    "current_price": 123.45,
    "return_1d": 2.34,
    "return_5d": 5.67,
    "return_1m": 12.34,
    "volatility": 18.5,
    "high_52w": 199.62,
    "low_52w": 102.35
  },
  "momentum": {
    "rsi": 65.23,
    "macd": 2.1234,
    "macd_signal": 1.8901,
    "macd_hist": 0.2333,
    "bb_upper": 145.32,
    "bb_middle": 135.10,
    "bb_lower": 124.88,
    "stoch_k": 72.5,
    "stoch_d": 68.3
  },
  "support_resistance": {
    "pivot": 130.00,
    "resistance_1": 135.50,
    "resistance_2": 140.00,
    "support_1": 125.00,
    "support_2": 120.50
  },
  "signal": {
    "recommendation": "🟢 BUY",
    "score": 2,
    "signals": [
      "RSI: Normal",
      "MACD: BULLISH ↗️",
      "Stochastic: OVERBOUGHT"
    ]
  },
  "info": {
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": "3500000000000",
    "pe_ratio": 28.5,
    "dividend_yield": 0.0045,
    "description": "Apple Inc. is a technology company..."
  }
}
```

### Brief API
```
GET http://localhost:5000/api/briefs/<TICKER>
```
Returns formatted brief as text.

---

## 📈 Trading Signal System

Scores are calculated from three indicators:

| Indicator | Signal | Score |
|-----------|--------|-------|
| RSI > 70 | Overbought | -1 |
| RSI < 30 | Oversold | +2 |
| MACD > Signal | Bullish | +1 |
| MACD < Signal | Bearish | -1 |
| Stoch > 80 | Overbought | -1 |
| Stoch < 20 | Oversold | +1 |

**Recommendations:**
- Score ≥ 2: 🟢 **STRONG BUY**
- Score ≥ 1: 🟢 **BUY**
- Score ≥ -1: 🟡 **HOLD**
- Score ≥ -2: 🔴 **SELL**
- Score < -2: 🔴 **STRONG SELL**

---

## ⚙️ Configuration

### Change Default Ticker in Dashboard
Edit `dashboard_premium.html`, line with `value="AAPL"`:
```html
<input type="text" id="tickerInput" placeholder="Enter ticker (e.g., AAPL)" value="AAPL">
```

### Adjust Analysis Period
In `analysis.py`, modify the `fetch_data()` call:
```python
def fetch_data(self, period='3mo', interval='1d'):  # Change '3mo' to desired period
```

Supported periods: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

---

## 🔍 Example Usage

### Dashboard Analysis
1. Open `http://localhost:5000` in browser
2. Enter ticker (e.g., `TSLA`)
3. Click "Analyze"
4. View comprehensive analysis with charts and recommendations

### CLI Analysis
```bash
# Quick analysis
python brief_cli.py AAPL

# Save for later
python brief_cli.py TSLA --save

# Programmatic access
python analysis.py MSFT
```

---

## 📊 Supported Indicators

### Momentum
- **RSI (14)**: Relative Strength Index
- **MACD (12,26,9)**: Moving Average Convergence Divergence
- **Bollinger Bands**: Upper/Middle/Lower bands

### Trend
- **Stochastic**: %K and %D values
- **Support/Resistance**: Pivot point analysis

### Performance
- **Returns**: 1-day, 5-day, 1-month
- **Volatility**: Annualized standard deviation
- **52-Week Range**: High and low prices

---

## 🚨 Error Handling

### Invalid Ticker
```
Error: No data found for ticker INVALID
```

### Network Issues
Ensure you have internet connection for fetching data from Yahoo Finance.

### Missing Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Data Source

All data is fetched from **Yahoo Finance** via the `yfinance` library.
- Real-time price data
- Historical OHLCV data
- Company fundamentals
- Sector/industry information

---

## 📱 Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Responsive design

---

## 🎯 Next Steps

1. ✅ Run the dashboard: `python app.py`
2. ✅ Test CLI: `python brief_cli.py AAPL`
3. ✅ Analyze your favorite stocks
4. ✅ Save briefs for later reference

---

## 📝 Notes

- Strategy: Short-term swing trading (1-3 day holds)
- Focus sectors: Energy, Space, Technology
- Data refresh: Manual (click "Analyze" for latest data)
- No historical data storage (real-time fetch each time)

---

**Made for serious swing traders who understand business models.**
