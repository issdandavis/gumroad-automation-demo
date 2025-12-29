"""
Feedback Analyzer for Self-Evolving AI Framework
================================================

Parses AI responses to extract improvement suggestions and
generate mutation proposals automatically.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from .models import Mutation, MutationType

logger = logging.getLogger(__name__)


@dataclass
class FeedbackInsight:
    """Extracted insight from AI feedback"""
    category: str
    suggestion: str
    confidence: float
    keywords: List[str]
    source_text: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FeedbackAnalyzer:
    """
    Analyzes AI responses to extract actionable improvements.
    
    Features:
    - Keyword-based pattern matching
    - Confidence scoring
    - Mutation proposal generation
    - Multi-language support
    """

    # Pattern categories for mutation detection
    PATTERNS = {
        MutationType.COMMUNICATION_ENHANCEMENT.value: {
            "keywords": ["communication", "channel", "messaging", "sync", "real-time", "notify"],
            "action_words": ["improve", "enhance", "add", "better", "faster", "optimize"]
        },
        MutationType.LANGUAGE_EXPANSION.value: {
            "keywords": ["language", "translation", "codex", "syntax", "protocol", "format"],
            "action_words": ["add", "support", "new", "expand", "include"]
        },
        MutationType.STORAGE_OPTIMIZATION.value: {
            "keywords": ["storage", "backup", "sync", "save", "persist", "cache", "database"],
            "action_words": ["optimize", "improve", "faster", "reliable", "efficient"]
        },
        MutationType.INTELLIGENCE_UPGRADE.value: {
            "keywords": ["learning", "intelligence", "smart", "ai", "model", "reasoning"],
            "action_words": ["upgrade", "improve", "enhance", "better", "advanced"]
        },
        MutationType.PROTOCOL_IMPROVEMENT.value: {
            "keywords": ["protocol", "api", "interface", "endpoint", "method"],
            "action_words": ["improve", "fix", "update", "standardize"]
        },
        MutationType.AUTONOMY_ADJUSTMENT.value: {
            "keywords": ["autonomy", "automatic", "self", "independent", "autonomous"],
            "action_words": ["increase", "decrease", "adjust", "tune"]
        },
        MutationType.PROVIDER_ADDITION.value: {
            "keywords": ["provider", "openai", "anthropic", "claude", "gpt", "gemini"],
            "action_words": ["add", "integrate", "connect", "use", "enable"]
        },
        MutationType.PLUGIN_INTEGRATION.value: {
            "keywords": ["plugin", "extension", "module", "addon", "integration"],
            "action_words": ["add", "install", "enable", "integrate"]
        }
    }
    
    # Confidence modifiers
    CONFIDENCE_MODIFIERS = {
        "should": 0.7,
        "could": 0.5,
        "must": 0.9,
        "need": 0.8,
        "recommend": 0.75,
        "suggest": 0.6,
        "consider": 0.4,
        "critical": 0.95,
        "important": 0.85
    }
    
    def __init__(self):
        self.insights_history: List[FeedbackInsight] = []
        logger.info("FeedbackAnalyzer initialized")
    
    def analyze(self, text: str, source_ai: str = "unknown") -> List[FeedbackInsight]:
        """
        Analyze text for improvement suggestions.
        
        Args:
            text: AI response or feedback text
            source_ai: Name of the AI that provided the feedback
            
        Returns:
            List of extracted insights
        """
        insights = []
        text_lower = text.lower()
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            for mutation_type, patterns in self.PATTERNS.items():
                # Check for keyword matches
                keyword_matches = [k for k in patterns["keywords"] if k in sentence_lower]
                action_matches = [a for a in patterns["action_words"] if a in sentence_lower]
                
                if keyword_matches and action_matches:
                    confidence = self._calculate_confidence(sentence_lower, keyword_matches)
                    
                    insight = FeedbackInsight(
                        category=mutation_type,
                        suggestion=sentence.strip(),
                        confidence=confidence,
                        keywords=keyword_matches + action_matches,
                        source_text=text[:200]
                    )
                    insights.append(insight)
                    self.insights_history.append(insight)
        
        logger.info(f"Analyzed feedback from {source_ai}: {len(insights)} insights found")
        return insights

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_confidence(self, text: str, keywords: List[str]) -> float:
        """Calculate confidence score based on modifiers and keyword density"""
        base_confidence = 0.5
        
        # Adjust based on modifier words
        for modifier, weight in self.CONFIDENCE_MODIFIERS.items():
            if modifier in text:
                base_confidence = max(base_confidence, weight)
        
        # Adjust based on keyword density
        keyword_boost = min(0.3, len(keywords) * 0.1)
        
        return min(1.0, base_confidence + keyword_boost)
    
    def generate_mutations(self, insights: List[FeedbackInsight], 
                          source_ai: str = "unknown",
                          min_confidence: float = 0.5) -> List[Mutation]:
        """
        Generate mutation proposals from insights.
        
        Args:
            insights: List of extracted insights
            source_ai: Source AI name
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of proposed mutations
        """
        mutations = []
        
        for insight in insights:
            if insight.confidence < min_confidence:
                continue
            
            # Estimate fitness impact based on confidence
            fitness_impact = self._estimate_fitness_impact(insight)
            
            mutation = Mutation(
                type=insight.category,
                description=f"AI suggestion: {insight.suggestion[:100]}",
                fitness_impact=fitness_impact,
                risk_score=self._estimate_risk(insight),
                source_ai=source_ai,
                metadata={
                    "confidence": insight.confidence,
                    "keywords": insight.keywords,
                    "insight_timestamp": insight.timestamp
                }
            )
            mutations.append(mutation)
        
        return mutations
    
    def _estimate_fitness_impact(self, insight: FeedbackInsight) -> float:
        """Estimate fitness impact from insight"""
        base_impacts = {
            MutationType.COMMUNICATION_ENHANCEMENT.value: 3.0,
            MutationType.LANGUAGE_EXPANSION.value: 2.0,
            MutationType.STORAGE_OPTIMIZATION.value: 2.5,
            MutationType.INTELLIGENCE_UPGRADE.value: 5.0,
            MutationType.PROTOCOL_IMPROVEMENT.value: 2.0,
            MutationType.AUTONOMY_ADJUSTMENT.value: 1.5,
            MutationType.PROVIDER_ADDITION.value: 3.5,
            MutationType.PLUGIN_INTEGRATION.value: 2.5
        }
        
        base = base_impacts.get(insight.category, 2.0)
        return round(base * insight.confidence, 2)
    
    def _estimate_risk(self, insight: FeedbackInsight) -> float:
        """Estimate risk score from insight"""
        # Higher confidence = lower risk
        base_risk = 1.0 - insight.confidence
        
        # Some mutation types are inherently riskier
        risk_multipliers = {
            MutationType.AUTONOMY_ADJUSTMENT.value: 1.5,
            MutationType.INTELLIGENCE_UPGRADE.value: 1.3,
            MutationType.PLUGIN_INTEGRATION.value: 1.2
        }
        
        multiplier = risk_multipliers.get(insight.category, 1.0)
        return min(1.0, base_risk * multiplier)
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """Get summary of all insights"""
        if not self.insights_history:
            return {"total": 0, "by_category": {}, "avg_confidence": 0}
        
        by_category = {}
        for insight in self.insights_history:
            by_category[insight.category] = by_category.get(insight.category, 0) + 1
        
        return {
            "total": len(self.insights_history),
            "by_category": by_category,
            "avg_confidence": sum(i.confidence for i in self.insights_history) / len(self.insights_history)
        }
