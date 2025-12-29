"""
Evolution Advisor - LLM-Powered Evolution Strategy
=================================================

Uses AWS Bedrock LLMs to provide intelligent guidance for system evolution.
Analyzes system state, generates mutation strategies, and provides reasoning
for autonomous decision-making.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .models import SystemDNA, Mutation, FitnessScore, MutationType
from .bedrock_client import BedrockClient, BedrockRequest, BedrockResponse
from .aws_config import AWSConfigManager

logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """Context for LLM analysis"""
    current_generation: int
    fitness_score: float
    recent_mutations: List[Dict[str, Any]]
    fitness_trend: str  # "improving", "stable", "degrading"
    performance_metrics: Dict[str, float]
    complexity: str  # "low", "medium", "high"
    system_age_hours: float
    error_rate: float
    recent_errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_generation": self.current_generation,
            "fitness_score": self.fitness_score,
            "recent_mutations": self.recent_mutations,
            "fitness_trend": self.fitness_trend,
            "performance_metrics": self.performance_metrics,
            "complexity": self.complexity,
            "system_age_hours": self.system_age_hours,
            "error_rate": self.error_rate,
            "recent_errors": self.recent_errors
        }


@dataclass
class EvolutionAnalysis:
    """LLM analysis of system evolution state"""
    current_state_assessment: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    recommended_focus_areas: List[str]
    confidence_score: float
    reasoning: str
    priority_mutations: List[str]
    risk_factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state_assessment": self.current_state_assessment,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "opportunities": self.opportunities,
            "threats": self.threats,
            "recommended_focus_areas": self.recommended_focus_areas,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "priority_mutations": self.priority_mutations,
            "risk_factors": self.risk_factors
        }


@dataclass
class StrategicMutation:
    """LLM-generated strategic mutation"""
    type: str
    description: str
    rationale: str
    expected_fitness_impact: float
    risk_score: float
    implementation_steps: List[str]
    success_criteria: Dict[str, float]
    dependencies: List[str]
    timeline_estimate: str
    confidence: float
    
    def to_mutation(self) -> Mutation:
        """Convert to standard Mutation object"""
        return Mutation(
            type=self.type,
            description=self.description,
            fitness_impact=self.expected_fitness_impact,
            risk_score=self.risk_score,
            metadata={
                "rationale": self.rationale,
                "implementation_steps": self.implementation_steps,
                "success_criteria": self.success_criteria,
                "dependencies": self.dependencies,
                "timeline_estimate": self.timeline_estimate,
                "confidence": self.confidence,
                "source": "evolution_advisor"
            }
        )


@dataclass
class MutationStrategy:
    """LLM-generated comprehensive mutation strategy"""
    primary_mutations: List[StrategicMutation]
    contingency_mutations: List[StrategicMutation]
    execution_order: List[str]
    success_criteria: Dict[str, float]
    risk_mitigation: List[str]
    expected_outcomes: Dict[str, str]
    timeline_estimate: str
    overall_confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_mutations": [m.__dict__ for m in self.primary_mutations],
            "contingency_mutations": [m.__dict__ for m in self.contingency_mutations],
            "execution_order": self.execution_order,
            "success_criteria": self.success_criteria,
            "risk_mitigation": self.risk_mitigation,
            "expected_outcomes": self.expected_outcomes,
            "timeline_estimate": self.timeline_estimate,
            "overall_confidence": self.overall_confidence,
            "reasoning": self.reasoning
        }


class EvolutionAdvisor:
    """
    Bedrock-powered evolution strategy advisor that provides intelligent
    guidance for system evolution using LLM reasoning.
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock = bedrock_client
        self.analysis_history: List[EvolutionAnalysis] = []
        self.strategy_history: List[MutationStrategy] = []
        
    def _prepare_analysis_context(self, dna: SystemDNA, 
                                fitness_history: List[FitnessScore]) -> AnalysisContext:
        """Prepare structured context for LLM analysis"""
        
        # Calculate fitness trend
        if len(fitness_history) >= 2:
            recent_scores = [f.overall for f in fitness_history[-5:]]
            if recent_scores[-1] > recent_scores[0] * 1.05:
                trend = "improving"
            elif recent_scores[-1] < recent_scores[0] * 0.95:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Extract performance metrics
        latest_fitness = fitness_history[-1] if fitness_history else FitnessScore(overall=100.0, success_rate=1.0, healing_speed=1.0, cost_efficiency=1.0, uptime=1.0)
        performance_metrics = {
            "success_rate": latest_fitness.success_rate,
            "healing_speed": latest_fitness.healing_speed,
            "cost_efficiency": latest_fitness.cost_efficiency,
            "uptime": latest_fitness.uptime
        }
        
        # Assess complexity based on system state
        complexity_score = 0
        complexity_score += len(dna.mutations) * 0.1
        complexity_score += len(dna.core_traits.ai_participants) * 0.2
        complexity_score += len(dna.core_traits.evolutionary_features) * 0.1
        
        if complexity_score < 2.0:
            complexity = "low"
        elif complexity_score < 5.0:
            complexity = "medium"
        else:
            complexity = "high"
        
        # Calculate system age
        birth_time = datetime.fromisoformat(dna.birth_timestamp.replace('Z', '+00:00'))
        system_age_hours = (datetime.now() - birth_time.replace(tzinfo=None)).total_seconds() / 3600
        
        # Extract recent mutations
        recent_mutations = [
            {
                "type": m.type,
                "description": m.description,
                "fitness_impact": m.fitness_impact,
                "risk_score": m.risk_score,
                "timestamp": m.timestamp
            }
            for m in dna.mutations[-10:]  # Last 10 mutations
        ]
        
        return AnalysisContext(
            current_generation=dna.generation,
            fitness_score=dna.fitness_score,
            recent_mutations=recent_mutations,
            fitness_trend=trend,
            performance_metrics=performance_metrics,
            complexity=complexity,
            system_age_hours=system_age_hours,
            error_rate=1.0 - performance_metrics["success_rate"],
            recent_errors=[]  # TODO: Extract from logs
        )
    
    def _build_analysis_prompt(self, context: AnalysisContext) -> str:
        """Build comprehensive analysis prompt for LLM"""
        
        prompt = f"""You are an expert AI system architect analyzing a self-evolving AI system for optimization opportunities.

SYSTEM STATE ANALYSIS:
- Current Generation: {context.current_generation}
- Fitness Score: {context.fitness_score:.2f}
- Fitness Trend: {context.fitness_trend}
- System Age: {context.system_age_hours:.1f} hours
- Complexity Level: {context.complexity}

PERFORMANCE METRICS:
- Success Rate: {context.performance_metrics['success_rate']:.2%}
- Healing Speed: {context.performance_metrics['healing_speed']:.2f}s
- Cost Efficiency: {context.performance_metrics['cost_efficiency']:.2f}
- Uptime: {context.performance_metrics['uptime']:.2%}
- Error Rate: {context.error_rate:.2%}

RECENT MUTATIONS ({len(context.recent_mutations)} total):
"""
        
        for i, mutation in enumerate(context.recent_mutations[-5:], 1):
            prompt += f"""
{i}. Type: {mutation['type']}
   Description: {mutation['description']}
   Fitness Impact: {mutation['fitness_impact']:+.1f}
   Risk Score: {mutation['risk_score']:.2f}
"""
        
        prompt += f"""
ANALYSIS REQUIREMENTS:
Please provide a comprehensive SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) of this AI system's current evolutionary state.

Focus on:
1. System performance and efficiency patterns
2. Evolution trajectory and mutation effectiveness
3. Risk factors and stability concerns
4. Growth opportunities and optimization potential
5. Technical debt and architectural considerations

Provide your analysis in the following JSON format:
{{
    "current_state_assessment": "Brief overall assessment of system health and evolution progress",
    "strengths": ["List of current system strengths"],
    "weaknesses": ["List of areas needing improvement"],
    "opportunities": ["List of growth and optimization opportunities"],
    "threats": ["List of risks and potential issues"],
    "recommended_focus_areas": ["Priority areas for next evolution cycle"],
    "confidence_score": 0.85,
    "reasoning": "Detailed explanation of your analysis and recommendations",
    "priority_mutations": ["List of mutation types that should be prioritized"],
    "risk_factors": ["List of specific risks to monitor"]
}}

Be specific, actionable, and focus on measurable improvements. Consider both short-term optimizations and long-term strategic evolution."""
        
        return prompt
    
    async def analyze_system_state(self, dna: SystemDNA, 
                                 fitness_history: List[FitnessScore]) -> EvolutionAnalysis:
        """Analyze current system state using Bedrock LLM"""
        
        # Prepare context for LLM
        context = self._prepare_analysis_context(dna, fitness_history)
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(context)
        
        # Create Bedrock request
        request = BedrockRequest(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            prompt=prompt,
            max_tokens=2000,
            temperature=0.3,
            metadata={"operation": "system_analysis", "generation": dna.generation}
        )
        
        # Query Bedrock for analysis
        response = await self.bedrock.invoke_model(request)
        
        if not response.success:
            logger.error(f"Bedrock analysis failed: {response.error}")
            # Return fallback analysis
            return self._create_fallback_analysis(context)
        
        # Parse LLM response
        try:
            analysis_data = self._parse_analysis_response(response.content)
            analysis = EvolutionAnalysis(**analysis_data)
            
            # Store in history
            self.analysis_history.append(analysis)
            
            # Keep only last 50 analyses
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-50:]
            
            logger.info(f"System analysis completed with confidence {analysis.confidence_score:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return self._create_fallback_analysis(context)
    
    def _parse_analysis_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM analysis response"""
        try:
            # Try to extract JSON from response
            content = response_content.strip()
            
            # Look for JSON block
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif content.startswith("{") and content.endswith("}"):
                json_str = content
            else:
                # Try to find JSON-like structure
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                else:
                    raise ValueError("No JSON structure found in response")
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to parse analysis JSON: {e}")
            # Return minimal valid structure
            return {
                "current_state_assessment": "Analysis parsing failed",
                "strengths": ["System is operational"],
                "weaknesses": ["Analysis system needs improvement"],
                "opportunities": ["Improve LLM response parsing"],
                "threats": ["Analysis failures"],
                "recommended_focus_areas": ["System stability"],
                "confidence_score": 0.1,
                "reasoning": f"Failed to parse LLM response: {str(e)}",
                "priority_mutations": ["communication_enhancement"],
                "risk_factors": ["Analysis system instability"]
            }
    
    def _create_fallback_analysis(self, context: AnalysisContext) -> EvolutionAnalysis:
        """Create fallback analysis when LLM fails"""
        return EvolutionAnalysis(
            current_state_assessment=f"System at generation {context.current_generation} with {context.fitness_trend} fitness trend",
            strengths=["System is operational", "Has mutation capability"],
            weaknesses=["LLM analysis unavailable", "Limited insight"],
            opportunities=["Restore LLM connectivity", "Improve fallback analysis"],
            threats=["Analysis system failure", "Reduced optimization capability"],
            recommended_focus_areas=["System stability", "LLM connectivity"],
            confidence_score=0.3,
            reasoning="Fallback analysis due to LLM unavailability",
            priority_mutations=["communication_enhancement", "intelligence_upgrade"],
            risk_factors=["LLM service disruption"]
        )
    
    async def generate_mutation_strategy(self, analysis: EvolutionAnalysis, 
                                       dna: SystemDNA) -> MutationStrategy:
        """Generate comprehensive mutation strategy using LLM reasoning"""
        
        strategy_prompt = self._build_strategy_prompt(analysis, dna)
        
        request = BedrockRequest(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            prompt=strategy_prompt,
            max_tokens=3000,
            temperature=0.4,
            metadata={"operation": "strategy_generation", "generation": dna.generation}
        )
        
        response = await self.bedrock.invoke_model(request)
        
        if not response.success:
            logger.error(f"Strategy generation failed: {response.error}")
            return self._create_fallback_strategy(analysis, dna)
        
        try:
            strategy_data = self._parse_strategy_response(response.content)
            strategy = self._build_mutation_strategy(strategy_data)
            
            # Store in history
            self.strategy_history.append(strategy)
            
            # Keep only last 20 strategies
            if len(self.strategy_history) > 20:
                self.strategy_history = self.strategy_history[-20:]
            
            logger.info(f"Mutation strategy generated with {len(strategy.primary_mutations)} primary mutations")
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to parse strategy response: {e}")
            return self._create_fallback_strategy(analysis, dna)
    
    def _build_strategy_prompt(self, analysis: EvolutionAnalysis, dna: SystemDNA) -> str:
        """Build strategy generation prompt"""
        
        available_mutations = [mt.value for mt in MutationType]
        
        prompt = f"""You are an expert AI system architect designing an evolution strategy based on system analysis.

SYSTEM ANALYSIS RESULTS:
Current State: {analysis.current_state_assessment}

Strengths:
{chr(10).join(f"- {s}" for s in analysis.strengths)}

Weaknesses:
{chr(10).join(f"- {w}" for w in analysis.weaknesses)}

Opportunities:
{chr(10).join(f"- {o}" for o in analysis.opportunities)}

Threats:
{chr(10).join(f"- {t}" for t in analysis.threats)}

Recommended Focus Areas:
{chr(10).join(f"- {f}" for f in analysis.recommended_focus_areas)}

AVAILABLE MUTATION TYPES:
{chr(10).join(f"- {mt}" for mt in available_mutations)}

CURRENT SYSTEM STATE:
- Generation: {dna.generation}
- Fitness Score: {dna.fitness_score}
- Recent Mutations: {len(dna.mutations)}

STRATEGY REQUIREMENTS:
Design a comprehensive mutation strategy that addresses the identified weaknesses and capitalizes on opportunities. Include:

1. Primary mutations (2-4 high-impact changes)
2. Contingency mutations (backup options if primary fails)
3. Execution order and dependencies
4. Risk mitigation strategies
5. Success criteria and expected outcomes

Provide your strategy in this JSON format:
{{
    "primary_mutations": [
        {{
            "type": "mutation_type_from_available_list",
            "description": "Detailed description of what this mutation does",
            "rationale": "Why this mutation is needed based on analysis",
            "expected_fitness_impact": 5.2,
            "risk_score": 0.3,
            "implementation_steps": ["Step 1", "Step 2", "Step 3"],
            "success_criteria": {{"metric1": 0.95, "metric2": 10.0}},
            "dependencies": ["other_mutation_type"],
            "timeline_estimate": "2-4 hours",
            "confidence": 0.8
        }}
    ],
    "contingency_mutations": [
        {{
            "type": "fallback_mutation_type",
            "description": "Fallback option if primary mutations fail",
            "rationale": "Backup strategy reasoning",
            "expected_fitness_impact": 2.0,
            "risk_score": 0.1,
            "implementation_steps": ["Fallback step 1"],
            "success_criteria": {{"basic_metric": 0.8}},
            "dependencies": [],
            "timeline_estimate": "1 hour",
            "confidence": 0.9
        }}
    ],
    "execution_order": ["mutation_type_1", "mutation_type_2"],
    "success_criteria": {{"overall_fitness": 110.0, "success_rate": 0.95}},
    "risk_mitigation": ["Create snapshot before mutations", "Monitor fitness continuously"],
    "expected_outcomes": {{"short_term": "Improved stability", "long_term": "Enhanced capabilities"}},
    "timeline_estimate": "4-8 hours total",
    "overall_confidence": 0.75,
    "reasoning": "Detailed explanation of strategy rationale and expected benefits"
}}

Focus on mutations that directly address the analysis findings. Be specific about implementation and measurable about success criteria."""
        
        return prompt
    
    def _parse_strategy_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM strategy response"""
        try:
            # Similar JSON extraction logic as analysis
            content = response_content.strip()
            
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                json_str = content[start:end].strip()
            elif content.startswith("{") and content.endswith("}"):
                json_str = content
            else:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                else:
                    raise ValueError("No JSON structure found in response")
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to parse strategy JSON: {e}")
            raise
    
    def _build_mutation_strategy(self, strategy_data: Dict[str, Any]) -> MutationStrategy:
        """Build MutationStrategy from parsed data"""
        
        primary_mutations = [
            StrategicMutation(**mutation_data)
            for mutation_data in strategy_data.get("primary_mutations", [])
        ]
        
        contingency_mutations = [
            StrategicMutation(**mutation_data)
            for mutation_data in strategy_data.get("contingency_mutations", [])
        ]
        
        return MutationStrategy(
            primary_mutations=primary_mutations,
            contingency_mutations=contingency_mutations,
            execution_order=strategy_data.get("execution_order", []),
            success_criteria=strategy_data.get("success_criteria", {}),
            risk_mitigation=strategy_data.get("risk_mitigation", []),
            expected_outcomes=strategy_data.get("expected_outcomes", {}),
            timeline_estimate=strategy_data.get("timeline_estimate", "Unknown"),
            overall_confidence=strategy_data.get("overall_confidence", 0.5),
            reasoning=strategy_data.get("reasoning", "No reasoning provided")
        )
    
    def _create_fallback_strategy(self, analysis: EvolutionAnalysis, 
                                dna: SystemDNA) -> MutationStrategy:
        """Create fallback strategy when LLM fails"""
        
        # Create basic mutations based on analysis
        primary_mutations = []
        
        if "communication" in analysis.recommended_focus_areas:
            primary_mutations.append(StrategicMutation(
                type="communication_enhancement",
                description="Improve system communication capabilities",
                rationale="Identified as priority focus area",
                expected_fitness_impact=3.0,
                risk_score=0.2,
                implementation_steps=["Enhance message routing", "Improve error handling"],
                success_criteria={"success_rate": 0.95},
                dependencies=[],
                timeline_estimate="2 hours",
                confidence=0.6
            ))
        
        if "intelligence" in analysis.recommended_focus_areas:
            primary_mutations.append(StrategicMutation(
                type="intelligence_upgrade",
                description="Upgrade system intelligence capabilities",
                rationale="Identified as priority focus area",
                expected_fitness_impact=4.0,
                risk_score=0.3,
                implementation_steps=["Improve decision making", "Enhance learning"],
                success_criteria={"fitness_score": dna.fitness_score + 5.0},
                dependencies=[],
                timeline_estimate="3 hours",
                confidence=0.5
            ))
        
        return MutationStrategy(
            primary_mutations=primary_mutations,
            contingency_mutations=[],
            execution_order=[m.type for m in primary_mutations],
            success_criteria={"overall_fitness": dna.fitness_score + 5.0},
            risk_mitigation=["Create snapshot before mutations"],
            expected_outcomes={"short_term": "Basic improvements"},
            timeline_estimate="2-5 hours",
            overall_confidence=0.4,
            reasoning="Fallback strategy due to LLM unavailability"
        )
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of analyses"""
        return [analysis.to_dict() for analysis in self.analysis_history]
    
    def get_strategy_history(self) -> List[Dict[str, Any]]:
        """Get history of strategies"""
        return [strategy.to_dict() for strategy in self.strategy_history]
    
    def get_advisor_stats(self) -> Dict[str, Any]:
        """Get advisor performance statistics"""
        if not self.analysis_history:
            return {"analyses_count": 0, "strategies_count": 0}
        
        recent_analyses = self.analysis_history[-10:]
        avg_confidence = sum(a.confidence_score for a in recent_analyses) / len(recent_analyses)
        
        return {
            "analyses_count": len(self.analysis_history),
            "strategies_count": len(self.strategy_history),
            "avg_confidence": avg_confidence,
            "last_analysis_time": datetime.now().isoformat(),
            "focus_areas_frequency": self._get_focus_areas_frequency()
        }
    
    def _get_focus_areas_frequency(self) -> Dict[str, int]:
        """Get frequency of recommended focus areas"""
        frequency = {}
        for analysis in self.analysis_history:
            for area in analysis.recommended_focus_areas:
                frequency[area] = frequency.get(area, 0) + 1
        return frequency