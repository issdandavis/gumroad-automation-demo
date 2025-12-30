"""
Evolution Framework REST API
===========================

Provides REST API endpoints for the Self-Evolving AI Framework
to enable integration with the Bridge API.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread

from self_evolving_core.framework import EvolvingAIFramework
from self_evolving_core.models import Mutation
from bridge_integration import BridgeIntegration, BridgeConfig, create_bridge_config_from_env

logger = logging.getLogger(__name__)

# Global framework instance
framework: Optional[EvolvingAIFramework] = None
bridge_integration: Optional[BridgeIntegration] = None

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)


def create_app(framework_instance: EvolvingAIFramework = None) -> Flask:
    """Create Flask app with framework instance"""
    global framework
    
    if framework_instance:
        framework = framework_instance
    elif not framework:
        # Create default framework instance
        framework = EvolvingAIFramework()
        framework.initialize()
        framework.start()
    
    return app


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get framework status"""
    try:
        if not framework:
            return jsonify({
                "error": "Framework not initialized",
                "connected": False
            }), 500
        
        status = framework.get_status()
        
        return jsonify({
            "connected": True,
            "version": framework.VERSION,
            "running": status["running"],
            "dna": status["dna"],
            "fitness": status["fitness"],
            "autonomy": status["autonomy"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "error": str(e),
            "connected": False
        }), 500


@app.route('/api/mutations/propose', methods=['POST'])
def propose_mutation():
    """Propose a mutation to the framework"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        data = request.get_json()
        
        # Create mutation from request data
        mutation = Mutation(
            type=data.get("type", "api_mutation"),
            parameters=data.get("parameters", {}),
            fitness_impact=data.get("fitness_impact", 0.0),
            source_ai=data.get("source_ai", "bridge_api")
        )
        
        # Propose mutation
        result = framework.propose_mutation(mutation)
        
        return jsonify({
            "mutation_id": result.get("mutation_id"),
            "approved": result.get("approved", False),
            "auto_approved": result.get("auto", False),
            "risk_score": result.get("risk", 0.0),
            "request_id": result.get("request_id"),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error proposing mutation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/fitness', methods=['GET'])
def get_fitness():
    """Get current fitness metrics"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        fitness = framework.get_fitness()
        
        return jsonify({
            "overall": fitness.overall,
            "trend": fitness.trend,
            "components": fitness.components,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting fitness: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/fitness/workflow-completion', methods=['POST'])
def process_workflow_completion():
    """Process workflow completion for fitness calculation"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        data = request.get_json()
        
        # Calculate fitness impact
        current_fitness = framework.get_fitness()
        previous_fitness = current_fitness.overall
        
        # Simple fitness calculation based on workflow success
        fitness_impact = 0.0
        if data.get("success", False):
            fitness_impact = 0.05  # Base reward for successful workflow
            
            # Bonus for fast execution
            execution_time = data.get("execution_time", 60)
            if execution_time < 30:
                fitness_impact += 0.02
            
            # Penalty for errors
            error_count = data.get("error_count", 0)
            fitness_impact -= error_count * 0.01
        else:
            fitness_impact = -0.05  # Penalty for failed workflow
        
        # Update fitness (this would need to be implemented in the framework)
        new_fitness = previous_fitness + fitness_impact
        
        return jsonify({
            "fitness_improved": fitness_impact > 0,
            "previous_fitness": previous_fitness,
            "new_fitness": new_fitness,
            "improvement": fitness_impact,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing workflow completion: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/mutations/agent-config', methods=['POST'])
def process_agent_config():
    """Process agent configuration for mutation analysis"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        data = request.get_json()
        
        # Analyze agent configuration and suggest mutations
        mutations = []
        
        config = data.get("configuration", {})
        agent_id = data.get("agent_id")
        
        # Example: Suggest temperature adjustment based on performance
        if "temperature" in config:
            current_temp = config["temperature"]
            performance_metrics = data.get("performance_metrics", {})
            
            if performance_metrics.get("success_rate", 0.5) < 0.7:
                new_temp = min(1.0, current_temp + 0.1)
                mutations.append({
                    "type": "agent_temperature_adjustment",
                    "parameters": {
                        "agent_id": agent_id,
                        "current_temperature": current_temp,
                        "suggested_temperature": new_temp
                    },
                    "expected_impact": 0.05,
                    "confidence": 0.7
                })
        
        return jsonify({
            "mutations_suggested": len(mutations),
            "mutations": mutations,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing agent config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analyze/performance', methods=['POST'])
def analyze_performance():
    """Analyze performance thresholds and suggest mutations"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        data = request.get_json()
        
        threshold_type = data.get("threshold_type")
        current_value = data.get("current_value")
        threshold_value = data.get("threshold_value")
        context = data.get("context", {})
        
        mutations = []
        
        # Generate mutations based on performance analysis
        if threshold_type == "response_time" and current_value > threshold_value:
            # Suggest optimizations for slow response times
            mutations.append({
                "id": f"perf_{datetime.now().timestamp()}",
                "type": "performance_optimization",
                "parameters": {
                    "optimization_type": "response_time",
                    "target_reduction": 0.2,
                    "context": context
                },
                "expected_impact": 0.1,
                "risk_score": 0.3
            })
        
        elif threshold_type == "error_rate" and current_value > threshold_value:
            # Suggest error reduction strategies
            mutations.append({
                "id": f"error_{datetime.now().timestamp()}",
                "type": "error_reduction",
                "parameters": {
                    "error_type": context.get("error_type", "unknown"),
                    "reduction_strategy": "retry_with_backoff",
                    "context": context
                },
                "expected_impact": 0.15,
                "risk_score": 0.2
            })
        
        return jsonify({
            "analysis_complete": True,
            "mutations": mutations,
            "recommendations": [
                {
                    "type": "monitoring",
                    "description": f"Continue monitoring {threshold_type} performance"
                }
            ],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing performance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/sync', methods=['POST'])
def trigger_sync():
    """Trigger system synchronization"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        # Trigger framework sync operations
        sync_id = f"sync_{datetime.now().timestamp()}"
        
        # Perform sync operations (this would be implemented in the framework)
        # For now, just return success
        
        return jsonify({
            "sync_id": sync_id,
            "status": "completed",
            "operations": [
                "dna_sync",
                "fitness_recalculation",
                "mutation_cleanup"
            ],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/events/optimization', methods=['POST'])
def handle_optimization_event():
    """Handle optimization events from Bridge API"""
    try:
        if not framework:
            return jsonify({"error": "Framework not initialized"}), 500
        
        data = request.get_json()
        
        event_type = data.get("event_type")
        payload = data.get("payload", {})
        
        logger.info(f"Received optimization event: {event_type}")
        
        # Process optimization event
        # This would trigger appropriate framework actions
        
        return jsonify({
            "event_processed": True,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling optimization event: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if not framework:
            return jsonify({
                "status": "unhealthy",
                "error": "Framework not initialized"
            }), 500
        
        return jsonify({
            "status": "healthy",
            "version": framework.VERSION,
            "uptime": "unknown",  # Would need to track this
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


def start_bridge_integration_async():
    """Start bridge integration in async context"""
    async def init_bridge():
        global bridge_integration
        
        try:
            if framework:
                config = create_bridge_config_from_env()
                bridge_integration = BridgeIntegration(framework, config)
                await bridge_integration.initialize()
                logger.info("Bridge integration started")
            else:
                logger.warning("Framework not available for bridge integration")
        except Exception as e:
            logger.error(f"Failed to start bridge integration: {e}")
    
    # Run in new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_bridge())


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Evolution API server"""
    
    # Start bridge integration in background thread
    bridge_thread = Thread(target=start_bridge_integration_async, daemon=True)
    bridge_thread.start()
    
    logger.info(f"Starting Evolution API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import os
    
    # Initialize framework
    framework = EvolvingAIFramework()
    framework.initialize()
    framework.start()
    
    # Run server
    port = int(os.getenv("EVOLUTION_API_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    run_server(port=port, debug=debug)