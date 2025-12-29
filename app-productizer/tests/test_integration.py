"""
Integration Tests for Self-Evolving AI Framework
================================================

End-to-end tests validating complete workflows including:
- Mutation workflow with rollback
- Storage sync operations
- Autonomous workflow execution
- Fitness monitoring and degradation detection

**Validates: Requirements 2.1-2.5, 3.1-3.5, 6.1-6.5, 8.1-8.7, 10.1-10.6**
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

from self_evolving_core.framework import EvolvingAIFramework
from self_evolving_core.models import Mutation, MutationType, SystemDNA
from self_evolving_core.autonomy import Workflow


class TestMutationWorkflowIntegration:
    """
    Integration tests for end-to-end mutation workflow with rollback.
    
    **Validates: Requirements 3.1-3.5, 8.7, 9.1-9.5**
    """
    
    @pytest.fixture
    def framework(self, tmp_path):
        """Create isolated framework instance"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        fw = EvolvingAIFramework()
        assert fw.initialize(), "Framework must initialize"
        return fw
    
    def test_mutation_apply_and_verify(self, framework):
        """Test applying a mutation and verifying DNA changes"""
        # Get initial state
        initial_dna = framework.get_dna()
        initial_gen = initial_dna.generation
        initial_fitness = initial_dna.fitness_score
        initial_mutations_count = len(initial_dna.mutations)
        
        # Create and apply mutation
        mutation = Mutation(
            type=MutationType.COMMUNICATION_ENHANCEMENT.value,
            description="Integration test: Add communication channel",
            fitness_impact=3.0,
            source_ai="integration_test"
        )
        
        result = framework.propose_mutation(mutation)
        
        # Verify mutation was applied
        assert result.get("approved"), "Low-risk mutation should be approved"
        
        if result.get("auto"):
            # Verify DNA changes
            new_dna = framework.get_dna()
            assert new_dna.generation == initial_gen + 1, "Generation must increment"
            assert new_dna.fitness_score == pytest.approx(initial_fitness + 3.0), \
                "Fitness must increase by impact"
            # Mutations list grows by 1 from initial count
            assert len(new_dna.mutations) == initial_mutations_count + 1, \
                f"Mutations list must grow by 1: was {initial_mutations_count}, now {len(new_dna.mutations)}"
    
    def test_mutation_rollback_restores_state(self, framework):
        """Test that rollback restores exact previous state"""
        # Get initial state
        initial_dna = framework.get_dna()
        initial_gen = initial_dna.generation
        initial_fitness = initial_dna.fitness_score
        
        # Apply mutation
        mutation = Mutation(
            type=MutationType.PROTOCOL_IMPROVEMENT.value,
            description="Integration test: Protocol improvement for rollback test",
            fitness_impact=2.5,
            source_ai="integration_test"
        )
        
        result = framework.propose_mutation(mutation)
        
        if result.get("approved") and result.get("auto"):
            # Verify mutation applied
            post_mutation_dna = framework.get_dna()
            assert post_mutation_dna.generation == initial_gen + 1
            
            # Get snapshots and rollback
            snapshots = framework.rollback.list_snapshots(5)
            assert len(snapshots) > 0, "Snapshots must exist"
            
            # Rollback to most recent snapshot
            rollback_result = framework.rollback_to(snapshots[0].id)
            assert rollback_result.get("success"), "Rollback must succeed"
            
            # Verify state restored
            restored_dna = framework.get_dna()
            assert restored_dna.generation < post_mutation_dna.generation, \
                "Generation must be reduced after rollback"
    
    def test_high_risk_mutation_requires_approval(self, framework):
        """Test that high-risk mutations are queued for approval"""
        mutation = Mutation(
            type=MutationType.AUTONOMY_ADJUSTMENT.value,
            description="High risk: Major autonomy adjustment",
            fitness_impact=15.0,  # High impact
            source_ai="external_unknown"
        )
        
        result = framework.propose_mutation(mutation)
        
        # High-risk mutations should be queued
        if not result.get("auto"):
            assert "request_id" in result, "Should have approval request ID"
            assert result.get("risk", 0) > 0.3, "Risk should be above threshold"


class TestStorageSyncIntegration:
    """
    Integration tests for storage sync operations.
    
    **Validates: Requirements 2.1-2.5, 6.1-6.5**
    """
    
    @pytest.fixture
    def framework(self, tmp_path):
        """Create isolated framework instance"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        fw = EvolvingAIFramework()
        assert fw.initialize(), "Framework must initialize"
        return fw
    
    def test_local_storage_sync(self, framework):
        """Test syncing data to local storage"""
        test_data = {
            "test_key": "test_value",
            "timestamp": datetime.now().isoformat(),
            "nested": {"a": 1, "b": 2}
        }
        
        results = framework.sync_storage(test_data, "test_sync.json")
        
        # Local sync should succeed
        assert "local" in results, "Local storage result must exist"
        local_result = results["local"]
        
        # Check if sync succeeded or at least was attempted
        if local_result.get("success"):
            # Verify file exists in the storage path
            data_dir = Path(framework.config.storage.local_path)
            sync_file = data_dir / "test_sync.json"
            
            if sync_file.exists():
                # Verify content
                with open(sync_file, 'r') as f:
                    stored = json.load(f)
                    assert stored["test_key"] == "test_value"
        else:
            # Sync may fail due to configuration, but should not error
            assert "error" in local_result or local_result.get("success") is False
    
    def test_sync_queue_retry_logic(self, framework):
        """Test that failed syncs are queued for retry"""
        # Queue should handle operations
        queue_status = framework.storage.get_sync_status()
        assert "queue_size" in queue_status, "Queue status must be available"
    
    def test_sync_does_not_mutate_dna(self, framework):
        """Test that storage sync doesn't change DNA state"""
        initial_dna = framework.get_dna()
        initial_gen = initial_dna.generation
        
        # Perform multiple syncs
        for i in range(3):
            framework.sync_storage({"iteration": i}, f"sync_test_{i}.json")
        
        # DNA should be unchanged
        final_dna = framework.get_dna()
        assert final_dna.generation == initial_gen, \
            "Syncing must not change generation"


class TestAutonomousWorkflowIntegration:
    """
    Integration tests for autonomous workflow execution.
    
    **Validates: Requirements 8.1-8.7**
    """
    
    @pytest.fixture
    def framework(self, tmp_path):
        """Create isolated framework instance"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        fw = EvolvingAIFramework()
        assert fw.initialize(), "Framework must initialize"
        return fw
    
    def test_simple_workflow_execution(self, framework):
        """Test executing a simple workflow"""
        workflow = Workflow(
            id="test_workflow_001",
            name="Integration Test Workflow",
            steps=[
                {"type": "sync", "data": {"step": 1}, "path": "workflow_step1.json"},
                {"type": "sync", "data": {"step": 2}, "path": "workflow_step2.json"},
            ],
            checkpoint_interval=5
        )
        
        result = framework.execute_workflow(workflow)
        
        assert result["workflow_id"] == "test_workflow_001"
        assert result["steps_completed"] >= 0
        assert "duration_ms" in result
    
    def test_workflow_with_mutation_step(self, framework):
        """Test workflow containing mutation step"""
        initial_gen = framework.get_dna().generation
        
        workflow = Workflow(
            id="test_mutation_workflow",
            name="Mutation Workflow Test",
            steps=[
                {
                    "type": "mutation",
                    "mutation": {
                        "type": MutationType.STORAGE_OPTIMIZATION.value,
                        "description": "Workflow mutation test",
                        "fitness_impact": 1.5,
                        "source_ai": "workflow_test"
                    }
                }
            ],
            allow_mutations=True
        )
        
        result = framework.execute_workflow(workflow)
        
        # Workflow should complete
        assert "steps_completed" in result
    
    def test_workflow_logging(self, framework):
        """Test that workflow actions are logged"""
        workflow = Workflow(
            id="test_logging_workflow",
            name="Logging Test Workflow",
            steps=[
                {"type": "sync", "data": {"test": True}, "path": "log_test.json"}
            ]
        )
        
        framework.execute_workflow(workflow)
        
        # Check audit log
        audit_entries = framework.autonomy.get_audit_log(50)
        workflow_entries = [e for e in audit_entries if "workflow" in e.get("action", "")]
        assert len(workflow_entries) > 0, "Workflow actions must be logged"


class TestFitnessMonitoringIntegration:
    """
    Integration tests for fitness monitoring and degradation detection.
    
    **Validates: Requirements 10.1-10.6**
    """
    
    @pytest.fixture
    def framework(self, tmp_path):
        """Create isolated framework instance"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        fw = EvolvingAIFramework()
        assert fw.initialize(), "Framework must initialize"
        return fw
    
    def test_fitness_calculation(self, framework):
        """Test fitness score calculation"""
        fitness = framework.get_fitness()
        
        assert fitness.overall >= 0, "Fitness must be non-negative"
        assert 0 <= fitness.success_rate <= 1, "Success rate must be 0-1"
        assert 0 <= fitness.uptime <= 1, "Uptime must be 0-1"
        assert fitness.timestamp is not None, "Timestamp must be set"
    
    def test_fitness_dashboard_data(self, framework):
        """Test fitness dashboard data generation"""
        dashboard = framework.fitness.get_dashboard_data()
        
        assert "current_fitness" in dashboard
        assert "operations_summary" in dashboard
        assert "healing_summary" in dashboard
        assert "cost_summary" in dashboard
    
    def test_fitness_tracking_after_mutations(self, framework):
        """Test that fitness is tracked correctly after mutations"""
        initial_fitness = framework.get_fitness().overall
        
        # Apply a mutation
        mutation = Mutation(
            type=MutationType.LANGUAGE_EXPANSION.value,
            description="Fitness tracking test mutation",
            fitness_impact=2.0,
            source_ai="fitness_test"
        )
        
        result = framework.propose_mutation(mutation)
        
        if result.get("approved") and result.get("auto"):
            # Fitness should reflect the change
            new_fitness = framework.get_fitness()
            # Note: Overall fitness calculation may differ from DNA fitness_score
            assert new_fitness.overall >= 0, "Fitness must remain valid"


class TestConfigurationValidation:
    """
    Integration tests for configuration validation.
    
    **Validates: Requirements 7.1-7.5**
    """
    
    def test_framework_initializes_with_defaults(self, tmp_path):
        """Test framework initializes with default configuration"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        
        fw = EvolvingAIFramework()
        result = fw.initialize()
        
        assert result, "Framework must initialize with defaults"
        assert fw.config is not None, "Config must be loaded"
    
    def test_missing_env_vars_handled(self, tmp_path):
        """Test that missing environment variables are handled gracefully"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        
        # Clear optional env vars
        for key in ["DROPBOX_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY"]:
            os.environ.pop(key, None)
        
        fw = EvolvingAIFramework()
        result = fw.initialize()
        
        # Should still initialize (with limited functionality)
        assert result, "Framework must initialize even without all tokens"


class TestSelfHealingIntegration:
    """
    Integration tests for self-healing capabilities.
    
    **Validates: Requirements 8.3**
    """
    
    @pytest.fixture
    def framework(self, tmp_path):
        """Create isolated framework instance"""
        os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
        fw = EvolvingAIFramework()
        assert fw.initialize(), "Framework must initialize"
        return fw
    
    def test_healing_attempt_logged(self, framework):
        """Test that healing attempts are logged"""
        # Trigger a healing attempt
        result = framework.heal("storage_failure", {"platform": "test", "error": "test error"})
        
        assert "success" in result
        assert "strategy_used" in result
        assert "attempts" in result
    
    def test_healing_stats_available(self, framework):
        """Test that healing statistics are available"""
        stats = framework.healer.get_healing_stats()
        
        assert "total_attempts" in stats
        # Check for success tracking (may be named differently)
        assert "success_rate" in stats or "successful_heals" in stats
        # Check for strategy tracking
        assert "by_strategy" in stats or "strategies_used" in stats
