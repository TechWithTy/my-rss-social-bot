import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Example config data structure
config_data = {
    "user_profile": {
        "medium_username": "codingoni",
        "target_audience": "Non Technical People Looking For Tech Thought Leadership",
        "professional_summary": "I'm a Software Engineer with a passion for creating innovative solutions and sharing my knowledge with the world."
    },
    "ai": {
        "text": {
            "generate_text": {
                "LLM": "openai"
            }
        },
        "creative": {
            "generate_image": {
                "LLM": "openai"
            }
        },
        "default_response_instructions": "Return a generated LinkedIn post based on the blog content.",
        "custom_system_instructions": "You're a professional copywriter helping turn blog posts into viral LinkedIn content.",
        "custom_user_instructions": "Make the post concise, actionable, and emotionally resonant.",
        "viral_posting": {
            "attention_grabbing_intro": {
                "description": "Start with a powerful hook that makes readers stop scrolling."
            },
            "emotional_storytelling": {
                "description": "Use stories that evoke strong emotions like curiosity, surprise, or inspiration."
            },
            "actionable_takeaways": {
                "description": "Include specific actions readers can implement immediately."
            }
        },
        "viral_posts_i_liked": [
            {
                "text": "Example viral post that received high engagement",
                "engagement": "500 likes 35 comments 20 reposts",
                "creative": "Image",
                "creative_asset": "https://example.com/image.jpg",
                "reason": "Strong hook and actionable content"
            }
        ]
    },
    "social_media_to_post_to": {
        "linkedin": {
            "enabled": True,
            "post_format": "Text",
            "maximum_characters": 3000,
            "minimum_characters": 500,
            "formatting_instructions": "Use emojis and bullet points for better readability."
        }
    },
    "hashtags": {
        "default_tags": [
            "#AI",
            "#MachineLearning",
            "#DataScience",
            "#Automation",
            "#Technology"
        ],
        "custom_tags": []
    }
}

def setup_mock_api_server():
    """
    This function demonstrates how to set up a simple API server for configuration.
    For production, you would use a real API server like Flask or FastAPI.
    
    This is just an example to show how the system could work with an external API.
    """
    print("\nTo integrate with an external API for configuration:")
    print("1. Set up a REST API endpoint that returns your configuration JSON")
    print("2. Set the following environment variables in your .env file:")
    print("   CONFIG_API_URL=your_api_endpoint_url")
    print("   CONFIG_API_KEY=your_api_key_if_needed")
    print("   CONFIG_CACHE_DURATION=300  # Cache duration in seconds")
    print("   CONFIG_HYBRID_MODE=true    # Use YAML as fallback if API fails\n")
    
    # Example API response format
    print("Example API response JSON format:")
    print(json.dumps(config_data, indent=2)[:500] + "...\n")

def main():
    print("=== API Configuration System Example ===")
    print("This script demonstrates how to set up the system to use API-based configuration.")
    
    # Show usage instructions
    setup_mock_api_server()
    
    # Show current environment variables
    print("Current environment variables:")
    config_api_url = os.environ.get("CONFIG_API_URL", "Not set")
    config_api_key = os.environ.get("CONFIG_API_KEY", "Not set (will use unauthenticated requests)")
    cache_duration = os.environ.get("CONFIG_CACHE_DURATION", "300 (default)")
    hybrid_mode = os.environ.get("CONFIG_HYBRID_MODE", "false (default)")
    
    print(f"CONFIG_API_URL: {config_api_url}")
    print(f"CONFIG_API_KEY: {'*****' if config_api_key != 'Not set (will use unauthenticated requests)' else config_api_key}")
    print(f"CONFIG_CACHE_DURATION: {cache_duration}")
    print(f"CONFIG_HYBRID_MODE: {hybrid_mode}")

if __name__ == "__main__":
    main()
