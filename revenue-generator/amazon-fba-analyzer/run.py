#!/usr/bin/env python3
"""
Amazon FBA Profit Analyzer - Complete Launch Script
Run this to start the product research tool
"""

import os
import sys
from main import app

if __name__ == '__main__':
    print("🚀 Starting Amazon FBA Profit Analyzer...")
    print("💰 Professional Research Tool - $297 Value")
    print("🌐 Web Interface: http://localhost:5001")
    print("📊 Real Amazon API Integration")
    print("💡 Advanced Profit Calculations")
    print("-" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 FBA analyzer stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)