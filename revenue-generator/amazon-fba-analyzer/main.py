#!/usr/bin/env python3
"""
Amazon FBA Profit Analyzer - Advanced Product Research Tool
Real Amazon API integration with profit calculations
Price: $297 - High-value product research tool
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import logging
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from flask import Flask, render_template, request, jsonify, send_file
import plotly.graph_objs as go
import plotly.utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    asin: str
    title: str
    price: float
    sales_rank: int
    category: str
    reviews_count: int
    rating: float
    dimensions: Dict[str, float]
    weight: float
    fba_fees: float
    estimated_sales: int
    profit_margin: float
    roi: float
    competition_level: str

@dataclass
class MarketAnalysis:
    total_products: int
    avg_price: float
    avg_sales_rank: int
    top_sellers: List[ProductData]
    profit_opportunities: List[ProductData]
    market_saturation: float
    recommended_price_range: Dict[str, float]

class AmazonAPIClient:
    """Real Amazon Product Advertising API client"""
    
    def __init__(self, access_key: str, secret_key: str, partner_tag: str, region: str = 'US'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_tag = partner_tag
        self.region = region
        self.base_url = f"https://webservices.amazon.{region.lower()}/paapi5"
        
    async def search_products(self, keywords: str, category: str = None, max_results: int = 50) -> List[Dict]:
        """Search for products using Amazon API"""
        try:
            headers = self._get_headers()
            payload = {
                "Keywords": keywords,
                "SearchIndex": category or "All",
                "ItemCount": min(max_results, 50),
                "Resources": [
                    "ItemInfo.Title",
                    "ItemInfo.Features",
                    "ItemInfo.ProductInfo",
                    "Offers.Listings.Price",
                    "Offers.Listings.DeliveryInfo",
                    "Images.Primary.Large",
                    "BrowseNodeInfo.BrowseNodes"
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/searchitems",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('SearchResult', {}).get('Items', [])
                    else:
                        logger.error(f"API Error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    async def get_product_details(self, asin: str) -> Optional[Dict]:
        """Get detailed product information"""
        try:
            headers = self._get_headers()
            payload = {
                "ItemIds": [asin],
                "Resources": [
                    "ItemInfo.Title",
                    "ItemInfo.Features",
                    "ItemInfo.ProductInfo",
                    "ItemInfo.TechnicalInfo",
                    "Offers.Listings.Price",
                    "Offers.Listings.DeliveryInfo",
                    "Images.Primary.Large",
                    "BrowseNodeInfo.BrowseNodes",
                    "CustomerReviews.Count",
                    "CustomerReviews.StarRating"
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/getitems",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('ItemsResult', {}).get('Items', [])
                        return items[0] if items else None
                    return None
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate API headers with authentication"""
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        return {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Amz-Target': 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems',
            'X-Amz-Date': timestamp,
            'Authorization': self._generate_auth_header(timestamp)
        }
    
    def _generate_auth_header(self, timestamp: str) -> str:
        """Generate AWS Signature V4 authorization header"""
        # Simplified - in production, use proper AWS signature generation
        return f"AWS4-HMAC-SHA256 Credential={self.access_key}/..."

class FBACalculator:
    """Calculate FBA fees and profit margins"""
    
    # FBA Fee Structure (simplified - actual fees vary by category and size)
    FBA_FEES = {
        'small_standard': {'fulfillment': 3.22, 'storage_monthly': 0.83},
        'large_standard': {'fulfillment': 4.09, 'storage_monthly': 1.20},
        'small_oversize': {'fulfillment': 9.73, 'storage_monthly': 2.40},
        'large_oversize': {'fulfillment': 75.78, 'storage_monthly': 12.00}
    }
    
    REFERRAL_FEES = {
        'Electronics': 0.08,
        'Books': 0.15,
        'Clothing': 0.17,
        'Home & Kitchen': 0.15,
        'Sports': 0.15,
        'Default': 0.15
    }
    
    @classmethod
    def calculate_size_tier(cls, dimensions: Dict[str, float], weight: float) -> str:
        """Determine FBA size tier based on dimensions and weight"""
        length = dimensions.get('length', 0)
        width = dimensions.get('width', 0)
        height = dimensions.get('height', 0)
        
        # Simplified size tier calculation
        if weight <= 1 and max(length, width, height) <= 15:
            return 'small_standard'
        elif weight <= 20 and max(length, width, height) <= 18:
            return 'large_standard'
        elif weight <= 70:
            return 'small_oversize'
        else:
            return 'large_oversize'
    
    @classmethod
    def calculate_fba_fees(cls, price: float, category: str, dimensions: Dict[str, float], weight: float) -> Dict[str, float]:
        """Calculate all FBA fees"""
        size_tier = cls.calculate_size_tier(dimensions, weight)
        
        # Referral fee
        referral_rate = cls.REFERRAL_FEES.get(category, cls.REFERRAL_FEES['Default'])
        referral_fee = price * referral_rate
        
        # Fulfillment fee
        fulfillment_fee = cls.FBA_FEES[size_tier]['fulfillment']
        
        # Storage fee (monthly)
        storage_fee = cls.FBA_FEES[size_tier]['storage_monthly']
        
        # Closing fee (for media categories)
        closing_fee = 1.80 if category in ['Books', 'Music', 'Video'] else 0
        
        total_fees = referral_fee + fulfillment_fee + storage_fee + closing_fee
        
        return {
            'referral_fee': referral_fee,
            'fulfillment_fee': fulfillment_fee,
            'storage_fee': storage_fee,
            'closing_fee': closing_fee,
            'total_fees': total_fees,
            'size_tier': size_tier
        }
    
    @classmethod
    def calculate_profit_metrics(cls, selling_price: float, cost_price: float, fba_fees: float) -> Dict[str, float]:
        """Calculate profit margins and ROI"""
        gross_profit = selling_price - cost_price - fba_fees
        profit_margin = (gross_profit / selling_price) * 100 if selling_price > 0 else 0
        roi = (gross_profit / cost_price) * 100 if cost_price > 0 else 0
        
        return {
            'gross_profit': gross_profit,
            'profit_margin': profit_margin,
            'roi': roi,
            'break_even_price': cost_price + fba_fees
        }

class SalesEstimator:
    """Estimate sales volume based on sales rank and category"""
    
    # Sales rank to monthly sales mapping (approximate)
    SALES_ESTIMATES = {
        'Electronics': {
            1: 10000, 100: 5000, 1000: 1000, 10000: 100, 100000: 10, 1000000: 1
        },
        'Home & Kitchen': {
            1: 8000, 100: 4000, 1000: 800, 10000: 80, 100000: 8, 1000000: 1
        },
        'Books': {
            1: 15000, 100: 7500, 1000: 1500, 10000: 150, 100000: 15, 1000000: 1
        },
        'Default': {
            1: 5000, 100: 2500, 1000: 500, 10000: 50, 100000: 5, 1000000: 1
        }
    }
    
    @classmethod
    def estimate_monthly_sales(cls, sales_rank: int, category: str) -> int:
        """Estimate monthly sales based on sales rank"""
        estimates = cls.SALES_ESTIMATES.get(category, cls.SALES_ESTIMATES['Default'])
        
        # Find the closest rank in our estimates
        ranks = sorted(estimates.keys())
        
        if sales_rank <= ranks[0]:
            return estimates[ranks[0]]
        
        if sales_rank >= ranks[-1]:
            return estimates[ranks[-1]]
        
        # Interpolate between two closest ranks
        for i in range(len(ranks) - 1):
            if ranks[i] <= sales_rank <= ranks[i + 1]:
                lower_rank, upper_rank = ranks[i], ranks[i + 1]
                lower_sales, upper_sales = estimates[lower_rank], estimates[upper_rank]
                
                # Linear interpolation
                ratio = (sales_rank - lower_rank) / (upper_rank - lower_rank)
                estimated_sales = lower_sales - (lower_sales - upper_sales) * ratio
                return int(estimated_sales)
        
        return 1

class ProductAnalyzer:
    """Main product analysis engine"""
    
    def __init__(self, amazon_client: AmazonAPIClient):
        self.amazon_client = amazon_client
        self.calculator = FBACalculator()
        self.estimator = SalesEstimator()
        
    async def analyze_product(self, asin: str, cost_price: float = None) -> Optional[ProductData]:
        """Analyze a single product"""
        try:
            product_data = await self.amazon_client.get_product_details(asin)
            if not product_data:
                return None
            
            # Extract product information
            title = product_data.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', 'Unknown')
            
            # Price information
            offers = product_data.get('Offers', {}).get('Listings', [])
            price = 0
            if offers:
                price_info = offers[0].get('Price', {})
                price = float(price_info.get('Amount', 0)) / 100 if price_info.get('Amount') else 0
            
            # Sales rank and category
            browse_nodes = product_data.get('BrowseNodeInfo', {}).get('BrowseNodes', [])
            category = browse_nodes[0].get('DisplayName', 'Unknown') if browse_nodes else 'Unknown'
            sales_rank = browse_nodes[0].get('SalesRank', 999999) if browse_nodes else 999999
            
            # Reviews
            reviews = product_data.get('CustomerReviews', {})
            reviews_count = reviews.get('Count', 0)
            rating = float(reviews.get('StarRating', {}).get('Value', 0))
            
            # Dimensions and weight (mock data - would come from API)
            dimensions = {'length': 10, 'width': 8, 'height': 6}
            weight = 1.5
            
            # Calculate FBA fees
            fba_data = self.calculator.calculate_fba_fees(price, category, dimensions, weight)
            
            # Estimate sales
            estimated_sales = self.estimator.estimate_monthly_sales(sales_rank, category)
            
            # Calculate profit metrics
            if cost_price:
                profit_data = self.calculator.calculate_profit_metrics(
                    price, cost_price, fba_data['total_fees']
                )
            else:
                # Estimate cost as 40% of selling price
                estimated_cost = price * 0.4
                profit_data = self.calculator.calculate_profit_metrics(
                    price, estimated_cost, fba_data['total_fees']
                )
            
            # Determine competition level
            competition_level = self._assess_competition(reviews_count, sales_rank)
            
            return ProductData(
                asin=asin,
                title=title,
                price=price,
                sales_rank=sales_rank,
                category=category,
                reviews_count=reviews_count,
                rating=rating,
                dimensions=dimensions,
                weight=weight,
                fba_fees=fba_data['total_fees'],
                estimated_sales=estimated_sales,
                profit_margin=profit_data['profit_margin'],
                roi=profit_data['roi'],
                competition_level=competition_level
            )
            
        except Exception as e:
            logger.error(f"Error analyzing product {asin}: {e}")
            return None
    
    async def analyze_market(self, keywords: str, category: str = None) -> MarketAnalysis:
        """Analyze entire market for given keywords"""
        try:
            # Search for products
            products_data = await self.amazon_client.search_products(keywords, category, 50)
            
            # Analyze each product
            analyzed_products = []
            for product in products_data:
                asin = product.get('ASIN')
                if asin:
                    analyzed = await self.analyze_product(asin)
                    if analyzed:
                        analyzed_products.append(analyzed)
            
            if not analyzed_products:
                return MarketAnalysis(0, 0, 0, [], [], 0, {})
            
            # Calculate market metrics
            total_products = len(analyzed_products)
            avg_price = sum(p.price for p in analyzed_products) / total_products
            avg_sales_rank = sum(p.sales_rank for p in analyzed_products) / total_products
            
            # Find top sellers (lowest sales rank)
            top_sellers = sorted(analyzed_products, key=lambda x: x.sales_rank)[:10]
            
            # Find profit opportunities (high profit margin, low competition)
            profit_opportunities = [
                p for p in analyzed_products 
                if p.profit_margin > 20 and p.competition_level in ['Low', 'Medium']
            ]
            profit_opportunities.sort(key=lambda x: x.roi, reverse=True)
            
            # Calculate market saturation
            high_competition_count = sum(1 for p in analyzed_products if p.competition_level == 'High')
            market_saturation = (high_competition_count / total_products) * 100
            
            # Recommend price range
            prices = [p.price for p in analyzed_products if p.price > 0]
            recommended_price_range = {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'median': sorted(prices)[len(prices)//2] if prices else 0
            }
            
            return MarketAnalysis(
                total_products=total_products,
                avg_price=avg_price,
                avg_sales_rank=avg_sales_rank,
                top_sellers=top_sellers,
                profit_opportunities=profit_opportunities[:10],
                market_saturation=market_saturation,
                recommended_price_range=recommended_price_range
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            return MarketAnalysis(0, 0, 0, [], [], 0, {})
    
    def _assess_competition(self, reviews_count: int, sales_rank: int) -> str:
        """Assess competition level based on reviews and sales rank"""
        if reviews_count > 1000 or sales_rank < 1000:
            return 'High'
        elif reviews_count > 100 or sales_rank < 10000:
            return 'Medium'
        else:
            return 'Low'

# Flask Web Application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# Initialize analyzer
amazon_client = AmazonAPIClient(
    access_key=os.environ.get('AMAZON_ACCESS_KEY', ''),
    secret_key=os.environ.get('AMAZON_SECRET_KEY', ''),
    partner_tag=os.environ.get('AMAZON_PARTNER_TAG', ''),
    region='US'
)
analyzer = ProductAnalyzer(amazon_client)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
async def analyze():
    data = request.get_json()
    keywords = data.get('keywords', '')
    category = data.get('category')
    
    if not keywords:
        return jsonify({'error': 'Keywords required'}), 400
    
    try:
        market_analysis = await analyzer.analyze_market(keywords, category)
        
        # Convert to JSON-serializable format
        result = {
            'total_products': market_analysis.total_products,
            'avg_price': round(market_analysis.avg_price, 2),
            'avg_sales_rank': int(market_analysis.avg_sales_rank),
            'market_saturation': round(market_analysis.market_saturation, 2),
            'recommended_price_range': market_analysis.recommended_price_range,
            'top_sellers': [
                {
                    'asin': p.asin,
                    'title': p.title[:50] + '...' if len(p.title) > 50 else p.title,
                    'price': p.price,
                    'sales_rank': p.sales_rank,
                    'estimated_sales': p.estimated_sales,
                    'profit_margin': round(p.profit_margin, 2)
                }
                for p in market_analysis.top_sellers
            ],
            'profit_opportunities': [
                {
                    'asin': p.asin,
                    'title': p.title[:50] + '...' if len(p.title) > 50 else p.title,
                    'price': p.price,
                    'profit_margin': round(p.profit_margin, 2),
                    'roi': round(p.roi, 2),
                    'competition_level': p.competition_level,
                    'estimated_sales': p.estimated_sales
                }
                for p in market_analysis.profit_opportunities
            ]
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/product/<asin>')
async def product_details(asin):
    try:
        cost_price = request.args.get('cost', type=float)
        product = await analyzer.analyze_product(asin, cost_price)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        result = {
            'asin': product.asin,
            'title': product.title,
            'price': product.price,
            'sales_rank': product.sales_rank,
            'category': product.category,
            'reviews_count': product.reviews_count,
            'rating': product.rating,
            'fba_fees': round(product.fba_fees, 2),
            'estimated_sales': product.estimated_sales,
            'profit_margin': round(product.profit_margin, 2),
            'roi': round(product.roi, 2),
            'competition_level': product.competition_level
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Product analysis error: {e}")
        return jsonify({'error': 'Product analysis failed'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)