"""
Model Router - Intelligent LLM Selection
========================================

Intelligent routing to appropriate Bedrock models based on task requirements,
performance history, cost constraints, and availability.
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks for model selection"""
    ANALYSIS = "analysis"
    DECISION = "decision"
    STRATEGY = "strategy"
    RESOLUTION = "resolution"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"


class ComplexityLevel(Enum):
    """Task complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TaskContext:
    """Context for model selection"""
    type: TaskType
    complexity: ComplexityLevel
    estimated_tokens: int
    max_latency_ms: Optional[int] = None
    accuracy_requirements: float = 0.8  # 0.0 - 1.0
    cost_sensitivity: float = 0.5  # 0.0 - 1.0, higher = more cost sensitive
    requires_reasoning: bool = False
    requires_creativity: bool = False
    domain_specific: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "complexity": self.complexity.value,
            "estimated_tokens": self.estimated_tokens,
            "max_latency_ms": self.max_latency_ms,
            "accuracy_requirements": self.accuracy_requirements,
            "cost_sensitivity": self.cost_sensitivity,
            "requires_reasoning": self.requires_reasoning,
            "requires_creativity": self.requires_creativity,
            "domain_specific": self.domain_specific
        }


@dataclass
class ModelCapabilities:
    """Model capabilities and characteristics"""
    id: str
    name: str
    strengths: List[str]
    weaknesses: List[str]
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    max_tokens: int
    avg_latency_ms: int
    reasoning_score: float  # 0.0 - 1.0
    creativity_score: float  # 0.0 - 1.0
    accuracy_score: float  # 0.0 - 1.0
    reliability_score: float  # 0.0 - 1.0
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token usage"""
        input_cost = (input_tokens / 1000) * self.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.cost_per_1k_output_tokens
        return input_cost + output_cost


@dataclass
class ModelPerformance:
    """Historical performance data for a model"""
    model_id: str
    task_type: str
    total_requests: int = 0
    successful_requests: int = 0
    total_latency_ms: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(1, self.total_requests)
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / max(1, self.successful_requests)
    
    @property
    def avg_cost_per_request(self) -> float:
        return self.total_cost / max(1, self.total_requests)
    
    def update(self, success: bool, latency_ms: float, cost: float, tokens: int) -> None:
        """Update performance metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.total_latency_ms += latency_ms
        self.total_cost += cost
        self.total_tokens += tokens
        self.last_updated = datetime.now().isoformat()


class ModelPerformanceTracker:
    """Tracks model performance across different task types"""
    
    def __init__(self):
        self.performance_data: Dict[str, ModelPerformance] = {}
    
    def _get_key(self, model_id: str, task_type: str) -> str:
        """Get key for performance data"""
        return f"{model_id}:{task_type}"
    
    def record_performance(self, model_id: str, task_type: str, 
                         success: bool, latency_ms: float, 
                         cost: float, tokens: int) -> None:
        """Record performance data"""
        key = self._get_key(model_id, task_type)
        
        if key not in self.performance_data:
            self.performance_data[key] = ModelPerformance(
                model_id=model_id,
                task_type=task_type
            )
        
        self.performance_data[key].update(success, latency_ms, cost, tokens)
    
    def get_performance(self, model_id: str, task_type: str) -> float:
        """Get performance score (0.0 - 1.0) for model and task type"""
        key = self._get_key(model_id, task_type)
        
        if key not in self.performance_data:
            return 0.5  # Default neutral score
        
        perf = self.performance_data[key]
        
        # Combine success rate and efficiency
        success_score = perf.success_rate
        efficiency_score = min(1.0, 1000.0 / max(100, perf.avg_latency_ms))  # Normalize latency
        
        return (success_score * 0.7) + (efficiency_score * 0.3)
    
    def get_all_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get all performance data"""
        return {
            key: {
                "model_id": perf.model_id,
                "task_type": perf.task_type,
                "success_rate": perf.success_rate,
                "avg_latency_ms": perf.avg_latency_ms,
                "avg_cost_per_request": perf.avg_cost_per_request,
                "total_requests": perf.total_requests
            }
            for key, perf in self.performance_data.items()
        }


class CostOptimizer:
    """Optimizes model selection based on cost constraints"""
    
    def __init__(self, daily_budget: float = 100.0, monthly_budget: float = 2000.0):
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.daily_spend = 0.0
        self.monthly_spend = 0.0
        self.last_reset_date = datetime.now().date()
    
    def update_spend(self, cost: float) -> None:
        """Update spending tracking"""
        today = datetime.now().date()
        
        # Reset daily counter if new day
        if today != self.last_reset_date:
            self.daily_spend = 0.0
            self.last_reset_date = today
        
        self.daily_spend += cost
        self.monthly_spend += cost
    
    def should_use_cheaper_model(self, task: TaskContext) -> bool:
        """Determine if cheaper model should be used based on budget"""
        daily_usage = self.daily_spend / self.daily_budget
        monthly_usage = self.monthly_spend / self.monthly_budget
        
        # Use cheaper models if approaching budget limits
        if daily_usage > 0.8 or monthly_usage > 0.8:
            return True
        
        # Consider cost sensitivity
        if task.cost_sensitivity > 0.7 and daily_usage > 0.5:
            return True
        
        return False
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status"""
        return {
            "daily_spend": self.daily_spend,
            "daily_budget": self.daily_budget,
            "daily_usage_percent": (self.daily_spend / self.daily_budget) * 100,
            "monthly_spend": self.monthly_spend,
            "monthly_budget": self.monthly_budget,
            "monthly_usage_percent": (self.monthly_spend / self.monthly_budget) * 100,
            "daily_remaining": max(0, self.daily_budget - self.daily_spend),
            "monthly_remaining": max(0, self.monthly_budget - self.monthly_spend)
        }


class ModelRouter:
    """
    Intelligent routing to optimal Bedrock models based on task requirements,
    performance history, cost constraints, and availability.
    """
    
    # Model definitions with capabilities and pricing
    MODELS = {
        'claude-3-5-sonnet': ModelCapabilities(
            id='anthropic.claude-3-5-sonnet-20241022-v2:0',
            name='Claude 3.5 Sonnet',
            strengths=['reasoning', 'code_analysis', 'complex_decisions', 'technical_writing'],
            weaknesses=['cost', 'latency'],
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015,
            max_tokens=200000,
            avg_latency_ms=2000,
            reasoning_score=0.95,
            creativity_score=0.85,
            accuracy_score=0.92,
            reliability_score=0.95
        ),
        'claude-3-haiku': ModelCapabilities(
            id='anthropic.claude-3-haiku-20240307-v1:0',
            name='Claude 3 Haiku',
            strengths=['speed', 'simple_tasks', 'classification', 'cost_efficiency'],
            weaknesses=['complex_reasoning', 'creativity'],
            cost_per_1k_input_tokens=0.00025,
            cost_per_1k_output_tokens=0.00125,
            max_tokens=200000,
            avg_latency_ms=500,
            reasoning_score=0.7,
            creativity_score=0.6,
            accuracy_score=0.85,
            reliability_score=0.9
        ),
        'titan-text': ModelCapabilities(
            id='amazon.titan-text-premier-v1:0',
            name='Amazon Titan Text',
            strengths=['summarization', 'content_generation', 'balanced_performance'],
            weaknesses=['advanced_reasoning', 'code_analysis'],
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            max_tokens=32000,
            avg_latency_ms=1000,
            reasoning_score=0.75,
            creativity_score=0.8,
            accuracy_score=0.8,
            reliability_score=0.85
        ),
        'jamba-large': ModelCapabilities(
            id='ai21.jamba-1-5-large-v1:0',
            name='AI21 Jamba 1.5 Large',
            strengths=['long_context', 'multilingual', 'creative_writing'],
            weaknesses=['cost', 'availability'],
            cost_per_1k_input_tokens=0.002,
            cost_per_1k_output_tokens=0.008,
            max_tokens=256000,
            avg_latency_ms=1500,
            reasoning_score=0.8,
            creativity_score=0.9,
            accuracy_score=0.82,
            reliability_score=0.8
        )
    }
    
    def __init__(self, daily_budget: float = 100.0, monthly_budget: float = 2000.0):
        self.performance_tracker = ModelPerformanceTracker()
        self.cost_optimizer = CostOptimizer(daily_budget, monthly_budget)
        self.model_availability: Dict[str, bool] = {
            model_name: True for model_name in self.MODELS.keys()
        }
        self.selection_history: List[Dict[str, Any]] = []
    
    def select_model(self, task: TaskContext) -> str:
        """Select optimal model based on task requirements"""
        
        # Score each available model for this task
        scores = {}
        for model_name, model_info in self.MODELS.items():
            if not self.model_availability.get(model_name, True):
                continue  # Skip unavailable models
            
            score = self._calculate_model_score(model_info, task)
            scores[model_name] = score
        
        if not scores:
            # All models unavailable, return default
            return self.MODELS['claude-3-haiku'].id
        
        # Select highest scoring model
        best_model_name = max(scores.items(), key=lambda x: x[1])[0]
        
        # Apply cost optimization
        if self.cost_optimizer.should_use_cheaper_model(task):
            best_model_name = self._select_cost_optimized_model(scores, task)
        
        selected_model = self.MODELS[best_model_name]
        
        # Record selection
        self._record_selection(task, best_model_name, scores[best_model_name])
        
        return selected_model.id
    
    def _calculate_model_score(self, model: ModelCapabilities, task: TaskContext) -> float:
        """Calculate model suitability score for task (0.0 - 1.0)"""
        
        score = 0.0
        
        # Task type matching (40% weight)
        task_score = self._calculate_task_type_score(model, task)
        score += task_score * 0.4
        
        # Complexity matching (25% weight)
        complexity_score = self._calculate_complexity_score(model, task)
        score += complexity_score * 0.25
        
        # Performance history (20% weight)
        historical_performance = self.performance_tracker.get_performance(
            model.id, task.type.value
        )
        score += historical_performance * 0.2
        
        # Latency requirements (10% weight)
        latency_score = self._calculate_latency_score(model, task)
        score += latency_score * 0.1
        
        # Cost efficiency (5% weight)
        cost_score = self._calculate_cost_score(model, task)
        score += cost_score * 0.05
        
        return min(1.0, max(0.0, score))
    
    def _calculate_task_type_score(self, model: ModelCapabilities, task: TaskContext) -> float:
        """Calculate score based on task type requirements"""
        
        task_type_mapping = {
            TaskType.ANALYSIS: {
                'reasoning': 0.8,
                'accuracy': 0.7,
                'technical': 0.6
            },
            TaskType.DECISION: {
                'reasoning': 0.9,
                'accuracy': 0.8,
                'reliability': 0.7
            },
            TaskType.STRATEGY: {
                'reasoning': 0.8,
                'creativity': 0.6,
                'accuracy': 0.7
            },
            TaskType.CREATIVE: {
                'creativity': 0.9,
                'reasoning': 0.5,
                'accuracy': 0.6
            },
            TaskType.TECHNICAL: {
                'reasoning': 0.8,
                'accuracy': 0.9,
                'reliability': 0.7
            },
            TaskType.CLASSIFICATION: {
                'accuracy': 0.9,
                'speed': 0.7,
                'reliability': 0.6
            },
            TaskType.SUMMARIZATION: {
                'accuracy': 0.7,
                'speed': 0.6,
                'reliability': 0.8
            }
        }
        
        requirements = task_type_mapping.get(task.type, {})
        
        score = 0.0
        total_weight = 0.0
        
        for requirement, weight in requirements.items():
            if requirement == 'reasoning':
                score += model.reasoning_score * weight
            elif requirement == 'creativity':
                score += model.creativity_score * weight
            elif requirement == 'accuracy':
                score += model.accuracy_score * weight
            elif requirement == 'reliability':
                score += model.reliability_score * weight
            elif requirement == 'speed':
                # Inverse of latency (lower latency = higher speed score)
                speed_score = max(0.1, 1000.0 / model.avg_latency_ms)
                score += min(1.0, speed_score) * weight
            elif requirement == 'technical':
                # Check if model has technical strengths
                technical_score = 0.8 if any(s in ['code_analysis', 'technical_writing', 'reasoning'] 
                                           for s in model.strengths) else 0.3
                score += technical_score * weight
            
            total_weight += weight
        
        return score / max(0.1, total_weight)
    
    def _calculate_complexity_score(self, model: ModelCapabilities, task: TaskContext) -> float:
        """Calculate score based on task complexity requirements"""
        
        if task.complexity == ComplexityLevel.HIGH:
            # High complexity tasks need strong reasoning
            return model.reasoning_score * 0.8 + model.accuracy_score * 0.2
        elif task.complexity == ComplexityLevel.MEDIUM:
            # Medium complexity needs balanced capabilities
            return (model.reasoning_score + model.accuracy_score + model.reliability_score) / 3
        else:  # LOW complexity
            # Low complexity prioritizes speed and cost efficiency
            speed_score = max(0.1, 1000.0 / model.avg_latency_ms)
            cost_score = max(0.1, 0.01 / model.cost_per_1k_input_tokens)  # Inverse of cost
            return (min(1.0, speed_score) + min(1.0, cost_score)) / 2
    
    def _calculate_latency_score(self, model: ModelCapabilities, task: TaskContext) -> float:
        """Calculate score based on latency requirements"""
        
        if task.max_latency_ms is None:
            return 0.5  # Neutral if no requirement
        
        if model.avg_latency_ms <= task.max_latency_ms:
            # Meets requirement, score based on how much better
            excess_capacity = task.max_latency_ms - model.avg_latency_ms
            return min(1.0, 0.7 + (excess_capacity / task.max_latency_ms) * 0.3)
        else:
            # Doesn't meet requirement
            return max(0.0, 0.5 - (model.avg_latency_ms - task.max_latency_ms) / task.max_latency_ms)
    
    def _calculate_cost_score(self, model: ModelCapabilities, task: TaskContext) -> float:
        """Calculate score based on cost efficiency"""
        
        estimated_cost = model.calculate_cost(
            task.estimated_tokens // 2,  # Rough input/output split
            task.estimated_tokens // 2
        )
        
        # Normalize cost score (lower cost = higher score)
        max_reasonable_cost = 0.1  # $0.10 per request
        cost_score = max(0.0, 1.0 - (estimated_cost / max_reasonable_cost))
        
        # Weight by cost sensitivity
        return cost_score * task.cost_sensitivity + 0.5 * (1 - task.cost_sensitivity)
    
    def _select_cost_optimized_model(self, scores: Dict[str, float], 
                                   task: TaskContext) -> str:
        """Select most cost-effective model that meets minimum requirements"""
        
        # Filter models that meet minimum accuracy requirements
        viable_models = []
        for model_name, score in scores.items():
            model = self.MODELS[model_name]
            if (score >= 0.6 and  # Minimum overall score
                model.accuracy_score >= task.accuracy_requirements):
                
                cost = model.calculate_cost(
                    task.estimated_tokens // 2,
                    task.estimated_tokens // 2
                )
                viable_models.append((model_name, score, cost))
        
        if not viable_models:
            # No viable models, return cheapest available
            cheapest = min(scores.keys(), 
                         key=lambda m: self.MODELS[m].cost_per_1k_input_tokens)
            return cheapest
        
        # Select model with best score/cost ratio
        best_model = max(viable_models, key=lambda x: x[1] / max(0.001, x[2]))
        return best_model[0]
    
    def _record_selection(self, task: TaskContext, model_name: str, score: float) -> None:
        """Record model selection for analysis"""
        
        selection_record = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task.type.value,
            "task_complexity": task.complexity.value,
            "selected_model": model_name,
            "model_id": self.MODELS[model_name].id,
            "selection_score": score,
            "estimated_tokens": task.estimated_tokens,
            "cost_sensitivity": task.cost_sensitivity,
            "accuracy_requirements": task.accuracy_requirements
        }
        
        self.selection_history.append(selection_record)
        
        # Keep only last 1000 selections
        if len(self.selection_history) > 1000:
            self.selection_history = self.selection_history[-1000:]
    
    def record_model_performance(self, model_id: str, task_type: str,
                               success: bool, latency_ms: float,
                               cost: float, tokens: int) -> None:
        """Record actual model performance"""
        
        self.performance_tracker.record_performance(
            model_id, task_type, success, latency_ms, cost, tokens
        )
        
        self.cost_optimizer.update_spend(cost)
    
    def set_model_availability(self, model_name: str, available: bool) -> None:
        """Set model availability status"""
        if model_name in self.MODELS:
            self.model_availability[model_name] = available
            logger.info(f"Model {model_name} availability set to {available}")
    
    def get_alternative_model(self, failed_model_id: str) -> Optional[str]:
        """Get alternative model when primary fails"""
        
        # Find the failed model name
        failed_model_name = None
        for name, model in self.MODELS.items():
            if model.id == failed_model_id:
                failed_model_name = name
                break
        
        if failed_model_name:
            # Mark as temporarily unavailable
            self.model_availability[failed_model_name] = False
        
        # Return next best available model
        available_models = [
            name for name, available in self.model_availability.items()
            if available and name != failed_model_name
        ]
        
        if available_models:
            # Return most reliable available model
            best_alternative = max(available_models, 
                                 key=lambda m: self.MODELS[m].reliability_score)
            return self.MODELS[best_alternative].id
        
        return None
    
    def get_router_stats(self) -> Dict[str, Any]:
        """Get router performance statistics"""
        
        recent_selections = self.selection_history[-100:] if self.selection_history else []
        
        model_usage = {}
        for selection in recent_selections:
            model = selection["selected_model"]
            model_usage[model] = model_usage.get(model, 0) + 1
        
        return {
            "total_selections": len(self.selection_history),
            "recent_selections": len(recent_selections),
            "model_usage_frequency": model_usage,
            "model_availability": self.model_availability.copy(),
            "budget_status": self.cost_optimizer.get_budget_status(),
            "performance_data": self.performance_tracker.get_all_performance(),
            "avg_selection_score": sum(s.get("selection_score", 0) for s in recent_selections) / max(1, len(recent_selections))
        }
    
    def optimize_routing(self) -> Dict[str, Any]:
        """Analyze and optimize routing decisions"""
        
        optimization_results = {
            "recommendations": [],
            "performance_insights": [],
            "cost_insights": []
        }
        
        # Analyze model performance
        perf_data = self.performance_tracker.get_all_performance()
        
        for key, perf in perf_data.items():
            model_id, task_type = key.split(":")
            
            if perf["success_rate"] < 0.8:
                optimization_results["recommendations"].append(
                    f"Consider alternative to {model_id} for {task_type} tasks (success rate: {perf['success_rate']:.1%})"
                )
            
            if perf["avg_latency_ms"] > 3000:
                optimization_results["performance_insights"].append(
                    f"High latency detected for {model_id} on {task_type} tasks: {perf['avg_latency_ms']:.0f}ms"
                )
        
        # Analyze cost efficiency
        budget_status = self.cost_optimizer.get_budget_status()
        
        if budget_status["daily_usage_percent"] > 80:
            optimization_results["cost_insights"].append(
                "High daily budget usage - consider using more cost-effective models"
            )
        
        return optimization_results