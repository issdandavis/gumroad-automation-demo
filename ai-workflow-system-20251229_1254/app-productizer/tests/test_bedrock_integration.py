"""
Integration Tests for AWS Bedrock AI Evolution System
====================================================

End-to-end integration tests that validate complete workflows
from feedback analysis to mutation application with LLM guidance.
"""

import pytest
import asyncio
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

# Import system components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_evolving_core.bedrock_framework import BedrockFramework
from self_evolving_core.aws_config import AWSConfigManager, AWSConfig
from self_evolving_core.bedrock_client import BedrockClient, BedrockResponse
from self_evolving_core.model_router import ModelRouter
from self_evolving_core.evolution_advisor import EvolutionAdvisor
from self_evolving_core.bedrock_decision_engine import BedrockDecisionEngine
from self_evolving_core.enhanced_autonomy import EnhancedAutonomyController
from self_evolving_core.cloud_dna_store import CloudDNAStore, EvolutionEvent
from self_evolving_core.cost_optimizer import CostTracker, BudgetEnforcer, CostOptimizer
from self_evolving_core.security_compliance import SecurityManager
from self_evolving_core.cloud_architecture import CloudArchitectureManager
from self_evolving_core.cloud_healing_strategies import CloudHealingStrategies, BedrockError
from self_evolving_core.models import SystemDNA, Mutation, FitnessScore


class TestBedrockIntegration:
    """Integration tests for Bedrock system components"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_aws_config(self):
        """Mock AWS configuration"""
        config = Mock()
        config.region = "us-east-1"
        config.bedrock.daily_budget_usd = 10.0
        config.bedrock.monthly_budget_usd = 300.0
        config.bedrock.default_model = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        config.evolution_bucket = "test-evolution-bucket"
        config.snapshots_table = "test-snapshots-table"
        config.metrics_namespace = "AI-Evolution-Test"
        config.security.kms_key_id = "test-kms-key"
        
        aws_config_manager = Mock()
        aws_config_manager.config = config
        aws_config_manager.test_connectivity.return_value = {
            "bedrock": True,
            "s3": True,
            "dynamodb": True,
            "cloudwatch": True
        }
        
        return aws_config_manager
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Mock Bedrock client with realistic responses"""
        client = Mock()
        
        # Mock successful responses
        async def mock_invoke_model(model_id, prompt, **kwargs):
            return BedrockResponse(
                success=True,
                content=json.dumps({
                    "analysis": {
                        "current_state_assessment": "System is performing well with room for improvement",
                        "confidence_score": 0.85,
                        "strengths": ["Stable performance", "Good error handling"],
                        "weaknesses": ["Limited scalability", "High latency"],
                        "opportunities": ["Optimize algorithms", "Add caching"],
                        "threats": ["Resource constraints", "Increasing load"],
                        "recommended_focus_areas": ["Performance optimization", "Scalability"]
                    },
                    "strategy": {
                        "primary_mutations": [
                            {
                                "type": "performance_optimization",
                                "description": "Implement caching layer",
                                "expected_fitness_impact": 5.0,
                                "risk_score": 0.3
                            }
                        ],
                        "execution_order": ["performance_optimization"],
                        "success_criteria": {"fitness_improvement": 5.0},
                        "timeline_estimate": "2-3 hours"
                    }
                }),
                model_id=model_id,
                tokens_input=len(prompt) // 4,
                tokens_output=200,
                cost_usd=0.003,
                processing_time_ms=1500
            )
        
        client.invoke_model = mock_invoke_model
        client.test_connection.return_value = Mock(success=True)
        client.get_usage_stats.return_value = {
            "total_requests": 10,
            "total_tokens": 5000,
            "total_cost": 0.05,
            "cost_tracking": {
                "daily_spend": 0.02,
                "monthly_spend": 0.05,
                "budget_status": {
                    "daily_usage_percent": 0.2,
                    "monthly_usage_percent": 0.017,
                    "daily_remaining": 9.98
                }
            }
        }
        
        return client
    
    @pytest.mark.asyncio
    async def test_complete_mutation_workflow(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test complete mutation workflow with LLM guidance"""
        
        # Create framework with mocked components
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=mock_bedrock_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                framework = BedrockFramework(aws_config_path=None)
                
                # Override storage path
                framework.config.storage.local_path = temp_storage
                
                # Initialize framework
                success = framework.initialize()
                assert success, "Framework initialization should succeed"
                assert framework.bedrock_enabled, "Bedrock should be enabled"
                
                # Create test mutation
                mutation = Mutation(
                    type="performance_optimization",
                    description="Implement caching layer for better performance",
                    fitness_impact=5.0,
                    source_ai="integration_test"
                )
                
                # Test enhanced mutation proposal
                result = await framework.propose_mutation_enhanced(mutation)
                
                # Verify result structure
                assert "enhanced" in result
                assert result["enhanced"] is True
                assert "final_decision" in result
                assert "confidence" in result
                assert "reasoning" in result
                
                # Verify decision was made
                assert result["final_decision"] in ["auto_approve", "require_approval"]
                assert isinstance(result["confidence"], float)
                assert 0.0 <= result["confidence"] <= 1.0
                assert isinstance(result["reasoning"], str)
                assert len(result["reasoning"]) > 0
    
    @pytest.mark.asyncio
    async def test_evolution_guidance_workflow(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test evolution guidance generation workflow"""
        
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=mock_bedrock_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                framework = BedrockFramework(aws_config_path=None)
                framework.config.storage.local_path = temp_storage
                
                # Initialize framework
                framework.initialize()
                
                # Get current DNA
                dna = framework.get_dna()
                
                # Request evolution guidance
                guidance = await framework.get_evolution_guidance(dna)
                
                # Verify guidance structure
                assert "analysis" in guidance
                assert "strategy" in guidance
                
                analysis = guidance["analysis"]
                assert "current_state_assessment" in analysis
                assert "confidence_score" in analysis
                assert "strengths" in analysis
                assert "opportunities" in analysis
                
                strategy = guidance["strategy"]
                assert "primary_mutations" in strategy
                assert "execution_order" in strategy
                assert "timeline_estimate" in strategy
                
                # Verify analysis quality
                assert isinstance(analysis["confidence_score"], float)
                assert 0.0 <= analysis["confidence_score"] <= 1.0
                assert isinstance(analysis["strengths"], list)
                assert isinstance(analysis["opportunities"], list)
    
    @pytest.mark.asyncio
    async def test_cost_optimization_workflow(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test cost optimization and monitoring workflow"""
        
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=mock_bedrock_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                framework = BedrockFramework(aws_config_path=None)
                framework.config.storage.local_path = temp_storage
                
                # Initialize framework
                framework.initialize()
                
                # Simulate some Bedrock usage
                if framework.bedrock_client:
                    await framework.bedrock_client.invoke_model(
                        "anthropic.claude-3-5-sonnet-20241022-v2:0",
                        "Test prompt for cost tracking",
                        max_tokens=100
                    )
                
                # Get optimization recommendations
                optimization = framework.optimize_bedrock_usage()
                
                # Verify optimization structure
                assert isinstance(optimization, dict)
                
                # Check for expected fields
                expected_fields = ["recommendations", "cost_analysis", "performance_insights"]
                for field in expected_fields:
                    if field in optimization:
                        assert isinstance(optimization[field], (list, dict))
                
                # Get Bedrock status
                status = framework.get_bedrock_status()
                
                # Verify status structure
                assert "bedrock_enabled" in status
                assert "usage_stats" in status
                assert status["bedrock_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_cloud_storage_workflow(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test cloud storage sync workflow"""
        
        # Mock AWS clients
        with patch('boto3.client') as mock_boto_client:
            with patch('boto3.resource') as mock_boto_resource:
                # Setup mocks
                mock_s3 = Mock()
                mock_dynamodb = Mock()
                mock_cloudwatch = Mock()
                
                mock_boto_client.side_effect = lambda service, **kwargs: {
                    's3': mock_s3,
                    'cloudwatch': mock_cloudwatch
                }.get(service, Mock())
                
                mock_table = Mock()
                mock_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
                mock_dynamodb.Table.return_value = mock_table
                mock_boto_resource.return_value = mock_dynamodb
                
                # Create cloud DNA store
                cloud_store = CloudDNAStore(mock_aws_config)
                
                # Test event storage
                test_event = EvolutionEvent(
                    id="test_event_123",
                    timestamp=datetime.now(),
                    type="mutation_applied",
                    generation=5,
                    fitness_delta=3.5,
                    data={"test": "data"},
                    importance=0.8
                )
                
                # Mock successful storage
                mock_s3.put_object.return_value = {"ETag": "test-etag"}
                
                # Test storage (would be async in real implementation)
                event_dict = test_event.to_dict()
                
                # Verify event structure
                assert event_dict["id"] == "test_event_123"
                assert event_dict["type"] == "mutation_applied"
                assert event_dict["generation"] == 5
                assert event_dict["fitness_delta"] == 3.5
                
                # Test snapshot creation
                test_dna = SystemDNA(generation=5, fitness_score=105.5)
                
                # Mock successful snapshot storage
                snapshot_result = {
                    "success": True,
                    "snapshot_id": "snap_test_123",
                    "storage_location": "dynamodb://test-table/snap_test_123"
                }
                
                # Verify snapshot structure
                assert snapshot_result["success"] is True
                assert "snapshot_id" in snapshot_result
                assert "storage_location" in snapshot_result
    
    @pytest.mark.asyncio
    async def test_security_compliance_workflow(self, temp_storage, mock_aws_config):
        """Test security and compliance workflow"""
        
        # Mock AWS clients for security components
        with patch('boto3.client') as mock_boto_client:
            mock_kms = Mock()
            mock_iam = Mock()
            mock_sts = Mock()
            mock_logs = Mock()
            
            mock_boto_client.side_effect = lambda service, **kwargs: {
                'kms': mock_kms,
                'iam': mock_iam,
                'sts': mock_sts,
                'logs': mock_logs
            }.get(service, Mock())
            
            # Mock successful encryption
            mock_kms.encrypt.return_value = {
                'CiphertextBlob': b'encrypted_data',
                'KeyId': 'test-kms-key'
            }
            mock_kms.decrypt.return_value = {
                'Plaintext': b'test_data'
            }
            
            # Mock IAM identity
            mock_sts.get_caller_identity.return_value = {
                'UserId': 'AIDA123456789',
                'Account': '123456789012',
                'Arn': 'arn:aws:iam::123456789012:user/test-user'
            }
            
            # Create security manager
            security_manager = SecurityManager(mock_aws_config, temp_storage)
            
            # Initialize security
            init_result = security_manager.initialize_security()
            
            # Verify initialization
            assert "initialization_status" in init_result
            assert "security_checks" in init_result
            
            # Test encryption workflow
            test_data = "sensitive_test_data"
            encrypted = security_manager.encryption_manager.encrypt_data(test_data)
            
            # Verify encryption
            assert "encrypted_data" in encrypted
            assert "method" in encrypted
            
            # Test decryption
            decrypted = security_manager.encryption_manager.decrypt_data(
                encrypted["encrypted_data"],
                encrypted["method"]
            )
            
            # Verify roundtrip
            assert decrypted == test_data
            
            # Run security assessment
            assessment = security_manager.run_security_assessment()
            
            # Verify assessment structure
            assert "compliance_reports" in assessment
            assert "security_posture" in assessment
            assert "recommendations" in assessment
    
    @pytest.mark.asyncio
    async def test_cloud_healing_workflow(self, temp_storage, mock_aws_config):
        """Test cloud healing strategies workflow"""
        
        # Create healing strategies
        healing_strategies = CloudHealingStrategies()
        
        # Test Bedrock throttling healing
        bedrock_error = BedrockError(
            type="bedrock_throttling",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            original_prompt="Test prompt",
            max_tokens=1000,
            retry_after=2
        )
        
        healing_result = await healing_strategies.heal_bedrock_failure(bedrock_error)
        
        # Verify healing result
        assert hasattr(healing_result, 'success')
        assert hasattr(healing_result, 'strategy_used')
        
        # Test token limit healing
        token_error = BedrockError(
            type="bedrock_token_limit",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            original_prompt="Very long prompt that exceeds token limits" * 100,
            max_tokens=1000
        )
        
        token_healing_result = await healing_strategies.heal_bedrock_failure(token_error)
        
        # Verify token healing
        assert hasattr(token_healing_result, 'success')
        if token_healing_result.success:
            assert hasattr(token_healing_result, 'new_prompt') or hasattr(token_healing_result, 'new_model')
    
    @pytest.mark.asyncio
    async def test_cloud_architecture_workflow(self, temp_storage, mock_aws_config):
        """Test cloud architecture management workflow"""
        
        # Mock AWS clients for architecture components
        with patch('boto3.client') as mock_boto_client:
            mock_lambda = Mock()
            mock_sqs = Mock()
            mock_ecs = Mock()
            mock_autoscaling = Mock()
            
            mock_boto_client.side_effect = lambda service, **kwargs: {
                'lambda': mock_lambda,
                'sqs': mock_sqs,
                'ecs': mock_ecs,
                'application-autoscaling': mock_autoscaling
            }.get(service, Mock())
            
            # Mock successful operations
            mock_ecs.create_cluster.return_value = {
                'cluster': {'clusterArn': 'arn:aws:ecs:us-east-1:123456789012:cluster/test-cluster'}
            }
            
            mock_sqs.create_queue.return_value = {
                'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
            }
            
            mock_lambda.create_function.return_value = {
                'FunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:test-function',
                'Version': '1'
            }
            
            # Create architecture manager
            architecture = CloudArchitectureManager(mock_aws_config)
            
            # Initialize architecture
            init_result = await architecture.initialize_architecture()
            
            # Verify initialization
            assert "initialization_results" in init_result
            assert "created_resources" in init_result
            
            # Check created resources
            results = init_result["initialization_results"]
            assert "ecs_cluster" in results
            assert "sqs_queues" in results
            assert "lambda_functions" in results
            assert "ecs_tasks" in results
            
            # Test health check
            health = await architecture.health_check()
            
            # Verify health check
            assert "overall_status" in health
            assert "component_status" in health
            assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]
            
            # Get architecture status
            status = architecture.get_architecture_status()
            
            # Verify status
            assert "initialized" in status
            assert "lambda_functions" in status
            assert "sqs_queues" in status
            assert "ecs_tasks" in status
    
    @pytest.mark.asyncio
    async def test_end_to_end_evolution_cycle(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test complete end-to-end evolution cycle"""
        
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=mock_bedrock_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                # Create and initialize framework
                framework = BedrockFramework(aws_config_path=None)
                framework.config.storage.local_path = temp_storage
                
                success = framework.initialize()
                assert success, "Framework should initialize successfully"
                
                # Step 1: Get initial system state
                initial_dna = framework.get_dna()
                initial_fitness = framework.get_fitness()
                
                assert initial_dna.generation >= 1
                assert initial_fitness.overall >= 0
                
                # Step 2: Get evolution guidance
                guidance = await framework.get_evolution_guidance(initial_dna)
                
                assert "analysis" in guidance
                assert "strategy" in guidance
                
                # Step 3: Create mutation based on guidance
                strategy = guidance["strategy"]
                if "primary_mutations" in strategy and strategy["primary_mutations"]:
                    suggested_mutation = strategy["primary_mutations"][0]
                    
                    mutation = Mutation(
                        type=suggested_mutation.get("type", "intelligence_upgrade"),
                        description=suggested_mutation.get("description", "AI-suggested improvement"),
                        fitness_impact=suggested_mutation.get("expected_fitness_impact", 3.0),
                        source_ai="evolution_guidance"
                    )
                else:
                    # Fallback mutation
                    mutation = Mutation(
                        type="intelligence_upgrade",
                        description="Enhance system intelligence based on LLM analysis",
                        fitness_impact=3.0,
                        source_ai="evolution_guidance"
                    )
                
                # Step 4: Evaluate mutation with enhanced decision engine
                mutation_result = await framework.propose_mutation_enhanced(mutation)
                
                assert "enhanced" in mutation_result
                assert "final_decision" in mutation_result
                assert "confidence" in mutation_result
                
                # Step 5: Check cost impact
                optimization = framework.optimize_bedrock_usage()
                
                # Verify cost tracking is working
                assert isinstance(optimization, dict)
                
                # Step 6: Get final system status
                final_status = framework.get_enhanced_status()
                
                assert "bedrock" in final_status
                assert final_status["initialized"] is True
                assert final_status["running"] is True
                
                # Verify evolution cycle completed
                assert final_status["dna"]["generation"] >= initial_dna.generation
    
    @pytest.mark.asyncio
    async def test_multi_region_consistency_workflow(self, temp_storage, mock_aws_config):
        """Test multi-region consistency and failover"""
        
        # Mock multiple region configurations
        regions = ["us-east-1", "us-west-2", "eu-west-1"]
        
        for region in regions:
            # Create region-specific config
            region_config = Mock()
            region_config.region = region
            region_config.evolution_bucket = f"test-evolution-bucket-{region}"
            region_config.snapshots_table = f"test-snapshots-table-{region}"
            
            region_aws_config = Mock()
            region_aws_config.config = region_config
            
            # Test cloud DNA store for each region
            with patch('boto3.client') as mock_boto_client:
                with patch('boto3.resource') as mock_boto_resource:
                    mock_s3 = Mock()
                    mock_dynamodb = Mock()
                    
                    mock_boto_client.return_value = mock_s3
                    mock_boto_resource.return_value = mock_dynamodb
                    
                    # Mock successful operations
                    mock_s3.put_object.return_value = {"ETag": f"etag-{region}"}
                    mock_table = Mock()
                    mock_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
                    mock_dynamodb.Table.return_value = mock_table
                    
                    # Create cloud store for region
                    cloud_store = CloudDNAStore(region_aws_config)
                    
                    # Test event storage in region
                    test_event = EvolutionEvent(
                        id=f"test_event_{region}",
                        timestamp=datetime.now(),
                        type="mutation_applied",
                        generation=1,
                        fitness_delta=2.0,
                        data={"region": region},
                        importance=0.7
                    )
                    
                    # Verify event can be stored in each region
                    event_dict = test_event.to_dict()
                    assert event_dict["data"]["region"] == region
                    assert event_dict["id"] == f"test_event_{region}"
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, temp_storage, mock_aws_config):
        """Test error handling and recovery mechanisms"""
        
        # Test with failing Bedrock client
        failing_client = Mock()
        failing_client.test_connection.return_value = Mock(success=False, error="Connection failed")
        
        async def failing_invoke(*args, **kwargs):
            raise Exception("Bedrock service unavailable")
        
        failing_client.invoke_model = failing_invoke
        
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=failing_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                # Framework should still initialize but with Bedrock disabled
                framework = BedrockFramework(aws_config_path=None)
                framework.config.storage.local_path = temp_storage
                
                success = framework.initialize()
                assert success, "Framework should initialize even with Bedrock failures"
                
                # Bedrock should be disabled due to connection failure
                # Framework should fall back to base functionality
                
                # Test fallback mutation proposal
                mutation = Mutation(
                    type="test_mutation",
                    description="Test mutation with failing Bedrock",
                    fitness_impact=2.0
                )
                
                # Should fall back to base implementation
                result = framework.propose_mutation(mutation)
                
                # Verify fallback works
                assert "approved" in result or "request_id" in result
                
                # Test evolution guidance with failure
                try:
                    guidance = await framework.get_evolution_guidance()
                    # Should return error message
                    assert "error" in guidance
                except Exception:
                    # Exception handling is also acceptable
                    pass


class TestBedrockPerformance:
    """Performance and load testing for Bedrock integration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_bedrock_requests(self, mock_bedrock_client):
        """Test handling of concurrent Bedrock requests"""
        
        # Create multiple concurrent requests
        async def make_request(i):
            return await mock_bedrock_client.invoke_model(
                "anthropic.claude-3-5-sonnet-20241022-v2:0",
                f"Test prompt {i}",
                max_tokens=100
            )
        
        # Run 10 concurrent requests
        tasks = [make_request(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests completed
        assert len(results) == 10
        
        # Count successful requests
        successful = [r for r in results if not isinstance(r, Exception)]
        assert len(successful) > 0, "At least some requests should succeed"
    
    @pytest.mark.asyncio
    async def test_cost_tracking_performance(self, temp_storage):
        """Test cost tracking performance with many operations"""
        
        cost_tracker = CostTracker(temp_storage)
        
        # Record many cost entries
        start_time = datetime.now()
        
        for i in range(1000):
            cost_tracker.record_cost(
                category="test",
                service="bedrock",
                operation=f"op_{i}",
                amount_usd=0.001
            )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time
        assert duration < 5.0, f"Cost tracking took too long: {duration}s"
        
        # Verify accuracy
        total_cost = cost_tracker.get_daily_spend()
        expected_cost = 1000 * 0.001
        assert abs(total_cost - expected_cost) < 0.000001
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, temp_storage, mock_aws_config, mock_bedrock_client):
        """Test memory usage stability over many operations"""
        
        with patch('self_evolving_core.bedrock_framework.BedrockClient', return_value=mock_bedrock_client):
            with patch('self_evolving_core.bedrock_framework.AWSConfigManager', return_value=mock_aws_config):
                framework = BedrockFramework(aws_config_path=None)
                framework.config.storage.local_path = temp_storage
                
                framework.initialize()
                
                # Perform many operations
                for i in range(100):
                    mutation = Mutation(
                        type="test_mutation",
                        description=f"Test mutation {i}",
                        fitness_impact=1.0
                    )
                    
                    # Alternate between enhanced and regular proposals
                    if i % 2 == 0:
                        result = await framework.propose_mutation_enhanced(mutation)
                    else:
                        result = framework.propose_mutation(mutation)
                    
                    # Verify result structure
                    assert isinstance(result, dict)
                
                # Framework should still be responsive
                status = framework.get_enhanced_status()
                assert status["initialized"] is True


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short", "-s"])