"""
Plugin System for Self-Evolving AI Framework
============================================

Extensible plugin architecture with:
- Dynamic plugin loading
- Lifecycle management
- Dependency resolution
- Hot reload support
"""

import logging
import importlib
import importlib.util
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .models import PluginInfo

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """
    Base class for all plugins.
    
    Plugins must implement:
    - initialize(): Setup plugin resources
    - execute(): Main plugin logic
    - cleanup(): Release resources
    """
    
    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "Base plugin"
    author: str = "Unknown"
    dependencies: List[str] = []
    
    def __init__(self, framework=None):
        self.framework = framework
        self.enabled = True
        self.config: Dict[str, Any] = {}
        self._initialized = False

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin resources. Return True on success."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic. Return result dict."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Update plugin configuration."""
        self.config.update(config)
    
    def get_info(self) -> PluginInfo:
        """Get plugin metadata."""
        return PluginInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            enabled=self.enabled,
            config=self.config,
            dependencies=self.dependencies
        )


class PluginManager:
    """
    Manages plugin lifecycle and execution.
    
    Features:
    - Dynamic loading from directory
    - Dependency resolution
    - Enable/disable plugins
    - Plugin configuration
    """
    
    def __init__(self, plugins_dir: str = "plugins", framework=None):
        self.plugins_dir = Path(plugins_dir)
        self.framework = framework
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_order: List[str] = []
        
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PluginManager initialized with dir: {plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in directory."""
        discovered = []
        
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            discovered.append(file_path.stem)
        
        return discovered
    
    def load_plugin(self, name: str) -> Optional[BasePlugin]:
        """Load a single plugin by name."""
        if name in self.plugins:
            return self.plugins[name]
        
        plugin_path = self.plugins_dir / f"{name}.py"
        if not plugin_path.exists():
            logger.error(f"Plugin not found: {name}")
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and issubclass(attr, BasePlugin) 
                    and attr is not BasePlugin):
                    plugin_class = attr
                    break
            
            if not plugin_class:
                logger.error(f"No plugin class found in {name}")
                return None
            
            plugin = plugin_class(self.framework)
            self.plugins[name] = plugin
            self.load_order.append(name)
            
            logger.info(f"Loaded plugin: {name} v{plugin.version}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {name}: {e}")
            return None

    def load_all(self) -> int:
        """Load all discovered plugins. Returns count loaded."""
        discovered = self.discover_plugins()
        loaded = 0
        
        # Sort by dependencies
        sorted_plugins = self._resolve_dependencies(discovered)
        
        for name in sorted_plugins:
            if self.load_plugin(name):
                loaded += 1
        
        return loaded
    
    def _resolve_dependencies(self, plugins: List[str]) -> List[str]:
        """Sort plugins by dependencies."""
        # Simple topological sort
        resolved = []
        unresolved = set(plugins)
        
        while unresolved:
            made_progress = False
            for name in list(unresolved):
                plugin_path = self.plugins_dir / f"{name}.py"
                deps = self._get_plugin_deps(plugin_path)
                
                if all(d in resolved or d not in plugins for d in deps):
                    resolved.append(name)
                    unresolved.remove(name)
                    made_progress = True
            
            if not made_progress and unresolved:
                # Circular dependency, just add remaining
                resolved.extend(unresolved)
                break
        
        return resolved
    
    def _get_plugin_deps(self, path: Path) -> List[str]:
        """Extract dependencies from plugin file."""
        try:
            with open(path, 'r') as f:
                content = f.read()
                # Look for dependencies = [...] pattern
                import re
                match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content)
                if match:
                    deps_str = match.group(1)
                    return [d.strip().strip('"\'') for d in deps_str.split(',') if d.strip()]
        except Exception:
            pass
        return []
    
    def initialize_all(self) -> Dict[str, bool]:
        """Initialize all loaded plugins."""
        results = {}
        for name, plugin in self.plugins.items():
            try:
                success = plugin.initialize()
                plugin._initialized = success
                results[name] = success
                if success:
                    logger.info(f"Initialized plugin: {name}")
                else:
                    logger.warning(f"Plugin initialization failed: {name}")
            except Exception as e:
                logger.error(f"Plugin {name} initialization error: {e}")
                results[name] = False
        return results
    
    def execute_plugin(self, name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specific plugin."""
        if name not in self.plugins:
            logger.error(f"Plugin not found: {name}")
            return None
        
        plugin = self.plugins[name]
        if not plugin.enabled:
            logger.debug(f"Plugin disabled: {name}")
            return None
        
        if not plugin._initialized:
            logger.warning(f"Plugin not initialized: {name}")
            return None
        
        try:
            return plugin.execute(context)
        except Exception as e:
            logger.error(f"Plugin {name} execution error: {e}")
            return {"error": str(e)}
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = True
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin."""
        if name in self.plugins:
            self.plugins[name].enabled = False
            return True
        return False
    
    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        if name in self.plugins:
            return self.plugins[name].get_info()
        return None
    
    def list_plugins(self) -> List[PluginInfo]:
        """List all loaded plugins."""
        return [p.get_info() for p in self.plugins.values()]
    
    def cleanup_all(self) -> None:
        """Cleanup all plugins."""
        for name in reversed(self.load_order):
            try:
                self.plugins[name].cleanup()
            except Exception as e:
                logger.error(f"Plugin {name} cleanup error: {e}")
