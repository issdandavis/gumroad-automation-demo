"""
Autonomy Controller for Self-Evolving AI Framework
==================================================

Manages autonomous workflow execution with:
- Risk-based approval system
- Configurable safety boundaries
- Human escalation for high-risk operations
- Checkpoint-based execution
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from .models import Mutation, WorkflowResult, OperationResult
from .config import AutonomyConfig

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for operations"""
    MINIMAL = "minimal"      # 0.0 - 0.1
    LOW = "low"              # 0.1 - 0.3
    MEDIUM = "medium"        # 0.3 - 0.5
    HIGH = "high"            # 0.5 - 0.7
    CRITICAL = "critical"    # 0.7 - 1.0


class ApprovalStatus(Enum):
    """Approval status for operations"""
    AUTO_APPROVED = "auto_approved"
    PENDING_REVIEW = "pending_review"
    HUMAN_APPROVED = "human_approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    """Request for human approval"""
    id: str
    item_type: str
    item_data: Dict[str, Any]
    risk_score: float
    risk_level: RiskLevel
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: ApprovalStatus = ApprovalStatus.PENDING_REVIEW
    reviewer: Optional[str] = None
    review_timestamp: Optional[str] = None
    review_notes: Optional[str] = None


@dataclass
class Checkpoint:
    """Workflow checkpoint for safe stopping points"""
    id: str
    workflow_id: str
    step_number: int
    timestamp: str
    state_snapshot: Dict[str, Any]
    can_resume: bool = True


@dataclass
class Workflow:
    """Workflow definition for autonomous execution"""
    id: str
    name: str
    steps: List[Dict[str, Any]]
    priority: str = "normal"
    max_runtime_hours: float = 24.0
    checkpoint_interval: int = 5  # steps between checkpoints
    allow_mutations: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutonomyController:
    """
    Controls autonomous AI operations with safety boundaries.
    
    Features:
    - Risk assessment for all operations
    - Auto-approval for low-risk items
    - Human escalation for high-risk items
    - Checkpoint-based workflow execution
    - Audit logging of all decisions
    """
    
    def __init__(self, config: Optional[AutonomyConfig] = None):
        self.config = config or AutonomyConfig()
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.session_mutations: int = 0
        self.session_start: datetime = datetime.now()
        self.audit_log: List[Dict[str, Any]] = []
        self._approval_callbacks: List[Callable] = []
        
        # Risk factors and their weights
        self.risk_factors = {
            "mutation_type": {
                "communication_enhancement": 0.1,
                "language_expansion": 0.15,
                "storage_optimization": 0.2,
                "intelligence_upgrade": 0.4,
                "protocol_improvement": 0.3,
                "autonomy_adjustment": 0.6,
                "provider_addition": 0.25,
                "plugin_integration": 0.35
            },
            "fitness_impact_threshold": 10.0,  # High impact above this
            "source_trust": {
                "system": 0.0,
                "known_ai": 0.1,
                "unknown_ai": 0.3,
                "external": 0.5
            }
        }
        
        logger.info(f"AutonomyController initialized with risk_threshold={self.config.risk_threshold}")
    
    def assess_risk(self, mutation: Mutation) -> float:
        """
        Calculate risk score for proposed mutation (0.0-1.0).
        
        Factors considered:
        - Mutation type inherent risk
        - Fitness impact magnitude
        - Source trustworthiness
        - Session mutation count
        - Time since session start
        """
        risk = 0.0
        
        # Base risk from mutation type
        type_risk = self.risk_factors["mutation_type"].get(mutation.type, 0.3)
        risk += type_risk * 0.4
        
        # Risk from fitness impact
        impact_magnitude = abs(mutation.fitness_impact)
        if impact_magnitude > self.risk_factors["fitness_impact_threshold"]:
            impact_risk = min(impact_magnitude / 20.0, 1.0)
            risk += impact_risk * 0.3
        
        # Risk from source
        source = mutation.source_ai or "system"
        if source in ["Kiro", "ChatGPT", "Claude", "Perplexity"]:
            source_type = "known_ai"
        elif source == "system":
            source_type = "system"
        else:
            source_type = "unknown_ai"
        source_risk = self.risk_factors["source_trust"].get(source_type, 0.3)
        risk += source_risk * 0.2
        
        # Risk from session state
        if self.session_mutations >= self.config.max_mutations_per_session * 0.8:
            risk += 0.1  # Approaching mutation limit
        
        # Ensure bounds
        risk = max(0.0, min(1.0, risk))
        
        self._log_audit("risk_assessment", {
            "mutation_type": mutation.type,
            "calculated_risk": risk,
            "factors": {
                "type_risk": type_risk,
                "source": source,
                "session_mutations": self.session_mutations
            }
        })
        
        return risk
    
    def get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if risk_score < 0.1:
            return RiskLevel.MINIMAL
        elif risk_score < 0.3:
            return RiskLevel.LOW
        elif risk_score < 0.5:
            return RiskLevel.MEDIUM
        elif risk_score < 0.7:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def should_auto_approve(self, mutation: Mutation) -> bool:
        """
        Determine if mutation can be auto-approved based on risk.
        
        Returns True if:
        - Risk score is below threshold
        - Auto-approval is enabled
        - Session limits not exceeded
        """
        if not self.config.auto_approve_low_risk:
            return False
        
        risk_score = mutation.risk_score if mutation.risk_score > 0 else self.assess_risk(mutation)
        
        # Check risk threshold
        if risk_score >= self.config.risk_threshold:
            return False
        
        # Check session limits
        if self.session_mutations >= self.config.max_mutations_per_session:
            logger.warning("Session mutation limit reached, requiring human approval")
            return False
        
        # Check session runtime
        runtime = datetime.now() - self.session_start
        if runtime > timedelta(hours=self.config.max_autonomous_runtime_hours):
            logger.warning("Session runtime limit reached, requiring human approval")
            return False
        
        return True
    
    def request_approval(self, item: Any, item_type: str, reason: str) -> ApprovalRequest:
        """Queue item for human review with context"""
        risk_score = 0.5
        if isinstance(item, Mutation):
            risk_score = item.risk_score if item.risk_score > 0 else self.assess_risk(item)
        
        request = ApprovalRequest(
            id=f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            item_type=item_type,
            item_data=item.to_dict() if hasattr(item, 'to_dict') else {"data": str(item)},
            risk_score=risk_score,
            risk_level=self.get_risk_level(risk_score),
            reason=reason
        )
        
        self.pending_approvals[request.id] = request
        
        self._log_audit("approval_requested", {
            "request_id": request.id,
            "item_type": item_type,
            "risk_score": risk_score,
            "reason": reason
        })
        
        # Notify callbacks
        for callback in self._approval_callbacks:
            try:
                callback(request)
            except Exception as e:
                logger.error(f"Approval callback error: {e}")
        
        logger.info(f"Approval requested: {request.id} ({item_type}) - Risk: {risk_score:.2f}")
        return request
    
    def approve(self, request_id: str, reviewer: str, notes: Optional[str] = None) -> bool:
        """Approve a pending request"""
        if request_id not in self.pending_approvals:
            logger.error(f"Approval request not found: {request_id}")
            return False
        
        request = self.pending_approvals[request_id]
        request.status = ApprovalStatus.HUMAN_APPROVED
        request.reviewer = reviewer
        request.review_timestamp = datetime.now().isoformat()
        request.review_notes = notes
        
        self._log_audit("approval_granted", {
            "request_id": request_id,
            "reviewer": reviewer,
            "notes": notes
        })
        
        logger.info(f"Approval granted: {request_id} by {reviewer}")
        return True
    
    def reject(self, request_id: str, reviewer: str, reason: str) -> bool:
        """Reject a pending request"""
        if request_id not in self.pending_approvals:
            logger.error(f"Approval request not found: {request_id}")
            return False
        
        request = self.pending_approvals[request_id]
        request.status = ApprovalStatus.REJECTED
        request.reviewer = reviewer
        request.review_timestamp = datetime.now().isoformat()
        request.review_notes = reason
        
        self._log_audit("approval_rejected", {
            "request_id": request_id,
            "reviewer": reviewer,
            "reason": reason
        })
        
        logger.info(f"Approval rejected: {request_id} by {reviewer}")
        return True
    
    def execute_workflow(self, workflow: Workflow, 
                        step_executor: Callable[[Dict[str, Any]], OperationResult]) -> WorkflowResult:
        """
        Execute workflow autonomously until completion or checkpoint.
        
        Args:
            workflow: Workflow definition
            step_executor: Function to execute each step
            
        Returns:
            WorkflowResult with execution details
        """
        start_time = datetime.now()
        steps_completed = 0
        mutations_applied = []
        errors = []
        last_checkpoint_id = None
        
        self._log_audit("workflow_started", {
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "total_steps": len(workflow.steps)
        })
        
        try:
            for i, step in enumerate(workflow.steps):
                # Check runtime limit
                runtime = datetime.now() - start_time
                max_runtime = timedelta(hours=workflow.max_runtime_hours)
                if runtime > max_runtime:
                    logger.warning(f"Workflow {workflow.id} exceeded max runtime")
                    break
                
                # Execute step
                try:
                    result = step_executor(step)
                    
                    if result.success:
                        steps_completed += 1
                        if result.data and "mutation_id" in result.data:
                            mutations_applied.append(result.data["mutation_id"])
                    else:
                        errors.append(f"Step {i}: {result.error}")
                        if step.get("required", True):
                            break  # Stop on required step failure
                            
                except Exception as e:
                    errors.append(f"Step {i}: {str(e)}")
                    logger.error(f"Workflow step {i} failed: {e}")
                    break
                
                # Create checkpoint if needed
                if (i + 1) % workflow.checkpoint_interval == 0:
                    checkpoint = self._create_checkpoint(workflow, i + 1, {
                        "steps_completed": steps_completed,
                        "mutations_applied": mutations_applied
                    })
                    last_checkpoint_id = checkpoint.id
                    
                    self._log_audit("checkpoint_created", {
                        "workflow_id": workflow.id,
                        "checkpoint_id": checkpoint.id,
                        "step_number": i + 1
                    })
        
        except Exception as e:
            errors.append(f"Workflow error: {str(e)}")
            logger.error(f"Workflow {workflow.id} failed: {e}")
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        result = WorkflowResult(
            success=len(errors) == 0 and steps_completed == len(workflow.steps),
            workflow_id=workflow.id,
            steps_completed=steps_completed,
            total_steps=len(workflow.steps),
            duration_ms=duration_ms,
            mutations_applied=mutations_applied,
            errors=errors,
            checkpoint_id=last_checkpoint_id
        )
        
        self._log_audit("workflow_completed", {
            "workflow_id": workflow.id,
            "success": result.success,
            "steps_completed": steps_completed,
            "duration_ms": duration_ms,
            "errors": errors
        })
        
        return result
    
    def _create_checkpoint(self, workflow: Workflow, step_number: int, 
                          state: Dict[str, Any]) -> Checkpoint:
        """Create a workflow checkpoint"""
        checkpoint = Checkpoint(
            id=f"ckpt_{workflow.id}_{step_number}_{datetime.now().strftime('%H%M%S')}",
            workflow_id=workflow.id,
            step_number=step_number,
            timestamp=datetime.now().isoformat(),
            state_snapshot=state
        )
        
        self.checkpoints[checkpoint.id] = checkpoint
        return checkpoint
    
    def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get checkpoint for workflow resumption"""
        return self.checkpoints.get(checkpoint_id)
    
    def record_mutation(self) -> None:
        """Record that a mutation was applied in this session"""
        self.session_mutations += 1
    
    def reset_session(self) -> None:
        """Reset session counters"""
        self.session_mutations = 0
        self.session_start = datetime.now()
        logger.info("Autonomy session reset")
    
    def on_approval_request(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Register callback for approval requests"""
        self._approval_callbacks.append(callback)
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return [r for r in self.pending_approvals.values() 
                if r.status == ApprovalStatus.PENDING_REVIEW]
    
    def _log_audit(self, action: str, details: Dict[str, Any]) -> None:
        """Log action to audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.audit_log.append(entry)
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries"""
        return self.audit_log[-limit:]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        runtime = datetime.now() - self.session_start
        return {
            "session_start": self.session_start.isoformat(),
            "runtime_seconds": runtime.total_seconds(),
            "mutations_applied": self.session_mutations,
            "mutations_remaining": max(0, self.config.max_mutations_per_session - self.session_mutations),
            "pending_approvals": len(self.get_pending_approvals()),
            "checkpoints_created": len(self.checkpoints)
        }
