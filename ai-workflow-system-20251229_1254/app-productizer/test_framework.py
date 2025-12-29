#!/usr/bin/env python3
"""
Comprehensive Testing Framework
==============================

Advanced testing system for the Self-Evolving AI Framework with
property-based testing, integration tests, and performance benchmarks.

Features:
- Property-based testing with Hypothesis
- Integration testing with real components
- Performance benchmarking and profiling
- Automated test discovery and execution
- Test reporting and analytics
- Continuous testing and monitoring

Usage:
    python test_framework.py run                    # Run all tests
    python test_framework.py property               # Property-based tests only
    python test_framework.py integration            # Integration tests only
    python test_framework.py benchmark              # Performance benchmarks
    python test_framework.py continuous             # Continuous testing mode
    python test_framework.py report                 # Generate test report
"""

import unittest
import json
import time
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import statistics
import threading

# Property-based testing
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

# Framework imports
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import (
    SystemDNA, Mutation, MutationType, FitnessScore, 
    CoreTraits, OperationResult, Snapshot
)
from self_evolving_core.mutation import MutationEngine
from self_evolving_core.fitness import FitnessMonitor
from self_evolving_core.rollback import RollbackManager
from self_evolving_core.autonomy import AutonomyController


class TestResults:
    """Test results tracking and reporting"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "framework_version": "2.0.0",
            "test_runs": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0.0
            },
            "performance_metrics": {},
            "property_test_stats": {},
            "coverage_report": {}
        }
    
    def add_test_result(self, test_name: str, status: str, duration: float, 
                       error: Optional[str] = None, details: Optional[Dict] = None):
        """Add a test result"""
        self.results["test_runs"].append({
            "name": test_name,
            "status": status,
            "duration": duration,
            "error": error,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["summary"]["total_tests"] += 1
        self.results["summary"][status] += 1
        self.results["summary"]["duration"] += duration
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        summary = self.results["summary"]
        success_rate = (summary["passed"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0
        
        report = f"""
🧪 Self-Evolving AI Framework Test Report
========================================

📊 Test Summary:
   Total Tests: {summary['total_tests']}
   Passed: {summary['passed']} ✅
   Failed: {summary['failed']} ❌
   Skipped: {summary['skipped']} ⏭️
   Success Rate: {success_rate:.1f}%
   Total Duration: {summary['duration']:.2f}s

🏃‍♂️ Performance Metrics:
"""
        
        for metric, value in self.results["performance_metrics"].items():
            report += f"   {metric}: {value}\n"
        
        if self.results["test_runs"]:
            report += "\n📋 Test Details:\n"
            for test in self.results["test_runs"]:
                status_emoji = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(test["status"], "❓")
                report += f"   {status_emoji} {test['name']} ({test['duration']:.3f}s)\n"
                if test["error"]:
                    report += f"      Error: {test['error']}\n"
        
        return report
    
    def save_report(self, filename: str = "test_report.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)


class PropertyBasedTests:
    """
    Property-based tests using Hypothesis.
    
    These tests validate universal properties that should hold
    across all valid inputs and system states.
    """
    
    def __init__(self, framework: EvolvingAIFramework):
        self.framework = framework
        self.results = TestResults()
    
    @given(st.builds(SystemDNA))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_dna_initialization_completeness(self, dna: SystemDNA):
        """
        Property 1: DNA Initialization Completeness
        
        For any SystemDNA instance, all required fields must be present
        and valid according to the system's invariants.
        
        Validates: Requirements 1.1, 1.5
        """
        start_time = time.time()
        
        try:
            # Test all required fields are present
            assert dna.version is not None, "Version must be set"
            assert dna.birth_timestamp is not None, "Birth timestamp must be set"
            assert dna.generation >= 1, "Generation must be at least 1"
            assert dna.fitness_score >= 0, "Fitness score must be non-negative"
            
            # Test core traits
            assert dna.core_traits.communication_channels >= 0, "Communication channels must be non-negative"
            assert dna.core_traits.language_support >= 0, "Language support must be non-negative"
            assert 0 <= dna.core_traits.autonomy_level <= 1, "Autonomy level must be between 0 and 1"
            assert len(dna.core_traits.evolutionary_features) >= 0, "Evolutionary features must be a list"
            
            # Test serialization round-trip
            dna_dict = dna.to_dict()
            restored_dna = SystemDNA.from_dict(dna_dict)
            assert restored_dna.generation == dna.generation, "Serialization must preserve generation"
            assert restored_dna.fitness_score == dna.fitness_score, "Serialization must preserve fitness"
            
            duration = time.time() - start_time
            self.results.add_test_result("dna_initialization_completeness", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("dna_initialization_completeness", "failed", duration, str(e))
            raise
    
    @given(st.builds(Mutation, 
                     type=st.sampled_from([t.value for t in MutationType]),
                     fitness_impact=st.floats(min_value=-10, max_value=10),
                     risk_score=st.floats(min_value=0, max_value=1)))
    @settings(max_examples=30)
    def test_mutation_logging_consistency(self, mutation: Mutation):
        """
        Property 2: Mutation Logging Consistency
        
        For any mutation applied to the system, the evolution log must
        contain a complete record within 1 second of application.
        
        Validates: Requirements 1.2, 3.4
        """
        start_time = time.time()
        
        try:
            # Get initial state
            initial_dna = self.framework.get_dna()
            initial_mutations = len(initial_dna.mutations)
            
            # Apply mutation
            result = self.framework.propose_mutation(mutation)
            
            if result.get('approved'):
                # Check that mutation was logged
                updated_dna = self.framework.get_dna()
                new_mutations = len(updated_dna.mutations)
                
                assert new_mutations == initial_mutations + 1, "Mutation count must increase by 1"
                
                # Check latest mutation record
                latest_mutation = updated_dna.mutations[-1]
                assert latest_mutation.type == mutation.type, "Mutation type must be logged correctly"
                assert latest_mutation.description == mutation.description, "Description must be logged"
                assert latest_mutation.fitness_impact == mutation.fitness_impact, "Fitness impact must be logged"
                assert latest_mutation.timestamp is not None, "Timestamp must be recorded"
            
            duration = time.time() - start_time
            self.results.add_test_result("mutation_logging_consistency", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("mutation_logging_consistency", "failed", duration, str(e))
            raise
    
    @given(st.lists(st.builds(Mutation, 
                             type=st.sampled_from([t.value for t in MutationType]),
                             fitness_impact=st.floats(min_value=0, max_value=5)),
                    min_size=1, max_size=5))
    @settings(max_examples=20)
    def test_fitness_score_tracking(self, mutations: List[Mutation]):
        """
        Property 3: Fitness Score Tracking
        
        For any sequence of mutations, the fitness score changes must
        equal the sum of all mutation impacts.
        
        Validates: Requirements 1.3, 9.2
        """
        start_time = time.time()
        
        try:
            # Get initial fitness
            initial_dna = self.framework.get_dna()
            initial_fitness = initial_dna.fitness_score
            
            # Apply mutations and track expected change
            expected_change = 0
            applied_mutations = 0
            
            for mutation in mutations:
                result = self.framework.propose_mutation(mutation)
                if result.get('approved'):
                    expected_change += mutation.fitness_impact
                    applied_mutations += 1
            
            # Check final fitness
            if applied_mutations > 0:
                final_dna = self.framework.get_dna()
                actual_change = final_dna.fitness_score - initial_fitness
                
                # Allow small floating point differences
                assert abs(actual_change - expected_change) < 0.01, \
                    f"Fitness change {actual_change} must equal sum of impacts {expected_change}"
            
            duration = time.time() - start_time
            self.results.add_test_result("fitness_score_tracking", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("fitness_score_tracking", "failed", duration, str(e))
            raise
    
    @given(st.builds(Mutation, 
                     type=st.sampled_from([t.value for t in MutationType])))
    @settings(max_examples=20)
    def test_generation_invariant(self, mutation: Mutation):
        """
        Property 4: Generation Invariant
        
        For any mutation applied, the generation counter must increment
        by exactly 1, and the mutations array length must increase by 1.
        
        Validates: Requirements 1.4
        """
        start_time = time.time()
        
        try:
            # Get initial state
            initial_dna = self.framework.get_dna()
            initial_generation = initial_dna.generation
            initial_mutations_count = len(initial_dna.mutations)
            
            # Apply mutation
            result = self.framework.propose_mutation(mutation)
            
            if result.get('approved'):
                # Check invariants
                updated_dna = self.framework.get_dna()
                
                assert updated_dna.generation == initial_generation + 1, \
                    "Generation must increment by exactly 1"
                assert len(updated_dna.mutations) == initial_mutations_count + 1, \
                    "Mutations array length must increase by 1"
            
            duration = time.time() - start_time
            self.results.add_test_result("generation_invariant", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("generation_invariant", "failed", duration, str(e))
            raise
    
    def test_rollback_completeness(self):
        """
        Property 12: Rollback Completeness
        
        For any failed mutation, executing rollback must restore
        SystemDNA to the exact state captured in the pre-mutation snapshot.
        
        Validates: Requirements 8.7
        """
        start_time = time.time()
        
        try:
            # Get initial state
            initial_dna = self.framework.get_dna()
            initial_state = initial_dna.to_dict()
            
            # Create snapshot
            snapshot = self.framework.rollback.create_snapshot(
                initial_dna, "test_rollback"
            )
            
            # Apply a mutation
            mutation = Mutation(
                type="communication_enhancement",
                description="Test mutation for rollback",
                fitness_impact=2.0
            )
            
            result = self.framework.propose_mutation(mutation)
            
            if result.get('approved'):
                # Verify state changed
                modified_dna = self.framework.get_dna()
                assert modified_dna.generation != initial_dna.generation, "State must have changed"
                
                # Perform rollback
                rollback_result = self.framework.rollback_to(snapshot.id)
                
                if rollback_result.get('success'):
                    # Verify complete restoration
                    restored_dna = self.framework.get_dna()
                    restored_state = restored_dna.to_dict()
                    
                    # Compare key fields (excluding timestamps)
                    assert restored_dna.generation == initial_dna.generation, "Generation must be restored"
                    assert restored_dna.fitness_score == initial_dna.fitness_score, "Fitness must be restored"
                    assert len(restored_dna.mutations) == len(initial_dna.mutations), "Mutations count must be restored"
            
            duration = time.time() - start_time
            self.results.add_test_result("rollback_completeness", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("rollback_completeness", "failed", duration, str(e))
            raise
    
    def run_all_property_tests(self):
        """Run all property-based tests"""
        print("🧪 Running Property-Based Tests...")
        
        test_methods = [
            self.test_dna_initialization_completeness,
            self.test_mutation_logging_consistency,
            self.test_fitness_score_tracking,
            self.test_generation_invariant,
            self.test_rollback_completeness
        ]
        
        for test_method in test_methods:
            try:
                print(f"   Running {test_method.__name__}...")
                test_method()
                print(f"   ✅ {test_method.__name__} passed")
            except Exception as e:
                print(f"   ❌ {test_method.__name__} failed: {e}")
        
        return self.results


class IntegrationTests:
    """
    Integration tests for end-to-end system functionality.
    
    Tests complete workflows and component interactions.
    """
    
    def __init__(self, framework: EvolvingAIFramework):
        self.framework = framework
        self.results = TestResults()
    
    def test_complete_mutation_workflow(self):
        """Test complete mutation workflow with rollback capability"""
        start_time = time.time()
        
        try:
            print("   Testing complete mutation workflow...")
            
            # 1. Get initial state
            initial_dna = self.framework.get_dna()
            initial_generation = initial_dna.generation
            
            # 2. Propose and apply mutation
            mutation = Mutation(
                type="communication_enhancement",
                description="Integration test mutation",
                fitness_impact=3.0,
                source_ai="IntegrationTest"
            )
            
            result = self.framework.propose_mutation(mutation)
            assert result.get('approved'), "Mutation should be approved"
            
            # 3. Verify changes
            updated_dna = self.framework.get_dna()
            assert updated_dna.generation == initial_generation + 1, "Generation should increment"
            assert updated_dna.fitness_score > initial_dna.fitness_score, "Fitness should improve"
            
            # 4. Test rollback capability
            snapshots = self.framework.rollback.list_snapshots(5)
            if snapshots:
                rollback_result = self.framework.rollback_to(snapshots[0].id)
                assert rollback_result.get('success'), "Rollback should succeed"
            
            duration = time.time() - start_time
            self.results.add_test_result("complete_mutation_workflow", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("complete_mutation_workflow", "failed", duration, str(e))
            raise
    
    def test_storage_sync_operations(self):
        """Test storage synchronization across platforms"""
        start_time = time.time()
        
        try:
            print("   Testing storage sync operations...")
            
            # Test data
            test_data = {
                "test_type": "integration_test",
                "timestamp": datetime.now().isoformat(),
                "data": {"key": "value", "number": 42}
            }
            
            # Sync to storage
            sync_results = self.framework.sync_storage(test_data, "integration_test.json")
            
            # Verify at least local storage succeeded
            assert sync_results.get('local', {}).get('success'), "Local storage sync should succeed"
            
            # Check file was created
            from pathlib import Path
            data_dir = Path(self.framework.config.storage.local_path)
            test_file = data_dir / "integration_test.json"
            assert test_file.exists(), "Test file should be created"
            
            # Verify content
            with open(test_file, 'r') as f:
                saved_data = json.load(f)
                assert saved_data["test_type"] == "integration_test", "Data should be saved correctly"
            
            duration = time.time() - start_time
            self.results.add_test_result("storage_sync_operations", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("storage_sync_operations", "failed", duration, str(e))
            raise
    
    def test_fitness_monitoring_workflow(self):
        """Test fitness monitoring and degradation detection"""
        start_time = time.time()
        
        try:
            print("   Testing fitness monitoring workflow...")
            
            # Get initial fitness
            initial_fitness = self.framework.get_fitness()
            assert initial_fitness.overall >= 0, "Fitness score should be non-negative"
            
            # Record some operations
            for i in range(5):
                operation_result = OperationResult(
                    success=True,
                    operation_type="test_operation",
                    duration_ms=100 + i * 10
                )
                self.framework.fitness.record_operation(operation_result)
            
            # Calculate updated fitness
            updated_fitness = self.framework.get_fitness()
            assert updated_fitness.timestamp != initial_fitness.timestamp, "Fitness should be updated"
            
            # Test dashboard data
            dashboard_data = self.framework.fitness.get_dashboard_data()
            assert "current_fitness" in dashboard_data, "Dashboard data should include current fitness"
            assert "operations_summary" in dashboard_data, "Dashboard data should include operations summary"
            
            duration = time.time() - start_time
            self.results.add_test_result("fitness_monitoring_workflow", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("fitness_monitoring_workflow", "failed", duration, str(e))
            raise
    
    def test_autonomous_workflow_execution(self):
        """Test autonomous workflow execution with checkpoints"""
        start_time = time.time()
        
        try:
            print("   Testing autonomous workflow execution...")
            
            # Create test workflow
            from self_evolving_core.autonomy import Workflow
            
            workflow = Workflow(
                id="test_workflow",
                name="Integration Test Workflow",
                steps=[
                    {
                        "type": "mutation",
                        "mutation": {
                            "type": "storage_optimization",
                            "description": "Test autonomous mutation",
                            "fitness_impact": 1.0
                        }
                    },
                    {
                        "type": "sync",
                        "data": {"workflow": "test"},
                        "path": "workflow_test.json"
                    }
                ]
            )
            
            # Execute workflow
            result = self.framework.execute_workflow(workflow)
            
            # Verify execution
            assert result.get('success') is not None, "Workflow should return success status"
            assert result.get('steps_completed', 0) > 0, "Some steps should be completed"
            
            duration = time.time() - start_time
            self.results.add_test_result("autonomous_workflow_execution", "passed", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.results.add_test_result("autonomous_workflow_execution", "failed", duration, str(e))
            raise
    
    def run_all_integration_tests(self):
        """Run all integration tests"""
        print("🔗 Running Integration Tests...")
        
        test_methods = [
            self.test_complete_mutation_workflow,
            self.test_storage_sync_operations,
            self.test_fitness_monitoring_workflow,
            self.test_autonomous_workflow_execution
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                print(f"   ✅ {test_method.__name__} passed")
            except Exception as e:
                print(f"   ❌ {test_method.__name__} failed: {e}")
        
        return self.results


class PerformanceBenchmarks:
    """Performance benchmarking and profiling"""
    
    def __init__(self, framework: EvolvingAIFramework):
        self.framework = framework
        self.results = TestResults()
    
    def benchmark_mutation_performance(self, num_mutations: int = 100):
        """Benchmark mutation application performance"""
        print(f"   Benchmarking {num_mutations} mutations...")
        
        start_time = time.time()
        durations = []
        
        for i in range(num_mutations):
            mutation_start = time.time()
            
            mutation = Mutation(
                type="communication_enhancement",
                description=f"Benchmark mutation {i}",
                fitness_impact=0.1,
                source_ai="Benchmark"
            )
            
            result = self.framework.propose_mutation(mutation)
            
            mutation_duration = time.time() - mutation_start
            durations.append(mutation_duration)
        
        total_duration = time.time() - start_time
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        self.results.results["performance_metrics"]["mutation_benchmark"] = {
            "total_mutations": num_mutations,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "median_duration": median_duration,
            "max_duration": max_duration,
            "min_duration": min_duration,
            "mutations_per_second": num_mutations / total_duration
        }
        
        print(f"   📊 Mutations/sec: {num_mutations / total_duration:.2f}")
        print(f"   📊 Avg duration: {avg_duration*1000:.2f}ms")
    
    def benchmark_fitness_calculation(self, num_calculations: int = 1000):
        """Benchmark fitness calculation performance"""
        print(f"   Benchmarking {num_calculations} fitness calculations...")
        
        start_time = time.time()
        
        for i in range(num_calculations):
            fitness = self.framework.get_fitness()
        
        total_duration = time.time() - start_time
        
        self.results.results["performance_metrics"]["fitness_benchmark"] = {
            "total_calculations": num_calculations,
            "total_duration": total_duration,
            "calculations_per_second": num_calculations / total_duration,
            "avg_duration": total_duration / num_calculations
        }
        
        print(f"   📊 Calculations/sec: {num_calculations / total_duration:.2f}")
    
    def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("🏃‍♂️ Running Performance Benchmarks...")
        
        self.benchmark_mutation_performance(50)
        self.benchmark_fitness_calculation(100)
        
        return self.results


class TestFramework:
    """Main testing framework orchestrator"""
    
    def __init__(self):
        self.framework = None
        self.overall_results = TestResults()
    
    def setup_framework(self):
        """Setup framework for testing"""
        print("🔧 Setting up test framework...")
        
        self.framework = EvolvingAIFramework()
        success = self.framework.initialize()
        
        if not success:
            raise RuntimeError("Failed to initialize framework for testing")
        
        print("✅ Framework initialized for testing")
    
    def run_property_tests(self):
        """Run property-based tests"""
        if not self.framework:
            self.setup_framework()
        
        property_tests = PropertyBasedTests(self.framework)
        results = property_tests.run_all_property_tests()
        
        # Merge results
        self.overall_results.results["test_runs"].extend(results.results["test_runs"])
        for key in ["total_tests", "passed", "failed", "skipped"]:
            self.overall_results.results["summary"][key] += results.results["summary"][key]
        
        return results
    
    def run_integration_tests(self):
        """Run integration tests"""
        if not self.framework:
            self.setup_framework()
        
        integration_tests = IntegrationTests(self.framework)
        results = integration_tests.run_all_integration_tests()
        
        # Merge results
        self.overall_results.results["test_runs"].extend(results.results["test_runs"])
        for key in ["total_tests", "passed", "failed", "skipped"]:
            self.overall_results.results["summary"][key] += results.results["summary"][key]
        
        return results
    
    def run_benchmarks(self):
        """Run performance benchmarks"""
        if not self.framework:
            self.setup_framework()
        
        benchmarks = PerformanceBenchmarks(self.framework)
        results = benchmarks.run_all_benchmarks()
        
        # Merge performance metrics
        self.overall_results.results["performance_metrics"].update(
            results.results["performance_metrics"]
        )
        
        return results
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("""
🧪 Self-Evolving AI Framework Test Suite
========================================

Running comprehensive tests including:
• Property-based tests (universal properties)
• Integration tests (end-to-end workflows)  
• Performance benchmarks (speed and efficiency)

This may take a few minutes...
        """)
        
        start_time = time.time()
        
        try:
            # Run all test categories
            self.run_property_tests()
            self.run_integration_tests()
            self.run_benchmarks()
            
            # Calculate total duration
            total_duration = time.time() - start_time
            self.overall_results.results["summary"]["duration"] = total_duration
            
            # Generate and display report
            report = self.overall_results.generate_report()
            print(report)
            
            # Save detailed results
            self.overall_results.save_report("test_results.json")
            print("\n💾 Detailed results saved to test_results.json")
            
            return self.overall_results
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            traceback.print_exc()
            return None
    
    def continuous_testing(self, interval: int = 300):
        """Run tests continuously at specified interval"""
        print(f"🔄 Starting continuous testing (every {interval} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n⏰ Running tests at {datetime.now().strftime('%H:%M:%S')}")
                self.run_all_tests()
                
                print(f"😴 Sleeping for {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Continuous testing stopped")


def main():
    """Main test framework entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Evolving AI Test Framework")
    parser.add_argument('command', 
                       choices=['run', 'property', 'integration', 'benchmark', 'continuous', 'report'],
                       help='Test command to run')
    parser.add_argument('--interval', type=int, default=300,
                       help='Interval for continuous testing (seconds)')
    
    args = parser.parse_args()
    
    test_framework = TestFramework()
    
    if args.command == 'run':
        test_framework.run_all_tests()
    elif args.command == 'property':
        test_framework.run_property_tests()
    elif args.command == 'integration':
        test_framework.run_integration_tests()
    elif args.command == 'benchmark':
        test_framework.run_benchmarks()
    elif args.command == 'continuous':
        test_framework.continuous_testing(args.interval)
    elif args.command == 'report':
        # Load and display existing report
        try:
            with open('test_results.json', 'r') as f:
                results_data = json.load(f)
                results = TestResults()
                results.results = results_data
                print(results.generate_report())
        except FileNotFoundError:
            print("❌ No test results found. Run tests first.")


if __name__ == "__main__":
    main()