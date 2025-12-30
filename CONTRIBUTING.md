# Contributing to AI Workflow Systems

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📋 Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS CLI configured
- Git

### Installation
```bash
# Clone your fork
git clone https://github.com/yourusername/ai-workflow-systems.git
cd ai-workflow-systems

# Install Python dependencies
cd agentcore-demo
pip install -r requirements.txt

# Install Node.js dependencies
cd ../ai-workflow-architect
npm install
```

## 🧪 Testing

### AgentCore Demo
```bash
cd agentcore-demo
python -m pytest tests/ -v
python validate_package.py
```

### AI Workflow Architect
```bash
cd ai-workflow-architect
npm test
npm run build
```

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Maximum line length: 88 characters

### TypeScript/JavaScript
- Use Prettier for formatting
- Follow ESLint rules
- Use meaningful variable names
- Add JSDoc comments for functions

## 🐛 Bug Reports

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

## 💡 Feature Requests

Use the feature request template and include:
- Problem description
- Proposed solution
- Alternative approaches considered
- Use cases and benefits

## 📚 Documentation

- Update README files for new features
- Add inline code comments
- Update API documentation
- Include examples and usage

## 🔒 Security

- Report security issues privately to security@aiworkflow.com
- Don't include sensitive data in commits
- Follow security best practices
- Use environment variables for secrets

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional environment

## 📞 Questions?

- Create a GitHub issue for technical questions
- Email support@aiworkflow.com for general inquiries
- Join our community discussions

Thank you for contributing to AI Workflow Systems! 🚀
