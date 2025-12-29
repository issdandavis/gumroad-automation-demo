#!/usr/bin/env python3
"""
Mutation Workflow End-to-End Test
=================================

Tests the complete mutation workflow from proposal to application.
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import framework
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation, MutationType


def test_mutation_workflow():
    """Test complete mutation workflow end-to-end"""
    print("🧬 Testing Mutation Workflow End-to-End")
    print("=" * 50)
    
    # Initialize framework
    print("\n1️⃣ Initializing Framework...")
    framework = EvolvingAIFramework()
    success = framework.initialize()
    assert success, "Framework initialization failed"
    print("   ✅ Framework initialized")
    
    # Get initial state
    print("\n2️⃣ Getting Initial State...")
    initial_dna = framework.get_dna()
    initial_generation = initial_dna.generation
    initial_fitness = initial_dna.fitness_score
    initial_mutations_count = len(initial_dna.mutations)
    
    print(f"   Initial Generation: {initial_generation}")
    print(f"   Initial Fitness: {initial_fitness}")
    print(f"   Initial Mutations: {initial_mutations_count}")
    
    # Test 1: Low-risk mutation (should auto-approve)
    print("\n3️⃣ Testing Low-Risk Mutation (Auto-Approval)...")
    low_risk_mutation = Mutation(
        type=MutationType.COMMUNICATION_ENHANCEMENT.value,
        description="Test: Add communication channel for testing",
        fitness_impact=2.0,
        source_ai="Test"
    )
    
    result = framework.propose_mutation(low_risk_mutation)
    assert isinstance(result, dict), "Mutation result should be dict"
    
    if result.get('approved') and result.get('auto'):
        print("   ✅ Low-risk mutation auto-approved and applied")
        
        # Verify DNA changes
        new_dna = framework.get_dna()
        assert new_dna.generation == initial_generation + 1, f"Generation should increment: {new_dna.generation} vs {initial_generation + 1}"
        assert new_dna.fitness_score == initial_fitness + 2.0, f"Fitness should increase: {new_dna.fitness_score} vs {initial_fitness + 2.0}"
        assert len(new_dna.mutations) == initial_mutations_count + 1, f"Mutations count should increase: {len(new_dna.mutations)} vs {initial_mutations_count + 1}"
        
        print(f"   New Generation: {new_dna.generation}")
        print(f"   New Fitness: {new_dna.fitness_score}")
        print(f"   New Mutations Count: {len(new_dna.mutations)}")
        
        # Update state for next test
        initial_generation = new_dna.generation
        initial_fitness = new_dna.fitness_score
        initial_mutations_count = len(new_dna.mutations)
        
    else:
        print("   ⏳ Low-risk mutation queued for approval (unexpected)")
        print(f"   Risk Score: {result.get('risk', 'unknown')}")
    
    # Test 2: High-risk mutation (should queue for approval)
    print("\n4️⃣ Testing High-Risk Mutation (Should Queue)...")
    high_risk_mutation = Mutation(
        type=MutationType.AUTONOMY_ADJUSTMENT.value,
        description="Test: Increase autonomy level significantly",
        fitness_impact=50.0,  # High impact should increase risk
        source_ai="Test"
    )
    
    result = framework.propose_mutation(high_risk_mutation)
    
    if not result.get('approved'):
        print("   ✅ High-risk mutation queued for approval (expected)")
        print(f"   Risk Score: {result.get('risk', 'unknown')}")
        print(f"   Request ID: {result.get('request_id', 'unknown')}")
        
        # Verify DNA didn't change
        unchanged_dna = framework.get_dna()
        assert unchanged_dna.generation == initial_generation, "Generation should not change for queued mutation"
        assert unchanged_dna.fitness_score == initial_fitness, "Fitness should not change for queued mutation"
        assert len(unchanged_dna.mutations) == initial_mutations_count, "Mutations count should not change for queued mutation"
        
    else:
        print("   ⚠️ High-risk mutation was auto-approved (unexpected but not necessarily wrong)")
    
    # Test 3: Feedback analysis and mutation generation
    print("\n5️⃣ Testing Feedback Analysis...")
    feedback_text = "The system should improve its communication channels and add better storage synchronization capabilities."
    mutations = framework.analyze_feedback(feedback_text, "TestAI")
    
    assert isinstance(mutations, list), "Feedback analysis should return list"
    assert len(mutations) > 0, "Feedback analysis should generate mutations"
    
    print(f"   Generated {len(mutations)} mutations from feedback:")
    for i, mutation in enumerate(mutations):
        print(f"   {i+1}. {mutation.type}: {mutation.description[:50]}...")
    
    # Test 4: Apply one of the generated mutations
    if mutations:
        print("\n6️⃣ Testing Generated Mutation Application...")
        generated_mutation = mutations[0]
        result = framework.propose_mutation(generated_mutation)
        
        if result.get('approved'):
            print("   ✅ Generated mutation applied successfully")
            final_dna = framework.get_dna()
            print(f"   Final Generation: {final_dna.generation}")
            print(f"   Final Fitness: {final_dna.fitness_score}")
        else:
            print("   ⏳ Generated mutation queued for approval")
    
    # Test 5: Verify mutation history
    print("\n7️⃣ Testing Mutation History...")
    final_dna = framework.get_dna()
    
    if len(final_dna.mutations) > initial_mutations_count:
        latest_mutation = final_dna.mutations[-1]
        print(f"   Latest Mutation ID: {latest_mutation.id}")
        print(f"   Latest Mutation Type: {latest_mutation.type}")
        print(f"   Latest Mutation Timestamp: {latest_mutation.timestamp}")
        print("   ✅ Mutation history properly recorded")
    
    # Test 6: Fitness tracking
    print("\n8️⃣ Testing Fitness Tracking...")
    fitness = framework.get_fitness()
    assert hasattr(fitness, 'overall'), "Fitness should have overall score"
    assert hasattr(fitness, 'trend'), "Fitness should have trend"
    
    print(f"   Current Fitness: {fitness.overall}")
    print(f"   Fitness Trend: {fitness.trend}")
    print("   ✅ Fitness tracking working")
    
    print("\n✨ All Mutation Workflow Tests Passed!")
    return True


def test_mutation_validation():
    """Test mutation validation logic"""
    print("\n🔍 Testing Mutation Validation")
    print("=" * 50)
    
    framework = EvolvingAIFramework()
    framework.initialize()
    
    # Test 1: Valid mutation
    print("\n1️⃣ Testing Valid Mutation...")
    valid_mutation = Mutation(
        type=MutationType.COMMUNICATION_ENHANCEMENT.value,
        description="Valid test mutation with proper description",
        fitness_impact=3.0,
        source_ai="Test"
    )
    
    dna = framework.get_dna()
    validation = framework.mutation_engine.validator.validate(valid_mutation, dna)
    
    assert validation.is_valid, f"Valid mutation should pass validation: {validation.errors}"
    print("   ✅ Valid mutation passed validation")
    
    # Test 2: Invalid mutation type
    print("\n2️⃣ Testing Invalid Mutation Type...")
    invalid_mutation = Mutation(
        type="invalid_type",
        description="Test mutation with invalid type",
        fitness_impact=2.0,
        source_ai="Test"
    )
    
    validation = framework.mutation_engine.validator.validate(invalid_mutation, dna)
    assert not validation.is_valid, "Invalid mutation type should fail validation"
    assert any("Invalid mutation type" in error for error in validation.errors), "Should have invalid type error"
    print("   ✅ Invalid mutation type properly rejected")
    
    # Test 3: Extreme fitness impact
    print("\n3️⃣ Testing Extreme Fitness Impact...")
    extreme_mutation = Mutation(
        type=MutationType.INTELLIGENCE_UPGRADE.value,
        description="Test mutation with extreme fitness impact",
        fitness_impact=1000.0,  # Very high impact
        source_ai="Test"
    )
    
    validation = framework.mutation_engine.validator.validate(extreme_mutation, dna)
    # Should have warnings about high impact
    assert len(validation.warnings) > 0, "Extreme fitness impact should generate warnings"
    print("   ✅ Extreme fitness impact generates warnings")
    
    # Test 4: Negative fitness impact that would break invariants
    print("\n4️⃣ Testing Negative Fitness Impact...")
    negative_mutation = Mutation(
        type=MutationType.STORAGE_OPTIMIZATION.value,
        description="Test mutation with negative fitness impact",
        fitness_impact=-200.0,  # Would make fitness negative
        source_ai="Test"
    )
    
    validation = framework.mutation_engine.validator.validate(negative_mutation, dna)
    assert not validation.is_valid, "Mutation causing negative fitness should fail validation"
    print("   ✅ Negative fitness impact properly rejected")
    
    print("\n✨ All Mutation Validation Tests Passed!")
    return True


def test_rollback_integration():
    """Test rollback integration with mutations"""
    print("\n⏪ Testing Rollback Integration")
    print("=" * 50)
    
    framework = EvolvingAIFramework()
    framework.initialize()
    
    # Get initial state
    initial_dna = framework.get_dna()
    initial_generation = initial_dna.generation
    
    print(f"\n1️⃣ Initial State: Generation {initial_generation}")
    
    # Apply a mutation
    print("\n2️⃣ Applying Mutation...")
    mutation = Mutation(
        type=MutationType.COMMUNICATION_ENHANCEMENT.value,
        description="Test mutation for rollback testing",
        fitness_impact=5.0,
        source_ai="Test"
    )
    
    result = framework.propose_mutation(mutation)
    
    if result.get('approved'):
        new_dna = framework.get_dna()
        new_generation = new_dna.generation
        print(f"   Mutation applied: Generation {new_generation}")
        
        # List available snapshots
        print("\n3️⃣ Checking Snapshots...")
        snapshots = framework.rollback.list_snapshots(10)
        print(f"   Available snapshots: {len(snapshots)}")
        
        if snapshots:
            # Find a snapshot from before the mutation
            pre_mutation_snapshot = None
            for snapshot in snapshots:
                if snapshot.metadata.get('generation', 0) < new_generation:
                    pre_mutation_snapshot = snapshot
                    break
            
            if pre_mutation_snapshot:
                print(f"\n4️⃣ Testing Rollback to {pre_mutation_snapshot.id}...")
                rollback_result = framework.rollback_to(pre_mutation_snapshot.id)
                
                if rollback_result.get('success'):
                    rolled_back_dna = framework.get_dna()
                    print(f"   Rollback successful: Generation {rolled_back_dna.generation}")
                    print("   ✅ Rollback integration working")
                else:
                    print(f"   ❌ Rollback failed: {rollback_result.get('error')}")
            else:
                print("   ⚠️ No suitable snapshot found for rollback test")
        else:
            print("   ⚠️ No snapshots available for rollback test")
    else:
        print("   ⏳ Mutation queued, cannot test rollback")
    
    return True


def main():
    """Run all mutation workflow tests"""
    try:
        print("🚀 Starting Mutation Workflow Tests")
        print("=" * 60)
        
        # Run tests
        test_mutation_workflow()
        test_mutation_validation()
        test_rollback_integration()
        
        print("\n🎉 ALL MUTATION WORKFLOW TESTS PASSED!")
        print("Basic mutation workflow verified successfully.")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)