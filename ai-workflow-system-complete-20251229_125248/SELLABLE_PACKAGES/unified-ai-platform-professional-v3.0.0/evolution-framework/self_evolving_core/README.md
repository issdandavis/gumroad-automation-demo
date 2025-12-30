# Self-Evolving AI Framework v2.0.0

A robust, versatile AI automation framework designed for autonomous operation, self-improvement, and multi-platform integration.

## Features

- **Autonomous Operation**: Risk-based approval system with configurable safety boundaries
- **Self-Evolution**: AI feedback analysis and automatic mutation application
- **Multi-Provider AI**: OpenAI, Anthropic, Google support with automatic fallback
- **Distributed Storage**: Local, Dropbox, GitHub sync with retry logic
- **Self-Healing**: Automatic error recovery with escalation
- **Plugin Architecture**: Extensible plugin system for custom functionality
- **Comprehensive Logging**: Audit trails and evolution history

## Quick Start

```python
from self_evolving_core import EvolvingAIFramework

# Initialize and start
framework = EvolvingAIFramework()
framework.initialize()
framework.start()

# Check status
status = framework.get_status()
print(f"Generation: {status['dna']['generation']}")
print(f"Fitness: {status['dna']['fitness_score']}")
```

## CLI Usage

```bash
# Show status
python evolving_ai_main.py status

# Run demo
python evolving_ai_main.py demo

# Propose mutation
python evolving_ai_main.py mutate -t communication_enhancement -d "Add new channel"

# Show fitness
python evolving_ai_main.py fitness
```

## Architecture

- `models.py` - Core data structures (SystemDNA, Mutation, FitnessScore)
- `config.py` - Configuration management with YAML/JSON/env support
- `autonomy.py` - Risk-based autonomous operation controller
- `mutation.py` - Mutation engine with validation
- `storage.py` - Multi-platform storage synchronization
- `fitness.py` - Performance monitoring and optimization
- `rollback.py` - Snapshot and rollback management
- `healing.py` - Self-healing with recovery strategies
- `providers.py` - Multi-provider AI integration
- `plugins.py` - Extensible plugin system
- `events.py` - Pub/sub event system
- `framework.py` - Main orchestrator

## License

Commercial - AI Agent Workflow Team
