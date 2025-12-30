#!/usr/bin/env python3
"""
Unified AI Platform - Commercial Package Creator
===============================================

Creates sellable packages for different tiers with proper licensing,
documentation, and deployment configurations.
"""

import os
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class UnifiedPlatformPackager:
    def __init__(self):
        self.version = "3.0.0"
        self.build_date = datetime.now().strftime("%Y%m%d")
        self.root_dir = Path(__file__).parent
        self.output_dir = self.root_dir / "SELLABLE_PACKAGES"
        self.output_dir.mkdir(exist_ok=True)
        
        self.tiers = {
            'starter': {
                'price': 297,
                'name': 'Starter Edition',
                'includes': ['bridge-api', 'evolution-framework', 'basic-docs'],
                'excludes': ['workflow-architect', 'aws-integration', 'enterprise-features']
            },
            'professional': {
                'price': 997,
                'name': 'Professional Edition', 
                'includes': ['bridge-api', 'evolution-framework', 'workflow-architect', 'monitoring'],
                'excludes': ['aws-integration', 'enterprise-security']
            },
            'enterprise': {
                'price': 2997,
                'name': 'Enterprise Edition',
                'includes': ['*'],  # Everything
                'excludes': []
            }
        }
    
    def create_all_packages(self):
        """Create all tier packages"""
        print(f"🚀 Creating Unified AI Platform packages v{self.version}")
        
        for tier_name, tier_config in self.tiers.items():
            print(f"\n📦 Creating {tier_config['name']}...")
            self.create_package(tier_name, tier_config)
        
        print(f"\n✅ All packages created in {self.output_dir}")
        self.create_distribution_info()
    
    def create_package(self, tier_name: str, tier_config: Dict):
        """Create a specific tier package"""
        package_name = f"unified-ai-platform-{tier_name}-v{self.version}"
        package_dir = self.output_dir / package_name
        
        # Clean and create package directory with better error handling
        if package_dir.exists():
            try:
                shutil.rmtree(package_dir)
            except PermissionError:
                # On Windows, try to handle permission issues
                import stat
                def handle_remove_readonly(func, path, exc):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(package_dir, onerror=handle_remove_readonly)
        
        package_dir.mkdir(parents=True)
        
        # Copy core components
        self.copy_bridge_api(package_dir, tier_config)
        self.copy_evolution_framework(package_dir, tier_config)
        
        if 'workflow-architect' in tier_config['includes']:
            self.copy_workflow_architect(package_dir, tier_config)
        
        # Copy deployment configurations
        self.copy_deployment_configs(package_dir, tier_config)
        
        # Create documentation
        self.create_documentation(package_dir, tier_config)
        
        # Create license and legal files
        self.create_license_files(package_dir, tier_config)
        
        # Create setup scripts
        self.create_setup_scripts(package_dir, tier_config)
        
        # Create ZIP file
        zip_path = self.output_dir / f"{package_name}.zip"
        self.create_zip(package_dir, zip_path)
        
        print(f"   ✅ {tier_config['name']} package created: {zip_path}")
    
    def copy_bridge_api(self, package_dir: Path, tier_config: Dict):
        """Copy Bridge API with tier-specific configurations"""
        bridge_dir = package_dir / "bridge-api"
        bridge_dir.mkdir()
        
        # Copy source files
        source_files = [
            "bridge-api/src",
            "bridge-api/package.json",
            "bridge-api/tsconfig.json",
            "bridge-api/.env.example"
        ]
        
        for file_path in source_files:
            src = self.root_dir / file_path
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, bridge_dir / src.name)
                else:
                    shutil.copy2(src, bridge_dir / src.name)
        
        # Create Dockerfile
        dockerfile_content = '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]'''
        
        (bridge_dir / "Dockerfile").write_text(dockerfile_content, encoding='utf-8')
    
    def copy_evolution_framework(self, package_dir: Path, tier_config: Dict):
        """Copy Evolution Framework"""
        evo_dir = package_dir / "evolution-framework"
        evo_dir.mkdir()
        
        # Copy framework files
        framework_files = [
            "app-productizer/self_evolving_core",
            "app-productizer/web_interface.py",
            "app-productizer/bridge_integration.py",
            "app-productizer/shared_types.py",
            "app-productizer/type_validation.py",
            "app-productizer/requirements.txt"
        ]
        
        for file_path in framework_files:
            src = self.root_dir / file_path
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, evo_dir / src.name)
                else:
                    shutil.copy2(src, evo_dir / src.name)
        
        # Create Dockerfile
        dockerfile_content = '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_interface.py", "--port", "5000"]'''
        
        (evo_dir / "Dockerfile").write_text(dockerfile_content, encoding='utf-8')
    
    def copy_workflow_architect(self, package_dir: Path, tier_config: Dict):
        """Copy AI Workflow Architect (Professional+ only)"""
        workflow_dir = package_dir / "workflow-architect"
        workflow_dir.mkdir()
        
        # Copy workflow files (excluding node_modules and build artifacts)
        workflow_source = self.root_dir / "projects_review" / "AI-Workflow-Architect"
        if workflow_source.exists():
            # Copy source files selectively to avoid node_modules issues
            source_files = [
                "src",
                "public", 
                "package.json",
                "package-lock.json",
                "tsconfig.json",
                "vite.config.ts",
                "index.html",
                ".env.example"
            ]
            
            for file_name in source_files:
                src_path = workflow_source / file_name
                if src_path.exists():
                    if src_path.is_dir():
                        shutil.copytree(src_path, workflow_dir / file_name, ignore=shutil.ignore_patterns('node_modules', 'dist', '.git'))
                    else:
                        shutil.copy2(src_path, workflow_dir / file_name)
        
        # Create integration configuration
        integration_config = {
            "bridge_api_url": "http://localhost:3001",
            "evolution_api_url": "http://localhost:5000",
            "websocket_enabled": True,
            "auto_connect": True
        }
        
        (workflow_dir / "integration.json").write_text(
            json.dumps(integration_config, indent=2), encoding='utf-8'
        )
        
        # Create Dockerfile for Workflow Architect
        dockerfile_content = '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]'''
        
        (workflow_dir / "Dockerfile").write_text(dockerfile_content, encoding='utf-8')
    
    def copy_deployment_configs(self, package_dir: Path, tier_config: Dict):
        """Copy deployment configurations"""
        deploy_dir = package_dir / "deployment"
        deploy_dir.mkdir()
        
        # Docker Compose for production
        compose_content = '''version: '3.8'
services:
  bridge-api:
    build: ./bridge-api
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - REDIS_HOST=redis
      - DATABASE_URL=postgresql://user:pass@postgres:5432/unified_ai
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  evolution-framework:
    build: ./evolution-framework
    ports:
      - "5000:5000"
    environment:
      - BRIDGE_API_URL=http://bridge-api:3001
    depends_on:
      - bridge-api
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=unified_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:'''
        
        (deploy_dir / "docker-compose.prod.yml").write_text(compose_content, encoding='utf-8')
        
        # Kubernetes manifests (Enterprise only)
        if tier_config['name'] == 'Enterprise Edition':
            k8s_dir = deploy_dir / "kubernetes"
            k8s_dir.mkdir()
            # Add K8s manifests here
    
    def create_documentation(self, package_dir: Path, tier_config: Dict):
        """Create comprehensive documentation"""
        docs_dir = package_dir / "docs"
        docs_dir.mkdir()
        
        # README.md
        readme_content = f'''# Unified AI Platform - {tier_config['name']}

## Quick Start

1. **Prerequisites**
   - Docker & Docker Compose
   - Node.js 18+ (for development)
   - Python 3.11+ (for development)

2. **Installation**
   ```bash
   # Extract the package
   unzip unified-ai-platform-{tier_config['name'].lower().replace(' ', '-').replace('edition', '').strip()}-v{self.version}.zip
   cd unified-ai-platform-*
   
   # Start with Docker Compose
   docker-compose -f deployment/docker-compose.prod.yml up -d
   ```

3. **Access the System**
   - Bridge API: http://localhost:3001
   - Evolution Framework: http://localhost:5000
   - Health Check: http://localhost:3001/health

## Architecture

The Unified AI Platform consists of:

- **Bridge API**: Central integration hub (TypeScript/Express)
- **Evolution Framework**: Self-evolving AI system (Python/Flask)
{"- **Workflow Architect**: AI workflow orchestration (React/Express)" if 'workflow-architect' in tier_config['includes'] else ""}

## Support

- Documentation: See `/docs` folder
- Issues: Create GitHub issues (if applicable)
- {"Enterprise Support: priority@yourcompany.com" if tier_config['name'] == 'Enterprise Edition' else "Community Support: community@yourcompany.com"}

## License

Commercial License - See LICENSE.md for details.
'''
        
        (package_dir / "README.md").write_text(readme_content, encoding='utf-8')
        
        # Installation Guide
        install_guide = '''# Installation Guide

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
'''
        
        (docs_dir / "installation.md").write_text(install_guide, encoding='utf-8')
    
    def create_license_files(self, package_dir: Path, tier_config: Dict):
        """Create license and legal files"""
        license_content = f'''# Commercial License Agreement

## Unified AI Platform - {tier_config['name']}

**License Type**: Commercial Use License
**Price**: ${tier_config['price']}
**Version**: {self.version}
**Date**: {datetime.now().strftime("%Y-%m-%d")}

### Grant of License

Subject to the terms of this agreement, you are granted a non-exclusive, 
non-transferable license to use the Unified AI Platform software for 
commercial purposes.

### Permitted Uses

- Deploy in production environments
- Modify source code for your needs
- Create derivative works
- Use for commercial projects
{"- White-label and resell (with restrictions)" if tier_config['name'] != 'Starter Edition' else ""}

### Restrictions

- No redistribution of source code
- No reverse engineering for competitive purposes
- Must maintain copyright notices
{"- Single developer use only" if tier_config['name'] == 'Starter Edition' else f"- Maximum {5 if tier_config['name'] == 'Professional Edition' else 'unlimited'} developers"}

### Support & Updates

{"- Community support via GitHub/Discord" if tier_config['name'] == 'Starter Edition' else ""}
{"- Email support with 48-hour response time" if tier_config['name'] == 'Professional Edition' else ""}
{"- Priority support with 4-hour response time and dedicated channel" if tier_config['name'] == 'Enterprise Edition' else ""}

### Warranty Disclaimer

THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.

### Contact

For license questions: legal@yourcompany.com
'''
        
        (package_dir / "LICENSE.md").write_text(license_content, encoding='utf-8')
    
    def create_setup_scripts(self, package_dir: Path, tier_config: Dict):
        """Create automated setup scripts"""
        scripts_dir = package_dir / "scripts"
        scripts_dir.mkdir()
        
        # Setup script for Unix systems
        setup_script = '''#!/bin/bash
set -e

echo "Setting up Unified AI Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment files
if [ ! -f bridge-api/.env ]; then
    cp bridge-api/.env.example bridge-api/.env
    echo "Created bridge-api/.env - please configure your settings"
fi

if [ ! -f evolution-framework/.env ]; then
    echo "BRIDGE_API_URL=http://localhost:3001" > evolution-framework/.env
    echo "Created evolution-framework/.env"
fi

# Start services
echo "Starting services with Docker Compose..."
docker-compose -f deployment/docker-compose.prod.yml up -d

echo "Waiting for services to start..."
sleep 10

# Health check
echo "Checking system health..."
curl -f http://localhost:3001/health || { echo "Health check failed. Check logs with: docker-compose logs"; exit 1; }

echo "Unified AI Platform is running!"
echo "Bridge API: http://localhost:3001"
echo "Evolution Framework: http://localhost:5000"
echo "Health Status: http://localhost:3001/health"
'''
        
        (scripts_dir / "setup.sh").write_text(setup_script, encoding='utf-8')
        os.chmod(scripts_dir / "setup.sh", 0o755)
        
        # Windows setup script
        windows_setup = '''@echo off
echo Setting up Unified AI Platform...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is required but not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

REM Create environment files
if not exist "bridge-api\\.env" (
    copy "bridge-api\\.env.example" "bridge-api\\.env"
    echo Created bridge-api\\.env - please configure your settings
)

if not exist "evolution-framework\\.env" (
    echo BRIDGE_API_URL=http://localhost:3001 > "evolution-framework\\.env"
    echo Created evolution-framework\\.env
)

REM Start services
echo Starting services with Docker Compose...
docker-compose -f deployment\\docker-compose.prod.yml up -d

echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo Unified AI Platform is running!
echo Bridge API: http://localhost:3001
echo Evolution Framework: http://localhost:5000
echo Health Status: http://localhost:3001/health

pause
'''
        
        (scripts_dir / "setup.bat").write_text(windows_setup, encoding='utf-8')
    
    def create_zip(self, source_dir: Path, zip_path: Path):
        """Create ZIP file from directory"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir.parent)
                    zipf.write(file_path, arcname)
    
    def create_distribution_info(self):
        """Create distribution information file"""
        dist_info = {
            "version": self.version,
            "build_date": self.build_date,
            "packages": {},
            "total_size_mb": 0
        }
        
        for tier_name, tier_config in self.tiers.items():
            zip_file = self.output_dir / f"unified-ai-platform-{tier_name}-v{self.version}.zip"
            if zip_file.exists():
                size_mb = zip_file.stat().st_size / (1024 * 1024)
                dist_info["packages"][tier_name] = {
                    "name": tier_config["name"],
                    "price": tier_config["price"],
                    "file": zip_file.name,
                    "size_mb": round(size_mb, 2)
                }
                dist_info["total_size_mb"] += size_mb
        
        dist_info["total_size_mb"] = round(dist_info["total_size_mb"], 2)
        
        (self.output_dir / "distribution_info.json").write_text(
            json.dumps(dist_info, indent=2), encoding='utf-8'
        )
        
        print(f"\n📊 Distribution Summary:")
        print(f"   Total packages: {len(dist_info['packages'])}")
        print(f"   Total size: {dist_info['total_size_mb']} MB")
        for tier, info in dist_info["packages"].items():
            print(f"   {info['name']}: ${info['price']} ({info['size_mb']} MB)")

if __name__ == "__main__":
    packager = UnifiedPlatformPackager()
    packager.create_all_packages()