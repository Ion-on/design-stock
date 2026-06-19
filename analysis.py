import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class StockAnalyzer:
    """Advanced stock analysis engine for swing trading"""

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.data = None
        self.fundamentals = None

    def fetch_data(self, period='3mo', interval='1d'):
        """Fetch historical data"""
        try:
            df = yf.download(self.ticker, period=period, interval=interval, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            self.data = df
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

    def fetch_info(self):
        """Fetch fundamental info"""
        try:
            ticker = yf.Ticker(self.ticker)
            self.fundamentals = ticker.info
            return self.fundamentals
        except Exception as e:
            print(f"Error fetching info: {e}")
            return {}

    def calculate_momentum(self):
        """Calculate momentum indicators"""
        if self.data is None:
            return {}

        df = self.data.copy()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal

        # Bollinger Bands
        sma20 = df['Close'].rolling(window=20).mean()
        std20 = df['Close'].rolling(window=20).std()
        bb_upper = sma20 + (std20 * 2)
        bb_lower = sma20 - (std20 * 2)

        # Stochastic
        low14 = df['Low'].rolling(window=14).min()
        high14 = df['High'].rolling(window=14).max()
        k = 100 * ((df['Close'] - low14) / (high14 - low14))
        d = k.rolling(window=3).mean()

        return {
            'rsi': rsi.iloc[-1],
            'macd': macd.iloc[-1],
            'macd_signal': signal.iloc[-1],
            'macd_hist': histogram.iloc[-1],
            'bb_upper': bb_upper.iloc[-1],
            'bb_middle': sma20.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'stoch_k': k.iloc[-1],
            'stoch_d': d.iloc[-1]
        }

    def calculate_performance(self):
        """Calculate performance metrics"""
        if self.data is None:
            return {}

        df = self.data.copy()
        current = df['Close'].iloc[-1]

        # Returns
        return_1d = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100 if len(df) > 1 else 0
        return_5d = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100 if len(df) > 5 else 0
        return_1m = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100 if len(df) > 0 else 0

        # Volatility
        daily_returns = df['Close'].pct_change()
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized

        # Highest and Lowest
        high_52w = df['High'].max()
        low_52w = df['Low'].min()

        return {
            'return_1d': round(return_1d, 2),
            'return_5d': round(return_5d, 2),
            'return_1m': round(return_1m, 2),
            'volatility': round(volatility, 2),
            'high_52w': round(high_52w, 2),
            'low_52w': round(low_52w, 2),
            'current_price': round(current, 2)
        }

    def calculate_support_resistance(self):
        """Calculate pivot points and support/resistance"""
        if self.data is None:
            return {}

        df = self.data.copy()
        h = df['High'].iloc[-1]
        l = df['Low'].iloc[-1]
        c = df['Close'].iloc[-1]

        # Pivot Points
        pivot = (h + l + c) / 3
        r1 = (2 * pivot) - l
        r2 = pivot + (h - l)
        s1 = (2 * pivot) - h
        s2 = pivot - (h - l)

        return {
            'pivot': round(pivot, 2),
            'resistance_1': round(r1, 2),
            'resistance_2': round(r2, 2),
            'support_1': round(s1, 2),
            'support_2': round(s2, 2)
        }

    def calculate_factors(self):
        """Identify key factors currently driving the stock price"""
        if self.data is None:
            return []

        df = self.data.copy()
        momentum = self.calculate_momentum()
        perf = self.calculate_performance()

        factors = []

        # Trend vs moving averages
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma50 = df['Close'].rolling(window=min(50, len(df))).mean().iloc[-1]
        price = df['Close'].iloc[-1]

        if price > sma20 > sma50:
            factors.append({
                'factor': 'Trend (SMA20/SMA50)',
                'direction': 'bullish',
                'detail': f'ราคา (${price:.2f}) อยู่เหนือ SMA20 (${sma20:.2f}) และ SMA50 (${sma50:.2f}) — แนวโน้มขาขึ้นระยะสั้น'
            })
        elif price < sma20 < sma50:
            factors.append({
                'factor': 'Trend (SMA20/SMA50)',
                'direction': 'bearish',
                'detail': f'ราคา (${price:.2f}) อยู่ใต้ SMA20 (${sma20:.2f}) และ SMA50 (${sma50:.2f}) — แนวโน้มขาลงระยะสั้น'
            })
        else:
            factors.append({
                'factor': 'Trend (SMA20/SMA50)',
                'direction': 'neutral',
                'detail': f'ราคาแกว่งตัวรอบเส้นค่าเฉลี่ย ยังไม่มีทิศทางชัดเจน'
            })

        # RSI
        rsi = momentum.get('rsi', 50)
        if rsi > 70:
            factors.append({'factor': 'RSI (14)', 'direction': 'bearish',
                             'detail': f'RSI = {rsi:.1f} เข้าเขต Overbought เสี่ยงพักฐานระยะสั้น'})
        elif rsi < 30:
            factors.append({'factor': 'RSI (14)', 'direction': 'bullish',
                             'detail': f'RSI = {rsi:.1f} เข้าเขต Oversold มีโอกาสเด้งกลับ'})
        else:
            factors.append({'factor': 'RSI (14)', 'direction': 'neutral',
                             'detail': f'RSI = {rsi:.1f} อยู่ในช่วงปกติ ไม่มี signal ชัดเจน'})

        # MACD
        macd, sig = momentum.get('macd', 0), momentum.get('macd_signal', 0)
        if macd > sig:
            factors.append({'factor': 'MACD', 'direction': 'bullish',
                             'detail': f'MACD ({macd:.3f}) ตัดขึ้นเหนือ Signal ({sig:.3f}) — โมเมนตัมเชิงบวก'})
        else:
            factors.append({'factor': 'MACD', 'direction': 'bearish',
                             'detail': f'MACD ({macd:.3f}) ต่ำกว่า Signal ({sig:.3f}) — โมเมนตัมเชิงลบ'})

        # Volume
        avg_vol = df['Volume'].rolling(window=20).mean().iloc[-1]
        curr_vol = df['Volume'].iloc[-1]
        vol_ratio = curr_vol / avg_vol if avg_vol else 1
        if vol_ratio > 1.5:
            factors.append({'factor': 'Volume', 'direction': 'bullish' if perf.get('return_1d', 0) >= 0 else 'bearish',
                             'detail': f'วอลุ่มวันนี้สูงกว่าค่าเฉลี่ย 20 วัน {vol_ratio:.1f}x — มีแรงซื้อ/ขายผิดปกติเข้ามา ยืนยันการเคลื่อนไหวราคา'})
        else:
            factors.append({'factor': 'Volume', 'direction': 'neutral',
                             'detail': f'วอลุ่มปกติ ({vol_ratio:.1f}x ของค่าเฉลี่ย) ยังไม่มีสัญญาณเงินไหลเข้าผิดปกติ'})

        # Bollinger position
        bb_upper, bb_lower = momentum.get('bb_upper'), momentum.get('bb_lower')
        if bb_upper and bb_lower:
            if price >= bb_upper:
                factors.append({'factor': 'Bollinger Bands', 'direction': 'bearish',
                                 'detail': 'ราคาแตะกรอบบน Bollinger Band — มักเกิดการพักฐานหรือ Sideways ใน 1-2 วันถัดไป'})
            elif price <= bb_lower:
                factors.append({'factor': 'Bollinger Bands', 'direction': 'bullish',
                                 'detail': 'ราคาแตะกรอบล่าง Bollinger Band — มีโอกาสรีบาวด์ระยะสั้น'})

        # Volatility
        vol = perf.get('volatility', 0)
        if vol > 50:
            factors.append({'factor': 'Volatility', 'direction': 'bearish',
                             'detail': f'Volatility สูง ({vol:.1f}% ต่อปี) — ความเสี่ยงสวิงราคาแรงทั้งสองทาง ควรคุม position size'})

        # Proximity to support/resistance
        sr = self.calculate_support_resistance()
        if sr:
            dist_r1 = abs(price - sr['resistance_1']) / price * 100
            dist_s1 = abs(price - sr['support_1']) / price * 100
            if dist_r1 < 1:
                factors.append({'factor': 'Resistance Zone', 'direction': 'bearish',
                                 'detail': f"ราคาใกล้แนวต้าน R1 (${sr['resistance_1']}) มาก — แรงขายอาจเพิ่มขึ้น"})
            if dist_s1 < 1:
                factors.append({'factor': 'Support Zone', 'direction': 'bullish',
                                 'detail': f"ราคาใกล้แนวรับ S1 (${sr['support_1']}) มาก — อาจมีแรงซื้อกลับเข้ามา"})

        return factors

    def predict_next_day(self):
        """Forecast direction and expected range for the next trading session"""
        if self.data is None:
            return {}

        df = self.data.copy()
        momentum = self.calculate_momentum()
        perf = self.calculate_performance()
        signal = self.generate_signal()
        price = df['Close'].iloc[-1]

        score = signal.get('score', 0)

        # Daily volatility (sigma) derived from annualized volatility
        daily_sigma_pct = perf.get('volatility', 20) / np.sqrt(252)

        # Direction from combined score + short trend
        sma5 = df['Close'].rolling(window=5).mean().iloc[-1]
        trend_bias = 1 if price > sma5 else -1
        composite = score + trend_bias

        if composite >= 2:
            direction = 'UP'
            confidence = 'High' if composite >= 3 else 'Medium'
            expected_move_pct = daily_sigma_pct * 0.8
        elif composite <= -2:
            direction = 'DOWN'
            confidence = 'High' if composite <= -3 else 'Medium'
            expected_move_pct = -daily_sigma_pct * 0.8
        elif composite > 0:
            direction = 'UP'
            confidence = 'Low'
            expected_move_pct = daily_sigma_pct * 0.4
        elif composite < 0:
            direction = 'DOWN'
            confidence = 'Low'
            expected_move_pct = -daily_sigma_pct * 0.4
        else:
            direction = 'SIDEWAYS'
            confidence = 'Low'
            expected_move_pct = 0

        target_price = price * (1 + expected_move_pct / 100)
        range_low = price * (1 - daily_sigma_pct / 100)
        range_high = price * (1 + daily_sigma_pct / 100)

        return {
            'direction': direction,
            'confidence': confidence,
            'expected_move_pct': round(expected_move_pct, 2),
            'target_price': round(target_price, 2),
            'range_low': round(range_low, 2),
            'range_high': round(range_high, 2),
            'composite_score': composite,
            'rationale': f"คะแนนสัญญาณรวม {composite} (Trading score {score} + Trend bias {trend_bias:+d}) "
                         f"และ Volatility รายวัน ~{daily_sigma_pct:.2f}% บ่งชี้ทิศทาง {direction} "
                         f"ด้วยความเชื่อมั่นระดับ {confidence} สำหรับการซื้อขายวันถัดไป"
        }

    def generate_signal(self):
        """Generate trading signal"""
        momentum = self.calculate_momentum()

        signals = []
        score = 0

        # RSI Signal
        if momentum.get('rsi', 50) > 70:
            signals.append("RSI: OVERBOUGHT ⚠️")
            score -= 1
        elif momentum.get('rsi', 50) < 30:
            signals.append("RSI: OVERSOLD ✅")
            score += 2

        # MACD Signal
        if momentum.get('macd', 0) > momentum.get('macd_signal', 0):
            signals.append("MACD: BULLISH ↗️")
            score += 1
        else:
            signals.append("MACD: BEARISH ↘️")
            score -= 1

        # Stochastic Signal
        stoch_k = momentum.get('stoch_k', 50)
        if stoch_k > 80:
            signals.append("Stochastic: OVERBOUGHT")
            score -= 1
        elif stoch_k < 20:
            signals.append("Stochastic: OVERSOLD")
            score += 1

        # Generate recommendation
        if score >= 2:
            recommendation = "🟢 STRONG BUY"
        elif score >= 1:
            recommendation = "🟢 BUY"
        elif score >= -1:
            recommendation = "🟡 HOLD"
        elif score >= -2:
            recommendation = "🔴 SELL"
        else:
            recommendation = "🔴 STRONG SELL"

        return {
            'signals': signals,
            'recommendation': recommendation,
            'score': score
        }

    def get_full_analysis(self):
        """Get complete analysis report"""
        self.fetch_data()
        self.fetch_info()

        analysis = {
            'ticker': self.ticker,
            'timestamp': datetime.now().isoformat(),
            'performance': self.calculate_performance(),
            'momentum': self.calculate_momentum(),
            'support_resistance': self.calculate_support_resistance(),
            'signal': self.generate_signal(),
            'factors': self.calculate_factors(),
            'prediction': self.predict_next_day(),
            'info': {
                'name': self.fundamentals.get('longName', 'N/A'),
                'sector': self.fundamentals.get('sector', 'N/A'),
                'industry': self.fundamentals.get('industry', 'N/A'),
                'market_cap': self.fundamentals.get('marketCap', 'N/A'),
                'pe_ratio': self.fundamentals.get('trailingPE', 'N/A'),
                'dividend_yield': self.fundamentals.get('dividendYield', 'N/A'),
                'description': self.fundamentals.get('longBusinessSummary', 'N/A')[:300]
            }
        }

        return analysis

    def to_json(self):
        """Export analysis to JSON"""
        return json.dumps(self.get_full_analysis(), indent=2, default=str)


if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

    analyzer = StockAnalyzer(ticker)
    print(analyzer.to_json())
