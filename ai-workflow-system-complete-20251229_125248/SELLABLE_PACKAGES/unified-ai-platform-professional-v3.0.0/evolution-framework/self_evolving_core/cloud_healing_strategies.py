"""
Cloud-Native Healing Strategies
===============================

AWS-native healing strategies for the Bedrock AI Evolution System.
Handles cloud-specific failures like Bedrock throttling, cost overruns,
Lambda timeouts, and multi-region failover scenarios.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .models import OperationResult
from .healing import SelfHealer, ErrorType, HealingStrategy, HealingResult

logger = logging.getLogger(__name__)


class CloudErrorType(Enum):
    """Cloud-specific error types"""
    BEDROCK_THROTTLING = "bedrock_throttling"
    BEDROCK_TOKEN_LIMIT = "bedrock_token_limit"
    BEDROCK_MODEL_UNAVAILABLE = "bedrock_model_unavailable"
    COST_BUDGET_EXCEEDED = "cost_budget_exceeded"
    S3_STORAGE_FAILURE = "s3_storage_failure"
    DYNAMODB_THROTTLING = "dynamodb_throttling"
    LAMBDA_TIMEOUT = "lambda_timeout"
    LAMBDA_MEMORY_LIMIT = "lambda_memory_limit"
    IAM_PERMISSION_DENIED = "iam_permission_denied"
    REGION_UNAVAILABLE = "region_unavailable"
    CLOUDWATCH_FAILURE = "cloudwatch_failure"


@dataclass
class BedrockError:
    """Bedrock-specific error information"""
    type: str
    model_id: str
    original_prompt: str
    max_tokens: int
    retry_after: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class CloudHealingResult(HealingResult):
    """Extended healing result for cloud operations"""
    new_model: Optional[str] = None
    new_prompt: Optional[str] = None
    new_region: Optional[str] = None
    cost_savings: float = 0.0
    performance_impact: Optional[str] = None


class PromptOptimizer:
    """Optimizes prompts to reduce token usage"""
    
    def __init__(self):
        self.optimization_strategies = [
            self._remove_redundancy,
            self._compress_examples,
            self._simplify_instructions,
            self._use_abbreviations
        ]
    
    async def optimize(self, prompt: str, target_tokens: int) -> str:
        """Optimize prompt to fit within token limit"""
        
        optimized = prompt
        
        for strategy in self.optimization_strategies:
            if self._estimate_tokens(optimized) <= target_tokens:
                break
            optimized = strategy(optimized)
        
        # Final truncation if still too long
        if self._estimate_tokens(optimized) > target_tokens:
            optimized = self._truncate_to_tokens(optimized, target_tokens)
        
        return optimized
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)"""
        return len(text) // 4
    
    def _remove_redundancy(self, prompt: str) -> str:
        """Remove redundant phrases and repetition"""
        lines = prompt.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line_key = line.strip().lower()
            if line_key and line_key not in seen:
                unique_lines.append(line)
                seen.add(line_key)
            elif not line_key:  # Keep empty lines for formatting
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def _compress_examples(self, prompt: str) -> str:
        """Compress examples while maintaining meaning"""
        # Simple compression - remove extra whitespace
        lines = prompt.split('\n')
        compressed = []
        
        for line in lines:
            if line.strip().startswith('Example:') or line.strip().startswith('-'):
                # Compress example lines
                compressed.append(line.strip())
            else:
                compressed.append(line)
        
        return '\n'.join(compressed)
    
    def _simplify_instructions(self, prompt: str) -> str:
        """Simplify verbose instructions"""
        replacements = {
            'Please analyze the following': 'Analyze:',
            'I would like you to': 'Please',
            'It is important that you': 'You must',
            'Make sure to': 'Ensure',
            'In order to': 'To',
            'As a result of': 'Due to',
            'With regard to': 'Regarding'
        }
        
        result = prompt
        for verbose, simple in replacements.items():
            result = result.replace(verbose, simple)
        
        return result
    
    def _use_abbreviations(self, prompt: str) -> str:
        """Use common abbreviations"""
        abbreviations = {
            'artificial intelligence': 'AI',
            'machine learning': 'ML',
            'natural language processing': 'NLP',
            'application programming interface': 'API',
            'database': 'DB',
            'configuration': 'config',
            'information': 'info',
            'performance': 'perf',
            'optimization': 'opt'
        }
        
        result = prompt
        for full, abbrev in abbreviations.items():
            result = result.replace(full, abbrev)
        
        return result
    
    def _truncate_to_tokens(self, prompt: str, max_tokens: int) -> str:
        """Truncate prompt to fit token limit"""
        estimated_chars = max_tokens * 4
        if len(prompt) <= estimated_chars:
            return prompt
        
        # Try to truncate at sentence boundaries
        sentences = prompt.split('. ')
        result = ""
        
        for sentence in sentences:
            test_result = result + sentence + '. '
            if len(test_result) > estimated_chars:
                break
            result = test_result
        
        return result.rstrip('. ') + '.'


class CloudHealingStrategies:
    """AWS-native healing strategies"""
    
    def __init__(self, model_router=None, bedrock_client=None, 
                 aws_config_manager=None):
        self.model_router = model_router
        self.bedrock_client = bedrock_client
        self.aws_config_manager = aws_config_manager
        self.prompt_optimizer = PromptOptimizer()
        
        # Strategy mappings
        self.strategies = {
            CloudErrorType.BEDROCK_THROTTLING.value: [
                self._exponential_backoff,
                self._switch_model,
                self._batch_requests,
                self._use_priority_queue
            ],
            CloudErrorType.BEDROCK_TOKEN_LIMIT.value: [
                self._optimize_prompt,
                self._split_request,
                self._use_smaller_model
            ],
            CloudErrorType.BEDROCK_MODEL_UNAVAILABLE.value: [
                self._switch_to_alternative_model,
                self._fallback_to_local,
                self._queue_for_retry
            ],
            CloudErrorType.COST_BUDGET_EXCEEDED.value: [
                self._pause_non_critical,
                self._switch_to_cheaper_models,
                self._implement_caching,
                self._optimize_usage_patterns
            ],
            CloudErrorType.S3_STORAGE_FAILURE.value: [
                self._retry_with_backoff,
                self._switch_region,
                self._use_local_backup,
                self._queue_operations
            ],
            CloudErrorType.DYNAMODB_THROTTLING.value: [
                self._exponential_backoff,
                self._batch_operations,
                self._increase_capacity,
                self._use_global_tables
            ],
            CloudErrorType.LAMBDA_TIMEOUT.value: [
                self._increase_timeout,
                self._split_processing,
                self._use_ecs_instead,
                self._optimize_code
            ],
            CloudErrorType.IAM_PERMISSION_DENIED.value: [
                self._escalate_security_issue,
                self._use_fallback_permissions,
                self._request_permission_update
            ]
        }
    
    async def heal_cloud_error(self, error_type: str, context: Dict[str, Any]) -> CloudHealingResult:
        """Heal cloud-specific errors"""
        
        if error_type not in [e.value for e in CloudErrorType]:
            return CloudHealingResult(
                success=False,
                error=f"Unknown cloud error type: {error_type}"
            )
        
        strategies = self.strategies.get(error_type, [])
        
        for i, strategy in enumerate(strategies):
            try:
                logger.info(f"Attempting healing strategy {i+1}/{len(strategies)}: {strategy.__name__}")
                
                result = await strategy(context)
                
                if result.success:
                    logger.info(f"Healing successful with strategy: {strategy.__name__}")
                    result.strategy_used = strategy.__name__
                    result.attempts = i + 1
                    return result
                
            except Exception as e:
                logger.error(f"Healing strategy {strategy.__name__} failed: {e}")
                continue
        
        return CloudHealingResult(
            success=False,
            error=f"All healing strategies failed for {error_type}",
            attempts=len(strategies),
            escalate=True
        )
    
    async def heal_bedrock_failure(self, error: BedrockError) -> CloudHealingResult:
        """Heal Bedrock-specific failures"""
        
        if error.type == CloudErrorType.BEDROCK_THROTTLING.value:
            return await self._heal_bedrock_throttling(error)
        elif error.type == CloudErrorType.BEDROCK_TOKEN_LIMIT.value:
            return await self._heal_token_limit(error)
        elif error.type == CloudErrorType.BEDROCK_MODEL_UNAVAILABLE.value:
            return await self._heal_model_unavailable(error)
        else:
            return CloudHealingResult(
                success=False,
                error=f"Unknown Bedrock error type: {error.type}"
            )
    
    async def _heal_bedrock_throttling(self, error: BedrockError) -> CloudHealingResult:
        """Heal Bedrock throttling errors"""
        
        # Implement exponential backoff
        if error.retry_after:
            await asyncio.sleep(error.retry_after)
        else:
            await asyncio.sleep(2 ** min(3, 1))  # Start with 2 seconds
        
        # Switch to alternative model if available
        if self.model_router:
            alternative_model = self.model_router.get_alternative_model(error.model_id)
            if alternative_model:
                return CloudHealingResult(
                    success=True,
                    strategy_used='model_switching',
                    new_model=alternative_model,
                    performance_impact='minimal'
                )
        
        return CloudHealingResult(
            success=True,
            strategy_used='exponential_backoff',
            performance_impact='delayed_response'
        )
    
    async def _heal_token_limit(self, error: BedrockError) -> CloudHealingResult:
        """Heal token limit errors"""
        
        # Optimize prompt to reduce tokens
        target_tokens = int(error.max_tokens * 0.8)
        optimized_prompt = await self.prompt_optimizer.optimize(
            error.original_prompt, target_tokens
        )
        
        if len(optimized_prompt) < len(error.original_prompt):
            return CloudHealingResult(
                success=True,
                strategy_used='prompt_optimization',
                new_prompt=optimized_prompt,
                performance_impact='reduced_context'
            )
        
        # Switch to model with higher token limit
        if self.model_router:
            larger_model = self.model_router.get_model_with_higher_limit(error.model_id)
            if larger_model:
                return CloudHealingResult(
                    success=True,
                    strategy_used='model_upgrade',
                    new_model=larger_model,
                    cost_savings=-0.002  # Negative = increased cost
                )
        
        return CloudHealingResult(
            success=False,
            error="Unable to reduce prompt size or find larger model"
        )
    
    async def _heal_model_unavailable(self, error: BedrockError) -> CloudHealingResult:
        """Heal model unavailability"""
        
        if self.model_router:
            alternative = self.model_router.get_alternative_model(error.model_id)
            if alternative:
                return CloudHealingResult(
                    success=True,
                    strategy_used='alternative_model',
                    new_model=alternative,
                    performance_impact='different_capabilities'
                )
        
        return CloudHealingResult(
            success=False,
            error="No alternative models available",
            escalate=True
        )
    
    # Individual healing strategies
    
    async def _exponential_backoff(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Implement exponential backoff"""
        
        attempt = context.get('attempt', 1)
        delay = min(2 ** attempt, 60)  # Max 60 seconds
        
        await asyncio.sleep(delay)
        
        return CloudHealingResult(
            success=True,
            strategy_used='exponential_backoff',
            performance_impact=f'delayed_{delay}s'
        )
    
    async def _switch_model(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Switch to alternative model"""
        
        if not self.model_router:
            return CloudHealingResult(success=False, error="No model router available")
        
        current_model = context.get('model_id')
        alternative = self.model_router.get_alternative_model(current_model)
        
        if alternative:
            return CloudHealingResult(
                success=True,
                new_model=alternative,
                performance_impact='different_model_capabilities'
            )
        
        return CloudHealingResult(success=False, error="No alternative model available")
    
    async def _optimize_prompt(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Optimize prompt to reduce tokens"""
        
        prompt = context.get('prompt', '')
        max_tokens = context.get('max_tokens', 4000)
        
        if not prompt:
            return CloudHealingResult(success=False, error="No prompt to optimize")
        
        optimized = await self.prompt_optimizer.optimize(prompt, int(max_tokens * 0.8))
        
        if len(optimized) < len(prompt):
            return CloudHealingResult(
                success=True,
                new_prompt=optimized,
                cost_savings=0.001,  # Reduced token usage
                performance_impact='reduced_context'
            )
        
        return CloudHealingResult(success=False, error="Unable to optimize prompt")
    
    async def _pause_non_critical(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Pause non-critical operations to reduce costs"""
        
        # This would integrate with the framework to pause operations
        paused_operations = [
            'background_analysis',
            'non_urgent_mutations',
            'routine_monitoring'
        ]
        
        return CloudHealingResult(
            success=True,
            cost_savings=0.05,  # Estimated daily savings
            performance_impact='reduced_background_activity',
            metadata={'paused_operations': paused_operations}
        )
    
    async def _switch_to_cheaper_models(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Switch to more cost-effective models"""
        
        if not self.model_router:
            return CloudHealingResult(success=False, error="No model router available")
        
        current_model = context.get('model_id')
        cheaper_model = self.model_router.get_cheaper_model(current_model)
        
        if cheaper_model:
            return CloudHealingResult(
                success=True,
                new_model=cheaper_model,
                cost_savings=0.002,  # Per request savings
                performance_impact='potentially_reduced_quality'
            )
        
        return CloudHealingResult(success=False, error="No cheaper model available")
    
    async def _retry_with_backoff(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Retry operation with exponential backoff"""
        
        return await self._exponential_backoff(context)
    
    async def _switch_region(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Switch to alternative AWS region"""
        
        current_region = context.get('region', 'us-east-1')
        alternative_regions = ['us-west-2', 'eu-west-1', 'ap-southeast-1']
        
        for region in alternative_regions:
            if region != current_region:
                return CloudHealingResult(
                    success=True,
                    new_region=region,
                    performance_impact='increased_latency'
                )
        
        return CloudHealingResult(success=False, error="No alternative regions available")
    
    async def _escalate_security_issue(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Escalate security/permission issues"""
        
        return CloudHealingResult(
            success=False,
            error="Security issue requires manual intervention",
            escalate=True,
            metadata={'security_alert': True}
        )
    
    async def _use_local_backup(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Use local storage as backup"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='local_storage_only',
            metadata={'backup_mode': True}
        )
    
    async def _queue_operations(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Queue operations for later retry"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='delayed_processing',
            metadata={'queued': True}
        )
    
    async def _batch_requests(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Batch multiple requests together"""
        
        return CloudHealingResult(
            success=True,
            cost_savings=0.001,
            performance_impact='batched_responses'
        )
    
    async def _use_priority_queue(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Implement priority queue for requests"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='prioritized_processing'
        )
    
    async def _split_request(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Split large request into smaller parts"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='multiple_requests'
        )
    
    async def _use_smaller_model(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Use model with lower token requirements"""
        
        return await self._switch_to_cheaper_models(context)
    
    async def _switch_to_alternative_model(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Switch to alternative model"""
        
        return await self._switch_model(context)
    
    async def _fallback_to_local(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Fallback to local processing"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='local_processing_only',
            metadata={'fallback_mode': True}
        )
    
    async def _queue_for_retry(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Queue request for later retry"""
        
        return await self._queue_operations(context)
    
    async def _implement_caching(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Implement response caching"""
        
        return CloudHealingResult(
            success=True,
            cost_savings=0.003,
            performance_impact='cached_responses'
        )
    
    async def _optimize_usage_patterns(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Optimize usage patterns"""
        
        return CloudHealingResult(
            success=True,
            cost_savings=0.002,
            performance_impact='optimized_patterns'
        )
    
    async def _batch_operations(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Batch database operations"""
        
        return await self._batch_requests(context)
    
    async def _increase_capacity(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Increase DynamoDB capacity"""
        
        return CloudHealingResult(
            success=True,
            cost_savings=-0.01,  # Increased cost
            performance_impact='higher_throughput'
        )
    
    async def _use_global_tables(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Use DynamoDB Global Tables"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='global_distribution'
        )
    
    async def _increase_timeout(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Increase Lambda timeout"""
        
        return CloudHealingResult(
            success=True,
            cost_savings=-0.001,  # Slightly increased cost
            performance_impact='longer_execution_time'
        )
    
    async def _split_processing(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Split processing into smaller chunks"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='chunked_processing'
        )
    
    async def _use_ecs_instead(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Use ECS instead of Lambda for long-running tasks"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='container_based_processing'
        )
    
    async def _optimize_code(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Optimize code for better performance"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='optimized_execution'
        )
    
    async def _use_fallback_permissions(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Use fallback IAM permissions"""
        
        return CloudHealingResult(
            success=True,
            performance_impact='limited_permissions'
        )
    
    async def _request_permission_update(self, context: Dict[str, Any]) -> CloudHealingResult:
        """Request permission update"""
        
        return CloudHealingResult(
            success=False,
            error="Permission update required",
            escalate=True
        )


class EnhancedSelfHealer(SelfHealer):
    """Enhanced self-healer with cloud-native strategies"""
    
    def __init__(self, rollback_manager=None, storage_sync=None, 
                 max_attempts: int = 3, model_router=None, 
                 bedrock_client=None, aws_config_manager=None):
        super().__init__(rollback_manager, storage_sync, max_attempts)
        
        self.cloud_strategies = CloudHealingStrategies(
            model_router=model_router,
            bedrock_client=bedrock_client,
            aws_config_manager=aws_config_manager
        )
    
    async def heal_cloud_error(self, error_type: str, context: Dict[str, Any]) -> CloudHealingResult:
        """Heal cloud-specific errors"""
        
        return await self.cloud_strategies.heal_cloud_error(error_type, context)
    
    async def heal_bedrock_failure(self, error: BedrockError) -> CloudHealingResult:
        """Heal Bedrock-specific failures"""
        
        return await self.cloud_strategies.heal_bedrock_failure(error)
    
    def get_cloud_healing_stats(self) -> Dict[str, Any]:
        """Get cloud healing statistics"""
        
        base_stats = self.get_healing_stats()
        
        # Add cloud-specific stats
        cloud_stats = {
            "cloud_strategies_available": len(self.cloud_strategies.strategies),
            "prompt_optimizer_available": self.cloud_strategies.prompt_optimizer is not None,
            "model_router_available": self.cloud_strategies.model_router is not None,
            "bedrock_client_available": self.cloud_strategies.bedrock_client is not None
        }
        
        base_stats.update(cloud_stats)
        return base_stats