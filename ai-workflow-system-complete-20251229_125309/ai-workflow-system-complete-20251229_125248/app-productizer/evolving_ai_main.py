#!/usr/bin/env python3
"""
Self-Evolving AI Framework - Main Entry Point
=============================================

CLI interface for the self-evolving AI system.

Usage:
    python evolving_ai_main.py [command] [options]

Commands:
    start       Start the framework
    status      Show system status
    mutate      Propose a mutation
    rollback    Rollback to snapshot
    sync        Sync data to storage
    fitness     Show fitness metrics
    demo        Run demonstration
"""

import argparse
import json
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import framework
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation, MutationType
from self_evolving_core.autonomy import Workflow


def cmd_start(args, framework):
    """Start the framework"""
    print("🚀 Starting Self-Evolving AI Framework...")
    framework.start()
    print(f"✅ Framework v{framework.VERSION} started successfully")
    print(f"   Generation: {framework.get_dna().generation}")
    print(f"   Fitness: {framework.get_dna().fitness_score:.2f}")


def cmd_status(args, framework):
    """Show system status"""
    status = framework.get_status()
    
    print("\n📊 Self-Evolving AI System Status")
    print("=" * 50)
    print(f"Version: {status['version']}")
    print(f"Running: {'✅' if status['running'] else '❌'}")
    
    print(f"\n🧬 DNA Status:")
    print(f"   Generation: {status['dna']['generation']}")
    print(f"   Fitness Score: {status['dna']['fitness_score']:.2f}")
    print(f"   Total Mutations: {status['dna']['mutations_count']}")
    
    print(f"\n💪 Fitness Metrics:")
    fitness = status['fitness']
    print(f"   Overall: {fitness['overall']:.2f}")
    print(f"   Success Rate: {fitness['success_rate']*100:.1f}%")
    print(f"   Trend: {fitness['trend']}")
    
    print(f"\n🤖 Autonomy:")
    auto = status['autonomy']
    print(f"   Mutations This Session: {auto['mutations_applied']}")
    print(f"   Pending Approvals: {auto['pending_approvals']}")
    
    print(f"\n💾 Storage:")
    storage = status['storage']
    print(f"   Queue Size: {storage['queue_size']}")
    platforms = storage['platforms']
    for p, enabled in platforms.items():
        print(f"   {p}: {'✅' if enabled else '❌'}")
    
    print(f"\n🔌 Providers:")
    for name, stats in status['providers'].get('providers', {}).items():
        print(f"   {name}: {stats['status']} (${stats['total_cost']:.4f})")


def cmd_mutate(args, framework):
    """Propose a mutation"""
    mutation = Mutation(
        type=args.type,
        description=args.description,
        fitness_impact=args.impact,
        source_ai="CLI"
    )
    
    print(f"\n🧬 Proposing Mutation: {args.type}")
    result = framework.propose_mutation(mutation)
    
    if result.get('approved'):
        if result.get('auto'):
            print("✅ Auto-approved and applied!")
            r = result['result']
            print(f"   Mutation ID: {r.mutation_id}")
            print(f"   New Generation: {r.new_generation}")
        else:
            print("✅ Approved by human review")
    else:
        print(f"⏳ Queued for approval (Risk: {result.get('risk', 0):.2f})")
        print(f"   Request ID: {result.get('request_id')}")


def cmd_rollback(args, framework):
    """Rollback to snapshot"""
    if args.list:
        snapshots = framework.rollback.list_snapshots(20)
        print("\n📸 Available Snapshots:")
        for s in snapshots:
            print(f"   {s.id} - Gen {s.metadata.get('generation')} - {s.label}")
        return
    
    if not args.snapshot_id:
        print("❌ Please provide --snapshot-id or use --list")
        return
    
    print(f"\n⏪ Rolling back to {args.snapshot_id}...")
    result = framework.rollback_to(args.snapshot_id)
    
    if result.get('success'):
        print(f"✅ Rolled back to generation {result.get('restored_generation')}")
    else:
        print(f"❌ Rollback failed: {result.get('error')}")


def cmd_sync(args, framework):
    """Sync data to storage"""
    dna = framework.get_dna()
    
    print("\n💾 Syncing system state...")
    results = framework.sync_storage(dna.to_dict(), "system_state.json")
    
    for platform, result in results.items():
        status = "✅" if result.get('success') else "❌"
        print(f"   {platform}: {status}")


def cmd_fitness(args, framework):
    """Show fitness metrics"""
    data = framework.fitness.get_dashboard_data()
    
    print("\n💪 Fitness Dashboard")
    print("=" * 50)
    
    current = data['current_fitness']
    print(f"Overall Score: {current['overall']:.2f}")
    print(f"Trend: {current['trend']}")
    
    print(f"\nComponents:")
    for metric, value in current['components'].items():
        bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
        print(f"   {metric:20} [{bar}] {value*100:.1f}%")
    
    print(f"\nOperations: {data['operations_summary']['total']}")
    print(f"Healing Events: {data['healing_summary']['total_events']}")
    print(f"Total Cost: ${data['cost_summary']['total_cost']:.4f}")


def cmd_demo(args, framework):
    """Run demonstration"""
    print("\n🎬 Self-Evolving AI Framework Demo")
    print("=" * 50)
    
    # Show initial state
    dna = framework.get_dna()
    print(f"\n1️⃣ Initial State:")
    print(f"   Generation: {dna.generation}")
    print(f"   Fitness: {dna.fitness_score:.2f}")
    
    # Analyze some feedback
    print(f"\n2️⃣ Analyzing AI Feedback...")
    feedback = "We should improve communication channels and add real-time sync capabilities."
    mutations = framework.analyze_feedback(feedback, "Demo")
    print(f"   Found {len(mutations)} mutation proposals")
    
    for m in mutations:
        print(f"   - {m.type}: {m.description[:50]}...")
    
    # Apply a low-risk mutation
    print(f"\n3️⃣ Applying Low-Risk Mutation...")
    mutation = Mutation(
        type=MutationType.COMMUNICATION_ENHANCEMENT.value,
        description="Demo: Add communication channel",
        fitness_impact=2.0,
        source_ai="Demo"
    )
    result = framework.propose_mutation(mutation)
    
    if result.get('approved'):
        print(f"   ✅ Mutation applied!")
        new_dna = framework.get_dna()
        print(f"   New Generation: {new_dna.generation}")
        print(f"   New Fitness: {new_dna.fitness_score:.2f}")
    else:
        print(f"   ⏳ Queued for approval")
    
    # Show fitness
    print(f"\n4️⃣ Fitness Check...")
    fitness = framework.get_fitness()
    print(f"   Overall: {fitness.overall:.2f}")
    print(f"   Trend: {fitness.trend}")
    
    # Sync to storage
    print(f"\n5️⃣ Syncing to Storage...")
    sync_results = framework.sync_storage(
        {"demo": True, "timestamp": datetime.now().isoformat()},
        "demo_sync.json"
    )
    for platform, r in sync_results.items():
        status = "✅" if r.get('success') else "❌"
        print(f"   {platform}: {status}")
    
    print(f"\n✨ Demo Complete!")
    print(f"   Final Generation: {framework.get_dna().generation}")
    print(f"   Final Fitness: {framework.get_dna().fitness_score:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Self-Evolving AI Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Start command
    subparsers.add_parser('start', help='Start the framework')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Mutate command
    mutate_parser = subparsers.add_parser('mutate', help='Propose a mutation')
    mutate_parser.add_argument('--type', '-t', required=True,
                              choices=[t.value for t in MutationType],
                              help='Mutation type')
    mutate_parser.add_argument('--description', '-d', required=True,
                              help='Mutation description')
    mutate_parser.add_argument('--impact', '-i', type=float, default=2.0,
                              help='Fitness impact')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback to snapshot')
    rollback_parser.add_argument('--snapshot-id', '-s', help='Snapshot ID')
    rollback_parser.add_argument('--list', '-l', action='store_true',
                                help='List available snapshots')
    
    # Sync command
    subparsers.add_parser('sync', help='Sync data to storage')
    
    # Fitness command
    subparsers.add_parser('fitness', help='Show fitness metrics')
    
    # Demo command
    subparsers.add_parser('demo', help='Run demonstration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize framework
    framework = EvolvingAIFramework()
    if not framework.initialize():
        print("❌ Failed to initialize framework")
        sys.exit(1)
    
    # Execute command
    commands = {
        'start': cmd_start,
        'status': cmd_status,
        'mutate': cmd_mutate,
        'rollback': cmd_rollback,
        'sync': cmd_sync,
        'fitness': cmd_fitness,
        'demo': cmd_demo
    }
    
    if args.command in commands:
        commands[args.command](args, framework)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
