#!/usr/bin/env python3
"""
Shopify Mobile Manager - Complete Launch Script
Run this to start the Shopify management application
"""

import os
import sys
from app import app, db

if __name__ == '__main__':
    print("🚀 Starting Shopify Mobile Manager...")
    print("💰 Professional Shopify Tool - $197 Value")
    print("🌐 Web Interface: http://localhost:5000")
    print("📱 Mobile Optimized Dashboard")
    print("🔗 Real Shopify API Integration")
    print("-" * 50)
    
    # Initialize database
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shopify manager stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)