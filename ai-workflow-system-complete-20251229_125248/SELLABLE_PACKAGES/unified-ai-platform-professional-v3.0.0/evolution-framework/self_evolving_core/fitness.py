"""
Fitness Monitor for Self-Evolving AI Framework
==============================================

Tracks system performance and triggers optimization with:
- Multi-metric fitness calculation
- Degradation detection with trend analysis
- Automatic optimization suggestions
- Dashboard-ready data export
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import statistics

from .models import FitnessScore, DegradationAlert, Mutation, OperationResult

logger = logging.getLogger(__name__)


@dataclass
class MetricDataPoint:
    """Single metric measurement"""
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""
    operation_type: str
    success: bool
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cost: float = 0.0
    error: Optional[str] = None


class FitnessMonitor:
    """
    Monitors system fitness and triggers optimization.
    
    Metrics tracked:
    - Success rate: % of successful operations
    - Healing speed: Time from error to resolution
    - Cost efficiency: Operations per dollar
    - Uptime: % of operational time
    
    Features:
    - Rolling window calculations
    - Trend detection
    - Automatic degradation alerts
    - Optimization suggestions
    """
    
    METRICS = ['success_rate', 'healing_speed', 'cost_efficiency', 'uptime']
    
    def __init__(self, config=None):
        self.config = config
        
        # Metric weights for overall fitness
        self.weights = {
            'success_rate': 0.4,
            'healing_speed': 0.2,
            'cost_efficiency': 0.2,
            'uptime': 0.2
        }
        if config and hasattr(config, 'fitness_weights'):
            self.weights.update(config.fitness_weights)
        
        # Degradation thresholds
        self.degradation_threshold = 5.0  # percent
        self.degradation_window_hours = 1.0
        if config:
            self.degradation_threshold = getattr(config, 'degradation_threshold_percent', 5.0)
            self.degradation_window_hours = getattr(config, 'degradation_window_hours', 1.0)
        
        # Metric history (rolling windows)
        self.max_history = 1000
        self.operations: deque = deque(maxlen=self.max_history)
        self.fitness_history: deque = deque(maxlen=self.max_history)
        self.healing_events: deque = deque(maxlen=100)
        
        # Uptime tracking
        self.start_time = datetime.now()
        self.downtime_seconds = 0.0
        self.last_health_check = datetime.now()
        
        # Cost tracking
        self.total_cost = 0.0
        self.total_operations = 0
        
        logger.info("FitnessMonitor initialized")
    
    def record_operation(self, operation: OperationMetrics) -> None:
        """Record operation outcome for fitness calculation"""
        self.operations.append(operation)
        self.total_operations += 1
        self.total_cost += operation.cost
        
        # Check for degradation after recording
        self._check_degradation()
    
    def record_operation_result(self, result: OperationResult) -> None:
        """Record from OperationResult model"""
        metrics = OperationMetrics(
            operation_type=result.operation_type,
            success=result.success,
            duration_ms=result.duration_ms,
            timestamp=result.timestamp,
            error=result.error
        )
        self.record_operation(metrics)
    
    def record_healing_event(self, error_time: datetime, resolution_time: datetime,
                            error_type: str, resolution_method: str) -> None:
        """Record self-healing event"""
        healing_time = (resolution_time - error_time).total_seconds()
        
        self.healing_events.append({
            'error_time': error_time.isoformat(),
            'resolution_time': resolution_time.isoformat(),
            'healing_time_seconds': healing_time,
            'error_type': error_type,
            'resolution_method': resolution_method
        })
    
    def record_downtime(self, duration_seconds: float) -> None:
        """Record system downtime"""
        self.downtime_seconds += duration_seconds
    
    def calculate_fitness(self) -> FitnessScore:
        """Calculate current fitness from all metrics"""
        metrics = self._calculate_metrics()
        
        # Calculate weighted overall score
        overall = sum(
            metrics[metric] * self.weights[metric] * 100
            for metric in self.METRICS
        )
        
        # Determine trend
        trend = self._calculate_trend()
        
        score = FitnessScore(
            overall=round(overall, 2),
            success_rate=metrics['success_rate'],
            healing_speed=metrics['healing_speed'],
            cost_efficiency=metrics['cost_efficiency'],
            uptime=metrics['uptime'],
            trend=trend,
            components=metrics
        )
        
        self.fitness_history.append({
            'timestamp': score.timestamp,
            'overall': score.overall,
            'metrics': metrics
        })
        
        return score
    
    def _calculate_metrics(self) -> Dict[str, float]:
        """Calculate individual metrics"""
        metrics = {}
        
        # Success rate
        if self.operations:
            successful = sum(1 for op in self.operations if op.success)
            metrics['success_rate'] = successful / len(self.operations)
        else:
            metrics['success_rate'] = 1.0
        
        # Healing speed (average seconds to heal)
        if self.healing_events:
            healing_times = [e['healing_time_seconds'] for e in self.healing_events]
            avg_healing = statistics.mean(healing_times)
            # Normalize: 0 seconds = 1.0, 60+ seconds = 0.0
            metrics['healing_speed'] = max(0, 1 - (avg_healing / 60))
        else:
            metrics['healing_speed'] = 1.0
        
        # Cost efficiency (operations per dollar, normalized)
        if self.total_cost > 0:
            ops_per_dollar = self.total_operations / self.total_cost
            # Normalize: 100+ ops/dollar = 1.0, 0 = 0.0
            metrics['cost_efficiency'] = min(1.0, ops_per_dollar / 100)
        else:
            metrics['cost_efficiency'] = 1.0  # No cost = perfect efficiency
        
        # Uptime
        total_time = (datetime.now() - self.start_time).total_seconds()
        if total_time > 0:
            uptime = (total_time - self.downtime_seconds) / total_time
            metrics['uptime'] = max(0, min(1, uptime))
        else:
            metrics['uptime'] = 1.0
        
        return metrics
    
    def _calculate_trend(self) -> str:
        """Calculate fitness trend from history"""
        if len(self.fitness_history) < 2:
            return "stable"
        
        # Get recent scores
        recent = list(self.fitness_history)[-10:]
        if len(recent) < 2:
            return "stable"
        
        # Calculate trend
        first_half = statistics.mean([r['overall'] for r in recent[:len(recent)//2]])
        second_half = statistics.mean([r['overall'] for r in recent[len(recent)//2:]])
        
        diff_percent = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        
        if diff_percent > 2:
            return "improving"
        elif diff_percent < -2:
            return "degrading"
        else:
            return "stable"
    
    def _check_degradation(self) -> None:
        """Check for performance degradation"""
        alert = self.detect_degradation()
        if alert:
            logger.warning(f"Degradation detected: {alert.metric} dropped {alert.degradation_percent:.1f}%")
    
    def detect_degradation(self) -> Optional[DegradationAlert]:
        """
        Detect performance degradation trends.
        
        Returns alert if any metric dropped more than threshold
        over the configured window.
        """
        if len(self.fitness_history) < 2:
            return None
        
        window_start = datetime.now() - timedelta(hours=self.degradation_window_hours)
        
        # Get scores in window
        recent_scores = [
            h for h in self.fitness_history
            if datetime.fromisoformat(h['timestamp']) >= window_start
        ]
        
        if len(recent_scores) < 2:
            return None
        
        # Check each metric
        for metric in self.METRICS:
            values = [h['metrics'].get(metric, 0) for h in recent_scores]
            if not values:
                continue
            
            first_value = values[0]
            last_value = values[-1]
            
            if first_value > 0:
                change_percent = ((last_value - first_value) / first_value) * 100
                
                if change_percent < -self.degradation_threshold:
                    return DegradationAlert(
                        metric=metric,
                        current_value=last_value,
                        threshold=self.degradation_threshold,
                        degradation_percent=abs(change_percent),
                        suggested_action=self._suggest_action(metric)
                    )
        
        return None
    
    def _suggest_action(self, metric: str) -> str:
        """Suggest action for degraded metric"""
        suggestions = {
            'success_rate': "Review recent errors and apply targeted fixes",
            'healing_speed': "Optimize self-healing strategies or add new recovery methods",
            'cost_efficiency': "Review API usage and optimize expensive operations",
            'uptime': "Investigate stability issues and add redundancy"
        }
        return suggestions.get(metric, "Investigate and optimize")
    
    def suggest_optimization(self, degradation: DegradationAlert) -> Mutation:
        """Generate optimization mutation for degradation"""
        from .models import Mutation
        
        mutation_types = {
            'success_rate': 'protocol_improvement',
            'healing_speed': 'intelligence_upgrade',
            'cost_efficiency': 'storage_optimization',
            'uptime': 'communication_enhancement'
        }
        
        return Mutation(
            type=mutation_types.get(degradation.metric, 'protocol_improvement'),
            description=f"Auto-optimization for {degradation.metric} degradation: {degradation.suggested_action}",
            fitness_impact=degradation.degradation_percent * 0.5,  # Aim to recover half
            risk_score=0.2,  # Low risk for auto-optimizations
            source_ai="FitnessMonitor",
            metadata={
                'trigger': 'degradation_detection',
                'metric': degradation.metric,
                'degradation_percent': degradation.degradation_percent
            }
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard"""
        current_fitness = self.calculate_fitness()
        
        # Recent operations summary
        recent_ops = list(self.operations)[-100:]
        ops_by_type = {}
        for op in recent_ops:
            if op.operation_type not in ops_by_type:
                ops_by_type[op.operation_type] = {'total': 0, 'success': 0}
            ops_by_type[op.operation_type]['total'] += 1
            if op.success:
                ops_by_type[op.operation_type]['success'] += 1
        
        # Fitness history for charts
        history_data = [
            {'timestamp': h['timestamp'], 'overall': h['overall']}
            for h in list(self.fitness_history)[-50:]
        ]
        
        return {
            'current_fitness': current_fitness.to_dict(),
            'trend': current_fitness.trend,
            'operations_summary': {
                'total': self.total_operations,
                'by_type': ops_by_type,
                'recent_count': len(recent_ops)
            },
            'healing_summary': {
                'total_events': len(self.healing_events),
                'avg_healing_time': statistics.mean(
                    [e['healing_time_seconds'] for e in self.healing_events]
                ) if self.healing_events else 0
            },
            'cost_summary': {
                'total_cost': self.total_cost,
                'cost_per_operation': self.total_cost / self.total_operations if self.total_operations > 0 else 0
            },
            'uptime': {
                'total_seconds': (datetime.now() - self.start_time).total_seconds(),
                'downtime_seconds': self.downtime_seconds,
                'percentage': current_fitness.uptime * 100
            },
            'fitness_history': history_data,
            'degradation_alert': self.detect_degradation()
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (for testing or new session)"""
        self.operations.clear()
        self.fitness_history.clear()
        self.healing_events.clear()
        self.start_time = datetime.now()
        self.downtime_seconds = 0.0
        self.total_cost = 0.0
        self.total_operations = 0
        logger.info("Fitness metrics reset")
