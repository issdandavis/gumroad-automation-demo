# 🚀 Customer Setup Guide
## Self-Evolving AI Framework - Professional Installation

**Welcome to the Self-Evolving AI Framework!** This guide will get you up and running in under 10 minutes.

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9 or higher (3.14 recommended)
- **Memory**: 4GB RAM minimum
- **Storage**: 2GB free space
- **Network**: Stable internet connection
- **OS**: Windows 10+, macOS 10.15+, or Linux

### Required API Keys
You'll need at least one AI provider API key:
- **OpenAI**: [Get API key](https://platform.openai.com/api-keys)
- **Anthropic**: [Get API key](https://console.anthropic.com/)
- **Google AI**: [Get API key](https://makersuite.google.com/app/apikey)
- **xAI**: [Get API key](https://console.x.ai/)

---

## ⚡ Quick Installation

### Step 1: Download & Extract
```bash
# Extract your purchased package
unzip self-evolving-ai-framework-v3.0.0.zip
cd self-evolving-ai-framework
```

### Step 2: Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python --version  # Should be 3.9+
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (use any text editor)
notepad .env  # Windows
nano .env     # Linux/Mac
```

### Step 4: Initialize System
```bash
# Initialize the framework
python evolving_ai_main.py init

# Run demo to verify everything works
python evolving_ai_main.py demo
```

**🎉 Success!** Your AI system is now evolving autonomously.

---

## 🔧 Environment Configuration

Edit your `.env` file with your API keys:

```bash
# AI Provider Keys (add at least one)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_AI_API_KEY=your-google-ai-key
XAI_API_KEY=your-xai-key-here

# Optional: Cloud Storage (for advanced features)
DROPBOX_ACCESS_TOKEN=your-dropbox-token
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-username/your-repo

# System Configuration (defaults work fine)
AI_NETWORK_LOCAL=./AI_NETWORK_LOCAL
AUTONOMY_RISK_THRESHOLD=0.3
MAX_AUTONOMOUS_MUTATIONS=10
```

---

## 🧪 Verify Installation

Run these commands to ensure everything is working:

```bash
# Check system status
python evolving_ai_main.py status

# View fitness metrics
python evolving_ai_main.py fitness

# Run comprehensive tests
python -m pytest tests/ -v
```

Expected output:
```
✅ System Status: Healthy
✅ Generation: 1
✅ Fitness Score: 100.0
✅ All tests passing
```

---

## 🚀 First Steps

### 1. Monitor Your AI
```bash
# Watch your AI evolve in real-time
python evolving_ai_main.py status
```

### 2. Propose Improvements
```python
from self_evolving_core import EvolvingAIFramework
from self_evolving_core.models import Mutation

framework = EvolvingAIFramework()
framework.initialize()

# Suggest an improvement
mutation = Mutation(
    type="intelligence_upgrade",
    description="Improve response accuracy",
    fitness_impact=5.0
)

result = framework.propose_mutation(mutation)
print(f"Mutation approved: {result['approved']}")
```

### 3. Track Performance
```python
# Monitor system fitness
fitness = framework.get_fitness()
print(f"Success Rate: {fitness.success_rate}")
print(f"Cost Efficiency: {fitness.cost_efficiency}")
```

---

## 🔍 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'self_evolving_core'`
**Solution**: 
```bash
cd app-productizer  # Make sure you're in the right directory
pip install -r requirements.txt
```

**Issue**: `API key not found` error
**Solution**: 
```bash
# Check your .env file has the correct format
cat .env | grep API_KEY
# Ensure no spaces around the = sign
```

**Issue**: Tests failing
**Solution**:
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clear cache and retry
rm -rf __pycache__ .pytest_cache
python -m pytest tests/ -v
```

### Getting Help

- **Documentation**: Check `COMPLETE_DOCUMENTATION.md`
- **Community**: Join our [Discord server](https://discord.gg/evolving-ai)
- **Email Support**: support@evolving-ai.com (Professional+ tiers)
- **Priority Support**: Call +1 (555) 123-4567 (Enterprise tier)

---

## 📈 Next Steps

### Production Deployment
```bash
# Deploy to AWS Lambda
python deploy.py --environment production

# Or use Docker
docker build -t my-evolving-ai .
docker run -d --name evolving-ai my-evolving-ai
```

### Advanced Configuration
- Review `COMMERCIAL_PACKAGE.md` for enterprise features
- Check `API_REFERENCE.md` for integration options
- Explore `examples/` directory for use cases

### Training & Certification
- Complete our [video course](https://evolving-ai.com/training)
- Join live workshops and Q&A sessions
- Earn Professional AI Automation Certificate

---

## 💡 Pro Tips

1. **Start Small**: Begin with basic mutations before complex workflows
2. **Monitor Fitness**: Keep an eye on the fitness score trends
3. **Use Rollback**: Don't hesitate to rollback if something goes wrong
4. **Join Community**: Connect with other users for tips and tricks
5. **Regular Updates**: Keep your system updated for best performance

---

## 📞 Support Contacts

### By License Tier

**Starter Edition**
- Community Discord support
- Documentation and tutorials
- Email: community@evolving-ai.com

**Professional Edition**  
- Priority email support (24-48h response)
- Training video access
- Email: professional@evolving-ai.com

**Enterprise Edition**
- Priority phone support (4h response)
- Custom development services
- 1-on-1 training sessions
- Phone: +1 (555) 123-4567
- Email: enterprise@evolving-ai.com

---

**🎉 Congratulations!** You're now ready to harness the power of self-evolving AI.

*Your AI system will continuously improve itself. Sit back and watch the magic happen.*