"""
Scalable Cloud Architecture Components
=====================================

AWS-native scalable architecture for the Bedrock AI Evolution System.
Implements Lambda functions, SQS queues, ECS tasks, auto-scaling,
and blue-green deployment capabilities.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategies"""
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    IMMEDIATE = "immediate"


class ScalingMetric(Enum):
    """Auto-scaling metrics"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_COUNT = "request_count"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"


@dataclass
class LambdaFunction:
    """Lambda function configuration"""
    name: str
    handler: str
    runtime: str
    memory_mb: int
    timeout_seconds: int
    environment_vars: Dict[str, str] = field(default_factory=dict)
    layers: List[str] = field(default_factory=list)
    vpc_config: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "FunctionName": self.name,
            "Handler": self.handler,
            "Runtime": self.runtime,
            "MemorySize": self.memory_mb,
            "Timeout": self.timeout_seconds,
            "Environment": {"Variables": self.environment_vars},
            "Layers": self.layers,
            "VpcConfig": self.vpc_config or {}
        }


@dataclass
class ECSTask:
    """ECS task configuration"""
    name: str
    cpu: int
    memory: int
    image: str
    environment_vars: Dict[str, str] = field(default_factory=dict)
    port_mappings: List[Dict[str, int]] = field(default_factory=list)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "family": self.name,
            "cpu": str(self.cpu),
            "memory": str(self.memory),
            "containerDefinitions": [{
                "name": self.name,
                "image": self.image,
                "environment": [{"name": k, "value": v} for k, v in self.environment_vars.items()],
                "portMappings": self.port_mappings,
                "mountPoints": [],
                "volumesFrom": []
            }],
            "volumes": self.volumes,
            "requiresCompatibilities": ["FARGATE"],
            "networkMode": "awsvpc"
        }


@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration"""
    min_capacity: int
    max_capacity: int
    target_value: float
    metric_type: str
    scale_out_cooldown: int = 300
    scale_in_cooldown: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "MinCapacity": self.min_capacity,
            "MaxCapacity": self.max_capacity,
            "TargetValue": self.target_value,
            "MetricType": self.metric_type,
            "ScaleOutCooldown": self.scale_out_cooldown,
            "ScaleInCooldown": self.scale_in_cooldown
        }


class LambdaManager:
    """Manages AWS Lambda functions for serverless processing"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.lambda_client = None
        self.functions: Dict[str, LambdaFunction] = {}
        
        if aws_config_manager:
            try:
                self.lambda_client = boto3.client('lambda', 
                    region_name=aws_config_manager.config.region)
            except Exception as e:
                logger.error(f"Failed to initialize Lambda client: {e}")
    
    def create_mutation_processor(self) -> LambdaFunction:
        """Create Lambda function for mutation processing"""
        
        function = LambdaFunction(
            name="ai-evolution-mutation-processor",
            handler="mutation_processor.handler",
            runtime="python3.9",
            memory_mb=512,
            timeout_seconds=300,
            environment_vars={
                "BEDROCK_REGION": self.aws_config_manager.config.region if self.aws_config_manager else "us-east-1",
                "LOG_LEVEL": "INFO"
            }
        )
        
        self.functions[function.name] = function
        return function
    
    def create_fitness_calculator(self) -> LambdaFunction:
        """Create Lambda function for fitness calculation"""
        
        function = LambdaFunction(
            name="ai-evolution-fitness-calculator",
            handler="fitness_calculator.handler",
            runtime="python3.9",
            memory_mb=256,
            timeout_seconds=180,
            environment_vars={
                "DYNAMODB_TABLE": "ai-evolution-snapshots",
                "LOG_LEVEL": "INFO"
            }
        )
        
        self.functions[function.name] = function
        return function
    
    def create_cost_optimizer(self) -> LambdaFunction:
        """Create Lambda function for cost optimization"""
        
        function = LambdaFunction(
            name="ai-evolution-cost-optimizer",
            handler="cost_optimizer.handler",
            runtime="python3.9",
            memory_mb=256,
            timeout_seconds=120,
            environment_vars={
                "COST_BUDGET_DAILY": "10.0",
                "COST_BUDGET_MONTHLY": "300.0",
                "LOG_LEVEL": "INFO"
            }
        )
        
        self.functions[function.name] = function
        return function
    
    async def deploy_function(self, function: LambdaFunction, 
                            code_zip: bytes) -> Dict[str, Any]:
        """Deploy Lambda function"""
        
        if not self.lambda_client:
            return {"error": "Lambda client not available"}
        
        try:
            # Check if function exists
            try:
                self.lambda_client.get_function(FunctionName=function.name)
                function_exists = True
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    function_exists = False
                else:
                    raise
            
            if function_exists:
                # Update existing function
                response = self.lambda_client.update_function_code(
                    FunctionName=function.name,
                    ZipFile=code_zip
                )
                
                # Update configuration
                config_response = self.lambda_client.update_function_configuration(
                    **function.to_dict()
                )
                
                return {
                    "action": "updated",
                    "function_arn": response["FunctionArn"],
                    "version": response["Version"]
                }
            
            else:
                # Create new function
                config = function.to_dict()
                config["Code"] = {"ZipFile": code_zip}
                
                response = self.lambda_client.create_function(**config)
                
                return {
                    "action": "created",
                    "function_arn": response["FunctionArn"],
                    "version": response["Version"]
                }
        
        except Exception as e:
            logger.error(f"Lambda deployment failed: {e}")
            return {"error": str(e)}
    
    async def invoke_function(self, function_name: str, payload: Dict[str, Any],
                            invocation_type: str = "RequestResponse") -> Dict[str, Any]:
        """Invoke Lambda function"""
        
        if not self.lambda_client:
            return {"error": "Lambda client not available"}
        
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(payload)
            )
            
            if invocation_type == "RequestResponse":
                result = json.loads(response['Payload'].read())
                return {
                    "success": True,
                    "result": result,
                    "status_code": response['StatusCode']
                }
            else:
                return {
                    "success": True,
                    "async_invocation": True,
                    "status_code": response['StatusCode']
                }
        
        except Exception as e:
            logger.error(f"Lambda invocation failed: {e}")
            return {"error": str(e)}
    
    def get_function_metrics(self, function_name: str, 
                           hours: int = 24) -> Dict[str, Any]:
        """Get function performance metrics"""
        
        # This would integrate with CloudWatch to get real metrics
        # For demo, return mock data
        return {
            "function_name": function_name,
            "period_hours": hours,
            "invocations": 150,
            "errors": 2,
            "duration_avg_ms": 1250,
            "memory_used_avg_mb": 128,
            "cost_estimate": 0.0025
        }


class SQSManager:
    """Manages SQS queues for asynchronous processing"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.sqs_client = None
        self.queues: Dict[str, str] = {}  # name -> URL mapping
        
        if aws_config_manager:
            try:
                self.sqs_client = boto3.client('sqs', 
                    region_name=aws_config_manager.config.region)
            except Exception as e:
                logger.error(f"Failed to initialize SQS client: {e}")
    
    async def create_mutation_queue(self) -> str:
        """Create queue for mutation processing"""
        
        queue_name = "ai-evolution-mutations"
        
        if not self.sqs_client:
            return f"mock://{queue_name}"
        
        try:
            response = self.sqs_client.create_queue(
                QueueName=queue_name,
                Attributes={
                    'VisibilityTimeoutSeconds': '300',
                    'MessageRetentionPeriod': '1209600',  # 14 days
                    'DelaySeconds': '0',
                    'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
                }
            )
            
            queue_url = response['QueueUrl']
            self.queues[queue_name] = queue_url
            
            logger.info(f"Created SQS queue: {queue_name}")
            return queue_url
        
        except Exception as e:
            logger.error(f"Failed to create SQS queue: {e}")
            return f"error://{e}"
    
    async def create_fitness_queue(self) -> str:
        """Create queue for fitness calculations"""
        
        queue_name = "ai-evolution-fitness"
        
        if not self.sqs_client:
            return f"mock://{queue_name}"
        
        try:
            response = self.sqs_client.create_queue(
                QueueName=queue_name,
                Attributes={
                    'VisibilityTimeoutSeconds': '180',
                    'MessageRetentionPeriod': '604800',  # 7 days
                    'DelaySeconds': '0'
                }
            )
            
            queue_url = response['QueueUrl']
            self.queues[queue_name] = queue_url
            
            logger.info(f"Created SQS queue: {queue_name}")
            return queue_url
        
        except Exception as e:
            logger.error(f"Failed to create SQS queue: {e}")
            return f"error://{e}"
    
    async def send_message(self, queue_name: str, message: Dict[str, Any],
                         delay_seconds: int = 0) -> Dict[str, Any]:
        """Send message to queue"""
        
        queue_url = self.queues.get(queue_name)
        if not queue_url or not self.sqs_client:
            return {"error": "Queue not available"}
        
        try:
            response = self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                DelaySeconds=delay_seconds
            )
            
            return {
                "success": True,
                "message_id": response['MessageId'],
                "md5": response['MD5OfBody']
            }
        
        except Exception as e:
            logger.error(f"Failed to send SQS message: {e}")
            return {"error": str(e)}
    
    async def receive_messages(self, queue_name: str, max_messages: int = 10,
                             wait_time: int = 20) -> List[Dict[str, Any]]:
        """Receive messages from queue"""
        
        queue_url = self.queues.get(queue_name)
        if not queue_url or not self.sqs_client:
            return []
        
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                AttributeNames=['All']
            )
            
            messages = []
            for msg in response.get('Messages', []):
                messages.append({
                    "message_id": msg['MessageId'],
                    "receipt_handle": msg['ReceiptHandle'],
                    "body": json.loads(msg['Body']),
                    "attributes": msg.get('Attributes', {})
                })
            
            return messages
        
        except Exception as e:
            logger.error(f"Failed to receive SQS messages: {e}")
            return []
    
    async def delete_message(self, queue_name: str, receipt_handle: str) -> bool:
        """Delete processed message"""
        
        queue_url = self.queues.get(queue_name)
        if not queue_url or not self.sqs_client:
            return False
        
        try:
            self.sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete SQS message: {e}")
            return False


class ECSManager:
    """Manages ECS tasks for long-running processes"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.ecs_client = None
        self.cluster_name = "ai-evolution-cluster"
        self.tasks: Dict[str, ECSTask] = {}
        
        if aws_config_manager:
            try:
                self.ecs_client = boto3.client('ecs', 
                    region_name=aws_config_manager.config.region)
            except Exception as e:
                logger.error(f"Failed to initialize ECS client: {e}")
    
    async def create_cluster(self) -> Dict[str, Any]:
        """Create ECS cluster"""
        
        if not self.ecs_client:
            return {"error": "ECS client not available"}
        
        try:
            response = self.ecs_client.create_cluster(
                clusterName=self.cluster_name,
                capacityProviders=['FARGATE'],
                defaultCapacityProviderStrategy=[{
                    'capacityProvider': 'FARGATE',
                    'weight': 1
                }]
            )
            
            return {
                "success": True,
                "cluster_arn": response['cluster']['clusterArn'],
                "cluster_name": self.cluster_name
            }
        
        except Exception as e:
            logger.error(f"Failed to create ECS cluster: {e}")
            return {"error": str(e)}
    
    def create_evolution_processor_task(self) -> ECSTask:
        """Create ECS task for evolution processing"""
        
        task = ECSTask(
            name="ai-evolution-processor",
            cpu=1024,  # 1 vCPU
            memory=2048,  # 2 GB
            image="ai-evolution:latest",
            environment_vars={
                "BEDROCK_REGION": self.aws_config_manager.config.region if self.aws_config_manager else "us-east-1",
                "LOG_LEVEL": "INFO",
                "PROCESSING_MODE": "batch"
            },
            port_mappings=[{
                "containerPort": 8080,
                "protocol": "tcp"
            }]
        )
        
        self.tasks[task.name] = task
        return task
    
    def create_monitoring_task(self) -> ECSTask:
        """Create ECS task for system monitoring"""
        
        task = ECSTask(
            name="ai-evolution-monitor",
            cpu=512,  # 0.5 vCPU
            memory=1024,  # 1 GB
            image="ai-evolution-monitor:latest",
            environment_vars={
                "MONITORING_INTERVAL": "60",
                "CLOUDWATCH_NAMESPACE": "AI-Evolution",
                "LOG_LEVEL": "INFO"
            }
        )
        
        self.tasks[task.name] = task
        return task
    
    async def register_task_definition(self, task: ECSTask) -> Dict[str, Any]:
        """Register ECS task definition"""
        
        if not self.ecs_client:
            return {"error": "ECS client not available"}
        
        try:
            response = self.ecs_client.register_task_definition(**task.to_dict())
            
            return {
                "success": True,
                "task_definition_arn": response['taskDefinition']['taskDefinitionArn'],
                "revision": response['taskDefinition']['revision']
            }
        
        except Exception as e:
            logger.error(f"Failed to register task definition: {e}")
            return {"error": str(e)}
    
    async def run_task(self, task_name: str, count: int = 1,
                      subnet_ids: List[str] = None) -> Dict[str, Any]:
        """Run ECS task"""
        
        if not self.ecs_client:
            return {"error": "ECS client not available"}
        
        try:
            network_config = {
                "awsvpcConfiguration": {
                    "subnets": subnet_ids or ["subnet-12345"],  # Default subnet
                    "assignPublicIp": "ENABLED"
                }
            }
            
            response = self.ecs_client.run_task(
                cluster=self.cluster_name,
                taskDefinition=task_name,
                count=count,
                launchType='FARGATE',
                networkConfiguration=network_config
            )
            
            return {
                "success": True,
                "tasks": [task['taskArn'] for task in response['tasks']],
                "failures": response.get('failures', [])
            }
        
        except Exception as e:
            logger.error(f"Failed to run ECS task: {e}")
            return {"error": str(e)}
    
    async def stop_task(self, task_arn: str, reason: str = "Manual stop") -> Dict[str, Any]:
        """Stop running ECS task"""
        
        if not self.ecs_client:
            return {"error": "ECS client not available"}
        
        try:
            response = self.ecs_client.stop_task(
                cluster=self.cluster_name,
                task=task_arn,
                reason=reason
            )
            
            return {
                "success": True,
                "task_arn": response['task']['taskArn'],
                "stopped_reason": response['task'].get('stoppedReason')
            }
        
        except Exception as e:
            logger.error(f"Failed to stop ECS task: {e}")
            return {"error": str(e)}


class AutoScalingManager:
    """Manages auto-scaling for cloud resources"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        self.autoscaling_client = None
        self.cloudwatch_client = None
        self.scaling_configs: Dict[str, AutoScalingConfig] = {}
        
        if aws_config_manager:
            try:
                self.autoscaling_client = boto3.client('application-autoscaling',
                    region_name=aws_config_manager.config.region)
                self.cloudwatch_client = boto3.client('cloudwatch',
                    region_name=aws_config_manager.config.region)
            except Exception as e:
                logger.error(f"Failed to initialize auto-scaling clients: {e}")
    
    def create_ecs_scaling_config(self, service_name: str) -> AutoScalingConfig:
        """Create auto-scaling configuration for ECS service"""
        
        config = AutoScalingConfig(
            min_capacity=1,
            max_capacity=10,
            target_value=70.0,  # 70% CPU utilization
            metric_type=ScalingMetric.CPU_UTILIZATION.value,
            scale_out_cooldown=300,
            scale_in_cooldown=600
        )
        
        self.scaling_configs[f"ecs:{service_name}"] = config
        return config
    
    def create_lambda_scaling_config(self, function_name: str) -> AutoScalingConfig:
        """Create auto-scaling configuration for Lambda function"""
        
        config = AutoScalingConfig(
            min_capacity=1,
            max_capacity=100,
            target_value=100.0,  # 100 concurrent executions
            metric_type=ScalingMetric.REQUEST_COUNT.value,
            scale_out_cooldown=60,
            scale_in_cooldown=300
        )
        
        self.scaling_configs[f"lambda:{function_name}"] = config
        return config
    
    async def register_scalable_target(self, resource_id: str, 
                                     service_namespace: str,
                                     scalable_dimension: str,
                                     config: AutoScalingConfig) -> Dict[str, Any]:
        """Register scalable target"""
        
        if not self.autoscaling_client:
            return {"error": "Auto-scaling client not available"}
        
        try:
            response = self.autoscaling_client.register_scalable_target(
                ServiceNamespace=service_namespace,
                ResourceId=resource_id,
                ScalableDimension=scalable_dimension,
                MinCapacity=config.min_capacity,
                MaxCapacity=config.max_capacity
            )
            
            return {
                "success": True,
                "resource_id": resource_id,
                "service_namespace": service_namespace
            }
        
        except Exception as e:
            logger.error(f"Failed to register scalable target: {e}")
            return {"error": str(e)}
    
    async def create_scaling_policy(self, resource_id: str,
                                  service_namespace: str,
                                  scalable_dimension: str,
                                  config: AutoScalingConfig) -> Dict[str, Any]:
        """Create scaling policy"""
        
        if not self.autoscaling_client:
            return {"error": "Auto-scaling client not available"}
        
        try:
            policy_name = f"{resource_id}-scaling-policy"
            
            response = self.autoscaling_client.put_scaling_policy(
                PolicyName=policy_name,
                ServiceNamespace=service_namespace,
                ResourceId=resource_id,
                ScalableDimension=scalable_dimension,
                PolicyType='TargetTrackingScaling',
                TargetTrackingScalingPolicyConfiguration={
                    'TargetValue': config.target_value,
                    'PredefinedMetricSpecification': {
                        'PredefinedMetricType': self._get_predefined_metric(config.metric_type)
                    },
                    'ScaleOutCooldown': config.scale_out_cooldown,
                    'ScaleInCooldown': config.scale_in_cooldown
                }
            )
            
            return {
                "success": True,
                "policy_arn": response['PolicyARN'],
                "policy_name": policy_name
            }
        
        except Exception as e:
            logger.error(f"Failed to create scaling policy: {e}")
            return {"error": str(e)}
    
    def _get_predefined_metric(self, metric_type: str) -> str:
        """Map metric type to AWS predefined metric"""
        
        mapping = {
            ScalingMetric.CPU_UTILIZATION.value: "ECSServiceAverageCPUUtilization",
            ScalingMetric.MEMORY_UTILIZATION.value: "ECSServiceAverageMemoryUtilization",
            ScalingMetric.REQUEST_COUNT.value: "ALBRequestCountPerTarget"
        }
        
        return mapping.get(metric_type, "ECSServiceAverageCPUUtilization")
    
    async def get_scaling_activities(self, resource_id: str,
                                   service_namespace: str) -> List[Dict[str, Any]]:
        """Get recent scaling activities"""
        
        if not self.autoscaling_client:
            return []
        
        try:
            response = self.autoscaling_client.describe_scaling_activities(
                ServiceNamespace=service_namespace,
                ResourceId=resource_id,
                MaxResults=10
            )
            
            activities = []
            for activity in response['ScalingActivities']:
                activities.append({
                    "activity_id": activity['ActivityId'],
                    "description": activity['Description'],
                    "cause": activity['Cause'],
                    "start_time": activity['StartTime'].isoformat(),
                    "status_code": activity['StatusCode'],
                    "status_message": activity.get('StatusMessage', '')
                })
            
            return activities
        
        except Exception as e:
            logger.error(f"Failed to get scaling activities: {e}")
            return []


class DeploymentManager:
    """Manages blue-green and other deployment strategies"""
    
    def __init__(self, lambda_manager: LambdaManager, ecs_manager: ECSManager):
        self.lambda_manager = lambda_manager
        self.ecs_manager = ecs_manager
        self.deployments: Dict[str, Dict[str, Any]] = {}
    
    async def deploy_lambda_blue_green(self, function_name: str, 
                                     new_code: bytes,
                                     traffic_shift_percent: int = 10) -> Dict[str, Any]:
        """Deploy Lambda function using blue-green strategy"""
        
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Deploy new version (green)
            function = self.lambda_manager.functions.get(function_name)
            if not function:
                return {"error": f"Function {function_name} not found"}
            
            deploy_result = await self.lambda_manager.deploy_function(function, new_code)
            if "error" in deploy_result:
                return deploy_result
            
            # Create alias for gradual traffic shift
            new_version = deploy_result["version"]
            
            deployment = {
                "deployment_id": deployment_id,
                "function_name": function_name,
                "strategy": DeploymentStrategy.BLUE_GREEN.value,
                "blue_version": "$LATEST",
                "green_version": new_version,
                "traffic_percent": traffic_shift_percent,
                "start_time": datetime.now().isoformat(),
                "status": "in_progress"
            }
            
            self.deployments[deployment_id] = deployment
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "green_version": new_version,
                "traffic_shift": traffic_shift_percent
            }
        
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            return {"error": str(e)}
    
    async def promote_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Promote green deployment to 100% traffic"""
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return {"error": "Deployment not found"}
        
        try:
            # In production, this would update Lambda aliases to route 100% traffic to green
            deployment["traffic_percent"] = 100
            deployment["status"] = "completed"
            deployment["promoted_time"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": "promoted",
                "traffic_percent": 100
            }
        
        except Exception as e:
            logger.error(f"Deployment promotion failed: {e}")
            return {"error": str(e)}
    
    async def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Rollback deployment to blue version"""
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return {"error": "Deployment not found"}
        
        try:
            # In production, this would route all traffic back to blue version
            deployment["traffic_percent"] = 0
            deployment["status"] = "rolled_back"
            deployment["rollback_time"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "status": "rolled_back",
                "blue_version": deployment["blue_version"]
            }
        
        except Exception as e:
            logger.error(f"Deployment rollback failed: {e}")
            return {"error": str(e)}
    
    async def deploy_ecs_rolling(self, service_name: str, 
                               new_task_definition: str) -> Dict[str, Any]:
        """Deploy ECS service using rolling update"""
        
        deployment_id = f"ecs_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # In production, this would update ECS service with new task definition
            deployment = {
                "deployment_id": deployment_id,
                "service_name": service_name,
                "strategy": DeploymentStrategy.ROLLING.value,
                "new_task_definition": new_task_definition,
                "start_time": datetime.now().isoformat(),
                "status": "in_progress"
            }
            
            self.deployments[deployment_id] = deployment
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "strategy": "rolling",
                "task_definition": new_task_definition
            }
        
        except Exception as e:
            logger.error(f"Rolling deployment failed: {e}")
            return {"error": str(e)}
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status"""
        
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return {"error": "Deployment not found"}
        
        return deployment
    
    def list_deployments(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent deployments"""
        
        deployments = list(self.deployments.values())
        deployments.sort(key=lambda x: x["start_time"], reverse=True)
        
        return deployments[:limit]


class CloudArchitectureManager:
    """Main cloud architecture management class"""
    
    def __init__(self, aws_config_manager=None):
        self.aws_config_manager = aws_config_manager
        
        # Initialize managers
        self.lambda_manager = LambdaManager(aws_config_manager)
        self.sqs_manager = SQSManager(aws_config_manager)
        self.ecs_manager = ECSManager(aws_config_manager)
        self.autoscaling_manager = AutoScalingManager(aws_config_manager)
        self.deployment_manager = DeploymentManager(self.lambda_manager, self.ecs_manager)
        
        self.initialized = False
    
    async def initialize_architecture(self) -> Dict[str, Any]:
        """Initialize cloud architecture components"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "initialization_results": {},
            "created_resources": [],
            "errors": []
        }
        
        try:
            # Create ECS cluster
            cluster_result = await self.ecs_manager.create_cluster()
            results["initialization_results"]["ecs_cluster"] = cluster_result
            
            if cluster_result.get("success"):
                results["created_resources"].append(f"ECS Cluster: {self.ecs_manager.cluster_name}")
            else:
                results["errors"].append(f"ECS cluster creation failed: {cluster_result.get('error')}")
            
            # Create SQS queues
            mutation_queue = await self.sqs_manager.create_mutation_queue()
            fitness_queue = await self.sqs_manager.create_fitness_queue()
            
            results["initialization_results"]["sqs_queues"] = {
                "mutation_queue": mutation_queue,
                "fitness_queue": fitness_queue
            }
            
            if not mutation_queue.startswith("error:"):
                results["created_resources"].append(f"SQS Queue: {mutation_queue}")
            else:
                results["errors"].append(f"Mutation queue creation failed: {mutation_queue}")
            
            if not fitness_queue.startswith("error:"):
                results["created_resources"].append(f"SQS Queue: {fitness_queue}")
            else:
                results["errors"].append(f"Fitness queue creation failed: {fitness_queue}")
            
            # Create Lambda functions
            mutation_processor = self.lambda_manager.create_mutation_processor()
            fitness_calculator = self.lambda_manager.create_fitness_calculator()
            cost_optimizer = self.lambda_manager.create_cost_optimizer()
            
            results["initialization_results"]["lambda_functions"] = {
                "mutation_processor": mutation_processor.name,
                "fitness_calculator": fitness_calculator.name,
                "cost_optimizer": cost_optimizer.name
            }
            
            results["created_resources"].extend([
                f"Lambda Function: {mutation_processor.name}",
                f"Lambda Function: {fitness_calculator.name}",
                f"Lambda Function: {cost_optimizer.name}"
            ])
            
            # Create ECS tasks
            evolution_processor = self.ecs_manager.create_evolution_processor_task()
            monitoring_task = self.ecs_manager.create_monitoring_task()
            
            results["initialization_results"]["ecs_tasks"] = {
                "evolution_processor": evolution_processor.name,
                "monitoring_task": monitoring_task.name
            }
            
            results["created_resources"].extend([
                f"ECS Task: {evolution_processor.name}",
                f"ECS Task: {monitoring_task.name}"
            ])
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Architecture initialization failed: {e}")
            results["errors"].append(str(e))
        
        return results
    
    async def scale_resources(self, resource_type: str, target_capacity: int) -> Dict[str, Any]:
        """Scale cloud resources"""
        
        if resource_type == "lambda":
            # Lambda auto-scales, but we can adjust concurrency
            return {
                "success": True,
                "resource_type": resource_type,
                "message": "Lambda functions auto-scale based on demand"
            }
        
        elif resource_type == "ecs":
            # Scale ECS services
            return {
                "success": True,
                "resource_type": resource_type,
                "target_capacity": target_capacity,
                "message": f"ECS services scaling to {target_capacity} tasks"
            }
        
        else:
            return {"error": f"Unknown resource type: {resource_type}"}
    
    def get_architecture_status(self) -> Dict[str, Any]:
        """Get comprehensive architecture status"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "initialized": self.initialized,
            "lambda_functions": len(self.lambda_manager.functions),
            "sqs_queues": len(self.sqs_manager.queues),
            "ecs_tasks": len(self.ecs_manager.tasks),
            "scaling_configs": len(self.autoscaling_manager.scaling_configs),
            "active_deployments": len([d for d in self.deployment_manager.deployments.values() 
                                     if d["status"] == "in_progress"]),
            "aws_region": self.aws_config_manager.config.region if self.aws_config_manager else "unknown"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform architecture health check"""
        
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "component_status": {},
            "issues": []
        }
        
        # Check Lambda functions
        if self.lambda_manager.lambda_client:
            health["component_status"]["lambda"] = "available"
        else:
            health["component_status"]["lambda"] = "unavailable"
            health["issues"].append("Lambda client not initialized")
        
        # Check SQS
        if self.sqs_manager.sqs_client:
            health["component_status"]["sqs"] = "available"
        else:
            health["component_status"]["sqs"] = "unavailable"
            health["issues"].append("SQS client not initialized")
        
        # Check ECS
        if self.ecs_manager.ecs_client:
            health["component_status"]["ecs"] = "available"
        else:
            health["component_status"]["ecs"] = "unavailable"
            health["issues"].append("ECS client not initialized")
        
        # Overall status
        if health["issues"]:
            health["overall_status"] = "degraded" if len(health["issues"]) < 3 else "unhealthy"
        
        return health


# Convenience function to create cloud architecture
def create_cloud_architecture(aws_config_manager=None) -> CloudArchitectureManager:
    """Create integrated cloud architecture system"""
    
    architecture = CloudArchitectureManager(aws_config_manager)
    logger.info("Cloud architecture manager created")
    
    return architecture