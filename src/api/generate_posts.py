from flask import Flask, request, jsonify
import os
import sys
import asyncio
import traceback

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.config_loader import config
from src.socials.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.socials.giphy import giphy_find_with_metadata, extract_social_upload_metadata
from src.utils.dispatch.dispatch_text import dispatch_text_pipeline
from src.utils.dispatch.dispatch_image import dispatch_image_pipeline
from src.utils.blog_rss_helper import load_blog_cache, save_blog_cache
from src.utils.prompt_builder import init_globals_if_needed, get_prompt_globals, set_prompt_globals

# Import the Flask app from config_api.py
from src.api.config_api import app

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """
    API endpoint to generate a social media post from blog content.
    
    Expected JSON format:
    {
        "blog_content": "Content of the blog post",
        "blog_title": "Title of the blog post",
        "blog_url": "URL of the blog post",
        "text_model": "Optional model name for text generation"
    }
    
    Returns:
        JSON response with the generated post
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'blog_content' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing blog_content in request'
            }), 400
        
        # Initialize global state with blog data
        blog_data = {
            "content": data.get('blog_content', ''),
            "title": data.get('blog_title', ''),
            "link": data.get('blog_url', ''),
            "id": data.get('blog_url', 'custom-post-' + str(hash(data.get('blog_title', ''))))
        }
        
        # Set global state for prompt generation
        set_prompt_globals(
            raw_blog=blog_data,
            blog_content=data.get('blog_content', ''),
            blog_title=data.get('blog_title', ''),
            blog_url=data.get('blog_url', '')
        )
        
        # Use specified text model or default from config
        text_model = data.get('text_model', config["ai"]["text"]["generate_text"]["LLM"])
        
        # Generate post content
        post = dispatch_text_pipeline(text_model)
        
        # Check if we need to add a GIF
        gif_tags = post.get("GifSearchTags", [])
        if gif_tags:
            gif_result = giphy_find_with_metadata(gif_tags)
            gif_obj = gif_result.get("result", {}).get("gif")
            if gif_obj:
                post["GifAsset"] = extract_social_upload_metadata(gif_obj)
        
        # Return the generated post
        return jsonify({
            'status': 'success',
            'message': 'Post generated successfully',
            'post': post
        }), 200
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error generating post: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/trigger-workflow', methods=['POST'])
def trigger_workflow():
    """
    API endpoint to manually trigger the whole workflow.
    
    Expected JSON format:
    {
        "rss_source": "medium_username or URL",
        "force_update": false  # Optional, force update even if no new blog
    }
    
    Returns:
        JSON response with workflow status
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'rss_source' not in data:
            # If no RSS source specified, use the one from config
            medium_username = config["user_profile"].get("medium_username")
            wix_url = config["user_profile"].get("wix_url")
            wordpress_url = config["user_profile"].get("wordpress_url")
            
            # Collect enabled sources
            enabled_sources = [
                source for source in [medium_username, wix_url, wordpress_url] if source
            ]
            
            if len(enabled_sources) > 1:
                return jsonify({
                    'status': 'error',
                    'message': 'Only one RSS source can be enabled at a time. Please check your config!'
                }), 400
            elif not enabled_sources:
                return jsonify({
                    'status': 'error',
                    'message': 'No RSS source configured. Please specify an RSS source or configure one in the config file.'
                }), 400
            
            rss_source = enabled_sources[0]
        else:
            rss_source = data['rss_source']
        
        force_update = data.get('force_update', False)
        
        # Initialize global state
        is_new_blog = init_globals_if_needed()
        
        if not is_new_blog and not force_update:
            return jsonify({
                'status': 'info',
                'message': 'No new blog detected — skipping generation and post.'
            }), 200
        
        # Get LinkedIn configuration
        linkedin_enabled = config["social_media_to_post_to"]["linkedin"].get("enabled", False)
        
        if not linkedin_enabled:
            return jsonify({
                'status': 'info',
                'message': 'LinkedIn posting is disabled in config. Enable it to post to LinkedIn.'
            }), 200
        
        # Authenticate LinkedIn
        try:
            profile_id = get_linkedin_profile_id()
            if not profile_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Could not retrieve LinkedIn profile ID.'
                }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'LinkedIn authentication error: {str(e)}'
            }), 500
        
        # Prepare post
        text_model = config["ai"]["text"]["generate_text"]["LLM"]
        post = dispatch_text_pipeline(text_model)
        
        # Add GIF if needed
        gif_tags = post.get("GifSearchTags", [])
        if gif_tags:
            gif_result = giphy_find_with_metadata(gif_tags)
            gif_obj = gif_result.get("result", {}).get("gif")
            if gif_obj:
                post["GifAsset"] = extract_social_upload_metadata(gif_obj)
        
        # Check for media asset
        image_url = post.get("ImageAsset")
        gif_asset = post.get("GifAsset")
        
        # Generate fallback image if needed
        if not image_url and not gif_asset:
            image_provider = config["ai"]["creative"]["generate_image"]["LLM"]
            image_data = asyncio.run(dispatch_image_pipeline(image_provider))
            
            if image_data:
                if "ImageAsset" in image_data:
                    post["ImageAsset"] = image_data["ImageAsset"]
                elif "GifAsset" in image_data:
                    post["GifAsset"] = extract_social_upload_metadata(image_data["GifAsset"])
        
        # Assemble post content
        post_text = post.get("Text", "")
        hashtags = post.get("Hashtags", [])
        full_text = f"{post_text}\n{' '.join(hashtags)}" if hashtags else post_text
        
        gif_asset = post.get("GifAsset")
        image_url = post.get("ImageAsset")
        
        media_url = gif_asset.get("gif_url") if gif_asset else image_url
        media_type = "GIF" if gif_asset else "IMAGE" if image_url else None
        
        # Post to LinkedIn
        if media_url and media_type:
            try:
                # Uncomment to actually post to LinkedIn
                # post_to_linkedin(
                #     post_text=full_text,
                #     profile_id=profile_id,
                #     media_url=media_url,
                #     media_type=media_type
                # )
                
                # Update blog cache
                state = get_prompt_globals()
                raw_blog = state.get("raw_blog")
                
                if raw_blog:
                    cached = load_blog_cache()
                    
                    # Normalize the cache structure
                    if isinstance(cached, list):
                        cached = {"blogs": cached}
                    elif not isinstance(cached, dict):
                        cached = {"blogs": []}
                    elif "blogs" not in cached:
                        cached["blogs"] = []
                    
                    cached["blogs"].insert(0, raw_blog)  # Prepend newest blog
                    save_blog_cache(cached)
                
                return jsonify({
                    'status': 'success',
                    'message': 'Workflow completed successfully',
                    'post': {
                        'text': full_text,
                        'media_type': media_type,
                        'media_url': media_url
                    }
                }), 200
                
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Failed to post to LinkedIn: {str(e)}'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': 'No valid media asset was available'
            }), 500
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error triggering workflow: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# Add this to the end of config_api.py to include these routes
if __name__ == '__main__':
    app.run(debug=True, port=5000)