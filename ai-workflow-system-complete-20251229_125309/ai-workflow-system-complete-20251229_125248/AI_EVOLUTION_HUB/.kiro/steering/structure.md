---
inclusion: always
---

# Project Structure: AI Evolution Hub

## Directory Organization

```
src/
├── core/                   # Core evolution framework
│   ├── models.py          # Data models and schemas
│   ├── mutation.py        # Mutation engine and validation
│   ├── fitness.py         # Performance monitoring
│   ├── rollback.py        # Snapshot and rollback management
│   └── autonomy.py        # Risk assessment and approval
├── services/              # Business logic services
│   ├── storage.py         # Multi-platform sync
│   ├── healing.py         # Self-healing strategies
│   ├── feedback.py        # AI response analysis
│   └── communication.py   # AI-to-AI protocols
├── api/                   # REST API endpoints
│   ├── evolution.py       # Evolution management
│   ├── fitness.py         # Metrics and monitoring
│   └── admin.py           # Human oversight interface
├── utils/                 # Helper functions
│   ├── logging.py         # Structured logging
│   ├── crypto.py          # Encryption utilities
│   └── validators.py      # Input validation
├── types/                 # TypeScript-style type hints
│   ├── evolution.py       # Evolution-related types
│   └── communication.py   # Communication types
└── config/                # Configuration management
    ├── settings.py        # Application settings
    └── aws.py             # AWS service configuration
```

## Naming Conventions

- **Classes**: PascalCase (`MutationEngine`, `FitnessMonitor`)
- **Functions**: snake_case (`assess_risk`, `apply_mutation`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_MUTATIONS_PER_SESSION`)
- **Files**: snake_case (`mutation_engine.py`, `fitness_monitor.py`)
- **Tests**: `test_` prefix (`test_mutation_engine.py`)

## Import Patterns

- Absolute imports: `from src.core.models import SystemDNA`
- Group: standard library, third-party, local imports
- Type imports: `from typing import TYPE_CHECKING`
- Prefer explicit imports over wildcard imports

## Infrastructure Location

- `infrastructure/` - AWS CDK stacks and constructs
- `infrastructure/lib/` - CDK stack definitions
- `infrastructure/bin/` - CDK app entry points