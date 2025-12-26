"""
Self-Healing System for Self-Evolving AI Framework
=================================================

Automatic error recovery with:
- Strategy-based healing approaches
- Escalation to human when needed
- Integration with rollback system
- Learning from healing outcomes
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors the system can encounter"""
    STORAGE_FAILURE = "storage_failure"
    MUTATION_FAILURE = "mutation_failure"
    COMMUNICATION_FAILURE = "communication_failure"
    FITNESS_DEGRADATION = "fitness_degradation"
    PROVIDER_FAILURE = "provider_failure"
    VALIDATION_FAILURE = "validation_failure"
    SYNC_FAILURE = "sync_failure"
    UNKNOWN = "unknown"


class HealingStrategy(Enum):
    """Available healing strategies"""
    RETRY = "retry"
    ROLLBACK = "rollback"
    FALLBACK = "fallback"
    RESTART = "restart"
    SKIP = "skip"
    ESCALATE = "escalate"


@dataclass
class HealingAttempt:
    """Record of a healing attempt"""
    id: str
    error_type: str
    strategy: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class HealingResult:
    """Result of healing operation"""
    success: bool
    error_type: str
    strategy_used: str
    attempts: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    escalated: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class SelfHealer:
    """
    Automatic error recovery system.
    
    Features:
    - Multiple healing strategies per error type
    - Configurable retry limits
    - Automatic escalation when healing fails
    - Learning from healing outcomes
    - Integration with rollback system
    """
    
    # Default strategies for each error type (in order of preference)
    DEFAULT_STRATEGIES: Dict[str, List[str]] = {
        ErrorType.STORAGE_FAILURE.value: [
            HealingStrategy.RETRY.value,
            HealingStrategy.FALLBACK.value,
            HealingStrategy.ESCALATE.value
        ],
        ErrorType.MUTATION_FAILURE.value: [
            HealingStrategy.ROLLBACK.value,
            HealingStrategy.SKIP.value,
            HealingStrategy.ESCALATE.value
        ],
        ErrorType.COMMUNICATION_FAILURE.value: [
            HealingStrategy.RETRY.value,
            HealingStrategy.FALLBACK.value,
            HealingStrategy.SKIP.value
        ],
        ErrorType.FITNESS_DEGRADATION.value: [
            HealingStrategy.ROLLBACK.value,
            HealingStrategy.RESTART.value,
            HealingStrategy.ESCALATE.value
        ],
        ErrorType.PROVIDER_FAILURE.value: [
            HealingStrategy.FALLBACK.value,
            HealingStrategy.RETRY.value,
            HealingStrategy.ESCALATE.value
        ],
        ErrorType.VALIDATION_FAILURE.value: [
            HealingStrategy.SKIP.value,
            HealingStrategy.ESCALATE.value
        ],
        ErrorType.SYNC_FAILURE.value: [
            HealingStrategy.RETRY.value,
            HealingStrategy.FALLBACK.value,
            HealingStrategy.SKIP.value
        ],
        ErrorType.UNKNOWN.value: [
            HealingStrategy.RETRY.value,
            HealingStrategy.ESCALATE.value
        ]
    }
    
    def __init__(self, rollback_manager=None, storage_sync=None, 
                 max_attempts: int = 3, retry_delay_ms: int = 1000):
        self.rollback = rollback_manager
        self.storage = storage_sync
        self.max_attempts = max_attempts
        self.retry_delay_ms = retry_delay_ms
        
        # Custom strategies (can override defaults)
        self.strategies = dict(self.DEFAULT_STRATEGIES)
        
        # Healing history for learning
        self.healing_history: List[HealingAttempt] = []
        
        # Strategy handlers
        self._handlers: Dict[str, Callable] = {
            HealingStrategy.RETRY.value: self._handle_retry,
            HealingStrategy.ROLLBACK.value: self._handle_rollback,
            HealingStrategy.FALLBACK.value: self._handle_fallback,
            HealingStrategy.RESTART.value: self._handle_restart,
            HealingStrategy.SKIP.value: self._handle_skip,
            HealingStrategy.ESCALATE.value: self._handle_escalate
        }
        
        # Escalation callbacks
        self._escalation_callbacks: List[Callable] = []
        
        logger.info(f"SelfHealer initialized with max_attempts={max_attempts}")
    
    def heal(self, error_type: str, context: Dict[str, Any], 
             retry_func: Optional[Callable] = None) -> HealingResult:
        """
        Attempt to heal from an error using configured strategies.
        
        Args:
            error_type: Type of error (from ErrorType enum)
            context: Error context with details
            retry_func: Optional function to retry the failed operation
            
        Returns:
            HealingResult with outcome details
        """
        strategies = self.strategies.get(error_type, self.strategies[ErrorType.UNKNOWN.value])
        
        attempts = 0
        last_error = None
        strategy_used = None
        
        for strategy in strategies:
            if attempts >= self.max_attempts:
                break
            
            attempts += 1
            strategy_used = strategy
            start_time = datetime.now()
            
            try:
                handler = self._handlers.get(strategy)
                if not handler:
                    continue
                
                success = handler(error_type, context, retry_func)
                
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Record attempt
                attempt = HealingAttempt(
                    id=f"heal_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    error_type=error_type,
                    strategy=strategy,
                    success=success,
                    duration_ms=duration_ms,
                    details=context
                )
                self.healing_history.append(attempt)
                
                if success:
                    logger.info(f"Healed {error_type} using {strategy} (attempt {attempts})")
                    return HealingResult(
                        success=True,
                        error_type=error_type,
                        strategy_used=strategy,
                        attempts=attempts,
                        details={"context": context}
                    )
                    
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Healing strategy {strategy} failed: {e}")
        
        # All strategies failed - escalate
        logger.warning(f"All healing strategies failed for {error_type}, escalating")
        self._escalate(error_type, context, last_error)
        
        return HealingResult(
            success=False,
            error_type=error_type,
            strategy_used=strategy_used or "none",
            attempts=attempts,
            escalated=True,
            error=last_error,
            details={"context": context}
        )
    
    def _handle_retry(self, error_type: str, context: Dict[str, Any],
                     retry_func: Optional[Callable]) -> bool:
        """Retry the failed operation"""
        if not retry_func:
            return False
        
        import time
        time.sleep(self.retry_delay_ms / 1000)
        
        try:
            result = retry_func()
            return bool(result)
        except Exception as e:
            logger.debug(f"Retry failed: {e}")
            return False
    
    def _handle_rollback(self, error_type: str, context: Dict[str, Any],
                        retry_func: Optional[Callable]) -> bool:
        """Rollback to previous state"""
        if not self.rollback:
            return False
        
        snapshot_id = context.get("rollback_snapshot_id")
        if snapshot_id:
            dna = self.rollback.rollback_by_id(snapshot_id)
            return dna is not None
        
        # Try latest snapshot
        latest = self.rollback.get_latest_snapshot()
        if latest:
            dna = self.rollback.rollback_by_id(latest.id)
            return dna is not None
        
        return False
    
    def _handle_fallback(self, error_type: str, context: Dict[str, Any],
                        retry_func: Optional[Callable]) -> bool:
        """Use fallback mechanism"""
        fallback_func = context.get("fallback_func")
        if fallback_func and callable(fallback_func):
            try:
                result = fallback_func()
                return bool(result)
            except Exception as e:
                logger.debug(f"Fallback failed: {e}")
                return False
        
        # For storage failures, try local storage as fallback
        if error_type == ErrorType.STORAGE_FAILURE.value and self.storage:
            data = context.get("data")
            path = context.get("path")
            if data and path:
                result = self.storage.local.save(path, data)
                return result.success
        
        return False
    
    def _handle_restart(self, error_type: str, context: Dict[str, Any],
                       retry_func: Optional[Callable]) -> bool:
        """Restart component or subsystem"""
        restart_func = context.get("restart_func")
        if restart_func and callable(restart_func):
            try:
                restart_func()
                return True
            except Exception as e:
                logger.debug(f"Restart failed: {e}")
                return False
        
        return False
    
    def _handle_skip(self, error_type: str, context: Dict[str, Any],
                    retry_func: Optional[Callable]) -> bool:
        """Skip the failed operation and continue"""
        # Log that we're skipping
        logger.info(f"Skipping failed operation: {error_type}")
        return True  # Skip is always "successful" in that we continue
    
    def _handle_escalate(self, error_type: str, context: Dict[str, Any],
                        retry_func: Optional[Callable]) -> bool:
        """Escalate to human intervention"""
        self._escalate(error_type, context, "Manual escalation requested")
        return False  # Escalation means we couldn't auto-heal
    
    def _escalate(self, error_type: str, context: Dict[str, Any], 
                  error: Optional[str]) -> None:
        """Notify humans of unrecoverable error"""
        escalation_data = {
            "error_type": error_type,
            "context": context,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "healing_attempts": len([h for h in self.healing_history[-10:] 
                                    if h.error_type == error_type])
        }
        
        for callback in self._escalation_callbacks:
            try:
                callback(escalation_data)
            except Exception as e:
                logger.error(f"Escalation callback failed: {e}")
        
        logger.warning(f"ESCALATION: {error_type} requires human intervention")
    
    def on_escalation(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register callback for escalation events"""
        self._escalation_callbacks.append(callback)
    
    def set_strategies(self, error_type: str, strategies: List[str]) -> None:
        """Set custom strategies for an error type"""
        self.strategies[error_type] = strategies
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get healing statistics"""
        if not self.healing_history:
            return {
                "total_attempts": 0,
                "success_rate": 0.0,
                "by_error_type": {},
                "by_strategy": {}
            }
        
        total = len(self.healing_history)
        successful = sum(1 for h in self.healing_history if h.success)
        
        # By error type
        by_error = {}
        for attempt in self.healing_history:
            if attempt.error_type not in by_error:
                by_error[attempt.error_type] = {"total": 0, "success": 0}
            by_error[attempt.error_type]["total"] += 1
            if attempt.success:
                by_error[attempt.error_type]["success"] += 1
        
        # By strategy
        by_strategy = {}
        for attempt in self.healing_history:
            if attempt.strategy not in by_strategy:
                by_strategy[attempt.strategy] = {"total": 0, "success": 0}
            by_strategy[attempt.strategy]["total"] += 1
            if attempt.success:
                by_strategy[attempt.strategy]["success"] += 1
        
        return {
            "total_attempts": total,
            "success_rate": successful / total if total > 0 else 0.0,
            "by_error_type": by_error,
            "by_strategy": by_strategy,
            "avg_duration_ms": sum(h.duration_ms for h in self.healing_history) / total if total > 0 else 0
        }
    
    def clear_history(self) -> None:
        """Clear healing history"""
        self.healing_history.clear()
