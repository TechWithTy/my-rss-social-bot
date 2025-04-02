# API Usage with UserPreferences Model

This document demonstrates how to use the API with the new UserPreferences data model. The API now accepts configuration through structured headers that map to fields in the UserPreferences model.

## Overview

The API has been updated to use a structured UserPreferences model instead of individual request parameters. This makes configuration more organized and maintainable. The UserPreferences model includes settings for:

- User profile information
- Social media platform configurations
- AI and LLM settings
- Content generation preferences
- Hashtag configurations

## Two Ways to Configure the API

### 1. Header-Based Configuration

You can provide configuration overrides through HTTP headers following this format:

```
X-Config-{Section}-{Subsection}-{Key}: Value
```

For example:

```
X-Config-AI-Text-Generate_Text-LLM: anthropic
X-Config-SocialMedia-LinkedIn-Enabled: true
```

### 2. Direct UserPreferences Object (JSON Body)

Alternatively, you can send a complete UserPreferences object directly in the request body, which gives you more control and allows for complex nested structures:

```http
POST /api/generate-post
Content-Type: application/json

{
  "source": "codingoni",
  "user_preferences": {
    "user_profile": {
      "medium_username": "techwriter123",
      "target_audience": "Software engineers and tech professionals",
      "cache": {
        "linkedin_posts": {
          "last_post_id": "post123",
          "last_post_date": "2025-04-01T12:30:00Z"
        }
      },
      "storage": {
        "preferences_version": "1.2.3"
      }
    },
    "social_media_to_post_to": {
      "linkedin": {
        "enabled": true,
        "post_format": "professional",
        "maximum_characters": 3000
      }
    },
    "ai": {
      "text": {
        "generate_text": {
          "enabled": true,
          "LLM": "anthropic"
        }
      },
      "viral_posting": {
        "include_viral_formatting": {
          "enabled": true
        },
        "attention_grabbing_intro": {
          "enabled": true
        }
      }
    },
    "hashtags": {
      "custom_tags": ["python", "machinelearning", "ai"]
    }
  }
}
```

This approach allows for more complex configurations and is especially useful when you need to:  
- Set deeply nested properties  
- Provide complex data structures like arrays and nested objects  
- Save and reuse entire configuration profiles  
- Share configurations between different client applications

## API Endpoints

### Generate Post

```http
POST /api/generate-post
Content-Type: application/json
X-Config-AI-Text-Generate_Text-LLM: anthropic
X-Config-SocialMedia-LinkedIn-Enabled: true
X-Config-AI-Viral_Posting-Include_Viral_Formatting-Enabled: true

{
  "source": "codingoni"
}
```

### Check Status

```http
GET /api/status
X-Config-User_Profile-Medium_Username: techwriter123
```

### Run Test

```http
GET /api/test
X-Config-AI-Creative-Generate_Image-Enabled: false
```

## Complete Example: Customizing LinkedIn Post Format

```http
POST /api/generate-post
Content-Type: application/json
X-Config-User_Profile-Professional_Summary: "Senior Software Engineer with 10+ years experience in Python and AI"
X-Config-SocialMedia-LinkedIn-Enabled: true
X-Config-SocialMedia-LinkedIn-Post_Format: "professional"
X-Config-SocialMedia-LinkedIn-Maximum_Characters: 3000
X-Config-AI-Text-Generate_Text-LLM: openai
X-Config-AI-Viral_Posting-Attention_Grabbing_Intro-Enabled: true
X-Config-Hashtags-Custom_Tags: ["python", "machinelearning", "ai"]

{
  "source": "codingoni"
}
```

## Using the Cache and Storage Fields

The `UserProfile` class now includes cache and storage fields for persisting data across API calls:

```python
cache: Dict[str, Optional[Dict[str, str]]] = field(default_factory=dict)
storage: Dict[str, str] = field(default_factory=dict)
```

These can be used to store:

- Previously generated content
- Processing statistics
- User-specific data
- Session information
- API rate limiting data

Example of using these fields in a request:

```http
POST /api/generate-post
Content-Type: application/json

{
  "source": "codingoni",
  "user_preferences": {
    "user_profile": {
      "medium_username": "techwriter123",
      "cache": {
        "previous_posts": {
          "last_post_id": "123456",
          "last_generation_date": "2025-04-01T10:15:30Z"
        }
      },
      "storage": {
        "session_id": "user_session_87654321"
      }
    }
  }
}
```

## Mapping Headers to UserPreferences

The API automatically converts the header-based configuration to a UserPreferences object. For example:

- `X-Config-User_Profile-Medium_Username: techwriter123` maps to `preferences.user_profile.medium_username`
- `X-Config-AI-Text-Generate_Text-LLM: anthropic` maps to `preferences.ai.text.generate_text.LLM`
- `X-Config-SocialMedia-LinkedIn-Enabled: true` maps to `preferences.social_media_to_post_to.linkedin.enabled`

## Error Handling

If there are issues with your configuration, the API will return appropriate error messages:

```json
{
  "success": false,
  "error": "Invalid configuration: LLM 'unknown_model' not supported"
}
```

## Best Practices

1. Only override the configuration values you need to change
2. Use JSON format for array and object values in headers (e.g., `X-Config-Hashtags-Custom_Tags: ["python", "ai"]`)
3. Boolean values can be provided as `true`/`false` strings
4. Numbers are automatically converted to the appropriate type
5. For complex configurations, prefer sending a complete UserPreferences object in the body
6. Utilize the cache and storage fields to persist state between API calls when needed
