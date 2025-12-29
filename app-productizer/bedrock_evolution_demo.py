#!/usr/bin/env python3
"""
AWS Bedrock AI Evolution System Demo
===================================

Comprehensive demonstration of the AWS Bedrock integration with the
self-evolving AI framework. Shows LLM-powered evolution guidance,
autonomous decision making, and cloud-native storage.

Usage:
    python bedrock_evolution_demo.py [--config config.yaml] [--aws-config aws_config.json]
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any
import argparse

# Import the Bedrock framework
from self_evolving_core.bedrock_framework import BedrockFramework, create_bedrock_framework
from self_evolving_core.models import Mutation, SystemDNA, FitnessScore
from self_evolving_core.cloud_dna_store import EvolutionEvent
from self_evolving_core.bedrock_decision_engine import SystemConflict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BedrockEvolutionDemo:
    """
    Comprehensive demo of AWS Bedrock AI Evolution capabilities
    """
    
    def __init__(self, config_path: str = None, aws_config_path: str = None):
        self.config_path = config_path
        self.aws_config_path = aws_config_path
        self.framework: BedrockFramework = None
        
    async def run_demo(self):
        """Run the complete Bedrock evolution demo"""
        
        print("🚀 AWS Bedrock AI Evolution System Demo")
        print("=" * 50)
        
        try:
            # Initialize framework
            await self.initialize_framework()
            
            # Run demo scenarios
            await self.demo_system_analysis()
            await self.demo_mutation_evaluation()
            await self.demo_conflict_resolution()
            await self.demo_cost_optimization()
            await self.demo_cloud_storage()
            
            # Show final status
            await self.show_final_status()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
        
        finally:
            if self.framework:
                self.framework.stop()
                print("\n✅ Demo completed successfully!")
    
    async def initialize_framework(self):
        """Initialize the Bedrock framework"""
        
        print("\n📋 Initializing Bedrock Framework...")
        
        try:
            self.framework = create_bedrock_framework(
                config_path=self.config_path,
                aws_config_path=self.aws_config_path
            )
            
            # Check Bedrock status
            status = self.framework.get_bedrock_status()
            
            if status["bedrock_enabled"]:
                print("✅ Bedrock integration enabled")
                
                # Show connectivity status
                connectivity = status.get("aws_connectivity", {})
                for service, connected in connectivity.items():
                    status_icon = "✅" if connected else "❌"
                    print(f"   {status_icon} {service.upper()}: {'Connected' if connected else 'Failed'}")
            else:
                print("⚠️  Bedrock integration disabled - using fallback mode")
            
        except Exception as e:
            logger.error(f"Framework initialization failed: {e}")
            print(f"❌ Framework initialization failed: {e}")
            raise
    
    async def demo_system_analysis(self):
        """Demonstrate LLM-powered system analysis"""
        
        print("\n🧠 LLM-Powered System Analysis")
        print("-" * 30)
        
        if not self.framework.bedrock_enabled:
            print("⚠️  Bedrock not available - skipping LLM analysis")
            return
        
        try:
            # Get current system state
            dna = self.framework.get_dna()
            print(f"📊 Current System State:")
            print(f"   Generation: {dna.generation}")
            print(f"   Fitness Score: {dna.fitness_score}")
            print(f"   Mutations Applied: {len(dna.mutations)}")
            
            # Get evolution guidance
            print("\n🔍 Requesting LLM Analysis...")
            guidance = await self.framework.get_evolution_guidance(dna)
            
            if "error" not in guidance:
                analysis = guidance.get("analysis", {})
                strategy = guidance.get("strategy", {})
                
                print("✅ LLM Analysis Complete:")
                print(f"   Assessment: {analysis.get('current_state_assessment', 'N/A')}")
                print(f"   Confidence: {analysis.get('confidence_score', 0):.2f}")
                
                strengths = analysis.get('strengths', [])
                if strengths:
                    print(f"   Strengths: {', '.join(strengths[:3])}")
                
                opportunities = analysis.get('opportunities', [])
                if opportunities:
                    print(f"   Opportunities: {', '.join(opportunities[:3])}")
                
                # Show strategy recommendations
                primary_mutations = strategy.get('primary_mutations', [])
                if primary_mutations:
                    print(f"\n💡 Recommended Mutations:")
                    for i, mutation in enumerate(primary_mutations[:3], 1):
                        print(f"   {i}. {mutation.get('type', 'Unknown')}: {mutation.get('description', 'N/A')}")
                        print(f"      Expected Impact: +{mutation.get('expected_fitness_impact', 0):.1f}")
                        print(f"      Risk Score: {mutation.get('risk_score', 0):.2f}")
            else:
                print(f"❌ Analysis failed: {guidance['error']}")
        
        except Exception as e:
            logger.error(f"System analysis demo failed: {e}")
            print(f"❌ System analysis failed: {e}")
    
    async def demo_mutation_evaluation(self):
        """Demonstrate LLM-powered mutation evaluation"""
        
        print("\n🔬 LLM-Powered Mutation Evaluation")
        print("-" * 35)
        
        # Create test mutations with different risk levels
        test_mutations = [
            Mutation(
                type="communication_enhancement",
                description="Improve message routing efficiency",
                fitness_impact=3.0,
                source_ai="Demo"
            ),
            Mutation(
                type="intelligence_upgrade",
                description="Enhance decision-making algorithms with advanced reasoning",
                fitness_impact=8.0,
                source_ai="Demo"
            ),
            Mutation(
                type="autonomy_adjustment",
                description="Increase autonomous operation capabilities significantly",
                fitness_impact=12.0,
                source_ai="Demo"
            )
        ]
        
        for i, mutation in enumerate(test_mutations, 1):
            print(f"\n🧪 Evaluating Mutation {i}: {mutation.type}")
            print(f"   Description: {mutation.description}")
            print(f"   Expected Impact: +{mutation.fitness_impact}")
            
            try:
                if self.framework.bedrock_enabled and hasattr(self.framework, 'propose_mutation_enhanced'):
                    # Use enhanced evaluation
                    result = await self.framework.propose_mutation_enhanced(mutation)
                    
                    print(f"   🤖 LLM Decision: {result.get('final_decision', 'Unknown')}")
                    print(f"   🎯 Confidence: {result.get('confidence', 0):.2f}")
                    
                    reasoning = result.get('reasoning', '')
                    if reasoning:
                        # Truncate long reasoning
                        short_reasoning = reasoning[:100] + "..." if len(reasoning) > 100 else reasoning
                        print(f"   💭 Reasoning: {short_reasoning}")
                    
                    if result.get('escalation_required'):
                        print("   ⚠️  Escalation Required")
                    
                    if result.get('mutation_applied'):
                        print("   ✅ Mutation Applied Successfully")
                    elif result.get('approval_request_id'):
                        print(f"   ⏳ Pending Approval: {result['approval_request_id']}")
                
                else:
                    # Use base evaluation
                    result = self.framework.propose_mutation(mutation)
                    print(f"   📋 Base Decision: {'Approved' if result.get('approved') else 'Requires Approval'}")
            
            except Exception as e:
                logger.error(f"Mutation evaluation failed: {e}")
                print(f"   ❌ Evaluation failed: {e}")
    
    async def demo_conflict_resolution(self):
        """Demonstrate LLM-powered conflict resolution"""
        
        print("\n🛠️  LLM-Powered Conflict Resolution")
        print("-" * 35)
        
        if not self.framework.bedrock_enabled or not self.framework.enhanced_autonomy:
            print("⚠️  Enhanced autonomy not available - skipping conflict resolution")
            return
        
        # Create a test system conflict
        test_conflict = SystemConflict(
            type="resource_contention",
            description="Multiple processes competing for limited memory resources",
            affected_components=["mutation_engine", "fitness_monitor", "storage_sync"],
            severity="medium",
            current_impact={"performance_degradation": 0.3, "error_rate": 0.05},
            available_resources={"cpu": 0.7, "memory": 0.4, "disk": 0.8},
            active_processes=["evolution", "monitoring", "sync"],
            recent_changes=[
                {"type": "mutation", "timestamp": "2025-12-29T10:00:00Z", "impact": "increased_memory_usage"}
            ]
        )
        
        print(f"🚨 System Conflict Detected:")
        print(f"   Type: {test_conflict.type}")
        print(f"   Severity: {test_conflict.severity}")
        print(f"   Affected: {', '.join(test_conflict.affected_components)}")
        
        try:
            print("\n🔍 Requesting LLM Resolution Strategy...")
            
            resolution = await self.framework.enhanced_autonomy.resolve_system_conflict(test_conflict)
            
            print("✅ Resolution Strategy Generated:")
            print(f"   Confidence: {resolution.confidence:.2f}")
            print(f"   Timeline: {resolution.timeline_estimate}")
            
            if resolution.immediate_actions:
                print("   🚀 Immediate Actions:")
                for action in resolution.immediate_actions[:3]:
                    print(f"      • {action}")
            
            if resolution.prevention_measures:
                print("   🛡️  Prevention Measures:")
                for measure in resolution.prevention_measures[:2]:
                    print(f"      • {measure}")
            
            print(f"   📊 Root Cause: {resolution.root_cause_analysis[:100]}...")
        
        except Exception as e:
            logger.error(f"Conflict resolution demo failed: {e}")
            print(f"❌ Conflict resolution failed: {e}")
    
    async def demo_cost_optimization(self):
        """Demonstrate cost tracking and optimization"""
        
        print("\n💰 Cost Tracking & Optimization")
        print("-" * 30)
        
        if not self.framework.bedrock_enabled:
            print("⚠️  Bedrock not available - skipping cost demo")
            return
        
        try:
            # Get current usage stats
            bedrock_status = self.framework.get_bedrock_status()
            usage_stats = bedrock_status.get("usage_stats", {})
            
            # Show Bedrock usage
            bedrock_usage = usage_stats.get("bedrock", {})
            if bedrock_usage:
                cost_tracking = bedrock_usage.get("cost_tracking", {})
                budget_status = cost_tracking.get("budget_status", {})
                
                print("📊 Current Usage:")
                print(f"   Daily Spend: ${cost_tracking.get('daily_spend', 0):.4f}")
                print(f"   Monthly Spend: ${cost_tracking.get('monthly_spend', 0):.4f}")
                print(f"   Total Requests: {cost_tracking.get('total_requests', 0)}")
                print(f"   Total Tokens: {cost_tracking.get('total_tokens', 0):,}")
                
                print("\n📈 Budget Status:")
                print(f"   Daily Usage: {budget_status.get('daily_usage_percent', 0):.1f}%")
                print(f"   Monthly Usage: {budget_status.get('monthly_usage_percent', 0):.1f}%")
                print(f"   Daily Remaining: ${budget_status.get('daily_remaining', 0):.2f}")
            
            # Show model router stats
            router_stats = usage_stats.get("model_router", {})
            if router_stats:
                model_usage = router_stats.get("model_usage_frequency", {})
                if model_usage:
                    print("\n🤖 Model Usage:")
                    for model, count in model_usage.items():
                        print(f"   {model}: {count} selections")
            
            # Get optimization recommendations
            print("\n🎯 Getting Optimization Recommendations...")
            optimization = self.framework.optimize_bedrock_usage()
            
            recommendations = optimization.get("recommendations", [])
            if recommendations:
                print("💡 Recommendations:")
                for rec in recommendations[:3]:
                    print(f"   • {rec}")
            
            cost_insights = optimization.get("cost_insights", [])
            if cost_insights:
                print("💸 Cost Insights:")
                for insight in cost_insights[:3]:
                    print(f"   • {insight}")
        
        except Exception as e:
            logger.error(f"Cost optimization demo failed: {e}")
            print(f"❌ Cost optimization failed: {e}")
    
    async def demo_cloud_storage(self):
        """Demonstrate cloud-native storage capabilities"""
        
        print("\n☁️  Cloud-Native Storage")
        print("-" * 25)
        
        if not self.framework.bedrock_enabled or not self.framework.cloud_dna_store:
            print("⚠️  Cloud storage not available - skipping storage demo")
            return
        
        try:
            # Show storage configuration
            storage_stats = self.framework.cloud_dna_store.get_storage_stats()
            
            print("📦 Storage Configuration:")
            print(f"   S3 Bucket: {storage_stats.get('s3_bucket', 'N/A')}")
            print(f"   DynamoDB Tables: {len(storage_stats.get('dynamodb_tables', {}))}")
            print(f"   CloudWatch Namespace: {storage_stats.get('cloudwatch_namespace', 'N/A')}")
            print(f"   Cross-Region Replication: {storage_stats.get('cross_region_replication', False)}")
            
            # Show table statistics if available
            table_stats = storage_stats.get("table_stats", {})
            if table_stats and "error" not in table_stats:
                print("\n📊 Storage Statistics:")
                print(f"   Snapshots: {table_stats.get('snapshots_item_count', 0)} items")
                print(f"   Events: {table_stats.get('events_item_count', 0)} items")
            
            # Demonstrate event storage (mock)
            print("\n📝 Storing Evolution Event...")
            
            test_event = EvolutionEvent(
                id=f"demo_event_{int(asyncio.get_event_loop().time())}",
                timestamp=datetime.now(),
                type="demo_mutation",
                generation=1,
                fitness_delta=2.5,
                data={"demo": True, "source": "bedrock_demo"},
                importance=0.7
            )
            
            # In a real scenario, this would store to AWS
            print(f"   Event ID: {test_event.id}")
            print(f"   Type: {test_event.type}")
            print(f"   Fitness Delta: +{test_event.fitness_delta}")
            print("   ✅ Event prepared for cloud storage")
        
        except Exception as e:
            logger.error(f"Cloud storage demo failed: {e}")
            print(f"❌ Cloud storage demo failed: {e}")
    
    async def show_final_status(self):
        """Show comprehensive final status"""
        
        print("\n📋 Final System Status")
        print("-" * 25)
        
        try:
            # Get enhanced status
            status = self.framework.get_enhanced_status()
            
            # Base framework status
            print("🔧 Framework Status:")
            print(f"   Version: {status.get('version', 'Unknown')}")
            print(f"   Initialized: {status.get('initialized', False)}")
            print(f"   Running: {status.get('running', False)}")
            
            # DNA status
            dna_status = status.get("dna", {})
            if dna_status:
                print(f"   Generation: {dna_status.get('generation', 0)}")
                print(f"   Fitness: {dna_status.get('fitness_score', 0):.1f}")
                print(f"   Mutations: {dna_status.get('mutations_count', 0)}")
            
            # Bedrock status
            bedrock_status = status.get("bedrock", {})
            if bedrock_status:
                print(f"\n🤖 Bedrock Status:")
                print(f"   Enabled: {bedrock_status.get('bedrock_enabled', False)}")
                
                connectivity = bedrock_status.get("aws_connectivity", {})
                connected_services = sum(1 for connected in connectivity.values() if connected)
                total_services = len(connectivity)
                print(f"   AWS Services: {connected_services}/{total_services} connected")
            
            # Performance summary
            fitness_status = status.get("fitness", {})
            if fitness_status:
                print(f"\n📊 Performance:")
                print(f"   Overall Fitness: {fitness_status.get('overall', 0):.1f}")
                print(f"   Success Rate: {fitness_status.get('success_rate', 0):.1%}")
                print(f"   Uptime: {fitness_status.get('uptime', 0):.1%}")
        
        except Exception as e:
            logger.error(f"Status display failed: {e}")
            print(f"❌ Status display failed: {e}")


def main():
    """Main demo entry point"""
    
    parser = argparse.ArgumentParser(description="AWS Bedrock AI Evolution Demo")
    parser.add_argument("--config", help="Path to framework config file")
    parser.add_argument("--aws-config", help="Path to AWS config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run demo
    demo = BedrockEvolutionDemo(
        config_path=args.config,
        aws_config_path=args.aws_config
    )
    
    try:
        asyncio.run(demo.run_demo())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        logger.error(f"Demo failed: {e}")


if __name__ == "__main__":
    main()