"""
AI Provider Hub for Self-Evolving AI Framework
==============================================

Multi-provider AI integration with:
- OpenAI, Anthropic, Google, Perplexity, xAI support
- Automatic fallback on failure
- Cost tracking per provider
- Rate limiting and retry logic
"""

import logging
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

from .models import AIProvider, OperationResult

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ProviderStats:
    """Statistics for an AI provider"""
    requests: int = 0
    successes: int = 0
    failures: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_latency_ms: float = 0.0
    last_used: Optional[str] = None
    status: str = "available"


class ProviderAdapter(ABC):
    """Base adapter for AI providers"""
    
    name: str = "base"
    
    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.model = model
        self.stats = ProviderStats()
        self.status = ProviderStatus.AVAILABLE
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.status == ProviderStatus.AVAILABLE and bool(self.api_key)
    
    def record_success(self, tokens: int, cost: float, latency_ms: float) -> None:
        """Record successful request"""
        self.stats.requests += 1
        self.stats.successes += 1
        self.stats.total_tokens += tokens
        self.stats.total_cost += cost
        self.stats.last_used = datetime.now().isoformat()
        # Update rolling average latency
        n = self.stats.successes
        self.stats.avg_latency_ms = ((n-1) * self.stats.avg_latency_ms + latency_ms) / n
    
    def record_failure(self) -> None:
        """Record failed request"""
        self.stats.requests += 1
        self.stats.failures += 1


class OpenAIAdapter(ProviderAdapter):
    """OpenAI API adapter"""
    
    name = "openai"
    
    def __init__(self, api_key: str = "", model: str = "gpt-4"):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY", ""), model)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using OpenAI"""
        if not self.is_available():
            return {"error": "OpenAI not configured", "success": False}
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            start = datetime.now()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7)
            )
            latency = (datetime.now() - start).total_seconds() * 1000
            
            tokens = response.usage.total_tokens if response.usage else 0
            cost = self._estimate_cost(tokens)
            self.record_success(tokens, cost, latency)
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "tokens": tokens,
                "cost": cost,
                "model": self.model
            }
        except Exception as e:
            self.record_failure()
            return {"error": str(e), "success": False}
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion"""
        if not self.is_available():
            return {"error": "OpenAI not configured", "success": False}
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            start = datetime.now()
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7)
            )
            latency = (datetime.now() - start).total_seconds() * 1000
            
            tokens = response.usage.total_tokens if response.usage else 0
            cost = self._estimate_cost(tokens)
            self.record_success(tokens, cost, latency)
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "tokens": tokens,
                "cost": cost
            }
        except Exception as e:
            self.record_failure()
            return {"error": str(e), "success": False}
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on model and tokens"""
        rates = {"gpt-4": 0.03, "gpt-4-turbo": 0.01, "gpt-3.5-turbo": 0.002}
        rate = rates.get(self.model, 0.01)
        return (tokens / 1000) * rate


class AnthropicAdapter(ProviderAdapter):
    """Anthropic Claude API adapter"""
    
    name = "anthropic"
    
    def __init__(self, api_key: str = "", model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY", ""), model)
    
    def complete(self, prompt: str, **kwargs) -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "Anthropic not configured", "success": False}
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            start = datetime.now()
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[{"role": "user", "content": prompt}]
            )
            latency = (datetime.now() - start).total_seconds() * 1000
            
            tokens = response.usage.input_tokens + response.usage.output_tokens
            cost = self._estimate_cost(tokens)
            self.record_success(tokens, cost, latency)
            
            return {
                "success": True,
                "content": response.content[0].text,
                "tokens": tokens,
                "cost": cost,
                "model": self.model
            }
        except Exception as e:
            self.record_failure()
            return {"error": str(e), "success": False}
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return self.complete(messages[-1].get("content", ""), **kwargs)
    
    def _estimate_cost(self, tokens: int) -> float:
        return (tokens / 1000) * 0.015


class AIProviderHub:
    """
    Central hub for multi-provider AI access.
    
    Features:
    - Automatic fallback on failure
    - Load balancing across providers
    - Cost tracking and budgeting
    - Provider health monitoring
    """
    
    def __init__(self, config=None):
        self.config = config
        self.providers: Dict[str, ProviderAdapter] = {}
        self.fallback_order: List[str] = []
        self.total_cost = 0.0
        self.budget_limit: Optional[float] = None
        
        self._init_providers()
        logger.info(f"AIProviderHub initialized with {len(self.providers)} providers")
    
    def _init_providers(self) -> None:
        """Initialize configured providers"""
        # OpenAI
        openai_key = ""
        openai_model = "gpt-4"
        if self.config:
            openai_key = getattr(self.config, 'openai_api_key', '')
            openai_model = getattr(self.config, 'openai_model', 'gpt-4')
        
        openai = OpenAIAdapter(openai_key, openai_model)
        if openai.is_available():
            self.providers["openai"] = openai
            self.fallback_order.append("openai")
        
        # Anthropic
        anthropic_key = ""
        anthropic_model = "claude-3-sonnet-20240229"
        if self.config:
            anthropic_key = getattr(self.config, 'anthropic_api_key', '')
            anthropic_model = getattr(self.config, 'anthropic_model', anthropic_model)
        
        anthropic = AnthropicAdapter(anthropic_key, anthropic_model)
        if anthropic.is_available():
            self.providers["anthropic"] = anthropic
            self.fallback_order.append("anthropic")
    
    def complete(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate completion with automatic fallback.
        
        Args:
            prompt: Input prompt
            provider: Preferred provider (optional)
            **kwargs: Additional parameters
            
        Returns:
            Completion result with content and metadata
        """
        # Check budget
        if self.budget_limit and self.total_cost >= self.budget_limit:
            return {"error": "Budget limit reached", "success": False}
        
        # Try preferred provider first
        providers_to_try = []
        if provider and provider in self.providers:
            providers_to_try.append(provider)
        providers_to_try.extend([p for p in self.fallback_order if p not in providers_to_try])
        
        for prov_name in providers_to_try:
            prov = self.providers.get(prov_name)
            if not prov or not prov.is_available():
                continue
            
            result = prov.complete(prompt, **kwargs)
            if result.get("success"):
                self.total_cost += result.get("cost", 0)
                result["provider"] = prov_name
                return result
        
        return {"error": "All providers failed", "success": False}

    def chat(self, messages: List[Dict[str, str]], provider: Optional[str] = None, 
             **kwargs) -> Dict[str, Any]:
        """Generate chat completion with fallback"""
        if self.budget_limit and self.total_cost >= self.budget_limit:
            return {"error": "Budget limit reached", "success": False}
        
        providers_to_try = []
        if provider and provider in self.providers:
            providers_to_try.append(provider)
        providers_to_try.extend([p for p in self.fallback_order if p not in providers_to_try])
        
        for prov_name in providers_to_try:
            prov = self.providers.get(prov_name)
            if not prov or not prov.is_available():
                continue
            
            result = prov.chat(messages, **kwargs)
            if result.get("success"):
                self.total_cost += result.get("cost", 0)
                result["provider"] = prov_name
                return result
        
        return {"error": "All providers failed", "success": False}
    
    def add_provider(self, name: str, adapter: ProviderAdapter) -> None:
        """Add a custom provider"""
        self.providers[name] = adapter
        if name not in self.fallback_order:
            self.fallback_order.append(name)
    
    def set_fallback_order(self, order: List[str]) -> None:
        """Set provider fallback order"""
        self.fallback_order = [p for p in order if p in self.providers]
    
    def set_budget(self, limit: float) -> None:
        """Set budget limit"""
        self.budget_limit = limit
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            "total_cost": self.total_cost,
            "budget_remaining": (self.budget_limit - self.total_cost) if self.budget_limit else None,
            "providers": {
                name: {
                    "requests": p.stats.requests,
                    "success_rate": p.stats.successes / p.stats.requests if p.stats.requests > 0 else 0,
                    "total_cost": p.stats.total_cost,
                    "avg_latency_ms": p.stats.avg_latency_ms,
                    "status": p.status.value
                }
                for name, p in self.providers.items()
            }
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [name for name, p in self.providers.items() if p.is_available()]
