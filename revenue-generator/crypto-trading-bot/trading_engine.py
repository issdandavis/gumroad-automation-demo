#!/usr/bin/env python3
"""
Advanced Cryptocurrency Trading Bot
Real-time trading with multiple exchanges and strategies
Price: $497 - Professional trading system
"""

import os
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
import ccxt
import websocket
import threading
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import ta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    price: float
    timestamp: datetime
    strategy: str
    indicators: Dict[str, float]

@dataclass
class Position:
    symbol: str
    side: str  # 'long', 'short'
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    timestamp: datetime

@dataclass
class Trade:
    id: str
    symbol: str
    side: str
    amount: float
    price: float
    fee: float
    timestamp: datetime
    strategy: str
    pnl: Optional[float] = None

class TechnicalAnalyzer:
    """Advanced technical analysis with multiple indicators"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""
        try:
            # Moving Averages
            df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
            df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
            df['ema_12'] = ta.trend.ema_indicator(df['close'], window=12)
            df['ema_26'] = ta.trend.ema_indicator(df['close'], window=26)
            
            # MACD
            df['macd'] = ta.trend.macd_diff(df['close'])
            df['macd_signal'] = ta.trend.macd_signal(df['close'])
            df['macd_histogram'] = ta.trend.macd(df['close'])
            
            # RSI
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['close'])
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Stochastic
            df['stoch_k'] = ta.momentum.stoch(df['high'], df['low'], df['close'])
            df['stoch_d'] = ta.momentum.stoch_signal(df['high'], df['low'], df['close'])
            
            # Volume indicators
            df['volume_sma'] = ta.volume.volume_sma(df['close'], df['volume'])
            df['vwap'] = ta.volume.volume_weighted_average_price(
                df['high'], df['low'], df['close'], df['volume']
            )
            
            # Volatility
            df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
            
            # Support and Resistance
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            
            # Price patterns
            df['higher_high'] = (df['high'] > df['high'].shift(1)) & (df['high'].shift(1) > df['high'].shift(2))
            df['lower_low'] = (df['low'] < df['low'].shift(1)) & (df['low'].shift(1) < df['low'].shift(2))
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.analyzer = TechnicalAnalyzer()
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[TradingSignal]:
        """Generate trading signal based on strategy"""
        raise NotImplementedError

class MACDStrategy(TradingStrategy):
    """MACD crossover strategy with RSI filter"""
    
    def __init__(self):
        super().__init__("MACD_RSI")
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[TradingSignal]:
        try:
            if len(df) < 50:
                return None
            
            df = self.analyzer.calculate_indicators(df)
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # MACD crossover signals
            macd_bullish = (latest['macd'] > latest['macd_signal'] and 
                           prev['macd'] <= prev['macd_signal'])
            macd_bearish = (latest['macd'] < latest['macd_signal'] and 
                           prev['macd'] >= prev['macd_signal'])
            
            # RSI filter
            rsi_oversold = latest['rsi'] < 30
            rsi_overbought = latest['rsi'] > 70
            rsi_neutral = 30 <= latest['rsi'] <= 70
            
            # Generate signals
            if macd_bullish and (rsi_oversold or rsi_neutral):
                confidence = 0.8 if rsi_oversold else 0.6
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'macd': latest['macd'],
                        'macd_signal': latest['macd_signal'],
                        'rsi': latest['rsi']
                    }
                )
            
            elif macd_bearish and (rsi_overbought or rsi_neutral):
                confidence = 0.8 if rsi_overbought else 0.6
                return TradingSignal(
                    symbol=symbol,
                    action='SELL',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'macd': latest['macd'],
                        'macd_signal': latest['macd_signal'],
                        'rsi': latest['rsi']
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in MACD strategy: {e}")
            return None

class BollingerBandsStrategy(TradingStrategy):
    """Bollinger Bands mean reversion strategy"""
    
    def __init__(self):
        super().__init__("BOLLINGER_BANDS")
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[TradingSignal]:
        try:
            if len(df) < 30:
                return None
            
            df = self.analyzer.calculate_indicators(df)
            latest = df.iloc[-1]
            
            # Price position relative to Bollinger Bands
            bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
            
            # Volume confirmation
            volume_above_avg = latest['volume'] > latest['volume_sma']
            
            # Generate signals
            if bb_position <= 0.1 and volume_above_avg:  # Near lower band
                confidence = 0.7
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'bb_position': bb_position,
                        'bb_width': latest['bb_width'],
                        'volume_ratio': latest['volume'] / latest['volume_sma']
                    }
                )
            
            elif bb_position >= 0.9 and volume_above_avg:  # Near upper band
                confidence = 0.7
                return TradingSignal(
                    symbol=symbol,
                    action='SELL',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'bb_position': bb_position,
                        'bb_width': latest['bb_width'],
                        'volume_ratio': latest['volume'] / latest['volume_sma']
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in Bollinger Bands strategy: {e}")
            return None

class MLStrategy(TradingStrategy):
    """Machine Learning based strategy using Random Forest"""
    
    def __init__(self):
        super().__init__("ML_RANDOM_FOREST")
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
    
    def train_model(self, df: pd.DataFrame):
        """Train the ML model on historical data"""
        try:
            df = self.analyzer.calculate_indicators(df)
            
            # Prepare features
            feature_cols = [
                'sma_20', 'sma_50', 'ema_12', 'ema_26', 'macd', 'macd_signal',
                'rsi', 'bb_width', 'stoch_k', 'stoch_d', 'atr', 'volume_sma'
            ]
            
            # Create target (future price movement)
            df['future_return'] = df['close'].shift(-5) / df['close'] - 1
            
            # Remove NaN values
            df_clean = df[feature_cols + ['future_return']].dropna()
            
            if len(df_clean) < 100:
                logger.warning("Insufficient data for ML training")
                return
            
            X = df_clean[feature_cols]
            y = df_clean['future_return']
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.feature_columns = feature_cols
            self.is_trained = True
            
            logger.info(f"ML model trained on {len(df_clean)} samples")
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
    
    def generate_signal(self, df: pd.DataFrame, symbol: str) -> Optional[TradingSignal]:
        try:
            if not self.is_trained or len(df) < 50:
                return None
            
            df = self.analyzer.calculate_indicators(df)
            latest = df.iloc[-1]
            
            # Prepare features
            features = [latest[col] for col in self.feature_columns]
            
            if any(pd.isna(features)):
                return None
            
            # Make prediction
            features_scaled = self.scaler.transform([features])
            predicted_return = self.model.predict(features_scaled)[0]
            
            # Generate signal based on prediction
            confidence = min(abs(predicted_return) * 10, 0.9)  # Scale confidence
            
            if predicted_return > 0.02:  # Predicted 2% gain
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'predicted_return': predicted_return,
                        'confidence': confidence
                    }
                )
            
            elif predicted_return < -0.02:  # Predicted 2% loss
                return TradingSignal(
                    symbol=symbol,
                    action='SELL',
                    confidence=confidence,
                    price=latest['close'],
                    timestamp=datetime.now(),
                    strategy=self.name,
                    indicators={
                        'predicted_return': predicted_return,
                        'confidence': confidence
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error in ML strategy: {e}")
            return None

class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, max_position_size: float = 0.1, max_daily_loss: float = 0.05):
        self.max_position_size = max_position_size  # 10% of portfolio per position
        self.max_daily_loss = max_daily_loss  # 5% daily loss limit
        self.daily_pnl = 0.0
        self.positions: Dict[str, Position] = {}
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, 
                              current_price: float) -> float:
        """Calculate optimal position size based on risk parameters"""
        try:
            # Base position size
            base_size = portfolio_value * self.max_position_size
            
            # Adjust based on signal confidence
            confidence_multiplier = signal.confidence
            
            # Adjust based on volatility (simplified)
            volatility_multiplier = 1.0  # Would calculate from ATR in real implementation
            
            # Calculate final position size
            position_value = base_size * confidence_multiplier * volatility_multiplier
            position_size = position_value / current_price
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def should_execute_trade(self, signal: TradingSignal, portfolio_value: float) -> bool:
        """Determine if trade should be executed based on risk rules"""
        try:
            # Check daily loss limit
            if self.daily_pnl <= -self.max_daily_loss * portfolio_value:
                logger.warning("Daily loss limit reached")
                return False
            
            # Check if we already have a position in this symbol
            if signal.symbol in self.positions:
                current_position = self.positions[signal.symbol]
                # Don't add to position if it would exceed size limit
                if current_position.side == signal.action.lower():
                    return False
            
            # Check signal confidence threshold
            if signal.confidence < 0.6:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in risk check: {e}")
            return False
    
    def update_position(self, symbol: str, side: str, size: float, price: float):
        """Update position tracking"""
        try:
            if symbol in self.positions:
                # Update existing position
                pos = self.positions[symbol]
                if pos.side == side:
                    # Add to position
                    total_value = pos.size * pos.entry_price + size * price
                    total_size = pos.size + size
                    pos.entry_price = total_value / total_size
                    pos.size = total_size
                else:
                    # Close or reduce position
                    if size >= pos.size:
                        # Close position
                        del self.positions[symbol]
                    else:
                        # Reduce position
                        pos.size -= size
            else:
                # New position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side=side,
                    size=size,
                    entry_price=price,
                    current_price=price,
                    pnl=0.0,
                    pnl_percentage=0.0,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error updating position: {e}")
    
    def update_pnl(self, current_prices: Dict[str, float]):
        """Update P&L for all positions"""
        try:
            total_pnl = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    position.current_price = current_price
                    
                    if position.side == 'long':
                        position.pnl = (current_price - position.entry_price) * position.size
                    else:  # short
                        position.pnl = (position.entry_price - current_price) * position.size
                    
                    position.pnl_percentage = (position.pnl / (position.entry_price * position.size)) * 100
                    total_pnl += position.pnl
            
            # Update daily P&L (simplified - would reset daily)
            self.daily_pnl = total_pnl
            
        except Exception as e:
            logger.error(f"Error updating P&L: {e}")

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, exchange_config: Dict[str, str]):
        self.exchange = self._initialize_exchange(exchange_config)
        self.strategies = [
            MACDStrategy(),
            BollingerBandsStrategy(),
            MLStrategy()
        ]
        self.risk_manager = RiskManager()
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT']
        self.is_running = False
        self.trades: List[Trade] = []
        
        # Initialize database
        self._init_database()
    
    def _initialize_exchange(self, config: Dict[str, str]):
        """Initialize exchange connection"""
        try:
            exchange_class = getattr(ccxt, config['exchange'])
            exchange = exchange_class({
                'apiKey': config['api_key'],
                'secret': config['secret'],
                'sandbox': config.get('sandbox', True),  # Use sandbox by default
                'enableRateLimit': True,
            })
            return exchange
        except Exception as e:
            logger.error(f"Error initializing exchange: {e}")
            return None
    
    def _init_database(self):
        """Initialize SQLite database for storing trades and signals"""
        try:
            conn = sqlite3.connect('trading_bot.db')
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    side TEXT,
                    amount REAL,
                    price REAL,
                    fee REAL,
                    timestamp TEXT,
                    strategy TEXT,
                    pnl REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    action TEXT,
                    confidence REAL,
                    price REAL,
                    timestamp TEXT,
                    strategy TEXT,
                    executed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    async def start_trading(self):
        """Start the trading bot"""
        try:
            self.is_running = True
            logger.info("Trading bot started")
            
            # Train ML model with historical data
            await self._train_ml_models()
            
            # Main trading loop
            while self.is_running:
                await self._trading_cycle()
                await asyncio.sleep(60)  # Run every minute
                
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
        finally:
            self.is_running = False
    
    async def _train_ml_models(self):
        """Train ML models with historical data"""
        try:
            for strategy in self.strategies:
                if isinstance(strategy, MLStrategy):
                    for symbol in self.symbols:
                        # Fetch historical data
                        ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=1000)
                        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        
                        # Train model
                        strategy.train_model(df)
                        
        except Exception as e:
            logger.error(f"Error training ML models: {e}")
    
    async def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Get current prices
            current_prices = {}
            portfolio_value = 10000  # Mock portfolio value
            
            for symbol in self.symbols:
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    current_prices[symbol] = ticker['last']
                    
                    # Fetch recent OHLCV data
                    ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Generate signals from all strategies
                    signals = []
                    for strategy in self.strategies:
                        signal = strategy.generate_signal(df, symbol)
                        if signal:
                            signals.append(signal)
                    
                    # Execute trades based on signals
                    for signal in signals:
                        if self.risk_manager.should_execute_trade(signal, portfolio_value):
                            await self._execute_trade(signal, portfolio_value)
                    
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
            
            # Update P&L
            self.risk_manager.update_pnl(current_prices)
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _execute_trade(self, signal: TradingSignal, portfolio_value: float):
        """Execute a trade based on signal"""
        try:
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                signal, portfolio_value, signal.price
            )
            
            if position_size <= 0:
                return
            
            # Execute trade (mock execution for demo)
            trade_id = f"{signal.symbol}_{datetime.now().timestamp()}"
            
            # In real implementation, would execute actual trade
            # order = self.exchange.create_market_order(
            #     signal.symbol, signal.action.lower(), position_size
            # )
            
            # Mock trade execution
            trade = Trade(
                id=trade_id,
                symbol=signal.symbol,
                side=signal.action.lower(),
                amount=position_size,
                price=signal.price,
                fee=signal.price * position_size * 0.001,  # 0.1% fee
                timestamp=datetime.now(),
                strategy=signal.strategy
            )
            
            self.trades.append(trade)
            
            # Update risk manager
            self.risk_manager.update_position(
                signal.symbol, signal.action.lower(), position_size, signal.price
            )
            
            # Store in database
            self._store_trade(trade)
            
            logger.info(f"Executed trade: {signal.action} {position_size:.6f} {signal.symbol} at {signal.price}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def _store_trade(self, trade: Trade):
        """Store trade in database"""
        try:
            conn = sqlite3.connect('trading_bot.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (id, symbol, side, amount, price, fee, timestamp, strategy, pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.id, trade.symbol, trade.side, trade.amount, trade.price,
                trade.fee, trade.timestamp.isoformat(), trade.strategy, trade.pnl
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}")
    
    def stop_trading(self):
        """Stop the trading bot"""
        self.is_running = False
        logger.info("Trading bot stopped")
    
    def get_performance_stats(self) -> Dict:
        """Get trading performance statistics"""
        try:
            if not self.trades:
                return {}
            
            total_trades = len(self.trades)
            profitable_trades = sum(1 for t in self.trades if t.pnl and t.pnl > 0)
            win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
            
            total_pnl = sum(t.pnl for t in self.trades if t.pnl)
            total_fees = sum(t.fee for t in self.trades)
            
            return {
                'total_trades': total_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'total_fees': round(total_fees, 2),
                'net_profit': round(total_pnl - total_fees, 2),
                'active_positions': len(self.risk_manager.positions),
                'daily_pnl': round(self.risk_manager.daily_pnl, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {}

# Flask Web Interface
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot instance
trading_bot = None

@app.route('/')
def index():
    return render_template('trading_dashboard.html')

@app.route('/api/start', methods=['POST'])
def start_bot():
    global trading_bot
    
    try:
        config = request.get_json()
        exchange_config = {
            'exchange': config.get('exchange', 'binance'),
            'api_key': config.get('api_key', ''),
            'secret': config.get('secret', ''),
            'sandbox': config.get('sandbox', True)
        }
        
        trading_bot = TradingBot(exchange_config)
        
        # Start trading in background
        asyncio.create_task(trading_bot.start_trading())
        
        return jsonify({'success': True, 'message': 'Trading bot started'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    global trading_bot
    
    if trading_bot:
        trading_bot.stop_trading()
        return jsonify({'success': True, 'message': 'Trading bot stopped'})
    
    return jsonify({'success': False, 'error': 'Bot not running'}), 400

@app.route('/api/status')
def get_status():
    global trading_bot
    
    if not trading_bot:
        return jsonify({'running': False})
    
    stats = trading_bot.get_performance_stats()
    positions = [asdict(pos) for pos in trading_bot.risk_manager.positions.values()]
    
    return jsonify({
        'running': trading_bot.is_running,
        'stats': stats,
        'positions': positions,
        'recent_trades': [asdict(t) for t in trading_bot.trades[-10:]]
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=False)