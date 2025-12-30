#!/usr/bin/env python3
"""
Setup Notion and Zapier Integration for AI Communication
Creates templates and guides for connecting with user's existing accounts
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_notion_integration_guide():
    """Create Notion database setup guide"""
    
    notion_guide = """# Notion AI Communication Database Setup

## Step 1: Create Notion Database

1. Go to your Notion workspace
2. Create a new database called "AI Communication Hub"
3. Add these properties:

### Database Properties:
- **Title** (Title) - Message title
- **From AI** (Text) - Sending AI name
- **To AI** (Text) - Receiving AI name  
- **Message Type** (Select) - greeting, task, analysis, research, response
- **Priority** (Select) - low, normal, high, urgent
- **Status** (Select) - pending, read, responded, completed
- **Message** (Text) - Full message content
- **Timestamp** (Date) - When message was sent
- **Message ID** (Text) - Unique identifier
- **Channels Used** (Multi-select) - file_system, github, notion, zapier, email

## Step 2: Get Integration Token

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "AI Communication Hub"
4. Select your workspace
5. Copy the "Internal Integration Token"
6. Save it as environment variable: NOTION_TOKEN

## Step 3: Get Database ID

1. Open your AI Communication Hub database
2. Copy the URL - it looks like:
   https://notion.so/workspace/DATABASE_ID?v=...
3. Extract the DATABASE_ID (32 character string)
4. Save it as environment variable: NOTION_AI_COMM_DB

## Step 4: Share Database with Integration

1. In your database, click "Share" 
2. Click "Invite"
3. Search for "AI Communication Hub" (your integration)
4. Click "Invite"

## Step 5: Test Integration

Run the test script: python test-notion-integration.py

## Environment Variables Needed:
```
NOTION_TOKEN=secret_your_integration_token_here
NOTION_AI_COMM_DB=your_database_id_here
```
"""
    
    with open("NOTION_SETUP_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(notion_guide)
    
    print("📝 Created: NOTION_SETUP_GUIDE.md")

def create_zapier_integration_guide():
    """Create Zapier webhook setup guide"""
    
    zapier_guide = """# Zapier AI Communication Webhook Setup

## Step 1: Create Zapier Webhook

1. Go to https://zapier.com/app/zaps
2. Click "Create Zap"
3. Choose "Webhooks by Zapier" as trigger
4. Select "Catch Hook" 
5. Copy the webhook URL
6. Save it as environment variable: ZAPIER_AI_COMM_WEBHOOK

## Step 2: Suggested Zap Actions

### Option 1: Send to Slack
- Action: Slack - Send Channel Message
- Channel: #ai-communication
- Message: Format the AI message data

### Option 2: Add to Google Sheets
- Action: Google Sheets - Create Spreadsheet Row
- Spreadsheet: "AI Communication Log"
- Map fields: From AI, To AI, Message, Timestamp, etc.

### Option 3: Send Email Notifications
- Action: Email by Zapier - Send Outbound Email
- To: your-email@domain.com
- Subject: "New AI Communication: {{from_ai}} → {{to_ai}}"

### Option 4: Create Trello Cards
- Action: Trello - Create Card
- Board: "AI Communication Tasks"
- List: "Pending Messages"
- Card Name: "{{from_ai}} → {{to_ai}}: {{message_type}}"

### Option 5: Post to Discord
- Action: Discord - Send Channel Message
- Channel: #ai-communication
- Message: Format the AI message data

## Step 3: Test Webhook

1. Turn on your Zap
2. Run: python test-zapier-integration.py
3. Check if the webhook receives the test data

## Environment Variables Needed:
```
ZAPIER_AI_COMM_WEBHOOK=https://hooks.zapier.com/hooks/catch/your_webhook_id/
```

## Sample Webhook Payload:
```json
{
  "id": "msg_20251225_123456_Kiro",
  "timestamp": "2025-12-25T12:34:56.789",
  "from_ai": "Kiro",
  "to_ai": "ChatGPT", 
  "message": "Hello! Testing AI communication.",
  "message_type": "greeting",
  "priority": "normal",
  "status": "pending"
}
```
"""
    
    with open("ZAPIER_SETUP_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(zapier_guide)
    
    print("📝 Created: ZAPIER_SETUP_GUIDE.md")

def create_notion_test_script():
    """Create Notion integration test script"""
    
    notion_test = '''#!/usr/bin/env python3
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
        print("\\n📖 See NOTION_SETUP_GUIDE.md for setup instructions")
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
'''
    
    with open("test-notion-integration.py", 'w', encoding='utf-8') as f:
        f.write(notion_test)
    
    print("📝 Created: test-notion-integration.py")

def create_zapier_test_script():
    """Create Zapier webhook test script"""
    
    zapier_test = '''#!/usr/bin/env python3
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
        print("\\n📖 See ZAPIER_SETUP_GUIDE.md for setup instructions")
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
'''
    
    with open("test-zapier-integration.py", 'w', encoding='utf-8') as f:
        f.write(zapier_test)
    
    print("📝 Created: test-zapier-integration.py")

def create_github_setup_guide():
    """Create GitHub repository setup guide"""
    
    github_guide = """# GitHub AI Communication Setup

## Step 1: Create GitHub Repository (Optional)

If you want to use actual GitHub Issues for AI communication:

1. Create a new repository called "ai-communication-hub"
2. Make it public or private (your choice)
3. Enable Issues in repository settings

## Step 2: Get GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or `public_repo` (for public)
4. Copy the token
5. Save it as environment variable: GITHUB_TOKEN

## Step 3: Update Repository Info

Edit the ai-communication-hub.py file and update:
```python
self.repo_owner = "your-github-username"
self.repo_name = "ai-communication-hub"  # or your preferred repo name
```

## Step 4: Test GitHub Integration

Run: python test-github-integration.py

## Environment Variables Needed:
```
GITHUB_TOKEN=ghp_your_token_here
```

## Alternative: Manual Issue Creation

If you don't want to use the API, the system creates markdown templates in:
- AI_GITHUB_ISSUES/ directory
- Copy and paste these into GitHub Issues manually
"""
    
    with open("GITHUB_SETUP_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(github_guide)
    
    print("📝 Created: GITHUB_SETUP_GUIDE.md")

def create_integration_status_checker():
    """Create script to check all integration statuses"""
    
    status_checker = '''#!/usr/bin/env python3
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
    
    print("\\n📋 Environment Variables:")
    for name, value in integrations.items():
        status = "✅ Set" if value else "❌ Missing"
        print(f"   {name}: {status}")
    
    # Check file system channels
    print("\\n📁 File System Channels:")
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
    print("\\n📄 Message Board:")
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
    print("\\n📊 Session Tracking:")
    session_exists = os.path.exists("AI_SESSION_LOG.json")
    status = "✅ Active" if session_exists else "❌ Missing"
    print(f"   AI_SESSION_LOG.json: {status}")
    
    # Integration recommendations
    print("\\n💡 Next Steps:")
    
    if not integrations["Notion"]:
        print("   - Set up Notion integration (see NOTION_SETUP_GUIDE.md)")
    
    if not integrations["Zapier"]:
        print("   - Set up Zapier webhook (see ZAPIER_SETUP_GUIDE.md)")
    
    if not integrations["GitHub"]:
        print("   - Set up GitHub token (see GITHUB_SETUP_GUIDE.md)")
    
    if all(integrations.values()):
        print("   - All integrations configured! Run full communication test")
    
    print("\\n🎯 Ready Channels:")
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
    
    print(f"\\n📈 Total Ready Channels: {len(ready_channels)}/6")

if __name__ == '__main__':
    check_integrations()
'''
    
    with open("check-integration-status.py", 'w', encoding='utf-8') as f:
        f.write(status_checker)
    
    print("📝 Created: check-integration-status.py")

def main():
    """Create all integration setup files"""
    
    print("🔧 SETTING UP NOTION & ZAPIER INTEGRATIONS")
    print("=" * 60)
    
    # Create setup guides
    create_notion_integration_guide()
    create_zapier_integration_guide()
    create_github_setup_guide()
    
    # Create test scripts
    create_notion_test_script()
    create_zapier_test_script()
    
    # Create status checker
    create_integration_status_checker()
    
    print("\n🎉 INTEGRATION SETUP COMPLETE!")
    print("=" * 60)
    print("Created files:")
    print("📖 NOTION_SETUP_GUIDE.md - Step-by-step Notion setup")
    print("📖 ZAPIER_SETUP_GUIDE.md - Step-by-step Zapier setup")
    print("📖 GITHUB_SETUP_GUIDE.md - GitHub repository setup")
    print("🧪 test-notion-integration.py - Test Notion connection")
    print("🧪 test-zapier-integration.py - Test Zapier webhook")
    print("🔍 check-integration-status.py - Check all integrations")
    
    print("\n💡 Next Steps:")
    print("1. Follow the setup guides to configure your accounts")
    print("2. Set environment variables for your tokens/webhooks")
    print("3. Run the test scripts to verify connections")
    print("4. Use check-integration-status.py to monitor setup")
    print("5. Run the full AI communication system!")

if __name__ == '__main__':
    main()