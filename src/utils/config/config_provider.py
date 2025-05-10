import os
import yaml
import requests
from typing import Dict, Any, Optional
import time

class ConfigProvider:
    """
    Abstract base class for config providers.
    """
    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration dictionary.
        """
        raise NotImplementedError("Subclasses must implement get_config()")

class YamlConfigProvider(ConfigProvider):
    """
    Loads configuration from a YAML file.
    """
    def __init__(self, file_path: str = "config.yaml"):
        self.file_path = file_path
        
    def get_config(self) -> Dict[str, Any]:
        # List of possible locations for the config file
        possible_paths = [
            self.file_path,  # Current directory
            os.path.join(os.path.dirname(__file__), "../..", self.file_path),  # Project root
            os.path.join(os.path.dirname(__file__), "../../_configs", self.file_path),  # _configs directory
        ]
        
        # Try each path until we find the file
        for path in possible_paths:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    print(f" Loading config from YAML file: {path}")
                    return yaml.safe_load(file)
            except FileNotFoundError:
                continue
        
        # For testing environments, return a default empty config if file not found
        print(f"\u26a0\ufe0f Warning: Config file '{self.file_path}' not found. Using default empty config for testing.")
        return {}

class ModularYamlConfigProvider(ConfigProvider):
    """
    Loads and deeply merges all YAML config files in the config/ directory for modular configuration.
    """
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        self.config_dir = config_dir

    def get_config(self) -> Dict[str, Any]:
        config = {}
        for fname in sorted(os.listdir(self.config_dir)):
            if fname.endswith('.yaml') or fname.endswith('.yml'):
                with open(os.path.join(self.config_dir, fname), 'r', encoding='utf-8') as f:
                    part = yaml.safe_load(f) or {}
                    config = self.deep_merge_dicts(config, part)
        return config

    @staticmethod
    def deep_merge_dicts(a: dict, b: dict) -> dict:
        result = a.copy()
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = ModularYamlConfigProvider.deep_merge_dicts(result[k], v)
            else:
                result[k] = v
        return result



class ApiConfigProvider(ConfigProvider):
    """
    Loads configuration from an API endpoint.
    """
    def __init__(self, 
                 api_url: str,
                 api_key: Optional[str] = None, 
                 cache_duration: int = 300):
        self.api_url = api_url
        self.api_key = api_key
        self.cache_duration = cache_duration  # Cache duration in seconds
        self.cached_config = None
        self.last_fetch_time = 0
    
    def get_config(self) -> Dict[str, Any]:
        # Check if we have a cached config and it's still fresh
        current_time = time.time()
        if self.cached_config and (current_time - self.last_fetch_time) < self.cache_duration:
            print(f"\ud83d\udc04 Using cached config (expires in {int(self.cache_duration - (current_time - self.last_fetch_time))}s)")
            return self.cached_config
        
        # Prepare headers with API key if provided
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            print("\ud83c\udf10 Fetching config from API")
            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            # Update cache
            self.cached_config = response.json()
            self.last_fetch_time = current_time
            
            print("\u2705 Successfully fetched config from API")
            return self.cached_config
            
        except requests.RequestException as e:
            print(f"\u274c Error fetching config from API: {e}")
            
            # If we have a cached config, use it as fallback
            if self.cached_config:
                print("\u26a0\ufe0f Using stale cached config as fallback")
                return self.cached_config
            
            # Otherwise return empty config
            print("\u26a0\ufe0f No cached config available. Using empty config.")
            return {}

class HybridConfigProvider(ConfigProvider):
    """
    Tries to load config from API first, falls back to YAML if API fails.
    """
    def __init__(self, 
                 api_url: Optional[str] = None,
                 api_key: Optional[str] = None,
                 yaml_file_path: str = "config.yaml",
                 cache_duration: int = 300):
        self.api_provider = None
        if api_url:
            self.api_provider = ApiConfigProvider(api_url, api_key, cache_duration)
        self.yaml_provider = YamlConfigProvider(yaml_file_path)
    
    def get_config(self) -> Dict[str, Any]:
        # If API provider is configured, try it first
        if self.api_provider:
            api_config = self.api_provider.get_config()
            if api_config:  # If we got a non-empty config from API
                return api_config
        
        # Fall back to YAML config
        return self.yaml_provider.get_config()

