from flask import request, jsonify, Blueprint
import json
from typing import Dict, Any, Optional
from src.utils.config.config_loader import config as base_config
from src.main import main as run_bot
from src.socials.linkedin_bot import get_linkedin_profile_id
from src.utils.prompt_builder import init_globals_if_needed, get_prompt_globals
from src.utils.helpers.post_cache_helper import is_blog_already_posted
from data.user_model import UserPreferences

# Create blueprint for API routes
api_blueprint = Blueprint('api', __name__)

# Store header-based config override for the current request
request_config_override = {}
request_preferences: Optional[UserPreferences] = None

def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries with override taking precedence.
    
    Args:
        base: Base configuration dictionary
        override: Override dictionary with values to apply on top of base
        
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        # If both base and override have dict at this key, merge them recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        # Otherwise override takes precedence
        else:
            result[key] = value
            
    return result

def extract_config_from_headers() -> Dict[str, Any]:
    """
    Extract configuration from request headers and parse them into a nested dictionary.
    Headers should follow the format: X-Config-{section}-{subsection}-{key}
    
    Example:
        X-Config-AI-Text-LLM: openai
        X-Config-SocialMedia-LinkedIn-Enabled: true
    
    Returns:
        Dictionary with configuration extracted from headers
    """
    config_override = {}
    
    prefix = "X-Config-"
    for header, value in request.headers.items():
        if header.startswith(prefix):
            # Remove prefix and split into path components
            path = header[len(prefix):].split("-")
            
            # Skip if empty path
            if not path:
                continue
                
            # Convert path to lowercase for case-insensitivity
            path = [p.lower() for p in path]
            
            # Parse value based on content
            try:
                # Try to parse as JSON first
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, use string value
                parsed_value = value
                
                # Convert "true"/"false" to boolean
                if parsed_value.lower() == "true":
                    parsed_value = True
                elif parsed_value.lower() == "false":
                    parsed_value = False
                    
                # Try to convert to number if possible
                try:
                    if "." in parsed_value:
                        parsed_value = float(parsed_value)
                    else:
                        parsed_value = int(parsed_value)
                except (ValueError, AttributeError):
                    # Keep as string if not a number
                    pass
            
            # Build nested dictionary
            current = config_override
            for i, part in enumerate(path):
                if i == len(path) - 1:
                    # Last element is the key
                    current[part] = parsed_value
                else:
                    # Create nested dictionary if it doesn't exist
                    if part not in current:
                        current[part] = {}
                    current = current[part]
    
    return config_override

# Function to convert dictionary config to UserPreferences object
def dict_to_user_preferences(config_dict: Dict[str, Any]) -> UserPreferences:
    """
    Convert a dictionary of configuration values to a UserPreferences object.
    
    Args:
        config_dict: Dictionary with configuration values
        
    Returns:
        UserPreferences object populated with values from the dictionary
    """
    # Create default preferences
    preferences = UserPreferences()
    
    # Process user_profile section
    user_profile_dict = config_dict.get('user_profile', {})
    if user_profile_dict:
        preferences.user_profile.medium_username = user_profile_dict.get('medium_username', preferences.user_profile.medium_username)
        preferences.user_profile.wix_url = user_profile_dict.get('wix_url', preferences.user_profile.wix_url)
        preferences.user_profile.wordpress_url = user_profile_dict.get('wordpress_url', preferences.user_profile.wordpress_url)
        preferences.user_profile.target_audience = user_profile_dict.get('target_audience', preferences.user_profile.target_audience)
        preferences.user_profile.professional_summary = user_profile_dict.get('professional_summary', preferences.user_profile.professional_summary)
        preferences.user_profile.resume_url = user_profile_dict.get('resume_url', preferences.user_profile.resume_url)
        
        # Process LLM configurations
        llm_dict = user_profile_dict.get('llm', {})
        if llm_dict:
            # Process OpenAI config
            openai_dict = llm_dict.get('OpenAI', {})
            if openai_dict:
                preferences.user_profile.llm.OpenAI.text_model = openai_dict.get('text_model', preferences.user_profile.llm.OpenAI.text_model)
                preferences.user_profile.llm.OpenAI.image_model = openai_dict.get('image_model', preferences.user_profile.llm.OpenAI.image_model)
                preferences.user_profile.llm.OpenAI.temperature = openai_dict.get('temperature', preferences.user_profile.llm.OpenAI.temperature)
            
            # Process Anthropic config
            anthropic_dict = llm_dict.get('Anthropic', {})
            if anthropic_dict:
                preferences.user_profile.llm.Anthropic.text_model = anthropic_dict.get('text_model', preferences.user_profile.llm.Anthropic.text_model)
                preferences.user_profile.llm.Anthropic.temperature = anthropic_dict.get('temperature', preferences.user_profile.llm.Anthropic.temperature)
    
    # Process social media platforms
    social_media_dict = config_dict.get('social_media_to_post_to', {})
    if social_media_dict:
        linkedin_dict = social_media_dict.get('linkedin', {})
        if linkedin_dict:
            preferences.social_media_to_post_to.linkedin.enabled = linkedin_dict.get('enabled', preferences.social_media_to_post_to.linkedin.enabled)
            preferences.social_media_to_post_to.linkedin.post_format = linkedin_dict.get('post_format', preferences.social_media_to_post_to.linkedin.post_format)
            preferences.social_media_to_post_to.linkedin.formatting_instructions = linkedin_dict.get('formatting_instructions', preferences.social_media_to_post_to.linkedin.formatting_instructions)
            preferences.social_media_to_post_to.linkedin.maximum_characters = linkedin_dict.get('maximum_characters', preferences.social_media_to_post_to.linkedin.maximum_characters)
    
    # Process AI configuration
    ai_dict = config_dict.get('ai', {})
    if ai_dict:
        preferences.ai.default_response_instructions = ai_dict.get('default_response_instructions', preferences.ai.default_response_instructions)
        preferences.ai.custom_system_instructions = ai_dict.get('custom_system_instructions', preferences.ai.custom_system_instructions)
        preferences.ai.custom_user_instructions = ai_dict.get('custom_user_instructions', preferences.ai.custom_user_instructions)
        
        # Process text generation settings
        text_dict = ai_dict.get('text', {})
        if text_dict:
            generate_text_dict = text_dict.get('generate_text', {})
            if generate_text_dict:
                preferences.ai.text.generate_text.enabled = generate_text_dict.get('enabled', preferences.ai.text.generate_text.enabled)
                preferences.ai.text.generate_text.LLM = generate_text_dict.get('LLM', preferences.ai.text.generate_text.LLM)
                preferences.ai.text.generate_text.prompt = generate_text_dict.get('prompt', preferences.ai.text.generate_text.prompt)
        
        # Process creative settings
        creative_dict = ai_dict.get('creative', {})
        if creative_dict:
            generate_image_dict = creative_dict.get('generate_image', {})
            if generate_image_dict:
                preferences.ai.creative.generate_image.enabled = generate_image_dict.get('enabled', preferences.ai.creative.generate_image.enabled)
                preferences.ai.creative.generate_image.LLM = generate_image_dict.get('LLM', preferences.ai.creative.generate_image.LLM)
                preferences.ai.creative.generate_image.width = generate_image_dict.get('width', preferences.ai.creative.generate_image.width)
                preferences.ai.creative.generate_image.height = generate_image_dict.get('height', preferences.ai.creative.generate_image.height)
                preferences.ai.creative.generate_image.prompt = generate_image_dict.get('prompt', preferences.ai.creative.generate_image.prompt)
        
        # Process viral posting settings
        viral_posting_dict = ai_dict.get('viral_posting', {})
        if viral_posting_dict:
            viral_settings = [
                ('include_viral_formatting', preferences.ai.viral_posting.include_viral_formatting),
                ('attention_grabbing_intro', preferences.ai.viral_posting.attention_grabbing_intro),
                ('emotional_storytelling', preferences.ai.viral_posting.emotional_storytelling),
                ('extreme_statements', preferences.ai.viral_posting.extreme_statements),
                ('relatable_experiences', preferences.ai.viral_posting.relatable_experiences),
                ('actionable_takeaways', preferences.ai.viral_posting.actionable_takeaways),
                ('data_backed_claims', preferences.ai.viral_posting.data_backed_claims)
            ]
            
            for setting_name, setting_obj in viral_settings:
                setting_dict = viral_posting_dict.get(setting_name, {})
                if setting_dict:
                    setting_obj.enabled = setting_dict.get('enabled', setting_obj.enabled)
                    setting_obj.description = setting_dict.get('description', setting_obj.description)
    
    # Process hashtags
    hashtags_dict = config_dict.get('hashtags', {})
    if hashtags_dict:
        preferences.hashtags.default_tags = hashtags_dict.get('default_tags', preferences.hashtags.default_tags)
        preferences.hashtags.custom_tags = hashtags_dict.get('custom_tags', preferences.hashtags.custom_tags)
    
    return preferences

# Function to convert UserPreferences object to dictionary
def user_preferences_to_dict(preferences: UserPreferences) -> Dict[str, Any]:
    """
    Convert a UserPreferences object to a dictionary that can be used with the existing config system.
    
    Args:
        preferences: UserPreferences object to convert
        
    Returns:
        Dictionary with configuration values
    """
    config_dict = {
        'user_profile': {
            'medium_username': preferences.user_profile.medium_username,
            'wix_url': preferences.user_profile.wix_url,
            'wordpress_url': preferences.user_profile.wordpress_url,
            'target_audience': preferences.user_profile.target_audience,
            'professional_summary': preferences.user_profile.professional_summary,
            'resume_url': preferences.user_profile.resume_url,
            'llm': {
                'OpenAI': {
                    'text_model': preferences.user_profile.llm.OpenAI.text_model,
                    'image_model': preferences.user_profile.llm.OpenAI.image_model,
                    'temperature': preferences.user_profile.llm.OpenAI.temperature,
                },
                'Anthropic': {
                    'text_model': preferences.user_profile.llm.Anthropic.text_model,
                    'temperature': preferences.user_profile.llm.Anthropic.temperature,
                }
            }
        },
        'social_media_to_post_to': {
            'linkedin': {
                'enabled': preferences.social_media_to_post_to.linkedin.enabled,
                'post_format': preferences.social_media_to_post_to.linkedin.post_format,
                'formatting_instructions': preferences.social_media_to_post_to.linkedin.formatting_instructions,
                'maximum_characters': preferences.social_media_to_post_to.linkedin.maximum_characters,
            }
        },
        'ai': {
            'default_response_instructions': preferences.ai.default_response_instructions,
            'custom_system_instructions': preferences.ai.custom_system_instructions,
            'custom_user_instructions': preferences.ai.custom_user_instructions,
            'text': {
                'generate_text': {
                    'enabled': preferences.ai.text.generate_text.enabled,
                    'LLM': preferences.ai.text.generate_text.LLM,
                    'prompt': preferences.ai.text.generate_text.prompt,
                }
            },
            'creative': {
                'generate_image': {
                    'enabled': preferences.ai.creative.generate_image.enabled,
                    'LLM': preferences.ai.creative.generate_image.LLM,
                    'width': preferences.ai.creative.generate_image.width,
                    'height': preferences.ai.creative.generate_image.height,
                    'prompt': preferences.ai.creative.generate_image.prompt,
                }
            },
            'viral_posting': {
                'include_viral_formatting': {
                    'enabled': preferences.ai.viral_posting.include_viral_formatting.enabled,
                    'description': preferences.ai.viral_posting.include_viral_formatting.description,
                },
                'attention_grabbing_intro': {
                    'enabled': preferences.ai.viral_posting.attention_grabbing_intro.enabled,
                    'description': preferences.ai.viral_posting.attention_grabbing_intro.description,
                },
                'emotional_storytelling': {
                    'enabled': preferences.ai.viral_posting.emotional_storytelling.enabled,
                    'description': preferences.ai.viral_posting.emotional_storytelling.description,
                },
                'extreme_statements': {
                    'enabled': preferences.ai.viral_posting.extreme_statements.enabled,
                    'description': preferences.ai.viral_posting.extreme_statements.description,
                },
                'relatable_experiences': {
                    'enabled': preferences.ai.viral_posting.relatable_experiences.enabled,
                    'description': preferences.ai.viral_posting.relatable_experiences.description,
                },
                'actionable_takeaways': {
                    'enabled': preferences.ai.viral_posting.actionable_takeaways.enabled,
                    'description': preferences.ai.viral_posting.actionable_takeaways.description,
                },
                'data_backed_claims': {
                    'enabled': preferences.ai.viral_posting.data_backed_claims.enabled,
                    'description': preferences.ai.viral_posting.data_backed_claims.description,
                }
            }
        },
        'hashtags': {
            'default_tags': preferences.hashtags.default_tags,
            'custom_tags': preferences.hashtags.custom_tags,
        }
    }
    
    return config_dict

@api_blueprint.before_request
def process_config_headers():
    """
    Process configuration headers before handling the request.
    Extracts header-based configuration and converts to UserPreferences object.
    """
    global request_config_override
    global request_preferences
    
    # Extract configuration from headers
    request_config_override = extract_config_from_headers()
    
    # Convert to UserPreferences object
    request_preferences = dict_to_user_preferences(request_config_override)
    
    print("Header config override processed into UserPreferences object")

def get_effective_config() -> Dict[str, Any]:
    """
    Get the effective configuration by merging base config with header overrides.
    Uses the UserPreferences model for structured configuration handling.
    
    Returns:
        Merged configuration dictionary
    """
    global request_config_override
    global request_preferences
    
    # If we have a UserPreferences object, convert it to dict for merging
    if request_preferences:
        # Convert UserPreferences to dict and merge with base config
        preferences_dict = user_preferences_to_dict(request_preferences)
        return merge_configs(base_config, preferences_dict)
    else:
        # Fall back to direct dictionary merging
        return merge_configs(base_config, request_config_override)

# API Routes
@api_blueprint.route('/generate-post', methods=['POST'])
def generate_post():
    """
    Generate a social media post from blog content.
    
    Can be configured in two ways:
    1. Through X-Config headers (recommended for simple overrides)
    2. By sending a UserPreferences object directly in the request body
    
    Returns:
        JSON response with generated post
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Check if a UserPreferences object was provided in the request body
        user_prefs_dict = data.get('user_preferences')
        
        # If user preferences were provided in the body, use them instead of headers
        if user_prefs_dict:
            # Create UserPreferences from the provided dictionary
            preferences = dict_to_user_preferences(user_prefs_dict)
            # Convert to dict for merging with base config
            preferences_dict = user_preferences_to_dict(preferences)
            effective_config = merge_configs(base_config, preferences_dict)
        else:
            # Use header-based configuration
            effective_config = get_effective_config()
        
        # Extract source from request body or use default
        rss_source = data.get('source', 'codingoni')  # Default to codingoni
        
        # Initialize globals and check for new blog
        is_new_blog = init_globals_if_needed()
        if not is_new_blog:
            return jsonify({
                "success": False,
                "error": "No new blog detected"
            }), 404
            
        # Get blog ID to check for duplicates
        blog_state = get_prompt_globals()
        raw_blog = blog_state.get("raw_blog", {})
        blog_id = raw_blog.get("id") if isinstance(raw_blog, dict) else None
        
        # Check if this blog has already been posted
        if blog_id and is_blog_already_posted(blog_id):
            return jsonify({
                "success": False,
                "error": f"Blog ID {blog_id} has already been posted"
            }), 409  # Conflict status code
        
        # Run the bot with the effective configuration
        run_bot(rss_source, override_config=effective_config)
        
        return jsonify({
            "success": True,
            "message": "Post generated and published successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_blueprint.route('/status', methods=['GET'])
def check_status():
    """
    Check the status of the bot and API.
    
    Can be configured in two ways:
    1. Through X-Config headers (recommended for simple overrides)
    2. By sending a UserPreferences object directly in the request query parameters
    
    Returns:
        JSON response with status information
    """
    try:
        # Get query parameters
        data = request.args.to_dict()
        
        # Check if a UserPreferences object was provided in the query parameters
        user_prefs_json = data.get('user_preferences')
        
        # If user preferences were provided, use them instead of headers
        if user_prefs_json:
            try:
                user_prefs_dict = json.loads(user_prefs_json)
                # Create UserPreferences from the provided dictionary
                preferences = dict_to_user_preferences(user_prefs_dict)
                # Convert to dict for merging with base config
                preferences_dict = user_preferences_to_dict(preferences)
                effective_config = merge_configs(base_config, preferences_dict)
            except json.JSONDecodeError:
                return jsonify({
                    "success": False,
                    "error": "Invalid JSON in user_preferences parameter"
                }), 400
        else:
            # Use header-based configuration
            effective_config = get_effective_config()
        
        # Get LinkedIn profile ID if configured
        linkedin_enabled = effective_config.get('social_media_to_post_to', {}).get('linkedin', {}).get('enabled', False)
        linkedin_profile_id = get_linkedin_profile_id() if linkedin_enabled else None
        
        return jsonify({
            "success": True,
            "status": "operational",
            "api_version": "1.0.0",
            "config": {
                "linkedin_enabled": linkedin_enabled,
                "linkedin_profile_id": linkedin_profile_id,
                "ai_provider": effective_config.get('ai', {}).get('text', {}).get('generate_text', {}).get('LLM', 'unknown')
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_blueprint.route('/test', methods=['GET'])
def run_test():
    """
    Run a test to verify the API is functioning.
    
    Can be configured in two ways:
    1. Through X-Config headers (recommended for simple overrides)
    2. By sending a UserPreferences object directly in the request query parameters
    
    Returns:
        JSON response with test results
    """
    try:
        # Get query parameters
        data = request.args.to_dict()
        
        # Check if a UserPreferences object was provided in the query parameters
        user_prefs_json = data.get('user_preferences')
        
        # If user preferences were provided, use them instead of headers
        if user_prefs_json:
            try:
                user_prefs_dict = json.loads(user_prefs_json)
                # Create UserPreferences from the provided dictionary
                preferences = dict_to_user_preferences(user_prefs_dict)
                # Convert to dict for merging with base config
                preferences_dict = user_preferences_to_dict(preferences)
                effective_config = merge_configs(base_config, preferences_dict)
            except json.JSONDecodeError:
                return jsonify({
                    "success": False,
                    "error": "Invalid JSON in user_preferences parameter"
                }), 400
        else:
            # Use header-based configuration
            effective_config = get_effective_config()
        
        # Perform a basic test without actually running the bot
        test_result = {
            "config_loaded": effective_config is not None,
            "ai_provider": effective_config.get('ai', {}).get('text', {}).get('generate_text', {}).get('LLM', 'unknown'),
            "linkedin_enabled": effective_config.get('social_media_to_post_to', {}).get('linkedin', {}).get('enabled', False),
        }
        
        return jsonify({
            "success": True,
            "test_result": test_result,
            "message": "API test completed successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
