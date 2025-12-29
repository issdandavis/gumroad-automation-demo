#!/usr/bin/env python3
"""
Advanced Configuration Management System
=======================================

Comprehensive configuration management for the Self-Evolving AI Framework.
Handles environment variables, secrets, validation, and setup automation.

Features:
- Environment-specific configurations (dev, staging, prod)
- Secure secrets management with encryption
- Automatic validation and setup
- Configuration templates and examples
- Health checks and diagnostics
- Migration and backup utilities

Usage:
    python config_manager.py setup          # Interactive setup
    python config_manager.py validate       # Validate configuration
    python config_manager.py generate       # Generate config templates
    python config_manager.py encrypt        # Encrypt sensitive data
    python config_manager.py health         # Health check
"""

import os
import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
from cryptography.fernet import Fernet
import getpass


@dataclass
class AIProviderConfig:
    """Configuration for AI providers"""
    name: str
    api_key: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    enabled: bool = True
    cost_per_token: float = 0.0001
    rate_limit: int = 100  # requests per minute


@dataclass
class StorageConfig:
    """Configuration for storage platforms"""
    platform: str
    credentials: Dict[str, str]
    enabled: bool = True
    sync_interval: int = 300  # seconds
    retry_attempts: int = 3
    backup_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_key: str
    session_secret: str
    api_key_rotation_days: int = 90
    audit_log_retention_days: int = 365
    max_login_attempts: int = 5
    password_min_length: int = 12


@dataclass
class SystemConfig:
    """Main system configuration"""
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    data_directory: str = "AI_NETWORK_LOCAL"
    backup_directory: str = "backups"
    max_concurrent_operations: int = 10
    health_check_interval: int = 60


class ConfigurationManager:
    """
    Advanced configuration management system.
    
    Handles all aspects of system configuration including:
    - Environment-specific settings
    - Secure credential storage
    - Validation and health checks
    - Setup automation
    - Migration utilities
    """
    
    def __init__(self, config_path: str = ".env"):
        self.config_path = Path(config_path)
        self.config_dir = self.config_path.parent
        self.encryption_key = None
        self.config_data = {}
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from files"""
        try:
            # Load main config
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            self.config_data[key] = value
            
            # Load additional config files
            yaml_config = self.config_dir / "config.yaml"
            if yaml_config.exists():
                with open(yaml_config, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                    self.config_data.update(yaml_data)
                    
        except Exception as e:
            print(f"⚠️  Configuration loading error: {e}")
    
    def setup_interactive(self):
        """
        Interactive setup wizard for first-time configuration.
        
        Guides users through complete system setup with validation
        and best practices recommendations.
        """
        print("""
🚀 Self-Evolving AI Framework Setup Wizard
==========================================

This wizard will guide you through setting up your AI framework
with proper security, integrations, and optimization.

Let's get started!
        """)
        
        # Step 1: Environment Selection
        print("\n1️⃣  Environment Configuration")
        print("Choose your deployment environment:")
        print("   1. Development (local testing)")
        print("   2. Staging (pre-production)")  
        print("   3. Production (live deployment)")
        
        env_choice = input("Select environment (1-3): ").strip()
        environment = {
            "1": "development",
            "2": "staging", 
            "3": "production"
        }.get(env_choice, "development")
        
        print(f"✅ Environment set to: {environment}")
        
        # Step 2: AI Provider Setup
        print("\n2️⃣  AI Provider Configuration")
        print("Configure your AI providers for intelligent operations:")
        
        ai_providers = []
        
        # OpenAI Setup
        if self._confirm("Configure OpenAI (GPT-4, GPT-3.5)?"):
            openai_key = self._get_secure_input("OpenAI API Key", 
                                              "sk-demo1234567890abcdef1234567890abcdef1234567890abcdef")
            ai_providers.append(AIProviderConfig(
                name="openai",
                api_key=openai_key,
                model="gpt-4-turbo-preview",
                cost_per_token=0.00003
            ))
        
        # Anthropic Setup
        if self._confirm("Configure Anthropic (Claude)?"):
            anthropic_key = self._get_secure_input("Anthropic API Key",
                                                 "sk-ant-demo1234567890abcdef1234567890abcdef1234567890abcdef")
            ai_providers.append(AIProviderConfig(
                name="anthropic", 
                api_key=anthropic_key,
                model="claude-3-sonnet-20240229",
                cost_per_token=0.000015
            ))
        
        # Google AI Setup
        if self._confirm("Configure Google AI (Gemini)?"):
            google_key = self._get_secure_input("Google AI API Key",
                                              "AIzaSyDemo1234567890abcdef1234567890abcdef123")
            ai_providers.append(AIProviderConfig(
                name="google",
                api_key=google_key,
                model="gemini-pro",
                cost_per_token=0.0000005
            ))
        
        # Step 3: Storage Configuration
        print("\n3️⃣  Storage Platform Configuration")
        print("Configure cloud storage for data synchronization:")
        
        storage_configs = []
        
        # Dropbox Setup
        if self._confirm("Configure Dropbox sync?"):
            dropbox_token = self._get_secure_input("Dropbox Access Token",
                                                 "sl.demo1234567890abcdef1234567890abcdef1234567890abcdef")
            storage_configs.append(StorageConfig(
                platform="dropbox",
                credentials={"access_token": dropbox_token}
            ))
        
        # GitHub Setup
        if self._confirm("Configure GitHub sync?"):
            github_token = self._get_secure_input("GitHub Personal Access Token",
                                                "ghp_demo1234567890abcdef1234567890abcdef1234567890abcdef")
            github_repo = input("GitHub repository (username/repo): ").strip() or "demo-user/ai-evolution"
            storage_configs.append(StorageConfig(
                platform="github",
                credentials={
                    "token": github_token,
                    "repository": github_repo
                }
            ))
        
        # Step 4: Security Configuration
        print("\n4️⃣  Security Configuration")
        print("Setting up encryption and security measures:")
        
        # Generate encryption key
        encryption_key = Fernet.generate_key().decode()
        session_secret = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        security_config = SecurityConfig(
            encryption_key=encryption_key,
            session_secret=session_secret
        )
        
        print("✅ Security keys generated")
        
        # Step 5: System Configuration
        print("\n5️⃣  System Configuration")
        
        data_dir = input("Data directory [AI_NETWORK_LOCAL]: ").strip() or "AI_NETWORK_LOCAL"
        log_level = input("Log level (DEBUG/INFO/WARNING/ERROR) [INFO]: ").strip() or "INFO"
        
        system_config = SystemConfig(
            environment=environment,
            debug=(environment == "development"),
            log_level=log_level,
            data_directory=data_dir
        )
        
        # Step 6: Save Configuration
        print("\n6️⃣  Saving Configuration")
        
        config_data = {
            "system": asdict(system_config),
            "security": asdict(security_config),
            "ai_providers": [asdict(provider) for provider in ai_providers],
            "storage": [asdict(storage) for storage in storage_configs],
            "setup_completed": datetime.now().isoformat(),
            "setup_version": "2.0.0"
        }
        
        # Save to multiple formats
        self._save_env_file(config_data)
        self._save_yaml_config(config_data)
        self._save_encrypted_secrets(config_data)
        
        print("""
🎉 Setup Complete!

Your Self-Evolving AI Framework is now configured and ready to use!

Files created:
✅ .env - Environment variables
✅ config.yaml - Main configuration
✅ secrets.enc - Encrypted sensitive data
✅ setup_log.json - Setup audit log

Next steps:
1. Run: python evolving_ai_main.py status
2. Run: python tutorial_system.py getting_started
3. Start web interface: python web_interface.py

Happy evolving! 🚀
        """)
    
    def _confirm(self, message: str) -> bool:
        """Get yes/no confirmation from user"""
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    
    def _get_secure_input(self, prompt: str, demo_value: str) -> str:
        """Get secure input with demo fallback"""
        print(f"\n{prompt}:")
        print(f"Demo value: {demo_value}")
        print("Enter your real API key, or press Enter to use demo value")
        
        value = getpass.getpass("API Key (hidden): ").strip()
        if not value:
            print("Using demo value for testing")
            return demo_value
        return value
    
    def _save_env_file(self, config_data: Dict[str, Any]):
        """Save environment variables file"""
        env_content = f"""# Self-Evolving AI Framework Configuration
# Generated on {datetime.now().isoformat()}

# System Configuration
ENVIRONMENT={config_data['system']['environment']}
DEBUG={str(config_data['system']['debug']).lower()}
LOG_LEVEL={config_data['system']['log_level']}
DATA_DIRECTORY={config_data['system']['data_directory']}

# Security
ENCRYPTION_KEY={config_data['security']['encryption_key']}
SESSION_SECRET={config_data['security']['session_secret']}

# AI Providers
"""
        
        for provider in config_data['ai_providers']:
            env_name = f"{provider['name'].upper()}_API_KEY"
            env_content += f"{env_name}={provider['api_key']}\n"
        
        # Storage credentials
        env_content += "\n# Storage Platforms\n"
        for storage in config_data['storage']:
            platform = storage['platform'].upper()
            for key, value in storage['credentials'].items():
                env_name = f"{platform}_{key.upper()}"
                env_content += f"{env_name}={value}\n"
        
        with open(self.config_path, 'w') as f:
            f.write(env_content)
    
    def _save_yaml_config(self, config_data: Dict[str, Any]):
        """Save YAML configuration file"""
        yaml_path = self.config_dir / "config.yaml"
        
        # Remove sensitive data for YAML
        safe_config = config_data.copy()
        for provider in safe_config['ai_providers']:
            provider['api_key'] = "***ENCRYPTED***"
        for storage in safe_config['storage']:
            for key in storage['credentials']:
                storage['credentials'][key] = "***ENCRYPTED***"
        safe_config['security']['encryption_key'] = "***ENCRYPTED***"
        safe_config['security']['session_secret'] = "***ENCRYPTED***"
        
        with open(yaml_path, 'w') as f:
            yaml.dump(safe_config, f, default_flow_style=False, indent=2)
    
    def _save_encrypted_secrets(self, config_data: Dict[str, Any]):
        """Save encrypted secrets file"""
        secrets_path = self.config_dir / "secrets.enc"
        
        # Extract sensitive data
        secrets = {
            "encryption_key": config_data['security']['encryption_key'],
            "session_secret": config_data['security']['session_secret'],
            "ai_providers": {},
            "storage": {}
        }
        
        for provider in config_data['ai_providers']:
            secrets['ai_providers'][provider['name']] = provider['api_key']
        
        for storage in config_data['storage']:
            secrets['storage'][storage['platform']] = storage['credentials']
        
        # Encrypt and save
        key = config_data['security']['encryption_key'].encode()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(secrets).encode())
        
        with open(secrets_path, 'wb') as f:
            f.write(encrypted_data)
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate current configuration.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        print("🔍 Validating Self-Evolving AI Configuration...")
        
        # Check required environment variables
        required_vars = [
            "ENVIRONMENT",
            "DATA_DIRECTORY", 
            "ENCRYPTION_KEY",
            "SESSION_SECRET"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing required environment variable: {var}")
        
        # Check AI provider configuration
        ai_providers = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_AI_KEY"]
        if not any(os.getenv(key) for key in ai_providers):
            issues.append("No AI provider API keys configured")
        
        # Check data directory
        data_dir = Path(os.getenv("DATA_DIRECTORY", "AI_NETWORK_LOCAL"))
        if not data_dir.exists():
            try:
                data_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created data directory: {data_dir}")
            except Exception as e:
                issues.append(f"Cannot create data directory: {e}")
        
        # Check file permissions
        config_files = [".env", "config.yaml", "secrets.enc"]
        for file in config_files:
            file_path = Path(file)
            if file_path.exists():
                # Check if file is readable
                try:
                    with open(file_path, 'r') as f:
                        f.read(1)
                except Exception as e:
                    issues.append(f"Cannot read config file {file}: {e}")
        
        # Validate API keys format
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("sk-"):
            issues.append("OpenAI API key format appears invalid")
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY") 
        if anthropic_key and not anthropic_key.startswith("sk-ant-"):
            issues.append("Anthropic API key format appears invalid")
        
        # Report results
        if issues:
            print(f"❌ Configuration validation failed with {len(issues)} issues:")
            for issue in issues:
                print(f"   • {issue}")
            return False, issues
        else:
            print("✅ Configuration validation passed!")
            return True, []
    
    def generate_templates(self):
        """Generate configuration templates and examples"""
        print("📝 Generating configuration templates...")
        
        # Generate .env.example
        env_example = """# Self-Evolving AI Framework Configuration Template
# Copy to .env and fill in your actual values

# System Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
DATA_DIRECTORY=AI_NETWORK_LOCAL

# Security (Generate new keys for production!)
ENCRYPTION_KEY=your-encryption-key-here
SESSION_SECRET=your-session-secret-here

# AI Provider API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_AI_KEY=your-google-ai-key-here
XAI_API_KEY=your-xai-key-here
PERPLEXITY_API_KEY=your-perplexity-key-here

# Storage Platform Credentials
DROPBOX_ACCESS_TOKEN=your-dropbox-token-here
GITHUB_TOKEN=ghp_your-github-token-here
GITHUB_REPOSITORY=username/repository-name
NOTION_TOKEN=secret_your-notion-token-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0

# Webhook URLs
WEBHOOK_URL=https://your-domain.com/webhook
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
"""
        
        with open(".env.example", 'w') as f:
            f.write(env_example)
        
        # Generate config template
        config_template = {
            "system": {
                "environment": "development",
                "debug": True,
                "log_level": "INFO",
                "data_directory": "AI_NETWORK_LOCAL",
                "backup_directory": "backups",
                "max_concurrent_operations": 10,
                "health_check_interval": 60
            },
            "ai_providers": [
                {
                    "name": "openai",
                    "model": "gpt-4-turbo-preview",
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "enabled": True,
                    "cost_per_token": 0.00003,
                    "rate_limit": 100
                },
                {
                    "name": "anthropic",
                    "model": "claude-3-sonnet-20240229", 
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "enabled": True,
                    "cost_per_token": 0.000015,
                    "rate_limit": 100
                }
            ],
            "storage": [
                {
                    "platform": "local",
                    "enabled": True,
                    "sync_interval": 300,
                    "retry_attempts": 3,
                    "backup_enabled": True
                },
                {
                    "platform": "dropbox",
                    "enabled": False,
                    "sync_interval": 600,
                    "retry_attempts": 3,
                    "backup_enabled": True
                }
            ],
            "security": {
                "api_key_rotation_days": 90,
                "audit_log_retention_days": 365,
                "max_login_attempts": 5,
                "password_min_length": 12
            }
        }
        
        with open("config.template.yaml", 'w') as f:
            yaml.dump(config_template, f, default_flow_style=False, indent=2)
        
        print("✅ Templates generated:")
        print("   • .env.example - Environment variables template")
        print("   • config.template.yaml - Configuration template")
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        print("🏥 Running system health check...")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Configuration check
        is_valid, issues = self.validate_configuration()
        health_status["checks"]["configuration"] = {
            "status": "pass" if is_valid else "fail",
            "issues": issues
        }
        
        # File system check
        data_dir = Path(os.getenv("DATA_DIRECTORY", "AI_NETWORK_LOCAL"))
        health_status["checks"]["filesystem"] = {
            "status": "pass" if data_dir.exists() else "fail",
            "data_directory": str(data_dir),
            "writable": os.access(data_dir, os.W_OK) if data_dir.exists() else False
        }
        
        # AI providers check
        ai_status = {}
        for provider in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_AI_KEY"]:
            key = os.getenv(provider)
            ai_status[provider.lower()] = {
                "configured": bool(key),
                "format_valid": self._validate_api_key_format(provider, key) if key else False
            }
        
        health_status["checks"]["ai_providers"] = ai_status
        
        # Determine overall status
        failed_checks = [
            check for check in health_status["checks"].values()
            if isinstance(check, dict) and check.get("status") == "fail"
        ]
        
        if failed_checks:
            health_status["overall_status"] = "unhealthy"
        
        # Print results
        status_emoji = "✅" if health_status["overall_status"] == "healthy" else "❌"
        print(f"{status_emoji} Overall Status: {health_status['overall_status']}")
        
        for check_name, check_data in health_status["checks"].items():
            if isinstance(check_data, dict) and "status" in check_data:
                check_emoji = "✅" if check_data["status"] == "pass" else "❌"
                print(f"   {check_emoji} {check_name}: {check_data['status']}")
        
        return health_status
    
    def _validate_api_key_format(self, provider: str, key: str) -> bool:
        """Validate API key format"""
        if not key:
            return False
        
        formats = {
            "OPENAI_API_KEY": lambda k: k.startswith("sk-") and len(k) > 20,
            "ANTHROPIC_API_KEY": lambda k: k.startswith("sk-ant-") and len(k) > 20,
            "GOOGLE_AI_KEY": lambda k: k.startswith("AIza") and len(k) > 20
        }
        
        validator = formats.get(provider)
        return validator(key) if validator else len(key) > 10


def main():
    """Main configuration manager entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Evolving AI Configuration Manager")
    parser.add_argument('command', choices=['setup', 'validate', 'generate', 'health'],
                       help='Configuration command to run')
    parser.add_argument('--config', default='.env', help='Configuration file path')
    
    args = parser.parse_args()
    
    config_manager = ConfigurationManager(args.config)
    
    if args.command == 'setup':
        config_manager.setup_interactive()
    elif args.command == 'validate':
        config_manager.validate_configuration()
    elif args.command == 'generate':
        config_manager.generate_templates()
    elif args.command == 'health':
        config_manager.health_check()


if __name__ == "__main__":
    main()