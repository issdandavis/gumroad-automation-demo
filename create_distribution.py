#!/usr/bin/env python3
"""
Create Distribution Package for AgentCore Demo
Creates a clean, commercial-ready package for distribution
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_distribution_package():
    """Create a clean distribution package"""
    
    # Package info
    package_name = "agentcore-demo-v1.0.0"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create distribution directory
    dist_dir = Path(f"dist/{package_name}")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include in distribution
    files_to_copy = [
        "agentcore_demo/agent.py",
        "agentcore_demo/requirements.txt",
        "agentcore_demo/setup.py",
        "agentcore_demo/README.md",
        "agentcore_demo/LICENSE",
        "agentcore_demo/DEPLOYMENT_GUIDE.md",
        "agentcore_demo/COMMERCIAL_PACKAGE.md",
        "agentcore_demo/.env.example",
        "agentcore_demo/tests/__init__.py",
        "agentcore_demo/tests/test_agent.py",
        "agentcore_demo/validate_package.py"
    ]
    
    # Copy files to distribution
    print("📦 Creating distribution package...")
    
    for file_path in files_to_copy:
        src = Path(file_path)
        if src.exists():
            # Maintain directory structure
            rel_path = src.relative_to("agentcore_demo")
            dest = dist_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"✅ Copied: {rel_path}")
        else:
            print(f"⚠️  Missing: {file_path}")
    
    # Create additional distribution files
    create_quick_start_guide(dist_dir)
    create_version_info(dist_dir)
    
    # Create ZIP archive
    zip_path = f"dist/{package_name}_{timestamp}.zip"
    create_zip_archive(dist_dir, zip_path)
    
    print(f"\n🎉 Distribution package created: {zip_path}")
    print(f"📁 Package directory: {dist_dir}")
    
    return zip_path, dist_dir

def create_quick_start_guide(dist_dir):
    """Create a quick start guide for customers"""
    
    quick_start = """# AgentCore Demo - Quick Start

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test Locally
```bash
python agent.py
```

### 3. Configure for AWS
```bash
agentcore configure --entrypoint agent.py --non-interactive
```

### 4. Deploy to AWS
```bash
agentcore deploy
```

### 5. Test Your Deployed Agent
```bash
agentcore invoke "Hello, AgentCore!"
```

## 📚 Next Steps

1. Read `README.md` for detailed information
2. Follow `DEPLOYMENT_GUIDE.md` for production setup
3. Run tests with `python -m pytest tests/`
4. Customize the agent in `agent.py`

## 🆘 Need Help?

- Check `DEPLOYMENT_GUIDE.md` for troubleshooting
- Email: support@aiworkflow.com
- 30-day money-back guarantee

---

**You're ready to build production AI agents with AgentCore!**
"""
    
    with open(dist_dir / "QUICK_START.md", "w", encoding="utf-8") as f:
        f.write(quick_start)
    
    print("✅ Created: QUICK_START.md")

def create_version_info(dist_dir):
    """Create version and package information"""
    
    version_info = {
        "package_name": "AgentCore Demo",
        "version": "1.0.0",
        "release_date": datetime.now().isoformat(),
        "license": "MIT",
        "author": "AI Workflow Systems",
        "description": "Production-ready AgentCore agent template",
        "requirements": {
            "python": ">=3.10",
            "aws_cli": ">=2.0",
            "agentcore": ">=0.2.5"
        },
        "features": [
            "Complete agent implementation",
            "AWS AgentCore integration",
            "Comprehensive test suite",
            "Production deployment ready",
            "Commercial license included"
        ],
        "support": {
            "email": "support@aiworkflow.com",
            "documentation": "README.md",
            "deployment_guide": "DEPLOYMENT_GUIDE.md",
            "guarantee": "30-day money-back"
        }
    }
    
    import json
    with open(dist_dir / "package_info.json", "w", encoding="utf-8") as f:
        json.dump(version_info, f, indent=2)
    
    print("✅ Created: package_info.json")

def create_zip_archive(source_dir, zip_path):
    """Create ZIP archive of the distribution"""
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created ZIP: {zip_path}")

def validate_distribution(dist_dir):
    """Validate the distribution package"""
    
    print("\n🔍 Validating distribution package...")
    
    required_files = [
        "agent.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "QUICK_START.md",
        "package_info.json"
    ]
    
    all_valid = True
    for file_name in required_files:
        file_path = dist_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ Missing: {file_name}")
            all_valid = False
    
    return all_valid

if __name__ == "__main__":
    print("🏭 AgentCore Demo - Distribution Package Creator")
    print("=" * 50)
    
    try:
        zip_path, dist_dir = create_distribution_package()
        
        if validate_distribution(dist_dir):
            print("\n✅ Distribution package is valid and ready for sale!")
            print(f"\n📦 Package Details:")
            print(f"   • ZIP File: {zip_path}")
            print(f"   • Size: {os.path.getsize(zip_path) / 1024:.1f} KB")
            print(f"   • Files: {len(list(dist_dir.rglob('*')))} total")
            
            print(f"\n🚀 Ready for Commercial Distribution:")
            print(f"   • Upload to marketplace")
            print(f"   • Set price: $97")
            print(f"   • Enable instant download")
            print(f"   • Activate payment processing")
        else:
            print("\n❌ Distribution package validation failed!")
            
    except Exception as e:
        print(f"\n❌ Error creating distribution: {e}")
        import traceback
        traceback.print_exc()