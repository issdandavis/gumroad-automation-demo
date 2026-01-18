"""
Shopify Connector - Zero-Click E-Commerce AI System
====================================================

AI-powered Shopify connector for automated store management.
New sellers can simply say 'find me products' and the AI does everything:
- Finds products from wholesaler APIs
- Calculates profit margins (ideal/natural/bad/loss)
- Auto-adds products to Shopify with optimal pricing
- Enables zero-click store management

Integrates with:
- AWS Bedrock for AI decisions
- Universal Bridge for inter-AI communication
- Self-Evolving AI Framework for autonomous operations
"""

import json
import os
import time
import uuid
import hashlib
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import requests

# Intelligence module imports (optional enhancement)
try:
    from ecommerce_intelligence import (
        EnhancedProductAnalyzer,
        CompetitorAnalyzer,
        TrendDetector,
        ProductScorer,
        HealthMonitor,
        WebhookHandler,
        cached
    )
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False

# PC Build compatibility checker (optional)
try:
    from pc_compatibility_checker import PCCompatibilityChecker, check_build
    COMPATIBILITY_CHECKER_AVAILABLE = True
except ImportError:
    COMPATIBILITY_CHECKER_AVAILABLE = False

# Framework imports - with graceful fallbacks for standalone operation
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Try to import Bedrock client (optional - falls back to mock)
try:
    from self_evolving_core.bedrock_client import BedrockClient, BedrockRequest, BedrockResponse
    from self_evolving_core.aws_config import AWSConfigManager
    from self_evolving_core.models import OperationResult, Event
    BEDROCK_AVAILABLE = True
except ImportError as e:
    BEDROCK_AVAILABLE = False
    # Mock classes for standalone operation
    @dataclass
    class BedrockRequest:
        model_id: str = ""
        prompt: str = ""
        max_tokens: int = 4000
        temperature: float = 0.3
        top_p: float = 0.9
        stop_sequences: List[str] = field(default_factory=list)
        metadata: Dict[str, Any] = field(default_factory=dict)

    @dataclass
    class BedrockResponse:
        success: bool = False
        content: str = ""
        model_id: str = ""
        error: Optional[str] = None

    class BedrockClient:
        def __init__(self, *args, **kwargs): pass
        async def invoke_model(self, request):
            return BedrockResponse(success=False, error="Bedrock not available")

    class AWSConfigManager:
        def __init__(self, *args, **kwargs): pass

    @dataclass
    class OperationResult:
        success: bool = False
        operation_type: str = ""
        error: Optional[str] = None

    @dataclass
    class Event:
        type: str = ""
        data: Dict[str, Any] = field(default_factory=dict)

# Try to import Universal Bridge (optional - falls back to mock)
try:
    # Handle both hyphenated directory name and module import
    bridge_path = Path(__file__).parent / "universal-bridge" / "core"
    if bridge_path.exists():
        sys.path.insert(0, str(bridge_path.parent.parent))
        sys.path.insert(0, str(bridge_path))

    from universal_protocol import (
        UniversalMessage,
        MessageType,
        CommunicationChannel,
        UniversalBridge
    )
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    # Mock classes for standalone operation
    class MessageType(Enum):
        AI_REQUEST = "ai_request"
        AI_RESPONSE = "ai_response"
        DATA_SYNC = "data_sync"
        ERROR = "error"

    class CommunicationChannel(Enum):
        WEBSOCKET = "websocket"
        FILE_SYSTEM = "file_system"

    class UniversalMessage:
        def __init__(self, msg_type, source, target, payload, channel):
            self.id = str(uuid.uuid4())
            self.message_type = msg_type
            self.source_language = source
            self.target_language = target
            self.payload = payload
            self.response_channel = channel

    class UniversalBridge:
        def __init__(self, *args, **kwargs): pass
        def register_language_handler(self, *args): pass
        def send_message(self, msg): pass

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class ShopifyConfig:
    """Shopify store configuration"""
    store_domain: str = "ng3ykv-h7.myshopify.com"
    api_version: str = field(default_factory=lambda: os.environ.get("SHOPIFY_API_VERSION", "2024-01"))
    access_token: str = field(default_factory=lambda: os.environ.get("SHOPIFY_ACCESS_TOKEN", ""))
    api_key: str = field(default_factory=lambda: os.environ.get("SHOPIFY_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.environ.get("SHOPIFY_API_SECRET", ""))

    # Pricing settings
    default_markup_percent: float = 50.0  # 50% markup by default
    ideal_margin_percent: float = 60.0    # Ideal: 60%+ margin
    natural_margin_percent: float = 40.0  # Natural: 40-60% margin
    bad_margin_percent: float = 20.0      # Bad: 20-40% margin
    loss_margin_percent: float = 0.0      # Loss: <20% margin

    # Auto-pricing settings
    auto_round_prices: bool = True
    price_ending: str = ".99"
    minimum_profit_usd: float = 5.0

    def get_api_url(self, endpoint: str) -> str:
        """Get full API URL for endpoint"""
        return f"https://{self.store_domain}/admin/api/{self.api_version}/{endpoint}"


# =============================================================================
# MARGIN CLASSIFICATION
# =============================================================================

class MarginCategory(Enum):
    """Profit margin categories"""
    IDEAL = "ideal"       # 60%+ margin - excellent, auto-approve
    NATURAL = "natural"   # 40-60% margin - good, auto-approve
    BAD = "bad"           # 20-40% margin - marginal, review recommended
    LOSS = "loss"         # <20% margin - losing money, reject


@dataclass
class PricingAnalysis:
    """Result of pricing analysis"""
    wholesale_cost: float
    recommended_price: float
    profit_usd: float
    margin_percent: float
    category: MarginCategory
    auto_approve: bool
    reasoning: str
    comparison_prices: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['category'] = self.category.value
        return data


@dataclass
class WholesaleProduct:
    """Product from wholesaler API"""
    id: str
    name: str
    description: str
    wholesale_price: float
    msrp: float
    category: str
    supplier: str
    sku: str
    images: List[str] = field(default_factory=list)
    variants: List[Dict[str, Any]] = field(default_factory=list)
    inventory: int = 0
    shipping_weight: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShopifyProduct:
    """Product ready for Shopify"""
    id: Optional[str] = None
    title: str = ""
    body_html: str = ""
    vendor: str = ""
    product_type: str = ""
    price: float = 0.0
    compare_at_price: Optional[float] = None
    sku: str = ""
    inventory_quantity: int = 0
    images: List[Dict[str, str]] = field(default_factory=list)
    variants: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    status: str = "draft"
    pricing_analysis: Optional[PricingAnalysis] = None
    source_product: Optional[WholesaleProduct] = None

    def to_shopify_payload(self) -> Dict[str, Any]:
        """Convert to Shopify API payload"""
        payload = {
            "product": {
                "title": self.title,
                "body_html": self.body_html,
                "vendor": self.vendor,
                "product_type": self.product_type,
                "tags": ", ".join(self.tags),
                "status": self.status,
                "variants": [
                    {
                        "price": str(self.price),
                        "compare_at_price": str(self.compare_at_price) if self.compare_at_price else None,
                        "sku": self.sku,
                        "inventory_quantity": self.inventory_quantity,
                        "inventory_management": "shopify"
                    }
                ] if not self.variants else self.variants,
                "images": self.images
            }
        }
        return payload


@dataclass
class ProductFinderResult:
    """Result of product finding operation"""
    success: bool
    products: List[WholesaleProduct] = field(default_factory=list)
    total_found: int = 0
    suppliers_searched: List[str] = field(default_factory=list)
    search_query: str = ""
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    ai_recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "success": self.success,
            "products": [p.to_dict() for p in self.products],
            "total_found": self.total_found,
            "suppliers_searched": self.suppliers_searched,
            "search_query": self.search_query,
            "filters_applied": self.filters_applied,
            "ai_recommendations": self.ai_recommendations,
            "error": self.error,
            "timestamp": self.timestamp
        }
        return data


# =============================================================================
# WHOLESALER INTEGRATIONS
# =============================================================================

class WholesalerAPI:
    """Base class for wholesaler API integrations"""

    def __init__(self, api_key: str = "", api_url: str = ""):
        self.api_key = api_key or os.environ.get("WHOLESALER_API_KEY", "")
        self.api_url = api_url
        self.name = "base"

    def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[WholesaleProduct]:
        """Search for products - override in subclasses"""
        raise NotImplementedError

    def get_product_details(self, product_id: str) -> Optional[WholesaleProduct]:
        """Get detailed product info - override in subclasses"""
        raise NotImplementedError


class AliExpressWholesaler(WholesalerAPI):
    """AliExpress dropshipping integration"""

    def __init__(self):
        super().__init__(
            api_key=os.environ.get("ALIEXPRESS_API_KEY", ""),
            api_url="https://api.aliexpress.com/v1"
        )
        self.name = "aliexpress"

    def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[WholesaleProduct]:
        """Search AliExpress products"""
        filters = filters or {}

        # Simulated search with realistic product data
        # In production, this would make actual API calls
        sample_products = self._get_sample_products(query, filters)
        return sample_products

    def _get_sample_products(self, query: str, filters: Dict[str, Any]) -> List[WholesaleProduct]:
        """Generate sample products for demonstration"""
        products = []

        categories = {
            "electronics": [
                ("Wireless Bluetooth Earbuds Pro", 8.50, 49.99, "earbuds_001"),
                ("Smart Watch Fitness Tracker", 12.00, 79.99, "watch_001"),
                ("Portable Phone Charger 20000mAh", 7.50, 39.99, "charger_001"),
                ("LED Desk Lamp with USB Port", 6.00, 34.99, "lamp_001"),
                ("Mini Projector HD 1080P", 45.00, 149.99, "projector_001"),
            ],
            "home": [
                ("Automatic Soap Dispenser", 5.00, 29.99, "soap_001"),
                ("Smart LED Strip Lights 10m", 8.00, 44.99, "lights_001"),
                ("Robot Vacuum Cleaner", 65.00, 199.99, "vacuum_001"),
                ("Air Purifier HEPA Filter", 25.00, 89.99, "purifier_001"),
                ("Electric Kettle Temperature Control", 12.00, 54.99, "kettle_001"),
            ],
            "fashion": [
                ("Canvas Backpack Waterproof", 9.00, 49.99, "backpack_001"),
                ("Stainless Steel Watch Minimalist", 15.00, 89.99, "fwatch_001"),
                ("Leather Wallet RFID Block", 6.00, 34.99, "wallet_001"),
                ("Sunglasses Polarized UV400", 4.00, 29.99, "sunglasses_001"),
                ("Sport Running Shoes", 18.00, 79.99, "shoes_001"),
            ],
            "default": [
                ("Premium Quality Product", 10.00, 49.99, "default_001"),
                ("Best Seller Item", 15.00, 69.99, "default_002"),
                ("Top Rated Product", 8.00, 39.99, "default_003"),
            ]
        }

        # Determine category from query
        query_lower = query.lower()
        category = "default"
        for cat in categories:
            if cat in query_lower or any(word in query_lower for word in cat.split()):
                category = cat
                break

        product_list = categories.get(category, categories["default"])

        for name, cost, msrp, sku in product_list:
            if query_lower in name.lower() or query_lower in category:
                product = WholesaleProduct(
                    id=f"ae_{sku}_{uuid.uuid4().hex[:8]}",
                    name=name,
                    description=f"High-quality {name.lower()}. {category.title()} category. Fast shipping available.",
                    wholesale_price=cost,
                    msrp=msrp,
                    category=category,
                    supplier=self.name,
                    sku=sku,
                    images=[f"https://example.com/images/{sku}.jpg"],
                    inventory=100,
                    shipping_weight=0.5,
                    metadata={
                        "rating": 4.5,
                        "reviews": 1250,
                        "orders": 5000,
                        "shipping_time": "7-15 days"
                    }
                )
                products.append(product)

        return products


class SpocketWholesaler(WholesalerAPI):
    """Spocket dropshipping integration (US/EU suppliers)"""

    def __init__(self):
        super().__init__(
            api_key=os.environ.get("SPOCKET_API_KEY", ""),
            api_url="https://api.spocket.co/v1"
        )
        self.name = "spocket"

    def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[WholesaleProduct]:
        """Search Spocket products (US/EU fast shipping)"""
        filters = filters or {}

        # Simulated search
        sample_products = self._get_sample_products(query, filters)
        return sample_products

    def _get_sample_products(self, query: str, filters: Dict[str, Any]) -> List[WholesaleProduct]:
        """Generate sample US/EU products"""
        products = []

        # US/EU products have higher costs but faster shipping
        product_data = [
            ("Premium Organic Coffee Beans 1lb", 12.00, 34.99, "coffee_001", "food"),
            ("Handmade Scented Candles Set", 8.00, 29.99, "candles_001", "home"),
            ("Bamboo Cutting Board Set", 15.00, 44.99, "bamboo_001", "kitchen"),
            ("Natural Skincare Gift Set", 20.00, 59.99, "skincare_001", "beauty"),
            ("Eco-Friendly Yoga Mat", 18.00, 54.99, "yoga_001", "fitness"),
        ]

        query_lower = query.lower()
        for name, cost, msrp, sku, category in product_data:
            if query_lower in name.lower() or query_lower in category:
                product = WholesaleProduct(
                    id=f"sp_{sku}_{uuid.uuid4().hex[:8]}",
                    name=f"{name} (USA)",
                    description=f"Premium {name.lower()}. Ships from USA warehouse. 2-5 day delivery.",
                    wholesale_price=cost,
                    msrp=msrp,
                    category=category,
                    supplier=self.name,
                    sku=f"US_{sku}",
                    images=[f"https://example.com/images/{sku}.jpg"],
                    inventory=50,
                    shipping_weight=0.8,
                    metadata={
                        "warehouse": "USA",
                        "shipping_time": "2-5 days",
                        "quality_verified": True
                    }
                )
                products.append(product)

        return products


class ModalystWholesaler(WholesalerAPI):
    """Modalyst integration (fashion/apparel focus)"""

    def __init__(self):
        super().__init__(
            api_key=os.environ.get("MODALYST_API_KEY", ""),
            api_url="https://api.modalyst.co/v1"
        )
        self.name = "modalyst"

    def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[WholesaleProduct]:
        """Search Modalyst products (fashion/apparel)"""
        filters = filters or {}

        sample_products = self._get_sample_products(query, filters)
        return sample_products

    def _get_sample_products(self, query: str, filters: Dict[str, Any]) -> List[WholesaleProduct]:
        """Generate sample fashion products"""
        products = []

        product_data = [
            ("Designer Leather Handbag", 35.00, 129.99, "handbag_001", "accessories"),
            ("Silk Scarf Collection", 12.00, 49.99, "scarf_001", "accessories"),
            ("Vintage Denim Jacket", 28.00, 89.99, "denim_001", "clothing"),
            ("Bohemian Maxi Dress", 22.00, 79.99, "dress_001", "clothing"),
            ("Sterling Silver Jewelry Set", 18.00, 69.99, "jewelry_001", "jewelry"),
        ]

        query_lower = query.lower()
        for name, cost, msrp, sku, category in product_data:
            if query_lower in name.lower() or query_lower in category or "fashion" in query_lower:
                product = WholesaleProduct(
                    id=f"mod_{sku}_{uuid.uuid4().hex[:8]}",
                    name=name,
                    description=f"Fashion-forward {name.lower()}. Trendy design. High quality materials.",
                    wholesale_price=cost,
                    msrp=msrp,
                    category=category,
                    supplier=self.name,
                    sku=f"MOD_{sku}",
                    images=[f"https://example.com/images/{sku}.jpg"],
                    inventory=25,
                    shipping_weight=0.4,
                    metadata={
                        "style": "trendy",
                        "material_quality": "premium",
                        "return_policy": "30 days"
                    }
                )
                products.append(product)

        return products


# =============================================================================
# PROFIT MARGIN CALCULATOR
# =============================================================================

class ProfitMarginCalculator:
    """
    Calculate profit margins and categorize them.

    Categories:
    - IDEAL (60%+): Excellent margin, auto-approve immediately
    - NATURAL (40-60%): Good margin, auto-approve
    - BAD (20-40%): Marginal, review recommended
    - LOSS (<20%): Losing money, reject
    """

    def __init__(self, config: ShopifyConfig):
        self.config = config

    def calculate_margin(
        self,
        wholesale_cost: float,
        selling_price: float,
        additional_costs: float = 0.0
    ) -> Tuple[float, float, MarginCategory]:
        """
        Calculate profit margin and categorize.

        Returns: (profit_usd, margin_percent, category)
        """
        total_cost = wholesale_cost + additional_costs
        profit = selling_price - total_cost

        if selling_price > 0:
            margin_percent = (profit / selling_price) * 100
        else:
            margin_percent = 0.0

        # Categorize margin
        if margin_percent >= self.config.ideal_margin_percent:
            category = MarginCategory.IDEAL
        elif margin_percent >= self.config.natural_margin_percent:
            category = MarginCategory.NATURAL
        elif margin_percent >= self.config.bad_margin_percent:
            category = MarginCategory.BAD
        else:
            category = MarginCategory.LOSS

        return profit, margin_percent, category

    def calculate_recommended_price(
        self,
        wholesale_cost: float,
        target_category: MarginCategory = MarginCategory.NATURAL,
        additional_costs: float = 0.0,
        competitor_prices: List[float] = None
    ) -> PricingAnalysis:
        """
        Calculate recommended selling price for target margin.
        """
        total_cost = wholesale_cost + additional_costs
        competitor_prices = competitor_prices or []

        # Target margin based on category
        target_margins = {
            MarginCategory.IDEAL: self.config.ideal_margin_percent / 100,
            MarginCategory.NATURAL: self.config.natural_margin_percent / 100,
            MarginCategory.BAD: self.config.bad_margin_percent / 100,
            MarginCategory.LOSS: 0.15  # Minimum 15% to not lose money
        }

        target_margin = target_margins[target_category]

        # Calculate base price: price = cost / (1 - margin)
        if target_margin < 1:
            base_price = total_cost / (1 - target_margin)
        else:
            base_price = total_cost * 2

        # Consider competitor prices
        if competitor_prices:
            avg_competitor = sum(competitor_prices) / len(competitor_prices)
            # Stay within 20% of competitor average
            min_competitive = avg_competitor * 0.8
            max_competitive = avg_competitor * 1.2

            if base_price < min_competitive:
                base_price = min_competitive
            elif base_price > max_competitive:
                # Adjust to be competitive but still profitable
                if min_competitive > total_cost * 1.2:
                    base_price = min_competitive

        # Round price if configured
        if self.config.auto_round_prices:
            recommended_price = self._round_price(base_price)
        else:
            recommended_price = round(base_price, 2)

        # Ensure minimum profit
        if recommended_price - total_cost < self.config.minimum_profit_usd:
            recommended_price = total_cost + self.config.minimum_profit_usd
            recommended_price = self._round_price(recommended_price)

        # Final calculations
        profit, margin_percent, actual_category = self.calculate_margin(
            wholesale_cost, recommended_price, additional_costs
        )

        # Determine if auto-approve
        auto_approve = actual_category in [MarginCategory.IDEAL, MarginCategory.NATURAL]

        # Generate reasoning
        reasoning = self._generate_reasoning(
            wholesale_cost, recommended_price, profit, margin_percent,
            actual_category, competitor_prices
        )

        return PricingAnalysis(
            wholesale_cost=wholesale_cost,
            recommended_price=recommended_price,
            profit_usd=profit,
            margin_percent=margin_percent,
            category=actual_category,
            auto_approve=auto_approve,
            reasoning=reasoning,
            comparison_prices={
                "competitor_avg": sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0,
                "msrp": wholesale_cost * 3  # Typical MSRP multiplier
            }
        )

    def _round_price(self, price: float) -> float:
        """Round price to psychological pricing point"""
        if self.config.price_ending == ".99":
            return float(int(price)) + 0.99
        elif self.config.price_ending == ".95":
            return float(int(price)) + 0.95
        else:
            return round(price, 2)

    def _generate_reasoning(
        self,
        cost: float,
        price: float,
        profit: float,
        margin: float,
        category: MarginCategory,
        competitor_prices: List[float]
    ) -> str:
        """Generate human-readable pricing reasoning"""
        reasoning = f"Cost: ${cost:.2f} -> Price: ${price:.2f} = ${profit:.2f} profit ({margin:.1f}% margin). "

        if category == MarginCategory.IDEAL:
            reasoning += "IDEAL margin - excellent profitability, highly recommended for listing."
        elif category == MarginCategory.NATURAL:
            reasoning += "NATURAL margin - good sustainable profit, recommended for listing."
        elif category == MarginCategory.BAD:
            reasoning += "BAD margin - marginal profit, consider higher pricing or different product."
        else:
            reasoning += "LOSS - not profitable, recommend skipping this product."

        if competitor_prices:
            avg = sum(competitor_prices) / len(competitor_prices)
            if price < avg:
                reasoning += f" Price is below competitor average (${avg:.2f})."
            else:
                reasoning += f" Price is competitive with market (avg ${avg:.2f})."

        return reasoning


# =============================================================================
# SHOPIFY API CLIENT
# =============================================================================

class ShopifyAPIClient:
    """Client for Shopify Admin API"""

    def __init__(self, config: ShopifyConfig):
        self.config = config
        self._session = None

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            "X-Shopify-Access-Token": self.config.access_token,
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """Make API request with retry logic"""
        url = self.config.get_api_url(endpoint)
        headers = self._get_headers()

        for attempt in range(retry_count):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=30)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                elif method.upper() == "PUT":
                    response = requests.put(url, headers=headers, json=data, timeout=30)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

        return {}

    def create_product(self, product: ShopifyProduct) -> Dict[str, Any]:
        """Create product in Shopify"""
        payload = product.to_shopify_payload()
        result = self._make_request("POST", "products.json", payload)

        if "product" in result:
            product.id = str(result["product"]["id"])
            logger.info(f"Created Shopify product: {product.title} (ID: {product.id})")

        return result

    def update_product(self, product_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing product"""
        payload = {"product": updates}
        return self._make_request("PUT", f"products/{product_id}.json", payload)

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get product by ID"""
        return self._make_request("GET", f"products/{product_id}.json")

    def list_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all products"""
        result = self._make_request("GET", f"products.json?limit={limit}")
        return result.get("products", [])

    def delete_product(self, product_id: str) -> bool:
        """Delete product"""
        try:
            self._make_request("DELETE", f"products/{product_id}.json")
            return True
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            return False

    def update_inventory(self, inventory_item_id: str, quantity: int) -> Dict[str, Any]:
        """Update inventory quantity"""
        payload = {
            "inventory_level": {
                "inventory_item_id": inventory_item_id,
                "available": quantity
            }
        }
        return self._make_request("POST", "inventory_levels/set.json", payload)


# =============================================================================
# AI-POWERED PRODUCT FINDER
# =============================================================================

class AIProductFinder:
    """
    AI-powered product discovery and recommendation engine.
    Uses AWS Bedrock for intelligent product selection and pricing.
    """

    def __init__(self, config: ShopifyConfig, bedrock_client: BedrockClient):
        self.config = config
        self.bedrock_client = bedrock_client
        self.margin_calculator = ProfitMarginCalculator(config)

        # Check if AWS credentials are available
        self.ai_enabled = self._check_aws_credentials()

        # Initialize wholesaler connections
        self.wholesalers = [
            AliExpressWholesaler(),
            SpocketWholesaler(),
            ModalystWholesaler()
        ]

    def _check_aws_credentials(self) -> bool:
        """Check if AWS credentials are available for Bedrock"""
        # Check environment variables
        if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            return True
        # Check for AWS config file
        aws_config = Path.home() / ".aws" / "credentials"
        if aws_config.exists():
            return True
        # Check for environment skip flag
        if os.environ.get("SKIP_AI_CALLS", "").lower() in ("true", "1", "yes"):
            return False
        # Default: disabled in test environments
        if os.environ.get("ENVIRONMENT", "").lower() in ("test", "development"):
            return False
        return False

    async def find_products(
        self,
        user_request: str,
        max_results: int = 20,
        min_margin: MarginCategory = MarginCategory.NATURAL
    ) -> ProductFinderResult:
        """
        Find products based on natural language request.

        Example: "find me products" or "electronics under $50" or "trending home decor"
        """

        # Step 1: Use AI to understand the request and generate search queries
        search_analysis = await self._analyze_request(user_request)

        # Step 2: Search all wholesalers
        all_products = []
        suppliers_searched = []

        for query in search_analysis.get("search_queries", [user_request]):
            for wholesaler in self.wholesalers:
                try:
                    products = wholesaler.search_products(
                        query,
                        filters=search_analysis.get("filters", {})
                    )
                    all_products.extend(products)
                    if wholesaler.name not in suppliers_searched:
                        suppliers_searched.append(wholesaler.name)
                except Exception as e:
                    logger.warning(f"Error searching {wholesaler.name}: {e}")

        # Step 3: Analyze margins and filter
        analyzed_products = []
        for product in all_products:
            pricing = self.margin_calculator.calculate_recommended_price(
                product.wholesale_price,
                target_category=min_margin
            )

            # Only include products meeting margin requirements
            if pricing.category.value <= min_margin.value or pricing.auto_approve:
                product.metadata["pricing_analysis"] = pricing.to_dict()
                analyzed_products.append(product)

        # Step 4: AI ranking and recommendations
        if analyzed_products:
            recommendations = await self._get_ai_recommendations(
                analyzed_products[:max_results],
                user_request
            )
        else:
            recommendations = ["No products found matching your criteria. Try broader search terms."]

        # Sort by margin (best first)
        analyzed_products.sort(
            key=lambda p: p.metadata.get("pricing_analysis", {}).get("margin_percent", 0),
            reverse=True
        )

        return ProductFinderResult(
            success=len(analyzed_products) > 0,
            products=analyzed_products[:max_results],
            total_found=len(analyzed_products),
            suppliers_searched=suppliers_searched,
            search_query=user_request,
            filters_applied=search_analysis.get("filters", {}),
            ai_recommendations=recommendations
        )

    async def _analyze_request(self, user_request: str) -> Dict[str, Any]:
        """Use AI to analyze and expand the user's product request"""

        # Skip AI if credentials not available
        if not self.ai_enabled:
            return self._fallback_analyze_request(user_request)

        prompt = f"""Analyze this product search request and extract structured information.

User request: "{user_request}"

Return a JSON object with:
1. "search_queries": List of 2-3 search terms to try
2. "filters": Dict with optional filters like "max_price", "min_price", "category"
3. "intent": What the user is looking for
4. "suggestions": Any improvements to the search

IMPORTANT: Return ONLY valid JSON, no other text.

Example output:
{{"search_queries": ["wireless earbuds", "bluetooth headphones", "audio electronics"], "filters": {{"max_price": 50}}, "intent": "Find affordable audio products", "suggestions": ["Consider TWS models for higher margins"]}}
"""

        try:
            request = BedrockRequest(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )

            response = await self.bedrock_client.invoke_model(request)

            if response.success and response.content:
                # Parse JSON from response
                try:
                    # Extract JSON from response
                    content = response.content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]

                    return json.loads(content.strip())
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI response as JSON")
        except Exception as e:
            logger.error(f"AI request analysis failed: {e}")

        # Fallback to basic parsing
        return self._fallback_analyze_request(user_request)

    def _fallback_analyze_request(self, user_request: str) -> Dict[str, Any]:
        """Fallback request analysis without AI"""
        request_lower = user_request.lower()

        # Extract common keywords
        categories = ["electronics", "home", "fashion", "beauty", "fitness", "kitchen", "outdoor"]
        detected_category = next((c for c in categories if c in request_lower), None)

        # Generate related search queries
        search_queries = []

        if detected_category:
            search_queries.append(detected_category)
        elif "product" in request_lower or "find" in request_lower:
            # Generic request - search multiple popular categories
            search_queries = ["electronics", "home", "fashion"]
        else:
            search_queries = [user_request]

        # Ensure we have at least one query
        if not search_queries:
            search_queries = ["electronics"]

        return {
            "search_queries": search_queries[:3],
            "filters": {},
            "intent": user_request,
            "suggestions": ["AI analysis unavailable - using keyword matching"]
        }

    async def _get_ai_recommendations(
        self,
        products: List[WholesaleProduct],
        user_request: str
    ) -> List[str]:
        """Get AI recommendations for the found products"""

        # Skip AI if credentials not available
        if not self.ai_enabled:
            return self._fallback_recommendations(products)

        product_summaries = []
        for p in products[:10]:  # Limit to 10 for context
            pricing = p.metadata.get("pricing_analysis", {})
            product_summaries.append(
                f"- {p.name}: ${p.wholesale_price:.2f} cost, "
                f"{pricing.get('margin_percent', 0):.1f}% margin, "
                f"{pricing.get('category', 'unknown')} category"
            )

        prompt = f"""Based on the user's search "{user_request}" and these products found:

{chr(10).join(product_summaries)}

Provide 3-5 brief, actionable recommendations for the seller. Focus on:
1. Which products offer best profit potential
2. Any market trends relevant to these products
3. Pricing strategy suggestions
4. Any risks to consider

Keep each recommendation to 1-2 sentences. Return as a JSON array of strings.

Example: ["The wireless earbuds offer 65% margin - excellent for listing.", "Consider bundling related products for higher average order value."]"""

        try:
            request = BedrockRequest(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                prompt=prompt,
                max_tokens=500,
                temperature=0.5
            )

            response = await self.bedrock_client.invoke_model(request)

            if response.success and response.content:
                try:
                    content = response.content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]

                    return json.loads(content.strip())
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error(f"AI recommendations failed: {e}")

        return self._fallback_recommendations(products)

    def _fallback_recommendations(self, products: List[WholesaleProduct]) -> List[str]:
        """Generate recommendations without AI"""
        recommendations = [
            f"Found {len(products)} products matching your search.",
            "Products are sorted by profit margin (highest first).",
        ]

        # Add margin-based recommendations
        ideal_count = sum(1 for p in products if p.metadata.get("pricing_analysis", {}).get("category") == "ideal")
        if ideal_count > 0:
            recommendations.append(f"{ideal_count} products have IDEAL margins (60%+) - highly recommended.")

        natural_count = sum(1 for p in products if p.metadata.get("pricing_analysis", {}).get("category") == "natural")
        if natural_count > 0:
            recommendations.append(f"{natural_count} products have NATURAL margins (40-60%) - good for listing.")

        recommendations.append("Review pricing analysis before listing.")
        return recommendations


# =============================================================================
# ZERO-CLICK STORE MANAGER
# =============================================================================

class ZeroClickStoreManager:
    """
    Zero-click store management - handles everything automatically.

    User says: "find me products" -> AI does everything:
    1. Searches wholesalers
    2. Analyzes margins
    3. Creates Shopify listings
    4. Sets optimal pricing
    5. Reports results
    """

    def __init__(
        self,
        config: ShopifyConfig = None,
        aws_config: AWSConfigManager = None,
        dry_run: bool = None
    ):
        self.config = config or ShopifyConfig()
        self.aws_config = aws_config or AWSConfigManager()
        self.bedrock_client = BedrockClient(self.aws_config)
        self.shopify_client = ShopifyAPIClient(self.config)
        self.product_finder = AIProductFinder(self.config, self.bedrock_client)
        self.margin_calculator = ProfitMarginCalculator(self.config)

        # Dry run mode - skip actual Shopify API calls
        if dry_run is None:
            self.dry_run = os.environ.get("DRY_RUN", "").lower() in ("true", "1", "yes") or \
                           os.environ.get("ENVIRONMENT", "").lower() in ("test", "development") or \
                           not self.config.access_token
        else:
            self.dry_run = dry_run

        # Bridge for inter-AI communication
        self.bridge = None
        self._setup_bridge()

    def _setup_bridge(self):
        """Setup Universal Bridge for communication"""
        try:
            self.bridge = UniversalBridge(port=8766)
            self.bridge.register_language_handler("python", self._handle_bridge_message)
            logger.info("Universal Bridge connected for inter-AI communication")
        except Exception as e:
            logger.warning(f"Bridge setup optional, continuing without: {e}")

    def _handle_bridge_message(self, function_name: str, args: list, kwargs: dict) -> Any:
        """Handle messages from other AI systems"""
        handlers = {
            "find_products": lambda: asyncio.run(self.find_and_list_products(args[0] if args else "trending")),
            "get_store_status": self.get_store_status,
            "optimize_pricing": lambda: self.optimize_all_prices(),
        }

        handler = handlers.get(function_name)
        if handler:
            return handler()
        return {"error": f"Unknown function: {function_name}"}

    async def process_user_request(self, request: str) -> Dict[str, Any]:
        """
        Main entry point - process natural language request.

        Examples:
        - "find me products"
        - "add 10 electronics products"
        - "find home decor items"
        - "optimize my store pricing"
        """
        request_lower = request.lower()

        # Determine action from request
        if any(word in request_lower for word in ["find", "search", "look", "get", "add"]):
            # Product finding and listing flow
            result = await self.find_and_list_products(request)
            return result

        elif "optimize" in request_lower or "pricing" in request_lower:
            # Price optimization flow
            return self.optimize_all_prices()

        elif "status" in request_lower or "report" in request_lower:
            # Store status report
            return self.get_store_status()

        else:
            # Default: treat as product search
            result = await self.find_and_list_products(request)
            return result

    async def find_and_list_products(
        self,
        request: str,
        auto_list: bool = True,
        max_products: int = 10
    ) -> Dict[str, Any]:
        """
        Find products and optionally auto-list them to Shopify.
        """
        start_time = time.time()

        # Step 1: Find products
        logger.info(f"Processing request: {request}")
        finder_result = await self.product_finder.find_products(
            request,
            max_results=max_products * 2  # Get more to filter
        )

        if not finder_result.success:
            return {
                "success": False,
                "message": "No products found",
                "error": finder_result.error,
                "recommendations": finder_result.ai_recommendations
            }

        # Step 2: Filter to auto-approvable products only
        approvable_products = []
        for product in finder_result.products:
            pricing = product.metadata.get("pricing_analysis", {})
            if pricing.get("auto_approve", False):
                approvable_products.append(product)

            if len(approvable_products) >= max_products:
                break

        # Step 3: Create Shopify listings if auto_list enabled
        listed_products = []
        failed_products = []

        if auto_list and approvable_products and not self.dry_run:
            for wholesale_product in approvable_products:
                try:
                    shopify_product = self._create_shopify_product(wholesale_product)
                    result = self.shopify_client.create_product(shopify_product)

                    if "product" in result:
                        listed_products.append({
                            "title": shopify_product.title,
                            "id": result["product"]["id"],
                            "price": shopify_product.price,
                            "margin": shopify_product.pricing_analysis.margin_percent if shopify_product.pricing_analysis else 0
                        })
                    else:
                        failed_products.append({
                            "title": wholesale_product.name,
                            "error": "API response missing product"
                        })

                except Exception as e:
                    failed_products.append({
                        "title": wholesale_product.name,
                        "error": str(e)
                    })
        elif self.dry_run and approvable_products:
            # In dry run mode, simulate successful listing
            for wholesale_product in approvable_products:
                shopify_product = self._create_shopify_product(wholesale_product)
                listed_products.append({
                    "title": shopify_product.title,
                    "id": f"dry_run_{uuid.uuid4().hex[:8]}",
                    "price": shopify_product.price,
                    "margin": shopify_product.pricing_analysis.margin_percent if shopify_product.pricing_analysis else 0,
                    "dry_run": True
                })

        duration = time.time() - start_time

        # Send bridge message about completed operation
        if self.bridge:
            message = UniversalMessage(
                MessageType.DATA_SYNC,
                "shopify_connector",
                "ai_neural_spine",
                {
                    "action": "products_listed",
                    "count": len(listed_products),
                    "total_found": finder_result.total_found,
                    "suppliers": finder_result.suppliers_searched
                },
                CommunicationChannel.FILE_SYSTEM
            )
            self.bridge.send_message(message)

        message = f"Found {finder_result.total_found} products"
        if self.dry_run:
            message += f", simulated listing {len(listed_products)} (DRY RUN)"
        else:
            message += f", listed {len(listed_products)} to Shopify"

        return {
            "success": True,
            "message": message,
            "products_found": finder_result.total_found,
            "products_listed": len(listed_products),
            "listed_products": listed_products,
            "failed_products": failed_products,
            "suppliers_searched": finder_result.suppliers_searched,
            "ai_recommendations": finder_result.ai_recommendations,
            "duration_seconds": round(duration, 2),
            "auto_approved": len([p for p in listed_products if p]),
            "pending_review": len(approvable_products) - len(listed_products),
            "dry_run": self.dry_run
        }

    def _create_shopify_product(self, wholesale: WholesaleProduct) -> ShopifyProduct:
        """Convert wholesale product to Shopify product"""
        pricing = wholesale.metadata.get("pricing_analysis", {})

        if not pricing:
            pricing_analysis = self.margin_calculator.calculate_recommended_price(
                wholesale.wholesale_price
            )
        else:
            pricing_analysis = PricingAnalysis(
                wholesale_cost=pricing.get("wholesale_cost", wholesale.wholesale_price),
                recommended_price=pricing.get("recommended_price", wholesale.msrp),
                profit_usd=pricing.get("profit_usd", 0),
                margin_percent=pricing.get("margin_percent", 0),
                category=MarginCategory(pricing.get("category", "natural")),
                auto_approve=pricing.get("auto_approve", False),
                reasoning=pricing.get("reasoning", "")
            )

        # Generate enhanced description
        description = f"""
<div class="product-description">
    <h3>Product Overview</h3>
    <p>{wholesale.description}</p>

    <h3>Key Features</h3>
    <ul>
        <li>High Quality Materials</li>
        <li>Fast Shipping Available</li>
        <li>Satisfaction Guaranteed</li>
    </ul>

    <p><strong>Category:</strong> {wholesale.category.title()}</p>
</div>
"""

        return ShopifyProduct(
            title=wholesale.name,
            body_html=description,
            vendor=wholesale.supplier.title(),
            product_type=wholesale.category.title(),
            price=pricing_analysis.recommended_price,
            compare_at_price=wholesale.msrp if wholesale.msrp > pricing_analysis.recommended_price else None,
            sku=wholesale.sku,
            inventory_quantity=min(wholesale.inventory, 100),  # Cap at 100
            images=[{"src": img} for img in wholesale.images] if wholesale.images else [],
            tags=[
                wholesale.category,
                wholesale.supplier,
                pricing_analysis.category.value + "_margin"
            ],
            status="active" if pricing_analysis.auto_approve else "draft",
            pricing_analysis=pricing_analysis,
            source_product=wholesale
        )

    def optimize_all_prices(self) -> Dict[str, Any]:
        """Optimize pricing for all store products"""
        try:
            products = self.shopify_client.list_products()
            optimized = 0

            for product in products:
                # Check current margins and optimize if needed
                current_price = float(product.get("variants", [{}])[0].get("price", 0))
                # Optimization logic would go here
                optimized += 1

            return {
                "success": True,
                "message": f"Analyzed {len(products)} products",
                "products_optimized": optimized
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_store_status(self) -> Dict[str, Any]:
        """Get comprehensive store status"""
        try:
            products = self.shopify_client.list_products()

            # Analyze margins
            margin_distribution = {
                "ideal": 0,
                "natural": 0,
                "bad": 0,
                "loss": 0
            }

            total_revenue_potential = 0
            total_products = len(products)

            for product in products:
                price = float(product.get("variants", [{}])[0].get("price", 0))
                total_revenue_potential += price

            return {
                "success": True,
                "store": self.config.store_domain,
                "total_products": total_products,
                "total_revenue_potential": total_revenue_potential,
                "margin_distribution": margin_distribution,
                "status": "healthy" if total_products > 0 else "empty"
            }
        except Exception as e:
            return {
                "success": False,
                "store": self.config.store_domain,
                "error": str(e)
            }


# =============================================================================
# LAMBDA HANDLER
# =============================================================================

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler for Shopify connector.

    Supports actions:
    - find_products: Find and list products
    - process_request: Process natural language request
    - get_status: Get store status
    - optimize_prices: Optimize all prices
    """
    try:
        # Parse event
        if "body" in event:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event

        action = body.get("action", "process_request")
        request = body.get("request", body.get("query", "find me products"))

        # Initialize manager
        manager = ZeroClickStoreManager()

        # Route to action
        if action == "find_products" or action == "process_request":
            result = asyncio.run(manager.process_user_request(request))
        elif action == "get_status":
            result = manager.get_store_status()
        elif action == "optimize_prices":
            result = manager.optimize_all_prices()
        else:
            result = {"error": f"Unknown action: {action}"}

        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str)
        }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# =============================================================================
# ENHANCED STORE MANAGER (with Intelligence Modules)
# =============================================================================

class EnhancedStoreManager(ZeroClickStoreManager):
    """
    Enhanced store manager with e-commerce intelligence capabilities.
    Adds competitor analysis, trend detection, and health monitoring.
    """

    def __init__(self, config: ShopifyConfig = None, dry_run: bool = None):
        super().__init__(config, dry_run)

        # Initialize intelligence modules if available
        if INTELLIGENCE_AVAILABLE:
            self.product_analyzer = EnhancedProductAnalyzer()
            self.competitor_analyzer = CompetitorAnalyzer()
            self.trend_detector = TrendDetector()
            self.health_monitor = HealthMonitor()
            self.webhook_handler = WebhookHandler()
            logger.info("Intelligence modules loaded")
        else:
            self.product_analyzer = None
            self.competitor_analyzer = None
            self.trend_detector = None
            self.health_monitor = None
            self.webhook_handler = None
            logger.info("Intelligence modules not available - basic mode")

        # Initialize compatibility checker if available
        if COMPATIBILITY_CHECKER_AVAILABLE:
            self.compatibility_checker = PCCompatibilityChecker()
            logger.info("PC compatibility checker loaded")
        else:
            self.compatibility_checker = None

    def analyze_opportunity(
        self,
        product_name: str,
        wholesale_cost: float,
        selling_price: float,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Get comprehensive product opportunity analysis.
        Uses intelligence modules for deeper insights.
        """
        if not INTELLIGENCE_AVAILABLE or not self.product_analyzer:
            # Fallback to basic margin analysis
            margin = ((selling_price - wholesale_cost) / selling_price) * 100
            return {
                "product_name": product_name,
                "profit_margin": round(margin, 1),
                "overall_score": 50,
                "recommendation": "Intelligence modules not available - manual review recommended",
                "analysis_mode": "basic"
            }

        # Full intelligence analysis
        analysis = self.product_analyzer.analyze_product_opportunity(
            product_name, wholesale_cost, selling_price, category
        )
        analysis["analysis_mode"] = "enhanced"
        return analysis

    def get_trending_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get currently trending product categories"""
        if not INTELLIGENCE_AVAILABLE or not self.trend_detector:
            return [{"message": "Trend detection not available"}]

        return self.trend_detector.get_trending_categories(limit)

    def analyze_competitors(
        self,
        product_name: str,
        your_price: float,
        category: str = "general"
    ) -> Dict[str, Any]:
        """Analyze competitor pricing for a product"""
        if not INTELLIGENCE_AVAILABLE or not self.competitor_analyzer:
            return {"message": "Competitor analysis not available"}

        from dataclasses import asdict
        analysis = self.competitor_analyzer.analyze_product(
            product_name, your_price, category
        )
        return {
            "product_name": analysis.product_name,
            "your_price": analysis.your_price,
            "market_average": analysis.market_average,
            "market_low": analysis.market_low,
            "market_high": analysis.market_high,
            "price_position": analysis.price_position,
            "recommended_price": analysis.recommended_price,
            "competitive_score": analysis.competitive_score,
            "competitor_count": len(analysis.competitor_prices)
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        if not INTELLIGENCE_AVAILABLE or not self.health_monitor:
            return {
                "status": "unknown",
                "message": "Health monitoring not available"
            }

        health = self.health_monitor.check_health()
        return {
            "status": health.status.value,
            "uptime_seconds": health.uptime_seconds,
            "memory_usage_mb": health.memory_usage_mb,
            "cache_stats": health.cache_stats,
            "recommendations": health.recommendations,
            "checks": [
                {
                    "component": c.component,
                    "status": c.status.value,
                    "message": c.message
                }
                for c in health.checks
            ]
        }

    def check_pc_build_compatibility(self, build: Dict[str, Any]) -> Dict[str, Any]:
        """Check PC build component compatibility"""
        if not COMPATIBILITY_CHECKER_AVAILABLE or not self.compatibility_checker:
            return {
                "compatible": True,
                "message": "Compatibility checker not available - manual review required"
            }

        report = self.compatibility_checker.check_build_compatibility(build)
        return report.to_dict()

    async def smart_process_request(self, request: str) -> Dict[str, Any]:
        """
        Enhanced request processing with intelligence insights.
        Adds trend and competition data to results.
        """
        # Get base results
        result = await self.process_user_request(request)

        # Enhance with intelligence if available and successful
        if result.get("success") and INTELLIGENCE_AVAILABLE:
            # Add trending categories
            result["trending_categories"] = self.get_trending_products(5)

            # Add system health
            result["system_health"] = self.get_system_health()

            # Enhance listed products with intelligence
            if result.get("listed_products") and self.product_analyzer:
                for product in result["listed_products"]:
                    if "title" in product and "price" in product:
                        # Estimate wholesale cost from margin
                        margin = product.get("margin", 50)
                        price = product["price"]
                        estimated_cost = price * (1 - margin / 100)

                        # Get intelligence analysis
                        intel = self.analyze_opportunity(
                            product["title"],
                            estimated_cost,
                            price
                        )
                        product["intelligence"] = {
                            "overall_score": intel.get("overall_score"),
                            "trend": intel.get("trend", {}).get("direction"),
                            "competition": intel.get("competition", {}).get("price_position")
                        }

        return result


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for testing"""
    import sys

    print("=" * 60)
    print("SHOPIFY CONNECTOR - Zero-Click E-Commerce AI")
    print("=" * 60)
    print(f"Store: ng3ykv-h7.myshopify.com")
    print()

    # Default request or use command line
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = "find me products"

    print(f"Request: {request}")
    print("-" * 60)

    # Process request
    manager = ZeroClickStoreManager()
    result = asyncio.run(manager.process_user_request(request))

    # Display results
    print("\nRESULTS:")
    print("-" * 60)

    if result.get("success"):
        print(f"Status: SUCCESS")
        print(f"Message: {result.get('message')}")
        print(f"\nProducts Found: {result.get('products_found', 0)}")
        print(f"Products Listed: {result.get('products_listed', 0)}")
        print(f"Duration: {result.get('duration_seconds', 0)}s")

        if result.get("listed_products"):
            print("\nListed Products:")
            for p in result["listed_products"]:
                print(f"  - {p['title']}: ${p['price']:.2f} ({p['margin']:.1f}% margin)")

        if result.get("ai_recommendations"):
            print("\nAI Recommendations:")
            for rec in result["ai_recommendations"]:
                print(f"  - {rec}")
    else:
        print(f"Status: FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("=" * 60)


if __name__ == "__main__":
    main()
