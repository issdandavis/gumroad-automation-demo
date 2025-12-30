"""
Rollback Manager for Self-Evolving AI Framework
===============================================

Manages system state snapshots and rollback capabilities with:
- Timestamped snapshots before mutations
- Field-by-field verification
- Automatic cleanup of old snapshots
- Multi-level rollback support
"""

import logging
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict

from .models import SystemDNA, Snapshot

logger = logging.getLogger(__name__)


@dataclass
class RollbackResult:
    """Result of rollback operation"""
    success: bool
    snapshot_id: str
    restored_generation: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None
    verification_passed: bool = False


class RollbackManager:
    """
    Manages system state snapshots and rollback operations.
    
    Features:
    - Create snapshots before risky operations
    - Restore to any previous snapshot
    - Verify rollback completeness
    - Automatic cleanup of old snapshots
    - Multi-level rollback chain
    """
    
    MAX_SNAPSHOTS = 50
    
    def __init__(self, storage_path: str = "AI_NETWORK_LOCAL/snapshots"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.snapshots: Dict[str, Snapshot] = {}
        self._load_snapshots()
        
        logger.info(f"RollbackManager initialized with {len(self.snapshots)} snapshots")
    
    def _load_snapshots(self) -> None:
        """Load existing snapshots from storage"""
        try:
            for file_path in self.storage_path.glob("snapshot_*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        snapshot = Snapshot.from_dict(data)
                        self.snapshots[snapshot.id] = snapshot
                except Exception as e:
                    logger.warning(f"Failed to load snapshot {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to load snapshots: {e}")
    
    def create_snapshot(self, dna: SystemDNA, label: str = "") -> Snapshot:
        """
        Create a snapshot of current system state.
        
        Args:
            dna: Current SystemDNA to snapshot
            label: Human-readable label for the snapshot
            
        Returns:
            Created Snapshot object
        """
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        snapshot = Snapshot(
            id=snapshot_id,
            timestamp=datetime.now().isoformat(),
            label=label or f"Snapshot at generation {dna.generation}",
            dna_checksum=dna.get_checksum(),
            dna_data=dna.to_dict(),
            metadata={
                "generation": dna.generation,
                "fitness_score": dna.fitness_score,
                "mutation_count": len(dna.mutations)
            }
        )
        
        # Save to storage
        self._save_snapshot(snapshot)
        self.snapshots[snapshot_id] = snapshot
        
        # Cleanup old snapshots if needed
        self._cleanup_old_snapshots()
        
        logger.info(f"Created snapshot: {snapshot_id} (gen {dna.generation})")
        return snapshot
    
    def _save_snapshot(self, snapshot: Snapshot) -> None:
        """Save snapshot to storage"""
        file_path = self.storage_path / f"snapshot_{snapshot.id}.json"
        with open(file_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2, default=str)
    
    def rollback(self, dna_manager, snapshot_id: str) -> RollbackResult:
        """
        Restore system to a previous snapshot.
        
        Args:
            dna_manager: DNAManager to restore to
            snapshot_id: ID of snapshot to restore
            
        Returns:
            RollbackResult with operation details
        """
        if snapshot_id not in self.snapshots:
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                restored_generation=0,
                error=f"Snapshot not found: {snapshot_id}"
            )
        
        snapshot = self.snapshots[snapshot_id]
        
        try:
            # Restore DNA from snapshot
            restored_dna = SystemDNA.from_dict(snapshot.dna_data)
            
            # Save restored DNA
            if dna_manager:
                dna_manager.save(restored_dna)
            
            # Verify rollback
            verification = self.verify_rollback(restored_dna, snapshot)
            
            logger.info(f"Rolled back to snapshot: {snapshot_id} (gen {restored_dna.generation})")
            
            return RollbackResult(
                success=True,
                snapshot_id=snapshot_id,
                restored_generation=restored_dna.generation,
                verification_passed=verification
            )
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return RollbackResult(
                success=False,
                snapshot_id=snapshot_id,
                restored_generation=0,
                error=str(e)
            )
    
    def rollback_by_id(self, snapshot_id: str) -> Optional[SystemDNA]:
        """
        Get DNA from snapshot without applying (for manual restoration).
        
        Args:
            snapshot_id: ID of snapshot to retrieve
            
        Returns:
            SystemDNA from snapshot or None if not found
        """
        if snapshot_id not in self.snapshots:
            return None
        
        snapshot = self.snapshots[snapshot_id]
        return SystemDNA.from_dict(snapshot.dna_data)
    
    def rollback_to_generation(self, dna_manager, target_generation: int) -> RollbackResult:
        """
        Rollback to a specific generation number.
        
        Args:
            dna_manager: DNAManager to restore to
            target_generation: Generation number to restore to
            
        Returns:
            RollbackResult with operation details
        """
        # Find snapshot with matching generation
        matching_snapshots = [
            s for s in self.snapshots.values()
            if s.metadata.get("generation") == target_generation
        ]
        
        if not matching_snapshots:
            return RollbackResult(
                success=False,
                snapshot_id="",
                restored_generation=0,
                error=f"No snapshot found for generation {target_generation}"
            )
        
        # Use most recent matching snapshot
        snapshot = max(matching_snapshots, key=lambda s: s.timestamp)
        return self.rollback(dna_manager, snapshot.id)
    
    def verify_rollback(self, restored_dna: SystemDNA, snapshot: Snapshot) -> bool:
        """
        Verify rollback completeness with field-by-field comparison.
        
        Args:
            restored_dna: DNA after restoration
            snapshot: Original snapshot
            
        Returns:
            True if verification passed
        """
        # Verify checksum
        if restored_dna.get_checksum() != snapshot.dna_checksum:
            logger.warning("Rollback verification failed: checksum mismatch")
            return False
        
        # Verify key fields
        original = snapshot.dna_data
        restored = restored_dna.to_dict()
        
        critical_fields = ["version", "generation", "fitness_score"]
        for field in critical_fields:
            if original.get(field) != restored.get(field):
                logger.warning(f"Rollback verification failed: {field} mismatch")
                return False
        
        return True
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get snapshot by ID"""
        return self.snapshots.get(snapshot_id)
    
    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Get most recent snapshot"""
        if not self.snapshots:
            return None
        return max(self.snapshots.values(), key=lambda s: s.timestamp)
    
    def get_snapshots_for_generation(self, generation: int) -> List[Snapshot]:
        """Get all snapshots for a specific generation"""
        return [
            s for s in self.snapshots.values()
            if s.metadata.get("generation") == generation
        ]
    
    def list_snapshots(self, limit: int = 20) -> List[Snapshot]:
        """List recent snapshots"""
        sorted_snapshots = sorted(
            self.snapshots.values(),
            key=lambda s: s.timestamp,
            reverse=True
        )
        return sorted_snapshots[:limit]
    
    def _cleanup_old_snapshots(self) -> int:
        """
        Remove old snapshots beyond retention limit.
        
        Returns:
            Number of snapshots removed
        """
        if len(self.snapshots) <= self.MAX_SNAPSHOTS:
            return 0
        
        # Sort by timestamp, oldest first
        sorted_snapshots = sorted(
            self.snapshots.values(),
            key=lambda s: s.timestamp
        )
        
        # Remove oldest snapshots
        to_remove = len(self.snapshots) - self.MAX_SNAPSHOTS
        removed = 0
        
        for snapshot in sorted_snapshots[:to_remove]:
            try:
                # Delete file
                file_path = self.storage_path / f"snapshot_{snapshot.id}.json"
                if file_path.exists():
                    file_path.unlink()
                
                # Remove from memory
                del self.snapshots[snapshot.id]
                removed += 1
                
            except Exception as e:
                logger.warning(f"Failed to remove snapshot {snapshot.id}: {e}")
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old snapshots")
        
        return removed
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a specific snapshot"""
        if snapshot_id not in self.snapshots:
            return False
        
        try:
            file_path = self.storage_path / f"snapshot_{snapshot_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            del self.snapshots[snapshot_id]
            logger.info(f"Deleted snapshot: {snapshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            return False
    
    def get_rollback_chain(self, current_dna: SystemDNA) -> List[Dict[str, Any]]:
        """
        Get chain of possible rollback points from current state.
        
        Returns list of snapshots with metadata for UI display.
        """
        chain = []
        
        for snapshot in self.list_snapshots(limit=20):
            gen = snapshot.metadata.get("generation", 0)
            if gen < current_dna.generation:
                chain.append({
                    "snapshot_id": snapshot.id,
                    "timestamp": snapshot.timestamp,
                    "label": snapshot.label,
                    "generation": gen,
                    "fitness_score": snapshot.metadata.get("fitness_score", 0),
                    "generations_back": current_dna.generation - gen
                })
        
        return chain
