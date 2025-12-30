"""
Cloud DNA Store - AWS-Native Evolution Data Storage
==================================================

AWS-native storage system for evolution data with intelligent tiering,
cross-region replication, and real-time metrics streaming.
"""

import json
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import boto3
from botocore.exceptions import ClientError, BotoCoreError

from .models import SystemDNA, MutationRecord, FitnessScore, OperationResult
from .aws_config import AWSConfigManager

logger = logging.getLogger(__name__)


@dataclass
class EvolutionEvent:
    """Evolution event for storage"""
    id: str
    timestamp: datetime
    type: str  # "mutation_applied", "fitness_calculated", "rollback", etc.
    generation: int
    fitness_delta: float
    mutation_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0-1.0 for storage tiering
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "generation": self.generation,
            "fitness_delta": self.fitness_delta,
            "mutation_id": self.mutation_id,
            "data": self.data,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvolutionEvent":
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            type=data["type"],
            generation=data["generation"],
            fitness_delta=data["fitness_delta"],
            mutation_id=data.get("mutation_id"),
            data=data.get("data", {}),
            importance=data.get("importance", 0.5)
        )


@dataclass
class StorageResult:
    """Result of storage operation"""
    s3_success: bool
    dynamodb_success: bool
    storage_location: str
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.s3_success and self.dynamodb_success


@dataclass
class SnapshotResult:
    """Result of snapshot operation"""
    success: bool
    snapshot_id: str
    storage_location: str
    error: Optional[str] = None


@dataclass
class EvolutionQuery:
    """Query parameters for evolution history"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: List[str] = field(default_factory=list)
    generation_range: Optional[Tuple[int, int]] = None
    limit: int = 100
    
    @property
    def time_range(self) -> timedelta:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return timedelta(days=30)  # Default


class CloudDNAStore:
    """
    AWS-native storage for evolution data with:
    - S3 for detailed event storage with lifecycle policies
    - DynamoDB for fast metadata queries
    - CloudWatch for real-time metrics
    - Cross-region replication for disaster recovery
    """
    
    def __init__(self, aws_config: AWSConfigManager):
        self.aws_config = aws_config
        self.config = aws_config.config.storage
        
        # Initialize AWS clients
        self.s3 = aws_config.get_s3_client()
        self.dynamodb = aws_config.get_dynamodb_resource()
        self.cloudwatch = aws_config.get_cloudwatch_client()
        
        # Table and bucket names
        self.evolution_bucket = self.config.s3_bucket or "evolving-ai-evolution-data"
        self.snapshots_table_name = f"{self.config.dynamodb_table_prefix}-snapshots"
        self.events_table_name = f"{self.config.dynamodb_table_prefix}-events"
        self.metrics_namespace = self.config.cloudwatch_namespace
        
        # Initialize resources
        self._ensure_resources_exist()
    
    def _ensure_resources_exist(self) -> None:
        """Ensure S3 bucket and DynamoDB tables exist"""
        try:
            # Create S3 bucket if it doesn't exist
            try:
                self.s3.head_bucket(Bucket=self.evolution_bucket)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    self._create_s3_bucket()
                else:
                    raise
            
            # Create DynamoDB tables if they don't exist
            self._ensure_dynamodb_tables()
            
            logger.info("Cloud DNA Store resources verified")
            
        except Exception as e:
            logger.error(f"Failed to ensure resources exist: {e}")
            raise
    
    def _create_s3_bucket(self) -> None:
        """Create S3 bucket with lifecycle policies"""
        try:
            # Create bucket
            if self.config.s3_region == 'us-east-1':
                self.s3.create_bucket(Bucket=self.evolution_bucket)
            else:
                self.s3.create_bucket(
                    Bucket=self.evolution_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.config.s3_region}
                )
            
            # Set up lifecycle policy
            lifecycle_policy = {
                'Rules': [
                    {
                        'ID': 'EvolutionDataLifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'evolution-events/'},
                        'Transitions': [
                            {
                                'Days': self.config.s3_lifecycle_days_ia,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': self.config.s3_lifecycle_days_glacier,
                                'StorageClass': 'GLACIER'
                            }
                        ]
                    }
                ]
            }
            
            self.s3.put_bucket_lifecycle_configuration(
                Bucket=self.evolution_bucket,
                LifecycleConfiguration=lifecycle_policy
            )
            
            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=self.evolution_bucket,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            logger.info(f"Created S3 bucket: {self.evolution_bucket}")
            
        except Exception as e:
            logger.error(f"Failed to create S3 bucket: {e}")
            raise
    
    def _ensure_dynamodb_tables(self) -> None:
        """Ensure DynamoDB tables exist with proper schema"""
        
        # Snapshots table
        try:
            self.snapshots_table = self.dynamodb.Table(self.snapshots_table_name)
            self.snapshots_table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_snapshots_table()
            else:
                raise
        
        # Events table
        try:
            self.events_table = self.dynamodb.Table(self.events_table_name)
            self.events_table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self._create_events_table()
            else:
                raise
    
    def _create_snapshots_table(self) -> None:
        """Create DynamoDB snapshots table"""
        
        table = self.dynamodb.create_table(
            TableName=self.snapshots_table_name,
            KeySchema=[
                {'AttributeName': 'snapshot_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'snapshot_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'generation', 'AttributeType': 'N'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'timestamp', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'generation-index',
                    'KeySchema': [
                        {'AttributeName': 'generation', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        self.snapshots_table = table
        
        logger.info(f"Created DynamoDB snapshots table: {self.snapshots_table_name}")
    
    def _create_events_table(self) -> None:
        """Create DynamoDB events table"""
        
        table = self.dynamodb.create_table(
            TableName=self.events_table_name,
            KeySchema=[
                {'AttributeName': 'event_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'event_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'event_type', 'AttributeType': 'S'},
                {'AttributeName': 'generation', 'AttributeType': 'N'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'timestamp', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'type-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'event_type', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        self.events_table = table
        
        logger.info(f"Created DynamoDB events table: {self.events_table_name}")
    
    async def store_evolution_event(self, event: EvolutionEvent) -> StorageResult:
        """Store evolution event with intelligent tiering"""
        
        try:
            # Store detailed data in S3 with lifecycle policies
            s3_key = f"evolution-events/{event.timestamp.year}/{event.timestamp.month:02d}/{event.id}.json"
            
            s3_result = await self._store_to_s3(
                bucket=self.evolution_bucket,
                key=s3_key,
                data=event.to_dict(),
                storage_class='STANDARD_IA' if event.importance < 0.5 else 'STANDARD'
            )
            
            # Store metadata in DynamoDB for fast queries
            dynamo_result = await self._store_event_metadata(event, s3_key)
            
            # Stream metrics to CloudWatch
            await self._send_event_metrics(event)
            
            return StorageResult(
                s3_success=s3_result,
                dynamodb_success=dynamo_result,
                storage_location=s3_key
            )
            
        except Exception as e:
            logger.error(f"Failed to store evolution event: {e}")
            return StorageResult(
                s3_success=False,
                dynamodb_success=False,
                storage_location="",
                error=str(e)
            )
    
    async def _store_to_s3(self, bucket: str, key: str, data: Dict[str, Any], 
                          storage_class: str = 'STANDARD') -> bool:
        """Store data to S3 with specified storage class"""
        try:
            self.s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data, indent=2, default=str),
                ContentType='application/json',
                StorageClass=storage_class,
                Metadata={
                    'evolution-system': 'bedrock-ai-evolution',
                    'storage-class': storage_class,
                    'created': datetime.now().isoformat()
                }
            )
            return True
        except Exception as e:
            logger.error(f"S3 storage failed: {e}")
            return False
    
    async def _store_event_metadata(self, event: EvolutionEvent, s3_location: str) -> bool:
        """Store event metadata in DynamoDB"""
        try:
            # Calculate TTL (optional cleanup)
            ttl = int((datetime.now() + timedelta(days=self.config.dynamodb_ttl_days)).timestamp())
            
            self.events_table.put_item(
                Item={
                    'event_id': event.id,
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.type,
                    'generation': event.generation,
                    'fitness_delta': event.fitness_delta,
                    'mutation_id': event.mutation_id or '',
                    's3_location': s3_location,
                    'importance': event.importance,
                    'ttl': ttl
                }
            )
            return True
        except Exception as e:
            logger.error(f"DynamoDB event storage failed: {e}")
            return False
    
    async def _send_event_metrics(self, event: EvolutionEvent) -> None:
        """Send event metrics to CloudWatch"""
        try:
            metrics = [
                {
                    'MetricName': 'EvolutionEvents',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'EventType', 'Value': event.type},
                        {'Name': 'Generation', 'Value': str(event.generation)}
                    ]
                },
                {
                    'MetricName': 'FitnessDelta',
                    'Value': event.fitness_delta,
                    'Unit': 'None',
                    'Dimensions': [
                        {'Name': 'EventType', 'Value': event.type}
                    ]
                }
            ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.metrics_namespace,
                MetricData=metrics
            )
            
        except Exception as e:
            logger.error(f"CloudWatch metrics failed: {e}")
    
    async def create_snapshot(self, dna: SystemDNA, metadata: Dict[str, Any]) -> SnapshotResult:
        """Create versioned snapshot with cross-region replication"""
        
        snapshot_id = f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Store in DynamoDB for fast access
            snapshot_item = {
                'snapshot_id': snapshot_id,
                'timestamp': datetime.now().isoformat(),
                'generation': dna.generation,
                'fitness_score': dna.fitness_score,
                'dna_data': dna.to_dict(),
                'metadata': metadata,
                'checksum': dna.get_checksum(),
                'ttl': int((datetime.now() + timedelta(days=90)).timestamp())
            }
            
            # Store with conditional write to prevent duplicates
            self.snapshots_table.put_item(
                Item=snapshot_item,
                ConditionExpression='attribute_not_exists(snapshot_id)'
            )
            
            # Replicate to backup regions if enabled
            if self.config.enable_cross_region_replication:
                await self._replicate_snapshot(snapshot_item)
            
            # Send snapshot metrics
            await self._send_snapshot_metrics(dna)
            
            return SnapshotResult(
                success=True,
                snapshot_id=snapshot_id,
                storage_location=f"dynamodb://{self.snapshots_table_name}/{snapshot_id}"
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return SnapshotResult(
                    success=False,
                    snapshot_id=snapshot_id,
                    storage_location="",
                    error="Snapshot already exists"
                )
            else:
                logger.error(f"Snapshot creation failed: {e}")
                return SnapshotResult(
                    success=False,
                    snapshot_id=snapshot_id,
                    storage_location="",
                    error=str(e)
                )
        except Exception as e:
            logger.error(f"Snapshot creation failed: {e}")
            return SnapshotResult(
                success=False,
                snapshot_id=snapshot_id,
                storage_location="",
                error=str(e)
            )
    
    async def _replicate_snapshot(self, snapshot_item: Dict[str, Any]) -> None:
        """Replicate snapshot to backup regions"""
        for region in self.config.backup_regions:
            try:
                # Create DynamoDB resource for backup region
                backup_dynamodb = boto3.resource('dynamodb', region_name=region)
                backup_table = backup_dynamodb.Table(self.snapshots_table_name)
                
                # Store snapshot in backup region
                backup_table.put_item(Item=snapshot_item)
                
                logger.info(f"Snapshot replicated to region: {region}")
                
            except Exception as e:
                logger.error(f"Snapshot replication to {region} failed: {e}")
    
    async def _send_snapshot_metrics(self, dna: SystemDNA) -> None:
        """Send snapshot metrics to CloudWatch"""
        try:
            metrics = [
                {
                    'MetricName': 'Snapshots',
                    'Value': 1,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'SystemGeneration',
                    'Value': dna.generation,
                    'Unit': 'Count'
                },
                {
                    'MetricName': 'FitnessScore',
                    'Value': dna.fitness_score,
                    'Unit': 'None'
                }
            ]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.metrics_namespace,
                MetricData=metrics
            )
            
        except Exception as e:
            logger.error(f"Snapshot metrics failed: {e}")
    
    async def get_evolution_event(self, event_id: str) -> Optional[EvolutionEvent]:
        """Retrieve evolution event by ID"""
        try:
            # First try DynamoDB for metadata
            response = self.events_table.get_item(Key={'event_id': event_id})
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            s3_location = item.get('s3_location')
            
            if s3_location:
                # Get full data from S3
                s3_response = self.s3.get_object(
                    Bucket=self.evolution_bucket,
                    Key=s3_location
                )
                event_data = json.loads(s3_response['Body'].read())
                return EvolutionEvent.from_dict(event_data)
            else:
                # Reconstruct from DynamoDB metadata
                return EvolutionEvent(
                    id=item['event_id'],
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    type=item['event_type'],
                    generation=int(item['generation']),
                    fitness_delta=float(item['fitness_delta']),
                    mutation_id=item.get('mutation_id') or None,
                    importance=float(item.get('importance', 0.5))
                )
                
        except Exception as e:
            logger.error(f"Failed to retrieve event {event_id}: {e}")
            return None
    
    async def query_evolution_history(self, query: EvolutionQuery) -> List[EvolutionEvent]:
        """Query evolution history with intelligent caching"""
        
        try:
            # Use DynamoDB for recent data (last 30 days)
            if query.time_range.days <= 30:
                return await self._query_dynamodb(query)
            else:
                # Use S3 Select for historical data
                return await self._query_s3_select(query)
                
        except Exception as e:
            logger.error(f"Evolution history query failed: {e}")
            return []
    
    async def _query_dynamodb(self, query: EvolutionQuery) -> List[EvolutionEvent]:
        """Query recent evolution history from DynamoDB"""
        
        events = []
        
        try:
            # Build query parameters
            if query.event_types:
                # Query by event type
                for event_type in query.event_types:
                    response = self.events_table.query(
                        IndexName='type-timestamp-index',
                        KeyConditionExpression='event_type = :event_type',
                        ExpressionAttributeValues={':event_type': event_type},
                        Limit=query.limit,
                        ScanIndexForward=False  # Most recent first
                    )
                    
                    for item in response.get('Items', []):
                        event = EvolutionEvent(
                            id=item['event_id'],
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            type=item['event_type'],
                            generation=int(item['generation']),
                            fitness_delta=float(item['fitness_delta']),
                            mutation_id=item.get('mutation_id') or None,
                            importance=float(item.get('importance', 0.5))
                        )
                        events.append(event)
            else:
                # Scan all events (limited)
                response = self.events_table.scan(
                    Limit=query.limit,
                    FilterExpression='attribute_exists(event_id)'
                )
                
                for item in response.get('Items', []):
                    event = EvolutionEvent(
                        id=item['event_id'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        type=item['event_type'],
                        generation=int(item['generation']),
                        fitness_delta=float(item['fitness_delta']),
                        mutation_id=item.get('mutation_id') or None,
                        importance=float(item.get('importance', 0.5))
                    )
                    events.append(event)
            
            # Sort by timestamp (most recent first)
            events.sort(key=lambda e: e.timestamp, reverse=True)
            
            return events[:query.limit]
            
        except Exception as e:
            logger.error(f"DynamoDB query failed: {e}")
            return []
    
    async def _query_s3_select(self, query: EvolutionQuery) -> List[EvolutionEvent]:
        """Query historical evolution data using S3 Select"""
        
        # This would use S3 Select for efficient querying of historical JSON data
        # For now, return empty list as S3 Select requires more complex setup
        logger.info("S3 Select query not implemented yet, returning empty results")
        return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        
        stats = {
            "s3_bucket": self.evolution_bucket,
            "dynamodb_tables": {
                "snapshots": self.snapshots_table_name,
                "events": self.events_table_name
            },
            "cloudwatch_namespace": self.metrics_namespace,
            "cross_region_replication": self.config.enable_cross_region_replication,
            "backup_regions": self.config.backup_regions
        }
        
        try:
            # Get DynamoDB table stats
            snapshots_desc = self.snapshots_table.describe()
            events_desc = self.events_table.describe()
            
            stats["table_stats"] = {
                "snapshots_item_count": snapshots_desc.get('Table', {}).get('ItemCount', 0),
                "events_item_count": events_desc.get('Table', {}).get('ItemCount', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            stats["table_stats"] = {"error": str(e)}
        
        return stats
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Clean up old evolution data beyond retention period"""
        
        cleanup_results = {
            "snapshots_deleted": 0,
            "events_deleted": 0,
            "errors": []
        }
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            # Clean up old snapshots
            response = self.snapshots_table.scan(
                FilterExpression='#ts < :cutoff',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={':cutoff': cutoff_date.isoformat()}
            )
            
            for item in response.get('Items', []):
                try:
                    self.snapshots_table.delete_item(
                        Key={'snapshot_id': item['snapshot_id']}
                    )
                    cleanup_results["snapshots_deleted"] += 1
                except Exception as e:
                    cleanup_results["errors"].append(f"Snapshot deletion failed: {e}")
            
            logger.info(f"Cleaned up {cleanup_results['snapshots_deleted']} old snapshots")
            
        except Exception as e:
            cleanup_results["errors"].append(f"Snapshot cleanup failed: {e}")
        
        return cleanup_results