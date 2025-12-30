#!/usr/bin/env python3
"""
Comprehensive Distribution Package Creator
Creates a complete downloadable package of the AI Workflow System
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
import fnmatch

def should_exclude(file_path, exclude_patterns):
    """Check if a file should be excluded based on patterns"""
    # Always exclude these regardless of patterns
    always_exclude = [
        '__pycache__',
        '.pytest_cache',
        '.hypothesis',
        'node_modules',
        '.git',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '.coverage',
        'htmlcov',
        '.mypy_cache',
        '.ruff_cache',
        'dist',
        'build',
        '*.egg-info',
        '.venv',
        'venv',
        'env'
    ]
    
    # Check if any part of the path contains excluded items
    path_parts = Path(file_path).parts
    for part in path_parts:
        if part in always_exclude:
            return True
        for pattern in always_exclude:
            if fnmatch.fnmatch(part, pattern):
                return True
    
    # Check against additional exclude patterns
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    
    return False

def create_comprehensive_package():
    """Create a comprehensive distribution package"""
    
    # Additional exclude patterns (beyond the always_exclude)
    exclude_patterns = [
        '*.tmp',
        '*.temp',
        '*.sqlite3',
        '*.db',
        '.env',
        '.envrc',
        'logs/*.json',
        'AI_NETWORK_LOCAL/snapshots/*.json',  # Keep structure but not all snapshots
        'universal_bridge.db',
        'AI_SPINE_MEMORY.db',
        'test_results.json',
        'validation_report.json',
        'AI_SESSION_LOG.json',
        'AI_BULLETIN_BOARD.json',
        'AI_VALIDATION_REPORT.json'
    ]
    
    # Create package directory
    package_name = f"ai-workflow-system-complete-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = Path(package_name)
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    print(f"Creating comprehensive distribution package: {package_name}")
    
    # Copy files with smart filtering
    copied_files = []
    skipped_files = []
    total_size = 0
    
    for root, dirs, files in os.walk('.'):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, '.')
            
            # Skip if matches exclude patterns
            if should_exclude(relative_path, exclude_patterns):
                skipped_files.append(relative_path)
                continue
            
            # Skip very large files (>50MB)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    skipped_files.append(f"{relative_path} (too large: {file_size/(1024*1024):.1f}MB)")
                    continue
            except:
                continue
            
            # Create destination directory
            dest_path = package_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            try:
                shutil.copy2(file_path, dest_path)
                copied_files.append(relative_path)
                total_size += file_size
            except Exception as e:
                print(f"Error copying {relative_path}: {e}")
                skipped_files.append(f"{relative_path} (error: {e})")
    
    # Create comprehensive package manifest
    manifest = {
        "package_name": package_name,
        "created_at": datetime.now().isoformat(),
        "total_files": len(copied_files),
        "skipped_files": len(skipped_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "description": "AI Workflow System - Complete Distribution Package",
        "version": "1.0.0",
        "components": {
            "self_evolving_ai": "app-productizer/",
            "workflow_architect": "projects_review/AI-Workflow-Architect/",
            "bridge_api": "bridge-api/",
            "business_apps": "business-apps/",
            "sellable_packages": "SELLABLE_PACKAGES/",
            "documentation": "Various .md files",
            "tests": "tests/ and test_*.py files",
            "configuration": ".kiro/ and config files"
        },
        "key_features": [
            "Self-Evolving AI Framework with web interface",
            "Multi-agent AI orchestration platform",
            "Bridge API for system integration",
            "Commercial packaging system",
            "Comprehensive documentation",
            "Testing and validation framework"
        ]
    }
    
    with open(package_dir / "PACKAGE_MANIFEST.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create comprehensive installation guide
    install_guide = f"""# AI Workflow System - Complete Installation Guide

## Package Overview

This is a complete distribution of the AI Workflow System, containing {len(copied_files)} files across multiple components.

### 🚀 Main Components

1. **Self-Evolving AI Framework** (`app-productizer/`)
   - Core AI evolution system
   - Web interface for management
   - Bridge integration capabilities
   - Commercial packaging tools

2. **AI Workflow Architect** (`projects_review/AI-Workflow-Architect/`)
   - Multi-agent orchestration platform
   - React + TypeScript frontend
   - Express.js backend
   - Database integration

3. **Bridge API** (`bridge-api/`)
   - System integration layer
   - TypeScript adapters
   - Workflow coordination

4. **Business Applications** (`business-apps/`)
   - Production-ready applications
   - E-commerce integrations

5. **Sellable Packages** (`SELLABLE_PACKAGES/`)
   - Commercial product packages
   - Ready-to-sell components

## 🛠️ Installation Steps

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Git (optional, for updates)

### 1. Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv ai-workflow-env
source ai-workflow-env/bin/activate  # On Windows: ai-workflow-env\\Scripts\\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Self-Evolving AI System
```bash
cd app-productizer

# Start the main AI system
python evolving_ai_main.py

# Or start the web interface
python web_interface.py
```

### 3. AI Workflow Architect (Full Stack)
```bash
cd projects_review/AI-Workflow-Architect

# Install dependencies
npm install

# Start development server
npm run dev

# Or build for production
npm run build
npm start
```

### 4. Bridge API
```bash
cd bridge-api

# Install dependencies
npm install

# Start the bridge API
npm run dev
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` files to `.env` and configure:

```bash
# AI Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Database Configuration
DATABASE_URL=your_database_url

# System Configuration
SESSION_SECRET=your_session_secret
```

### Database Setup
```bash
# For AI Workflow Architect
cd projects_review/AI-Workflow-Architect
npm run db:push
```

## 📚 Documentation

- `README.md` - Main project overview
- `COMPLETE_COMMERCIALIZATION_GUIDE.md` - Business deployment
- `ENTERPRISE_DEPLOYMENT_GUIDE.md` - Enterprise setup
- `TECHNICAL_ARCHITECTURE_OVERVIEW.md` - Technical details
- `app-productizer/API_REFERENCE.md` - API documentation
- `app-productizer/QUICK_START.md` - Quick start guide

## 🧪 Testing

```bash
# Run comprehensive tests
python test_unified_system.py

# Test specific components
cd app-productizer
python test-ai-communication.py
```

## 🚀 Deployment

### Local Development
All components can run locally for development and testing.

### Production Deployment
See `ENTERPRISE_DEPLOYMENT_GUIDE.md` for production deployment instructions.

## 📦 Package Contents Summary

- **Total Files**: {len(copied_files)}
- **Package Size**: {total_size / (1024 * 1024):.1f} MB
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🆘 Support

For support, documentation, and updates:
1. Check the included documentation files
2. Review the API reference guides
3. Run the test suites to validate your setup

---

**Note**: This package contains the complete AI Workflow System as of {datetime.now().strftime('%Y-%m-%d')}. 
Some features may require additional configuration or API keys.
"""
    
    with open(package_dir / "INSTALLATION_GUIDE.md", 'w') as f:
        f.write(install_guide)
    
    # Create a quick start script
    quick_start = """#!/bin/bash
# Quick Start Script for AI Workflow System

echo "🚀 AI Workflow System - Quick Start"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎯 Choose what to start:"
echo "1. Self-Evolving AI System (Python)"
echo "2. AI Workflow Architect (Full Stack)"
echo "3. Both systems"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🤖 Starting Self-Evolving AI System..."
        cd app-productizer
        python evolving_ai_main.py
        ;;
    2)
        echo "🏗️ Starting AI Workflow Architect..."
        cd projects_review/AI-Workflow-Architect
        npm install
        npm run dev
        ;;
    3)
        echo "🚀 Starting both systems..."
        echo "Starting AI System in background..."
        cd app-productizer
        python evolving_ai_main.py &
        cd ../projects_review/AI-Workflow-Architect
        npm install
        npm run dev
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
"""
    
    with open(package_dir / "quick_start.sh", 'w') as f:
        f.write(quick_start)
    
    # Make quick start script executable
    os.chmod(package_dir / "quick_start.sh", 0o755)
    
    # Create ZIP archive
    zip_filename = f"{package_name}.zip"
    print(f"📦 Creating ZIP archive: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir.parent)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    # Print comprehensive summary
    print(f"\n✅ Comprehensive distribution package created successfully!")
    print(f"📦 Package: {zip_filename}")
    print(f"📁 Files included: {len(copied_files)}")
    print(f"⏭️  Files skipped: {len(skipped_files)}")
    print(f"📊 Package size: {os.path.getsize(zip_filename) / (1024*1024):.1f} MB")
    
    # Show key components
    print(f"\n📋 Key components included:")
    
    component_counts = {}
    for file_path in copied_files:
        if file_path.startswith('app-productizer/'):
            component_counts['Self-Evolving AI'] = component_counts.get('Self-Evolving AI', 0) + 1
        elif file_path.startswith('projects_review/AI-Workflow-Architect'):
            component_counts['AI Workflow Architect'] = component_counts.get('AI Workflow Architect', 0) + 1
        elif file_path.startswith('bridge-api/'):
            component_counts['Bridge API'] = component_counts.get('Bridge API', 0) + 1
        elif file_path.startswith('SELLABLE_PACKAGES/'):
            component_counts['Sellable Packages'] = component_counts.get('Sellable Packages', 0) + 1
        elif file_path.startswith('business-apps/'):
            component_counts['Business Apps'] = component_counts.get('Business Apps', 0) + 1
        elif file_path.endswith('.md'):
            component_counts['Documentation'] = component_counts.get('Documentation', 0) + 1
        elif 'test' in file_path.lower():
            component_counts['Tests'] = component_counts.get('Tests', 0) + 1
    
    for component, count in component_counts.items():
        print(f"  ✓ {component}: {count} files")
    
    # Show some sample files
    print(f"\n📄 Sample included files:")
    sample_files = [
        'requirements.txt',
        'README.md',
        'app-productizer/evolving_ai_main.py',
        'app-productizer/web_interface.py',
        'COMPLETE_COMMERCIALIZATION_GUIDE.md',
        'test_unified_system.py'
    ]
    
    for sample in sample_files:
        if sample in copied_files:
            print(f"  ✓ {sample}")
    
    return zip_filename

if __name__ == "__main__":
    package_file = create_comprehensive_package()
    print(f"\n🎉 Ready to distribute: {package_file}")
    print(f"\n💡 Next steps:")
    print(f"   1. Test the package by extracting and following INSTALLATION_GUIDE.md")
    print(f"   2. Upload to your distribution platform")
    print(f"   3. Share with customers or team members")