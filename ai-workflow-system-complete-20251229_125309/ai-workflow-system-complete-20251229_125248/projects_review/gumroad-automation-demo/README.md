# Gumroad Automation Demo

AI-powered browser automation demo for Gumroad product publishing. Built with Skyvern + FastAPI for automating web forms and workflows.

## 🎯 Purpose

This repository demonstrates automated workflows for Gumroad product management, including:
- Automated product creation and publishing
- Form filling and validation
- Sales webhook integration
- Email notification systems
- Customer onboarding automation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (if using JavaScript)
- Git
- Gumroad account
- API keys (see Configuration section)

### Installation

```bash
# Clone the repository
git clone https://github.com/issdandavis/gumroad-automation-demo.git
cd gumroad-automation-demo

# Install Python dependencies
pip install -r requirements.txt

# Or if using Node.js
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API credentials to `.env`:
```
GUMROAD_API_KEY=your_gumroad_api_key_here
SKYVERN_API_KEY=your_skyvern_key_here
FASTAPI_PORT=8000
```

### Running the Application

```bash
# Start the FastAPI server
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📁 Project Structure

```
gumroad-automation-demo/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── main.py              # FastAPI application
├── automation/          # Automation scripts
│   ├── gumroad.py      # Gumroad-specific automations
│   ├── webhooks.py     # Webhook handlers
│   └── utils.py        # Utility functions
├── tests/              # Test files
└── docs/               # Additional documentation
```

## 🔧 Usage

### Example: Automate Product Publishing

```python
from automation.gumroad import publish_product

# Publish a new product
result = publish_product(
    name="My Digital Product",
    price=29.99,
    description="An amazing product",
    file_path="/path/to/product.zip"
)
```

### API Endpoints

- `POST /api/publish` - Publish a new product
- `POST /api/webhook/sales` - Handle Gumroad sales webhooks
- `GET /api/status` - Check automation status
- `POST /api/notifications/send` - Send email notifications

## 🤖 AI Integration

This project is designed to be easily used by AI agents and automation tools:

### For External AI Systems

1. **Clear API Documentation**: All endpoints are documented with OpenAPI/Swagger
2. **Standardized Responses**: JSON responses with consistent error handling
3. **Environment Variables**: Easy configuration without code changes
4. **Modular Design**: Import specific functions as needed

### Using with AI Assistants

```python
# AI-friendly import structure
from automation import publish_product, send_notification, handle_webhook

# Simple function calls
publish_product(name="Product", price=10)
send_notification(email="user@example.com", message="Success!")
```

## 🔐 Security

- Never commit `.env` files or API keys
- Use environment variables for all sensitive data
- Review `.gitignore` to ensure secrets are excluded
- Rotate API keys regularly

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=automation tests/
```

## 📋 Current Issues & Roadmap

See the [Issues](https://github.com/issdandavis/gumroad-automation-demo/issues) tab for:
- Webhook integration tasks
- Email notification features
- Customer onboarding workflows
- Product variant automation
- Multi-product publishing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - feel free to use this project for learning and automation purposes.

## 🔗 Related Resources

- [Gumroad API Documentation](https://gumroad.com/api)
- [Skyvern Documentation](https://skyvern.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 💡 Tips for AI Agents

- All functions include type hints for better code understanding
- Error messages are descriptive and actionable
- Configuration is centralized in `.env` file
- No hardcoded values - everything is parameterized
- Logging is enabled for debugging and monitoring

## 📞 Support

For questions or issues:
1. Check existing [Issues](https://github.com/issdandavis/gumroad-automation-demo/issues)
2. Create a new issue with detailed description
3. Review documentation in the `docs/` folder

---

**Note**: This is a demonstration project. Ensure you comply with Gumroad's Terms of Service when using automation tools.
