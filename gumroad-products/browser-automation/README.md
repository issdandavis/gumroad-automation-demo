# 🤖 Browser Automation Tool

**Automate Any Web Task Locally – No Code, No Cloud, Just Results**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 What Is This?

A privacy-first browser automation tool that runs **entirely on your machine**. No cloud services, no data leaving your computer, no monthly subscriptions eating your profits.

Perfect for:
- 🛒 **E-commerce sellers** - Bulk update prices, manage inventory
- 💼 **Freelancers** - Automate LinkedIn outreach, data collection
- 📊 **Marketers** - Scrape competitor data, automate reports
- 🔧 **Anyone** tired of repetitive browser tasks

## ✨ Features

- **🔒 Privacy-First**: Everything runs locally. Your data never leaves your machine.
- **📝 No-Code Recipes**: YAML-based automation - just edit text files
- **🚀 One-Command Setup**: `./install.sh` and you're ready
- **🔄 Reusable Templates**: Pre-built recipes for common tasks
- **📈 Export Anywhere**: CSV, JSON, or direct to Google Sheets

## 🚀 Quick Start

### 1. Install (One Command)

```bash
# macOS/Linux
chmod +x install.sh && ./install.sh

# Windows (PowerShell)
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
playwright install chromium
```

### 2. Configure

Edit `config.yaml` with your settings:

```yaml
browser:
  headless: false  # Watch it work, or set true for background
  
credentials:
  shopify:
    store_url: "your-store.myshopify.com"
```

### 3. Run

```bash
# Preview what will happen (dry run)
python run.py --recipe recipes/shopify-price-updater.yaml --dry-run

# Execute for real
python run.py --recipe recipes/shopify-price-updater.yaml
```

## 📦 Included Recipes

### 🛍️ Shopify Price Updater
Bulk update product prices from a CSV file. Perfect for sales, seasonal adjustments, or supplier price changes.

```bash
python run.py --recipe recipes/shopify-price-updater.yaml
```

**Input**: `prices.csv` with columns: `product_id, sku, new_price, compare_at_price`

### 🔗 LinkedIn Connector
Automatically send connection requests to profiles matching your criteria. Includes customizable note templates.

```bash
python run.py --recipe recipes/linkedin-connector.yaml
```

**Config**: Set `max_connections_per_day` (default: 25) to stay within LinkedIn limits.

### 📊 Google Sheets Scraper
Extract data from any website directly into Google Sheets. Handles pagination automatically.

```bash
python run.py --recipe recipes/google-sheets-scraper.yaml
```

**Config**: Customize `selectors` for your target website.

## 🛠️ Create Your Own Recipe

Recipes are simple YAML files:

```yaml
name: My Custom Automation
version: "1.0.0"
description: What this does

steps:
  - action: navigate
    url: "https://example.com"
    wait_for: ".main-content"
    
  - action: click
    selector: "button.submit"
    
  - action: type
    selector: "input[name='search']"
    value: "my search term"
    
  - action: extract
    selector: ".results-item"
    store_as: "my_data"
```

### Available Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `navigate` | Go to URL | `url`, `wait_for` |
| `click` | Click element | `selector`, `wait_for` |
| `type` | Enter text | `selector`, `value` |
| `clear` | Clear input | `selector` |
| `wait` | Pause execution | `duration_ms` |
| `extract` | Get data | `selector`, `store_as` |
| `keyboard` | Press keys | `keys` (array) |
| `loop` | Repeat steps | `data`, `steps` |
| `conditional` | If/then logic | `if`, `then` |

## 📁 Project Structure

```
browser-automation/
├── install.sh          # One-command installer
├── run.py              # Main runner script
├── config.yaml         # Your settings
├── requirements.txt    # Python dependencies
├── recipes/            # Automation recipes
│   ├── shopify-price-updater.yaml
│   ├── linkedin-connector.yaml
│   └── google-sheets-scraper.yaml
├── output/             # Results and exports
└── logs/               # Execution logs
```

## ⚙️ Configuration

### config.yaml

```yaml
browser:
  headless: false       # true = run in background
  timeout: 30000        # Max wait time (ms)
  
automation:
  delay_between_actions: 1500  # Be nice to websites
  max_retries: 3
  screenshot_on_error: true
  
output:
  directory: "./output"
  format: "csv"         # csv, json, xlsx
```

## 🔐 Security & Privacy

- **100% Local**: No cloud, no servers, no tracking
- **Your Credentials Stay Yours**: Stored in local config only
- **Open Source**: Inspect every line of code
- **No Telemetry**: We don't know you exist (and we like it that way)

## 🆘 Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Element not found"
- Increase `timeout` in config.yaml
- Check if the website changed its layout
- Use browser DevTools to verify selectors

### "Rate limited"
- Increase `delay_between_actions`
- Reduce daily limits in recipe config
- Add random delays between actions

## 📄 License

MIT License - Use it, modify it, sell products built with it. Just don't blame us if something breaks.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/issdandavis/browser-automation/issues)
- **Email**: support@example.com

---

**Built for solopreneurs who value their time and privacy.**

*Stop doing repetitive tasks. Start automating.*
