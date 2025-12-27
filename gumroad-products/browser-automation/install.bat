@echo off
REM ============================================
REM Browser Automation Tool - Windows Setup
REM Powered by Skyvern | Privacy-First | No-Code
REM ============================================

echo.
echo Browser Automation Tool Installer
echo =====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat
echo [OK] Virtual environment created

REM Install dependencies
echo.
echo Installing dependencies...
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] Dependencies installed

REM Install Playwright browsers
echo.
echo Installing browser automation drivers...
playwright install chromium
echo [OK] Chromium browser installed

REM Create directories
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo [OK] Output directories created

REM Create config if not exists
if not exist "config.yaml" (
    echo.
    echo Creating default configuration...
    (
        echo # Browser Automation Configuration
        echo browser:
        echo   headless: false
        echo   timeout: 30000
        echo automation:
        echo   delay_between_actions: 1500
        echo   max_retries: 3
        echo   screenshot_on_error: true
        echo output:
        echo   directory: "./output"
        echo   format: "csv"
    ) > config.yaml
    echo [OK] Configuration file created
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo Quick Start:
echo   1. Edit config.yaml with your settings
echo   2. Run: python run.py --recipe recipes/shopify-price-updater.yaml
echo.
echo Available Recipes:
for %%f in (recipes\*.yaml) do echo   - %%f
echo.
pause
