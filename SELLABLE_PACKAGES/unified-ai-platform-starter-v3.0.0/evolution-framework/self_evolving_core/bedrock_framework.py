"""
Bedrock-Enhanced AI Framework
============================

Extended version of EvolvingAIFramework with AWS Bedrock integration
for cloud-native, LLM-powered autonomous evolution.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .framework import EvolvingAIFramework, DNAManager
from .aws_config import AWSConfigManager, AWSConfig
from .bedrock_client import BedrockClient
from .model_router import ModelRouter
from .evolution_advisor import EvolutionAdvisor
from .bedrock_decision_engine import BedrockDecisionEngine, DecisionConfig
from .enhanced_autonomy import EnhancedAutonomyController
from .cloud_dna_store import CloudDNAStore, EvolutionEvent
from .models import SystemDNA, Mutation, FitnessScore, OperationResult

logger = logging.getLogger(__name__)


class BedrockFramework(EvolvingAIFramework):
    """
    Enhanced AI Framework with AWS Bedrock integration.
    
    Extends the base framework with:
    - LLM-powered evolution guidance
    - Cloud-native storage and analytics
    - Autonomous decision making with reasoning
    - Cost optimization and monitoring
    - Enterprise security and compliance
    """
    
    VERSION = "3.0.0-bedrock"
    
    def __init__(self, config_path: Optional[str] = None, 
                 aws_config_path: Optional[str] = None):
        super().__init__(config_path)
        
        # AWS and Bedrock components
        self.aws_config_manager: Optional[AWSConfigManager] = None
        self.bedrock_client: Optional[BedrockClient] = None
        self.model_router: Optional[ModelRouter] = None
        self.evolution_advisor: Optional[EvolutionAdvisor] = None
        self.decision_engine: Optional[BedrockDecisionEngine] = None
        self.enhanced_autonomy: Optional[EnhancedAutonomyController] = None
        self.cloud_dna_store: Optional[CloudDNAStore] = None
        
        # Configuration
        self.aws_config_path = aws_config_path
        self.bedrock_enabled = False
        
        logger.info(f"BedrockFramework v{self.VERSION} created")
    
    def initialize(self) -> bool:
        """Initialize framework with Bedrock components"""
        
        # Initialize base framework first
        if not super().initialize():
            return False
        
        try:
            # Initialize AWS components
            self._initialize_aws_components()
            
            # Replace autonomy controller with enhanced version
            if self.bedrock_enabled and self.decision_engine:
                self.enhanced_autonomy = EnhancedAutonomyController(
                    config=self.config.autonomy,
                    decision_engine=self.decision_engine
                )
                # Keep reference to original for compatibility
                self.autonomy = self.enhanced_autonomy
            
            # Wire up Bedrock event handlers
            self._setup_bedrock_event_handlers()
            
            logger.info("Bedrock framework initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Bedrock framework initialization failed: {e}")
            # Continue with base framework if Bedrock fails
            logger.warning("Continuing with base framework functionality")
            return True
    
    def _initialize_aws_components(self) -> None:
        """Initialize AWS Bedrock components"""
        
        try:
            # Initialize AWS configuration
            self.aws_config_manager = AWSConfigManager(self.aws_config_path)
            
            # Test AWS connectivity
            connectivity = self.aws_config_manager.test_connectivity()
            
            if not all(connectivity.values()):
                logger.warning(f"AWS connectivity issues: {connectivity}")
                logger.warning("Some Bedrock features may be unavailable")
            
            # Initialize Bedrock client
            self.bedrock_client = BedrockClient(self.aws_config_manager)
            
            # Test Bedrock connection
            bedrock_test = self.bedrock_client.test_connection()
            if not bedrock_test.success:
                logger.error(f"Bedrock connection failed: {bedrock_test.error}")
                return
            
            # Initialize model router
            daily_budget = self.aws_config_manager.config.bedrock.daily_budget_usd
            monthly_budget = self.aws_config_manager.config.bedrock.monthly_budget_usd
            self.model_router = ModelRouter(daily_budget, monthly_budget)
            
            # Initialize evolution advisor
            self.evolution_advisor = EvolutionAdvisor(self.bedrock_client)
            
            # Initialize decision engine
            decision_config = DecisionConfig(
                risk_tolerance=self.config.autonomy.risk_threshold,
                performance_requirements={
                    "min_fitness_score": 80.0,
                    "max_error_rate": 0.05,
                    "min_uptime": 0.99
                }
            )
            self.decision_engine = BedrockDecisionEngine(
                self.bedrock_client, self.model_router, decision_config
            )
            
            # Initialize cloud DNA store
            self.cloud_dna_store = CloudDNAStore(self.aws_config_manager)
            
            self.bedrock_enabled = True
            logger.info("AWS Bedrock components initialized successfully")
            
        except Exception as e:
            logger.error(f"AWS component initialization failed: {e}")
            self.bedrock_enabled = False
    
    def _setup_bedrock_event_handlers(self) -> None:
        """Set up event handlers for Bedrock integration"""
        
        if not self.bedrock_enabled:
            return
        
        # Handle evolution events for cloud storage
        def cloud_storage_handler(event):
            if event.type in ["mutation_applied", "fitness_calculated", "rollback"]:
                try:
                    evolution_event = EvolutionEvent(
                        id=f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        timestamp=datetime.now(),
                        type=event.type,
                        generation=event.data.get("generation", 1),
                        fitness_delta=event.data.get("fitness_delta", 0.0),
                        mutation_id=event.data.get("mutation_id"),
                        data=event.data,
                        importance=0.8 if event.type == "mutation_applied" else 0.5
                    )
                    
                    # Store asynchronously (would use asyncio in production)
                    # For now, just log the event
                    logger.info(f"Evolution event for cloud storage: {evolution_event.id}")
                    
                except Exception as e:
                    logger.error(f"Cloud storage event handler failed: {e}")
        
        self.event_bus.subscribe("*", cloud_storage_handler)
    
    # Enhanced API methods with Bedrock integration
    
    async def propose_mutation_enhanced(self, mutation: Mutation) -> Dict[str, Any]:
        """Enhanced mutation proposal with LLM guidance"""
        
        if not self.bedrock_enabled or not self.enhanced_autonomy:
            # Fall back to base implementation
            return self.propose_mutation(mutation)
        
        try:
            # Create system context
            dna = self.get_dna()
            fitness_history = [self.get_fitness()]  # Would get real history
            system_context = self.enhanced_autonomy.create_system_context(dna, fitness_history)
            
            # Get enhanced decision
            enhanced_decision = await self.enhanced_autonomy.should_auto_approve_enhanced(
                mutation, system_context
            )
            
            result = {
                "enhanced": True,
                "original_decision": enhanced_decision.original_decision,
                "final_decision": enhanced_decision.final_decision,
                "confidence": enhanced_decision.confidence,
                "reasoning": enhanced_decision.reasoning,
                "escalation_required": enhanced_decision.escalation_required
            }
            
            # Apply mutation if approved
            if enhanced_decision.final_decision == "auto_approve":
                mutation_result = self.mutation_engine.apply_mutation(mutation)
                result["mutation_applied"] = mutation_result.success
                result["mutation_id"] = mutation_result.mutation_id if mutation_result.success else None
                
                # Record decision outcome for learning
                if enhanced_decision.llm_decision:
                    self.enhanced_autonomy.record_decision_outcome(
                        enhanced_decision.llm_decision.decision_id,
                        {"success": mutation_result.success, "fitness_impact": mutation.fitness_impact}
                    )
            
            elif enhanced_decision.final_decision == "require_approval":
                approval_request = self.enhanced_autonomy.request_approval(
                    mutation, "enhanced_mutation", enhanced_decision.reasoning
                )
                result["approval_request_id"] = approval_request.id
            
            return result
            
        except Exception as e:
            logger.error(f"Enhanced mutation proposal failed: {e}")
            # Fall back to base implementation
            return self.propose_mutation(mutation)
    
    async def get_evolution_guidance(self, dna: Optional[SystemDNA] = None) -> Dict[str, Any]:
        """Get LLM-powered evolution guidance"""
        
        if not self.bedrock_enabled or not self.evolution_advisor:
            return {"error": "Bedrock not available", "guidance": "Use base framework features"}
        
        try:
            if not dna:
                dna = self.get_dna()
            
            # Get fitness history (simplified for demo)
            fitness_history = [self.get_fitness()]
            
            # Get system analysis
            analysis = await self.evolution_advisor.analyze_system_state(dna, fitness_history)
            
            # Generate mutation strategy
            strategy = await self.evolution_advisor.generate_mutation_strategy(analysis, dna)
            
            return {
                "analysis": analysis.to_dict(),
                "strategy": strategy.to_dict(),
                "advisor_stats": self.evolution_advisor.get_advisor_stats()
            }
            
        except Exception as e:
            logger.error(f"Evolution guidance failed: {e}")
            return {"error": str(e), "guidance": "Evolution guidance temporarily unavailable"}
    
    def get_bedrock_status(self) -> Dict[str, Any]:
        """Get comprehensive Bedrock integration status"""
        
        status = {
            "bedrock_enabled": self.bedrock_enabled,
            "aws_connectivity": {},
            "component_status": {},
            "usage_stats": {}
        }
        
        if self.aws_config_manager:
            status["aws_connectivity"] = self.aws_config_manager.test_connectivity()
        
        if self.bedrock_client:
            status["usage_stats"]["bedrock"] = self.bedrock_client.get_usage_stats()
        
        if self.model_router:
            status["usage_stats"]["model_router"] = self.model_router.get_router_stats()
        
        if self.evolution_advisor:
            status["usage_stats"]["evolution_advisor"] = self.evolution_advisor.get_advisor_stats()
        
        if self.decision_engine:
            status["usage_stats"]["decision_engine"] = self.decision_engine.get_decision_stats()
        
        if self.enhanced_autonomy:
            status["usage_stats"]["enhanced_autonomy"] = self.enhanced_autonomy.get_enhanced_stats()
        
        if self.cloud_dna_store:
            status["usage_stats"]["cloud_storage"] = self.cloud_dna_store.get_storage_stats()
        
        return status
    
    def optimize_bedrock_usage(self) -> Dict[str, Any]:
        """Analyze and optimize Bedrock usage"""
        
        if not self.bedrock_enabled:
            return {"error": "Bedrock not enabled"}
        
        optimization_results = {
            "recommendations": [],
            "cost_analysis": {},
            "performance_insights": []
        }
        
        try:
            # Get model router optimization
            if self.model_router:
                router_optimization = self.model_router.optimize_routing()
                optimization_results.update(router_optimization)
            
            # Get cost analysis
            if self.bedrock_client:
                usage_stats = self.bedrock_client.get_usage_stats()
                budget_status = usage_stats.get("cost_tracking", {}).get("budget_status", {})
                
                optimization_results["cost_analysis"] = {
                    "daily_usage": budget_status.get("daily_usage_percent", 0),
                    "monthly_usage": budget_status.get("monthly_usage_percent", 0),
                    "recommendations": []
                }
                
                if budget_status.get("daily_usage_percent", 0) > 80:
                    optimization_results["cost_analysis"]["recommendations"].append(
                        "Consider using more cost-effective models for routine tasks"
                    )
            
            # Get performance insights
            if self.enhanced_autonomy:
                autonomy_stats = self.enhanced_autonomy.get_enhanced_stats()
                llm_stats = autonomy_stats.get("llm_decisions", {})
                
                if llm_stats.get("avg_llm_confidence", 0) < 0.7:
                    optimization_results["performance_insights"].append(
                        "LLM confidence is low - consider adjusting prompts or models"
                    )
                
                if llm_stats.get("escalation_rate", 0) > 0.3:
                    optimization_results["performance_insights"].append(
                        "High escalation rate - consider adjusting risk thresholds"
                    )
            
        except Exception as e:
            logger.error(f"Bedrock optimization analysis failed: {e}")
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced system status including Bedrock metrics"""
        
        base_status = super().get_status()
        
        if self.bedrock_enabled:
            base_status["bedrock"] = self.get_bedrock_status()
        
        return base_status
    
    def get_enhanced_dashboard_data(self) -> Dict[str, Any]:
        """Get enhanced dashboard data with Bedrock insights"""
        
        base_data = super().get_dashboard_data()
        
        if self.bedrock_enabled:
            try:
                # Add Bedrock-specific dashboard data
                bedrock_data = {
                    "bedrock_status": self.get_bedrock_status(),
                    "recent_llm_decisions": [],
                    "evolution_guidance": {},
                    "cost_tracking": {}
                }
                
                if self.enhanced_autonomy:
                    bedrock_data["recent_llm_decisions"] = self.enhanced_autonomy.get_recent_llm_decisions(10)
                
                if self.bedrock_client:
                    usage_stats = self.bedrock_client.get_usage_stats()
                    bedrock_data["cost_tracking"] = usage_stats.get("cost_tracking", {})
                
                base_data["bedrock"] = bedrock_data
                
            except Exception as e:
                logger.error(f"Enhanced dashboard data failed: {e}")
                base_data["bedrock"] = {"error": str(e)}
        
        return base_data
    
    def stop(self) -> None:
        """Stop framework with Bedrock cleanup"""
        
        if self.bedrock_enabled:
            logger.info("Shutting down Bedrock components...")
            
            # Save any pending data
            if self.model_router:
                try:
                    # Could save model performance data here
                    pass
                except Exception as e:
                    logger.error(f"Model router cleanup failed: {e}")
        
        super().stop()


# Convenience function for creating Bedrock-enabled framework
def create_bedrock_framework(config_path: Optional[str] = None,
                           aws_config_path: Optional[str] = None) -> BedrockFramework:
    """Create and initialize Bedrock-enabled framework"""
    
    framework = BedrockFramework(config_path, aws_config_path)
    
    if framework.initialize():
        logger.info("Bedrock framework ready")
        return framework
    else:
        logger.error("Bedrock framework initialization failed")
        raise RuntimeError("Failed to initialize Bedrock framework")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        # Create framework
        framework = create_bedrock_framework()
        
        try:
            # Get evolution guidance
            guidance = await framework.get_evolution_guidance()
            print("Evolution Guidance:", guidance)
            
            # Propose a mutation
            mutation = Mutation(
                type="intelligence_upgrade",
                description="Enhance decision-making capabilities",
                fitness_impact=5.0
            )
            
            result = await framework.propose_mutation_enhanced(mutation)
            print("Mutation Result:", result)
            
            # Get status
            status = framework.get_enhanced_status()
            print("Framework Status:", status)
            
        finally:
            framework.stop()
    
    # Run demo
    asyncio.run(demo())