#!/usr/bin/env python3
"""
Test Zapier Webhook for AI Communication
"""

import requests
import json
import os
from datetime import datetime

def test_zapier_webhook():
    """Test sending a message to Zapier webhook"""
    
    webhook_url = os.getenv('ZAPIER_AI_COMM_WEBHOOK', '')
    
    if not webhook_url:
        print("❌ Missing environment variable:")
        print("   ZAPIER_AI_COMM_WEBHOOK - Your Zapier webhook URL")
        print("\n📖 See ZAPIER_SETUP_GUIDE.md for setup instructions")
        return False
    
    # Test message
    test_message = {
        "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "from_ai": "Kiro",
        "to_ai": "Test AI",
        "message": "This is a test message to verify Zapier webhook is working!",
        "message_type": "test",
        "priority": "normal",
        "status": "pending"
    }
    
    try:
        response = requests.post(webhook_url, json=test_message)
        
        if response.status_code == 200:
            print("✅ Zapier webhook test successful!")
            print(f"   Message ID: {test_message['id']}")
            print(f"   Check your Zapier dashboard for the triggered action")
            return True
        else:
            print(f"❌ Zapier webhook error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Zapier webhook: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Zapier Webhook...")
    test_zapier_webhook()
