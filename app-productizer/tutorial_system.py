#!/usr/bin/env python3
"""
Self-Evolving AI Tutorial System
===============================

Interactive tutorial system that guides users through every aspect of the
self-evolving AI framework. Perfect for learning and demonstration purposes.

Features:
- Step-by-step guided tutorials
- Interactive demos with real examples
- Code explanations and best practices
- Dummy data for safe testing
- Progress tracking and validation

Usage:
    python tutorial_system.py [tutorial_name]
    
Available Tutorials:
    - getting_started: Basic framework introduction
    - mutations: Understanding and applying mutations
    - fitness: Fitness monitoring and optimization
    - storage: Multi-platform storage sync
    - autonomy: Autonomous operation setup
    - ai_providers: AI provider integration
    - plugins: Plugin development and management
    - advanced: Advanced features and customization
"""

import json
import time
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation, MutationType, SystemDNA, CoreTraits


class TutorialSystem:
    """
    Interactive tutorial system for the Self-Evolving AI Framework.
    
    This system provides comprehensive, step-by-step guidance through
    all aspects of the framework, from basic setup to advanced features.
    """
    
    def __init__(self):
        self.framework = None
        self.current_step = 0
        self.tutorial_data = self._load_tutorial_data()
        self.demo_secrets = self._get_demo_secrets()
        
    def _load_tutorial_data(self) -> Dict[str, Any]:
        """Load tutorial configuration and demo data"""
        return {
            "demo_mutations": [
                {
                    "type": "communication_enhancement",
                    "description": "Add real-time WebSocket communication channel",
                    "fitness_impact": 5.0,
                    "tutorial_notes": "This mutation improves real-time communication capabilities"
                },
                {
                    "type": "intelligence_upgrade", 
                    "description": "Integrate GPT-4 Turbo for enhanced reasoning",
                    "fitness_impact": 8.0,
                    "tutorial_notes": "AI provider upgrades significantly boost system intelligence"
                },
                {
                    "type": "storage_optimization",
                    "description": "Implement distributed caching layer",
                    "fitness_impact": 3.0,
                    "tutorial_notes": "Storage optimizations improve performance and reliability"
                }
            ],
            "demo_workflows": [
                {
                    "name": "Content Generation Pipeline",
                    "steps": [
                        {"type": "ai_call", "prompt": "Generate blog post outline about AI"},
                        {"type": "mutation", "mutation": {"type": "language_expansion"}},
                        {"type": "sync", "data": {"content": "generated"}, "path": "content.json"}
                    ]
                }
            ],
            "sample_feedback": [
                "The system should add support for Claude 3.5 Sonnet for better reasoning",
                "We need faster storage sync - current delays are impacting performance", 
                "Add plugin support for custom AI workflows and integrations",
                "Implement cost optimization to reduce API expenses by 30%"
            ]
        }
    
    def _get_demo_secrets(self) -> Dict[str, str]:
        """
        Demo API keys and secrets for tutorial purposes.
        
        ⚠️  IMPORTANT: These are dummy values for demonstration only!
        Replace with real credentials for production use.
        """
        return {
            # AI Provider API Keys (Demo - Replace with real keys)
            "OPENAI_API_KEY": "sk-demo1234567890abcdef1234567890abcdef1234567890abcdef",
            "ANTHROPIC_API_KEY": "sk-ant-demo1234567890abcdef1234567890abcdef1234567890abcdef",
            "GOOGLE_AI_KEY": "AIzaSyDemo1234567890abcdef1234567890abcdef123",
            "XAI_API_KEY": "xai-demo1234567890abcdef1234567890abcdef1234567890abcdef",
            "PERPLEXITY_API_KEY": "pplx-demo1234567890abcdef1234567890abcdef1234567890abcdef",
            
            # Storage Platform Tokens (Demo - Replace with real tokens)
            "DROPBOX_ACCESS_TOKEN": "sl.demo1234567890abcdef1234567890abcdef1234567890abcdef",
            "GITHUB_TOKEN": "ghp_demo1234567890abcdef1234567890abcdef1234567890abcdef",
            "NOTION_TOKEN": "secret_demo1234567890abcdef1234567890abcdef1234567890abcdef",
            
            # Database and Infrastructure (Demo - Replace with real values)
            "DATABASE_URL": "postgresql://demo_user:demo_pass@localhost:5432/demo_db",
            "REDIS_URL": "redis://localhost:6379/0",
            "AWS_ACCESS_KEY_ID": "AKIADEMO1234567890AB",
            "AWS_SECRET_ACCESS_KEY": "demo1234567890abcdef1234567890abcdef12345678",
            
            # Webhook and Integration URLs (Demo - Replace with real URLs)
            "WEBHOOK_URL": "https://demo-webhook.example.com/evolving-ai",
            "SLACK_WEBHOOK": "https://hooks.slack.com/services/T00000000/B00000000/demo1234567890abcdef",
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123456789/demo1234567890abcdef"
        }

    def print_header(self, title: str, subtitle: str = ""):
        """Print formatted tutorial header"""
        print("\n" + "="*60)
        print(f"🎓 {title}")
        if subtitle:
            print(f"   {subtitle}")
        print("="*60)

    def print_step(self, step_num: int, title: str, description: str = ""):
        """Print formatted tutorial step"""
        print(f"\n{step_num}️⃣  {title}")
        if description:
            print(f"    {description}")

    def wait_for_user(self, message: str = "Press Enter to continue..."):
        """Wait for user input to proceed"""
        input(f"\n💡 {message}")

    def tutorial_getting_started(self):
        """
        Getting Started Tutorial
        
        This tutorial introduces the basic concepts and demonstrates
        the core functionality of the Self-Evolving AI Framework.
        """
        self.print_header("Getting Started with Self-Evolving AI", 
                         "Learn the basics and see the system in action")
        
        print("""
🌟 Welcome to the Self-Evolving AI Framework!

This system is designed to:
• Automatically improve itself based on AI feedback
• Manage multiple AI providers with cost optimization
• Sync data across multiple cloud platforms
• Execute workflows autonomously with safety controls
• Track fitness metrics and performance over time

Let's start with a hands-on demonstration!
        """)
        
        self.wait_for_user()
        
        # Step 1: Initialize Framework
        self.print_step(1, "Framework Initialization", 
                       "Setting up the core components")
        
        print("Initializing framework with demo configuration...")
        self.framework = EvolvingAIFramework()
        success = self.framework.initialize()
        
        if success:
            print("✅ Framework initialized successfully!")
            print(f"   Version: {self.framework.VERSION}")
            print(f"   Components: {len([c for c in dir(self.framework) if not c.startswith('_')])} loaded")
        else:
            print("❌ Framework initialization failed")
            return
        
        self.wait_for_user()
        
        # Step 2: Examine System DNA
        self.print_step(2, "System DNA Overview", 
                       "Understanding the genetic configuration")
        
        dna = self.framework.get_dna()
        print(f"""
🧬 Current System DNA:
   Generation: {dna.generation}
   Fitness Score: {dna.fitness_score}
   Birth Date: {dna.birth_timestamp[:10]}
   
🔧 Core Traits:
   Communication Channels: {dna.core_traits.communication_channels}
   Language Support: {dna.core_traits.language_support}
   Autonomy Level: {dna.core_traits.autonomy_level:.1%}
   
📊 Evolution History:
   Total Mutations: {len(dna.mutations)}
   Available Snapshots: {len(dna.snapshots)}
        """)
        
        self.wait_for_user()
        
        # Step 3: Demonstrate Mutation
        self.print_step(3, "Applying Your First Mutation", 
                       "See how the system evolves")
        
        demo_mutation = self.tutorial_data["demo_mutations"][0]
        mutation = Mutation(
            type=demo_mutation["type"],
            description=demo_mutation["description"],
            fitness_impact=demo_mutation["fitness_impact"],
            source_ai="Tutorial"
        )
        
        print(f"""
🧬 Proposing Mutation:
   Type: {mutation.type}
   Description: {mutation.description}
   Expected Fitness Impact: +{mutation.fitness_impact}
   
💡 Tutorial Note: {demo_mutation['tutorial_notes']}
        """)
        
        result = self.framework.propose_mutation(mutation)
        
        if result.get('approved'):
            print("✅ Mutation approved and applied!")
            new_dna = self.framework.get_dna()
            print(f"   New Generation: {new_dna.generation}")
            print(f"   New Fitness: {new_dna.fitness_score}")
        else:
            print(f"⏳ Mutation queued for approval (Risk: {result.get('risk', 0):.2f})")
        
        self.wait_for_user()
        
        # Step 4: Fitness Monitoring
        self.print_step(4, "Fitness Monitoring", 
                       "Understanding system performance metrics")
        
        fitness = self.framework.get_fitness()
        print(f"""
💪 Current Fitness Metrics:
   Overall Score: {fitness.overall:.2f}
   Success Rate: {fitness.success_rate*100:.1f}%
   Trend: {fitness.trend}
   Last Updated: {fitness.timestamp[:19]}
   
📈 What These Metrics Mean:
   • Overall Score: Combined performance indicator
   • Success Rate: Percentage of successful operations
   • Trend: Direction of performance change
        """)
        
        self.wait_for_user()
        
        # Step 5: Storage Sync Demo
        self.print_step(5, "Storage Synchronization", 
                       "Backing up system state across platforms")
        
        demo_data = {
            "tutorial_completion": "getting_started",
            "timestamp": datetime.now().isoformat(),
            "system_state": {
                "generation": self.framework.get_dna().generation,
                "fitness": self.framework.get_dna().fitness_score
            }
        }
        
        print("Syncing tutorial progress to storage platforms...")
        sync_results = self.framework.sync_storage(demo_data, "tutorial_progress.json")
        
        for platform, result in sync_results.items():
            status = "✅" if result.get('success') else "❌"
            print(f"   {platform}: {status}")
        
        print("""
💾 Storage Sync Benefits:
   • Automatic backup across multiple platforms
   • Version control for system evolution
   • Disaster recovery capabilities
   • Collaborative AI development
        """)
        
        self.wait_for_user()
        
        print("""
🎉 Congratulations! You've completed the Getting Started tutorial!

What you learned:
✅ How to initialize the framework
✅ Understanding System DNA and evolution
✅ Applying mutations to improve the system
✅ Monitoring fitness and performance
✅ Syncing data across storage platforms

Next Steps:
🔄 Try: python tutorial_system.py mutations
🔄 Try: python tutorial_system.py fitness  
🔄 Try: python tutorial_system.py autonomy

Happy evolving! 🚀
        """)

    def tutorial_mutations(self):
        """
        Mutations Tutorial
        
        Deep dive into the mutation system - the core of evolution.
        Learn different mutation types, risk assessment, and rollback.
        """
        self.print_header("Mastering Mutations", 
                         "The heart of self-evolution")
        
        print("""
🧬 Mutations are the core mechanism for system evolution!

Types of Mutations:
• Communication Enhancement - Improve AI-to-AI communication
• Intelligence Upgrade - Add new AI providers or capabilities  
• Storage Optimization - Enhance data sync and storage
• Language Expansion - Add support for new programming languages
• Protocol Improvement - Upgrade communication protocols
• Autonomy Adjustment - Modify autonomous operation parameters

Let's explore each type with hands-on examples!
        """)
        
        self.wait_for_user()
        
        # Initialize framework if not already done
        if not self.framework:
            self.framework = EvolvingAIFramework()
            self.framework.initialize()
        
        # Demonstrate each mutation type
        for i, demo_mutation in enumerate(self.tutorial_data["demo_mutations"], 1):
            self.print_step(i, f"Mutation Type: {demo_mutation['type']}", 
                           demo_mutation['tutorial_notes'])
            
            mutation = Mutation(
                type=demo_mutation["type"],
                description=demo_mutation["description"],
                fitness_impact=demo_mutation["fitness_impact"],
                source_ai="Tutorial"
            )
            
            # Show risk assessment
            risk = self.framework.autonomy.assess_risk(mutation)
            print(f"""
🎯 Mutation Details:
   Type: {mutation.type}
   Description: {mutation.description}
   Fitness Impact: +{mutation.fitness_impact}
   Risk Score: {risk:.3f}
   Auto-Approval: {'Yes' if risk < 0.3 else 'No'}
            """)
            
            # Apply mutation
            result = self.framework.propose_mutation(mutation)
            
            if result.get('approved'):
                print("✅ Mutation applied successfully!")
                if result.get('auto'):
                    print("   (Auto-approved due to low risk)")
            else:
                print("⏳ Mutation queued for manual approval")
            
            self.wait_for_user("Ready for next mutation type?")
        
        # Demonstrate rollback
        self.print_step(4, "Rollback Demonstration", 
                       "Safety mechanism for failed mutations")
        
        snapshots = self.framework.rollback.list_snapshots(5)
        if snapshots:
            print(f"""
📸 Available Snapshots:
            """)
            for snap in snapshots[:3]:
                print(f"   {snap.id} - {snap.label} (Gen {snap.metadata.get('generation', 'N/A')})")
            
            print("""
🔄 Rollback Process:
1. System creates snapshot before each mutation
2. If mutation fails or causes issues, rollback is triggered
3. System state is restored to exact previous condition
4. All changes are logged for audit purposes

This ensures safe evolution with zero data loss!
            """)
        
        self.wait_for_user()
        
        print("""
🎓 Mutations Tutorial Complete!

Key Takeaways:
✅ 6 different mutation types for comprehensive evolution
✅ Risk assessment prevents dangerous changes
✅ Auto-approval for low-risk mutations
✅ Rollback system ensures safety
✅ All changes are logged and auditable

Advanced Topics:
🔄 Try: python tutorial_system.py fitness
🔄 Try: python tutorial_system.py autonomy
        """)

    def tutorial_fitness(self):
        """Fitness monitoring and optimization tutorial"""
        self.print_header("Fitness Monitoring & Optimization", 
                         "Measuring and improving system performance")
        
        # Implementation for fitness tutorial
        print("🏃‍♂️ Fitness tutorial coming soon...")
        
    def tutorial_storage(self):
        """Storage synchronization tutorial"""
        self.print_header("Multi-Platform Storage Sync", 
                         "Backing up across Dropbox, GitHub, and more")
        
        # Implementation for storage tutorial
        print("💾 Storage tutorial coming soon...")
        
    def tutorial_autonomy(self):
        """Autonomous operation tutorial"""
        self.print_header("Autonomous Operation", 
                         "Setting up self-managing AI workflows")
        
        # Implementation for autonomy tutorial
        print("🤖 Autonomy tutorial coming soon...")

    def run_tutorial(self, tutorial_name: str):
        """Run a specific tutorial"""
        tutorials = {
            "getting_started": self.tutorial_getting_started,
            "mutations": self.tutorial_mutations,
            "fitness": self.tutorial_fitness,
            "storage": self.tutorial_storage,
            "autonomy": self.tutorial_autonomy
        }
        
        if tutorial_name in tutorials:
            tutorials[tutorial_name]()
        else:
            print(f"❌ Tutorial '{tutorial_name}' not found!")
            print(f"Available tutorials: {', '.join(tutorials.keys())}")

    def list_tutorials(self):
        """List all available tutorials"""
        self.print_header("Available Tutorials")
        
        tutorials = [
            ("getting_started", "Basic framework introduction and demo"),
            ("mutations", "Understanding and applying system mutations"),
            ("fitness", "Fitness monitoring and performance optimization"),
            ("storage", "Multi-platform storage synchronization"),
            ("autonomy", "Autonomous operation and workflow management"),
            ("ai_providers", "AI provider integration and management"),
            ("plugins", "Plugin development and customization"),
            ("advanced", "Advanced features and enterprise deployment")
        ]
        
        for name, description in tutorials:
            print(f"📚 {name:15} - {description}")
        
        print(f"\nUsage: python tutorial_system.py [tutorial_name]")


def main():
    """Main tutorial system entry point"""
    tutorial = TutorialSystem()
    
    if len(sys.argv) < 2:
        tutorial.list_tutorials()
        return
    
    tutorial_name = sys.argv[1]
    tutorial.run_tutorial(tutorial_name)


if __name__ == "__main__":
    main()