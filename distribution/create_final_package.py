#!/usr/bin/env python3
"""
Final Distribution Package Creator - Windows Compatible
Creates a downloadable package of the AI Workflow System
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
import fnmatch

def should_exclude(file_path):
    """Check if a file should be excluded"""
    exclude_items = [
        '__pycache__',
        '.pytest_cache',
        '.hypothesis',
        'node_modules',
        '.git',
        '.pyc',
        '.pyo',
        '.pyd',
        '.DS_Store',
        'Thumbs.db',
        '.log',
        '.coverage',
        'htmlcov',
        '.mypy_cache',
        '.ruff_cache',
        'dist',
        'build',
        '.egg-info',
        '.venv',
        'venv',
        'env',
        '.env',
        '.sqlite3',
        '.db',
        'snapshots',
        'logs'
    ]
    
    # Check if any part of the path contains excluded items
    path_parts = Path(file_path).parts
    for part in path_parts:
        for exclude_item in exclude_items:
            if exclude_item in part.lower():
                return True
    
    return False

def create_final_package():
    """Create a final distribution package"""
    
    # Create package directory with shorter name
    package_name = f"ai-workflow-{datetime.now().strftime('%Y%m%d_%H%M')}"
    package_dir = Path(package_name)
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    print(f"Creating distribution package: {package_name}")
    
    # Define key files and directories to include
    include_patterns = [
        # Core Python files
        'requirements.txt',
        '*.py',
        
        # Documentation
        '*.md',
        
        # Configuration
        '.kiro/steering/*.md',
        '.env.example',
        
        # Core app-productizer files
        'app-productizer/*.py',
        'app-productizer/*.md',
        'app-productizer/*.txt',
        'app-productizer/*.json',
        'app-productizer/*.yml',
        'app-productizer/*.yaml',
        'app-productizer/self_evolving_core/*.py',
        'app-productizer/tests/*.py',
        
        # Bridge API
        'bridge-api/src/**/*.ts',
        'bridge-api/package.json',
        'bridge-api/*.md',
        
        # AI Workflow Architect (key files only)
        'projects_review/AI-Workflow-Architect/package.json',
        'projects_review/AI-Workflow-Architect/client/src/**/*.tsx',
        'projects_review/AI-Workflow-Architect/client/src/**/*.ts',
        'projects_review/AI-Workflow-Architect/server/**/*.ts',
        'projects_review/AI-Workflow-Architect/shared/**/*.ts',
        
        # Business apps
        'business-apps/**/*.py',
        'business-apps/**/*.md',
        
        # Sellable packages
        'SELLABLE_PACKAGES/**/*',
        
        # Tests
        'tests/*.py',
        'test_*.py',
    ]
    
    copied_files = []
    total_size = 0
    
    # Copy files based on patterns
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, '.').replace('\\', '/')
            
            # Skip if excluded
            if should_exclude(relative_path):
                continue
            
            # Check if matches include patterns
            should_include = False
            for pattern in include_patterns:
                if fnmatch.fnmatch(relative_path, pattern):
                    should_include = True
                    break
            
            if not should_include:
                continue
            
            # Skip very large files
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    continue
            except:
                continue
            
            # Create shorter destination path
            dest_relative = relative_path
            if len(dest_relative) > 200:  # Windows path limit safety
                continue
                
            dest_path = package_dir / dest_relative
            
            # Create destination directory
            try:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                continue  # Skip if path too long
            
            # Copy file
            try:
                shutil.copy2(file_path, dest_path)
                copied_files.append(relative_path)
                total_size += file_size
            except Exception as e:
                print(f"Skipped {relative_path}: {e}")
                continue
    
    # Create package info
    package_info = {
        "name": "AI Workflow System",
        "version": "1.0.0",
        "created": datetime.now().isoformat(),
        "files": len(copied_files),
        "size_mb": round(total_size / (1024 * 1024), 2),
        "components": [
            "Self-Evolving AI Framework",
            "AI Workflow Architect",
            "Bridge API",
            "Business Applications",
            "Documentation"
        ]
    }
    
    with open(package_dir / "package_info.json", 'w', encoding='utf-8') as f:
        json.dump(package_info, f, indent=2)
    
    # Create simple README
    readme_content = f"""# AI Workflow System Distribution Package

## Quick Start

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the AI system:
   ```
   cd app-productizer
   python evolving_ai_main.py
   ```

3. Start web interface:
   ```
   cd app-productizer  
   python web_interface.py
   ```

## Package Contents

- **Files**: {len(copied_files)}
- **Size**: {package_info['size_mb']} MB
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Components

- Self-Evolving AI Framework (app-productizer/)
- AI Workflow Architect (projects_review/)
- Bridge API (bridge-api/)
- Documentation (*.md files)
- Tests and utilities

## Support

See the included documentation files for detailed setup instructions.
"""
    
    with open(package_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create ZIP file
    zip_filename = f"{package_name}.zip"
    print(f"Creating ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir.parent)
                zipf.write(file_path, arcname)
    
    # Clean up
    shutil.rmtree(package_dir)
    
    # Summary
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    print(f"\n✅ Package created successfully!")
    print(f"📦 File: {zip_filename}")
    print(f"📁 Files: {len(copied_files)}")
    print(f"📊 Size: {zip_size:.1f} MB")
    
    # Show key components
    components = {}
    for file_path in copied_files:
        if file_path.startswith('app-productizer/'):
            components['AI Framework'] = components.get('AI Framework', 0) + 1
        elif file_path.startswith('projects_review/'):
            components['Workflow Architect'] = components.get('Workflow Architect', 0) + 1
        elif file_path.startswith('bridge-api/'):
            components['Bridge API'] = components.get('Bridge API', 0) + 1
        elif file_path.endswith('.md'):
            components['Documentation'] = components.get('Documentation', 0) + 1
        elif 'test' in file_path:
            components['Tests'] = components.get('Tests', 0) + 1
    
    print(f"\n📋 Components:")
    for component, count in components.items():
        print(f"  ✓ {component}: {count} files")
    
    return zip_filename

if __name__ == "__main__":
    package_file = create_final_package()
    print(f"\n🎉 Distribution ready: {package_file}")