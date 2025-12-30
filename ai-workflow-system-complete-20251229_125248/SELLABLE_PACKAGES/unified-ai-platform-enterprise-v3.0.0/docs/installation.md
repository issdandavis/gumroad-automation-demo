# Installation Guide

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for AI provider APIs

## Installation Methods

### Method 1: Docker Compose (Recommended)

1. Install Docker and Docker Compose
2. Extract the package
3. Run: `docker-compose -f deployment/docker-compose.prod.yml up -d`

### Method 2: Manual Installation

1. Install Node.js 18+
2. Install Python 3.11+
3. Install dependencies:
   ```bash
   cd bridge-api && npm install
   cd ../evolution-framework && pip install -r requirements.txt
   ```
4. Start services:
   ```bash
   # Terminal 1: Bridge API
   cd bridge-api && npm run dev
   
   # Terminal 2: Evolution Framework
   cd evolution-framework && python web_interface.py
   ```

## Configuration

1. Copy `.env.example` to `.env` in each service directory
2. Configure API keys and database connections
3. Restart services

## Verification

Run the test suite:
```bash
python test_unified_system.py
```

All tests should pass for a successful installation.
