"""
E-Commerce Intelligence Module
==============================

Advanced features for the Shopify connector:
- Competitor price analysis
- Product trend detection
- Smart product scoring
- Caching layer for API efficiency
- Webhook handlers for real-time updates
- Health monitoring and alerts

Integrates with shopify_connector.py for enhanced AI-powered e-commerce.
"""

import json
import os
import time
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from collections import defaultdict
import threading
import queue

logger = logging.getLogger(__name__)


# =============================================================================
# CACHING LAYER
# =============================================================================

class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"       # Least Recently Used
    LFU = "lfu"       # Least Frequently Used
    TTL = "ttl"       # Time To Live
    FIFO = "fifo"     # First In First Out


@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    created_at: float
    accessed_at: float
    access_count: int = 0
    ttl_seconds: int = 3600  # 1 hour default


class IntelligentCache:
    """
    Multi-strategy cache for API responses and computed data.
    Reduces API calls and speeds up repeated operations.
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            # Check TTL
            if time.time() - entry.created_at > entry.ttl_seconds:
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            # Update access stats
            entry.accessed_at = time.time()
            entry.access_count += 1
            self._stats["hits"] += 1

            return entry.value

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache"""
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict()

            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                accessed_at=time.time(),
                ttl_seconds=ttl or self.default_ttl
            )

    def _evict(self) -> None:
        """Evict entries based on strategy"""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Remove least recently accessed
            oldest_key = min(self._cache, key=lambda k: self._cache[k].accessed_at)
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            oldest_key = min(self._cache, key=lambda k: self._cache[k].access_count)
        elif self.strategy == CacheStrategy.FIFO:
            # Remove first inserted
            oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)
        else:  # TTL - remove oldest by creation time
            oldest_key = min(self._cache, key=lambda k: self._cache[k].created_at)

        del self._cache[oldest_key]
        self._stats["evictions"] += 1

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": f"{hit_rate:.2%}"
        }


# Global cache instance
_cache = IntelligentCache(max_size=5000, default_ttl=1800)


def cached(ttl: int = 1800):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try cache first
            result = _cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator


# =============================================================================
# COMPETITOR PRICE ANALYSIS
# =============================================================================

@dataclass
class CompetitorPrice:
    """Price data from a competitor"""
    competitor: str
    price: float
    url: str
    last_updated: str
    in_stock: bool = True
    shipping_cost: float = 0.0
    rating: float = 0.0
    review_count: int = 0


@dataclass
class PriceAnalysis:
    """Complete price analysis for a product"""
    product_name: str
    your_price: float
    competitor_prices: List[CompetitorPrice]
    market_average: float
    market_low: float
    market_high: float
    price_position: str  # "lowest", "below_avg", "average", "above_avg", "highest"
    recommended_price: float
    potential_savings: float
    competitive_score: float  # 0-100


class CompetitorAnalyzer:
    """
    Analyze competitor pricing across multiple platforms.
    Provides pricing intelligence for optimal positioning.
    """

    # Simulated competitor data sources
    COMPETITORS = [
        "Amazon",
        "eBay",
        "Walmart",
        "Target",
        "Best Buy",
        "Newegg",
        "AliExpress Direct"
    ]

    def __init__(self):
        self.cache = IntelligentCache(max_size=2000, default_ttl=3600)

    @cached(ttl=1800)
    def analyze_product(
        self,
        product_name: str,
        your_price: float,
        category: str = "general"
    ) -> PriceAnalysis:
        """
        Analyze pricing position for a product.
        Returns comprehensive market analysis.
        """
        # Simulate competitor price lookup
        competitor_prices = self._fetch_competitor_prices(product_name, category)

        if not competitor_prices:
            return PriceAnalysis(
                product_name=product_name,
                your_price=your_price,
                competitor_prices=[],
                market_average=your_price,
                market_low=your_price,
                market_high=your_price,
                price_position="only_seller",
                recommended_price=your_price,
                potential_savings=0,
                competitive_score=50.0
            )

        # Calculate market stats
        prices = [cp.price for cp in competitor_prices]
        market_avg = sum(prices) / len(prices)
        market_low = min(prices)
        market_high = max(prices)

        # Determine price position
        if your_price <= market_low:
            position = "lowest"
            score = 95.0
        elif your_price < market_avg * 0.9:
            position = "below_avg"
            score = 80.0
        elif your_price <= market_avg * 1.1:
            position = "average"
            score = 60.0
        elif your_price <= market_high:
            position = "above_avg"
            score = 40.0
        else:
            position = "highest"
            score = 20.0

        # Calculate recommended price (10% below average for competitiveness)
        recommended = market_avg * 0.9

        # Potential savings if priced at recommendation
        savings = (your_price - recommended) if your_price > recommended else 0

        return PriceAnalysis(
            product_name=product_name,
            your_price=your_price,
            competitor_prices=competitor_prices,
            market_average=round(market_avg, 2),
            market_low=market_low,
            market_high=market_high,
            price_position=position,
            recommended_price=round(recommended, 2),
            potential_savings=round(savings, 2),
            competitive_score=score
        )

    def _fetch_competitor_prices(
        self,
        product_name: str,
        category: str
    ) -> List[CompetitorPrice]:
        """
        Fetch competitor prices (simulated).
        In production, this would scrape or use APIs.
        """
        import random

        # Base price estimation based on product name keywords
        base_price = self._estimate_base_price(product_name)

        prices = []
        for competitor in random.sample(self.COMPETITORS, k=random.randint(3, 6)):
            # Vary price ±30% from base
            variance = random.uniform(0.7, 1.3)
            price = round(base_price * variance, 2)

            prices.append(CompetitorPrice(
                competitor=competitor,
                price=price,
                url=f"https://{competitor.lower().replace(' ', '')}.com/product/{hash(product_name) % 100000}",
                last_updated=datetime.now().isoformat(),
                in_stock=random.random() > 0.1,  # 90% in stock
                shipping_cost=round(random.uniform(0, 9.99), 2) if random.random() > 0.5 else 0,
                rating=round(random.uniform(3.5, 5.0), 1),
                review_count=random.randint(10, 5000)
            ))

        return prices

    def _estimate_base_price(self, product_name: str) -> float:
        """Estimate base price from product name"""
        name_lower = product_name.lower()

        # Price ranges by keyword
        price_hints = {
            "earbuds": 35, "headphones": 50, "watch": 80,
            "phone": 200, "laptop": 800, "desktop": 600,
            "charger": 25, "cable": 15, "adapter": 20,
            "speaker": 60, "keyboard": 70, "mouse": 40,
            "monitor": 300, "tv": 500, "projector": 150,
            "camera": 400, "drone": 300, "tablet": 350,
            "smart": 50, "wireless": 40, "bluetooth": 35,
            "led": 30, "usb": 15, "portable": 45
        }

        for keyword, price in price_hints.items():
            if keyword in name_lower:
                return price

        return 50.0  # Default base price


# =============================================================================
# TREND DETECTION
# =============================================================================

class TrendDirection(Enum):
    """Trend direction indicators"""
    RISING_FAST = "rising_fast"      # >20% growth
    RISING = "rising"                 # 5-20% growth
    STABLE = "stable"                 # -5% to 5%
    DECLINING = "declining"           # -5% to -20%
    DECLINING_FAST = "declining_fast" # <-20%


@dataclass
class ProductTrend:
    """Trend data for a product or category"""
    name: str
    direction: TrendDirection
    growth_rate: float  # Percentage
    search_volume: int
    social_mentions: int
    predicted_demand: str  # "high", "medium", "low"
    seasonality: str  # "year_round", "seasonal", "holiday"
    recommendation: str
    confidence: float  # 0-1


class TrendDetector:
    """
    Detect product and category trends.
    Uses simulated data for trend analysis.
    """

    # Trending categories with growth rates
    TREND_DATA = {
        "electronics": {
            "wireless_earbuds": {"growth": 15, "season": "year_round"},
            "smart_home": {"growth": 25, "season": "year_round"},
            "portable_chargers": {"growth": 10, "season": "year_round"},
            "gaming_accessories": {"growth": 20, "season": "holiday"},
            "vr_headsets": {"growth": 30, "season": "year_round"},
        },
        "home": {
            "air_purifiers": {"growth": 35, "season": "seasonal"},
            "led_lights": {"growth": 18, "season": "holiday"},
            "organization": {"growth": 12, "season": "year_round"},
            "kitchen_gadgets": {"growth": 8, "season": "year_round"},
        },
        "fashion": {
            "sustainable": {"growth": 40, "season": "year_round"},
            "athleisure": {"growth": 22, "season": "year_round"},
            "minimalist": {"growth": 15, "season": "year_round"},
        },
        "health": {
            "fitness_trackers": {"growth": 18, "season": "year_round"},
            "supplements": {"growth": 25, "season": "year_round"},
            "massage_devices": {"growth": 30, "season": "holiday"},
        }
    }

    def __init__(self):
        self.cache = IntelligentCache(max_size=500, default_ttl=7200)

    @cached(ttl=3600)
    def analyze_trend(self, product_name: str, category: str = None) -> ProductTrend:
        """Analyze trend for a specific product"""
        import random

        # Find matching trend data
        growth_rate = 0
        seasonality = "year_round"

        name_lower = product_name.lower()

        for cat, trends in self.TREND_DATA.items():
            for trend_key, data in trends.items():
                if trend_key.replace("_", " ") in name_lower or any(
                    word in name_lower for word in trend_key.split("_")
                ):
                    growth_rate = data["growth"] + random.uniform(-5, 5)
                    seasonality = data["season"]
                    break

        # If no match, generate reasonable default
        if growth_rate == 0:
            growth_rate = random.uniform(-10, 15)

        # Determine direction
        if growth_rate > 20:
            direction = TrendDirection.RISING_FAST
        elif growth_rate > 5:
            direction = TrendDirection.RISING
        elif growth_rate > -5:
            direction = TrendDirection.STABLE
        elif growth_rate > -20:
            direction = TrendDirection.DECLINING
        else:
            direction = TrendDirection.DECLINING_FAST

        # Predict demand
        if growth_rate > 15:
            demand = "high"
        elif growth_rate > 0:
            demand = "medium"
        else:
            demand = "low"

        # Generate recommendation
        if direction in [TrendDirection.RISING_FAST, TrendDirection.RISING]:
            recommendation = "Strong buy signal - consider stocking up and promoting actively"
        elif direction == TrendDirection.STABLE:
            recommendation = "Steady performer - maintain current inventory levels"
        else:
            recommendation = "Caution advised - consider reducing inventory or finding alternatives"

        return ProductTrend(
            name=product_name,
            direction=direction,
            growth_rate=round(growth_rate, 1),
            search_volume=random.randint(1000, 100000),
            social_mentions=random.randint(100, 50000),
            predicted_demand=demand,
            seasonality=seasonality,
            recommendation=recommendation,
            confidence=random.uniform(0.6, 0.95)
        )

    def get_trending_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top trending categories"""
        trends = []

        for category, items in self.TREND_DATA.items():
            for item_name, data in items.items():
                trends.append({
                    "category": category,
                    "subcategory": item_name.replace("_", " ").title(),
                    "growth_rate": data["growth"],
                    "seasonality": data["season"]
                })

        # Sort by growth rate
        trends.sort(key=lambda x: x["growth_rate"], reverse=True)
        return trends[:limit]


# =============================================================================
# PRODUCT SCORING
# =============================================================================

@dataclass
class ProductScore:
    """Comprehensive product score"""
    product_name: str
    overall_score: float  # 0-100
    margin_score: float
    trend_score: float
    competition_score: float
    demand_score: float
    risk_score: float
    recommendation: str
    factors: Dict[str, float]


class ProductScorer:
    """
    Calculate comprehensive product scores for decision making.
    Combines multiple factors into actionable scores.
    """

    # Score weights
    WEIGHTS = {
        "margin": 0.30,
        "trend": 0.25,
        "competition": 0.20,
        "demand": 0.15,
        "risk": 0.10
    }

    def __init__(self):
        self.competitor_analyzer = CompetitorAnalyzer()
        self.trend_detector = TrendDetector()

    def score_product(
        self,
        product_name: str,
        wholesale_cost: float,
        selling_price: float,
        category: str = "general"
    ) -> ProductScore:
        """Calculate comprehensive product score"""

        # Calculate individual scores
        margin_score = self._calculate_margin_score(wholesale_cost, selling_price)
        trend_score = self._calculate_trend_score(product_name)
        competition_score = self._calculate_competition_score(product_name, selling_price)
        demand_score = self._calculate_demand_score(product_name)
        risk_score = self._calculate_risk_score(wholesale_cost, margin_score, trend_score)

        # Calculate weighted overall score
        overall = (
            margin_score * self.WEIGHTS["margin"] +
            trend_score * self.WEIGHTS["trend"] +
            competition_score * self.WEIGHTS["competition"] +
            demand_score * self.WEIGHTS["demand"] +
            (100 - risk_score) * self.WEIGHTS["risk"]  # Invert risk for scoring
        )

        # Generate recommendation
        if overall >= 80:
            recommendation = "EXCELLENT - Top priority for listing, high confidence"
        elif overall >= 65:
            recommendation = "GOOD - Recommended for listing with standard promotion"
        elif overall >= 50:
            recommendation = "FAIR - List with caution, monitor performance closely"
        elif overall >= 35:
            recommendation = "POOR - Consider alternatives or negotiate better pricing"
        else:
            recommendation = "AVOID - High risk, low potential, not recommended"

        return ProductScore(
            product_name=product_name,
            overall_score=round(overall, 1),
            margin_score=round(margin_score, 1),
            trend_score=round(trend_score, 1),
            competition_score=round(competition_score, 1),
            demand_score=round(demand_score, 1),
            risk_score=round(risk_score, 1),
            recommendation=recommendation,
            factors={
                "margin_weight": self.WEIGHTS["margin"],
                "trend_weight": self.WEIGHTS["trend"],
                "competition_weight": self.WEIGHTS["competition"],
                "demand_weight": self.WEIGHTS["demand"],
                "risk_weight": self.WEIGHTS["risk"]
            }
        )

    def _calculate_margin_score(self, cost: float, price: float) -> float:
        """Score based on profit margin"""
        if price <= 0:
            return 0

        margin = ((price - cost) / price) * 100

        if margin >= 60:
            return 100
        elif margin >= 50:
            return 85
        elif margin >= 40:
            return 70
        elif margin >= 30:
            return 55
        elif margin >= 20:
            return 40
        elif margin >= 10:
            return 25
        else:
            return max(0, margin)

    def _calculate_trend_score(self, product_name: str) -> float:
        """Score based on trend analysis"""
        trend = self.trend_detector.analyze_trend(product_name)

        direction_scores = {
            TrendDirection.RISING_FAST: 100,
            TrendDirection.RISING: 75,
            TrendDirection.STABLE: 50,
            TrendDirection.DECLINING: 25,
            TrendDirection.DECLINING_FAST: 0
        }

        return direction_scores.get(trend.direction, 50)

    def _calculate_competition_score(self, product_name: str, your_price: float) -> float:
        """Score based on competitive position"""
        analysis = self.competitor_analyzer.analyze_product(product_name, your_price)
        return analysis.competitive_score

    def _calculate_demand_score(self, product_name: str) -> float:
        """Score based on estimated demand"""
        trend = self.trend_detector.analyze_trend(product_name)

        demand_scores = {
            "high": 90,
            "medium": 60,
            "low": 30
        }

        base_score = demand_scores.get(trend.predicted_demand, 50)

        # Adjust for seasonality
        if trend.seasonality == "holiday":
            # Boost during Q4
            month = datetime.now().month
            if month in [10, 11, 12]:
                base_score = min(100, base_score * 1.3)
        elif trend.seasonality == "seasonal":
            base_score *= 0.9  # Slight penalty for seasonal

        return base_score

    def _calculate_risk_score(
        self,
        cost: float,
        margin_score: float,
        trend_score: float
    ) -> float:
        """Calculate risk score (higher = riskier)"""
        risk = 0

        # High cost = higher risk
        if cost > 100:
            risk += 20
        elif cost > 50:
            risk += 10

        # Low margin = higher risk
        if margin_score < 40:
            risk += 30
        elif margin_score < 60:
            risk += 15

        # Declining trend = higher risk
        if trend_score < 30:
            risk += 30
        elif trend_score < 50:
            risk += 15

        return min(100, risk)


# =============================================================================
# WEBHOOK HANDLERS
# =============================================================================

@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_type: str
    payload: Dict[str, Any]
    timestamp: str
    source: str
    processed: bool = False
    result: Optional[Dict[str, Any]] = None


class WebhookHandler:
    """
    Handle incoming webhooks from various sources.
    Processes events and triggers appropriate actions.
    """

    def __init__(self):
        self.event_queue: queue.Queue = queue.Queue()
        self.handlers: Dict[str, Callable] = {}
        self.event_log: List[WebhookEvent] = []
        self._running = False
        self._worker_thread = None

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register a handler for an event type"""
        self.handlers[event_type] = handler
        logger.info(f"Registered webhook handler for: {event_type}")

    def receive_event(self, event_type: str, payload: Dict[str, Any], source: str = "unknown") -> str:
        """Receive and queue a webhook event"""
        event = WebhookEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now().isoformat(),
            source=source
        )

        self.event_queue.put(event)
        self.event_log.append(event)

        # Keep only last 1000 events
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]

        return f"Event queued: {event_type}"

    def start_processing(self) -> None:
        """Start background event processing"""
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self._worker_thread.start()
        logger.info("Webhook processor started")

    def stop_processing(self) -> None:
        """Stop background processing"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("Webhook processor stopped")

    def _process_events(self) -> None:
        """Background event processing loop"""
        while self._running:
            try:
                event = self.event_queue.get(timeout=1)
                self._handle_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing webhook event: {e}")

    def _handle_event(self, event: WebhookEvent) -> None:
        """Handle a single event"""
        handler = self.handlers.get(event.event_type)

        if handler:
            try:
                result = handler(event.payload)
                event.processed = True
                event.result = result
                logger.info(f"Processed webhook: {event.event_type}")
            except Exception as e:
                event.result = {"error": str(e)}
                logger.error(f"Webhook handler error: {e}")
        else:
            logger.warning(f"No handler for event type: {event.event_type}")

    def get_stats(self) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        processed = sum(1 for e in self.event_log if e.processed)
        failed = sum(1 for e in self.event_log if e.result and "error" in e.result)

        return {
            "total_events": len(self.event_log),
            "processed": processed,
            "failed": failed,
            "pending": self.event_queue.qsize(),
            "registered_handlers": list(self.handlers.keys())
        }


# =============================================================================
# HEALTH MONITORING
# =============================================================================

class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthCheck:
    """Individual health check result"""
    component: str
    status: HealthStatus
    latency_ms: float
    message: str
    last_check: str


@dataclass
class SystemHealth:
    """Overall system health"""
    status: HealthStatus
    checks: List[HealthCheck]
    uptime_seconds: float
    memory_usage_mb: float
    cache_stats: Dict[str, Any]
    webhook_stats: Dict[str, Any]
    recommendations: List[str]


class HealthMonitor:
    """
    Monitor system health and provide diagnostics.
    Tracks performance, errors, and system resources.
    """

    def __init__(self):
        self.start_time = time.time()
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.latency_history: List[float] = []
        self.webhook_handler = WebhookHandler()

    def check_health(self) -> SystemHealth:
        """Perform comprehensive health check"""
        checks = []
        recommendations = []

        # Check cache health
        cache_check = self._check_cache()
        checks.append(cache_check)
        if cache_check.status != HealthStatus.HEALTHY:
            recommendations.append("Consider clearing cache or increasing cache size")

        # Check API connectivity (simulated)
        api_check = self._check_api()
        checks.append(api_check)
        if api_check.status != HealthStatus.HEALTHY:
            recommendations.append("API connectivity issues detected, check network")

        # Check webhook processor
        webhook_check = self._check_webhooks()
        checks.append(webhook_check)

        # Check memory usage
        memory_check = self._check_memory()
        checks.append(memory_check)
        if memory_check.status == HealthStatus.DEGRADED:
            recommendations.append("Memory usage high, consider restarting service")

        # Determine overall status
        statuses = [c.status for c in checks]
        if HealthStatus.CRITICAL in statuses:
            overall = HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            overall = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return SystemHealth(
            status=overall,
            checks=checks,
            uptime_seconds=time.time() - self.start_time,
            memory_usage_mb=self._get_memory_usage(),
            cache_stats=_cache.get_stats(),
            webhook_stats=self.webhook_handler.get_stats(),
            recommendations=recommendations
        )

    def _check_cache(self) -> HealthCheck:
        """Check cache health"""
        start = time.time()
        stats = _cache.get_stats()
        latency = (time.time() - start) * 1000

        hit_rate = float(stats["hit_rate"].rstrip("%")) / 100

        if hit_rate >= 0.5:
            status = HealthStatus.HEALTHY
            msg = f"Cache performing well ({stats['hit_rate']} hit rate)"
        elif hit_rate >= 0.2:
            status = HealthStatus.DEGRADED
            msg = f"Cache hit rate low ({stats['hit_rate']})"
        else:
            status = HealthStatus.UNHEALTHY
            msg = f"Cache not effective ({stats['hit_rate']} hit rate)"

        return HealthCheck(
            component="cache",
            status=status,
            latency_ms=latency,
            message=msg,
            last_check=datetime.now().isoformat()
        )

    def _check_api(self) -> HealthCheck:
        """Check API connectivity (simulated)"""
        import random
        start = time.time()

        # Simulate API check
        latency = random.uniform(50, 200)
        time.sleep(0.01)  # Simulate network delay

        latency = (time.time() - start) * 1000

        if latency < 100:
            status = HealthStatus.HEALTHY
            msg = "API responding normally"
        elif latency < 500:
            status = HealthStatus.DEGRADED
            msg = "API response slow"
        else:
            status = HealthStatus.UNHEALTHY
            msg = "API response very slow"

        return HealthCheck(
            component="api",
            status=status,
            latency_ms=latency,
            message=msg,
            last_check=datetime.now().isoformat()
        )

    def _check_webhooks(self) -> HealthCheck:
        """Check webhook processor health"""
        start = time.time()
        stats = self.webhook_handler.get_stats()
        latency = (time.time() - start) * 1000

        pending = stats["pending"]
        if pending == 0:
            status = HealthStatus.HEALTHY
            msg = "Webhook queue empty"
        elif pending < 100:
            status = HealthStatus.DEGRADED
            msg = f"Webhook queue has {pending} pending events"
        else:
            status = HealthStatus.UNHEALTHY
            msg = f"Webhook queue backlogged ({pending} pending)"

        return HealthCheck(
            component="webhooks",
            status=status,
            latency_ms=latency,
            message=msg,
            last_check=datetime.now().isoformat()
        )

    def _check_memory(self) -> HealthCheck:
        """Check memory usage"""
        start = time.time()
        memory_mb = self._get_memory_usage()
        latency = (time.time() - start) * 1000

        if memory_mb < 500:
            status = HealthStatus.HEALTHY
            msg = f"Memory usage normal ({memory_mb:.1f}MB)"
        elif memory_mb < 1000:
            status = HealthStatus.DEGRADED
            msg = f"Memory usage elevated ({memory_mb:.1f}MB)"
        else:
            status = HealthStatus.UNHEALTHY
            msg = f"Memory usage high ({memory_mb:.1f}MB)"

        return HealthCheck(
            component="memory",
            status=status,
            latency_ms=latency,
            message=msg,
            last_check=datetime.now().isoformat()
        )

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return usage.ru_maxrss / 1024  # Convert KB to MB
        except:
            return 100.0  # Default estimate


# =============================================================================
# INTEGRATION WITH SHOPIFY CONNECTOR
# =============================================================================

class EnhancedProductAnalyzer:
    """
    Enhanced product analyzer that combines all intelligence modules.
    Drop-in enhancement for shopify_connector.py
    """

    def __init__(self):
        self.competitor_analyzer = CompetitorAnalyzer()
        self.trend_detector = TrendDetector()
        self.product_scorer = ProductScorer()
        self.health_monitor = HealthMonitor()

    def analyze_product_opportunity(
        self,
        product_name: str,
        wholesale_cost: float,
        selling_price: float,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Comprehensive product opportunity analysis.
        Returns all intelligence data for a product.
        """
        # Get all analyses
        score = self.product_scorer.score_product(
            product_name, wholesale_cost, selling_price, category
        )
        trend = self.trend_detector.analyze_trend(product_name, category)
        competition = self.competitor_analyzer.analyze_product(
            product_name, selling_price, category
        )

        return {
            "product_name": product_name,
            "wholesale_cost": wholesale_cost,
            "selling_price": selling_price,
            "profit_margin": round(((selling_price - wholesale_cost) / selling_price) * 100, 1),

            # Scoring
            "overall_score": score.overall_score,
            "recommendation": score.recommendation,
            "scores": {
                "margin": score.margin_score,
                "trend": score.trend_score,
                "competition": score.competition_score,
                "demand": score.demand_score,
                "risk": score.risk_score
            },

            # Trend data
            "trend": {
                "direction": trend.direction.value,
                "growth_rate": trend.growth_rate,
                "predicted_demand": trend.predicted_demand,
                "seasonality": trend.seasonality
            },

            # Competition data
            "competition": {
                "market_average": competition.market_average,
                "market_low": competition.market_low,
                "market_high": competition.market_high,
                "price_position": competition.price_position,
                "recommended_price": competition.recommended_price,
                "competitor_count": len(competition.competitor_prices)
            },

            # Action items
            "actions": self._generate_actions(score, trend, competition)
        }

    def _generate_actions(
        self,
        score: ProductScore,
        trend: ProductTrend,
        competition: PriceAnalysis
    ) -> List[str]:
        """Generate actionable recommendations"""
        actions = []

        if score.overall_score >= 70:
            actions.append("✅ APPROVE: Strong opportunity, proceed with listing")
        elif score.overall_score >= 50:
            actions.append("⚠️ REVIEW: Moderate opportunity, consider adjustments")
        else:
            actions.append("❌ SKIP: Poor opportunity, find alternatives")

        if competition.price_position == "highest":
            actions.append(f"💰 REPRICE: Consider lowering to ${competition.recommended_price}")

        if trend.direction == TrendDirection.RISING_FAST:
            actions.append("📈 STOCK UP: Trending product, increase inventory")
        elif trend.direction == TrendDirection.DECLINING_FAST:
            actions.append("📉 CLEAR OUT: Declining trend, reduce inventory")

        if trend.seasonality == "holiday":
            month = datetime.now().month
            if month in [9, 10]:
                actions.append("🎄 PREPARE: Holiday season approaching, stock now")
            elif month in [11, 12]:
                actions.append("🎁 PROMOTE: Peak holiday season, maximize exposure")

        return actions


# =============================================================================
# CLI DEMO
# =============================================================================

def demo():
    """Demonstrate intelligence features"""
    print("=" * 70)
    print("E-COMMERCE INTELLIGENCE DEMO")
    print("=" * 70)

    analyzer = EnhancedProductAnalyzer()

    # Test products
    products = [
        ("Wireless Bluetooth Earbuds Pro", 12.00, 39.99),
        ("Smart Home LED Strip Lights", 8.00, 29.99),
        ("Portable Phone Charger 20000mAh", 15.00, 44.99),
        ("Vintage Cassette Player", 25.00, 45.99),  # Declining trend
    ]

    for name, cost, price in products:
        print(f"\n{'='*70}")
        print(f"PRODUCT: {name}")
        print(f"Cost: ${cost:.2f} | Price: ${price:.2f}")
        print("-" * 70)

        analysis = analyzer.analyze_product_opportunity(name, cost, price)

        print(f"\nOVERALL SCORE: {analysis['overall_score']}/100")
        print(f"Profit Margin: {analysis['profit_margin']}%")
        print(f"\nScores:")
        for key, value in analysis['scores'].items():
            print(f"  - {key.title()}: {value}/100")

        print(f"\nTrend: {analysis['trend']['direction']} ({analysis['trend']['growth_rate']:+.1f}%)")
        print(f"Demand: {analysis['trend']['predicted_demand'].upper()}")

        print(f"\nCompetition:")
        print(f"  - Market Avg: ${analysis['competition']['market_average']}")
        print(f"  - Your Position: {analysis['competition']['price_position']}")
        print(f"  - Recommended: ${analysis['competition']['recommended_price']}")

        print(f"\nACTIONS:")
        for action in analysis['actions']:
            print(f"  {action}")

    # Health check
    print(f"\n{'='*70}")
    print("SYSTEM HEALTH")
    print("-" * 70)

    health = analyzer.health_monitor.check_health()
    print(f"Status: {health.status.value.upper()}")
    print(f"Uptime: {health.uptime_seconds:.0f}s")
    print(f"Memory: {health.memory_usage_mb:.1f}MB")
    print(f"Cache: {health.cache_stats}")

    for check in health.checks:
        icon = "✅" if check.status == HealthStatus.HEALTHY else "⚠️"
        print(f"  {icon} {check.component}: {check.message}")

    print("=" * 70)


if __name__ == "__main__":
    demo()
