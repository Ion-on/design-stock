#!/usr/bin/env python3
"""
Premium Stock Analysis Dashboard Backend
Serves the dashboard and provides API endpoints for stock analysis
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from analysis import StockAnalyzer
import os

app = Flask(__name__)
CORS(app)

# Load the dashboard HTML
DASHBOARD_HTML = open('dashboard_premium.html', 'r', encoding='utf-8').read()


@app.route('/')
def dashboard():
    """Serve the premium dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/analyze/<ticker>', methods=['GET'])
def analyze_stock(ticker):
    """
    API endpoint to analyze a stock
    Returns comprehensive analysis as JSON
    """
    try:
        ticker = ticker.upper().strip()

        if not ticker or len(ticker) > 5:
            return jsonify({'error': 'Invalid ticker symbol'}), 400

        analyzer = StockAnalyzer(ticker)
        analysis = analyzer.get_full_analysis()

        return jsonify(analysis), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/briefs/<ticker>', methods=['GET'])
def get_brief(ticker):
    """
    API endpoint to get formatted brief
    Returns formatted text brief
    """
    try:
        ticker = ticker.upper().strip()

        if not ticker or len(ticker) > 5:
            return jsonify({'error': 'Invalid ticker symbol'}), 400

        analyzer = StockAnalyzer(ticker)
        analysis = analyzer.get_full_analysis()

        # Format as brief
        from brief_cli import format_brief
        brief_text = format_brief(analysis)

        return jsonify({
            'ticker': ticker,
            'brief': brief_text,
            'timestamp': analysis['timestamp']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    # Create briefs directory if it doesn't exist
    os.makedirs('briefs', exist_ok=True)

    print("🚀 Starting Premium Stock Analysis Dashboard")
    print("📊 Dashboard available at: http://localhost:5000")
    print("🔍 API endpoint: http://localhost:5000/api/analyze/<TICKER>")
    print("\nExamples:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/api/analyze/AAPL")
    print("  - http://localhost:5000/api/briefs/TSLA")

    app.run(debug=True, host='0.0.0.0', port=5000)
