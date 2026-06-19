import yfinance as yf
import json
import sys

def get_stock_data(ticker_symbol):
    try:
        # Initialize the ticker
        ticker = yf.Ticker(ticker_symbol)

        # Get the most recent historical data (last 2 days to calculate change)
        hist = ticker.history(period="2d")

        if hist.empty:
            return {"error": f"No data found for ticker {ticker_symbol}"}

        # Current price is the last close price in the history
        current_price = hist['Close'].iloc[-1]

        # Previous close to calculate percentage change
        if len(hist) > 1:
            prev_close = hist['Close'].iloc[-2]
            pct_change = ((current_price - prev_close) / prev_close) * 100
        else:
            pct_change = 0.0  # Not enough data to calculate change

        # Volume of the most recent day
        volume = hist['Volume'].iloc[-1]

        # Prepare output data
        data = {
            "ticker": ticker_symbol.upper(),
            "last_price": round(current_price, 2),
            "volume": int(volume),
            "pct_change": round(pct_change, 2)
        }

        return data

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Use ticker from command line argument, or default to ASTS
    symbol = sys.argv[1] if len(sys.argv) > 1 else "ASTS"

    result = get_stock_data(symbol)
    print(json.dumps(result, indent=4))
