#!/usr/bin/env python3
"""
Shopify Mobile Manager - Complete Mobile App for Shopify Store Management
Production-ready Flask application with real Shopify API integration
Price: $197 - Immediate revenue generator
"""

import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import shopify
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///shopify_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    shopify_domain = db.Column(db.String(255))
    shopify_token = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_active = db.Column(db.Boolean, default=True)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shop_domain = db.Column(db.String(255), nullable=False)
    shop_name = db.Column(db.String(255))
    total_orders = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    last_sync = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopify_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float)
    inventory = db.Column(db.Integer)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopify_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(50))
    customer_email = db.Column(db.String(120))
    total_price = db.Column(db.Float)
    fulfillment_status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Shopify API Helper Class
class ShopifyManager:
    def __init__(self, shop_domain, access_token):
        self.shop_domain = shop_domain
        self.access_token = access_token
        shopify.ShopifyResource.set_site(f"https://{shop_domain}")
        shopify.ShopifyResource.set_headers({"X-Shopify-Access-Token": access_token})
    
    def get_products(self, limit=50):
        """Fetch products from Shopify"""
        try:
            products = shopify.Product.find(limit=limit)
            return [self._format_product(p) for p in products]
        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            return []
    
    def get_orders(self, limit=50, status='any'):
        """Fetch orders from Shopify"""
        try:
            orders = shopify.Order.find(limit=limit, status=status)
            return [self._format_order(o) for o in orders]
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    def update_product_inventory(self, product_id, inventory_quantity):
        """Update product inventory"""
        try:
            product = shopify.Product.find(product_id)
            if product.variants:
                variant = product.variants[0]
                variant.inventory_quantity = inventory_quantity
                variant.save()
                return True
        except Exception as e:
            logger.error(f"Error updating inventory: {e}")
        return False
    
    def fulfill_order(self, order_id, tracking_number=None):
        """Fulfill an order"""
        try:
            order = shopify.Order.find(order_id)
            fulfillment_data = {
                'location_id': order.line_items[0].fulfillment_service,
                'tracking_number': tracking_number,
                'notify_customer': True
            }
            fulfillment = shopify.Fulfillment(fulfillment_data)
            fulfillment.prefix_options = {'order_id': order_id}
            return fulfillment.save()
        except Exception as e:
            logger.error(f"Error fulfilling order: {e}")
        return False
    
    def get_analytics(self, days=30):
        """Get store analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            orders = shopify.Order.find(
                created_at_min=start_date.isoformat(),
                created_at_max=end_date.isoformat(),
                status='any'
            )
            
            total_revenue = sum(float(order.total_price) for order in orders)
            total_orders = len(orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            return {
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'avg_order_value': avg_order_value,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}
    
    def _format_product(self, product):
        """Format product data"""
        return {
            'id': product.id,
            'title': product.title,
            'price': float(product.variants[0].price) if product.variants else 0,
            'inventory': product.variants[0].inventory_quantity if product.variants else 0,
            'status': product.status,
            'image': product.images[0].src if product.images else None
        }
    
    def _format_order(self, order):
        """Format order data"""
        return {
            'id': order.id,
            'order_number': order.order_number,
            'customer_email': order.email,
            'total_price': float(order.total_price),
            'fulfillment_status': order.fulfillment_status,
            'created_at': order.created_at,
            'line_items': len(order.line_items)
        }

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        shopify_domain = request.form['shopify_domain']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            shopify_domain=shopify_domain
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return redirect(url_for('setup_shopify'))
    
    return render_template('register.html')

@app.route('/setup-shopify')
@login_required
def setup_shopify():
    return render_template('setup_shopify.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    if not user.shopify_token:
        return redirect(url_for('setup_shopify'))
    
    # Get store analytics
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    analytics = shopify_manager.get_analytics()
    recent_orders = shopify_manager.get_orders(limit=10)
    
    return render_template('dashboard.html', 
                         analytics=analytics, 
                         recent_orders=recent_orders,
                         user=user)

@app.route('/products')
@login_required
def products():
    user = User.query.get(session['user_id'])
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    products = shopify_manager.get_products()
    
    return render_template('products.html', products=products)

@app.route('/orders')
@login_required
def orders():
    user = User.query.get(session['user_id'])
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    orders = shopify_manager.get_orders()
    
    return render_template('orders.html', orders=orders)

@app.route('/api/update-inventory', methods=['POST'])
@login_required
def update_inventory():
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    success = shopify_manager.update_product_inventory(
        data['product_id'], 
        data['quantity']
    )
    
    return jsonify({'success': success})

@app.route('/api/fulfill-order', methods=['POST'])
@login_required
def fulfill_order():
    user = User.query.get(session['user_id'])
    data = request.get_json()
    
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    success = shopify_manager.fulfill_order(
        data['order_id'], 
        data.get('tracking_number')
    )
    
    return jsonify({'success': success})

@app.route('/api/analytics')
@login_required
def api_analytics():
    user = User.query.get(session['user_id'])
    days = request.args.get('days', 30, type=int)
    
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    analytics = shopify_manager.get_analytics(days)
    
    return jsonify(analytics)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Mobile API Endpoints
@app.route('/api/mobile/login', methods=['POST'])
def mobile_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            'success': True,
            'user_id': user.id,
            'shopify_domain': user.shopify_domain
        })
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/mobile/dashboard/<int:user_id>')
def mobile_dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    shopify_manager = ShopifyManager(user.shopify_domain, user.shopify_token)
    analytics = shopify_manager.get_analytics()
    
    return jsonify({
        'analytics': analytics,
        'store_name': user.shopify_domain,
        'last_sync': datetime.utcnow().isoformat()
    })

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)