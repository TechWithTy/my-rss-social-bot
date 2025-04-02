from typing import Dict, Any
from src.utils.index import get_env_variable
from src.utils.config.config_provider import YamlConfigProvider, ApiConfigProvider, HybridConfigProvider

def load_config() -> Dict[str, Any]:
    """
    Loads the configuration using the appropriate provider based on environment variables.
    Returns the configuration as a dictionary.
    """
    # Check for API configuration in environment variables
    api_url = get_env_variable("CONFIG_API_URL")
    api_key = get_env_variable("CONFIG_API_KEY")
    
    # Cache duration (default: 5 minutes)
    try:
        cache_duration = int(get_env_variable("CONFIG_CACHE_DURATION"),300)
    except ValueError:
        cache_duration = 300
    
    # Choose the appropriate config provider
    if api_url:
        print(f"ud83cudf10 Using API config provider with URL: {api_url}")
        if get_env_variable("CONFIG_HYBRID_MODE").lower() == "true":
            print("u2699ufe0f Using hybrid mode (API with YAML fallback)")
            provider = HybridConfigProvider(api_url, api_key, "config.yaml", cache_duration)
        else:
            provider = ApiConfigProvider(api_url, api_key, cache_duration)
    else:
        print("ud83dudcc4 Using YAML config provider")
        provider = YamlConfigProvider("config.yaml")
    
    return provider.get_config()

# Load config globally
config = load_config()
