"""
Unit Tests for MutationValidator
===============================

Tests for mutation validation logic including type checking,
bounds validation, and invariant preservation.

**Validates: Requirements 3.5**
"""

import pytest
from self_evolving_core.mutation import MutationValidator, ValidationResult
from self_evolving_core.models import SystemDNA, Mutation, MutationType, CoreTraits


class TestMutationValidator:
    """Unit tests for MutationValidator class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = MutationValidator()
        self.sample_dna = SystemDNA(
            generation=5,
            fitness_score=100.0,
            core_traits=CoreTraits(
                communication_channels=8,
                language_support=12,
                autonomy_level=0.7
            )
        )
    
    def test_accepts_valid_mutation_type(self):
        """Test that valid mutation types are accepted"""
        mutation = Mutation(
            type=MutationType.COMMUNICATION_ENHANCEMENT.value,
            description="Valid communication enhancement",
            fitness_impact=5.0
        )
        
        result = self.validator.validate(mutation, self.sample_dna)
        
        assert result.is_valid, "Valid mutation type should be accepted"
        assert len(result.errors) == 0, "No errors should be present for valid type"
    
    def test_rejects_unknown_mutation_type(self):
        """Test that unknown mutation types are rejected"""
        mutation = Mutation(
            type="unknown_mutation_type",
            description="Invalid mutation type test",
            fitness_impact=5.0
        )
        
        result = self.validator.validate(mutation, self.sample_dna)
        
        assert not result.is_valid, "Unknown mutation type should be rejected"
        assert any("Invalid mutation type" in error for error in result.errors), \
            "Should have error about invalid mutation type"
    
    def test_fitness_impact_bounds_validation(self):
        """Test fitness impact bounds checking"""
        # Test maximum bound
        high_impact_mutation = Mutation(
            type=MutationType.INTELLIGENCE_UPGRADE.value,
            description="High impact mutation",
            fitness_impact=100.0  # Exceeds MAX_FITNESS_IMPACT
        )
        
        result = self.validator.validate(high_impact_mutation, self.sample_dna)
        assert len(result.warnings) > 0, "High impact should generate warning"
        
        # Test minimum bound
        low_impact_mutation = Mutation(
            type=MutationType.STORAGE_OPTIMIZATION.value,
            description="Negative impact mutation",
            fitness_impact=-50.0  # Below MIN_FITNESS_IMPACT
        )
        
        result = self.validator.validate(low_impact_mutation, self.sample_dna)
        assert not result.is_valid, "Extremely negative impact should be rejected"
        assert any("below minimum" in error for error in result.errors), \
            "Should have error about minimum fitness impact"
    
    def test_prevents_negative_fitness_result(self):
        """Test that mutations resulting in negative fitness are rejected"""
        mutation = Mutation(
            type=MutationType.AUTONOMY_ADJUSTMENT.value,
            description="Mutation causing negative fitness",
            fitness_impact=-150.0  # Would result in negative fitness
        )
        
        result = self.validator.validate(mutation, self.sample_dna)
        
        assert not result.is_valid, "Mutation causing negative fitness should be rejected"
        assert any("negative fitness" in error for error in result.errors), \
            "Should have error about negative fitness result"
    
    def test_description_validation(self):
        """Test mutation description validation"""
        # Test missing description
        mutation_no_desc = Mutation(
            type=MutationType.LANGUAGE_EXPANSION.value,
            description="",
            fitness_impact=3.0
        )
        
        result = self.validator.validate(mutation_no_desc, self.sample_dna)
        assert len(result.warnings) > 0, "Missing description should generate warning"
        
        # Test short description
        mutation_short_desc = Mutation(
            type=MutationType.LANGUAGE_EXPANSION.value,
            description="Short",
            fitness_impact=3.0
        )
        
        result = self.validator.validate(mutation_short_desc, self.sample_dna)
        assert len(result.warnings) > 0, "Short description should generate warning"
    
    def test_risk_score_validation(self):
        """Test risk score validation"""
        mutation = Mutation(
            type=MutationType.PROTOCOL_IMPROVEMENT.value,
            description="Test mutation without risk score",
            fitness_impact=2.0,
            risk_score=0.0  # Not calculated
        )
        
        result = self.validator.validate(mutation, self.sample_dna)
        assert len(result.warnings) > 0, "Missing risk score should generate warning"
    
    def test_check_invariants_communication_channels(self):
        """Test invariant checking for communication channels"""
        invalid_dna = SystemDNA(
            generation=1,
            fitness_score=50.0,
            core_traits=CoreTraits(
                communication_channels=0,  # Below minimum
                language_support=5,
                autonomy_level=0.5
            )
        )
        
        is_valid, violations = self.validator.check_invariants(invalid_dna)
        
        assert not is_valid, "DNA with zero communication channels should be invalid"
        assert any("Communication channels below minimum" in v for v in violations), \
            "Should have violation for communication channels"
    
    def test_check_invariants_autonomy_level(self):
        """Test invariant checking for autonomy level bounds"""
        # Test upper bound
        high_autonomy_dna = SystemDNA(
            generation=1,
            fitness_score=50.0,
            core_traits=CoreTraits(
                communication_channels=5,
                language_support=5,
                autonomy_level=1.5  # Above maximum
            )
        )
        
        is_valid, violations = self.validator.check_invariants(high_autonomy_dna)
        assert not is_valid, "DNA with autonomy level > 1.0 should be invalid"
        
        # Test lower bound
        low_autonomy_dna = SystemDNA(
            generation=1,
            fitness_score=50.0,
            core_traits=CoreTraits(
                communication_channels=5,
                language_support=5,
                autonomy_level=-0.1  # Below minimum
            )
        )
        
        is_valid, violations = self.validator.check_invariants(low_autonomy_dna)
        assert not is_valid, "DNA with negative autonomy level should be invalid"
    
    def test_check_invariants_fitness_score(self):
        """Test invariant checking for fitness score"""
        invalid_fitness_dna = SystemDNA(
            generation=1,
            fitness_score=-10.0,  # Below minimum
            core_traits=CoreTraits(
                communication_channels=5,
                language_support=5,
                autonomy_level=0.5
            )
        )
        
        is_valid, violations = self.validator.check_invariants(invalid_fitness_dna)
        
        assert not is_valid, "DNA with negative fitness should be invalid"
        assert any("Fitness score below minimum" in v for v in violations), \
            "Should have violation for negative fitness"
    
    def test_valid_dna_passes_invariants(self):
        """Test that valid DNA passes all invariant checks"""
        is_valid, violations = self.validator.check_invariants(self.sample_dna)
        
        assert is_valid, "Valid DNA should pass all invariant checks"
        assert len(violations) == 0, "Valid DNA should have no violations"