from flask import Flask, request, jsonify
import os
import sys
import asyncio
import traceback

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.config_loader import config

from src.socials.linkedin_bot import get_linkedin_profile_id, post_to_linkedin

from src.utils.blog_rss_helper import load_blog_cache
from src.utils.prompt_builder import set_prompt_globals
from src.utils.dispatch.dispatch_text import dispatch_text_pipeline
# Import the Flask app from config_api.py
from src.api.config_api import app
@app.route('/api/status', methods=['GET'])
def get_status():
    """
    API endpoint to check the status of the bot or API.
    
    Returns:
        JSON response with system status
    """
    try:
        # Check configuration
        medium_username = config["user_profile"].get("medium_username")
        wix_url = config["user_profile"].get("wix_url")
        wordpress_url = config["user_profile"].get("wordpress_url")
        
        # Check LinkedIn configuration
        linkedin_enabled = config["social_media_to_post_to"]["linkedin"].get("enabled", False)
        
        # Check AI models
        text_model = config["ai"]["text"]["generate_text"]["LLM"]
        image_provider = config["ai"]["creative"]["generate_image"]["LLM"]
        
        # Get blog cache status
        blog_cache = load_blog_cache()
        blog_count = len(blog_cache) if isinstance(blog_cache, list) else (
            len(blog_cache.get("blogs", [])) if isinstance(blog_cache, dict) else 0
        )
        
        # Return status information
        return jsonify({
            'status': 'success',
            'system_status': 'online',
            'config': {
                'rss_sources': {
                    'medium_username': medium_username,
                    'wix_url': wix_url,
                    'wordpress_url': wordpress_url
                },
                'social_media': {
                    'linkedin_enabled': linkedin_enabled
                },
                'ai_models': {
                    'text_model': text_model,
                    'image_provider': image_provider
                }
            },
            'blog_cache': {
                'count': blog_count
            }
        }), 200
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving status: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/test', methods=['GET'])
def run_tests():
    """
    API endpoint to run automated tests to ensure everything is working correctly.
    
    Query parameters:
        test_type: Type of test to run (default: 'basic')
    
    Returns:
        JSON response with test results
    """
    try:
        test_type = request.args.get('test_type', 'basic')
        test_results = {}
        
        # Basic connectivity tests
        if test_type == 'basic' or test_type == 'all':
            test_results['config'] = {
                'status': 'success',
                'message': 'Configuration loaded successfully'
            }
            
            # Test LinkedIn connectivity
            try:
                profile_id = get_linkedin_profile_id()
                test_results['linkedin'] = {
                    'status': 'success' if profile_id else 'error',
                    'message': 'LinkedIn authentication successful' if profile_id else 'LinkedIn authentication failed'
                }
            except Exception as e:
                test_results['linkedin'] = {
                    'status': 'error',
                    'message': f'LinkedIn authentication error: {str(e)}'
                }
        
        # Test text generation
        if test_type == 'text' or test_type == 'all':
            try:
                # Set up test data
                set_prompt_globals(
                    raw_blog={
                        "content": "This is a test blog post for API testing.",
                        "title": "Test Blog Post",
                        "link": "https://example.com/test-post",
                        "id": "test-post-123"
                    },
                    blog_content="This is a test blog post for API testing.",
                    blog_title="Test Blog Post",
                    blog_url="https://example.com/test-post"
                )
                
                # Test text generation
                text_model = config["ai"]["text"]["generate_text"]["LLM"]
                post = dispatch_text_pipeline(text_model)
                
                test_results['text_generation'] = {
                    'status': 'success' if post and 'Text' in post else 'error',
                    'message': 'Text generation successful' if post and 'Text' in post else 'Text generation failed',
                    'sample': post.get('Text', '')[:100] + '...' if post and 'Text' in post else None
                }
            except Exception as e:
                test_results['text_generation'] = {
                    'status': 'error',
                    'message': f'Text generation error: {str(e)}'
                }
        
        # Return test results
        return jsonify({
            'status': 'success',
            'message': 'Tests completed',
            'test_type': test_type,
            'results': test_results
        }), 200
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error running tests: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500
