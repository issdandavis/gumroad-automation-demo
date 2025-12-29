"""
AWS Bedrock Client Wrapper
==========================

Wrapper for AWS Bedrock runtime client with error handling, retry logic,
cost tracking, and intelligent model routing.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from .aws_config import AWSConfigManager, BedrockConfig
from .models import OperationResult

logger = logging.getLogger(__name__)


@dataclass
class BedrockRequest:
    """Bedrock API request parameters"""
    model_id: str
    prompt: str
    max_tokens: int = 4000
    temperature: float = 0.3
    top_p: float = 0.9
    stop_sequences: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BedrockResponse:
    """Bedrock API response"""
    success: bool
    content: str = ""
    model_id: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "model_id": self.model_id,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class CostTracker:
    """Tracks Bedrock API costs and usage"""
    daily_spend: float = 0.0
    monthly_spend: float = 0.0
    total_tokens: int = 0
    total_requests: int = 0
    last_reset_date: str = field(default_factory=lambda: datetime.now().date().isoformat())
    
    # Model pricing (per 1K tokens) - as of Dec 2024
    MODEL_PRICING = {
        "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 0.003, "output": 0.015},
        "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
        "amazon.titan-text-premier-v1:0": {"input": 0.0005, "output": 0.0015},
        "ai21.jamba-1-5-large-v1:0": {"input": 0.002, "output": 0.008}
    }
    
    def calculate_cost(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        if model_id not in self.MODEL_PRICING:
            logger.warning(f"Unknown model pricing for {model_id}, using default")
            return (input_tokens + output_tokens) * 0.001  # Default $0.001 per token
        
        pricing = self.MODEL_PRICING[model_id]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
    
    def add_usage(self, model_id: str, input_tokens: int, output_tokens: int) -> float:
        """Add usage and return cost"""
        cost = self.calculate_cost(model_id, input_tokens, output_tokens)
        
        # Check if we need to reset daily counters
        today = datetime.now().date().isoformat()
        if today != self.last_reset_date:
            self.daily_spend = 0.0
            self.last_reset_date = today
        
        self.daily_spend += cost
        self.monthly_spend += cost
        self.total_tokens += input_tokens + output_tokens
        self.total_requests += 1
        
        return cost
    
    def check_budget(self, daily_budget: float, monthly_budget: float) -> Dict[str, Any]:
        """Check if usage is within budget"""
        return {
            "within_daily_budget": self.daily_spend <= daily_budget,
            "within_monthly_budget": self.monthly_spend <= monthly_budget,
            "daily_usage_percent": (self.daily_spend / daily_budget) * 100,
            "monthly_usage_percent": (self.monthly_spend / monthly_budget) * 100,
            "daily_remaining": max(0, daily_budget - self.daily_spend),
            "monthly_remaining": max(0, monthly_budget - self.monthly_spend)
        }


class BedrockClient:
    """
    AWS Bedrock client wrapper with intelligent features:
    - Automatic retry with exponential backoff
    - Cost tracking and budget enforcement
    - Model fallback on failures
    - Request/response logging
    - Performance monitoring
    """
    
    def __init__(self, aws_config: AWSConfigManager):
        self.aws_config = aws_config
        self.config = aws_config.config.bedrock
        self._client = None
        self.cost_tracker = CostTracker()
        self._request_history: List[Dict[str, Any]] = []
        
    def _get_client(self):
        """Get or create Bedrock client"""
        if self._client is None:
            self._client = self.aws_config.get_bedrock_client()
        return self._client
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)
    
    def _parse_response(self, response_body: Dict[str, Any], model_id: str) -> Dict[str, Any]:
        """Parse response body based on model type"""
        if model_id.startswith("anthropic.claude"):
            # Claude response format
            content = response_body.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "")
            else:
                text = response_body.get("completion", "")
            
            return {
                "content": text,
                "input_tokens": response_body.get("usage", {}).get("input_tokens", 0),
                "output_tokens": response_body.get("usage", {}).get("output_tokens", 0)
            }
        
        elif model_id.startswith("amazon.titan"):
            # Titan response format
            results = response_body.get("results", [])
            if results:
                text = results[0].get("outputText", "")
            else:
                text = response_body.get("outputText", "")
            
            return {
                "content": text,
                "input_tokens": response_body.get("inputTextTokenCount", 0),
                "output_tokens": response_body.get("outputTextTokenCount", 0)
            }
        
        else:
            # Generic fallback
            return {
                "content": str(response_body),
                "input_tokens": self._estimate_tokens(str(response_body)),
                "output_tokens": 0
            }
    
    def _build_request_body(self, request: BedrockRequest) -> str:
        """Build request body based on model type"""
        if request.model_id.startswith("anthropic.claude"):
            # Claude request format
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ]
            }
            
            if request.stop_sequences:
                body["stop_sequences"] = request.stop_sequences
        
        elif request.model_id.startswith("amazon.titan"):
            # Titan request format
            body = {
                "inputText": request.prompt,
                "textGenerationConfig": {
                    "maxTokenCount": request.max_tokens,
                    "temperature": request.temperature,
                    "topP": request.top_p
                }
            }
            
            if request.stop_sequences:
                body["textGenerationConfig"]["stopSequences"] = request.stop_sequences
        
        else:
            # Generic format
            body = {
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
        
        return json.dumps(body)
    
    async def invoke_model(self, request: BedrockRequest) -> BedrockResponse:
        """
        Invoke Bedrock model with retry logic and cost tracking
        """
        start_time = time.time()
        
        # Check budget before making request
        budget_check = self.cost_tracker.check_budget(
            self.config.daily_budget_usd,
            self.config.monthly_budget_usd
        )
        
        if not budget_check["within_daily_budget"]:
            return BedrockResponse(
                success=False,
                error=f"Daily budget exceeded: ${self.cost_tracker.daily_spend:.2f} / ${self.config.daily_budget_usd:.2f}"
            )
        
        if not budget_check["within_monthly_budget"]:
            return BedrockResponse(
                success=False,
                error=f"Monthly budget exceeded: ${self.cost_tracker.monthly_spend:.2f} / ${self.config.monthly_budget_usd:.2f}"
            )
        
        # Try primary model first, then fallbacks
        models_to_try = [request.model_id] + self.config.fallback_models
        last_error = None
        
        for attempt, model_id in enumerate(models_to_try):
            try:
                # Update request with current model
                current_request = BedrockRequest(
                    model_id=model_id,
                    prompt=request.prompt,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    stop_sequences=request.stop_sequences,
                    metadata=request.metadata
                )
                
                # Build request body
                body = self._build_request_body(current_request)
                
                # Make API call with retry logic
                response = await self._invoke_with_retry(model_id, body)
                
                if response.success:
                    # Calculate latency
                    response.latency_ms = (time.time() - start_time) * 1000
                    
                    # Track cost
                    response.cost_usd = self.cost_tracker.add_usage(
                        model_id, response.input_tokens, response.output_tokens
                    )
                    
                    # Log successful request
                    self._log_request(current_request, response)
                    
                    return response
                else:
                    last_error = response.error
                    logger.warning(f"Model {model_id} failed: {response.error}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Exception with model {model_id}: {e}")
        
        # All models failed
        return BedrockResponse(
            success=False,
            error=f"All models failed. Last error: {last_error}",
            latency_ms=(time.time() - start_time) * 1000
        )
    
    async def _invoke_with_retry(self, model_id: str, body: str) -> BedrockResponse:
        """Invoke model with exponential backoff retry"""
        client = self._get_client()
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = client.invoke_model(
                    modelId=model_id,
                    body=body,
                    contentType="application/json",
                    accept="application/json"
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                parsed = self._parse_response(response_body, model_id)
                
                return BedrockResponse(
                    success=True,
                    content=parsed["content"],
                    model_id=model_id,
                    input_tokens=parsed["input_tokens"],
                    output_tokens=parsed["output_tokens"]
                )
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                
                if error_code == 'ThrottlingException':
                    if attempt < self.config.max_retries:
                        wait_time = (self.config.retry_backoff_base ** attempt)
                        logger.warning(f"Throttled, waiting {wait_time}s before retry {attempt + 1}")
                        time.sleep(wait_time)
                        continue
                
                return BedrockResponse(
                    success=False,
                    error=f"AWS Error: {error_code} - {e.response['Error']['Message']}"
                )
            
            except Exception as e:
                if attempt < self.config.max_retries:
                    wait_time = (self.config.retry_backoff_base ** attempt)
                    logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                
                return BedrockResponse(
                    success=False,
                    error=f"Request failed after {self.config.max_retries} retries: {str(e)}"
                )
        
        return BedrockResponse(
            success=False,
            error="Max retries exceeded"
        )
    
    def _log_request(self, request: BedrockRequest, response: BedrockResponse) -> None:
        """Log request/response for monitoring"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_id": response.model_id,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.cost_usd,
            "latency_ms": response.latency_ms,
            "success": response.success,
            "prompt_length": len(request.prompt),
            "response_length": len(response.content)
        }
        
        self._request_history.append(log_entry)
        
        # Keep only last 1000 requests in memory
        if len(self._request_history) > 1000:
            self._request_history = self._request_history[-1000:]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        budget_check = self.cost_tracker.check_budget(
            self.config.daily_budget_usd,
            self.config.monthly_budget_usd
        )
        
        recent_requests = self._request_history[-100:] if self._request_history else []
        
        return {
            "cost_tracking": {
                "daily_spend": self.cost_tracker.daily_spend,
                "monthly_spend": self.cost_tracker.monthly_spend,
                "total_tokens": self.cost_tracker.total_tokens,
                "total_requests": self.cost_tracker.total_requests,
                "budget_status": budget_check
            },
            "performance": {
                "recent_requests": len(recent_requests),
                "avg_latency_ms": sum(r.get("latency_ms", 0) for r in recent_requests) / max(1, len(recent_requests)),
                "success_rate": sum(1 for r in recent_requests if r.get("success")) / max(1, len(recent_requests)),
                "avg_cost_per_request": sum(r.get("cost_usd", 0) for r in recent_requests) / max(1, len(recent_requests))
            }
        }
    
    def reset_daily_usage(self) -> None:
        """Reset daily usage counters"""
        self.cost_tracker.daily_spend = 0.0
        self.cost_tracker.last_reset_date = datetime.now().date().isoformat()
        logger.info("Daily usage counters reset")
    
    def test_connection(self) -> OperationResult:
        """Test Bedrock connection with a simple request"""
        try:
            test_request = BedrockRequest(
                model_id=self.config.default_model,
                prompt="Hello, this is a test. Please respond with 'Test successful.'",
                max_tokens=50,
                temperature=0.1
            )
            
            # Use sync version for testing
            import asyncio
            response = asyncio.run(self.invoke_model(test_request))
            
            if response.success:
                return OperationResult(
                    success=True,
                    operation_type="bedrock_test",
                    data={
                        "model_id": response.model_id,
                        "response_content": response.content,
                        "cost_usd": response.cost_usd,
                        "latency_ms": response.latency_ms
                    }
                )
            else:
                return OperationResult(
                    success=False,
                    operation_type="bedrock_test",
                    error=response.error
                )
        
        except Exception as e:
            return OperationResult(
                success=False,
                operation_type="bedrock_test",
                error=f"Connection test failed: {str(e)}"
            )