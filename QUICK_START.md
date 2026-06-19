# 🚀 QUICK START GUIDE

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed yfinance pandas numpy Flask flask-cors streamlit plotly pandas-ta feedparser
```

---

## Step 2: Run the Dashboard Server

```bash
python app.py
```

**Expected output:**
```
🚀 Starting Premium Stock Analysis Dashboard
📊 Dashboard available at: http://localhost:5000
🔍 API endpoint: http://localhost:5000/api/analyze/<TICKER>
```

---

## Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

You'll see the premium NOOTTOIN dashboard! 

**Try these tickers:**
- `AAPL` - Apple
- `TSLA` - Tesla
- `MSFT` - Microsoft
- `AMD` - AMD
- `NVDA` - NVIDIA

---

## Alternative: CLI Analysis (Command Line)

In a different terminal, while the server is running:

```bash
# Get analysis in terminal
python brief_cli.py AAPL

# Save analysis to file
python brief_cli.py TSLA --save
```

Saved briefs go to: `briefs/TICKER.md`

---

## 📊 What You Get

### Dashboard Features
✅ Real-time stock analysis  
✅ Beautiful dark theme with gold/green accents  
✅ Technical indicators (RSI, MACD, Bollinger Bands, Stochastic)  
✅ Support & Resistance levels  
✅ AI trading recommendations  
✅ Performance metrics (1d, 5d, 1m returns)  
✅ Company information  

### API Endpoints (for developers)
```
GET /api/analyze/AAPL          → Full JSON analysis
GET /api/briefs/TSLA           → Formatted brief
GET /health                    → Server health check
```

---

## 🐛 Troubleshooting

### "No module named 'Flask'"
```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```
Then open: `http://localhost:5001`

### "No data found for ticker"
Make sure:
1. Ticker is valid (e.g., `AAPL`, not `APP`)
2. You have internet connection
3. Yahoo Finance is accessible

### Dashboard won't load
1. Check that Flask server is running
2. Verify no errors in terminal
3. Try a different ticker
4. Clear browser cache (Ctrl+Shift+Del)

---

## 📁 Project Structure

```
.
├── app.py                    ← Run this!
├── dashboard_premium.html    ← This opens in browser
├── analysis.py               ← Core analysis engine
├── brief_cli.py              ← CLI tool
├── requirements.txt          ← Install this
├── README_SETUP.md           ← Full documentation
└── briefs/                   ← Saved analysis files
```

---

## 💡 Pro Tips

1. **Bookmark the dashboard** in your browser for quick access

2. **Use saved briefs** for tracking analysis over time:
   ```bash
   python brief_cli.py AAPL --save
   # Opens: briefs/AAPL.md
   ```

3. **Analyze multiple stocks** by entering different tickers in the dashboard

4. **Check the API** directly in a new terminal:
   ```bash
   curl http://localhost:5000/api/analyze/AAPL
   ```

5. **Use in scripts** - the Flask API returns JSON:
   ```python
   import requests
   data = requests.get('http://localhost:5000/api/analyze/AAPL').json()
   print(data['signal']['recommendation'])
   ```

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Start the server (`python app.py`)
3. ✅ Open `http://localhost:5000` in browser
4. ✅ Enter a ticker and click "Analyze"
5. ✅ Explore the dashboard!

---

**Ready to analyze? Start with Step 1! 🚀**
