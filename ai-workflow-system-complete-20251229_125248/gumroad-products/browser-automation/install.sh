#!/bin/bash
# ============================================
# Browser Automation Tool - One-Command Setup
# Powered by Skyvern | Privacy-First | No-Code
# ============================================

set -e

echo "🚀 Browser Automation Tool Installer"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
        return 0
    else
        echo -e "${RED}✗${NC} Python 3.8+ required. Please install Python first."
        echo "  Download: https://www.python.org/downloads/"
        exit 1
    fi
}

# Check Docker (optional but recommended)
check_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker found (recommended for browser isolation)"
    else
        echo -e "${YELLOW}!${NC} Docker not found - will use local browser"
    fi
}

# Create virtual environment
setup_venv() {
    echo ""
    echo "📦 Setting up virtual environment..."
    python3 -m venv .venv
    
    # Activate based on OS
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    echo -e "${GREEN}✓${NC} Virtual environment created"
}

# Install dependencies
install_deps() {
    echo ""
    echo "📥 Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓${NC} Dependencies installed"
}

# Install Playwright browsers
install_browsers() {
    echo ""
    echo "🌐 Installing browser automation drivers..."
    playwright install chromium
    echo -e "${GREEN}✓${NC} Chromium browser installed"
}

# Create config file
create_config() {
    if [ ! -f "config.yaml" ]; then
        echo ""
        echo "⚙️  Creating default configuration..."
        cat > config.yaml << 'EOF'
# Browser Automation Configuration
# Edit this file to customize your setup

browser:
  headless: false  # Set to true to run without visible browser
  timeout: 30000   # Max wait time in milliseconds
  
automation:
  delay_between_actions: 1500  # Milliseconds between actions
  max_retries: 3
  screenshot_on_error: true
  
output:
  directory: "./output"
  format: "csv"  # csv, json, or xlsx
  
# Add your credentials here (stored locally only)
credentials:
  # shopify:
  #   store_url: "your-store.myshopify.com"
  # linkedin:
  #   email: "your@email.com"
EOF
        echo -e "${GREEN}✓${NC} Configuration file created"
    fi
}

# Create output directory
setup_directories() {
    mkdir -p output
    mkdir -p logs
    echo -e "${GREEN}✓${NC} Output directories created"
}

# Main installation
main() {
    echo "Checking requirements..."
    echo ""
    
    check_python
    check_docker
    setup_venv
    install_deps
    install_browsers
    create_config
    setup_directories
    
    echo ""
    echo "============================================"
    echo -e "${GREEN}✅ Installation Complete!${NC}"
    echo "============================================"
    echo ""
    echo "Quick Start:"
    echo "  1. Edit config.yaml with your settings"
    echo "  2. Run: python run.py --recipe recipes/shopify-price-updater.yaml"
    echo ""
    echo "Available Recipes:"
    for recipe in recipes/*.yaml; do
        name=$(grep "^name:" "$recipe" | cut -d'"' -f2 | cut -d"'" -f2)
        echo "  • $recipe - $name"
    done
    echo ""
    echo "📚 Documentation: README.md"
    echo "🆘 Support: https://github.com/issdandavis/browser-automation/issues"
    echo ""
}

main "$@"
