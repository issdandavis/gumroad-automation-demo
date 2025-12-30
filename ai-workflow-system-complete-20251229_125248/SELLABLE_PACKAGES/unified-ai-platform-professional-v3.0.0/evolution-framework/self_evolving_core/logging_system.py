"""
Logging System for Self-Evolving AI Framework
=============================================

Comprehensive logging with:
- Structured audit logging
- Evolution history tracking
- JSON and text format support
- Queryable audit trail
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(Enum):
    MUTATION = "mutation"
    STORAGE = "storage"
    AUTONOMY = "autonomy"
    HEALING = "healing"
    FITNESS = "fitness"
    SYSTEM = "system"
    SECURITY = "security"


@dataclass
class AuditEntry:
    """Single audit log entry"""
    id: str
    timestamp: str
    category: str
    action: str
    actor: str
    details: Dict[str, Any]
    level: str = "info"
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


@dataclass
class EvolutionEntry:
    """Evolution history entry"""
    generation: int
    timestamp: str
    mutation_type: str
    fitness_before: float
    fitness_after: float
    source_ai: str
    auto_approved: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditLogger:
    """
    Comprehensive audit logging for all system operations.
    
    Features:
    - Structured log entries with categories
    - Queryable audit trail
    - File and memory storage
    - JSON export for analysis
    """
    
    def __init__(self, log_path: str = "logs/audit.log", max_entries: int = 10000):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.entries: List[AuditEntry] = []
        self._load_recent()
    
    def _load_recent(self) -> None:
        """Load recent entries from file"""
        if not self.log_path.exists():
            return
        try:
            with open(self.log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.entries.append(AuditEntry(**data))
            self.entries = self.entries[-self.max_entries:]
        except Exception as e:
            logger.warning(f"Failed to load audit log: {e}")

    def log(self, category: str, action: str, actor: str = "system",
            details: Optional[Dict[str, Any]] = None, level: str = "info",
            success: bool = True, error: Optional[str] = None) -> AuditEntry:
        """Log an audit entry"""
        entry = AuditEntry(
            id=f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            category=category,
            action=action,
            actor=actor,
            details=details or {},
            level=level,
            success=success,
            error=error
        )
        
        self.entries.append(entry)
        self._write_entry(entry)
        
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        return entry
    
    def _write_entry(self, entry: AuditEntry) -> None:
        """Write entry to file"""
        try:
            with open(self.log_path, 'a') as f:
                f.write(entry.to_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit entry: {e}")
    
    def log_mutation(self, mutation_id: str, mutation_type: str, 
                    source_ai: str, auto_approved: bool,
                    fitness_impact: float, success: bool = True) -> AuditEntry:
        """Log mutation event"""
        return self.log(
            category=AuditCategory.MUTATION.value,
            action="apply_mutation",
            actor=source_ai,
            details={
                "mutation_id": mutation_id,
                "mutation_type": mutation_type,
                "auto_approved": auto_approved,
                "fitness_impact": fitness_impact
            },
            success=success
        )
    
    def log_storage(self, operation: str, platform: str, path: str,
                   success: bool = True, error: Optional[str] = None) -> AuditEntry:
        """Log storage operation"""
        return self.log(
            category=AuditCategory.STORAGE.value,
            action=operation,
            details={"platform": platform, "path": path},
            success=success,
            error=error
        )

    def log_autonomy(self, action: str, risk_score: float,
                    auto_approved: bool, details: Optional[Dict] = None) -> AuditEntry:
        """Log autonomy decision"""
        return self.log(
            category=AuditCategory.AUTONOMY.value,
            action=action,
            details={
                "risk_score": risk_score,
                "auto_approved": auto_approved,
                **(details or {})
            }
        )
    
    def log_healing(self, error_type: str, strategy: str,
                   success: bool, attempts: int) -> AuditEntry:
        """Log healing event"""
        return self.log(
            category=AuditCategory.HEALING.value,
            action="heal",
            details={
                "error_type": error_type,
                "strategy": strategy,
                "attempts": attempts
            },
            success=success
        )
    
    def query(self, category: Optional[str] = None, actor: Optional[str] = None,
             success: Optional[bool] = None, limit: int = 100) -> List[AuditEntry]:
        """Query audit entries with filters"""
        results = self.entries
        
        if category:
            results = [e for e in results if e.category == category]
        if actor:
            results = [e for e in results if e.actor == actor]
        if success is not None:
            results = [e for e in results if e.success == success]
        
        return results[-limit:]
    
    def get_recent(self, limit: int = 50) -> List[AuditEntry]:
        """Get recent entries"""
        return self.entries[-limit:]
    
    def export_json(self, path: str) -> None:
        """Export all entries to JSON file"""
        with open(path, 'w') as f:
            json.dump([e.to_dict() for e in self.entries], f, indent=2, default=str)


class EvolutionLog:
    """
    Tracks system evolution history.
    
    Features:
    - Generation-by-generation tracking
    - Fitness trend analysis
    - AI contribution tracking
    """
    
    def __init__(self, log_path: str = "logs/evolution.json"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[EvolutionEntry] = []
        self._load()

    def _load(self) -> None:
        """Load evolution history"""
        if not self.log_path.exists():
            return
        try:
            with open(self.log_path, 'r') as f:
                data = json.load(f)
                self.entries = [EvolutionEntry(**e) for e in data]
        except Exception as e:
            logger.warning(f"Failed to load evolution log: {e}")
    
    def _save(self) -> None:
        """Save evolution history"""
        try:
            with open(self.log_path, 'w') as f:
                json.dump([e.to_dict() for e in self.entries], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save evolution log: {e}")
    
    def record(self, generation: int, mutation_type: str,
              fitness_before: float, fitness_after: float,
              source_ai: str, auto_approved: bool,
              details: Optional[Dict] = None) -> EvolutionEntry:
        """Record evolution event"""
        entry = EvolutionEntry(
            generation=generation,
            timestamp=datetime.now().isoformat(),
            mutation_type=mutation_type,
            fitness_before=fitness_before,
            fitness_after=fitness_after,
            source_ai=source_ai,
            auto_approved=auto_approved,
            details=details or {}
        )
        self.entries.append(entry)
        self._save()
        return entry
    
    def get_fitness_trend(self, generations: int = 10) -> List[Dict[str, Any]]:
        """Get fitness trend over recent generations"""
        recent = self.entries[-generations:]
        return [
            {"generation": e.generation, "fitness": e.fitness_after, "timestamp": e.timestamp}
            for e in recent
        ]
    
    def get_ai_contributions(self) -> Dict[str, int]:
        """Get mutation count by AI source"""
        contributions = {}
        for entry in self.entries:
            ai = entry.source_ai
            contributions[ai] = contributions.get(ai, 0) + 1
        return contributions
    
    def get_mutation_stats(self) -> Dict[str, Any]:
        """Get mutation statistics"""
        if not self.entries:
            return {"total": 0, "by_type": {}, "avg_impact": 0}
        
        by_type = {}
        total_impact = 0
        
        for entry in self.entries:
            by_type[entry.mutation_type] = by_type.get(entry.mutation_type, 0) + 1
            total_impact += entry.fitness_after - entry.fitness_before
        
        return {
            "total": len(self.entries),
            "by_type": by_type,
            "avg_impact": total_impact / len(self.entries),
            "auto_approved_rate": sum(1 for e in self.entries if e.auto_approved) / len(self.entries)
        }
