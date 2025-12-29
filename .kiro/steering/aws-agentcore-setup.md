---
inclusion: manual
---

# AWS AgentCore MCP Server Setup Guide

## Issue Resolution

The "MCP error -32000: Connection closed" for the AWS AgentCore server occurs because it requires proper AWS credentials and configuration to connect to Amazon Bedrock services.

## Quick Fix

### Step 1: Configure AWS Credentials

You need to set up AWS credentials. Choose one of these methods:

**Option A: Environment Variables**
```bash
# Add these to your environment
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

**Option B: AWS Profile**
```bash
# Configure AWS CLI profile
aws configure --profile agentcore
# Enter your credentials when prompted
```

### Step 2: Update MCP Configuration

The current configuration needs environment variables. Here's the corrected version:

```json
{
  "power-aws-agentcore-agentcore-mcp-server": {
    "command": "uvx",
    "args": [
      "awslabs.amazon-bedrock-agentcore-mcp-server@latest"
    ],
    "env": {
      "AWS_REGION": "us-east-1",
      "AWS_PROFILE": "default",
      "FASTMCP_LOG_LEVEL": "ERROR"
    },
    "disabled": false,
    "timeout": 120000
  }
}
```

### Step 3: Verify Prerequisites

**Check if uvx is installed:**
```bash
uvx --version
```

**If not installed, install uv first:**
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# Or via pip
pip install uv
```

### Step 4: Test the Connection

After configuring credentials, restart Kiro or reconnect the MCP server from the MCP Server view in the Kiro feature panel.

## Alternative: Disable the Server Temporarily

If you don't need AWS AgentCore right now, you can disable it:

```json
{
  "power-aws-agentcore-agentcore-mcp-server": {
    "command": "uvx",
    "args": [
      "awslabs.amazon-bedrock-agentcore-mcp-server@latest"
    ],
    "disabled": true
  }
}
```

## What AWS AgentCore Provides

Once properly configured, AWS AgentCore gives you:

- **Agent Development**: Build and deploy AI agents on AWS Bedrock
- **Multi-Model Support**: Access to Claude, Titan, Jurassic, and other Bedrock models
- **Agent Orchestration**: Coordinate multiple AI agents
- **Knowledge Bases**: Integration with Bedrock Knowledge Bases
- **Function Calling**: Custom tool integration for agents

## Required AWS Permissions

Your AWS credentials need these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "bedrock-agent:*",
        "bedrock-runtime:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

**Error: "uvx command not found"**
- Install uv: `pip install uv`
- Restart your terminal

**Error: "AWS credentials not found"**
- Set environment variables or configure AWS CLI
- Verify with: `aws sts get-caller-identity`

**Error: "Access denied"**
- Check your AWS permissions
- Ensure Bedrock is available in your region

**Connection still fails**
- Check your internet connection
- Verify AWS region is correct
- Try increasing timeout in MCP config

The Figma power we set up earlier should still work fine - this is a separate MCP server issue.