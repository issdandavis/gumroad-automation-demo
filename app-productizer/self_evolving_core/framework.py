"""
Main Framework for Self-Evolving AI System
==========================================

Central orchestrator that integrates all components into a
cohesive, self-evolving AI system.

Usage:
    from self_evolving_core import EvolvingAIFramework
    
    framework = EvolvingAIFramework()
    framework.initialize()
    framework.start()
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path

from .models import SystemDNA, Mutation, FitnessScore, OperationResult
from .config import ConfigManager, FrameworkConfig
from .autonomy import AutonomyController, Workflow
from .mutation import MutationEngine
from .storage import StorageSync
from .fitness import FitnessMonitor
from .rollback import RollbackManager
from .healing import SelfHealer, ErrorType
from .logging_system import AuditLogger, EvolutionLog
from .feedback import FeedbackAnalyzer
from .plugins import PluginManager
from .providers import AIProviderHub
from .events import EventBus, EventType

logger = logging.getLogger(__name__)


class DNAManager:
    """Manages SystemDNA persistence"""
    
    def __init__(self, storage_path: str = "AI_NETWORK_LOCAL"):
        self.storage_path = Path(storage_path)
        self.dna_file = self.storage_path / "system_dna.json"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._dna: Optional[SystemDNA] = None
    
    def load(self) -> SystemDNA:
        """Load DNA from storage or create new"""
        if self._dna:
            return self._dna
        
        if self.dna_file.exists():
            try:
                with open(self.dna_file, 'r') as f:
                    data = json.load(f)
                    self._dna = SystemDNA.from_dict(data)
                    return self._dna
            except Exception as e:
                logger.warning(f"Failed to load DNA: {e}")
        
        self._dna = SystemDNA()
        self.save(self._dna)
        return self._dna
    
    def save(self, dna: SystemDNA) -> bool:
        """Save DNA to storage"""
        try:
            with open(self.dna_file, 'w') as f:
                json.dump(dna.to_dict(), f, indent=2, default=str)
            self._dna = dna
            return True
        except Exception as e:
            logger.error(f"Failed to save DNA: {e}")
            return False
    
    def get_current(self) -> Optional[SystemDNA]:
        """Get current DNA without loading"""
        return self._dna


class EvolvingAIFramework:
    """
    Main framework orchestrating all self-evolving AI components.
    
    Features:
    - Unified initialization and lifecycle management
    - Component wiring and event routing
    - High-level API for common operations
    - Status monitoring and health checks
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        
        # Core components (initialized in initialize())
        self.dna_manager: Optional[DNAManager] = None
        self.event_bus: Optional[EventBus] = None
        self.autonomy: Optional[AutonomyController] = None
        self.mutation_engine: Optional[MutationEngine] = None
        self.storage: Optional[StorageSync] = None
        self.fitness: Optional[FitnessMonitor] = None
        self.rollback: Optional[RollbackManager] = None
        self.healer: Optional[SelfHealer] = None
        self.audit: Optional[AuditLogger] = None
        self.evolution_log: Optional[EvolutionLog] = None
        self.feedback: Optional[FeedbackAnalyzer] = None
        self.plugins: Optional[PluginManager] = None
        self.providers: Optional[AIProviderHub] = None
        
        self._initialized = False
        self._running = False
        
        logger.info(f"EvolvingAIFramework v{self.VERSION} created")

    def initialize(self) -> bool:
        """
        Initialize all framework components.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            logger.info("Initializing framework components...")
            
            # Event bus first (other components may use it)
            self.event_bus = EventBus()
            
            # DNA management
            self.dna_manager = DNAManager(self.config.storage.local_path)
            
            # Rollback manager
            self.rollback = RollbackManager(
                f"{self.config.storage.local_path}/snapshots"
            )
            
            # Autonomy controller
            self.autonomy = AutonomyController(self.config.autonomy)
            
            # Mutation engine
            self.mutation_engine = MutationEngine(
                dna_manager=self.dna_manager,
                autonomy_controller=self.autonomy,
                rollback_manager=self.rollback
            )
            
            # Storage sync
            self.storage = StorageSync(self.config.storage)
            
            # Fitness monitor
            self.fitness = FitnessMonitor(self.config.fitness)
            
            # Self healer
            self.healer = SelfHealer(
                rollback_manager=self.rollback,
                storage_sync=self.storage,
                max_attempts=self.config.autonomy.healing_attempts
            )
            
            # Logging
            self.audit = AuditLogger(self.config.logging.audit_log_path)
            self.evolution_log = EvolutionLog()
            
            # Feedback analyzer
            self.feedback = FeedbackAnalyzer()
            
            # Plugin manager
            self.plugins = PluginManager(
                self.config.plugins.plugins_directory,
                framework=self
            )
            
            # AI providers
            self.providers = AIProviderHub(self.config.ai_providers)
            
            # Wire up event handlers
            self._setup_event_handlers()
            
            # Load plugins
            if self.config.plugins.auto_load:
                self.plugins.load_all()
                self.plugins.initialize_all()
            
            self._initialized = True
            self.event_bus.publish(EventType.SYSTEM_STARTED.value, {
                "version": self.VERSION,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info("Framework initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Framework initialization failed: {e}")
            return False
    
    def _setup_event_handlers(self) -> None:
        """Wire up internal event handlers"""
        # Log all events to audit
        def audit_handler(event):
            self.audit.log(
                category="event",
                action=event.type,
                details=event.data
            )
        self.event_bus.subscribe("*", audit_handler)
        
        # Handle healing escalations
        def escalation_handler(data):
            self.event_bus.publish(EventType.HEALING_ESCALATED.value, data)
        self.healer.on_escalation(escalation_handler)

    def start(self) -> None:
        """Start the framework (begin autonomous operation)"""
        if not self._initialized:
            self.initialize()
        
        self._running = True
        logger.info("Framework started")
    
    def stop(self) -> None:
        """Stop the framework"""
        self._running = False
        
        if self.plugins:
            self.plugins.cleanup_all()
        
        if self.event_bus:
            self.event_bus.publish(EventType.SYSTEM_STOPPED.value, {
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info("Framework stopped")
    
    # High-level API methods
    
    def get_dna(self) -> SystemDNA:
        """Get current system DNA (defensive copy to avoid shared-reference surprises)"""
        dna = self.dna_manager.load()
        # Deep-ish copy through serialization to prevent in-place mutation side effects
        return SystemDNA.from_dict(dna.to_dict())
    
    def propose_mutation(self, mutation: Mutation) -> Dict[str, Any]:
        """
        Propose a mutation for the system.
        
        Returns dict with approval status and mutation result if applied.
        """
        dna = self.get_dna()
        
        # Assess risk
        risk = self.autonomy.assess_risk(mutation)
        mutation.risk_score = risk
        
        # Check auto-approval
        if self.autonomy.should_auto_approve(mutation):
            mutation.auto_approved = True
            result = self.mutation_engine.apply_mutation(mutation)
            
            if result.success:
                self.event_bus.emit_mutation_applied(
                    result.mutation_id, mutation.type, mutation.fitness_impact
                )
                self.evolution_log.record(
                    generation=result.new_generation,
                    mutation_type=mutation.type,
                    fitness_before=dna.fitness_score,
                    fitness_after=dna.fitness_score + mutation.fitness_impact,
                    source_ai=mutation.source_ai or "unknown",
                    auto_approved=True
                )
            
            return {"approved": True, "auto": True, "result": result}
        else:
            # Queue for human approval
            request = self.autonomy.request_approval(
                mutation, "mutation", f"Risk score {risk:.2f} exceeds threshold"
            )
            self.event_bus.publish(EventType.APPROVAL_REQUESTED.value, {
                "request_id": request.id,
                "mutation_type": mutation.type,
                "risk_score": risk
            })
            return {"approved": False, "request_id": request.id, "risk": risk}
    
    def analyze_feedback(self, text: str, source_ai: str = "unknown") -> List[Mutation]:
        """Analyze AI feedback and generate mutation proposals"""
        insights = self.feedback.analyze(text, source_ai)
        return self.feedback.generate_mutations(insights, source_ai)
    
    def sync_storage(self, data: Dict[str, Any], path: str) -> Dict[str, Any]:
        """Sync data to all configured storage platforms"""
        results = self.storage.sync_all(data, path)
        
        for platform, result in results.items():
            self.audit.log_storage(
                operation="sync",
                platform=platform,
                path=path,
                success=result.success,
                error=result.error
            )
        
        return {p: r.to_dict() for p, r in results.items()}
    
    def get_fitness(self) -> FitnessScore:
        """Calculate and return current fitness"""
        score = self.fitness.calculate_fitness()
        self.event_bus.emit_fitness_calculated(score.overall, score.trend)
        return score

    def heal(self, error_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to heal from an error"""
        result = self.healer.heal(error_type, context)
        
        self.audit.log_healing(
            error_type=error_type,
            strategy=result.strategy_used,
            success=result.success,
            attempts=result.attempts
        )
        
        self.event_bus.emit_healing_completed(
            error_type, result.strategy_used, result.success
        )
        
        return result.__dict__
    
    def rollback_to(self, snapshot_id: str) -> Dict[str, Any]:
        """Rollback system to a previous snapshot"""
        result = self.rollback.rollback(self.dna_manager, snapshot_id)
        return result.__dict__
    
    def ai_complete(self, prompt: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI completion using configured providers"""
        return self.providers.complete(prompt, provider)
    
    def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute an autonomous workflow"""
        def step_executor(step: Dict[str, Any]) -> OperationResult:
            # Execute step based on type
            step_type = step.get("type", "unknown")
            start = datetime.now()
            
            try:
                if step_type == "mutation":
                    mutation = Mutation(**step.get("mutation", {}))
                    result = self.mutation_engine.apply_mutation(mutation)
                    return OperationResult(
                        success=result.success,
                        operation_type="mutation",
                        data={"mutation_id": result.mutation_id}
                    )
                elif step_type == "sync":
                    results = self.sync_storage(step.get("data", {}), step.get("path", ""))
                    success = all(r.get("success") for r in results.values())
                    return OperationResult(success=success, operation_type="sync")
                elif step_type == "ai_call":
                    result = self.ai_complete(step.get("prompt", ""))
                    return OperationResult(
                        success=result.get("success", False),
                        operation_type="ai_call",
                        data=result
                    )
                else:
                    return OperationResult(
                        success=False,
                        operation_type=step_type,
                        error=f"Unknown step type: {step_type}"
                    )
            except Exception as e:
                return OperationResult(
                    success=False,
                    operation_type=step_type,
                    error=str(e)
                )
        
        self.event_bus.publish(EventType.WORKFLOW_STARTED.value, {
            "workflow_id": workflow.id,
            "workflow_name": workflow.name
        })
        
        result = self.autonomy.execute_workflow(workflow, step_executor)
        
        self.event_bus.publish(EventType.WORKFLOW_COMPLETED.value, {
            "workflow_id": workflow.id,
            "success": result.success,
            "steps_completed": result.steps_completed
        })
        
        return result.to_dict()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        dna = self.get_dna()
        fitness = self.get_fitness()
        
        return {
            "version": self.VERSION,
            "initialized": self._initialized,
            "running": self._running,
            "dna": {
                "generation": dna.generation,
                "fitness_score": dna.fitness_score,
                "mutations_count": len(dna.mutations)
            },
            "fitness": fitness.to_dict(),
            "autonomy": self.autonomy.get_session_stats(),
            "storage": self.storage.get_sync_status(),
            "providers": self.providers.get_stats(),
            "healing": self.healer.get_healing_stats(),
            "plugins": [p.to_dict() for p in self.plugins.list_plugins()]
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display"""
        return {
            "status": self.get_status(),
            "fitness_dashboard": self.fitness.get_dashboard_data(),
            "recent_events": [e.to_dict() for e in self.event_bus.get_recent(20)],
            "pending_approvals": [
                {"id": r.id, "type": r.item_type, "risk": r.risk_score}
                for r in self.autonomy.get_pending_approvals()
            ],
            "evolution_stats": self.evolution_log.get_mutation_stats()
        }
