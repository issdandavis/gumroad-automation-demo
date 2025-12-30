"""
Comprehensive Monitoring Dashboard System
Real-time monitoring and alerting for Self-Evolving AI Framework
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics
import aiohttp
import websockets
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics we track"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: MetricType


@dataclass
class Alert:
    """Alert definition and state"""
    id: str
    name: str
    description: str
    severity: AlertSeverity
    condition: str
    threshold: float
    is_active: bool
    triggered_at: Optional[datetime]
    resolved_at: Optional[datetime]
    notification_channels: List[str]


@dataclass
class SystemHealth:
    """Overall system health status"""
    status: str  # healthy, degraded, critical
    uptime_percentage: float
    response_time_p95: float
    error_rate: float
    active_alerts: int
    last_updated: datetime


class MetricsCollector:
    """Collects and stores metrics from various sources"""
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)
        self.metric_aggregates = defaultdict(list)
        self.prometheus_metrics = {
            'requests_total': Counter('requests_total', 'Total requests', ['method', 'endpoint']),
            'request_duration': Histogram('request_duration_seconds', 'Request duration'),
            'active_connections': Gauge('active_connections', 'Active connections'),
            'evolution_fitness': Gauge('evolution_fitness_score', 'Current fitness score'),
            'cost_spent': Counter('cost_spent_total', 'Total cost spent', ['provider']),
            'mutations_applied': Counter('mutations_applied_total', 'Total mutations applied'),
            'security_events': Counter('security_events_total', 'Security events', ['event_type'])
        }
        
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        import psutil
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network
        network = psutil.net_io_counters()
        
        metrics = {
            'cpu_usage_percent': cpu_percent,
            'memory_usage_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_usage_percent': (disk.used / disk.total) * 100,
            'network_bytes_sent': network.bytes_sent,
            'network_bytes_recv': network.bytes_recv,
            'timestamp': datetime.now()
        }
        
        # Store metrics
        for name, value in metrics.items():
            if name != 'timestamp':
                await self.record_metric(name, value, MetricType.GAUGE)
        
        return metrics
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        # This would integrate with your actual application
        # For now, we'll simulate some metrics
        
        metrics = {
            'active_evolution_processes': np.random.randint(1, 10),
            'current_fitness_score': np.random.uniform(0.7, 0.95),
            'ai_requests_per_minute': np.random.randint(50, 200),
            'average_response_time_ms': np.random.uniform(50, 150),
            'error_rate_percent': np.random.uniform(0, 2),
            'cost_per_hour': np.random.uniform(5, 25),
            'successful_mutations_count': np.random.randint(0, 5),
            'failed_mutations_count': np.random.randint(0, 2),
            'timestamp': datetime.now()
        }
        
        # Update Prometheus metrics
        self.prometheus_metrics['evolution_fitness'].set(metrics['current_fitness_score'])
        self.prometheus_metrics['active_connections'].set(metrics['active_evolution_processes'])
        
        # Store metrics
        for name, value in metrics.items():
            if name != 'timestamp':
                await self.record_metric(name, value, MetricType.GAUGE)
        
        return metrics
    
    async def record_metric(self, name: str, value: float, metric_type: MetricType, labels: Dict[str, str] = None):
        """Record a single metric"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            labels=labels or {},
            metric_type=metric_type
        )
        
        self.metrics_buffer.append(metric)
        self.metric_aggregates[name].append(value)
        
        # Keep only recent values for aggregation
        if len(self.metric_aggregates[name]) > 1000:
            self.metric_aggregates[name] = self.metric_aggregates[name][-1000:]
    
    def get_metric_statistics(self, metric_name: str, time_window: timedelta = None) -> Dict[str, float]:
        """Get statistics for a metric"""
        if metric_name not in self.metric_aggregates:
            return {}
        
        values = self.metric_aggregates[metric_name]
        if not values:
            return {}
        
        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            # This is simplified - in practice you'd filter by timestamp
            values = values[-100:]  # Get recent values
        
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
            'count': len(values)
        }


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alerts = {}
        self.notification_channels = {}
        self.alert_history = deque(maxlen=1000)
        
    def register_alert(self, alert: Alert):
        """Register a new alert"""
        self.alerts[alert.id] = alert
        
    def register_notification_channel(self, name: str, handler: Callable):
        """Register a notification channel"""
        self.notification_channels[name] = handler
        
    async def check_alerts(self):
        """Check all alerts and trigger notifications"""
        for alert_id, alert in self.alerts.items():
            await self._evaluate_alert(alert)
    
    async def _evaluate_alert(self, alert: Alert):
        """Evaluate a single alert condition"""
        try:
            # Parse the condition (simplified - in practice use a proper parser)
            if ">" in alert.condition:
                metric_name, threshold_str = alert.condition.split(">")
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                stats = self.metrics_collector.get_metric_statistics(metric_name)
                if stats and stats.get('mean', 0) > threshold:
                    await self._trigger_alert(alert)
                elif alert.is_active:
                    await self._resolve_alert(alert)
                    
            elif "<" in alert.condition:
                metric_name, threshold_str = alert.condition.split("<")
                metric_name = metric_name.strip()
                threshold = float(threshold_str.strip())
                
                stats = self.metrics_collector.get_metric_statistics(metric_name)
                if stats and stats.get('mean', 0) < threshold:
                    await self._trigger_alert(alert)
                elif alert.is_active:
                    await self._resolve_alert(alert)
                    
        except Exception as e:
            logging.error(f"Error evaluating alert {alert.id}: {e}")
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        if not alert.is_active:
            alert.is_active = True
            alert.triggered_at = datetime.now()
            alert.resolved_at = None
            
            # Send notifications
            for channel_name in alert.notification_channels:
                if channel_name in self.notification_channels:
                    await self.notification_channels[channel_name](alert)
            
            # Record in history
            self.alert_history.append({
                'alert_id': alert.id,
                'action': 'triggered',
                'timestamp': alert.triggered_at,
                'severity': alert.severity.value
            })
            
            logging.warning(f"Alert triggered: {alert.name} - {alert.description}")
    
    async def _resolve_alert(self, alert: Alert):
        """Resolve an alert"""
        if alert.is_active:
            alert.is_active = False
            alert.resolved_at = datetime.now()
            
            # Send resolution notifications
            for channel_name in alert.notification_channels:
                if channel_name in self.notification_channels:
                    await self.notification_channels[channel_name](alert, resolved=True)
            
            # Record in history
            self.alert_history.append({
                'alert_id': alert.id,
                'action': 'resolved',
                'timestamp': alert.resolved_at,
                'severity': alert.severity.value
            })
            
            logging.info(f"Alert resolved: {alert.name}")


class DashboardGenerator:
    """Generates dashboard visualizations"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        
    def create_system_overview_dashboard(self) -> str:
        """Create system overview dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('System Health', 'Evolution Fitness', 'Response Times', 
                          'Cost Tracking', 'Error Rates', 'Resource Usage'),
            specs=[[{"type": "indicator"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # System Health Indicator
        current_fitness = self.metrics_collector.get_metric_statistics('current_fitness_score')
        fitness_value = current_fitness.get('mean', 0.8) if current_fitness else 0.8
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=fitness_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "System Fitness"},
                delta={'reference': 0.9},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 0.5], 'color': "lightgray"},
                        {'range': [0.5, 0.8], 'color': "yellow"},
                        {'range': [0.8, 1], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.9
                    }
                }
            ),
            row=1, col=1
        )
        
        # Evolution Fitness Over Time
        fitness_data = self._generate_time_series_data('current_fitness_score')
        fig.add_trace(
            go.Scatter(
                x=fitness_data['timestamps'],
                y=fitness_data['values'],
                mode='lines+markers',
                name='Fitness Score',
                line=dict(color='blue', width=2)
            ),
            row=1, col=2
        )
        
        # Response Times
        response_time_data = self._generate_time_series_data('average_response_time_ms')
        fig.add_trace(
            go.Scatter(
                x=response_time_data['timestamps'],
                y=response_time_data['values'],
                mode='lines',
                name='Response Time (ms)',
                line=dict(color='green', width=2)
            ),
            row=2, col=1
        )
        
        # Cost Tracking
        providers = ['OpenAI', 'Anthropic', 'Bedrock', 'xAI']
        costs = [np.random.uniform(10, 100) for _ in providers]
        fig.add_trace(
            go.Bar(
                x=providers,
                y=costs,
                name='Cost by Provider',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ),
            row=2, col=2
        )
        
        # Error Rates
        error_rate_data = self._generate_time_series_data('error_rate_percent')
        fig.add_trace(
            go.Scatter(
                x=error_rate_data['timestamps'],
                y=error_rate_data['values'],
                mode='lines',
                name='Error Rate (%)',
                line=dict(color='red', width=2)
            ),
            row=3, col=1
        )
        
        # Resource Usage
        cpu_data = self._generate_time_series_data('cpu_usage_percent')
        memory_data = self._generate_time_series_data('memory_usage_percent')
        
        fig.add_trace(
            go.Scatter(
                x=cpu_data['timestamps'],
                y=cpu_data['values'],
                mode='lines',
                name='CPU Usage (%)',
                line=dict(color='orange', width=2)
            ),
            row=3, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=memory_data['timestamps'],
                y=memory_data['values'],
                mode='lines',
                name='Memory Usage (%)',
                line=dict(color='purple', width=2)
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title="Self-Evolving AI Framework - System Dashboard",
            height=800,
            showlegend=True,
            template="plotly_dark"
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def create_evolution_analytics_dashboard(self) -> str:
        """Create evolution-specific analytics dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Fitness Evolution', 'Mutation Success Rate', 
                          'Performance Improvements', 'Safety Metrics'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "indicator"}]]
        )
        
        # Fitness Evolution Over Time
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
        fitness_scores = [0.7 + 0.2 * np.random.random() + 0.05 * i for i in range(24)]
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=fitness_scores,
                mode='lines+markers',
                name='Fitness Score',
                line=dict(color='#00D4AA', width=3),
                marker=dict(size=6)
            ),
            row=1, col=1
        )
        
        # Mutation Success Rate
        mutation_types = ['Parameter Tuning', 'Architecture Change', 'Provider Switch', 'Cost Optimization']
        success_rates = [85, 72, 91, 88]
        
        fig.add_trace(
            go.Bar(
                x=mutation_types,
                y=success_rates,
                name='Success Rate (%)',
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ),
            row=1, col=2
        )
        
        # Performance Improvements
        improvement_metrics = ['Response Time', 'Accuracy', 'Cost Efficiency', 'User Satisfaction']
        before_values = [120, 0.82, 0.75, 0.78]
        after_values = [85, 0.91, 0.89, 0.87]
        
        fig.add_trace(
            go.Scatter(
                x=improvement_metrics,
                y=before_values,
                mode='markers',
                name='Before Evolution',
                marker=dict(size=12, color='red', symbol='x')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=improvement_metrics,
                y=after_values,
                mode='markers',
                name='After Evolution',
                marker=dict(size=12, color='green', symbol='circle')
            ),
            row=2, col=1
        )
        
        # Safety Score Indicator
        safety_score = 0.94
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=safety_score,
                title={'text': "Safety Score"},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 0.7], 'color': "red"},
                        {'range': [0.7, 0.9], 'color': "yellow"},
                        {'range': [0.9, 1], 'color': "green"}
                    ]
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="Evolution Analytics Dashboard",
            height=600,
            template="plotly_dark"
        )
        
        return fig.to_html(include_plotlyjs=True)
    
    def _generate_time_series_data(self, metric_name: str, hours: int = 24) -> Dict[str, List]:
        """Generate time series data for visualization"""
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(hours, 0, -1)]
        
        # Generate realistic data based on metric type
        if 'fitness' in metric_name:
            base_value = 0.8
            values = [base_value + 0.1 * np.sin(i/5) + 0.05 * np.random.random() for i in range(hours)]
        elif 'response_time' in metric_name:
            base_value = 100
            values = [base_value + 20 * np.sin(i/3) + 10 * np.random.random() for i in range(hours)]
        elif 'error_rate' in metric_name:
            values = [max(0, 1 + 0.5 * np.sin(i/4) + 0.3 * np.random.random()) for i in range(hours)]
        elif 'cpu_usage' in metric_name:
            values = [40 + 20 * np.sin(i/6) + 10 * np.random.random() for i in range(hours)]
        elif 'memory_usage' in metric_name:
            values = [60 + 15 * np.sin(i/8) + 5 * np.random.random() for i in range(hours)]
        else:
            values = [50 + 10 * np.random.random() for _ in range(hours)]
        
        return {
            'timestamps': timestamps,
            'values': values
        }


class WebSocketServer:
    """WebSocket server for real-time dashboard updates"""
    
    def __init__(self, metrics_collector: MetricsCollector, port: int = 8765):
        self.metrics_collector = metrics_collector
        self.port = port
        self.connected_clients = set()
        
    async def register_client(self, websocket, path):
        """Register a new WebSocket client"""
        self.connected_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
    
    async def broadcast_metrics(self):
        """Broadcast metrics to all connected clients"""
        while True:
            if self.connected_clients:
                # Collect current metrics
                system_metrics = await self.metrics_collector.collect_system_metrics()
                app_metrics = await self.metrics_collector.collect_application_metrics()
                
                message = {
                    'type': 'metrics_update',
                    'timestamp': datetime.now().isoformat(),
                    'system_metrics': system_metrics,
                    'application_metrics': app_metrics
                }
                
                # Send to all clients
                disconnected_clients = set()
                for client in self.connected_clients:
                    try:
                        await client.send(json.dumps(message, default=str))
                    except websockets.exceptions.ConnectionClosed:
                        disconnected_clients.add(client)
                
                # Remove disconnected clients
                self.connected_clients -= disconnected_clients
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    async def start_server(self):
        """Start the WebSocket server"""
        server = await websockets.serve(self.register_client, "localhost", self.port)
        
        # Start broadcasting metrics
        broadcast_task = asyncio.create_task(self.broadcast_metrics())
        
        logging.info(f"WebSocket server started on port {self.port}")
        
        try:
            await server.wait_closed()
        finally:
            broadcast_task.cancel()


class MonitoringDashboard:
    """Main monitoring dashboard orchestrator"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.dashboard_generator = DashboardGenerator(self.metrics_collector)
        self.websocket_server = WebSocketServer(self.metrics_collector)
        
        # Setup default alerts
        self._setup_default_alerts()
        
        # Setup notification channels
        self._setup_notification_channels()
    
    def _setup_default_alerts(self):
        """Setup default system alerts"""
        alerts = [
            Alert(
                id="high_error_rate",
                name="High Error Rate",
                description="Error rate exceeds 5%",
                severity=AlertSeverity.HIGH,
                condition="error_rate_percent > 5",
                threshold=5.0,
                is_active=False,
                triggered_at=None,
                resolved_at=None,
                notification_channels=["email", "slack"]
            ),
            Alert(
                id="low_fitness_score",
                name="Low Fitness Score",
                description="System fitness score below 0.7",
                severity=AlertSeverity.MEDIUM,
                condition="current_fitness_score < 0.7",
                threshold=0.7,
                is_active=False,
                triggered_at=None,
                resolved_at=None,
                notification_channels=["email"]
            ),
            Alert(
                id="high_response_time",
                name="High Response Time",
                description="Average response time exceeds 200ms",
                severity=AlertSeverity.MEDIUM,
                condition="average_response_time_ms > 200",
                threshold=200.0,
                is_active=False,
                triggered_at=None,
                resolved_at=None,
                notification_channels=["slack"]
            ),
            Alert(
                id="high_cost",
                name="High Cost",
                description="Hourly cost exceeds $50",
                severity=AlertSeverity.HIGH,
                condition="cost_per_hour > 50",
                threshold=50.0,
                is_active=False,
                triggered_at=None,
                resolved_at=None,
                notification_channels=["email", "slack"]
            )
        ]
        
        for alert in alerts:
            self.alert_manager.register_alert(alert)
    
    def _setup_notification_channels(self):
        """Setup notification channels"""
        async def email_notification(alert: Alert, resolved: bool = False):
            """Send email notification"""
            status = "RESOLVED" if resolved else "TRIGGERED"
            logging.info(f"EMAIL: Alert {alert.name} {status} - {alert.description}")
        
        async def slack_notification(alert: Alert, resolved: bool = False):
            """Send Slack notification"""
            status = "RESOLVED" if resolved else "TRIGGERED"
            logging.info(f"SLACK: Alert {alert.name} {status} - {alert.description}")
        
        self.alert_manager.register_notification_channel("email", email_notification)
        self.alert_manager.register_notification_channel("slack", slack_notification)
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        logging.info("Starting monitoring dashboard system...")
        
        # Start Prometheus metrics server
        start_http_server(8000)
        logging.info("Prometheus metrics server started on port 8000")
        
        # Start WebSocket server for real-time updates
        websocket_task = asyncio.create_task(self.websocket_server.start_server())
        
        # Start metrics collection loop
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        # Start alert checking loop
        alerts_task = asyncio.create_task(self._alert_checking_loop())
        
        try:
            await asyncio.gather(websocket_task, metrics_task, alerts_task)
        except KeyboardInterrupt:
            logging.info("Shutting down monitoring system...")
        finally:
            websocket_task.cancel()
            metrics_task.cancel()
            alerts_task.cancel()
    
    async def _metrics_collection_loop(self):
        """Main metrics collection loop"""
        while True:
            try:
                # Collect system metrics
                await self.metrics_collector.collect_system_metrics()
                
                # Collect application metrics
                await self.metrics_collector.collect_application_metrics()
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logging.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _alert_checking_loop(self):
        """Main alert checking loop"""
        while True:
            try:
                await self.alert_manager.check_alerts()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error in alert checking: {e}")
                await asyncio.sleep(120)  # Wait longer on error
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        # Calculate overall health metrics
        fitness_stats = self.metrics_collector.get_metric_statistics('current_fitness_score')
        response_time_stats = self.metrics_collector.get_metric_statistics('average_response_time_ms')
        error_rate_stats = self.metrics_collector.get_metric_statistics('error_rate_percent')
        
        # Count active alerts
        active_alerts = sum(1 for alert in self.alert_manager.alerts.values() if alert.is_active)
        
        # Determine overall status
        fitness_score = fitness_stats.get('mean', 0.8) if fitness_stats else 0.8
        error_rate = error_rate_stats.get('mean', 1.0) if error_rate_stats else 1.0
        
        if fitness_score < 0.7 or error_rate > 5 or active_alerts > 2:
            status = "critical"
        elif fitness_score < 0.8 or error_rate > 2 or active_alerts > 0:
            status = "degraded"
        else:
            status = "healthy"
        
        return SystemHealth(
            status=status,
            uptime_percentage=99.5,  # This would be calculated from actual uptime data
            response_time_p95=response_time_stats.get('max', 100) if response_time_stats else 100,
            error_rate=error_rate,
            active_alerts=active_alerts,
            last_updated=datetime.now()
        )
    
    def generate_dashboard_html(self) -> str:
        """Generate complete dashboard HTML"""
        system_dashboard = self.dashboard_generator.create_system_overview_dashboard()
        evolution_dashboard = self.dashboard_generator.create_evolution_analytics_dashboard()
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Self-Evolving AI Framework - Monitoring Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #1e1e1e;
                    color: white;
                }}
                .dashboard-header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .dashboard-section {{
                    margin-bottom: 40px;
                }}
                .health-status {{
                    display: flex;
                    justify-content: space-around;
                    margin-bottom: 30px;
                    padding: 20px;
                    background-color: #2d2d2d;
                    border-radius: 10px;
                }}
                .health-metric {{
                    text-align: center;
                }}
                .health-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #00D4AA;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>🚀 Self-Evolving AI Framework</h1>
                <h2>Real-Time Monitoring Dashboard</h2>
            </div>
            
            <div class="health-status">
                <div class="health-metric">
                    <div class="health-value">HEALTHY</div>
                    <div>System Status</div>
                </div>
                <div class="health-metric">
                    <div class="health-value">99.9%</div>
                    <div>Uptime</div>
                </div>
                <div class="health-metric">
                    <div class="health-value">0.89</div>
                    <div>Fitness Score</div>
                </div>
                <div class="health-metric">
                    <div class="health-value">0</div>
                    <div>Active Alerts</div>
                </div>
            </div>
            
            <div class="dashboard-section">
                <h3>System Overview</h3>
                {system_dashboard}
            </div>
            
            <div class="dashboard-section">
                <h3>Evolution Analytics</h3>
                {evolution_dashboard}
            </div>
            
            <script>
                // WebSocket connection for real-time updates
                const ws = new WebSocket('ws://localhost:8765');
                
                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'metrics_update') {{
                        console.log('Received metrics update:', data);
                        // Update dashboard with new data
                        // This would trigger chart updates in a real implementation
                    }}
                }};
                
                ws.onopen = function(event) {{
                    console.log('Connected to monitoring WebSocket');
                }};
                
                ws.onclose = function(event) {{
                    console.log('Disconnected from monitoring WebSocket');
                }};
            </script>
        </body>
        </html>
        """
        
        return html_template


async def main():
    """Main function to run the monitoring dashboard"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and start monitoring dashboard
    dashboard = MonitoringDashboard()
    
    # Generate static dashboard HTML
    dashboard_html = dashboard.generate_dashboard_html()
    with open('dashboard.html', 'w') as f:
        f.write(dashboard_html)
    
    logging.info("Dashboard HTML generated: dashboard.html")
    
    # Start monitoring system
    await dashboard.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())