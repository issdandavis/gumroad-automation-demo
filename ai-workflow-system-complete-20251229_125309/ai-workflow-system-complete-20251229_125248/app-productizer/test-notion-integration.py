#!/usr/bin/env python3
"""
Test Notion Integration for AI Communication
"""

import requests
import json
import os
from datetime import datetime

def test_notion_integration():
    """Test sending a message to Notion database"""
    
    notion_token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('NOTION_AI_COMM_DB', '')
    
    if not notion_token or not database_id:
        print("❌ Missing environment variables:")
        print("   NOTION_TOKEN - Your Notion integration token")
        print("   NOTION_AI_COMM_DB - Your database ID")
        print("\n📖 See NOTION_SETUP_GUIDE.md for setup instructions")
        return False
    
    # Test message
    test_message = {
        "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "from_ai": "Kiro",
        "to_ai": "Test AI",
        "message": "This is a test message to verify Notion integration is working!",
        "message_type": "test",
        "priority": "normal",
        "status": "pending"
    }
    
    # Notion API payload
    notion_payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [{"text": {"content": f"{test_message['from_ai']} → {test_message['to_ai']}"}}]
            },
            "From AI": {
                "rich_text": [{"text": {"content": test_message['from_ai']}}]
            },
            "To AI": {
                "rich_text": [{"text": {"content": test_message['to_ai']}}]
            },
            "Message Type": {
                "select": {"name": test_message['message_type']}
            },
            "Priority": {
                "select": {"name": test_message['priority']}
            },
            "Status": {
                "select": {"name": test_message['status']}
            },
            "Message": {
                "rich_text": [{"text": {"content": test_message['message']}}]
            },
            "Timestamp": {
                "date": {"start": test_message['timestamp']}
            },
            "Message ID": {
                "rich_text": [{"text": {"content": test_message['id']}}]
            }
        }
    }
    
    # Send to Notion
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=notion_payload
        )
        
        if response.status_code == 200:
            print("✅ Notion integration test successful!")
            print(f"   Message ID: {test_message['id']}")
            print(f"   Page created in Notion database")
            return True
        else:
            print(f"❌ Notion API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Notion integration: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Notion Integration...")
    test_notion_integration()
