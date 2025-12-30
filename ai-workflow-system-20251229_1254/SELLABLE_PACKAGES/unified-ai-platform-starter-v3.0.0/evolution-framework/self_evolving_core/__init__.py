"""
Self-Evolving AI Framework - 10x Enhanced Edition
=================================================

A robust, versatile AI automation framework designed for:
- Standalone product sales (Gumroad)
- Integration into other apps (AI Workflow Architect, Chat Archive, etc.)
- Enterprise-grade reliability and observability

Core Components:
- AutonomyController: Risk-based autonomous operation
- MutationEngine: Self-improvement through AI feedback
- StorageSync: Multi-platform distributed storage
- FitnessMonitor: Performance tracking and optimization
- PluginManager: Extensible plugin architecture
- AIProviderHub: Multi-provider AI integration
- EventBus: Event-driven architecture
- ConfigManager: Flexible configuration management

Usage:
    from self_evolving_core import EvolvingAIFramework
    
    framework = EvolvingAIFramework()
    framework.initialize()
    framework.start()

Author: AI Agent Workflow Team
Version: 2.0.0 (10x Enhanced)
License: Commercial
"""

__version__ = "2.0.0"
__author__ = "AI Agent Workflow Team"

from .models import (
    SystemDNA,
    CoreTraits,
    Mutation,
    MutationRecord,
    FitnessScore,
    WorkflowResult,
    SyncResult,
    OperationResult
)

from .autonomy import AutonomyController, AutonomyConfig
from .mutation import MutationEngine, MutationValidator
from .storage import StorageSync, SyncQueue, LocalStorage, DropboxClient, GitHubClient
from .fitness import FitnessMonitor, DegradationAlert
from .rollback import RollbackManager, Snapshot
from .healing import SelfHealer
from .logging_system import AuditLogger, EvolutionLog
from .feedback import FeedbackAnalyzer
from .config import ConfigManager, ConfigValidator
from .plugins import PluginManager, BasePlugin
from .providers import AIProviderHub, ProviderAdapter
from .events import EventBus, Event

# Main framework class
from .framework import EvolvingAIFramework

__all__ = [
    # Version info
    "__version__",
    "__author__",
    
    # Data models
    "SystemDNA",
    "CoreTraits", 
    "Mutation",
    "MutationRecord",
    "FitnessScore",
    "WorkflowResult",
    "SyncResult",
    "OperationResult",
    
    # Core components
    "AutonomyController",
    "AutonomyConfig",
    "MutationEngine",
    "MutationValidator",
    "StorageSync",
    "SyncQueue",
    "LocalStorage",
    "DropboxClient",
    "GitHubClient",
    "FitnessMonitor",
    "DegradationAlert",
    "RollbackManager",
    "Snapshot",
    "SelfHealer",
    "AuditLogger",
    "EvolutionLog",
    "FeedbackAnalyzer",
    "ConfigManager",
    "ConfigValidator",
    "PluginManager",
    "BasePlugin",
    "AIProviderHub",
    "ProviderAdapter",
    "EventBus",
    "Event",
    
    # Main framework
    "EvolvingAIFramework"
]
