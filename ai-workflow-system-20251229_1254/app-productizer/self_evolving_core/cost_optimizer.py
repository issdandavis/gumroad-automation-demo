"""
Cost Optimization and Monitoring
================================

Comprehensive cost tracking, budget enforcement, and optimization
for AWS Bedrock AI Evolution System.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class CostCategory(Enum):
    """Cost categories for tracking"""
    BEDROCK_LLM = "bedrock_llm"
    S3_STORAGE = "s3_storage"
    DYNAMODB = "dynamodb"
    LAMBDA = "lambda"
    CLOUDWATCH = "cloudwatch"
    DATA_TRANSFER = "data_transfer"
    OTHER = "other"


class BudgetPeriod(Enum):
    """Budget tracking periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class CostEntry:
    """Individual cost entry"""
    timestamp: datetime
    category: str
    service: str
    operation: str
    amount_usd: float
    tokens_used: int = 0
    requests_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "category": self.category,
            "service": self.service,
            "operation": self.operation,
            "amount_usd": self.amount_usd,
            "tokens_used": self.tokens_used,
            "requests_count": self.requests_count,
            "metadata": self.metadata
        }


@dataclass
class BudgetAlert:
    """Budget alert configuration"""
    threshold_percent: float
    alert_type: str  # warning, critical, emergency
    actions: List[str]
    notification_channels: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "threshold_percent": self.threshold_percent,
            "alert_type": self.alert_type,
            "actions": self.actions,
            "notification_channels": self.notification_channels
        }


@dataclass
class BudgetStatus:
    """Current budget status"""
    period: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    usage_percent: float
    projected_spend: float
    days_remaining: int
    on_track: bool
    alerts_triggered: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "period": self.period,
            "budget_amount": self.budget_amount,
            "spent_amount": self.spent_amount,
            "remaining_amount": self.remaining_amount,
            "usage_percent": self.usage_percent,
            "projected_spend": self.projected_spend,
            "days_remaining": self.days_remaining,
            "on_track": self.on_track,
            "alerts_triggered": self.alerts_triggered
        }


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    category: str
    description: str
    potential_savings_usd: float
    potential_savings_percent: float
    implementation_effort: str  # low, medium, high
    risk_level: str  # low, medium, high
    actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "potential_savings_usd": self.potential_savings_usd,
            "potential_savings_percent": self.potential_savings_percent,
            "implementation_effort": self.implementation_effort,
            "risk_level": self.risk_level,
            "actions": self.actions
        }


class CostTracker:
    """Tracks costs across all AWS services"""
    
    def __init__(self, storage_path: str = "AI_NETWORK_LOCAL"):
        self.storage_path = storage_path
        self.cost_entries: List[CostEntry] = []
        self.daily_totals: Dict[str, float] = {}
        self.monthly_totals: Dict[str, float] = {}
        
        # Load existing data
        self._load_cost_data()
    
    def record_cost(self, category: str, service: str, operation: str, 
                   amount_usd: float, tokens_used: int = 0, 
                   metadata: Dict[str, Any] = None) -> None:
        """Record a cost entry"""
        
        entry = CostEntry(
            timestamp=datetime.now(),
            category=category,
            service=service,
            operation=operation,
            amount_usd=amount_usd,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )
        
        self.cost_entries.append(entry)
        self._update_totals(entry)
        self._save_cost_data()
        
        logger.debug(f"Recorded cost: {service}.{operation} = ${amount_usd:.6f}")
    
    def record_bedrock_cost(self, model_id: str, tokens_input: int, 
                           tokens_output: int, cost_per_1k_input: float,
                           cost_per_1k_output: float) -> float:
        """Record Bedrock LLM cost"""
        
        input_cost = (tokens_input / 1000) * cost_per_1k_input
        output_cost = (tokens_output / 1000) * cost_per_1k_output
        total_cost = input_cost + output_cost
        
        self.record_cost(
            category=CostCategory.BEDROCK_LLM.value,
            service="bedrock",
            operation=f"invoke_{model_id.split('.')[-1]}",
            amount_usd=total_cost,
            tokens_used=tokens_input + tokens_output,
            metadata={
                "model_id": model_id,
                "tokens_input": tokens_input,
                "tokens_output": tokens_output,
                "cost_input": input_cost,
                "cost_output": output_cost
            }
        )
        
        return total_cost
    
    def get_daily_spend(self, date: datetime = None) -> float:
        """Get total spend for a specific day"""
        
        if date is None:
            date = datetime.now()
        
        date_key = date.strftime("%Y-%m-%d")
        return self.daily_totals.get(date_key, 0.0)
    
    def get_monthly_spend(self, year: int = None, month: int = None) -> float:
        """Get total spend for a specific month"""
        
        if year is None or month is None:
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        month_key = f"{year}-{month:02d}"
        return self.monthly_totals.get(month_key, 0.0)
    
    def get_spend_by_category(self, days: int = 30) -> Dict[str, float]:
        """Get spending breakdown by category"""
        
        cutoff = datetime.now() - timedelta(days=days)
        category_totals = {}
        
        for entry in self.cost_entries:
            if entry.timestamp >= cutoff:
                category = entry.category
                category_totals[category] = category_totals.get(category, 0) + entry.amount_usd
        
        return category_totals
    
    def get_spend_by_service(self, days: int = 30) -> Dict[str, float]:
        """Get spending breakdown by service"""
        
        cutoff = datetime.now() - timedelta(days=days)
        service_totals = {}
        
        for entry in self.cost_entries:
            if entry.timestamp >= cutoff:
                service = entry.service
                service_totals[service] = service_totals.get(service, 0) + entry.amount_usd
        
        return service_totals
    
    def get_token_efficiency(self, days: int = 30) -> Dict[str, float]:
        """Get cost per token by service"""
        
        cutoff = datetime.now() - timedelta(days=days)
        service_costs = {}
        service_tokens = {}
        
        for entry in self.cost_entries:
            if entry.timestamp >= cutoff and entry.tokens_used > 0:
                service = entry.service
                service_costs[service] = service_costs.get(service, 0) + entry.amount_usd
                service_tokens[service] = service_tokens.get(service, 0) + entry.tokens_used
        
        efficiency = {}
        for service in service_costs:
            if service_tokens[service] > 0:
                efficiency[service] = service_costs[service] / service_tokens[service]
        
        return efficiency
    
    def _update_totals(self, entry: CostEntry) -> None:
        """Update daily and monthly totals"""
        
        date_key = entry.timestamp.strftime("%Y-%m-%d")
        month_key = entry.timestamp.strftime("%Y-%m")
        
        self.daily_totals[date_key] = self.daily_totals.get(date_key, 0) + entry.amount_usd
        self.monthly_totals[month_key] = self.monthly_totals.get(month_key, 0) + entry.amount_usd
    
    def _load_cost_data(self) -> None:
        """Load cost data from storage"""
        
        try:
            cost_file = f"{self.storage_path}/cost_tracking.json"
            with open(cost_file, 'r') as f:
                data = json.load(f)
                
                # Load entries
                for entry_data in data.get("entries", []):
                    entry = CostEntry(
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        category=entry_data["category"],
                        service=entry_data["service"],
                        operation=entry_data["operation"],
                        amount_usd=entry_data["amount_usd"],
                        tokens_used=entry_data.get("tokens_used", 0),
                        metadata=entry_data.get("metadata", {})
                    )
                    self.cost_entries.append(entry)
                
                # Load totals
                self.daily_totals = data.get("daily_totals", {})
                self.monthly_totals = data.get("monthly_totals", {})
                
        except FileNotFoundError:
            logger.info("No existing cost data found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load cost data: {e}")
    
    def _save_cost_data(self) -> None:
        """Save cost data to storage"""
        
        try:
            cost_file = f"{self.storage_path}/cost_tracking.json"
            
            data = {
                "entries": [entry.to_dict() for entry in self.cost_entries[-1000:]],  # Keep last 1000
                "daily_totals": self.daily_totals,
                "monthly_totals": self.monthly_totals,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(cost_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cost data: {e}")


class BudgetEnforcer:
    """Enforces budget limits and triggers alerts"""
    
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.budgets: Dict[str, float] = {}
        self.alerts: Dict[str, List[BudgetAlert]] = {}
        self.enforcement_actions: Dict[str, List[str]] = {}
        
        # Default budgets (can be overridden)
        self.budgets = {
            BudgetPeriod.DAILY.value: 10.0,
            BudgetPeriod.MONTHLY.value: 300.0
        }
        
        # Default alerts
        self.alerts = {
            BudgetPeriod.DAILY.value: [
                BudgetAlert(50.0, "warning", ["log"], ["console"]),
                BudgetAlert(80.0, "critical", ["throttle"], ["console", "email"]),
                BudgetAlert(95.0, "emergency", ["pause"], ["console", "email", "sms"])
            ],
            BudgetPeriod.MONTHLY.value: [
                BudgetAlert(70.0, "warning", ["log"], ["console"]),
                BudgetAlert(90.0, "critical", ["throttle"], ["console", "email"]),
                BudgetAlert(100.0, "emergency", ["pause"], ["console", "email", "sms"])
            ]
        }
    
    def set_budget(self, period: str, amount: float) -> None:
        """Set budget for a period"""
        self.budgets[period] = amount
        logger.info(f"Set {period} budget to ${amount:.2f}")
    
    def check_budget_status(self, period: str) -> BudgetStatus:
        """Check current budget status"""
        
        budget_amount = self.budgets.get(period, 0.0)
        
        if period == BudgetPeriod.DAILY.value:
            spent_amount = self.cost_tracker.get_daily_spend()
            days_remaining = 1
        elif period == BudgetPeriod.MONTHLY.value:
            now = datetime.now()
            spent_amount = self.cost_tracker.get_monthly_spend(now.year, now.month)
            # Calculate days remaining in month
            next_month = now.replace(day=28) + timedelta(days=4)
            last_day = (next_month - timedelta(days=next_month.day)).day
            days_remaining = last_day - now.day + 1
        else:
            spent_amount = 0.0
            days_remaining = 1
        
        remaining_amount = max(0, budget_amount - spent_amount)
        usage_percent = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        # Project spending
        if period == BudgetPeriod.DAILY.value:
            projected_spend = spent_amount  # Already at end of day
        else:
            daily_average = spent_amount / max(1, 30 - days_remaining + 1)
            projected_spend = spent_amount + (daily_average * days_remaining)
        
        on_track = projected_spend <= budget_amount
        
        # Check for triggered alerts
        alerts_triggered = []
        for alert in self.alerts.get(period, []):
            if usage_percent >= alert.threshold_percent:
                alerts_triggered.append(alert.alert_type)
        
        return BudgetStatus(
            period=period,
            budget_amount=budget_amount,
            spent_amount=spent_amount,
            remaining_amount=remaining_amount,
            usage_percent=usage_percent,
            projected_spend=projected_spend,
            days_remaining=days_remaining,
            on_track=on_track,
            alerts_triggered=alerts_triggered
        )
    
    def enforce_budget(self, period: str) -> List[str]:
        """Enforce budget limits and return actions taken"""
        
        status = self.check_budget_status(period)
        actions_taken = []
        
        for alert in self.alerts.get(period, []):
            if status.usage_percent >= alert.threshold_percent:
                for action in alert.actions:
                    if action not in actions_taken:
                        actions_taken.append(action)
                        self._execute_enforcement_action(action, status)
        
        return actions_taken
    
    def _execute_enforcement_action(self, action: str, status: BudgetStatus) -> None:
        """Execute a budget enforcement action"""
        
        if action == "log":
            logger.warning(f"Budget alert: {status.period} usage at {status.usage_percent:.1f}%")
        
        elif action == "throttle":
            logger.warning(f"Throttling operations due to budget usage: {status.usage_percent:.1f}%")
            # Would implement throttling logic here
        
        elif action == "pause":
            logger.critical(f"Pausing operations due to budget exceeded: {status.usage_percent:.1f}%")
            # Would implement pause logic here
        
        else:
            logger.info(f"Unknown enforcement action: {action}")


class CostOptimizer:
    """Analyzes costs and provides optimization recommendations"""
    
    def __init__(self, cost_tracker: CostTracker, budget_enforcer: BudgetEnforcer):
        self.cost_tracker = cost_tracker
        self.budget_enforcer = budget_enforcer
    
    def analyze_costs(self, days: int = 30) -> Dict[str, Any]:
        """Comprehensive cost analysis"""
        
        analysis = {
            "period_days": days,
            "total_spend": 0.0,
            "daily_average": 0.0,
            "spend_by_category": {},
            "spend_by_service": {},
            "token_efficiency": {},
            "trends": {},
            "anomalies": []
        }
        
        # Get spending data
        category_spend = self.cost_tracker.get_spend_by_category(days)
        service_spend = self.cost_tracker.get_spend_by_service(days)
        token_efficiency = self.cost_tracker.get_token_efficiency(days)
        
        analysis["total_spend"] = sum(category_spend.values())
        analysis["daily_average"] = analysis["total_spend"] / days
        analysis["spend_by_category"] = category_spend
        analysis["spend_by_service"] = service_spend
        analysis["token_efficiency"] = token_efficiency
        
        # Analyze trends (simplified)
        recent_spend = self.cost_tracker.get_spend_by_category(7)
        older_spend = self.cost_tracker.get_spend_by_category(14)
        
        for category in category_spend:
            recent_avg = recent_spend.get(category, 0) / 7
            older_avg = (older_spend.get(category, 0) - recent_spend.get(category, 0)) / 7
            
            if older_avg > 0:
                trend = (recent_avg - older_avg) / older_avg * 100
                analysis["trends"][category] = trend
        
        # Detect anomalies (simplified)
        for category, spend in category_spend.items():
            avg_daily = spend / days
            recent_daily = recent_spend.get(category, 0) / 7
            
            if recent_daily > avg_daily * 2:
                analysis["anomalies"].append({
                    "category": category,
                    "type": "spending_spike",
                    "recent_daily": recent_daily,
                    "average_daily": avg_daily
                })
        
        return analysis
    
    def generate_recommendations(self, days: int = 30) -> List[OptimizationRecommendation]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        analysis = self.analyze_costs(days)
        
        # High Bedrock costs
        bedrock_spend = analysis["spend_by_service"].get("bedrock", 0)
        if bedrock_spend > analysis["total_spend"] * 0.7:
            recommendations.append(OptimizationRecommendation(
                category="bedrock_optimization",
                description="Bedrock costs are high - consider using cheaper models for routine tasks",
                potential_savings_usd=bedrock_spend * 0.3,
                potential_savings_percent=30.0,
                implementation_effort="low",
                risk_level="low",
                actions=[
                    "Use Claude Haiku for simple tasks",
                    "Implement response caching",
                    "Optimize prompt engineering"
                ]
            ))
        
        # Token inefficiency
        token_efficiency = analysis["token_efficiency"]
        if token_efficiency:
            avg_efficiency = sum(token_efficiency.values()) / len(token_efficiency)
            for service, efficiency in token_efficiency.items():
                if efficiency > avg_efficiency * 1.5:
                    recommendations.append(OptimizationRecommendation(
                        category="token_optimization",
                        description=f"{service} has high cost per token - optimize prompts",
                        potential_savings_usd=analysis["spend_by_service"].get(service, 0) * 0.2,
                        potential_savings_percent=20.0,
                        implementation_effort="medium",
                        risk_level="low",
                        actions=[
                            "Compress prompts",
                            "Remove redundant context",
                            "Use more efficient models"
                        ]
                    ))
        
        # Spending trends
        for category, trend in analysis["trends"].items():
            if trend > 50:  # 50% increase
                recommendations.append(OptimizationRecommendation(
                    category="trend_analysis",
                    description=f"{category} spending increased {trend:.1f}% - investigate usage patterns",
                    potential_savings_usd=analysis["spend_by_category"].get(category, 0) * 0.1,
                    potential_savings_percent=10.0,
                    implementation_effort="medium",
                    risk_level="medium",
                    actions=[
                        "Analyze usage patterns",
                        "Implement usage controls",
                        "Review automation rules"
                    ]
                ))
        
        # Budget status recommendations
        daily_status = self.budget_enforcer.check_budget_status(BudgetPeriod.DAILY.value)
        if daily_status.usage_percent > 80:
            recommendations.append(OptimizationRecommendation(
                category="budget_management",
                description="Daily budget usage is high - implement cost controls",
                potential_savings_usd=daily_status.spent_amount * 0.2,
                potential_savings_percent=20.0,
                implementation_effort="high",
                risk_level="medium",
                actions=[
                    "Implement request throttling",
                    "Pause non-critical operations",
                    "Switch to cheaper models"
                ]
            ))
        
        return recommendations
    
    def optimize_model_selection(self, task_type: str, quality_requirement: float = 0.8) -> Dict[str, Any]:
        """Recommend optimal model for cost/quality balance"""
        
        # Model cost and quality data (simplified)
        models = {
            "claude-3-5-sonnet": {"cost_per_1k": 0.003, "quality": 0.95, "speed": 0.7},
            "claude-3-haiku": {"cost_per_1k": 0.00025, "quality": 0.85, "speed": 0.95},
            "titan-text": {"cost_per_1k": 0.0005, "quality": 0.75, "speed": 0.8}
        }
        
        # Task-specific quality adjustments
        task_adjustments = {
            "analysis": {"claude-3-5-sonnet": 1.0, "claude-3-haiku": 0.9, "titan-text": 0.7},
            "simple_decision": {"claude-3-5-sonnet": 1.0, "claude-3-haiku": 1.0, "titan-text": 0.9},
            "creative": {"claude-3-5-sonnet": 1.0, "claude-3-haiku": 0.8, "titan-text": 0.9}
        }
        
        recommendations = []
        
        for model, specs in models.items():
            adjusted_quality = specs["quality"] * task_adjustments.get(task_type, {}).get(model, 1.0)
            
            if adjusted_quality >= quality_requirement:
                cost_efficiency = adjusted_quality / specs["cost_per_1k"]
                
                recommendations.append({
                    "model": model,
                    "cost_per_1k": specs["cost_per_1k"],
                    "adjusted_quality": adjusted_quality,
                    "speed": specs["speed"],
                    "cost_efficiency": cost_efficiency
                })
        
        # Sort by cost efficiency
        recommendations.sort(key=lambda x: x["cost_efficiency"], reverse=True)
        
        return {
            "task_type": task_type,
            "quality_requirement": quality_requirement,
            "recommended_models": recommendations,
            "best_choice": recommendations[0] if recommendations else None
        }
    
    def should_use_cheaper_model(self, task_context: Dict[str, Any]) -> bool:
        """Determine if cheaper model should be used based on budget status"""
        
        daily_status = self.budget_enforcer.check_budget_status(BudgetPeriod.DAILY.value)
        monthly_status = self.budget_enforcer.check_budget_status(BudgetPeriod.MONTHLY.value)
        
        # Use cheaper models if budget usage is high
        if daily_status.usage_percent > 70 or monthly_status.usage_percent > 80:
            return True
        
        # Use cheaper models for low-priority tasks
        if task_context.get("priority", "normal") == "low":
            return True
        
        # Use cheaper models if cost sensitivity is high
        if task_context.get("cost_sensitivity", 0.5) > 0.7:
            return True
        
        return False


class RealTimeMonitor:
    """Real-time cost and usage monitoring"""
    
    def __init__(self, cost_tracker: CostTracker, budget_enforcer: BudgetEnforcer):
        self.cost_tracker = cost_tracker
        self.budget_enforcer = budget_enforcer
        self.monitoring_active = False
        self.alert_callbacks: List[Callable] = []
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for real-time alerts"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self, check_interval: int = 60) -> None:
        """Start real-time monitoring"""
        
        self.monitoring_active = True
        logger.info("Started real-time cost monitoring")
        
        while self.monitoring_active:
            try:
                await self._check_budgets()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(check_interval)
    
    def stop_monitoring(self) -> None:
        """Stop real-time monitoring"""
        self.monitoring_active = False
        logger.info("Stopped real-time cost monitoring")
    
    async def _check_budgets(self) -> None:
        """Check budget status and trigger alerts"""
        
        for period in [BudgetPeriod.DAILY.value, BudgetPeriod.MONTHLY.value]:
            status = self.budget_enforcer.check_budget_status(period)
            
            # Check for alerts
            if status.alerts_triggered:
                alert_data = {
                    "period": period,
                    "status": status.to_dict(),
                    "timestamp": datetime.now().isoformat()
                }
                
                for callback in self.alert_callbacks:
                    try:
                        callback("budget_alert", alert_data)
                    except Exception as e:
                        logger.error(f"Alert callback failed: {e}")
            
            # Enforce budget
            actions = self.budget_enforcer.enforce_budget(period)
            if actions:
                logger.info(f"Budget enforcement actions for {period}: {actions}")
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        
        now = datetime.now()
        
        return {
            "timestamp": now.isoformat(),
            "daily_spend": self.cost_tracker.get_daily_spend(now),
            "monthly_spend": self.cost_tracker.get_monthly_spend(now.year, now.month),
            "daily_budget_status": self.budget_enforcer.check_budget_status(BudgetPeriod.DAILY.value).to_dict(),
            "monthly_budget_status": self.budget_enforcer.check_budget_status(BudgetPeriod.MONTHLY.value).to_dict(),
            "recent_costs": [entry.to_dict() for entry in self.cost_tracker.cost_entries[-10:]],
            "monitoring_active": self.monitoring_active
        }


# Convenience function to create integrated cost management system
def create_cost_management_system(storage_path: str = "AI_NETWORK_LOCAL",
                                daily_budget: float = 10.0,
                                monthly_budget: float = 300.0) -> Tuple[CostTracker, BudgetEnforcer, CostOptimizer, RealTimeMonitor]:
    """Create integrated cost management system"""
    
    cost_tracker = CostTracker(storage_path)
    budget_enforcer = BudgetEnforcer(cost_tracker)
    cost_optimizer = CostOptimizer(cost_tracker, budget_enforcer)
    real_time_monitor = RealTimeMonitor(cost_tracker, budget_enforcer)
    
    # Set budgets
    budget_enforcer.set_budget(BudgetPeriod.DAILY.value, daily_budget)
    budget_enforcer.set_budget(BudgetPeriod.MONTHLY.value, monthly_budget)
    
    return cost_tracker, budget_enforcer, cost_optimizer, real_time_monitor