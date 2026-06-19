#!/usr/bin/env python3
"""Simple HTTP server for NOOTTOIN dashboard - no Flask required"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from analysis import StockAnalyzer
except ImportError:
    print("ERROR: yfinance and pandas not installed!")
    print("Please install: python -m pip install yfinance pandas numpy")
    sys.exit(1)


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        query = urlparse(self.path).query

        # Root - serve dashboard
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('dashboard_premium.html', 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))

        # API: Analyze stock
        elif path.startswith('/api/analyze/'):
            ticker = path.split('/api/analyze/')[-1].upper().strip()

            try:
                if not ticker or len(ticker) > 5:
                    self.send_error(400, 'Invalid ticker')
                    return

                analyzer = StockAnalyzer(ticker)
                analysis = analyzer.get_full_analysis()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(analysis, indent=2, default=str).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

        # Health check
        elif path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))

        else:
            self.send_error(404, 'Not found')

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=5000):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)

    print("\n" + "="*70)
    print("NOOTTOIN Premium Stock Dashboard")
    print("="*70)
    print(f"Dashboard: http://localhost:{port}")
    print(f"API: http://localhost:{port}/api/analyze/<TICKER>")
    print("\nServer running... (Press Ctrl+C to stop)")
    print("="*70 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        sys.exit(0)


if __name__ == '__main__':
    run_server()
