# API Configuration System for RSS Social Bot

## Overview

This implementation adds API-based configuration to the RSS Social Bot, allowing you to manage your bot's configuration through an external API rather than relying solely on the local YAML file. This provides several benefits:

1. **Remote Management**: Update configuration without accessing the server
2. **Centralized Control**: Manage multiple bots from a single source
3. **Dynamic Updates**: Change configuration on the fly without restart
4. **Fallback Mechanism**: Continue working even if API is temporarily unavailable

## Implementation Details

The new system uses a provider-based architecture with three main configuration providers:

1. **YamlConfigProvider**: The original config provider that reads from local YAML files
2. **ApiConfigProvider**: Fetches configuration from a REST API endpoint
3. **HybridConfigProvider**: Attempts to use the API first, falls back to YAML if the API fails

## How to Use

### Environment Variables

The system uses environment variables to determine how to load configuration:

```
CONFIG_API_URL=https://your-api-endpoint.com/config
CONFIG_API_KEY=your_secret_key_here
CONFIG_CACHE_DURATION=300
CONFIG_HYBRID_MODE=true
```

- **CONFIG_API_URL**: URL of your API endpoint that returns the configuration JSON
- **CONFIG_API_KEY**: (Optional) Authentication key for the API
- **CONFIG_CACHE_DURATION**: How long to cache the API response (in seconds)
- **CONFIG_HYBRID_MODE**: Whether to fall back to YAML if the API fails

### API Response Format

Your API endpoint should return a JSON object with the same structure as your config.yaml file. For example:

```json
{
  "user_profile": {
    "medium_username": "codingoni",
    "target_audience": "Non Technical People Looking For Tech Thought Leadership"
  },
  "ai": {
    "text": {
      "generate_text": {
        "LLM": "openai"
      }
    },
    "custom_system_instructions": "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
  },
  "social_media_to_post_to": {
    "linkedin": {
      "enabled": true,
      "maximum_characters": 3000
    }
  },
  "hashtags": {
    "default_tags": ["#AI", "#MachineLearning"]
  }
}
```

## Testing

Run the example script to see how the API configuration system works:

```bash
pipenv run python example_api_config.py
```

## Migration Guide

### Existing Code

Existing code that imports and uses the config object will continue to work without changes:

```python
from utils.config.config_loader import config

# Access config as before
linkedin_enabled = config["social_media_to_post_to"]["linkedin"].get("enabled", False)
```

### Creating Your API

You can implement the API endpoint using any web framework like Flask or FastAPI. The endpoint should:

1. Return the complete configuration as a JSON response
2. Implement authentication if needed
3. Handle any request parameters you want to support

## Caching Behavior

The API provider implements caching to reduce API calls and ensure the system remains responsive even during network issues:

1. Configuration is cached for the duration specified in CONFIG_CACHE_DURATION
2. If the API fails but cached config exists, the system will use the cached version
3. Cache is refreshed automatically when expired

## Advanced Usage

### Custom Configuration Providers

You can create your own configuration provider by extending the ConfigProvider base class:

```python
from utils.config_provider import ConfigProvider

class MyCustomProvider(ConfigProvider):
    def get_config(self):
        # Your custom logic here
        return custom_config
```

### Handling Multiple Environments

Use different environment variables for different environments:

```
# Development
CONFIG_API_URL=https://dev-config-api.example.com

# Production
CONFIG_API_URL=https://prod-config-api.example.com
```
