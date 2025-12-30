# APK Packaging Guide for Self-Evolving AI Framework

This guide covers how to package the Self-Evolving AI Framework as an Android APK for distribution on Shopify or other mobile platforms.

## Options Overview

| Tool | Best For | Complexity | Native Feel |
|------|----------|------------|-------------|
| **Kivy + Buildozer** | Custom UI, Games | Medium | Custom |
| **BeeWare + Briefcase** | Native UI Apps | Medium | Native |
| **Chaquopy** | Android Studio Integration | High | Native |

## Recommended: Kivy + Buildozer

Best for our use case - provides full control over UI and works well with Python backend logic.

### Prerequisites

```bash
# Linux/WSL required for building
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-setuptools git zip unzip openjdk-17-jdk

# Install Buildozer
pip install buildozer cython kivy
```

### Project Structure for APK

```
shopify_ai_app/
├── main.py                 # Entry point (required name)
├── buildozer.spec          # Build configuration
├── self_evolving_core/     # Copy framework here
│   ├── __init__.py
│   ├── models.py
│   ├── framework.py
│   └── ...
└── assets/
    └── icon.png
```


### Sample main.py for Kivy App

```python
"""
Shopify AI Manager - Mobile App
Built with Kivy + Self-Evolving AI Framework
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from self_evolving_core import EvolvingAIFramework


class ShopifyAIApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.framework = EvolvingAIFramework()
    
    def build(self):
        self.framework.initialize()
        
        layout = BoxLayout(orientation='vertical', padding=10)
        
        # Status display
        status = self.framework.get_status()
        layout.add_widget(Label(
            text=f"AI Framework v{status['version']}",
            size_hint_y=0.1
        ))
        layout.add_widget(Label(
            text=f"Generation: {status['dna']['generation']} | Fitness: {status['dna']['fitness_score']:.1f}",
            size_hint_y=0.1
        ))
        
        # Action buttons
        btn_status = Button(text="Refresh Status", size_hint_y=0.15)
        btn_status.bind(on_press=self.refresh_status)
        layout.add_widget(btn_status)
        
        btn_sync = Button(text="Sync Data", size_hint_y=0.15)
        btn_sync.bind(on_press=self.sync_data)
        layout.add_widget(btn_sync)
        
        return layout
    
    def refresh_status(self, instance):
        status = self.framework.get_status()
        print(f"Status: {status}")
    
    def sync_data(self, instance):
        result = self.framework.sync_storage({"mobile": True}, "mobile_sync.json")
        print(f"Sync: {result}")


if __name__ == '__main__':
    ShopifyAIApp().run()
```

### buildozer.spec Configuration

```ini
[app]
title = Shopify AI Manager
package.name = shopifyai
package.domain = com.yourcompany
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

# Requirements
requirements = python3,kivy,requests,pyyaml

# Android specific
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.arch = arm64-v8a

# Build settings
[buildozer]
log_level = 2
warn_on_root = 1
```

### Build Commands

```bash
# Initialize buildozer (creates buildozer.spec)
buildozer init

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release

# Deploy to connected device
buildozer android deploy run
```

## Alternative: BeeWare + Briefcase

Better for native Android look and feel.

```bash
# Install BeeWare
pip install briefcase toga

# Create new project
briefcase new

# Build for Android
briefcase create android
briefcase build android
briefcase package android
```

## For Shopify App Store

1. Build release APK with signing key
2. Create Google Play Developer account ($25 one-time)
3. Submit to Google Play Store
4. Link from Shopify App Store listing

## Quick Start Checklist

- [ ] Set up Linux/WSL environment
- [ ] Install Java JDK 17+
- [ ] Install Android SDK
- [ ] Copy self_evolving_core to project
- [ ] Create main.py with Kivy UI
- [ ] Configure buildozer.spec
- [ ] Build and test on emulator
- [ ] Sign APK for release
- [ ] Submit to app stores
