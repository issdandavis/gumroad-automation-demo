#!/usr/bin/env python3
"""
Crypto Trading Bot - Complete Launch Script
Run this to start the trading bot with web interface
"""

import os
import sys
from trading_engine import app, socketio

if __name__ == '__main__':
    print("🚀 Starting Crypto Trading Bot...")
    print("💰 Professional Trading System - $497 Value")
    print("🌐 Web Interface: http://localhost:5002")
    print("📊 Real-time Dashboard Available")
    print("⚠️  Demo Mode: Uses sandbox trading")
    print("-" * 50)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5002, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Trading bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)