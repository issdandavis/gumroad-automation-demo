"""
Enhanced Autonomy Controller with Bedrock Decision Engine Integration
====================================================================

Extends the existing AutonomyController with LLM-powered decision making
for complex scenarios, high-risk mutations, and system conflicts.
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .autonomy import AutonomyController, ApprovalRequest, RiskLevel, ApprovalStatus
from .bedrock_decision_engine import (
    BedrockDecisionEngine, DecisionResult, SystemContext, SystemConflict,
    ResolutionStrategy, DecisionConfig
)
from .models import Mutation, OperationResult, SystemDNA, FitnessScore
from .config import AutonomyConfig

logger = logging.getLogger(__name__)


@dataclass
class EnhancedDecision:
    """Enhanced decision with LLM reasoning"""
    original_decision: str  # "auto_approve", "require_approval", "reject"
    llm_decision: Optional[DecisionResult] = None
    final_decision: str = ""
    reasoning: str = ""
    confidence: float = 0.0
    escalation_required: bool = False


class EnhancedAutonomyController(AutonomyController):
    """
    Enhanced autonomy controller that uses Bedrock Decision Engine
    for complex decision making while maintaining compatibility with
    the existing framework.
    """
    
    def __init__(self, config: Optional[AutonomyConfig] = None,
                 decision_engine: Optional[BedrockDecisionEngine] = None):
        super().__init__(config)
        self.decision_engine = decision_engine
        self.llm_decisions: List[EnhancedDecision] = []
        self.system_conflicts: Dict[str, SystemConflict] = {}
        
        # Enhanced risk thresholds for LLM integration
        self.llm_thresholds = {
            "use_llm_above_risk": 0.4,  # Use LLM for decisions above this risk
            "require_llm_above_risk": 0.6,  # Require LLM for decisions above this
            "escalate_above_risk": 0.8,  # Always escalate above this risk
            "min_confidence_threshold": 0.7  # Minimum LLM confidence to accept
        }
        
        logger.info("Enhanced AutonomyController initialized with Bedrock integration")
    
    def assess_risk_enhanced(self, mutation: Mutation, 
                           system_context: Optional[SystemContext] = None) -> float:
        """Enhanced risk assessment with system context"""
        
        # Start with base risk assessment
        base_risk = super().assess_risk(mutation)
        
        # Add context-based risk factors if available
        if system_context:
            context_risk = self._assess_context_risk(system_context)
            # Weighted combination: 70% base risk, 30% context risk
            enhanced_risk = (base_risk * 0.7) + (context_risk * 0.3)
        else:
            enhanced_risk = base_risk
        
        # Ensure bounds
        enhanced_risk = max(0.0, min(1.0, enhanced_risk))
        
        self._log_audit("enhanced_risk_assessment", {
            "mutation_type": mutation.type,
            "base_risk": base_risk,
            "enhanced_risk": enhanced_risk,
            "has_context": system_context is not None
        })
        
        return enhanced_risk
    
    def _assess_context_risk(self, context: SystemContext) -> float:
        """Assess risk based on system context"""
        risk = 0.0
        
        # Risk from low fitness score
        if context.fitness_score < 80.0:
            risk += 0.2
        
        # Risk from high error rate
        error_rate = 1.0 - context.recent_performance.get("success_rate", 1.0)
        if error_rate > 0.1:
            risk += error_rate * 0.3
        
        # Risk from high system load
        cpu_load = context.system_load.get("cpu", 0.0)
        memory_load = context.system_load.get("memory", 0.0)
        if cpu_load > 0.8 or memory_load > 0.8:
            risk += 0.15
        
        # Risk from recent errors
        if len(context.error_history) > 5:
            risk += 0.1
        
        return min(1.0, risk)
    
    async def should_auto_approve_enhanced(self, mutation: Mutation,
                                         system_context: Optional[SystemContext] = None) -> EnhancedDecision:
        """
        Enhanced auto-approval decision using LLM for complex cases
        """
        
        # Get enhanced risk score
        risk_score = self.assess_risk_enhanced(mutation, system_context)
        mutation.risk_score = risk_score
        
        # Start with base decision logic
        base_auto_approve = super().should_auto_approve(mutation)
        
        enhanced_decision = EnhancedDecision(
            original_decision="auto_approve" if base_auto_approve else "require_approval"
        )
        
        # Use LLM for decisions above threshold
        if (self.decision_engine and 
            risk_score >= self.llm_thresholds["use_llm_above_risk"]):
            
            try:
                # Get LLM decision
                if not system_context:
                    system_context = self._create_default_context()
                
                llm_result = await self.decision_engine.evaluate_high_risk_mutation(
                    mutation, system_context
                )
                
                enhanced_decision.llm_decision = llm_result
                enhanced_decision.confidence = llm_result.confidence
                enhanced_decision.reasoning = llm_result.reasoning
                
                # Make final decision based on LLM recommendation and confidence
                if llm_result.confidence >= self.llm_thresholds["min_confidence_threshold"]:
                    if llm_result.recommendation == "APPROVE":
                        enhanced_decision.final_decision = "auto_approve"
                    elif llm_result.recommendation == "REJECT":
                        enhanced_decision.final_decision = "reject"
                    elif llm_result.recommendation == "DEFER":
                        enhanced_decision.final_decision = "require_approval"
                    else:  # ESCALATE
                        enhanced_decision.final_decision = "escalate"
                        enhanced_decision.escalation_required = True
                else:
                    # Low confidence, escalate
                    enhanced_decision.final_decision = "escalate"
                    enhanced_decision.escalation_required = True
                    enhanced_decision.reasoning += " (Low LLM confidence)"
                
            except Exception as e:
                logger.error(f"LLM decision failed: {e}")
                # Fall back to base decision with escalation flag
                enhanced_decision.final_decision = "escalate"
                enhanced_decision.escalation_required = True
                enhanced_decision.reasoning = f"LLM decision failed: {str(e)}"
        
        else:
            # Use base decision for low-risk mutations
            enhanced_decision.final_decision = enhanced_decision.original_decision
            enhanced_decision.reasoning = "Base risk assessment used"
            enhanced_decision.confidence = 0.8 if base_auto_approve else 0.6
        
        # Always escalate very high risk
        if risk_score >= self.llm_thresholds["escalate_above_risk"]:
            enhanced_decision.final_decision = "escalate"
            enhanced_decision.escalation_required = True
            enhanced_decision.reasoning += " (Very high risk - mandatory escalation)"
        
        # Record decision
        self.llm_decisions.append(enhanced_decision)
        
        # Keep only last 100 decisions
        if len(self.llm_decisions) > 100:
            self.llm_decisions = self.llm_decisions[-100:]
        
        self._log_audit("enhanced_decision", {
            "mutation_type": mutation.type,
            "risk_score": risk_score,
            "original_decision": enhanced_decision.original_decision,
            "final_decision": enhanced_decision.final_decision,
            "llm_used": enhanced_decision.llm_decision is not None,
            "confidence": enhanced_decision.confidence,
            "escalation_required": enhanced_decision.escalation_required
        })
        
        return enhanced_decision
    
    async def resolve_system_conflict(self, conflict: SystemConflict) -> ResolutionStrategy:
        """Resolve system conflict using LLM reasoning"""
        
        if not self.decision_engine:
            logger.error("No decision engine available for conflict resolution")
            return self._create_fallback_resolution(conflict)
        
        try:
            strategy = await self.decision_engine.resolve_system_conflict(conflict)
            
            # Store conflict and strategy
            self.system_conflicts[conflict.type] = conflict
            
            self._log_audit("conflict_resolved", {
                "conflict_type": conflict.type,
                "severity": conflict.severity,
                "strategy_confidence": strategy.confidence,
                "immediate_actions": len(strategy.immediate_actions)
            })
            
            return strategy
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return self._create_fallback_resolution(conflict)
    
    def _create_default_context(self) -> SystemContext:
        """Create default system context when none provided"""
        return SystemContext(
            generation=1,
            fitness_score=100.0,
            recent_performance={"success_rate": 0.95, "avg_latency": 1.0},
            system_load={"cpu": 0.5, "memory": 0.6},
            active_processes=["main", "monitor"],
            recent_changes=[],
            error_history=[],
            resource_usage={"cpu": 0.5, "memory": 0.6, "disk": 0.3}
        )
    
    def _create_fallback_resolution(self, conflict: SystemConflict) -> ResolutionStrategy:
        """Create fallback resolution when LLM unavailable"""
        return ResolutionStrategy(
            strategy_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            immediate_actions=["Log conflict", "Alert administrators"],
            root_cause_analysis="Unable to analyze - LLM unavailable",
            prevention_measures=["Restore LLM connectivity"],
            resource_requirements={"manual_intervention": True},
            risk_assessment={"unknown_risk": 0.5},
            success_metrics={"basic_stability": 0.8},
            timeline_estimate="Manual intervention required",
            confidence=0.2
        )
    
    def create_system_context(self, dna: SystemDNA, 
                            fitness_history: List[FitnessScore]) -> SystemContext:
        """Create system context from current state"""
        
        # Get latest fitness metrics
        latest_fitness = fitness_history[-1] if fitness_history else FitnessScore(
            overall=100.0, success_rate=1.0, healing_speed=1.0, 
            cost_efficiency=1.0, uptime=1.0
        )
        
        # Calculate recent performance
        recent_performance = {
            "success_rate": latest_fitness.success_rate,
            "healing_speed": latest_fitness.healing_speed,
            "cost_efficiency": latest_fitness.cost_efficiency,
            "uptime": latest_fitness.uptime
        }
        
        # Estimate system load (would be real metrics in production)
        system_load = {
            "cpu": 0.4 + (len(dna.mutations) * 0.01),  # Rough estimate
            "memory": 0.3 + (dna.generation * 0.005),
            "network": 0.2
        }
        
        # Extract recent changes
        recent_changes = [
            {
                "type": "mutation",
                "mutation_type": m.type,
                "timestamp": m.timestamp,
                "fitness_impact": m.fitness_impact
            }
            for m in dna.mutations[-5:]  # Last 5 mutations
        ]
        
        return SystemContext(
            generation=dna.generation,
            fitness_score=dna.fitness_score,
            recent_performance=recent_performance,
            system_load=system_load,
            active_processes=["framework", "evolution", "monitoring"],
            recent_changes=recent_changes,
            error_history=[],  # Would be populated from logs
            resource_usage=system_load
        )
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Get enhanced statistics including LLM decisions"""
        
        base_stats = super().get_session_stats()
        
        # LLM decision statistics
        llm_stats = {
            "total_llm_decisions": len(self.llm_decisions),
            "llm_usage_rate": 0.0,
            "avg_llm_confidence": 0.0,
            "decision_distribution": {},
            "escalation_rate": 0.0
        }
        
        if self.llm_decisions:
            llm_used = sum(1 for d in self.llm_decisions if d.llm_decision is not None)
            llm_stats["llm_usage_rate"] = llm_used / len(self.llm_decisions)
            
            confidences = [d.confidence for d in self.llm_decisions if d.confidence > 0]
            if confidences:
                llm_stats["avg_llm_confidence"] = sum(confidences) / len(confidences)
            
            # Decision distribution
            for decision in self.llm_decisions:
                final = decision.final_decision
                llm_stats["decision_distribution"][final] = llm_stats["decision_distribution"].get(final, 0) + 1
            
            # Escalation rate
            escalations = sum(1 for d in self.llm_decisions if d.escalation_required)
            llm_stats["escalation_rate"] = escalations / len(self.llm_decisions)
        
        # Conflict resolution statistics
        conflict_stats = {
            "total_conflicts": len(self.system_conflicts),
            "conflict_types": list(self.system_conflicts.keys())
        }
        
        return {
            **base_stats,
            "llm_decisions": llm_stats,
            "conflict_resolution": conflict_stats,
            "decision_engine_available": self.decision_engine is not None
        }
    
    def record_decision_outcome(self, decision_id: str, outcome: Dict[str, Any]) -> None:
        """Record outcome of LLM decision for learning"""
        if self.decision_engine:
            self.decision_engine.record_decision_outcome(decision_id, outcome)
    
    def update_llm_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update LLM decision thresholds"""
        self.llm_thresholds.update(new_thresholds)
        logger.info(f"LLM thresholds updated: {self.llm_thresholds}")
    
    def get_recent_llm_decisions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent LLM decisions for analysis"""
        recent = self.llm_decisions[-limit:] if self.llm_decisions else []
        
        return [
            {
                "original_decision": d.original_decision,
                "final_decision": d.final_decision,
                "confidence": d.confidence,
                "reasoning": d.reasoning[:200] + "..." if len(d.reasoning) > 200 else d.reasoning,
                "escalation_required": d.escalation_required,
                "llm_used": d.llm_decision is not None
            }
            for d in recent
        ]