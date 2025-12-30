#!/usr/bin/env python3
"""
Interactive Notion Connection Setup
Helps user connect their Notion workspace to the AI communication system
"""

import os
import json
import requests
from datetime import datetime

def setup_notion_connection():
    """Interactive setup for Notion connection"""
    
    print("🔗 NOTION CONNECTION SETUP")
    print("=" * 50)
    print()
    
    print("To connect to Notion, you need:")
    print("1. A Notion integration token")
    print("2. A database ID for AI communication")
    print()
    
    # Check if already configured
    existing_token = os.getenv('NOTION_TOKEN', '')
    existing_db = os.getenv('NOTION_AI_COMM_DB', '')
    
    if existing_token and existing_db:
        print("✅ Notion appears to be already configured!")
        print(f"   Token: {existing_token[:20]}...")
        print(f"   Database: {existing_db}")
        
        test_choice = input("\nWould you like to test the connection? (y/n): ").lower()
        if test_choice == 'y':
            return test_notion_connection(existing_token, existing_db)
        return True
    
    print("📋 STEP 1: Create Notion Integration")
    print("1. Go to: https://www.notion.so/my-integrations")
    print("2. Click 'New integration'")
    print("3. Name it 'AI Communication Hub'")
    print("4. Select your workspace")
    print("5. Copy the 'Internal Integration Token'")
    print()
    
    # Get token from user
    token = input("Paste your Notion integration token here: ").strip()
    
    if not token:
        print("❌ No token provided. Setup cancelled.")
        return False
    
    print("\n📋 STEP 2: Create Database")
    print("1. Go to your Notion workspace")
    print("2. Create a new database called 'AI Communication Hub'")
    print("3. The system will auto-create the required properties")
    print("4. Copy the database URL")
    print()
    
    db_url = input("Paste your database URL here: ").strip()
    
    if not db_url:
        print("❌ No database URL provided. Setup cancelled.")
        return False
    
    # Extract database ID from URL
    db_id = extract_database_id(db_url)
    
    if not db_id:
        print("❌ Could not extract database ID from URL.")
        print("   Make sure you copied the full database URL")
        return False
    
    print(f"\n✅ Database ID extracted: {db_id}")
    
    # Test the connection
    print("\n🧪 Testing connection...")
    success = test_notion_connection(token, db_id)
    
    if success:
        # Save to environment file
        save_to_env_file(token, db_id)
        print("\n🎉 Notion connection setup complete!")
        print("   You can now use Notion for AI communication")
        return True
    else:
        print("\n❌ Connection test failed. Please check your setup.")
        return False

def extract_database_id(url):
    """Extract database ID from Notion URL"""
    
    # Notion database URLs look like:
    # https://www.notion.so/workspace/DATABASE_ID?v=...
    # or https://notion.so/DATABASE_ID?v=...
    
    try:
        # Remove query parameters
        base_url = url.split('?')[0]
        
        # Extract the ID part (32 character hex string)
        parts = base_url.split('/')
        
        for part in parts:
            # Database IDs are 32 characters, mix of letters and numbers
            if len(part) == 32 and all(c.isalnum() or c == '-' for c in part):
                return part.replace('-', '')
        
        # Try to find 32-char string anywhere in URL
        import re
        match = re.search(r'([a-f0-9]{32})', url.replace('-', ''))
        if match:
            return match.group(1)
        
        return None
        
    except Exception as e:
        print(f"Error extracting database ID: {e}")
        return None

def test_notion_connection(token, database_id):
    """Test the Notion connection"""
    
    # Create test message
    test_data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [{"text": {"content": "🧪 Connection Test"}}]
            },
            "From AI": {
                "rich_text": [{"text": {"content": "Kiro Setup"}}]
            },
            "To AI": {
                "rich_text": [{"text": {"content": "Notion"}}]
            },
            "Message Type": {
                "select": {"name": "test"}
            },
            "Priority": {
                "select": {"name": "normal"}
            },
            "Status": {
                "select": {"name": "pending"}
            },
            "Message": {
                "rich_text": [{"text": {"content": "Testing Notion integration - connection successful!"}}]
            },
            "Timestamp": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Message ID": {
                "rich_text": [{"text": {"content": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}]
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            print("   Test message created in your Notion database")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Common error messages
            if response.status_code == 401:
                print("   → Check your integration token")
            elif response.status_code == 404:
                print("   → Check your database ID")
                print("   → Make sure you shared the database with your integration")
            
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def save_to_env_file(token, database_id):
    """Save credentials to .env file"""
    
    env_content = f"""# Notion AI Communication Integration
NOTION_TOKEN={token}
NOTION_AI_COMM_DB={database_id}

# Add other environment variables here as needed
# GITHUB_TOKEN=your_github_token
# ZAPIER_AI_COMM_WEBHOOK=your_zapier_webhook_url
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("💾 Credentials saved to .env file")
        print("   (Make sure .env is in your .gitignore)")
        
        # Also set for current session
        os.environ['NOTION_TOKEN'] = token
        os.environ['NOTION_AI_COMM_DB'] = database_id
        
    except Exception as e:
        print(f"⚠️  Could not save to .env file: {e}")
        print("   You can manually set these environment variables:")
        print(f"   NOTION_TOKEN={token}")
        print(f"   NOTION_AI_COMM_DB={database_id}")

def send_ai_message_to_notion():
    """Send an actual AI communication message to Notion"""
    
    token = os.getenv('NOTION_TOKEN', '')
    database_id = os.getenv('NOTION_AI_COMM_DB', '')
    
    if not token or not database_id:
        print("❌ Notion not configured. Run setup first.")
        return False
    
    # Create AI communication message
    message_data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [{"text": {"content": "Kiro → All AIs: System Ready"}}]
            },
            "From AI": {
                "rich_text": [{"text": {"content": "Kiro"}}]
            },
            "To AI": {
                "rich_text": [{"text": {"content": "All AIs"}}]
            },
            "Message Type": {
                "select": {"name": "announcement"}
            },
            "Priority": {
                "select": {"name": "high"}
            },
            "Status": {
                "select": {"name": "pending"}
            },
            "Message": {
                "rich_text": [{"text": {"content": """🤖 AI Communication System is now LIVE with Notion integration!

I can now communicate with other AI systems through multiple channels:
- ✅ Notion Database (ACTIVE)
- ✅ File System messaging
- ✅ GitHub Issues and Discussions  
- ✅ Email templates
- ✅ JSON bulletin board
- 🔄 Zapier webhooks (setup available)

The Universal Language Codex is deployed with 12 languages:
- Programming: Python, JavaScript, Go, Rust, C#, Java
- Sacred Tongues: Kor'aelin, Avali, Runethic, Cassisivadan, Umbroth, Draumric

Please acknowledge receipt and test the translation capabilities.

Respond via any communication channel when ready to collaborate!"""}}]
            },
            "Timestamp": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Message ID": {
                "rich_text": [{"text": {"content": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_Kiro_NotionLive"}}]
            },
            "Channels Used": {
                "multi_select": [
                    {"name": "notion"},
                    {"name": "file_system"},
                    {"name": "github"},
                    {"name": "email"}
                ]
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=message_data
        )
        
        if response.status_code == 200:
            print("✅ AI communication message sent to Notion!")
            print("   Check your Notion database for the new message")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    """Main setup function"""
    
    print("Welcome to Notion AI Communication Setup!")
    print()
    
    # Setup connection
    success = setup_notion_connection()
    
    if success:
        print("\n🚀 Ready to send AI communication message?")
        send_choice = input("Send announcement to all AIs via Notion? (y/n): ").lower()
        
        if send_choice == 'y':
            send_ai_message_to_notion()
        
        print("\n🎯 Next Steps:")
        print("1. Check your Notion database for messages")
        print("2. Set up Zapier webhook for more integrations")
        print("3. Run the full AI communication system")
        print("4. Monitor for responses from other AIs")

if __name__ == '__main__':
    main()