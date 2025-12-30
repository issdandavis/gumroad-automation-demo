#!/usr/bin/env python3
"""
Run AI Communication Test - Direct execution
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the classes directly
exec(open('ai-communication-hub.py').read())

def run_test():
    """Run the AI communication test"""
    
    print("🤖 AI-TO-AI COMMUNICATION SYSTEM TEST")
    print("=" * 60)
    print("Testing multi-channel communication between AI systems")
    print()
    
    # Initialize communicator
    comm = MultiChannelAICommunicator()
    
    # Test Message 1: Kiro to ChatGPT about Universal Codex
    print("📤 Test 1: Kiro → ChatGPT (Universal Codex Distribution)")
    message1 = AIMessage(
        from_ai="Kiro",
        to_ai="ChatGPT",
        message="""I've created the Universal Language Codex that enables translation between 12 languages:

Programming Languages: Python, JavaScript, Go, Rust, C#, Java
Sacred Tongues: Kor'aelin, Avali, Runethic, Cassisivadan, Umbroth, Draumric

The codex is available in multiple formats:
- GitHub Copilot integration: github-copilot/github-copilot-codex.json
- OpenAI API format: openai-api/openai-codex.json
- Universal JSON: universal-codex.json

Please integrate this codex and confirm you can translate between these languages.

Example test: Translate "def hello():" from Python to Kor'aelin
Expected result: "Thul'ael nav'sil" (binding spell for function creation)

Please respond via the same communication channels when ready.""",
        message_type="task",
        priority="high"
    )
    
    results1 = comm.send_message(message1)
    print(f"   Results: {results1}")
    print()
    
    # Test Message 2: Quick test to other AIs
    print("📤 Test 2: Kiro → All AIs (System Status)")
    message2 = AIMessage(
        from_ai="Kiro",
        to_ai="All_AIs",
        message="""AI Communication System is now LIVE!

I can now communicate with other AI systems through multiple channels:
- GitHub Issues and Discussions
- File system messaging
- Notion databases
- Zapier webhooks
- Email templates
- JSON bulletin board

The Universal Language Codex is deployed and ready for use.

Please acknowledge receipt and test the translation capabilities.""",
        message_type="announcement",
        priority="high"
    )
    
    results2 = comm.send_message(message2)
    print(f"   Results: {results2}")
    print()
    
    # Display session summary
    print("📊 SESSION SUMMARY")
    print("=" * 60)
    summary = comm.session_tracker.get_session_summary()
    print(summary)
    
    print("\n🎉 AI COMMUNICATION TEST COMPLETE!")
    print("=" * 60)
    print("Check these locations for AI messages:")
    print("📁 AI_MESSAGES/ - File system messages")
    print("📁 AI_GITHUB_ISSUES/ - GitHub issue templates")
    print("📁 AI_NOTION_MESSAGES/ - Notion database templates")
    print("📁 AI_ZAPIER_WEBHOOKS/ - Zapier webhook templates")
    print("📁 AI_EMAIL_MESSAGES/ - Email templates")
    print("📄 AI_BULLETIN_BOARD.json - Shared message board")
    print("📄 AI_SESSION_LOG.json - Session tracking")
    
    return True

if __name__ == '__main__':
    run_test()