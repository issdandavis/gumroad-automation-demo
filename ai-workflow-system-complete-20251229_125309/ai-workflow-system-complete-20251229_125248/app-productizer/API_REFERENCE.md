# 📚 API Reference
## Self-Evolving AI Framework v3.0.0

Complete API documentation for integrating and extending the Self-Evolving AI Framework.

---

## 🚀 Quick Start

```python
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation, SystemDNA

# Initialize framework
framework = EvolvingAIFramework()
success = framework.initialize()

if success:
    print("Framework initialized successfully!")
    
    # Get system status
    status = framework.get_status()
    print(f"Generation: {status['generation']}")
    print(f"Fitness: {status['fitness_score']}")
```

---

## 🏗 Core Framework API

### EvolvingAIFramework

Main framework class for all operations.

#### Constructor
```python
framework = EvolvingAIFramework(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (optional): Path to custom configuration file

#### Methods

##### `initialize() -> bool`
Initialize the framework and all components.

**Returns:** `bool` - Success status

**Example:**
```python
framework = EvolvingAIFramework()
if framework.initialize():
    print("Ready to evolve!")
```

##### `get_status() -> Dict[str, Any]`
Get current system status and health metrics.

**Returns:** Dictionary with system information

**Response Format:**
```python
{
    "generation": 1,
    "fitness_score": 100.0,
    "version": "3.0.0",
    "birth_timestamp": "2024-12-29T10:00:00Z",
    "mutations_count": 0,
    "snapshots_count": 5,
    "health": "healthy",
    "components": {
        "mutation_engine": "active",
        "fitness_monitor": "active",
        "storage_sync": "active",
        "rollback_manager": "active"
    }
}
```

##### `get_dna() -> SystemDNA`
Get current system DNA configuration.

**Returns:** `SystemDNA` object

**Example:**
```python
dna = framework.get_dna()
print(f"Generation: {dna.generation}")
print(f"Fitness: {dna.fitness_score}")
print(f"Traits: {dna.core_traits.evolutionary_features}")
```

##### `propose_mutation(mutation: Mutation) -> Dict[str, Any]`
Propose a system mutation for evaluation and potential application.

**Parameters:**
- `mutation`: Mutation object with type, description, and impact

**Returns:** Dictionary with proposal result

**Example:**
```python
mutation = Mutation(
    type="intelligence_upgrade",
    description="Improve response accuracy by 15%",
    fitness_impact=5.0,
    source_ai="user_request"
)

result = framework.propose_mutation(mutation)
if result["approved"]:
    print(f"Mutation applied! New generation: {result['new_generation']}")
else:
    print(f"Mutation rejected: {result['reason']}")
```

**Response Format:**
```python
{
    "approved": True,
    "auto": True,
    "mutation_id": "mut_20241229_123456",
    "new_generation": 2,
    "fitness_change": 5.0,
    "risk_score": 0.2,
    "reason": "Low risk, high impact mutation approved"
}
```

##### `get_fitness() -> FitnessScore`
Get current fitness metrics and trends.

**Returns:** `FitnessScore` object

**Example:**
```python
fitness = framework.get_fitness()
print(f"Overall: {fitness.overall}")
print(f"Success Rate: {fitness.success_rate}")
print(f"Cost Efficiency: {fitness.cost_efficiency}")
print(f"Trend: {fitness.trend}")
```

##### `sync_storage(data: Dict, filename: str) -> Dict[str, Any]`
Synchronize data across all configured storage platforms.

**Parameters:**
- `data`: Dictionary to synchronize
- `filename`: Target filename for storage

**Returns:** Sync results for each platform

**Example:**
```python
data = {"message": "Hello AI Network", "timestamp": "2024-12-29T10:00:00Z"}
result = framework.sync_storage(data, "ai_message.json")

for platform, status in result.items():
    print(f"{platform}: {'✅' if status['success'] else '❌'}")
```

##### `rollback_to(snapshot_id: str) -> Dict[str, Any]`
Rollback system to a previous snapshot.

**Parameters:**
- `snapshot_id`: ID of snapshot to restore

**Returns:** Rollback operation result

**Example:**
```python
# List available snapshots
snapshots = framework.rollback.list_snapshots(5)
latest = snapshots[0]

# Rollback to latest snapshot
result = framework.rollback_to(latest.id)
if result["success"]:
    print(f"Rolled back to generation {result['restored_generation']}")
```

---

## 🧬 Data Models

### SystemDNA

Core genetic configuration of the AI system.

```python
@dataclass
class SystemDNA:
    version: str = "3.0.0"
    birth_timestamp: str
    generation: int = 1
    fitness_score: float = 100.0
    core_traits: CoreTraits
    mutations: List[MutationRecord] = field(default_factory=list)
    snapshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Methods:**
- `to_dict() -> Dict[str, Any]`: Convert to dictionary
- `to_json() -> str`: Convert to JSON string
- `from_dict(data: Dict) -> SystemDNA`: Create from dictionary
- `get_checksum() -> str`: Generate integrity checksum

### Mutation

Proposed system modification.

```python
@dataclass
class Mutation:
    type: str  # MutationType enum value
    description: str
    fitness_impact: float = 0.0
    risk_score: float = 0.0
    source_ai: Optional[str] = None
    auto_approved: bool = False
    rollback_data: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**Mutation Types:**
- `communication_enhancement`: Improve AI communication
- `language_expansion`: Add language support
- `storage_optimization`: Optimize storage operations
- `intelligence_upgrade`: Enhance AI capabilities
- `protocol_improvement`: Improve system protocols
- `autonomy_adjustment`: Adjust autonomy settings
- `provider_addition`: Add new AI providers
- `plugin_integration`: Integrate new plugins

### FitnessScore

Comprehensive system performance metrics.

```python
@dataclass
class FitnessScore:
    overall: float
    success_rate: float
    healing_speed: float  # seconds
    cost_efficiency: float  # operations per dollar
    uptime: float  # percentage (0-1)
    timestamp: str
    trend: str = "stable"  # improving, stable, degrading
    components: Dict[str, float] = field(default_factory=dict)
```

### CoreTraits

System capabilities and characteristics.

```python
@dataclass
class CoreTraits:
    communication_channels: int = 8
    language_support: int = 12
    ai_participants: List[str] = field(default_factory=list)
    evolutionary_features: List[str] = field(default_factory=lambda: [
        "self_modification", "learning_from_responses",
        "adaptive_communication", "distributed_storage",
        "version_control", "autonomous_workflow"
    ])
    autonomy_level: float = 0.7
    enabled_providers: List[str] = field(default_factory=lambda: ["openai", "anthropic"])
    enabled_storage: List[str] = field(default_factory=lambda: ["local", "github"])
    max_concurrent_operations: int = 10
```

---

## 🔄 Component APIs

### MutationEngine

Handles system evolution and mutations.

```python
from self_evolving_core.mutation import MutationEngine

engine = framework.mutation_engine

# Analyze AI feedback for mutation opportunities
mutations = engine.analyze_feedback(ai_feedback)

# Validate mutation before application
validation = engine.validate_mutation(mutation)
if validation.is_valid:
    result = engine.apply_mutation(mutation)
```

### FitnessMonitor

Tracks system performance and health.

```python
from self_evolving_core.fitness import FitnessMonitor

monitor = framework.fitness_monitor

# Record operation result
monitor.record_operation(operation, result)

# Calculate current fitness
fitness = monitor.calculate_fitness()

# Detect performance degradation
alert = monitor.detect_degradation()
if alert:
    print(f"Degradation detected: {alert.metric}")
```

### StorageSync

Multi-platform data synchronization.

```python
from self_evolving_core.storage import StorageSync

storage = framework.storage_sync

# Sync to all platforms
result = storage.sync_all(data, "filename.json")

# Process failed operations queue
results = storage.process_queue()

# Verify data integrity
is_valid = storage.verify_integrity(data, checksum)
```

### RollbackManager

Safe system state management.

```python
from self_evolving_core.rollback import RollbackManager

rollback = framework.rollback

# Create snapshot before risky operation
snapshot = rollback.create_snapshot(dna, "pre-upgrade")

# List available snapshots
snapshots = rollback.list_snapshots(10)

# Rollback to specific snapshot
result = rollback.rollback(snapshot)
```

---

## 🌐 REST API Endpoints

The framework includes an optional REST API server for remote management.

### Start API Server
```python
from self_evolving_core.api import APIServer

server = APIServer(framework)
server.start(host="0.0.0.0", port=8080)
```

### Endpoints

#### `GET /api/v1/status`
Get system status and health.

**Response:**
```json
{
  "generation": 1,
  "fitness_score": 100.0,
  "health": "healthy",
  "version": "3.0.0"
}
```

#### `GET /api/v1/fitness`
Get fitness metrics.

**Response:**
```json
{
  "overall": 100.0,
  "success_rate": 0.95,
  "cost_efficiency": 150.0,
  "trend": "improving"
}
```

#### `POST /api/v1/mutations`
Propose a system mutation.

**Request:**
```json
{
  "type": "intelligence_upgrade",
  "description": "Improve response accuracy",
  "fitness_impact": 5.0,
  "source_ai": "api_client"
}
```

**Response:**
```json
{
  "approved": true,
  "mutation_id": "mut_20241229_123456",
  "new_generation": 2,
  "fitness_change": 5.0
}
```

#### `POST /api/v1/rollback`
Rollback to previous snapshot.

**Request:**
```json
{
  "snapshot_id": "snap_20241229_123456"
}
```

**Response:**
```json
{
  "success": true,
  "restored_generation": 1,
  "message": "System rolled back successfully"
}
```

#### `POST /api/v1/sync`
Synchronize data to storage platforms.

**Request:**
```json
{
  "data": {"key": "value"},
  "filename": "sync_data.json"
}
```

**Response:**
```json
{
  "local": {"success": true},
  "github": {"success": true},
  "dropbox": {"success": false, "error": "Token expired"}
}
```

---

## 🔧 Configuration API

### Environment Variables
```python
import os

# AI Provider Configuration
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["ANTHROPIC_API_KEY"] = "your-key"

# Storage Configuration  
os.environ["GITHUB_TOKEN"] = "your-token"
os.environ["DROPBOX_ACCESS_TOKEN"] = "your-token"

# System Configuration
os.environ["AUTONOMY_RISK_THRESHOLD"] = "0.3"
os.environ["MAX_AUTONOMOUS_MUTATIONS"] = "10"
```

### Configuration File
```python
# config.yaml
autonomy:
  risk_threshold: 0.3
  max_mutations: 10
  checkpoint_interval: 300

storage:
  platforms: ["local", "github", "dropbox"]
  retry_attempts: 3
  backup_retention: 50

fitness:
  metrics: ["success_rate", "healing_speed", "cost_efficiency", "uptime"]
  degradation_threshold: 0.05
  optimization_trigger: 0.20
```

---

## 🧪 Testing API

### Property-Based Testing
```python
from hypothesis import given, strategies as st
from self_evolving_core.models import SystemDNA, Mutation

@given(st.builds(SystemDNA))
def test_dna_serialization(dna):
    """Test DNA serialization round-trip"""
    json_data = dna.to_json()
    restored = SystemDNA.from_json(json_data)
    assert restored.generation == dna.generation
    assert restored.fitness_score == dna.fitness_score
```

### Integration Testing
```python
import pytest
from self_evolving_core import EvolvingAIFramework

def test_mutation_workflow():
    """Test complete mutation workflow"""
    framework = EvolvingAIFramework()
    framework.initialize()
    
    # Create mutation
    mutation = Mutation(
        type="protocol_improvement",
        description="Test mutation",
        fitness_impact=1.0
    )
    
    # Propose and verify
    result = framework.propose_mutation(mutation)
    assert result["approved"] is not None
```

---

## 🚨 Error Handling

### Exception Types
```python
from self_evolving_core.exceptions import (
    FrameworkError,
    MutationError,
    StorageError,
    RollbackError,
    ValidationError
)

try:
    framework.propose_mutation(invalid_mutation)
except MutationError as e:
    print(f"Mutation failed: {e.message}")
    print(f"Error code: {e.code}")
except ValidationError as e:
    print(f"Validation failed: {e.details}")
```

### Error Codes
- `MUTATION_001`: Invalid mutation type
- `MUTATION_002`: Risk threshold exceeded
- `STORAGE_001`: Platform connection failed
- `STORAGE_002`: Sync operation timeout
- `ROLLBACK_001`: Snapshot not found
- `ROLLBACK_002`: Rollback verification failed

---

## 📊 Monitoring & Metrics

### Custom Metrics
```python
# Add custom fitness component
framework.fitness_monitor.add_component("custom_metric", 0.85)

# Record custom operation
operation = {
    "type": "custom_operation",
    "duration": 150,
    "success": True
}
framework.fitness_monitor.record_operation(operation, result)
```

### Health Checks
```python
# Comprehensive health check
health = framework.get_health_status()
print(f"Overall Health: {health['status']}")
for component, status in health['components'].items():
    print(f"  {component}: {status}")
```

---

## 🔌 Plugin System

### Creating Plugins
```python
from self_evolving_core.plugins import BasePlugin

class CustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__("custom_plugin", "1.0.0")
    
    def initialize(self, framework):
        """Initialize plugin with framework access"""
        self.framework = framework
        return True
    
    def on_mutation(self, mutation):
        """Called before mutation application"""
        print(f"Processing mutation: {mutation.type}")
    
    def on_fitness_change(self, old_score, new_score):
        """Called when fitness score changes"""
        print(f"Fitness changed: {old_score} -> {new_score}")

# Register plugin
framework.plugins.register(CustomPlugin())
```

---

## 📞 Support & Resources

### Getting Help
- **Documentation**: Complete guides and examples
- **Community**: Discord server with 1000+ developers
- **Support**: Email and phone support by tier
- **Training**: Video courses and certification

### Useful Links
- **GitHub**: [Source code and issues](https://github.com/your-org/evolving-ai-framework)
- **Discord**: [Community support](https://discord.gg/evolving-ai)
- **Documentation**: [Full docs site](https://docs.evolving-ai.com)
- **Training**: [Video courses](https://evolving-ai.com/training)

---

**© 2024 Evolving AI Systems. All rights reserved.**

*Build AI that evolves itself. Start with our comprehensive API today.*