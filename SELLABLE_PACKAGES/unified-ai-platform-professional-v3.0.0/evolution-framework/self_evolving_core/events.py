"""
Event System for Self-Evolving AI Framework
==========================================

Pub/sub event system for decoupled communication with:
- Event registration and dispatch
- Async event handling
- Event history and replay
- Typed event definitions
"""

import logging
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Standard event types"""
    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPED = "system.stopped"
    SYSTEM_ERROR = "system.error"
    
    # Mutation events
    MUTATION_PROPOSED = "mutation.proposed"
    MUTATION_APPROVED = "mutation.approved"
    MUTATION_REJECTED = "mutation.rejected"
    MUTATION_APPLIED = "mutation.applied"
    MUTATION_FAILED = "mutation.failed"
    
    # Storage events
    STORAGE_SYNC_STARTED = "storage.sync.started"
    STORAGE_SYNC_COMPLETED = "storage.sync.completed"
    STORAGE_SYNC_FAILED = "storage.sync.failed"
    
    # Fitness events
    FITNESS_CALCULATED = "fitness.calculated"
    FITNESS_DEGRADED = "fitness.degraded"
    FITNESS_IMPROVED = "fitness.improved"
    
    # Healing events
    HEALING_STARTED = "healing.started"
    HEALING_COMPLETED = "healing.completed"
    HEALING_ESCALATED = "healing.escalated"
    
    # Autonomy events
    APPROVAL_REQUESTED = "autonomy.approval.requested"
    APPROVAL_GRANTED = "autonomy.approval.granted"
    WORKFLOW_STARTED = "autonomy.workflow.started"
    WORKFLOW_COMPLETED = "autonomy.workflow.completed"
    CHECKPOINT_CREATED = "autonomy.checkpoint.created"


@dataclass
class Event:
    """Event data structure"""
    type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "system"
    id: str = field(default_factory=lambda: f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source
        }


class EventBus:
    """
    Central event bus for pub/sub communication.
    
    Features:
    - Subscribe to specific event types
    - Wildcard subscriptions
    - Event history for replay
    - Async-compatible handlers
    """
    
    def __init__(self, max_history: int = 1000):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.history: List[Event] = []
        self.max_history = max_history
        self._paused = False
        
        logger.info("EventBus initialized")
    
    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Event type to subscribe to (or "*" for all)
            handler: Callback function receiving Event
        """
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """Unsubscribe handler from event type"""
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            return True
        return False
    
    def publish(self, event_type: str, data: Dict[str, Any], source: str = "system") -> Event:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event payload
            source: Event source identifier
            
        Returns:
            Published Event object
        """
        event = Event(type=event_type, data=data, source=source)
        
        # Store in history
        self.history.append(event)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        if self._paused:
            return event
        
        # Notify subscribers
        self._dispatch(event)
        
        return event

    def _dispatch(self, event: Event) -> None:
        """Dispatch event to subscribers"""
        handlers = []
        
        # Specific type subscribers
        if event.type in self.subscribers:
            handlers.extend(self.subscribers[event.type])
        
        # Wildcard subscribers
        if "*" in self.subscribers:
            handlers.extend(self.subscribers["*"])
        
        # Category subscribers (e.g., "mutation.*")
        parts = event.type.split(".")
        if len(parts) > 1:
            category = f"{parts[0]}.*"
            if category in self.subscribers:
                handlers.extend(self.subscribers[category])
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error for {event.type}: {e}")
    
    def emit(self, event_type: str, **kwargs) -> Event:
        """Convenience method to emit event with kwargs as data"""
        return self.publish(event_type, kwargs)
    
    def pause(self) -> None:
        """Pause event dispatch (events still recorded)"""
        self._paused = True
    
    def resume(self) -> None:
        """Resume event dispatch"""
        self._paused = False
    
    def replay(self, event_type: Optional[str] = None, since: Optional[str] = None) -> List[Event]:
        """
        Replay events from history.
        
        Args:
            event_type: Filter by event type (optional)
            since: Filter events after this timestamp (optional)
            
        Returns:
            List of matching events
        """
        events = self.history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events
    
    def get_recent(self, limit: int = 50, event_type: Optional[str] = None) -> List[Event]:
        """Get recent events"""
        events = self.history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history"""
        self.history.clear()
    
    # Convenience methods for common events
    def emit_mutation_applied(self, mutation_id: str, mutation_type: str, 
                             fitness_impact: float, source: str = "system") -> Event:
        return self.publish(EventType.MUTATION_APPLIED.value, {
            "mutation_id": mutation_id,
            "mutation_type": mutation_type,
            "fitness_impact": fitness_impact
        }, source)
    
    def emit_fitness_calculated(self, score: float, trend: str, source: str = "system") -> Event:
        return self.publish(EventType.FITNESS_CALCULATED.value, {
            "score": score,
            "trend": trend
        }, source)
    
    def emit_healing_completed(self, error_type: str, strategy: str, 
                              success: bool, source: str = "system") -> Event:
        return self.publish(EventType.HEALING_COMPLETED.value, {
            "error_type": error_type,
            "strategy": strategy,
            "success": success
        }, source)
