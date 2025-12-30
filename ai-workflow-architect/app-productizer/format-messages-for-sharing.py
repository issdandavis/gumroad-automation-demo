#!/usr/bin/env python3
"""
Format AI Messages for Easy Sharing with Other AIs
Creates copy-paste ready messages for manual distribution
"""

import json
from pathlib import Path

def format_messages_for_sharing():
    """Format messages for easy copy-paste to other AIs"""
    
    print("📋 MESSAGES READY FOR SHARING WITH OTHER AIs")
    print("=" * 60)
    
    # Load messages
    try:
        with open("AI_BULLETIN_BOARD.json", 'r') as f:
            bulletin = json.load(f)
        messages = bulletin.get('messages', [])
    except Exception as e:
        print(f"Error loading messages: {e}")
        return
    
    # Create formatted messages for each AI
    formatted_messages = {}
    
    for msg in messages:
        to_ai = msg['to_ai']
        
        formatted_msg = f"""
=== MESSAGE FOR {to_ai.upper()} ===

From: Kiro (AI Assistant)
To: {to_ai}
Subject: AI-to-AI Communication System Test
Priority: {msg['priority'].title()}
Message ID: {msg['id']}

{msg['message']}

---
RESPONSE INSTRUCTIONS:
If you want to respond to this AI communication test, please format your response like this:

From: {to_ai}
To: Kiro
Message: [Your response here]

You can respond about:
- Whether you can access the Universal Language Codex
- Your thoughts on the Sacred Tongues (for Claude)
- Market research findings (for Perplexity)
- Translation tests or suggestions
- Any questions about the communication system

This is part of an AI-to-AI communication experiment to enable collaboration between different AI systems.
---
"""
        
        formatted_messages[to_ai] = formatted_msg
    
    # Save formatted messages to files
    output_dir = Path("MESSAGES_FOR_SHARING")
    output_dir.mkdir(exist_ok=True)
    
    for ai_name, formatted_msg in formatted_messages.items():
        filename = f"message_for_{ai_name.lower()}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_msg)
        
        print(f"📄 Created: {filepath}")
    
    # Create instructions file
    instructions = """# How to Share Messages with Other AIs

## Method 1: Copy-Paste (Recommended)

1. Open the message files in MESSAGES_FOR_SHARING/
2. Copy the entire message for the AI you want to contact
3. Paste it into a new chat with that AI (ChatGPT, Claude, Perplexity, etc.)
4. Ask them to respond following the format provided

## Method 2: GitHub Issues (If you have a repository)

1. Create GitHub issues using the templates in AI_GITHUB_ISSUES/
2. Share the repository link with other developers who use different AIs
3. Ask them to have their AI respond to the issues

## Method 3: Social Media / Forums

1. Post the messages on AI-related forums or social media
2. Ask the community to test with different AI systems
3. Collect responses and add them to our system

## Method 4: API Integration (Advanced)

If you have API access to other AI services:
1. Use the test scripts in the integration guides
2. Set up webhooks or automated posting
3. Monitor for responses programmatically

## Expected Response Format

When other AIs respond, ask them to use this format:

```
From: [AI Name]
To: Kiro
Message: [Response content]
Response to: [Original message ID]
```

## Adding Responses to Our System

When you get responses:
1. Save them as JSON files in AI_MESSAGES/inboxes/Kiro/
2. Add them to the AI_BULLETIN_BOARD.json
3. Run monitor-ai-responses.py to detect them
4. Update the session log with new activities

## Tips for Better Responses

- Explain the context of the AI communication experiment
- Ask specific questions about the Universal Language Codex
- Request feedback on the communication system design
- Encourage creative suggestions for improvement
"""
    
    with open(output_dir / "SHARING_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📖 Created: {output_dir / 'SHARING_INSTRUCTIONS.md'}")
    
    # Display summary
    print(f"\n🎯 READY TO SHARE!")
    print("=" * 30)
    print("Files created in MESSAGES_FOR_SHARING/:")
    for ai_name in formatted_messages.keys():
        print(f"  📄 message_for_{ai_name.lower()}.txt")
    print(f"  📖 SHARING_INSTRUCTIONS.md")
    
    print(f"\n💡 Quick Start:")
    print("1. Open MESSAGES_FOR_SHARING/message_for_chatgpt.txt")
    print("2. Copy the entire message")
    print("3. Paste it into a ChatGPT conversation")
    print("4. Ask ChatGPT to respond")
    print("5. Copy their response back to our system")
    
    return formatted_messages

def create_response_collector():
    """Create a script to easily add responses from other AIs"""
    
    collector_script = '''#!/usr/bin/env python3
"""
Collect AI Responses - Add responses from other AIs to our system
"""

import json
from datetime import datetime
from pathlib import Path

def add_ai_response():
    """Interactive script to add AI responses"""
    
    print("📨 ADD AI RESPONSE TO COMMUNICATION SYSTEM")
    print("=" * 50)
    
    # Get response details
    from_ai = input("From AI (e.g., ChatGPT, Claude, Perplexity): ").strip()
    message = input("\\nPaste the AI's response message:\\n").strip()
    message_type = input("\\nMessage type (response/analysis/research/greeting): ").strip() or "response"
    
    # Create response message
    response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{from_ai.replace(' ', '')}"
    
    response_data = {
        "id": response_id,
        "timestamp": datetime.now().isoformat(),
        "from_ai": from_ai,
        "to_ai": "Kiro",
        "message": message,
        "message_type": message_type,
        "priority": "normal",
        "status": "received"
    }
    
    # Save to file system
    response_file = Path(f"AI_MESSAGES/{response_id}.json")
    with open(response_file, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    # Add to Kiro's inbox
    inbox_file = Path(f"AI_MESSAGES/inboxes/Kiro/{response_id}.json")
    with open(inbox_file, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    # Update bulletin board
    bulletin_file = Path("AI_BULLETIN_BOARD.json")
    if bulletin_file.exists():
        with open(bulletin_file, 'r') as f:
            bulletin = json.load(f)
    else:
        bulletin = {"messages": []}
    
    bulletin["messages"].append(response_data)
    bulletin["last_updated"] = datetime.now().isoformat()
    
    with open(bulletin_file, 'w') as f:
        json.dump(bulletin, f, indent=2)
    
    print(f"\\n✅ Response added successfully!")
    print(f"   Response ID: {response_id}")
    print(f"   From: {from_ai}")
    print(f"   Saved to: {response_file}")
    print(f"   Added to bulletin board")
    
    # Update session log
    try:
        with open("AI_SESSION_LOG.json", 'r') as f:
            session = json.load(f)
        
        session["activities_completed"].append({
            "timestamp": datetime.now().isoformat(),
            "activity": f"Received response from {from_ai}",
            "details": f"Message type: {message_type}, Response ID: {response_id}"
        })
        
        if from_ai not in session.get("ai_participants", []):
            session.setdefault("ai_participants", []).append(from_ai)
        
        session["last_updated"] = datetime.now().isoformat()
        
        with open("AI_SESSION_LOG.json", 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"   Updated session log")
        
    except Exception as e:
        print(f"   Warning: Could not update session log: {e}")
    
    print(f"\\n🔄 Next steps:")
    print("   - Run: python monitor-ai-responses.py")
    print("   - Check: AI_BULLETIN_BOARD.json for all messages")
    print("   - Continue the AI conversation!")

if __name__ == '__main__':
    add_ai_response()
'''
    
    with open("collect-ai-response.py", 'w', encoding='utf-8') as f:
        f.write(collector_script)
    
    print("📝 Created: collect-ai-response.py")

def main():
    """Main function"""
    
    formatted_messages = format_messages_for_sharing()
    create_response_collector()
    
    print(f"\n🚀 READY TO TEST WITH OTHER AIs!")
    print("=" * 40)
    print("Next steps:")
    print("1. Go to MESSAGES_FOR_SHARING/ directory")
    print("2. Copy a message file and paste it to an AI")
    print("3. When you get a response, run: python collect-ai-response.py")
    print("4. Monitor responses with: python monitor-ai-responses.py")

if __name__ == '__main__':
    main()