#!/usr/bin/env python3
"""
Distribution Package Creator
Creates a comprehensive downloadable package of the AI Workflow System
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
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True
    return False

def create_distribution_package():
    """Create a comprehensive distribution package"""
    
    # Define what to exclude (based on .gitignore and additional patterns)
    exclude_patterns = [
        '__pycache__/*',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'build/*',
        'dist/*',
        '*.egg-info/*',
        '.venv/*',
        'venv/*',
        'env/*',
        '.env',
        '.git/*',
        '.pytest_cache/*',
        '.hypothesis/*',
        '*.log',
        '.coverage',
        'htmlcov/*',
        '.mypy_cache/*',
        '.ruff_cache/*',
        'node_modules/*',
        '.DS_Store',
        'Thumbs.db',
        '*.tmp',
        '*.temp',
        '.vscode/settings.json',  # Keep workspace settings but not personal ones
        '.idea/*',
        '*.sqlite3',
        '*.db',
        'logs/*.json',  # Exclude log files but keep the structure
        'AI_NETWORK_LOCAL/snapshots/*',  # Exclude snapshots but keep structure
    ]
    
    # Define essential directories and files to include
    essential_paths = [
        # Core application
        'app-productizer/',
        'bridge-api/',
        
        # AI Workflow Architect projects
        'projects_review/AI-Workflow-Architect/',
        'projects_review/AI-Workflow-Architect.01.01.02/',
        
        # Business applications
        'business-apps/',
        
        # Configuration and documentation
        '.kiro/',
        'docs/',
        
        # Sellable packages
        'SELLABLE_PACKAGES/',
        'gumroad-products/',
        
        # Scripts and utilities
        'create_sellable_packages.py',
        'create_sellable_template.py',
        'deploy_ai_workflow_architect.py',
        'repo_audit.py',
        'test_unified_system.py',
        
        # Requirements and configuration
        'requirements.txt',
        'LICENSE',
        'LICENSE.md',
        
        # Documentation files
        '*.md',
        
        # CI/CD and deployment
        'ci_cd/',
        'deployment/',
        'production/',
        'monitoring/',
        
        # Tests
        'tests/',
        
        # Stable releases
        'stable/',
    ]
    
    # Create package directory
    package_name = f"ai-workflow-system-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = Path(package_name)
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    print(f"Creating distribution package: {package_name}")
    
    # Copy essential files and directories
    copied_files = []
    skipped_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and excluded patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.kiro', '.github']]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, '.')
            
            # Skip if matches exclude patterns
            if should_exclude(relative_path, exclude_patterns):
                skipped_files.append(relative_path)
                continue
            
            # Check if file is in essential paths or matches patterns
            should_include = False
            
            # Include all .md files at root level
            if file.endswith('.md') and root == '.':
                should_include = True
            
            # Include files in essential directories
            for essential_path in essential_paths:
                if essential_path.endswith('/'):
                    if relative_path.startswith(essential_path):
                        should_include = True
                        break
                else:
                    if relative_path == essential_path or relative_path.startswith(essential_path + '/'):
                        should_include = True
                        break
            
            if should_include:
                # Create destination directory
                dest_path = package_dir / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                try:
                    shutil.copy2(file_path, dest_path)
                    copied_files.append(relative_path)
                except Exception as e:
                    print(f"Error copying {relative_path}: {e}")
                    skipped_files.append(relative_path)
    
    # Create package manifest
    manifest = {
        "package_name": package_name,
        "created_at": datetime.now().isoformat(),
        "total_files": len(copied_files),
        "skipped_files": len(skipped_files),
        "description": "AI Workflow System - Complete Distribution Package",
        "version": "1.0.0",
        "components": [
            "Self-Evolving AI Framework",
            "AI Workflow Architect",
            "Bridge API Integration",
            "Business Applications",
            "Sellable Packages",
            "Documentation & Guides"
        ]
    }
    
    with open(package_dir / "PACKAGE_MANIFEST.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create installation guide
    install_guide = """# AI Workflow System - Installation Guide

## Package Contents

This package contains the complete AI Workflow System including:

- **Self-Evolving AI Framework** (`app-productizer/`)
- **AI Workflow Architect** (`projects_review/AI-Workflow-Architect/`)
- **Bridge API Integration** (`bridge-api/`)
- **Business Applications** (`business-apps/`)
- **Sellable Packages** (`SELLABLE_PACKAGES/`)
- **Documentation & Guides** (Various .md files)

## Quick Start

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Self-Evolving AI System**:
   ```bash
   cd app-productizer
   python evolving_ai_main.py
   ```

3. **Start the Web Interface**:
   ```bash
   cd app-productizer
   python web_interface.py
   ```

4. **Access the AI Workflow Architect**:
   ```bash
   cd projects_review/AI-Workflow-Architect
   npm install
   npm run dev
   ```

## Configuration

1. Copy `.env.example` to `.env` and configure your settings
2. Set up your AI provider API keys
3. Configure database connections if needed

## Documentation

- `README.md` - Main project overview
- `COMPLETE_COMMERCIALIZATION_GUIDE.md` - Business deployment guide
- `ENTERPRISE_DEPLOYMENT_GUIDE.md` - Enterprise setup
- `TECHNICAL_ARCHITECTURE_OVERVIEW.md` - Technical details

## Support

For support and updates, visit the project repository or contact support.

---
Package created: {created_at}
Total files: {total_files}
""".format(
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_files=len(copied_files)
    )
    
    with open(package_dir / "INSTALLATION_GUIDE.md", 'w') as f:
        f.write(install_guide)
    
    # Create ZIP archive
    zip_filename = f"{package_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir.parent)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    # Print summary
    print(f"\n✅ Distribution package created successfully!")
    print(f"📦 Package: {zip_filename}")
    print(f"📁 Files included: {len(copied_files)}")
    print(f"⏭️  Files skipped: {len(skipped_files)}")
    print(f"📊 Package size: {os.path.getsize(zip_filename) / (1024*1024):.1f} MB")
    
    # Show some key included files
    print(f"\n📋 Key components included:")
    key_components = [
        'app-productizer/evolving_ai_main.py',
        'app-productizer/web_interface.py',
        'bridge-api/src/',
        'projects_review/AI-Workflow-Architect/',
        'SELLABLE_PACKAGES/',
        'requirements.txt',
        'README.md'
    ]
    
    for component in key_components:
        matching_files = [f for f in copied_files if f.startswith(component)]
        if matching_files:
            print(f"  ✓ {component} ({len(matching_files)} files)")
    
    return zip_filename

if __name__ == "__main__":
    package_file = create_distribution_package()
    print(f"\n🎉 Ready to distribute: {package_file}")