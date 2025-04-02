# Using the RSS Social Bot API with Configuration Headers

## Overview

This guide demonstrates how to use the RSS Social Bot API with custom configuration passed through HTTP headers. This approach allows you to customize the bot's behavior without modifying the server-side configuration files.

## Running the API Server

```bash
# Start the API server
pipenv run python -m src.api.app
```

The server will start on http://localhost:5000 by default.

## API Endpoints

### 1. Generate Post

**Endpoint**: `/api/generate-post`
**Method**: POST
**Description**: Generates and posts content based on the latest blog from the specified source

**Request Body**:
```json
{
  "source": "codingoni"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Post generated and published successfully"
}
```

### 2. Status Check

**Endpoint**: `/api/status`
**Method**: GET
**Description**: Check the status of the bot and API configuration

**Response**:
```json
{
  "success": true,
  "status": "online",
  "linkedin_authenticated": true,
  "linkedin_profile_id": "your-profile-id",
  "config_override_active": true
}
```

### 3. Test Configuration

**Endpoint**: `/api/test`
**Method**: GET
**Description**: Test the API and view effective configuration

**Response**:
```json
{
  "success": true,
  "message": "API test successful",
  "config_override": {...},
  "effective_config_sample": {...}
}
```

## Using Configuration Headers

You can customize the bot's behavior by sending configuration in HTTP headers. The header format is:

```
X-Config-{Section}-{Subsection}-{Key}: Value
```

Header names are case-insensitive. Values are parsed as JSON when possible, otherwise treated as strings/booleans/numbers.

### Examples

#### Python Example with Requests

```python
import requests

# API endpoint
url = "http://localhost:5000/api/generate-post"

# Custom configuration through headers
headers = {
    # Customize AI model
    "X-Config-AI-Text-Generate_Text-LLM": "anthropic",
    
    # Customize LinkedIn post format
    "X-Config-Social_Media_To_Post_To-LinkedIn-Post_Format": "Text+Image",
    "X-Config-Social_Media_To_Post_To-LinkedIn-Formatting_Instructions": "Use bullet points and make it professional",
    
    # Add custom hashtags
    "X-Config-Hashtags-Custom_Tags": "[\"#Engineering\", \"#Innovation\"]"
}

# Request body
data = {
    "source": "codingoni"
}

# Send request
response = requests.post(url, headers=headers, json=data)
print(response.json())
```

#### cURL Example

```bash
curl -X POST http://localhost:5000/api/generate-post \
  -H "X-Config-AI-Text-Generate_Text-LLM: anthropic" \
  -H "X-Config-Social_Media_To_Post_To-LinkedIn-Post_Format: Text+Image" \
  -H "X-Config-Hashtags-Custom_Tags: [\"#Engineering\", \"#Innovation\"]" \
  -H "Content-Type: application/json" \
  -d '{"source": "codingoni"}'
```

## Header Value Formats

The API supports different value formats:

1. **Strings**: Simple text values
   ```
   X-Config-User_Profile-Medium_Username: newusername
   ```

2. **Booleans**: `true` or `false` (case-insensitive)
   ```
   X-Config-Social_Media_To_Post_To-LinkedIn-Enabled: true
   ```

3. **Numbers**: Integer or decimal values
   ```
   X-Config-Social_Media_To_Post_To-LinkedIn-Maximum_Characters: 1500
   ```

4. **Arrays/Objects**: JSON-formatted strings
   ```
   X-Config-Hashtags-Default_Tags: ["#AI", "#Tech", "#Innovation"]
   ```

## Configuration Structure

The configuration structure matches the structure in `config.yaml`. Here are the main sections:

1. **user_profile**: User identity and audience information
2. **ai**: AI model configurations and instructions
3. **social_media_to_post_to**: Platform-specific settings
4. **hashtags**: Default and custom hashtags

## Testing Your Configuration

Use the `/api/test` endpoint with your custom headers to verify the effective configuration before generating posts:

```bash
curl -X GET http://localhost:5000/api/test \
  -H "X-Config-AI-Text-Generate_Text-LLM: anthropic"
```

This will return the effective configuration that would be used for post generation.

## Advanced Usage

### Completely Replacing Sections

You can replace entire configuration sections by providing JSON objects:

```
X-Config-Hashtags: {"default_tags":["#NewTag1","#NewTag2"],"custom_tags":[]}
```

### Nested Configuration

For deeply nested configurations, use multiple headers:

```
X-Config-AI-Viral_Posting-Attention_Grabbing_Intro-Description: "Start with a question that challenges assumptions"
X-Config-AI-Viral_Posting-Emotional_Storytelling-Description: "Use personal anecdotes that relate to reader pain points"
```
