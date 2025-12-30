#!/usr/bin/env python3
"""
Framework Initialization Test
============================

Tests that all framework components initialize correctly and are properly wired.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import framework
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import SystemDNA


def test_framework_initialization():
    """Test framework initialization and component loading"""
    print("🧪 Testing Framework Initialization")
    print("=" * 50)
    
    # Test 1: Framework creation
    print("\n1️⃣ Testing Framework Creation...")
    framework = EvolvingAIFramework()
    assert framework is not None, "Framework creation failed"
    assert framework.VERSION == "2.0.0", f"Expected version 2.0.0, got {framework.VERSION}"
    assert not framework._initialized, "Framework should not be initialized yet"
    print("   ✅ Framework created successfully")
    
    # Test 2: Framework initialization
    print("\n2️⃣ Testing Framework Initialization...")
    success = framework.initialize()
    assert success, "Framework initialization failed"
    assert framework._initialized, "Framework should be marked as initialized"
    print("   ✅ Framework initialized successfully")
    
    # Test 3: Component verification
    print("\n3️⃣ Testing Component Loading...")
    
    # Check all components are loaded
    components = {
        'dna_manager': framework.dna_manager,
        'event_bus': framework.event_bus,
        'autonomy': framework.autonomy,
        'mutation_engine': framework.mutation_engine,
        'storage': framework.storage,
        'fitness': framework.fitness,
        'rollback': framework.rollback,
        'healer': framework.healer,
        'audit': framework.audit,
        'evolution_log': framework.evolution_log,
        'feedback': framework.feedback,
        'plugins': framework.plugins,
        'providers': framework.providers
    }
    
    for name, component in components.items():
        assert component is not None, f"Component {name} not loaded"
        print(f"   ✅ {name}: {type(component).__name__}")
    
    # Test 4: DNA loading
    print("\n4️⃣ Testing DNA Loading...")
    dna = framework.get_dna()
    assert isinstance(dna, SystemDNA), f"Expected SystemDNA, got {type(dna)}"
    assert dna.version is not None, "DNA version not set"
    assert dna.generation >= 1, f"Invalid generation: {dna.generation}"
    assert dna.fitness_score >= 0, f"Invalid fitness score: {dna.fitness_score}"
    print(f"   ✅ DNA loaded: Gen {dna.generation}, Fitness {dna.fitness_score}")
    
    # Test 5: Status retrieval
    print("\n5️⃣ Testing Status Retrieval...")
    status = framework.get_status()
    assert isinstance(status, dict), "Status should be a dictionary"
    
    required_keys = ['version', 'initialized', 'running', 'dna', 'fitness', 'autonomy', 'storage', 'providers']
    for key in required_keys:
        assert key in status, f"Missing status key: {key}"
    
    assert status['version'] == "2.0.0", f"Wrong version in status: {status['version']}"
    assert status['initialized'] == True, "Status should show initialized=True"
    print("   ✅ Status retrieval working")
    
    # Test 6: Event system
    print("\n6️⃣ Testing Event System...")
    events_received = []
    
    def test_handler(event):
        events_received.append(event)
    
    framework.event_bus.subscribe("test_event", test_handler)
    framework.event_bus.publish("test_event", {"test": "data"})
    
    assert len(events_received) > 0, "Event not received"
    print("   ✅ Event system working")
    
    # Test 7: Configuration loading
    print("\n7️⃣ Testing Configuration...")
    config = framework.config
    assert config is not None, "Configuration not loaded"
    assert hasattr(config, 'storage'), "Storage config missing"
    assert hasattr(config, 'autonomy'), "Autonomy config missing"
    assert hasattr(config, 'fitness'), "Fitness config missing"
    print("   ✅ Configuration loaded")
    
    # Test 8: Component interactions
    print("\n8️⃣ Testing Component Interactions...")
    
    # Test fitness calculation
    fitness = framework.get_fitness()
    assert fitness is not None, "Fitness calculation failed"
    assert hasattr(fitness, 'overall'), "Fitness missing overall score"
    print(f"   ✅ Fitness calculation: {fitness.overall}")
    
    # Test storage status
    storage_status = framework.storage.get_sync_status()
    assert isinstance(storage_status, dict), "Storage status should be dict"
    print("   ✅ Storage status retrieval")
    
    # Test provider stats
    provider_stats = framework.providers.get_stats()
    assert isinstance(provider_stats, dict), "Provider stats should be dict"
    print("   ✅ Provider stats retrieval")
    
    print("\n✨ All Framework Initialization Tests Passed!")
    return True


def test_component_dependencies():
    """Test that components have proper dependencies"""
    print("\n🔗 Testing Component Dependencies")
    print("=" * 50)
    
    framework = EvolvingAIFramework()
    framework.initialize()
    
    # Test mutation engine dependencies
    print("\n1️⃣ Testing Mutation Engine Dependencies...")
    assert framework.mutation_engine.dna_manager is not None, "MutationEngine missing DNA manager"
    assert framework.mutation_engine.autonomy is not None, "MutationEngine missing autonomy controller"
    assert framework.mutation_engine.rollback is not None, "MutationEngine missing rollback manager"
    print("   ✅ Mutation engine dependencies verified")
    
    # Test autonomy controller
    print("\n2️⃣ Testing Autonomy Controller...")
    assert framework.autonomy.config is not None, "AutonomyController missing config"
    print("   ✅ Autonomy controller dependencies verified")
    
    # Test storage sync
    print("\n3️⃣ Testing Storage Sync...")
    assert framework.storage is not None, "StorageSync not initialized"
    assert hasattr(framework.storage, 'local'), "StorageSync missing local storage"
    print("   ✅ Storage sync dependencies verified")
    
    # Test self healer
    print("\n4️⃣ Testing Self Healer...")
    assert framework.healer.rollback is not None, "SelfHealer missing rollback manager"
    assert framework.healer.storage is not None, "SelfHealer missing storage sync"
    print("   ✅ Self healer dependencies verified")
    
    print("\n✨ All Component Dependencies Verified!")
    return True


def main():
    """Run all initialization tests"""
    try:
        print("🚀 Starting Framework Initialization Tests")
        print("=" * 60)
        
        # Run tests
        test_framework_initialization()
        test_component_dependencies()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("Framework initialization and component loading verified successfully.")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)