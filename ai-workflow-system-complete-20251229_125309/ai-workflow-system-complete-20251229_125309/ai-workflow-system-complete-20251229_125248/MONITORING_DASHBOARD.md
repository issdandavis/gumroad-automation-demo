# AI Workflow Architect - Monitoring Dashboard

## Real-Time System Monitoring

### Executive Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI WORKFLOW ARCHITECT                        │
│                   System Health Dashboard                       │
└─────────────────────────────────────────────────────────────────┘

🟢 System Status: HEALTHY
📊 Active Users: 1,247
🤖 AI Requests/min: 342
💰 Daily Cost: $127.45
⚡ Avg Response: 245ms

┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│   Web Tier      │  Application    │   AI Services   │   Data Layer    │
│                 │     Tier        │                 │                 │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ 🟢 ECS Tasks: 3 │ 🟢 API Srv: 3   │ 🟢 Bedrock: ✓   │ 🟢 RDS: 98%     │
│ 📈 CPU: 45%     │ 📈 CPU: 62%     │ 🔄 OpenAI: ✓    │ 🔗 Conn: 15/100 │
│ 💾 RAM: 67%     │ 💾 RAM: 71%     │ ⚡ Anthropic: ✓ │ 📊 Cache: 89%   │
│ 🌐 ALB: 99.9%   │ 🔄 Queue: 12    │ 🎯 xAI: ✓       │ 💿 Storage: 45% │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘

Recent Alerts:
🟡 High memory usage on API-2 (85%) - Auto-scaling triggered
🟢 Database backup completed successfully
🟢 SSL certificate renewed automatically
```

### Key Performance Indicators (KPIs)

#### System Performance Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Uptime** | 99.97% | 99.9% | 🟢 Excellent |
| **Response Time** | 245ms | <500ms | 🟢 Good |
| **Error Rate** | 0.02% | <0.1% | 🟢 Excellent |
| **Throughput** | 342 req/min | >200 req/min | 🟢 Good |
| **AI Success Rate** | 99.8% | >99% | 🟢 Excellent |

#### Business Metrics

| Metric | Today | This Week | This Month |
|--------|-------|-----------|------------|
| **Active Users** | 1,247 | 8,934 | 34,567 |
| **AI Requests** | 24,680 | 172,760 | 689,450 |
| **Cost per Request** | $0.0052 | $0.0048 | $0.0051 |
| **Revenue** | $2,340 | $16,780 | $67,890 |
| **Profit Margin** | 73% | 75% | 74% |

### Real-Time Monitoring Components

#### 1. Infrastructure Health Monitor

```python
import boto3
import json
from datetime import datetime, timedelta

class InfrastructureMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.ecs = boto3.client('ecs')
        self.rds = boto3.client('rds')
        self.elasticache = boto3.client('elasticache')
    
    def get_system_health(self):
        """Get comprehensive system health status"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # ECS Health
        ecs_health = self.check_ecs_health()
        health_status['components']['ecs'] = ecs_health
        
        # RDS Health
        rds_health = self.check_rds_health()
        health_status['components']['rds'] = rds_health
        
        # ElastiCache Health
        cache_health = self.check_cache_health()
        health_status['components']['cache'] = cache_health
        
        # AI Services Health
        ai_health = self.check_ai_services_health()
        health_status['components']['ai_services'] = ai_health
        
        # Determine overall status
        component_statuses = [comp['status'] for comp in health_status['components'].values()]
        if 'critical' in component_statuses:
            health_status['overall_status'] = 'critical'
        elif 'warning' in component_statuses:
            health_status['overall_status'] = 'warning'
        
        return health_status
    
    def check_ecs_health(self):
        """Check ECS cluster and service health"""
        try:
            # Get cluster info
            clusters = self.ecs.describe_clusters(clusters=['ai-workflow-cluster'])
            cluster = clusters['clusters'][0]
            
            # Get service info
            services = self.ecs.describe_services(
                cluster='ai-workflow-cluster',
                services=['ai-workflow-web', 'ai-workflow-api']
            )
            
            running_tasks = cluster['runningTasksCount']
            desired_tasks = sum(service['desiredCount'] for service in services['services'])
            
            health_ratio = running_tasks / desired_tasks if desired_tasks > 0 else 0
            
            if health_ratio >= 0.9:
                status = 'healthy'
            elif health_ratio >= 0.7:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'running_tasks': running_tasks,
                'desired_tasks': desired_tasks,
                'health_ratio': health_ratio,
                'services': len(services['services'])
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def check_rds_health(self):
        """Check RDS database health"""
        try:
            instances = self.rds.describe_db_instances(
                DBInstanceIdentifier='ai-workflow-db'
            )
            
            db_instance = instances['DBInstances'][0]
            status = db_instance['DBInstanceStatus']
            
            # Get CloudWatch metrics
            cpu_metrics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': 'ai-workflow-db'
                    }
                ],
                StartTime=datetime.now() - timedelta(minutes=5),
                EndTime=datetime.now(),
                Period=300,
                Statistics=['Average']
            )
            
            avg_cpu = cpu_metrics['Datapoints'][-1]['Average'] if cpu_metrics['Datapoints'] else 0
            
            if status == 'available' and avg_cpu < 80:
                health_status = 'healthy'
            elif status == 'available' and avg_cpu < 90:
                health_status = 'warning'
            else:
                health_status = 'critical'
            
            return {
                'status': health_status,
                'db_status': status,
                'cpu_utilization': avg_cpu,
                'engine': db_instance['Engine'],
                'multi_az': db_instance['MultiAZ']
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def check_cache_health(self):
        """Check ElastiCache Redis health"""
        try:
            clusters = self.elasticache.describe_replication_groups(
                ReplicationGroupId='ai-workflow-redis'
            )
            
            cluster = clusters['ReplicationGroups'][0]
            status = cluster['Status']
            
            if status == 'available':
                health_status = 'healthy'
            else:
                health_status = 'warning'
            
            return {
                'status': health_status,
                'cluster_status': status,
                'num_cache_clusters': cluster['NumCacheClusters'],
                'engine': cluster['CacheNodeType']
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def check_ai_services_health(self):
        """Check AI service providers health"""
        providers = {
            'bedrock': self.check_bedrock_health(),
            'openai': self.check_openai_health(),
            'anthropic': self.check_anthropic_health(),
            'xai': self.check_xai_health()
        }
        
        healthy_providers = sum(1 for p in providers.values() if p['status'] == 'healthy')
        total_providers = len(providers)
        
        if healthy_providers == total_providers:
            overall_status = 'healthy'
        elif healthy_providers >= total_providers * 0.75:
            overall_status = 'warning'
        else:
            overall_status = 'critical'
        
        return {
            'status': overall_status,
            'providers': providers,
            'healthy_count': healthy_providers,
            'total_count': total_providers
        }
    
    def check_bedrock_health(self):
        """Check AWS Bedrock service health"""
        try:
            bedrock = boto3.client('bedrock-runtime')
            # Simple health check - list available models
            models = bedrock.list_foundation_models()
            return {
                'status': 'healthy',
                'available_models': len(models['modelSummaries'])
            }
        except Exception as e:
            return {
                'status': 'critical',
                'error': str(e)
            }
    
    def check_openai_health(self):
        """Check OpenAI API health"""
        # This would typically make a test API call
        return {'status': 'healthy', 'last_check': datetime.now().isoformat()}
    
    def check_anthropic_health(self):
        """Check Anthropic API health"""
        # This would typically make a test API call
        return {'status': 'healthy', 'last_check': datetime.now().isoformat()}
    
    def check_xai_health(self):
        """Check xAI API health"""
        # This would typically make a test API call
        return {'status': 'healthy', 'last_check': datetime.now().isoformat()}
```

#### 2. Performance Analytics Dashboard

```python
class PerformanceAnalytics:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.timestream = boto3.client('timestream-query')
    
    def get_performance_metrics(self, time_range='1h'):
        """Get comprehensive performance metrics"""
        end_time = datetime.now()
        
        if time_range == '1h':
            start_time = end_time - timedelta(hours=1)
            period = 300  # 5 minutes
        elif time_range == '24h':
            start_time = end_time - timedelta(days=1)
            period = 3600  # 1 hour
        elif time_range == '7d':
            start_time = end_time - timedelta(days=7)
            period = 86400  # 1 day
        
        metrics = {
            'response_times': self.get_response_time_metrics(start_time, end_time, period),
            'throughput': self.get_throughput_metrics(start_time, end_time, period),
            'error_rates': self.get_error_rate_metrics(start_time, end_time, period),
            'resource_utilization': self.get_resource_metrics(start_time, end_time, period),
            'ai_performance': self.get_ai_performance_metrics(start_time, end_time, period)
        }
        
        return metrics
    
    def get_response_time_metrics(self, start_time, end_time, period):
        """Get API response time metrics"""
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='TargetResponseTime',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': 'app/ai-workflow-alb/1234567890abcdef'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average', 'Maximum', 'Minimum']
        )
        
        datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
        
        return {
            'average': [dp['Average'] * 1000 for dp in datapoints],  # Convert to ms
            'maximum': [dp['Maximum'] * 1000 for dp in datapoints],
            'minimum': [dp['Minimum'] * 1000 for dp in datapoints],
            'timestamps': [dp['Timestamp'].isoformat() for dp in datapoints]
        }
    
    def get_throughput_metrics(self, start_time, end_time, period):
        """Get request throughput metrics"""
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='RequestCount',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': 'app/ai-workflow-alb/1234567890abcdef'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Sum']
        )
        
        datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
        
        return {
            'requests_per_period': [dp['Sum'] for dp in datapoints],
            'requests_per_minute': [dp['Sum'] / (period / 60) for dp in datapoints],
            'timestamps': [dp['Timestamp'].isoformat() for dp in datapoints]
        }
    
    def get_error_rate_metrics(self, start_time, end_time, period):
        """Get error rate metrics"""
        # Get total requests
        total_requests = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='RequestCount',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': 'app/ai-workflow-alb/1234567890abcdef'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Sum']
        )
        
        # Get 4xx errors
        client_errors = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='HTTPCode_Target_4XX_Count',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': 'app/ai-workflow-alb/1234567890abcdef'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Sum']
        )
        
        # Get 5xx errors
        server_errors = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='HTTPCode_Target_5XX_Count',
            Dimensions=[
                {
                    'Name': 'LoadBalancer',
                    'Value': 'app/ai-workflow-alb/1234567890abcdef'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Sum']
        )
        
        # Calculate error rates
        total_datapoints = {dp['Timestamp']: dp['Sum'] for dp in total_requests['Datapoints']}
        client_datapoints = {dp['Timestamp']: dp['Sum'] for dp in client_errors['Datapoints']}
        server_datapoints = {dp['Timestamp']: dp['Sum'] for dp in server_errors['Datapoints']}
        
        error_rates = []
        timestamps = []
        
        for timestamp, total in total_datapoints.items():
            client_count = client_datapoints.get(timestamp, 0)
            server_count = server_datapoints.get(timestamp, 0)
            error_count = client_count + server_count
            
            error_rate = (error_count / total * 100) if total > 0 else 0
            
            error_rates.append(error_rate)
            timestamps.append(timestamp.isoformat())
        
        return {
            'error_rate_percentage': error_rates,
            'timestamps': timestamps
        }
    
    def get_resource_metrics(self, start_time, end_time, period):
        """Get resource utilization metrics"""
        # ECS CPU utilization
        ecs_cpu = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'ServiceName',
                    'Value': 'ai-workflow-web'
                },
                {
                    'Name': 'ClusterName',
                    'Value': 'ai-workflow-cluster'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        
        # ECS Memory utilization
        ecs_memory = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='MemoryUtilization',
            Dimensions=[
                {
                    'Name': 'ServiceName',
                    'Value': 'ai-workflow-web'
                },
                {
                    'Name': 'ClusterName',
                    'Value': 'ai-workflow-cluster'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        
        # RDS CPU utilization
        rds_cpu = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'DBInstanceIdentifier',
                    'Value': 'ai-workflow-db'
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        
        return {
            'ecs_cpu': [dp['Average'] for dp in sorted(ecs_cpu['Datapoints'], key=lambda x: x['Timestamp'])],
            'ecs_memory': [dp['Average'] for dp in sorted(ecs_memory['Datapoints'], key=lambda x: x['Timestamp'])],
            'rds_cpu': [dp['Average'] for dp in sorted(rds_cpu['Datapoints'], key=lambda x: x['Timestamp'])],
            'timestamps': [dp['Timestamp'].isoformat() for dp in sorted(ecs_cpu['Datapoints'], key=lambda x: x['Timestamp'])]
        }
    
    def get_ai_performance_metrics(self, start_time, end_time, period):
        """Get AI service performance metrics"""
        # This would query custom metrics for AI performance
        return {
            'ai_request_count': [120, 135, 142, 138, 145],
            'ai_success_rate': [99.8, 99.9, 99.7, 99.8, 99.9],
            'ai_response_time': [1200, 1150, 1180, 1160, 1140],
            'cost_per_request': [0.0052, 0.0051, 0.0053, 0.0052, 0.0051],
            'timestamps': ['2024-01-01T10:00:00Z', '2024-01-01T10:05:00Z', '2024-01-01T10:10:00Z', '2024-01-01T10:15:00Z', '2024-01-01T10:20:00Z']
        }
```

#### 3. Cost Monitoring Dashboard

```python
class CostMonitor:
    def __init__(self):
        self.ce = boto3.client('ce')  # Cost Explorer
        self.pricing = boto3.client('pricing', region_name='us-east-1')
    
    def get_cost_breakdown(self, time_period='MONTHLY'):
        """Get detailed cost breakdown by service"""
        end_date = datetime.now()
        
        if time_period == 'DAILY':
            start_date = end_date - timedelta(days=1)
        elif time_period == 'WEEKLY':
            start_date = end_date - timedelta(days=7)
        elif time_period == 'MONTHLY':
            start_date = end_date - timedelta(days=30)
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['BlendedCost', 'UsageQuantity'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        cost_breakdown = {}
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                
                if service not in cost_breakdown:
                    cost_breakdown[service] = 0
                
                cost_breakdown[service] += cost
                total_cost += cost
        
        # Calculate percentages
        cost_percentages = {
            service: (cost / total_cost * 100) if total_cost > 0 else 0
            for service, cost in cost_breakdown.items()
        }
        
        return {
            'total_cost': total_cost,
            'cost_breakdown': cost_breakdown,
            'cost_percentages': cost_percentages,
            'period': time_period
        }
    
    def get_ai_cost_analysis(self):
        """Get detailed AI service cost analysis"""
        # This would analyze costs for different AI providers
        return {
            'bedrock_cost': 45.67,
            'openai_cost': 32.45,
            'anthropic_cost': 28.90,
            'xai_cost': 15.23,
            'total_ai_cost': 122.25,
            'cost_per_request': 0.0052,
            'requests_today': 23456,
            'projected_monthly': 3678.90
        }
    
    def get_cost_optimization_recommendations(self):
        """Get cost optimization recommendations"""
        recommendations = []
        
        # Analyze Reserved Instance opportunities
        ri_response = self.ce.get_reservation_purchase_recommendation(
            Service='Amazon Elastic Compute Cloud - Compute'
        )
        
        for recommendation in ri_response.get('Recommendations', []):
            recommendations.append({
                'type': 'Reserved Instance',
                'service': 'EC2',
                'potential_savings': recommendation.get('RecommendationDetails', {}).get('EstimatedMonthlySavingsAmount', 0),
                'description': f"Purchase {recommendation.get('RecommendationDetails', {}).get('InstanceDetails', {}).get('InstanceType', 'N/A')} Reserved Instances"
            })
        
        # Add custom recommendations
        recommendations.extend([
            {
                'type': 'Right Sizing',
                'service': 'ECS',
                'potential_savings': 156.78,
                'description': 'Reduce ECS task memory allocation from 2GB to 1.5GB based on usage patterns'
            },
            {
                'type': 'Storage Optimization',
                'service': 'S3',
                'potential_savings': 89.45,
                'description': 'Move infrequently accessed logs to S3 Intelligent Tiering'
            },
            {
                'type': 'AI Optimization',
                'service': 'Bedrock',
                'potential_savings': 234.56,
                'description': 'Implement request caching to reduce duplicate AI API calls'
            }
        ])
        
        return recommendations
```

#### 4. Alert Management System

```python
class AlertManager:
    def __init__(self):
        self.sns = boto3.client('sns')
        self.cloudwatch = boto3.client('cloudwatch')
        self.ses = boto3.client('ses')
    
    def create_alert_rules(self):
        """Create comprehensive alert rules"""
        alert_rules = [
            {
                'name': 'HighCPUUtilization',
                'metric': 'CPUUtilization',
                'threshold': 80,
                'comparison': 'GreaterThanThreshold',
                'evaluation_periods': 2,
                'period': 300,
                'severity': 'WARNING'
            },
            {
                'name': 'HighMemoryUtilization',
                'metric': 'MemoryUtilization',
                'threshold': 85,
                'comparison': 'GreaterThanThreshold',
                'evaluation_periods': 2,
                'period': 300,
                'severity': 'WARNING'
            },
            {
                'name': 'HighErrorRate',
                'metric': 'HTTPCode_Target_5XX_Count',
                'threshold': 10,
                'comparison': 'GreaterThanThreshold',
                'evaluation_periods': 1,
                'period': 300,
                'severity': 'CRITICAL'
            },
            {
                'name': 'DatabaseConnectionsHigh',
                'metric': 'DatabaseConnections',
                'threshold': 80,
                'comparison': 'GreaterThanThreshold',
                'evaluation_periods': 2,
                'period': 300,
                'severity': 'WARNING'
            },
            {
                'name': 'AIServiceFailure',
                'metric': 'AIRequestFailureRate',
                'threshold': 5,
                'comparison': 'GreaterThanThreshold',
                'evaluation_periods': 1,
                'period': 300,
                'severity': 'CRITICAL'
            }
        ]
        
        for rule in alert_rules:
            self.create_cloudwatch_alarm(rule)
    
    def create_cloudwatch_alarm(self, rule):
        """Create CloudWatch alarm"""
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=rule['name'],
                ComparisonOperator=rule['comparison'],
                EvaluationPeriods=rule['evaluation_periods'],
                MetricName=rule['metric'],
                Namespace='AIWorkflow/Custom',
                Period=rule['period'],
                Statistic='Average',
                Threshold=rule['threshold'],
                ActionsEnabled=True,
                AlarmActions=[
                    'arn:aws:sns:us-east-1:123456789012:ai-workflow-alerts'
                ],
                AlarmDescription=f"Alert for {rule['name']} - Severity: {rule['severity']}",
                Unit='Percent' if 'Utilization' in rule['metric'] else 'Count'
            )
        except Exception as e:
            print(f"Failed to create alarm {rule['name']}: {e}")
    
    def send_alert_notification(self, alert_type, message, severity='INFO'):
        """Send alert notification via multiple channels"""
        # Send SNS notification
        self.sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:ai-workflow-alerts',
            Message=message,
            Subject=f"AI Workflow Alert - {severity}: {alert_type}"
        )
        
        # Send email for critical alerts
        if severity in ['CRITICAL', 'HIGH']:
            self.send_email_alert(alert_type, message, severity)
        
        # Log to CloudWatch
        self.cloudwatch.put_metric_data(
            Namespace='AIWorkflow/Alerts',
            MetricData=[
                {
                    'MetricName': f'Alert_{severity}',
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.now()
                }
            ]
        )
    
    def send_email_alert(self, alert_type, message, severity):
        """Send email alert for critical issues"""
        try:
            self.ses.send_email(
                Source='alerts@aiworkflow.com',
                Destination={
                    'ToAddresses': ['admin@aiworkflow.com', 'ops@aiworkflow.com']
                },
                Message={
                    'Subject': {
                        'Data': f'🚨 {severity} Alert: {alert_type}',
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': f"""
                            <html>
                            <body>
                                <h2 style="color: red;">AI Workflow Architect Alert</h2>
                                <p><strong>Severity:</strong> {severity}</p>
                                <p><strong>Alert Type:</strong> {alert_type}</p>
                                <p><strong>Time:</strong> {datetime.now().isoformat()}</p>
                                <p><strong>Message:</strong></p>
                                <div style="background-color: #f5f5f5; padding: 10px; border-left: 4px solid #ff0000;">
                                    {message}
                                </div>
                                <p>Please investigate immediately.</p>
                            </body>
                            </html>
                            """,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
        except Exception as e:
            print(f"Failed to send email alert: {e}")
```

### Dashboard Visualization Components

#### Real-Time Metrics Display

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Workflow Architect - Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #4CAF50; }
        .status-warning { background-color: #FF9800; }
        .status-critical { background-color: #F44336; }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>AI Workflow Architect - System Monitoring</h1>
        <p>Real-time system health and performance metrics</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" id="system-status">
                <span class="status-indicator status-healthy"></span>HEALTHY
            </div>
            <div class="metric-label">System Status</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" id="active-users">1,247</div>
            <div class="metric-label">Active Users</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" id="ai-requests">342/min</div>
            <div class="metric-label">AI Requests</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" id="daily-cost">$127.45</div>
            <div class="metric-label">Daily Cost</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" id="response-time">245ms</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-value" id="uptime">99.97%</div>
            <div class="metric-label">Uptime</div>
        </div>
    </div>

    <div class="chart-container">
        <h3>Response Time Trends</h3>
        <canvas id="responseTimeChart" width="400" height="200"></canvas>
    </div>

    <div class="chart-container">
        <h3>System Resource Utilization</h3>
        <canvas id="resourceChart" width="400" height="200"></canvas>
    </div>

    <div class="chart-container">
        <h3>AI Service Performance</h3>
        <canvas id="aiPerformanceChart" width="400" height="200"></canvas>
    </div>

    <script>
        // Initialize charts
        const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
        const resourceCtx = document.getElementById('resourceChart').getContext('2d');
        const aiPerformanceCtx = document.getElementById('aiPerformanceChart').getContext('2d');

        // Response Time Chart
        const responseTimeChart = new Chart(responseTimeCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                }
            }
        });

        // Resource Utilization Chart
        const resourceChart = new Chart(resourceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'CPU %',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)'
                    },
                    {
                        label: 'Memory %',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Utilization %'
                        }
                    }
                }
            }
        });

        // AI Performance Chart
        const aiPerformanceChart = new Chart(aiPerformanceCtx, {
            type: 'doughnut',
            data: {
                labels: ['Bedrock', 'OpenAI', 'Anthropic', 'xAI'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'AI Provider Usage Distribution'
                    }
                }
            }
        });

        // Real-time data updates
        function updateMetrics() {
            fetch('/api/metrics/current')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('active-users').textContent = data.activeUsers.toLocaleString();
                    document.getElementById('ai-requests').textContent = `${data.aiRequestsPerMinute}/min`;
                    document.getElementById('daily-cost').textContent = `$${data.dailyCost.toFixed(2)}`;
                    document.getElementById('response-time').textContent = `${data.avgResponseTime}ms`;
                    document.getElementById('uptime').textContent = `${data.uptime}%`;
                    
                    // Update system status
                    const statusElement = document.getElementById('system-status');
                    const indicator = statusElement.querySelector('.status-indicator');
                    
                    indicator.className = `status-indicator status-${data.systemStatus}`;
                    statusElement.innerHTML = `<span class="status-indicator status-${data.systemStatus}"></span>${data.systemStatus.toUpperCase()}`;
                })
                .catch(error => console.error('Error fetching metrics:', error));
        }

        function updateCharts() {
            fetch('/api/metrics/timeseries')
                .then(response => response.json())
                .then(data => {
                    // Update response time chart
                    responseTimeChart.data.labels = data.timestamps;
                    responseTimeChart.data.datasets[0].data = data.responseTimes;
                    responseTimeChart.update();
                    
                    // Update resource chart
                    resourceChart.data.labels = data.timestamps;
                    resourceChart.data.datasets[0].data = data.cpuUtilization;
                    resourceChart.data.datasets[1].data = data.memoryUtilization;
                    resourceChart.update();
                    
                    // Update AI performance chart
                    aiPerformanceChart.data.datasets[0].data = data.aiProviderUsage;
                    aiPerformanceChart.update();
                })
                .catch(error => console.error('Error fetching chart data:', error));
        }

        // Update metrics every 30 seconds
        setInterval(updateMetrics, 30000);
        setInterval(updateCharts, 60000);

        // Initial load
        updateMetrics();
        updateCharts();
    </script>
</body>
</html>
```

This comprehensive monitoring dashboard provides real-time visibility into system health, performance metrics, cost analysis, and AI service performance with automated alerting and detailed analytics.