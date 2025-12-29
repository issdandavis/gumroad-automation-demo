"""
REST API for Self-Evolving AI Framework
=======================================

FastAPI-based REST API for remote access to the framework.

Usage:
    uvicorn self_evolving_core.api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Pydantic models for API
class MutationRequest(BaseModel):
    type: str = Field(..., description="Mutation type")
    description: str = Field(..., description="Mutation description")
    fitness_impact: float = Field(default=2.0, description="Expected fitness impact")
    source_ai: str = Field(default="API", description="Source AI identifier")

class FeedbackRequest(BaseModel):
    text: str = Field(..., description="AI feedback text to analyze")
    source_ai: str = Field(default="API", description="Source AI identifier")

class SyncRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data to sync")
    path: str = Field(..., description="Storage path")

class WorkflowStep(BaseModel):
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)

class WorkflowRequest(BaseModel):
    name: str
    steps: List[WorkflowStep]
    risk_level: str = Field(default="low")

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    uptime_seconds: float

class StatusResponse(BaseModel):
    version: str
    initialized: bool
    running: bool
    dna: Dict[str, Any]
    fitness: Dict[str, Any]
    autonomy: Dict[str, Any]
    storage: Dict[str, Any]

# Create FastAPI app
app = FastAPI(
    title="Self-Evolving AI Framework API",
    description="REST API for autonomous AI system management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Framework instance (lazy loaded)
_framework = None
_start_time = datetime.now()

def get_framework():
    """Get or create framework instance"""
    global _framework
    if _framework is None:
        from .framework import EvolvingAIFramework
        _framework = EvolvingAIFramework()
        _framework.initialize()
        _framework.start()
    return _framework


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now().isoformat(),
        uptime_seconds=(datetime.now() - _start_time).total_seconds()
    )


@app.get("/status", tags=["System"])
async def get_status():
    """Get comprehensive system status"""
    framework = get_framework()
    return framework.get_status()


@app.get("/dashboard", tags=["System"])
async def get_dashboard():
    """Get dashboard data"""
    framework = get_framework()
    return framework.get_dashboard_data()


@app.get("/dna", tags=["DNA"])
async def get_dna():
    """Get current system DNA"""
    framework = get_framework()
    dna = framework.get_dna()
    return dna.to_dict()


@app.get("/fitness", tags=["Fitness"])
async def get_fitness():
    """Get current fitness metrics"""
    framework = get_framework()
    fitness = framework.get_fitness()
    return fitness.to_dict()


@app.get("/fitness/dashboard", tags=["Fitness"])
async def get_fitness_dashboard():
    """Get fitness dashboard data"""
    framework = get_framework()
    return framework.fitness.get_dashboard_data()


@app.post("/mutations", tags=["Mutations"])
async def propose_mutation(request: MutationRequest):
    """Propose a new mutation"""
    from .models import Mutation
    
    framework = get_framework()
    mutation = Mutation(
        type=request.type,
        description=request.description,
        fitness_impact=request.fitness_impact,
        source_ai=request.source_ai
    )
    
    result = framework.propose_mutation(mutation)
    return result


@app.post("/feedback/analyze", tags=["Feedback"])
async def analyze_feedback(request: FeedbackRequest):
    """Analyze AI feedback and generate mutation proposals"""
    framework = get_framework()
    mutations = framework.analyze_feedback(request.text, request.source_ai)
    return {
        "mutations": [m.to_dict() for m in mutations],
        "count": len(mutations)
    }


@app.post("/sync", tags=["Storage"])
async def sync_storage(request: SyncRequest):
    """Sync data to all storage platforms"""
    framework = get_framework()
    results = framework.sync_storage(request.data, request.path)
    return results


@app.get("/sync/status", tags=["Storage"])
async def get_sync_status():
    """Get storage sync status"""
    framework = get_framework()
    return framework.storage.get_sync_status()


@app.get("/snapshots", tags=["Rollback"])
async def list_snapshots(limit: int = 20):
    """List available snapshots"""
    framework = get_framework()
    snapshots = framework.rollback.list_snapshots(limit)
    return [s.to_dict() for s in snapshots]


@app.post("/rollback/{snapshot_id}", tags=["Rollback"])
async def rollback_to_snapshot(snapshot_id: str):
    """Rollback to a specific snapshot"""
    framework = get_framework()
    result = framework.rollback_to(snapshot_id)
    return result


@app.post("/heal", tags=["Healing"])
async def trigger_healing(error_type: str, context: Dict[str, Any] = None):
    """Trigger self-healing for an error"""
    framework = get_framework()
    result = framework.heal(error_type, context or {})
    return result


@app.get("/healing/stats", tags=["Healing"])
async def get_healing_stats():
    """Get healing statistics"""
    framework = get_framework()
    return framework.healer.get_healing_stats()


@app.get("/plugins", tags=["Plugins"])
async def list_plugins():
    """List all plugins"""
    framework = get_framework()
    return [p.to_dict() for p in framework.plugins.list_plugins()]


@app.post("/plugins/{plugin_name}/enable", tags=["Plugins"])
async def enable_plugin(plugin_name: str):
    """Enable a plugin"""
    framework = get_framework()
    success = framework.plugins.enable_plugin(plugin_name)
    return {"success": success, "plugin": plugin_name}


@app.post("/plugins/{plugin_name}/disable", tags=["Plugins"])
async def disable_plugin(plugin_name: str):
    """Disable a plugin"""
    framework = get_framework()
    success = framework.plugins.disable_plugin(plugin_name)
    return {"success": success, "plugin": plugin_name}


@app.get("/providers", tags=["AI Providers"])
async def list_providers():
    """List AI providers and their stats"""
    framework = get_framework()
    return framework.providers.get_stats()


@app.post("/ai/complete", tags=["AI Providers"])
async def ai_complete(prompt: str, provider: Optional[str] = None):
    """Generate AI completion"""
    framework = get_framework()
    result = framework.ai_complete(prompt, provider)
    return result


@app.get("/events/recent", tags=["Events"])
async def get_recent_events(limit: int = 50):
    """Get recent events"""
    framework = get_framework()
    events = framework.event_bus.get_recent(limit)
    return [e.to_dict() for e in events]


@app.get("/approvals/pending", tags=["Approvals"])
async def get_pending_approvals():
    """Get pending approval requests"""
    framework = get_framework()
    requests = framework.autonomy.get_pending_approvals()
    return [{"id": r.id, "type": r.item_type, "risk": r.risk_score} for r in requests]


@app.post("/approvals/{request_id}/approve", tags=["Approvals"])
async def approve_request(request_id: str):
    """Approve a pending request"""
    framework = get_framework()
    success = framework.autonomy.approve(request_id)
    return {"success": success, "request_id": request_id}


@app.post("/approvals/{request_id}/reject", tags=["Approvals"])
async def reject_request(request_id: str, reason: str = ""):
    """Reject a pending request"""
    framework = get_framework()
    success = framework.autonomy.reject(request_id, reason)
    return {"success": success, "request_id": request_id}


@app.get("/evolution/log", tags=["Evolution"])
async def get_evolution_log(limit: int = 100):
    """Get evolution history"""
    framework = get_framework()
    return framework.evolution_log.get_history(limit)


@app.get("/evolution/stats", tags=["Evolution"])
async def get_evolution_stats():
    """Get evolution statistics"""
    framework = get_framework()
    return framework.evolution_log.get_mutation_stats()


# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize framework on startup"""
    logger.info("Starting Self-Evolving AI API...")
    get_framework()
    logger.info("API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global _framework
    if _framework:
        _framework.stop()
        _framework = None
    logger.info("API shutdown complete")
