import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import feedparser
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURATION ---
TICKER_SYMBOL = "ASTS"
VOLUME_SPIKE_THRESHOLD = 2.0  # แจ้งเตือนเมื่อ Volume สูงกว่าค่าเฉลี่ย 2 เท่า
UPDATE_INTERVAL = 60          # อัปเดตข้อมูลทุก 60 วินาที

st.set_page_config(page_title=f"{TICKER_SYMBOL} Trading Dashboard", layout="wide")

# --- FUNCTIONS ---

def get_stock_data(ticker, interval='15m', period='5d'):
    \"\"\"ดึงข้อมูลหุ้นและคำนวณ RSI, MACD\"\"\"
    df = yf.download(ticker, period=period, interval=interval, progress=False)

    # คำนวณ RSI (14)
    df['RSI'] = ta.rsi(df['Close'], length=14)

    # คำนวณ MACD (12, 26, 9)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)

    return df

def check_volume_spike(df):
    \"\"\"ตรวจสอบว่า Volume ปัจจุบันสูงกว่าค่าเฉลี่ยหรือไม่\"\"\"
    avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
    curr_vol = df['Volume'].iloc[-1]
    if curr_vol > (avg_vol * VOLUME_SPIKE_THRESHOLD):
        return True, curr_vol, avg_vol
    return False, curr_vol, avg_vol

def get_news(ticker):
    \"\"\"ดึงข่าวจาก Yahoo Finance RSS Feed\"\"\"
    rss_url = f"https://finance.yahoo.com/rss/headline?q={ticker}"
    feed = feedparser.parse(rss_url)
    return feed.entries[:5] # เอา 5 ข่าวล่าสุด

# --- UI LAYOUT ---

st.title(f"🚀 {TICKER_SYMBOL} Real-time Signal Monitor")
st.markdown(f"**Strategy:** Short-term (1-3 Days) | **Update Interval:** {UPDATE_INTERVAL}s")

# สร้าง Placeholder สำหรับข้อมูลที่ต้องอัปเดตแบบ Real-time
price_placeholder = st.empty()
alert_placeholder = st.empty()
chart_placeholder = st.empty()
news_placeholder = st.empty()

# เลือก Timeframe
tf_option = st.selectbox("เลือก Timeframe เพื่อดูสัญญาณ", ["15m", "1h"], index=0)

while True:
    # 1. ดึงข้อมูล
    df = get_stock_data(TICKER_SYMBOL, interval=tf_option)
    curr_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_diff = curr_price - prev_price

    # 2. คำนวณสัญญาณ RSI / MACD
    rsi_val = df['RSI'].iloc[-1]
    macd_val = df['MACD_12_26_9'].iloc[-1]
    macd_sig = df['MACDs_12_26_9'].iloc[-1]

    # กำหนดสีและสถานะ RSI
    rsi_status = "Normal"
    rsi_color = "white"
    if rsi_val >= 70:
        rsi_status = "⚠️ OVERBOUGHT (ขาย)"
        rsi_color = "red"
    elif rsi_val <= 30:
        rsi_status = "✅ OVERSOLD (ซื้อ)"
        rsi_color = "green"

    # 3. ตรวจสอบ Volume Spike
    is_spike, c_vol, a_vol = check_volume_spike(df)

    # --- แสดงผลส่วนราคาและอินดิเคเตอร์ ---
    with price_placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${curr_price:.2f}", f"{price_diff:.2f}")
        col2.metric("RSI (14)", f"{rsi_val:.2f}", rsi_status, delta_color="normal")
        col3.metric("MACD Trend", "Bullish" if macd_val > macd_sig else "Bearish")

    # --- แสดงผลการแจ้งเตือน (Alerts) ---
    with alert_placeholder.container():
        if is_spike:
            st.error(f"🚨 **VOLUME SPIKE ALERT!** Current Volume ({c_vol:,.0f}) is {VOLUME_SPIKE_THRESHOLD}x higher than average ({a_vol:,.0f})")
        elif rsi_status != "Normal":
            st.warning(f"⚡ **Signal Alert:** {rsi_status}")

    # --- กราฟราคาและ MACD ---
    with chart_placeholder.container():
        fig = go.Figure()
        # กราฟราคา (Candlestick)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="Price"))
        fig.update_layout(title=f"{TICKER_SYMBOL} Price Action ({tf_option})",
                          xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    # --- ข่าวสารล่าสุด ---
    with news_placeholder.container():
        st.subheader("📰 Latest News Feed")
        news_items = get_news(TICKER_SYMBOL)
        for item in news_items:
            st.markdown(f"**[{item.title}]({item.link})**  \\n*Published: {item.published}*")
            st.divider()

    time.sleep(UPDATE_INTERVAL)
    st.rerun()
