"""
AWS Bedrock Configuration Management
===================================

Configuration management for AWS Bedrock integration with the self-evolving AI framework.
Handles AWS credentials, IAM roles, cost tracking, and service configurations.
"""

import os
import boto3
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BedrockConfig:
    """AWS Bedrock service configuration"""
    region: str = "us-east-1"
    access_key_id: str = ""
    secret_access_key: str = ""
    session_token: str = ""  # For temporary credentials
    role_arn: str = ""  # IAM role for Bedrock access
    
    # Model configurations
    default_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    fallback_models: List[str] = field(default_factory=lambda: [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-premier-v1:0"
    ])
    
    # Cost and performance settings
    max_tokens_per_request: int = 4000
    default_temperature: float = 0.3
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    
    # Cost tracking
    cost_tracking_enabled: bool = True
    daily_budget_usd: float = 100.0
    monthly_budget_usd: float = 2000.0
    cost_alert_threshold: float = 0.8  # Alert at 80% of budget


@dataclass
class CloudStorageConfig:
    """AWS cloud storage configuration"""
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    dynamodb_table_prefix: str = "evolving-ai"
    cloudwatch_namespace: str = "EvolvingAI"
    
    # Data lifecycle
    s3_lifecycle_days_ia: int = 30  # Move to Infrequent Access after 30 days
    s3_lifecycle_days_glacier: int = 90  # Move to Glacier after 90 days
    dynamodb_ttl_days: int = 365  # TTL for DynamoDB items
    
    # Cross-region replication
    enable_cross_region_replication: bool = True
    backup_regions: List[str] = field(default_factory=lambda: ["us-west-2"])


@dataclass
class IAMConfig:
    """IAM configuration for least-privilege access"""
    bedrock_role_name: str = "EvolvingAI-BedrockRole"
    s3_role_name: str = "EvolvingAI-S3Role"
    dynamodb_role_name: str = "EvolvingAI-DynamoDBRole"
    lambda_role_name: str = "EvolvingAI-LambdaRole"
    
    # Policy ARNs
    bedrock_policy_arn: str = ""
    s3_policy_arn: str = ""
    dynamodb_policy_arn: str = ""
    
    # Security settings
    enable_mfa: bool = True
    session_duration_hours: int = 12
    external_id: str = ""  # For cross-account access


@dataclass
class CostTrackingConfig:
    """Cost tracking and optimization configuration"""
    enable_detailed_billing: bool = True
    cost_allocation_tags: Dict[str, str] = field(default_factory=lambda: {
        "Project": "EvolvingAI",
        "Environment": "production",
        "Component": "bedrock-integration"
    })
    
    # Budget alerts
    budget_alert_emails: List[str] = field(default_factory=list)
    cost_anomaly_detection: bool = True
    
    # Optimization settings
    auto_optimize_on_budget_exceed: bool = True
    emergency_shutdown_threshold: float = 1.2  # Shutdown at 120% of budget


@dataclass
class AWSConfig:
    """Complete AWS configuration for Bedrock integration"""
    bedrock: BedrockConfig = field(default_factory=BedrockConfig)
    storage: CloudStorageConfig = field(default_factory=CloudStorageConfig)
    iam: IAMConfig = field(default_factory=IAMConfig)
    cost_tracking: CostTrackingConfig = field(default_factory=CostTrackingConfig)
    
    # Global AWS settings
    profile_name: str = "default"
    use_iam_roles: bool = True
    enable_cloudtrail: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "bedrock": self.bedrock.__dict__,
            "storage": self.storage.__dict__,
            "iam": self.iam.__dict__,
            "cost_tracking": self.cost_tracking.__dict__,
            "profile_name": self.profile_name,
            "use_iam_roles": self.use_iam_roles,
            "enable_cloudtrail": self.enable_cloudtrail
        }


class AWSConfigManager:
    """Manages AWS configuration with validation and credential handling"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = AWSConfig()
        self._session: Optional[boto3.Session] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load AWS configuration from environment and files"""
        # Load from environment variables
        self._load_from_env()
        
        # Load from config file if specified
        if self.config_path and os.path.exists(self.config_path):
            self._load_from_file(self.config_path)
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        env_mappings = {
            # AWS credentials
            "AWS_ACCESS_KEY_ID": ("bedrock", "access_key_id"),
            "AWS_SECRET_ACCESS_KEY": ("bedrock", "secret_access_key"),
            "AWS_SESSION_TOKEN": ("bedrock", "session_token"),
            "AWS_DEFAULT_REGION": ("bedrock", "region"),
            "AWS_PROFILE": ("profile_name",),
            
            # Bedrock specific
            "BEDROCK_REGION": ("bedrock", "region"),
            "BEDROCK_DEFAULT_MODEL": ("bedrock", "default_model"),
            "BEDROCK_DAILY_BUDGET": ("bedrock", "daily_budget_usd"),
            "BEDROCK_MONTHLY_BUDGET": ("bedrock", "monthly_budget_usd"),
            
            # Storage
            "S3_BUCKET": ("storage", "s3_bucket"),
            "S3_REGION": ("storage", "s3_region"),
            "DYNAMODB_TABLE_PREFIX": ("storage", "dynamodb_table_prefix"),
            
            # IAM
            "BEDROCK_ROLE_ARN": ("bedrock", "role_arn"),
        }
        
        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(path, value)
    
    def _load_from_file(self, path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Merge with current config
            if "bedrock" in data:
                for k, v in data["bedrock"].items():
                    if hasattr(self.config.bedrock, k):
                        setattr(self.config.bedrock, k, v)
            
            if "storage" in data:
                for k, v in data["storage"].items():
                    if hasattr(self.config.storage, k):
                        setattr(self.config.storage, k, v)
            
            logger.info(f"Loaded AWS config from {path}")
        except Exception as e:
            logger.error(f"Failed to load AWS config from {path}: {e}")
    
    def _set_nested_value(self, path: tuple, value: str) -> None:
        """Set nested configuration value"""
        if len(path) == 1:
            setattr(self.config, path[0], value)
        elif len(path) == 2:
            section = getattr(self.config, path[0])
            if hasattr(section, path[1]):
                # Convert to appropriate type
                current = getattr(section, path[1])
                if isinstance(current, bool):
                    value = value.lower() in ('true', '1', 'yes')
                elif isinstance(current, int):
                    value = int(value)
                elif isinstance(current, float):
                    value = float(value)
                setattr(section, path[1], value)
    
    def _validate_config(self) -> None:
        """Validate AWS configuration"""
        errors = []
        
        # Check required fields
        if not self.config.bedrock.region:
            errors.append("Bedrock region is required")
        
        # Validate budget settings
        if self.config.bedrock.daily_budget_usd <= 0:
            errors.append("Daily budget must be positive")
        
        if self.config.bedrock.monthly_budget_usd <= 0:
            errors.append("Monthly budget must be positive")
        
        # Check model availability
        if not self.config.bedrock.default_model:
            errors.append("Default Bedrock model is required")
        
        if errors:
            raise ValueError(f"AWS configuration validation failed: {'; '.join(errors)}")
    
    def get_session(self) -> boto3.Session:
        """Get or create AWS session with proper credentials"""
        if self._session is None:
            session_kwargs = {}
            
            # Use profile if specified
            if self.config.profile_name != "default":
                session_kwargs["profile_name"] = self.config.profile_name
            
            # Use explicit credentials if provided
            if self.config.bedrock.access_key_id:
                session_kwargs.update({
                    "aws_access_key_id": self.config.bedrock.access_key_id,
                    "aws_secret_access_key": self.config.bedrock.secret_access_key,
                    "region_name": self.config.bedrock.region
                })
                
                if self.config.bedrock.session_token:
                    session_kwargs["aws_session_token"] = self.config.bedrock.session_token
            
            self._session = boto3.Session(**session_kwargs)
            
            # Test the session
            try:
                sts = self._session.client('sts')
                identity = sts.get_caller_identity()
                logger.info(f"AWS session established for account: {identity.get('Account')}")
            except Exception as e:
                logger.error(f"Failed to establish AWS session: {e}")
                raise
        
        return self._session
    
    def get_bedrock_client(self):
        """Get Bedrock runtime client"""
        session = self.get_session()
        
        if self.config.bedrock.role_arn:
            # Assume role for Bedrock access
            sts = session.client('sts')
            assumed_role = sts.assume_role(
                RoleArn=self.config.bedrock.role_arn,
                RoleSessionName=f"EvolvingAI-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            
            credentials = assumed_role['Credentials']
            return boto3.client(
                'bedrock-runtime',
                region_name=self.config.bedrock.region,
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
        else:
            return session.client('bedrock-runtime', region_name=self.config.bedrock.region)
    
    def get_s3_client(self):
        """Get S3 client"""
        session = self.get_session()
        return session.client('s3', region_name=self.config.storage.s3_region)
    
    def get_dynamodb_resource(self):
        """Get DynamoDB resource"""
        session = self.get_session()
        return session.resource('dynamodb', region_name=self.config.storage.s3_region)
    
    def get_cloudwatch_client(self):
        """Get CloudWatch client"""
        session = self.get_session()
        return session.client('cloudwatch', region_name=self.config.bedrock.region)
    
    def test_connectivity(self) -> Dict[str, bool]:
        """Test connectivity to all AWS services"""
        results = {}
        
        try:
            # Test Bedrock
            bedrock = self.get_bedrock_client()
            # Note: Bedrock doesn't have a simple list operation, so we'll test with STS
            results["bedrock"] = True
        except Exception as e:
            logger.error(f"Bedrock connectivity test failed: {e}")
            results["bedrock"] = False
        
        try:
            # Test S3
            s3 = self.get_s3_client()
            s3.list_buckets()
            results["s3"] = True
        except Exception as e:
            logger.error(f"S3 connectivity test failed: {e}")
            results["s3"] = False
        
        try:
            # Test DynamoDB
            dynamodb = self.get_dynamodb_resource()
            list(dynamodb.tables.all())
            results["dynamodb"] = True
        except Exception as e:
            logger.error(f"DynamoDB connectivity test failed: {e}")
            results["dynamodb"] = False
        
        try:
            # Test CloudWatch
            cloudwatch = self.get_cloudwatch_client()
            cloudwatch.list_metrics(MaxRecords=1)
            results["cloudwatch"] = True
        except Exception as e:
            logger.error(f"CloudWatch connectivity test failed: {e}")
            results["cloudwatch"] = False
        
        return results
    
    def save_config(self, path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = path or self.config_path or "aws_config.json"
        
        with open(save_path, 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        
        logger.info(f"AWS configuration saved to {save_path}")


def create_iam_policies() -> Dict[str, Dict[str, Any]]:
    """Create IAM policies for least-privilege access"""
    
    bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/anthropic.claude*",
                    "arn:aws:bedrock:*::foundation-model/amazon.titan*",
                    "arn:aws:bedrock:*::foundation-model/ai21.j2*"
                ]
            }
        ]
    }
    
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::evolving-ai-*",
                    "arn:aws:s3:::evolving-ai-*/*"
                ]
            }
        ]
    }
    
    dynamodb_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/evolving-ai-*"
            }
        ]
    }
    
    cloudwatch_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "cloudwatch:PutMetricData",
                    "cloudwatch:GetMetricStatistics",
                    "cloudwatch:ListMetrics"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "cloudwatch:namespace": "EvolvingAI"
                    }
                }
            }
        ]
    }
    
    return {
        "bedrock": bedrock_policy,
        "s3": s3_policy,
        "dynamodb": dynamodb_policy,
        "cloudwatch": cloudwatch_policy
    }