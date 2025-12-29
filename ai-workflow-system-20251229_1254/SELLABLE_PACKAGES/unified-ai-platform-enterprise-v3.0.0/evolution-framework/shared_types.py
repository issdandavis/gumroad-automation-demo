"""
Generated Python types for Unified AI Platform Bridge API
Auto-generated from TypeScript definitions - do not edit manually
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal, TypeVar
from enum import Enum
from pydantic import BaseModel, Field

T = TypeVar('T')

class EventType(str, Enum):
    MUTATION_APPLIED = "mutation_applied"
    MUTATION_PROPOSED = "mutation_proposed"
    FITNESS_CALCULATED = "fitness_calculated"
    SYSTEM_EVOLVED = "system_evolved"
    HEALING_COMPLETED = "healing_completed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    AGENT_CONFIGURED = "agent_configured"
    AGENT_PERFORMANCE_UPDATED = "agent_performance_updated"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    SYSTEM_HEALING = "system_healing"
    OPTIMIZATION_SUGGESTED = "optimization_suggested"
    CONFIGURATION_SYNCED = "configuration_synced"
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    HEALTH_CHECK = "health_check"


class CrossSystemEvent(BaseModel):
    id: str
    type: EventType
    source: Literal['evolution', 'workflow']
    target: Literal['evolution', 'workflow', 'both']
    payload: Any
    timestamp: datetime
    correlationId: Optional[str] = None
    priority: Optional[Literal['low', 'medium', 'high', 'critical']] = None


class UnifiedSystemStatus(BaseModel):
    bridge: Dict[str, Any]
    evolution: Dict[str, Any]
    workflow: Dict[str, Any]
    integration: Dict[str, Any]


class EvolutionConfig(BaseModel):
    apiUrl: str
    apiKey: Optional[str] = None
    healthCheckInterval: int
    mutationThreshold: float
    fitnessTargets: Dict[str, float]


class WorkflowConfig(BaseModel):
    apiUrl: str
    apiKey: Optional[str] = None
    healthCheckInterval: int
    maxConcurrentWorkflows: int
    agentDefaults: Dict[str, Any]


class BridgeConfig(BaseModel):
    port: int
    cors: Dict[str, Any]
    rateLimit: Dict[str, Any]
    websocket: Dict[str, Any]


class SharedConfig(BaseModel):
    database: Dict[str, Any]
    redis: Dict[str, Any]
    security: Dict[str, Any]
    monitoring: Dict[str, Any]


class UnifiedConfig(BaseModel):
    evolution: EvolutionConfig
    workflow: WorkflowConfig
    bridge: BridgeConfig
    shared: SharedConfig


class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime
    requestId: str


class PaginatedResponse(BaseModel):
    success: bool
    data: Optional[List[Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime
    requestId: str
    pagination: Dict[str, Any]


class HealthCheck(BaseModel):
    service: str
    status: Literal['healthy', 'degraded', 'unhealthy']
    timestamp: datetime
    responseTime: float
    details: Optional[Dict[str, Any]] = None


class SystemMetrics(BaseModel):
    cpu: float
    memory: float
    disk: float
    network: Dict[str, float]
    requests: Dict[str, Any]


class WebSocketMessage(BaseModel):
    type: Literal['event', 'status', 'metrics', 'error']
    payload: Any
    timestamp: datetime
    id: str


class BridgeAPIError(Exception):
    """Base exception class for Bridge API errors"""
    def __init__(self, message: str, code: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class IntegrationError(BridgeAPIError):
    """Integration error between systems"""
    def __init__(self, message: str, system: Literal['evolution', 'workflow'], details: Any = None):
        super().__init__(message, 'INTEGRATION_ERROR', 502, details)
        self.system = system


class ConfigurationError(BridgeAPIError):
    """Configuration validation error"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, 'CONFIGURATION_ERROR', 400, details)
