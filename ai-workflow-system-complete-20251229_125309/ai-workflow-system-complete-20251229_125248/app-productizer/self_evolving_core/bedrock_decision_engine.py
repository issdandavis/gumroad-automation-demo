"""
Bedrock Decision Engine - LLM-Powered Autonomous Decisions
=========================================================

Advanced decision-making component using LLM reasoning for complex scenarios,
high-risk mutations, system conflicts, and autonomous operations.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .models import Mutation, SystemDNA, OperationResult
from .bedrock_client import BedrockClient, BedrockRequest
from .model_router import ModelRouter, TaskContext, TaskType, ComplexityLevel

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions the engine can make"""
    MUTATION_APPROVAL = "mutation_approval"
    CONFLICT_RESOLUTION = "conflict_resolution"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGY_SELECTION = "strategy_selection"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_HANDLING = "error_handling"


@dataclass
class SystemContext:
    """Current system context for decision making"""
    generation: int
    fitness_score: float
    recent_performance: Dict[str, float]
    system_load: Dict[str, float]
    active_processes: List[str]
    recent_changes: List[Dict[str, Any]]
    error_history: List[Dict[str, Any]]
    resource_usage: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "fitness_score": self.fitness_score,
            "recent_performance": self.recent_performance,
            "system_load": self.system_load,
            "active_processes": self.active_processes,
            "recent_changes": self.recent_changes,
            "error_history": self.error_history,
            "resource_usage": self.resource_usage
        }


@dataclass
class SystemConflict:
    """System conflict requiring resolution"""
    type: str
    description: str
    affected_components: List[str]
    severity: str  # "low", "medium", "high", "critical"
    current_impact: Dict[str, float]
    available_resources: Dict[str, Any]
    active_processes: List[str]
    recent_changes: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "affected_components": self.affected_components,
            "severity": self.severity,
            "current_impact": self.current_impact,
            "available_resources": self.available_resources,
            "active_processes": self.active_processes,
            "recent_changes": self.recent_changes
        }


@dataclass
class DecisionResult:
    """LLM decision result with reasoning"""
    decision_id: str
    recommendation: str  # APPROVE, REJECT, DEFER, ESCALATE
    confidence: float
    risk_assessment: Dict[str, float]
    benefits: List[str]
    drawbacks: List[str]
    mitigation_strategies: List[str]
    reasoning: str
    estimated_impact: Dict[str, float]
    alternative_options: List[str]
    escalation_required: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "risk_assessment": self.risk_assessment,
            "benefits": self.benefits,
            "drawbacks": self.drawbacks,
            "mitigation_strategies": self.mitigation_strategies,
            "reasoning": self.reasoning,
            "estimated_impact": self.estimated_impact,
            "alternative_options": self.alternative_options,
            "escalation_required": self.escalation_required
        }


@dataclass
class ResolutionStrategy:
    """Strategy for resolving system conflicts"""
    strategy_id: str
    immediate_actions: List[str]
    root_cause_analysis: str
    prevention_measures: List[str]
    resource_requirements: Dict[str, Any]
    risk_assessment: Dict[str, float]
    success_metrics: Dict[str, float]
    timeline_estimate: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "immediate_actions": self.immediate_actions,
            "root_cause_analysis": self.root_cause_analysis,
            "prevention_measures": self.prevention_measures,
            "resource_requirements": self.resource_requirements,
            "risk_assessment": self.risk_assessment,
            "success_metrics": self.success_metrics,
            "timeline_estimate": self.timeline_estimate,
            "confidence": self.confidence
        }


@dataclass
class DecisionConfig:
    """Configuration for decision engine"""
    risk_tolerance: float = 0.3
    performance_requirements: Dict[str, float] = field(default_factory=lambda: {
        "min_fitness_score": 80.0,
        "max_error_rate": 0.05,
        "min_uptime": 0.99
    })
    business_constraints: Dict[str, Any] = field(default_factory=lambda: {
        "max_downtime_minutes": 5,
        "max_cost_per_decision": 0.50,
        "require_approval_above_risk": 0.7
    })
    escalation_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "low_confidence": 0.6,
        "high_risk": 0.8,
        "critical_impact": 0.9
    })


class DecisionHistory:
    """Tracks decision history for learning and analysis"""
    
    def __init__(self):
        self.decisions: List[Dict[str, Any]] = []
        self.outcomes: Dict[str, Dict[str, Any]] = {}
    
    def record(self, mutation: Mutation, context: SystemContext, 
              decision: DecisionResult) -> None:
        """Record a decision for learning"""
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision.decision_id,
            "mutation_type": mutation.type,
            "mutation_risk": mutation.risk_score,
            "system_generation": context.generation,
            "system_fitness": context.fitness_score,
            "recommendation": decision.recommendation,
            "confidence": decision.confidence,
            "reasoning_length": len(decision.reasoning),
            "mitigation_count": len(decision.mitigation_strategies)
        }
        
        self.decisions.append(record)
        
        # Keep only last 1000 decisions
        if len(self.decisions) > 1000:
            self.decisions = self.decisions[-1000:]
    
    def record_outcome(self, decision_id: str, actual_outcome: Dict[str, Any]) -> None:
        """Record actual outcome of a decision"""
        self.outcomes[decision_id] = {
            "timestamp": datetime.now().isoformat(),
            "outcome": actual_outcome
        }
    
    def get_decision_accuracy(self) -> float:
        """Calculate decision accuracy based on outcomes"""
        if not self.outcomes:
            return 0.5  # Default neutral
        
        correct_decisions = 0
        total_decisions = len(self.outcomes)
        
        for decision_id, outcome_data in self.outcomes.items():
            # Find corresponding decision
            decision = next((d for d in self.decisions if d["decision_id"] == decision_id), None)
            if decision:
                # Simple accuracy check: did recommendation align with outcome?
                outcome = outcome_data["outcome"]
                if decision["recommendation"] == "APPROVE" and outcome.get("success", False):
                    correct_decisions += 1
                elif decision["recommendation"] == "REJECT" and not outcome.get("success", True):
                    correct_decisions += 1
        
        return correct_decisions / max(1, total_decisions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get decision history statistics"""
        if not self.decisions:
            return {"total_decisions": 0}
        
        recent_decisions = self.decisions[-100:]
        
        recommendation_counts = {}
        avg_confidence = 0.0
        
        for decision in recent_decisions:
            rec = decision["recommendation"]
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
            avg_confidence += decision["confidence"]
        
        avg_confidence /= len(recent_decisions)
        
        return {
            "total_decisions": len(self.decisions),
            "recent_decisions": len(recent_decisions),
            "recommendation_distribution": recommendation_counts,
            "average_confidence": avg_confidence,
            "decision_accuracy": self.get_decision_accuracy(),
            "outcomes_tracked": len(self.outcomes)
        }


class BedrockDecisionEngine:
    """
    LLM-powered autonomous decision making engine that uses Bedrock
    for complex reasoning about mutations, conflicts, and system operations.
    """
    
    def __init__(self, bedrock_client: BedrockClient, model_router: ModelRouter, 
                 config: DecisionConfig):
        self.bedrock = bedrock_client
        self.model_router = model_router
        self.config = config
        self.decision_history = DecisionHistory()
        
    async def evaluate_high_risk_mutation(self, mutation: Mutation, 
                                        context: SystemContext) -> DecisionResult:
        """Use LLM reasoning to evaluate high-risk mutations"""
        
        decision_id = f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Select appropriate model for decision making
        task_context = TaskContext(
            type=TaskType.DECISION,
            complexity=ComplexityLevel.HIGH,
            estimated_tokens=2000,
            accuracy_requirements=0.9,
            requires_reasoning=True
        )
        
        model_id = self.model_router.select_model(task_context)
        
        decision_prompt = self._build_mutation_evaluation_prompt(
            mutation, context, decision_id
        )
        
        request = BedrockRequest(
            model_id=model_id,
            prompt=decision_prompt,
            max_tokens=2000,
            temperature=0.2,  # Lower temperature for consistent decisions
            metadata={"operation": "mutation_evaluation", "decision_id": decision_id}
        )
        
        response = await self.bedrock.invoke_model(request)
        
        if not response.success:
            logger.error(f"Decision evaluation failed: {response.error}")
            return self._create_fallback_decision(decision_id, mutation, context, "DEFER")
        
        try:
            decision = self._parse_decision_response(response.content, decision_id)
            
            # Record decision for learning
            self.decision_history.record(mutation, context, decision)
            
            # Record model performance
            self.model_router.record_model_performance(
                model_id, TaskType.DECISION.value, True,
                response.latency_ms, response.cost_usd, 
                response.input_tokens + response.output_tokens
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to parse decision response: {e}")
            return self._create_fallback_decision(decision_id, mutation, context, "DEFER")
    
    def _build_mutation_evaluation_prompt(self, mutation: Mutation, 
                                        context: SystemContext, 
                                        decision_id: str) -> str:
        """Build comprehensive mutation evaluation prompt"""
        
        prompt = f"""You are an expert AI system architect evaluating a high-risk mutation for an autonomous AI system.

DECISION ID: {decision_id}

SYSTEM CONTEXT:
- Current Generation: {context.generation}
- Fitness Score: {context.fitness_score}
- Recent Performance: {json.dumps(context.recent_performance, indent=2)}
- System Load: {json.dumps(context.system_load, indent=2)}
- Active Processes: {len(context.active_processes)} processes
- Recent Errors: {len(context.error_history)} errors in history

PROPOSED MUTATION:
- Type: {mutation.type}
- Description: {mutation.description}
- Expected Fitness Impact: {mutation.fitness_impact:+.2f}
- Risk Score: {mutation.risk_score:.2f}
- Source: {mutation.source_ai or 'Unknown'}

DECISION CRITERIA:
- Risk Tolerance: {self.config.risk_tolerance}
- Performance Requirements: {json.dumps(self.config.performance_requirements, indent=2)}
- Business Constraints: {json.dumps(self.config.business_constraints, indent=2)}

EVALUATION REQUIREMENTS:
Analyze this mutation comprehensively and provide a decision. Consider:

1. **Risk Assessment**: Technical, operational, and business risks
2. **Benefit Analysis**: Expected improvements and value
3. **Impact Evaluation**: Short-term and long-term effects
4. **Mitigation Strategies**: How to reduce identified risks
5. **Alternative Options**: Other approaches to achieve similar benefits

Provide your analysis in this JSON format:
{{
    "recommendation": "APPROVE|REJECT|DEFER|ESCALATE",
    "confidence": 0.85,
    "risk_assessment": {{
        "technical_risk": 0.3,
        "operational_risk": 0.2,
        "business_risk": 0.4,
        "overall_risk": 0.3
    }},
    "benefits": [
        "Specific benefit 1",
        "Specific benefit 2"
    ],
    "drawbacks": [
        "Specific concern 1",
        "Specific concern 2"
    ],
    "mitigation_strategies": [
        "Specific mitigation action 1",
        "Specific mitigation action 2"
    ],
    "reasoning": "Detailed explanation of your decision logic, considering all factors and trade-offs",
    "estimated_impact": {{
        "fitness_change": 4.2,
        "performance_change": 0.05,
        "stability_impact": -0.1
    }},
    "alternative_options": [
        "Alternative approach 1",
        "Alternative approach 2"
    ],
    "escalation_required": false
}}

DECISION GUIDELINES:
- APPROVE: Low risk, clear benefits, good mitigation strategies
- REJECT: High risk, unclear benefits, insufficient mitigation
- DEFER: Need more information or better timing
- ESCALATE: Requires human judgment due to complexity or high stakes

Be thorough, specific, and focus on measurable impacts. Your decision will directly affect system evolution."""
        
        return prompt
    
    async def resolve_system_conflict(self, conflict: SystemConflict) -> ResolutionStrategy:
        """Generate conflict resolution strategy using LLM reasoning"""
        
        strategy_id = f"res_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Select model for conflict resolution
        task_context = TaskContext(
            type=TaskType.RESOLUTION,
            complexity=ComplexityLevel.HIGH if conflict.severity in ["high", "critical"] else ComplexityLevel.MEDIUM,
            estimated_tokens=2500,
            accuracy_requirements=0.85,
            requires_reasoning=True
        )
        
        model_id = self.model_router.select_model(task_context)
        
        resolution_prompt = self._build_conflict_resolution_prompt(conflict, strategy_id)
        
        request = BedrockRequest(
            model_id=model_id,
            prompt=resolution_prompt,
            max_tokens=2500,
            temperature=0.3,
            metadata={"operation": "conflict_resolution", "strategy_id": strategy_id}
        )
        
        response = await self.bedrock.invoke_model(request)
        
        if not response.success:
            logger.error(f"Conflict resolution failed: {response.error}")
            return self._create_fallback_resolution(strategy_id, conflict)
        
        try:
            strategy = self._parse_resolution_response(response.content, strategy_id)
            
            # Record model performance
            self.model_router.record_model_performance(
                model_id, TaskType.RESOLUTION.value, True,
                response.latency_ms, response.cost_usd,
                response.input_tokens + response.output_tokens
            )
            
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to parse resolution response: {e}")
            return self._create_fallback_resolution(strategy_id, conflict)
    
    def _build_conflict_resolution_prompt(self, conflict: SystemConflict, 
                                        strategy_id: str) -> str:
        """Build conflict resolution prompt"""
        
        prompt = f"""You are resolving a system conflict in an autonomous AI evolution system.

STRATEGY ID: {strategy_id}

CONFLICT DETAILS:
- Type: {conflict.type}
- Description: {conflict.description}
- Affected Components: {', '.join(conflict.affected_components)}
- Severity: {conflict.severity}
- Current Impact: {json.dumps(conflict.current_impact, indent=2)}

SYSTEM STATE:
- Available Resources: {json.dumps(conflict.available_resources, indent=2)}
- Active Processes: {len(conflict.active_processes)} processes
- Recent Changes: {len(conflict.recent_changes)} recent changes

RESOLUTION REQUIREMENTS:
Generate a comprehensive resolution strategy that:

1. **Immediately stabilizes** the system
2. **Identifies root causes** of the conflict
3. **Prevents future occurrences** through systematic improvements
4. **Minimizes disruption** to ongoing operations
5. **Provides measurable success criteria**

Provide your strategy in this JSON format:
{{
    "immediate_actions": [
        "Specific action 1 to stabilize system",
        "Specific action 2 for immediate relief"
    ],
    "root_cause_analysis": "Detailed analysis of why this conflict occurred",
    "prevention_measures": [
        "Long-term measure 1 to prevent recurrence",
        "Long-term measure 2 for system improvement"
    ],
    "resource_requirements": {{
        "cpu_usage": 0.2,
        "memory_mb": 512,
        "network_bandwidth": 0.1,
        "estimated_duration_minutes": 15
    }},
    "risk_assessment": {{
        "implementation_risk": 0.2,
        "disruption_risk": 0.1,
        "failure_risk": 0.15
    }},
    "success_metrics": {{
        "conflict_resolved": 1.0,
        "system_stability": 0.95,
        "performance_restored": 0.9
    }},
    "timeline_estimate": "15-30 minutes",
    "confidence": 0.8
}}

PRIORITY ORDER:
1. System stability and data integrity
2. Minimal disruption to operations
3. Comprehensive problem resolution
4. Prevention of future issues

Be specific, actionable, and focus on measurable outcomes."""
        
        return prompt
    
    def _parse_decision_response(self, response_content: str, decision_id: str) -> DecisionResult:
        """Parse LLM decision response"""
        try:
            # Extract JSON from response
            content = response_content.strip()
            
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif content.startswith("{") and content.endswith("}"):
                json_str = content
            else:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                else:
                    raise ValueError("No JSON structure found")
            
            data = json.loads(json_str)
            
            return DecisionResult(
                decision_id=decision_id,
                recommendation=data.get("recommendation", "DEFER"),
                confidence=data.get("confidence", 0.5),
                risk_assessment=data.get("risk_assessment", {}),
                benefits=data.get("benefits", []),
                drawbacks=data.get("drawbacks", []),
                mitigation_strategies=data.get("mitigation_strategies", []),
                reasoning=data.get("reasoning", "No reasoning provided"),
                estimated_impact=data.get("estimated_impact", {}),
                alternative_options=data.get("alternative_options", []),
                escalation_required=data.get("escalation_required", False)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse decision JSON: {e}")
            raise
    
    def _parse_resolution_response(self, response_content: str, strategy_id: str) -> ResolutionStrategy:
        """Parse LLM resolution response"""
        try:
            # Similar JSON extraction logic
            content = response_content.strip()
            
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif content.startswith("{") and content.endswith("}"):
                json_str = content
            else:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                else:
                    raise ValueError("No JSON structure found")
            
            data = json.loads(json_str)
            
            return ResolutionStrategy(
                strategy_id=strategy_id,
                immediate_actions=data.get("immediate_actions", []),
                root_cause_analysis=data.get("root_cause_analysis", "Unknown"),
                prevention_measures=data.get("prevention_measures", []),
                resource_requirements=data.get("resource_requirements", {}),
                risk_assessment=data.get("risk_assessment", {}),
                success_metrics=data.get("success_metrics", {}),
                timeline_estimate=data.get("timeline_estimate", "Unknown"),
                confidence=data.get("confidence", 0.5)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse resolution JSON: {e}")
            raise
    
    def _create_fallback_decision(self, decision_id: str, mutation: Mutation, 
                                context: SystemContext, recommendation: str) -> DecisionResult:
        """Create fallback decision when LLM fails"""
        
        return DecisionResult(
            decision_id=decision_id,
            recommendation=recommendation,
            confidence=0.3,
            risk_assessment={"overall_risk": mutation.risk_score},
            benefits=["Potential system improvement"],
            drawbacks=["LLM evaluation unavailable"],
            mitigation_strategies=["Create snapshot before applying"],
            reasoning="Fallback decision due to LLM unavailability",
            estimated_impact={"fitness_change": mutation.fitness_impact},
            alternative_options=["Defer until LLM available"],
            escalation_required=True
        )
    
    def _create_fallback_resolution(self, strategy_id: str, 
                                  conflict: SystemConflict) -> ResolutionStrategy:
        """Create fallback resolution when LLM fails"""
        
        return ResolutionStrategy(
            strategy_id=strategy_id,
            immediate_actions=["Log conflict details", "Alert administrators"],
            root_cause_analysis="Unable to analyze due to LLM unavailability",
            prevention_measures=["Restore LLM connectivity"],
            resource_requirements={"cpu_usage": 0.1, "memory_mb": 256},
            risk_assessment={"implementation_risk": 0.5},
            success_metrics={"basic_stability": 0.8},
            timeline_estimate="Manual intervention required",
            confidence=0.2
        )
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        return {
            "decision_history": self.decision_history.get_stats(),
            "config": {
                "risk_tolerance": self.config.risk_tolerance,
                "performance_requirements": self.config.performance_requirements,
                "escalation_thresholds": self.config.escalation_thresholds
            }
        }
    
    def update_config(self, new_config: DecisionConfig) -> None:
        """Update decision engine configuration"""
        self.config = new_config
        logger.info("Decision engine configuration updated")
    
    def record_decision_outcome(self, decision_id: str, outcome: Dict[str, Any]) -> None:
        """Record the actual outcome of a decision for learning"""
        self.decision_history.record_outcome(decision_id, outcome)