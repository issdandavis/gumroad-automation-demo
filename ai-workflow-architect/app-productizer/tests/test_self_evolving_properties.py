"""
Property-Based Tests for Self-Evolving AI Framework
==================================================

Comprehensive property-based testing using Hypothesis to validate
universal properties that must hold across all valid system states.

These tests validate the core correctness properties defined in the
design document and ensure system reliability under all conditions.
"""

import os
import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from self_evolving_core.framework import EvolvingAIFramework
from self_evolving_core.models import SystemDNA, Mutation, MutationType


# -----------------------------
# Helpers / Strategies
# -----------------------------

def _make_framework(tmp_path: Path) -> EvolvingAIFramework:
    """
    Creates a framework instance whose local storage is isolated per-test.
    This ensures tests don't interfere with each other or production data.
    """
    # Set isolated storage path
    os.environ["AI_NETWORK_LOCAL"] = str(tmp_path / "AI_NETWORK_LOCAL")
    
    fw = EvolvingAIFramework()
    ok = fw.initialize()
    assert ok is True, "Framework initialization must succeed"
    return fw


# Mutation types as strings (Mutation model expects string "type")
mutation_type_strings = st.sampled_from([t.value for t in MutationType])

# Safe text generation avoiding problematic characters
safe_text = st.text(
    min_size=10,
    max_size=200,
    alphabet=st.characters(blacklist_categories=("Cs",)),
)

# Fitness impact within reasonable bounds
fitness_impact = st.floats(
    min_value=-10.0, 
    max_value=10.0, 
    allow_nan=False, 
    allow_infinity=False
)


# -----------------------------
# Property 1: DNA Initialization Completeness
# Validates: Requirements 1.1, 1.5
# -----------------------------

@given(seed=st.integers(min_value=0, max_value=10_000))
@settings(max_examples=30)
def test_property_dna_initialization_completeness(seed):
    """
    Property 1: DNA Initialization Completeness
    
    For any system initialization, the resulting SystemDNA must contain
    all required fields with valid values according to system invariants.
    
    **Validates: Requirements 1.1, 1.5**
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        dna = fw.get_dna()
        
        # Core field validation
        assert isinstance(dna, SystemDNA), "Must return SystemDNA instance"
        assert dna.version is not None, "Version must be set"
        assert dna.birth_timestamp is not None, "Birth timestamp must be set"
        assert dna.generation >= 1, "Generation must be at least 1"
        assert dna.core_traits is not None, "Core traits must be present"
        assert isinstance(dna.mutations, list), "Mutations must be a list"
        assert isinstance(dna.snapshots, list), "Snapshots must be a list"
        
        # Core traits validation
        traits = dna.core_traits
        assert traits.communication_channels >= 0, "Communication channels must be non-negative"
        assert traits.language_support >= 0, "Language support must be non-negative"
        assert 0 <= traits.autonomy_level <= 1, "Autonomy level must be between 0 and 1"
        assert isinstance(traits.evolutionary_features, list), "Evolutionary features must be a list"
        
        # Serialization round-trip validation
        payload = dna.to_dict()
        json.dumps(payload, default=str)  # Must be JSON serializable
        
        restored_dna = SystemDNA.from_dict(payload)
        assert restored_dna.generation == dna.generation, "Serialization must preserve generation"
        assert restored_dna.fitness_score == dna.fitness_score, "Serialization must preserve fitness"


# -----------------------------
# Property 2: Mutation Logging Consistency
# Validates: Requirements 1.2, 3.4
# -----------------------------

@given(
    mtype=mutation_type_strings,
    desc=safe_text,
    impact=fitness_impact
)
@settings(max_examples=40)
def test_property_mutation_logging_consistency(mtype, desc, impact):
    """
    Property 2: Mutation Logging Consistency
    
    For any mutation applied to the system, the Evolution_Log must contain
    a complete record with all required fields within the mutation process.
    
    **Validates: Requirements 1.2, 3.4**
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        # Capture initial state
        before = fw.get_dna()
        before_gen = before.generation
        before_count = len(before.mutations)
        before_fitness = before.fitness_score
        
        # Create mutation
        mutation = Mutation(
            type=mtype,
            description=desc,
            fitness_impact=float(impact),
            source_ai="property_test"
        )
        
        # Propose mutation
        result = fw.propose_mutation(mutation)
        
        # If auto-approved and applied, DNA should reflect it consistently
        if result.get("approved") and result.get("auto"):
            after = fw.get_dna()
            
            # Generation and mutation count must increment by exactly 1
            assert after.generation == before_gen + 1, "Generation must increment by 1"
            assert len(after.mutations) == before_count + 1, "Mutations count must increment by 1"
            
            # Latest mutation record must have complete information
            last = after.mutations[-1]
            assert last.type == mtype, "Mutation type must be logged correctly"
            assert last.description == desc, "Description must be logged correctly"
            assert last.source_ai == "property_test", "Source AI must be logged correctly"
            assert last.timestamp is not None, "Timestamp must be recorded"
            assert last.id is not None, "Mutation ID must be assigned"
            
            # Fitness tracking must align with mutation impact
            expected_fitness = before_fitness + float(impact)
            assert after.fitness_score == pytest.approx(expected_fitness, rel=1e-6, abs=1e-6), \
                f"Fitness must change by impact amount"
        else:
            # If not approved, DNA must not mutate
            after = fw.get_dna()
            assert after.generation == before_gen, "Generation must not change if not approved"
            assert len(after.mutations) == before_count, "Mutations count must not change if not approved"
            assert after.fitness_score == before_fitness, "Fitness must not change if not approved"


# -----------------------------
# Property 3: Fitness Score Tracking
# Validates: Requirements 1.3, 9.2
# -----------------------------

@given(impacts=st.lists(fitness_impact, min_size=1, max_size=8))
@settings(max_examples=25, deadline=None)
def test_property_fitness_score_tracking(impacts):
    """
    Property 3: Fitness Score Tracking
    
    For any sequence of mutations, the fitness score changes must equal
    the sum of all applied mutation impacts.
    
    **Validates: Requirements 1.3, 9.2**
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        dna = fw.get_dna()
        start_fitness = dna.fitness_score
        expected_fitness = start_fitness
        start_gen = dna.generation
        
        applied_count = 0
        
        for i, impact in enumerate(impacts):
            mutation = Mutation(
                type=MutationType.PROTOCOL_IMPROVEMENT.value,
                description=f"property fitness tracking #{i}",
                fitness_impact=float(impact),
                source_ai="property_test"
            )
            
            result = fw.propose_mutation(mutation)
            
            if result.get("approved") and result.get("auto"):
                applied_count += 1
                expected_fitness += float(impact)
        
        final_dna = fw.get_dna()
        assert final_dna.generation == start_gen + applied_count, \
            f"Generation must increment by applied mutations"
        assert final_dna.fitness_score == pytest.approx(expected_fitness, rel=1e-6, abs=1e-6), \
            f"Fitness must equal sum of impacts"


# -----------------------------
# Property 4: Generation Invariant
# Validates: Requirements 1.4
# -----------------------------

@given(
    actions=st.lists(
        st.sampled_from(["status", "fitness", "sync"]), 
        min_size=1, 
        max_size=12
    )
)
@settings(max_examples=30)
def test_property_generation_invariant(actions):
    """
    Property 4: Generation Invariant
    
    For any sequence of non-mutating operations, the generation counter
    must remain unchanged. Only mutations should increment generation.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        dna = fw.get_dna()
        start_gen = dna.generation
        
        for action in actions:
            if action == "status":
                fw.get_status()
            elif action == "fitness":
                fw.get_fitness()
            elif action == "sync":
                fw.sync_storage({"test": "data"}, "property_sync.json")
        
        final_dna = fw.get_dna()
        assert final_dna.generation == start_gen, \
            f"Generation must not change for non-mutating operations"


# -----------------------------
# Property 12: Rollback Completeness
# Validates: Requirements 8.7
# -----------------------------

@given(impact=fitness_impact)
@settings(max_examples=20)
def test_property_rollback_completeness(impact):
    """
    Property 12: Rollback Completeness
    
    For any mutation followed by rollback, the system must be restored
    to the exact state captured in the pre-mutation snapshot.
    
    **Validates: Requirements 8.7**
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        dna0 = fw.get_dna()
        gen0 = dna0.generation
        fit0 = dna0.fitness_score
        
        mutation = Mutation(
            type=MutationType.AUTONOMY_ADJUSTMENT.value,
            description="rollback property test mutation",
            fitness_impact=float(impact),
            source_ai="property_test"
        )
        
        result = fw.propose_mutation(mutation)
        
        if not (result.get("approved") and result.get("auto")):
            dna1 = fw.get_dna()
            assert dna1.generation == gen0, "Generation must not change if mutation not applied"
            assert dna1.fitness_score == fit0, "Fitness must not change if mutation not applied"
            return
        
        dna_after_mutation = fw.get_dna()
        assert dna_after_mutation.generation == gen0 + 1, "Mutation must have been applied"
        
        snapshots = fw.rollback.list_snapshots(10)
        assert len(snapshots) > 0, "Rollback snapshots must be available"
        
        latest_snapshot = snapshots[0]
        rollback_result = fw.rollback_to(latest_snapshot.id)
        assert rollback_result.get("success") is True, "Rollback operation must succeed"
        
        dna_after_rollback = fw.get_dna()
        
        restored_gen = rollback_result.get("restored_generation")
        if restored_gen is not None:
            assert dna_after_rollback.generation == restored_gen, \
                f"Generation must be restored to snapshot value"
        
        assert dna_after_rollback.generation < dna_after_mutation.generation, \
            "Rollback must reduce generation from post-mutation state"


# -----------------------------
# Additional Property Tests
# -----------------------------

@given(
    mutation_count=st.integers(min_value=1, max_value=5),
    mutation_types=st.lists(mutation_type_strings, min_size=1, max_size=5)
)
@settings(max_examples=15)
def test_property_mutation_sequence_consistency(mutation_count, mutation_types):
    """
    Property: Mutation Sequence Consistency
    
    For any sequence of mutations, the system must maintain consistency
    in generation increments and mutation logging.
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        initial_dna = fw.get_dna()
        initial_gen = initial_dna.generation
        initial_mutations = len(initial_dna.mutations)
        
        applied_mutations = 0
        
        for i in range(min(mutation_count, len(mutation_types))):
            mutation = Mutation(
                type=mutation_types[i],
                description=f"Sequence test mutation {i}",
                fitness_impact=1.0,
                source_ai="sequence_test"
            )
            
            result = fw.propose_mutation(mutation)
            if result.get("approved") and result.get("auto"):
                applied_mutations += 1
        
        final_dna = fw.get_dna()
        
        assert final_dna.generation == initial_gen + applied_mutations, \
            "Generation must increment by number of applied mutations"
        assert len(final_dna.mutations) == initial_mutations + applied_mutations, \
            "Mutations list must grow by number of applied mutations"


@given(
    sync_data=st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=20)
def test_property_storage_sync_idempotency(sync_data):
    """
    Property: Storage Sync Idempotency
    
    For any data, syncing multiple times should not change the final
    stored result or system state.
    """
    with tempfile.TemporaryDirectory() as d:
        fw = _make_framework(Path(d))
        
        initial_dna = fw.get_dna()
        
        filename = "idempotency_test.json"
        
        result1 = fw.sync_storage(sync_data, filename)
        result2 = fw.sync_storage(sync_data, filename)
        result3 = fw.sync_storage(sync_data, filename)
        
        assert result1.get("local", {}).get("success"), "First sync must succeed"
        assert result2.get("local", {}).get("success"), "Second sync must succeed"
        assert result3.get("local", {}).get("success"), "Third sync must succeed"
        
        final_dna = fw.get_dna()
        assert final_dna.generation == initial_dna.generation, \
            "Syncing must not change generation"
        assert final_dna.fitness_score == initial_dna.fitness_score, \
            "Syncing must not change fitness score"
        
        data_dir = Path(os.environ.get("AI_NETWORK_LOCAL", "AI_NETWORK_LOCAL"))
        sync_file = data_dir / filename
        assert sync_file.exists(), "Sync file must be created"
        
        with open(sync_file, 'r') as f:
            stored_data = json.load(f)
            for key, value in sync_data.items():
                assert key in stored_data, f"Key {key} must be in stored data"
                assert stored_data[key] == value, f"Value for {key} must match"
