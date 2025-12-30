# AgentCore Demo - Deployment Guide

Complete step-by-step guide for deploying your AgentCore agent to AWS.

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites Check
```bash
# Verify Python version
python --version  # Should be 3.10+

# Check AWS CLI
aws --version
aws sts get-caller-identity  # Verify AWS access

# Verify AgentCore installation
agentcore --version
```

### 2. One-Command Deployment
```bash
# Navigate to project directory
cd agentcore_demo

# Deploy to AWS (this handles everything)
agentcore deploy
```

### 3. Test Your Deployed Agent
```bash
# Test the deployed agent
agentcore invoke "Hello, AgentCore!"

# Check deployment status
agentcore status
```

## 📋 Detailed Setup

### AWS Prerequisites

1. **AWS Account Setup**
   - Active AWS account with billing enabled
   - AWS CLI installed and configured
   - Appropriate IAM permissions

2. **Required AWS Permissions**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:*",
           "iam:CreateRole",
           "iam:AttachRolePolicy",
           "iam:PassRole",
           "ecr:*",
           "codebuild:*",
           "lambda:*",
           "logs:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Bedrock Model Access**
   - Enable Claude Sonnet in AWS Bedrock console
   - Request model access if needed (can take 24-48 hours)

### Environment Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Test Locally First**
   ```bash
   python agent.py
   ```

## 🔧 Configuration Options

### Memory Configuration
```yaml
# In .bedrock_agentcore.yaml
memory:
  mode: STM_ONLY          # Short-term memory only
  # mode: STM_AND_LTM     # Both short and long-term
  # mode: NO_MEMORY       # No memory
```

### Network Configuration
```yaml
# Public deployment (default)
network_configuration:
  network_mode: PUBLIC

# VPC deployment (for private resources)
network_configuration:
  network_mode: VPC
  vpc_config:
    subnets: ["subnet-12345", "subnet-67890"]
    security_groups: ["sg-abcdef"]
```

### Runtime Configuration
```yaml
# Container deployment (recommended)
deployment_type: container
platform: linux/arm64

# Direct code deployment (faster cold starts)
deployment_type: direct_code_deploy
runtime_type: PYTHON_3_11
```

## 🚀 Deployment Commands

### Basic Deployment
```bash
# Configure agent
agentcore configure --entrypoint agent.py

# Deploy to AWS
agentcore deploy

# Test deployment
agentcore invoke "test message"
```

### Advanced Deployment
```bash
# Deploy with custom settings
agentcore configure \
  --entrypoint agent.py \
  --name my-production-agent \
  --region us-east-1 \
  --deployment-type container

# Deploy with memory enabled
agentcore configure \
  --entrypoint agent.py \
  --memory-mode STM_AND_LTM

# Deploy in VPC
agentcore configure \
  --entrypoint agent.py \
  --vpc \
  --subnets subnet-123,subnet-456 \
  --security-groups sg-789
```

## 📊 Monitoring & Observability

### Built-in Monitoring
AgentCore provides automatic monitoring:
- Request/response traces
- Performance metrics
- Error logging
- Cost tracking

### CloudWatch Integration
```bash
# View logs
aws logs describe-log-groups --log-group-name-prefix /aws/bedrock/agentcore

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/BedrockAgentCore \
  --metric-name Invocations \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-01T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### Custom Monitoring
Add custom metrics to your agent:
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_custom_metric(metric_name, value):
    cloudwatch.put_metric_data(
        Namespace='AgentCore/Custom',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': 'Count'
            }
        ]
    )
```

## 💰 Cost Optimization

### Understanding Costs
- **Compute**: Pay per request (serverless)
- **Memory**: Storage costs for conversation history
- **Observability**: CloudWatch logs and metrics
- **Network**: Data transfer (minimal for most use cases)

### Cost Optimization Tips
```bash
# Set session timeouts
agentcore configure --idle-timeout 300 --max-lifetime 3600

# Use memory efficiently
agentcore configure --memory-mode STM_ONLY

# Monitor costs
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🔒 Security Best Practices

### IAM Configuration
```bash
# Create dedicated execution role
aws iam create-role \
  --role-name AgentCoreExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# Attach minimal permissions
aws iam attach-role-policy \
  --role-name AgentCoreExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### Network Security
```bash
# Deploy in private VPC
agentcore configure \
  --vpc \
  --subnets subnet-private1,subnet-private2 \
  --security-groups sg-restrictive
```

### Data Protection
- All data encrypted in transit and at rest
- Memory data automatically encrypted
- No sensitive data in logs

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Verify permissions
   aws iam simulate-principal-policy \
     --policy-source-arn arn:aws:iam::ACCOUNT:user/USERNAME \
     --action-names bedrock:InvokeModel
   ```

2. **Agent Not Responding**
   ```bash
   # Check agent status
   agentcore status
   
   # View logs
   agentcore logs
   
   # Test connectivity
   agentcore invoke --debug "test"
   ```

3. **Memory Issues**
   ```bash
   # Reset memory
   agentcore memory reset
   
   # Check memory status
   agentcore memory status
   ```

### Debug Mode
```bash
# Enable verbose logging
agentcore deploy --verbose

# Test with debug output
agentcore invoke --debug "test message"
```

## 📈 Scaling & Performance

### Auto Scaling
AgentCore automatically scales based on demand:
- Cold start optimization
- Concurrent request handling
- Regional deployment

### Performance Tuning
```bash
# Optimize for latency
agentcore configure --deployment-type direct_code_deploy

# Optimize for throughput
agentcore configure --deployment-type container
```

### Load Testing
```bash
# Simple load test
for i in {1..100}; do
  agentcore invoke "test $i" &
done
wait
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
name: Deploy AgentCore
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2
      - name: Deploy AgentCore
        run: agentcore deploy --non-interactive
```

## 📞 Support

### Getting Help
1. Check the [troubleshooting section](#troubleshooting)
2. Review [AWS AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
3. Contact support through AWS channels

### Community Resources
- [AgentCore GitHub](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [AWS re:Post](https://repost.aws/tags/bedrock-agentcore)
- [AWS Developer Forums](https://forums.aws.amazon.com/forum.jspa?forumID=148)

---

**Ready to deploy?** Run `agentcore deploy` and your agent will be live in minutes!