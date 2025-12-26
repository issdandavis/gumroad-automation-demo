"""
Configuration Management for Self-Evolving AI Framework
=======================================================

Flexible configuration system supporting:
- Environment variables
- YAML/JSON config files
- Runtime updates without restart
- Environment-specific configs (dev/staging/prod)
- Validation and defaults
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Storage platform configuration"""
    local_path: str = "AI_NETWORK_LOCAL"
    dropbox_token: str = ""
    dropbox_app_folder: str = "/AI_Network"
    github_token: str = ""
    github_repo: str = "ai-evolution-hub"
    github_owner: str = ""
    notion_token: str = ""
    notion_database_id: str = ""
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    sync_interval_seconds: int = 60
    max_retries: int = 5
    retry_backoff_base: float = 2.0
    retry_backoff_max: float = 300.0


@dataclass
class AutonomyConfig:
    """Autonomy controller configuration"""
    risk_threshold: float = 0.3
    max_mutations_per_session: int = 10
    checkpoint_interval_seconds: int = 300
    healing_attempts: int = 3
    auto_approve_low_risk: bool = True
    require_human_approval_above: float = 0.7
    max_autonomous_runtime_hours: float = 24.0


@dataclass
class AIProviderConfig:
    """AI provider configuration"""
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"
    google_api_key: str = ""
    google_model: str = "gemini-pro"
    perplexity_api_key: str = ""
    xai_api_key: str = ""
    default_provider: str = "openai"
    fallback_providers: List[str] = field(default_factory=lambda: ["anthropic", "google"])
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 60
    cost_tracking_enabled: bool = True


@dataclass
class FitnessConfig:
    """Fitness monitoring configuration"""
    degradation_threshold_percent: float = 5.0
    degradation_window_hours: float = 1.0
    metrics_retention_days: int = 30
    auto_optimize_on_degradation: bool = True
    fitness_weights: Dict[str, float] = field(default_factory=lambda: {
        "success_rate": 0.4,
        "healing_speed": 0.2,
        "cost_efficiency": 0.2,
        "uptime": 0.2
    })


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"  # json or text
    file_path: str = "logs/evolving_ai.log"
    max_file_size_mb: int = 100
    backup_count: int = 5
    audit_log_path: str = "logs/audit.log"
    metrics_export_path: str = "metrics/"
    enable_console: bool = True


@dataclass
class PluginConfig:
    """Plugin system configuration"""
    plugins_directory: str = "plugins"
    auto_load: bool = True
    enabled_plugins: List[str] = field(default_factory=list)
    disabled_plugins: List[str] = field(default_factory=list)


@dataclass
class FrameworkConfig:
    """Main framework configuration"""
    environment: str = "development"  # development, staging, production
    debug: bool = False
    storage: StorageConfig = field(default_factory=StorageConfig)
    autonomy: AutonomyConfig = field(default_factory=AutonomyConfig)
    ai_providers: AIProviderConfig = field(default_factory=AIProviderConfig)
    fitness: FitnessConfig = field(default_factory=FitnessConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    
    # Framework metadata
    version: str = "2.0.0"
    instance_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False)


class ConfigValidator:
    """Validates configuration settings"""
    
    REQUIRED_FOR_PRODUCTION = [
        "storage.github_token",
        "ai_providers.openai_api_key"
    ]
    
    @classmethod
    def validate(cls, config: FrameworkConfig) -> tuple[bool, List[str]]:
        """Validate configuration, return (is_valid, errors)"""
        errors = []
        
        # Check autonomy bounds
        if not 0.0 <= config.autonomy.risk_threshold <= 1.0:
            errors.append("autonomy.risk_threshold must be between 0.0 and 1.0")
        
        # Check fitness weights sum to 1.0
        weights_sum = sum(config.fitness.fitness_weights.values())
        if abs(weights_sum - 1.0) > 0.01:
            errors.append(f"fitness.fitness_weights must sum to 1.0, got {weights_sum}")
        
        # Check production requirements
        if config.environment == "production":
            for req in cls.REQUIRED_FOR_PRODUCTION:
                parts = req.split(".")
                value = config
                for part in parts:
                    value = getattr(value, part, None)
                if not value:
                    errors.append(f"Production requires {req} to be set")
        
        # Check paths are valid
        if config.storage.local_path:
            try:
                Path(config.storage.local_path)
            except Exception as e:
                errors.append(f"Invalid storage.local_path: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_and_raise(cls, config: FrameworkConfig) -> None:
        """Validate and raise exception if invalid"""
        is_valid, errors = cls.validate(config)
        if not is_valid:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


class ConfigManager:
    """
    Manages framework configuration with support for:
    - Environment variables
    - Config files (YAML/JSON)
    - Runtime updates
    - Environment-specific overrides
    """
    
    ENV_PREFIX = "EVOLVING_AI_"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: FrameworkConfig = FrameworkConfig()
        self._watchers: List[callable] = []
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from all sources"""
        # 1. Start with defaults
        self.config = FrameworkConfig()
        
        # 2. Load from file if specified
        if self.config_path:
            self._load_from_file(self.config_path)
        else:
            # Try default locations
            for path in ["config.yaml", "config.json", "evolving_ai.yaml", "evolving_ai.json"]:
                if Path(path).exists():
                    self._load_from_file(path)
                    break
        
        # 3. Override with environment variables
        self._load_from_env()
        
        # 4. Validate
        ConfigValidator.validate_and_raise(self.config)
        
        logger.info(f"Configuration loaded for environment: {self.config.environment}")
    
    def _load_from_file(self, path: str) -> None:
        """Load configuration from file"""
        file_path = Path(path)
        if not file_path.exists():
            logger.warning(f"Config file not found: {path}")
            return
        
        try:
            with open(file_path, 'r') as f:
                if path.endswith('.yaml') or path.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            self._merge_config(data)
            logger.info(f"Loaded config from {path}")
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        env_mappings = {
            # Storage
            f"{self.ENV_PREFIX}DROPBOX_TOKEN": ("storage", "dropbox_token"),
            f"{self.ENV_PREFIX}GITHUB_TOKEN": ("storage", "github_token"),
            f"{self.ENV_PREFIX}GITHUB_REPO": ("storage", "github_repo"),
            f"{self.ENV_PREFIX}GITHUB_OWNER": ("storage", "github_owner"),
            f"{self.ENV_PREFIX}NOTION_TOKEN": ("storage", "notion_token"),
            "DROPBOX_ACCESS_TOKEN": ("storage", "dropbox_token"),
            "GITHUB_TOKEN": ("storage", "github_token"),
            "NOTION_TOKEN": ("storage", "notion_token"),
            
            # AI Providers
            f"{self.ENV_PREFIX}OPENAI_API_KEY": ("ai_providers", "openai_api_key"),
            f"{self.ENV_PREFIX}ANTHROPIC_API_KEY": ("ai_providers", "anthropic_api_key"),
            f"{self.ENV_PREFIX}GOOGLE_API_KEY": ("ai_providers", "google_api_key"),
            "OPENAI_API_KEY": ("ai_providers", "openai_api_key"),
            "ANTHROPIC_API_KEY": ("ai_providers", "anthropic_api_key"),
            
            # Framework
            f"{self.ENV_PREFIX}ENVIRONMENT": ("environment",),
            f"{self.ENV_PREFIX}DEBUG": ("debug",),
        }
        
        for env_var, path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(path, value)
    
    def _merge_config(self, data: Dict[str, Any]) -> None:
        """Merge dictionary into config"""
        for key, value in data.items():
            if hasattr(self.config, key):
                current = getattr(self.config, key)
                if isinstance(current, (StorageConfig, AutonomyConfig, AIProviderConfig, 
                                       FitnessConfig, LoggingConfig, PluginConfig)):
                    # Merge nested config
                    for k, v in value.items():
                        if hasattr(current, k):
                            setattr(current, k, v)
                else:
                    setattr(self.config, key, value)
    
    def _set_nested(self, path: tuple, value: Any) -> None:
        """Set a nested config value"""
        if len(path) == 1:
            if hasattr(self.config, path[0]):
                # Convert string to appropriate type
                current = getattr(self.config, path[0])
                if isinstance(current, bool):
                    value = value.lower() in ('true', '1', 'yes')
                elif isinstance(current, int):
                    value = int(value)
                elif isinstance(current, float):
                    value = float(value)
                setattr(self.config, path[0], value)
        elif len(path) == 2:
            section = getattr(self.config, path[0], None)
            if section and hasattr(section, path[1]):
                setattr(section, path[1], value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key"""
        parts = key.split(".")
        value = self.config
        for part in parts:
            value = getattr(value, part, None)
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set config value by dot-notation key"""
        parts = key.split(".")
        self._set_nested(tuple(parts), value)
        self._notify_watchers(key, value)
    
    def watch(self, callback: callable) -> None:
        """Register callback for config changes"""
        self._watchers.append(callback)
    
    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify watchers of config change"""
        for watcher in self._watchers:
            try:
                watcher(key, value)
            except Exception as e:
                logger.error(f"Config watcher error: {e}")
    
    def save(self, path: Optional[str] = None) -> None:
        """Save current config to file"""
        save_path = path or self.config_path or "config.yaml"
        
        with open(save_path, 'w') as f:
            if save_path.endswith('.json'):
                json.dump(self.config.to_dict(), f, indent=2)
            else:
                yaml.dump(self.config.to_dict(), f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {save_path}")
    
    def reload(self) -> None:
        """Reload configuration from sources"""
        self._load_config()
        for watcher in self._watchers:
            try:
                watcher("__reload__", None)
            except Exception as e:
                logger.error(f"Config reload watcher error: {e}")


def create_default_config_file(path: str = "config.yaml") -> None:
    """Create a default configuration file"""
    config = FrameworkConfig()
    
    with open(path, 'w') as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False)
    
    print(f"Created default config file: {path}")
