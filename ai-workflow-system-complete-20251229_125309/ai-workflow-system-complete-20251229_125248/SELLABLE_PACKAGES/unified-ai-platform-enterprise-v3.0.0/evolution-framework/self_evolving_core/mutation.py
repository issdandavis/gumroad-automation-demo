"""
Mutation Engine for Self-Evolving AI Framework
==============================================

Processes AI feedback and applies system mutations with:
- Validation before application
- Risk assessment integration
- Rollback capability
- Fitness impact calculation
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import re

from .models import (
    SystemDNA, Mutation, MutationRecord, MutationType,
    OperationResult, CoreTraits
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of mutation validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggested_modifications: Optional[Dict[str, Any]] = None


@dataclass
class MutationResult:
    """Result of mutation application"""
    success: bool
    mutation_id: str
    fitness_delta: float
    new_generation: int
    rollback_snapshot_id: Optional[str] = None
    error: Optional[str] = None


class MutationValidator:
    """
    Validates mutations to prevent system corruption.
    
    Checks:
    - Type validity
    - Fitness impact bounds
    - DNA invariants
    - Compatibility with current state
    """
    
    VALID_MUTATION_TYPES = [t.value for t in MutationType]
    
    MAX_FITNESS_IMPACT = 50.0
    MIN_FITNESS_IMPACT = -30.0
    
    # Invariants that must be maintained
    INVARIANTS = {
        "min_communication_channels": 1,
        "min_language_support": 1,
        "min_fitness_score": 0.0,
        "max_autonomy_level": 1.0,
        "min_autonomy_level": 0.0
    }
    
    def validate(self, mutation: Mutation, current_dna: SystemDNA) -> ValidationResult:
        """
        Check mutation safety and compatibility.
        
        Returns ValidationResult with validity status and any issues.
        """
        errors = []
        warnings = []
        
        # Check mutation type
        if mutation.type not in self.VALID_MUTATION_TYPES:
            errors.append(f"Invalid mutation type: {mutation.type}")
        
        # Check fitness impact bounds
        if mutation.fitness_impact > self.MAX_FITNESS_IMPACT:
            warnings.append(f"Fitness impact {mutation.fitness_impact} exceeds recommended max {self.MAX_FITNESS_IMPACT}")
        if mutation.fitness_impact < self.MIN_FITNESS_IMPACT:
            errors.append(f"Fitness impact {mutation.fitness_impact} below minimum {self.MIN_FITNESS_IMPACT}")
        
        # Check resulting fitness would be valid
        projected_fitness = current_dna.fitness_score + mutation.fitness_impact
        if projected_fitness < self.INVARIANTS["min_fitness_score"]:
            errors.append(f"Mutation would result in negative fitness: {projected_fitness}")
        
        # Check description is meaningful
        if not mutation.description or len(mutation.description) < 10:
            warnings.append("Mutation description is too short or missing")
        
        # Check risk score is set
        if mutation.risk_score <= 0:
            warnings.append("Risk score not calculated, will be assessed during application")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def check_invariants(self, proposed_dna: SystemDNA) -> Tuple[bool, List[str]]:
        """
        Verify DNA invariants are maintained.
        
        Returns (is_valid, list of violations)
        """
        violations = []
        
        if proposed_dna.core_traits.communication_channels < self.INVARIANTS["min_communication_channels"]:
            violations.append(f"Communication channels below minimum: {proposed_dna.core_traits.communication_channels}")
        
        if proposed_dna.core_traits.language_support < self.INVARIANTS["min_language_support"]:
            violations.append(f"Language support below minimum: {proposed_dna.core_traits.language_support}")
        
        if proposed_dna.fitness_score < self.INVARIANTS["min_fitness_score"]:
            violations.append(f"Fitness score below minimum: {proposed_dna.fitness_score}")
        
        if proposed_dna.core_traits.autonomy_level > self.INVARIANTS["max_autonomy_level"]:
            violations.append(f"Autonomy level above maximum: {proposed_dna.core_traits.autonomy_level}")
        
        if proposed_dna.core_traits.autonomy_level < self.INVARIANTS["min_autonomy_level"]:
            violations.append(f"Autonomy level below minimum: {proposed_dna.core_traits.autonomy_level}")
        
        return len(violations) == 0, violations


class MutationEngine:
    """
    Engine for AI system evolution and self-modification.
    
    Responsibilities:
    - Analyze AI feedback for mutation opportunities
    - Validate mutations before application
    - Apply mutations with rollback capability
    - Calculate fitness impact
    - Track mutation history
    """
    
    def __init__(self, dna_manager=None, autonomy_controller=None, rollback_manager=None):
        self.dna_manager = dna_manager
        self.autonomy = autonomy_controller
        self.rollback = rollback_manager
        self.validator = MutationValidator()
        
        # Mutation type handlers
        self._handlers = {
            MutationType.COMMUNICATION_ENHANCEMENT.value: self._apply_communication_enhancement,
            MutationType.LANGUAGE_EXPANSION.value: self._apply_language_expansion,
            MutationType.STORAGE_OPTIMIZATION.value: self._apply_storage_optimization,
            MutationType.INTELLIGENCE_UPGRADE.value: self._apply_intelligence_upgrade,
            MutationType.PROTOCOL_IMPROVEMENT.value: self._apply_protocol_improvement,
            MutationType.AUTONOMY_ADJUSTMENT.value: self._apply_autonomy_adjustment,
            MutationType.PROVIDER_ADDITION.value: self._apply_provider_addition,
            MutationType.PLUGIN_INTEGRATION.value: self._apply_plugin_integration
        }
        
        logger.info("MutationEngine initialized")
    
    def analyze_feedback(self, feedback_text: str, source_ai: str = "unknown") -> List[Mutation]:
        """
        Analyze AI feedback to generate mutation proposals.
        
        Looks for improvement-related keywords and patterns.
        """
        mutations = []
        feedback_lower = feedback_text.lower()
        
        # Communication improvements
        comm_patterns = ["communication", "channel", "messaging", "sync", "real-time"]
        if any(p in feedback_lower for p in comm_patterns):
            if any(w in feedback_lower for w in ["improve", "enhance", "add", "better", "faster"]):
                mutations.append(Mutation(
                    type=MutationType.COMMUNICATION_ENHANCEMENT.value,
                    description=f"Communication improvement suggested by {source_ai}",
                    fitness_impact=self._estimate_impact("communication_enhancement", feedback_text),
                    source_ai=source_ai
                ))
        
        # Language expansion
        lang_patterns = ["language", "translation", "codex", "syntax"]
        if any(p in feedback_lower for p in lang_patterns):
            if any(w in feedback_lower for w in ["add", "support", "new", "expand"]):
                mutations.append(Mutation(
                    type=MutationType.LANGUAGE_EXPANSION.value,
                    description=f"Language expansion suggested by {source_ai}",
                    fitness_impact=self._estimate_impact("language_expansion", feedback_text),
                    source_ai=source_ai
                ))
        
        # Storage optimization
        storage_patterns = ["storage", "backup", "sync", "save", "persist"]
        if any(p in feedback_lower for p in storage_patterns):
            if any(w in feedback_lower for w in ["optimize", "improve", "faster", "reliable"]):
                mutations.append(Mutation(
                    type=MutationType.STORAGE_OPTIMIZATION.value,
                    description=f"Storage optimization suggested by {source_ai}",
                    fitness_impact=self._estimate_impact("storage_optimization", feedback_text),
                    source_ai=source_ai
                ))
        
        # Intelligence upgrade
        intel_patterns = ["learning", "intelligence", "smart", "ai", "model"]
        if any(p in feedback_lower for p in intel_patterns):
            if any(w in feedback_lower for w in ["upgrade", "improve", "enhance", "better"]):
                mutations.append(Mutation(
                    type=MutationType.INTELLIGENCE_UPGRADE.value,
                    description=f"Intelligence upgrade suggested by {source_ai}",
                    fitness_impact=self._estimate_impact("intelligence_upgrade", feedback_text),
                    source_ai=source_ai
                ))
        
        # Provider addition
        provider_patterns = ["provider", "api", "openai", "anthropic", "claude", "gpt"]
        if any(p in feedback_lower for p in provider_patterns):
            if any(w in feedback_lower for w in ["add", "integrate", "connect", "use"]):
                mutations.append(Mutation(
                    type=MutationType.PROVIDER_ADDITION.value,
                    description=f"Provider addition suggested by {source_ai}",
                    fitness_impact=self._estimate_impact("provider_addition", feedback_text),
                    source_ai=source_ai
                ))
        
        logger.info(f"Analyzed feedback from {source_ai}, generated {len(mutations)} mutation proposals")
        return mutations
    
    def _estimate_impact(self, mutation_type: str, context: str) -> float:
        """Estimate fitness impact based on mutation type and context"""
        base_impacts = {
            "communication_enhancement": 3.0,
            "language_expansion": 2.0,
            "storage_optimization": 2.5,
            "intelligence_upgrade": 5.0,
            "protocol_improvement": 2.0,
            "autonomy_adjustment": 1.5,
            "provider_addition": 3.5,
            "plugin_integration": 2.5
        }
        
        impact = base_impacts.get(mutation_type, 1.0)
        
        # Adjust based on urgency words
        if any(w in context.lower() for w in ["critical", "urgent", "important"]):
            impact *= 1.5
        
        return round(impact, 2)
    
    def validate_mutation(self, mutation: Mutation, dna: Optional[SystemDNA] = None) -> ValidationResult:
        """Validate mutation before application"""
        if dna is None and self.dna_manager:
            dna = self.dna_manager.load()
        
        if dna is None:
            return ValidationResult(
                is_valid=False,
                errors=["No DNA available for validation"],
                warnings=[]
            )
        
        return self.validator.validate(mutation, dna)
    
    def apply_mutation(self, mutation: Mutation, dna: Optional[SystemDNA] = None) -> MutationResult:
        """
        Apply validated mutation with rollback capability.
        
        Steps:
        1. Load current DNA
        2. Create rollback snapshot
        3. Validate mutation
        4. Apply mutation changes
        5. Verify invariants
        6. Save updated DNA
        """
        # Load DNA
        if dna is None and self.dna_manager:
            dna = self.dna_manager.load()
        
        if dna is None:
            return MutationResult(
                success=False,
                mutation_id="",
                fitness_delta=0,
                new_generation=0,
                error="No DNA available"
            )
        
        # Create rollback snapshot
        snapshot_id = None
        if self.rollback:
            snapshot = self.rollback.create_snapshot(dna, f"pre_mutation_{mutation.type}")
            snapshot_id = snapshot.id
        
        # Validate
        validation = self.validator.validate(mutation, dna)
        if not validation.is_valid:
            return MutationResult(
                success=False,
                mutation_id="",
                fitness_delta=0,
                new_generation=dna.generation,
                error=f"Validation failed: {'; '.join(validation.errors)}"
            )
        
        # Log warnings
        for warning in validation.warnings:
            logger.warning(f"Mutation warning: {warning}")
        
        try:
            # Apply mutation based on type
            handler = self._handlers.get(mutation.type)
            if handler:
                handler(dna, mutation)
            else:
                logger.warning(f"No handler for mutation type: {mutation.type}")
            
            # Update fitness and generation
            old_fitness = dna.fitness_score
            dna.fitness_score += mutation.fitness_impact
            dna.generation += 1
            
            # Create mutation record
            mutation_id = f"mut_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            record = MutationRecord(
                id=mutation_id,
                timestamp=datetime.now().isoformat(),
                type=mutation.type,
                description=mutation.description,
                fitness_impact=mutation.fitness_impact,
                risk_score=mutation.risk_score,
                generation=dna.generation,
                source_ai=mutation.source_ai,
                auto_approved=mutation.auto_approved,
                rollback_snapshot=snapshot_id
            )
            dna.mutations.append(record)
            
            # Verify invariants
            is_valid, violations = self.validator.check_invariants(dna)
            if not is_valid:
                # Rollback
                if self.rollback and snapshot_id:
                    self.rollback.rollback_by_id(snapshot_id)
                return MutationResult(
                    success=False,
                    mutation_id=mutation_id,
                    fitness_delta=0,
                    new_generation=dna.generation - 1,
                    error=f"Invariant violations: {'; '.join(violations)}"
                )
            
            # Save DNA
            if self.dna_manager:
                self.dna_manager.save(dna)
            
            # Record mutation in autonomy controller
            if self.autonomy:
                self.autonomy.record_mutation()
            
            logger.info(f"Mutation applied: {mutation_id} ({mutation.type}) - Fitness: {old_fitness} -> {dna.fitness_score}")
            
            return MutationResult(
                success=True,
                mutation_id=mutation_id,
                fitness_delta=mutation.fitness_impact,
                new_generation=dna.generation,
                rollback_snapshot_id=snapshot_id
            )
            
        except Exception as e:
            logger.error(f"Mutation application failed: {e}")
            # Attempt rollback
            if self.rollback and snapshot_id:
                try:
                    self.rollback.rollback_by_id(snapshot_id)
                except Exception as re:
                    logger.error(f"Rollback also failed: {re}")
            
            return MutationResult(
                success=False,
                mutation_id="",
                fitness_delta=0,
                new_generation=dna.generation if dna else 0,
                error=str(e)
            )
    
    def calculate_fitness_impact(self, mutation: Mutation, dna: SystemDNA) -> float:
        """Calculate expected fitness impact for a mutation"""
        return self._estimate_impact(mutation.type, mutation.description)
    
    # Mutation type handlers
    def _apply_communication_enhancement(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply communication enhancement mutation"""
        dna.core_traits.communication_channels += 1
        if "real-time" in mutation.description.lower():
            if "real_time_sync" not in dna.core_traits.evolutionary_features:
                dna.core_traits.evolutionary_features.append("real_time_sync")
    
    def _apply_language_expansion(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply language expansion mutation"""
        dna.core_traits.language_support += 1
    
    def _apply_storage_optimization(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply storage optimization mutation"""
        if "optimized_storage" not in dna.core_traits.evolutionary_features:
            dna.core_traits.evolutionary_features.append("optimized_storage")
    
    def _apply_intelligence_upgrade(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply intelligence upgrade mutation"""
        if "advanced_learning" not in dna.core_traits.evolutionary_features:
            dna.core_traits.evolutionary_features.append("advanced_learning")
    
    def _apply_protocol_improvement(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply protocol improvement mutation"""
        if "enhanced_protocols" not in dna.core_traits.evolutionary_features:
            dna.core_traits.evolutionary_features.append("enhanced_protocols")
    
    def _apply_autonomy_adjustment(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply autonomy adjustment mutation"""
        # Parse adjustment from description or metadata
        adjustment = mutation.metadata.get("autonomy_delta", 0.05)
        new_level = dna.core_traits.autonomy_level + adjustment
        dna.core_traits.autonomy_level = max(0.0, min(1.0, new_level))
    
    def _apply_provider_addition(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply provider addition mutation"""
        provider = mutation.metadata.get("provider_name")
        if provider and provider not in dna.core_traits.enabled_providers:
            dna.core_traits.enabled_providers.append(provider)
    
    def _apply_plugin_integration(self, dna: SystemDNA, mutation: Mutation) -> None:
        """Apply plugin integration mutation"""
        if "plugin_system" not in dna.core_traits.evolutionary_features:
            dna.core_traits.evolutionary_features.append("plugin_system")
