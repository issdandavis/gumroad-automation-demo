#!/usr/bin/env python3
"""
App Productizer - CDK App Entry Point
Transforms your Google IDX/Studio apps into sellable products
"""

import aws_cdk as cdk
from constructs import Construct
from stacks.productizer_stack import ProductizerStack

# Configuration for your apps
APP_CONFIG = {
    "ai_workflow_architect": {
        "github_repo": "issdandavis/AI-Workflow-Architect.01.01.02",
        "domain": "ai-workflow.your-domain.com",  # Optional - you can add your domain later
        "price_tier": "enterprise",  # $99-299
        "deployment_type": "fullstack"
    },
    "gumroad_automation": {
        "github_repo": "issdandavis/gumroad-automation-demo", 
        "domain": "gumroad-tools.your-domain.com",  # Optional
        "price_tier": "business",  # $49-99
        "deployment_type": "api"
    },
    "chat_archive": {
        "github_repo": "issdandavis/chat-archive-system",
        "domain": "chat-archive.your-domain.com",  # Optional
        "price_tier": "utility",  # $29-49
        "deployment_type": "webapp"
    }
}

# AI Services Configuration
AI_CONFIG = {
    "perplexity_api_key": "your-perplexity-key",  # For documentation generation
    "notion_token": "your-notion-token",          # For project management
    "zapier_webhook_url": "your-zapier-webhook",  # For workflow automation
    "github_token": "your-github-token"           # For repository access
}

app = cdk.App()

# Deploy productizer infrastructure
ProductizerStack(
    app, 
    "AppProductizer",
    app_config=APP_CONFIG,
    ai_config=AI_CONFIG,
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()