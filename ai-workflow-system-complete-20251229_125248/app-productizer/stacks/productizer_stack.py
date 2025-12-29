"""
ProductizerStack - Main CDK stack for app productization
Transforms your apps into professional, sellable products
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    Duration,
    RemovalPolicy
)
from constructs import Construct
from typing import Dict, Any

class ProductizerStack(Stack):
    """
    Main stack for productizing your apps
    """
    
    def __init__(self, scope: Construct, construct_id: str, 
                 app_config: Dict[str, Any], ai_config: Dict[str, Any], **props) -> None:
        super().__init__(scope, construct_id, **props)
        
        self.app_config = app_config
        self.ai_config = ai_config
        
        # Core infrastructure
        self._create_storage()
        self._create_ai_services()
        self._create_quality_gates()
        self._create_deployment_pipeline()
        self._create_monitoring()
        self._create_gumroad_integration()
        
    def _create_storage(self) -> None:
        """Create storage for apps, docs, and assets"""
        
        # S3 bucket for app deployments
        self.app_bucket = s3.Bucket(
            self, "AppDeploymentBucket",
            bucket_name=f"app-productizer-{self.account}-{self.region}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )
        
        # S3 bucket for generated documentation and assets
        self.docs_bucket = s3.Bucket(
            self, "DocumentationBucket", 
            bucket_name=f"app-docs-{self.account}-{self.region}",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            public_read_access=True,
            website_index_document="index.html"
        )
        
        # DynamoDB table for tracking app status and metrics
        self.app_table = dynamodb.Table(
            self, "AppStatusTable",
            table_name="app-productizer-status",
            partition_key=dynamodb.Attribute(
                name="app_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )
        
    def _create_ai_services(self) -> None:
        """Create Lambda functions for AI-powered services"""
        
        # Documentation generator using Perplexity
        self.doc_generator = _lambda.Function(
            self, "DocumentationGenerator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="doc_generator.handler",
            code=_lambda.Code.from_asset("lambda/doc_generator"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "PERPLEXITY_API_KEY": self.ai_config.get("perplexity_api_key", ""),
                "NOTION_TOKEN": self.ai_config.get("notion_token", ""),
                "DOCS_BUCKET": self.docs_bucket.bucket_name,
                "APP_TABLE": self.app_table.table_name
            }
        )
        
        # Quality assurance checker
        self.qa_checker = _lambda.Function(
            self, "QualityAssuranceChecker",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="qa_checker.handler", 
            code=_lambda.Code.from_asset("lambda/qa_checker"),
            timeout=Duration.minutes(10),
            memory_size=2048,
            environment={
                "APP_BUCKET": self.app_bucket.bucket_name,
                "APP_TABLE": self.app_table.table_name,
                "GITHUB_TOKEN": self.ai_config.get("github_token", "")
            }
        )
        
        # Zapier integration webhook
        self.zapier_webhook = _lambda.Function(
            self, "ZapierWebhook",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="zapier_webhook.handler",
            code=_lambda.Code.from_asset("lambda/zapier_webhook"),
            timeout=Duration.minutes(2),
            memory_size=512,
            environment={
                "ZAPIER_WEBHOOK_URL": self.ai_config.get("zapier_webhook_url", ""),
                "APP_TABLE": self.app_table.table_name
            }
        )
        
        # Grant permissions
        self.docs_bucket.grant_read_write(self.doc_generator)
        self.app_bucket.grant_read_write(self.qa_checker)
        self.app_table.grant_read_write_data(self.doc_generator)
        self.app_table.grant_read_write_data(self.qa_checker)
        self.app_table.grant_read_write_data(self.zapier_webhook)
        
    def _create_quality_gates(self) -> None:
        """Create automated testing and validation"""
        
        # CodeBuild project for testing
        self.test_project = codebuild.Project(
            self, "AppTestProject",
            project_name="app-productizer-tests",
            source=codebuild.Source.git_hub(
                owner="your-username",  # Replace with your GitHub username
                repo="your-repo",       # Will be configured per app
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(
                        codebuild.EventAction.PUSH,
                        codebuild.EventAction.PULL_REQUEST_CREATED,
                        codebuild.EventAction.PULL_REQUEST_UPDATED
                    )
                ]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {
                            "python": "3.11",
                            "nodejs": "18"
                        },
                        "commands": [
                            "pip install -r requirements.txt || echo 'No Python requirements'",
                            "npm install || echo 'No Node.js dependencies'"
                        ]
                    },
                    "pre_build": {
                        "commands": [
                            "echo Running quality checks...",
                            "python -m pytest tests/ || echo 'No Python tests'",
                            "npm test || echo 'No Node.js tests'",
                            "npm run build || echo 'No build script'"
                        ]
                    },
                    "build": {
                        "commands": [
                            "echo Packaging application...",
                            "zip -r app-package.zip . -x '*.git*' 'node_modules/*' '__pycache__/*'",
                            f"aws s3 cp app-package.zip s3://{self.app_bucket.bucket_name}/$CODEBUILD_BUILD_ID/"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "echo Build completed on `date`",
                            f"aws lambda invoke --function-name {self.qa_checker.function_name} --payload '{{\"build_id\": \"$CODEBUILD_BUILD_ID\"}}' response.json"
                        ]
                    }
                }
            })
        )
        
        # Grant CodeBuild permissions
        self.app_bucket.grant_read_write(self.test_project)
        self.qa_checker.grant_invoke(self.test_project)
        
    def _create_deployment_pipeline(self) -> None:
        """Create deployment pipeline for each app"""
        
        # SNS topic for deployment notifications
        self.deployment_topic = sns.Topic(
            self, "DeploymentNotifications",
            topic_name="app-productizer-deployments"
        )
        
        # Create API Gateway for webhook endpoints
        self.api = apigw.RestApi(
            self, "ProductizerAPI",
            rest_api_name="App Productizer API",
            description="API for app productization workflow",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Zapier webhook endpoint
        zapier_integration = apigw.LambdaIntegration(self.zapier_webhook)
        self.api.root.add_resource("zapier").add_method("POST", zapier_integration)
        
        # Documentation generation endpoint
        docs_integration = apigw.LambdaIntegration(self.doc_generator)
        self.api.root.add_resource("generate-docs").add_method("POST", docs_integration)
        
        # QA check endpoint
        qa_integration = apigw.LambdaIntegration(self.qa_checker)
        self.api.root.add_resource("quality-check").add_method("POST", qa_integration)
        
    def _create_monitoring(self) -> None:
        """Create monitoring and alerting"""
        
        # EventBridge rule for failed builds
        build_failure_rule = events.Rule(
            self, "BuildFailureRule",
            event_pattern=events.EventPattern(
                source=["aws.codebuild"],
                detail_type=["CodeBuild Build State Change"],
                detail={
                    "build-status": ["FAILED", "FAULT", "STOPPED", "TIMED_OUT"]
                }
            )
        )
        
        # Send notifications to SNS
        build_failure_rule.add_target(targets.SnsTopic(self.deployment_topic))
        
        # Lambda function for Slack/Discord notifications (optional)
        self.notification_handler = _lambda.Function(
            self, "NotificationHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="notifications.handler",
            code=_lambda.Code.from_asset("lambda/notifications"),
            timeout=Duration.minutes(1),
            memory_size=256,
            environment={
                "ZAPIER_WEBHOOK_URL": self.ai_config.get("zapier_webhook_url", "")
            }
        )
        
        # Subscribe notification handler to SNS topic
        self.deployment_topic.add_subscription(
            subs.LambdaSubscription(self.notification_handler)
        )
        
    def _create_gumroad_integration(self) -> None:
        """Create Gumroad product integration"""
        
        # Lambda for Gumroad product creation and management
        self.gumroad_manager = _lambda.Function(
            self, "GumroadManager",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="gumroad_manager.handler",
            code=_lambda.Code.from_asset("lambda/gumroad_manager"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "APP_BUCKET": self.app_bucket.bucket_name,
                "DOCS_BUCKET": self.docs_bucket.bucket_name,
                "APP_TABLE": self.app_table.table_name,
                "ZAPIER_WEBHOOK_URL": self.ai_config.get("zapier_webhook_url", "")
            }
        )
        
        # Grant permissions
        self.app_bucket.grant_read(self.gumroad_manager)
        self.docs_bucket.grant_read(self.gumroad_manager)
        self.app_table.grant_read_write_data(self.gumroad_manager)
        
        # Add Gumroad endpoint to API
        gumroad_integration = apigw.LambdaIntegration(self.gumroad_manager)
        gumroad_resource = self.api.root.add_resource("gumroad")
        gumroad_resource.add_method("POST", gumroad_integration)  # Create product
        gumroad_resource.add_method("GET", gumroad_integration)   # Get product status
        
        # EventBridge rule for successful deployments -> Gumroad update
        deployment_success_rule = events.Rule(
            self, "DeploymentSuccessRule",
            event_pattern=events.EventPattern(
                source=["aws.codebuild"],
                detail_type=["CodeBuild Build State Change"],
                detail={
                    "build-status": ["SUCCEEDED"]
                }
            )
        )
        
        deployment_success_rule.add_target(targets.LambdaFunction(self.gumroad_manager))
        
        # Output important values
        cdk.CfnOutput(
            self, "APIEndpoint",
            value=self.api.url,
            description="API Gateway endpoint for webhooks"
        )
        
        cdk.CfnOutput(
            self, "AppBucket",
            value=self.app_bucket.bucket_name,
            description="S3 bucket for app deployments"
        )
        
        cdk.CfnOutput(
            self, "DocsBucket", 
            value=self.docs_bucket.bucket_name,
            description="S3 bucket for documentation"
        )