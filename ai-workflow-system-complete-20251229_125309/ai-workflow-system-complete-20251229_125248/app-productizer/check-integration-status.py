#!/usr/bin/env python3
"""
Check AI Communication Integration Status
"""

import os
import requests
from datetime import datetime

def check_integrations():
    """Check status of all AI communication integrations"""
    
    print("🔍 AI COMMUNICATION INTEGRATION STATUS")
    print("=" * 50)
    
    # Check environment variables
    integrations = {
        "GitHub": os.getenv('GITHUB_TOKEN', ''),
        "Notion": os.getenv('NOTION_TOKEN', ''),
        "Notion DB": os.getenv('NOTION_AI_COMM_DB', ''),
        "Zapier": os.getenv('ZAPIER_AI_COMM_WEBHOOK', '')
    }
    
    print("\n📋 Environment Variables:")
    for name, value in integrations.items():
        status = "✅ Set" if value else "❌ Missing"
        print(f"   {name}: {status}")
    
    # Check file system channels
    print("\n📁 File System Channels:")
    directories = [
        "AI_MESSAGES",
        "AI_MESSAGES/inboxes",
        "AI_GITHUB_ISSUES",
        "AI_NOTION_MESSAGES",
        "AI_ZAPIER_WEBHOOKS",
        "AI_EMAIL_MESSAGES"
    ]
    
    for directory in directories:
        exists = os.path.exists(directory)
        status = "✅ Exists" if exists else "❌ Missing"
        print(f"   {directory}: {status}")
    
    # Check bulletin board
    print("\n📄 Message Board:")
    bulletin_exists = os.path.exists("AI_BULLETIN_BOARD.json")
    status = "✅ Active" if bulletin_exists else "❌ Missing"
    print(f"   AI_BULLETIN_BOARD.json: {status}")
    
    if bulletin_exists:
        try:
            import json
            with open("AI_BULLETIN_BOARD.json", 'r') as f:
                bulletin = json.load(f)
            message_count = len(bulletin.get('messages', []))
            print(f"   Messages: {message_count}")
        except:
            print("   Messages: Error reading")
    
    # Check session log
    print("\n📊 Session Tracking:")
    session_exists = os.path.exists("AI_SESSION_LOG.json")
    status = "✅ Active" if session_exists else "❌ Missing"
    print(f"   AI_SESSION_LOG.json: {status}")
    
    # Integration recommendations
    print("\n💡 Next Steps:")
    
    if not integrations["Notion"]:
        print("   - Set up Notion integration (see NOTION_SETUP_GUIDE.md)")
    
    if not integrations["Zapier"]:
        print("   - Set up Zapier webhook (see ZAPIER_SETUP_GUIDE.md)")
    
    if not integrations["GitHub"]:
        print("   - Set up GitHub token (see GITHUB_SETUP_GUIDE.md)")
    
    if all(integrations.values()):
        print("   - All integrations configured! Run full communication test")
    
    print("\n🎯 Ready Channels:")
    ready_channels = []
    if bulletin_exists:
        ready_channels.append("JSON Bulletin Board")
    if os.path.exists("AI_MESSAGES"):
        ready_channels.append("File System")
    if os.path.exists("AI_EMAIL_MESSAGES"):
        ready_channels.append("Email Templates")
    if integrations["GitHub"]:
        ready_channels.append("GitHub Issues")
    if integrations["Notion"] and integrations["Notion DB"]:
        ready_channels.append("Notion Database")
    if integrations["Zapier"]:
        ready_channels.append("Zapier Webhooks")
    
    for channel in ready_channels:
        print(f"   ✅ {channel}")
    
    print(f"\n📈 Total Ready Channels: {len(ready_channels)}/6")

if __name__ == '__main__':
    check_integrations()
