# AgentCore Demo - Production-Ready AI Agent

A complete, production-ready example of building and deploying AI agents using AWS Bedrock AgentCore.

## 🚀 Features

- **Production-Ready**: Complete agent implementation with error handling
- **AgentCore Integration**: Proper use of BedrockAgentCoreApp wrapper
- **Local Development**: Test locally before deploying to AWS
- **Memory Support**: Configured for AgentCore memory management
- **Observability**: Built-in logging and monitoring
- **Scalable**: Ready for enterprise deployment

## 📋 Prerequisites

- Python 3.10 or higher
- AWS CLI configured with appropriate permissions
- AWS Bedrock model access (Claude Sonnet recommended)
- AgentCore starter toolkit installed

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS configuration
   ```

3. **Test locally:**
   ```bash
   python agent.py
   ```

## 🚀 Deployment

### 1. Configure AgentCore
```bash
agentcore configure --entrypoint agent.py --non-interactive
```

### 2. Deploy to AWS
```bash
agentcore deploy
```

### 3. Test Deployed Agent
```bash
agentcore invoke "Hello, AgentCore!"
```

## 💡 Usage Examples

### Local Testing
```python
from agent import agent_handler

response = agent_handler({"prompt": "What can you do?"})
print(response["response"])
```

### AgentCore Commands
```bash
# Start development server
agentcore dev

# Test locally
agentcore invoke --dev "Tell me about AgentCore"

# Check deployment status
agentcore status

# Stop active session
agentcore stop-session

# Clean up resources
agentcore destroy
```

## 🏗️ Architecture

```
AgentCore Demo Agent
├── agent.py              # Main agent implementation
├── requirements.txt       # Python dependencies
├── .bedrock_agentcore.yaml # AgentCore configuration (auto-generated)
├── .env.example          # Environment template
└── README.md             # This file
```

## 🔧 Configuration

The agent supports various configuration options:

- **Memory Mode**: STM_ONLY (short-term memory)
- **Deployment**: Container-based for cross-platform compatibility
- **Runtime**: Python 3.11 on AWS Lambda
- **Observability**: Enabled with OpenTelemetry

## 📊 Monitoring

AgentCore provides built-in observability:

- **Traces**: Request/response tracking
- **Metrics**: Performance monitoring
- **Logs**: Detailed execution logs
- **Dashboard**: CloudWatch integration

## 🔒 Security

- IAM-based authentication
- Encrypted memory storage
- VPC support for private deployments
- Request header validation

## 💰 Cost Optimization

- Serverless runtime (pay per request)
- Automatic scaling
- Session lifecycle management
- Memory cleanup policies

## 🚀 Production Checklist

- [ ] AWS credentials configured
- [ ] Bedrock model access enabled
- [ ] Environment variables set
- [ ] Local testing completed
- [ ] AgentCore configuration validated
- [ ] Deployment successful
- [ ] Monitoring enabled
- [ ] Cost alerts configured

## 📚 Learn More

- [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Starter Toolkit](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [Best Practices Guide](https://aws.github.io/bedrock-agentcore-starter-toolkit/)

## 🤝 Support

For issues and questions:
- Check the [troubleshooting guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/troubleshooting.html)
- Review [AgentCore examples](https://github.com/aws/bedrock-agentcore-starter-toolkit/tree/main/examples)
- Contact support through AWS channels

## 📄 License

MIT License - see LICENSE file for details.