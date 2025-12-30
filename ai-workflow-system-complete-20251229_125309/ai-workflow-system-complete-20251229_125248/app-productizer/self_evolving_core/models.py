"""
Data Models for Self-Evolving AI Framework
==========================================

Core dataclasses and type definitions for the entire framework.
Designed for type safety, serialization, and cross-component compatibility.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
import hashlib


class MutationType(Enum):
    """Types of mutations the system can apply"""
    COMMUNICATION_ENHANCEMENT = "communication_enhancement"
    LANGUAGE_EXPANSION = "language_expansion"
    STORAGE_OPTIMIZATION = "storage_optimization"
    INTELLIGENCE_UPGRADE = "intelligence_upgrade"
    PROTOCOL_IMPROVEMENT = "protocol_improvement"
    AUTONOMY_ADJUSTMENT = "autonomy_adjustment"
    PROVIDER_ADDITION = "provider_addition"
    PLUGIN_INTEGRATION = "plugin_integration"


class Priority(Enum):
    """Priority levels for operations and messages"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class OperationStatus(Enum):
    """Status of operations"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    QUEUED = "queued"


class StoragePlatform(Enum):
    """Supported storage platforms"""
    LOCAL = "local"
    DROPBOX = "dropbox"
    GITHUB = "github"
    NOTION = "notion"
    S3 = "s3"
    GOOGLE_DRIVE = "google_drive"


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"
    XAI = "xai"
    LOCAL = "local"


@dataclass
class CoreTraits:
    """Core genetic traits of the AI system"""
    communication_channels: int = 8
    language_support: int = 12
    ai_participants: List[str] = field(default_factory=list)
    evolutionary_features: List[str] = field(default_factory=lambda: [
        "self_modification",
        "learning_from_responses",
        "adaptive_communication",
        "distributed_storage",
        "version_control",
        "autonomous_workflow",
        "multi_provider_ai",
        "plugin_architecture"
    ])
    autonomy_level: float = 0.7
    enabled_providers: List[str] = field(default_factory=lambda: ["openai", "anthropic"])
    enabled_storage: List[str] = field(default_factory=lambda: ["local", "github"])
    max_concurrent_operations: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreTraits":
        return cls(**data)


@dataclass
class BedrockDecisionRecord:
    """Record of a Bedrock LLM decision"""
    decision_id: str
    timestamp: str
    model_used: str
    decision: str  # APPROVE, REJECT, DEFER
    confidence: float
    reasoning: str
    cost_usd: float
    tokens_used: int
    processing_time_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CloudStorageMetadata:
    """Cloud storage metadata for evolution data"""
    s3_location: Optional[str] = None
    dynamodb_item_id: Optional[str] = None
    cloudwatch_metric_name: Optional[str] = None
    cross_region_replicated: bool = False
    storage_class: str = "STANDARD"
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MutationRecord:
    """Record of an applied mutation"""
    id: str
    timestamp: str
    type: str
    description: str
    fitness_impact: float
    risk_score: float
    generation: int
    source_ai: Optional[str] = None
    auto_approved: bool = False
    rollback_snapshot: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Cloud-specific fields
    bedrock_decision: Optional[BedrockDecisionRecord] = None
    cloud_storage: Optional[CloudStorageMetadata] = None
    llm_reasoning: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SystemDNA:
    """Core genetic configuration for the AI system"""
    version: str = "3.0.0"  # Updated for Bedrock integration
    birth_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    generation: int = 1
    fitness_score: float = 100.0
    core_traits: CoreTraits = field(default_factory=CoreTraits)
    mutations: List[MutationRecord] = field(default_factory=list)
    snapshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Cloud-specific fields
    bedrock_decisions: List[BedrockDecisionRecord] = field(default_factory=list)
    cloud_storage_locations: Dict[str, CloudStorageMetadata] = field(default_factory=dict)
    aws_region: Optional[str] = None
    cost_tracking: Dict[str, float] = field(default_factory=dict)
    model_usage_history: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemDNA":
        if "core_traits" in data and isinstance(data["core_traits"], dict):
            data["core_traits"] = CoreTraits.from_dict(data["core_traits"])
        if "mutations" in data:
            data["mutations"] = [
                MutationRecord(**m) if isinstance(m, dict) else m 
                for m in data["mutations"]
            ]
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "SystemDNA":
        return cls.from_dict(json.loads(json_str))
    
    def get_checksum(self) -> str:
        """Generate checksum for integrity verification"""
        content = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Mutation:
    """Proposed mutation before application"""
    type: str
    description: str
    fitness_impact: float = 0.0
    risk_score: float = 0.0
    source_ai: Optional[str] = None
    auto_approved: bool = False
    rollback_data: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FitnessScore:
    """Comprehensive fitness metrics"""
    overall: float
    success_rate: float
    healing_speed: float  # seconds
    cost_efficiency: float  # operations per dollar
    uptime: float  # percentage (0-1)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    trend: str = "stable"  # improving, stable, degrading
    components: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OperationResult:
    """Result of any system operation"""
    success: bool
    operation_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SyncResult:
    """Result of storage sync operation"""
    success: bool
    platform: str
    operation: str  # upload, download, delete
    path: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    checksum: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    success: bool
    workflow_id: str
    steps_completed: int
    total_steps: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0
    mutations_applied: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    checkpoint_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass 
class Snapshot:
    """System state snapshot for rollback"""
    id: str
    timestamp: str
    label: str
    dna_checksum: str
    dna_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        return cls(**data)


@dataclass
class DegradationAlert:
    """Alert for performance degradation"""
    metric: str
    current_value: float
    threshold: float
    degradation_percent: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    suggested_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AIMessage:
    """Standard AI message format"""
    id: str
    timestamp: str
    from_ai: str
    to_ai: str
    message: str
    message_type: str = "general"
    priority: str = "normal"
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Event:
    """Event for pub/sub system"""
    type: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "system"
    id: str = field(default_factory=lambda: f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
