from flask import Flask, request, jsonify
import os
import sys
import asyncio
import traceback

# Add the project root to the path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.socials.linkedin_bot import get_linkedin_profile_id, post_to_linkedin

from src.utils.blog_rss_helper import load_blog_cache, save_blog_cache
from src.utils.prompt_builder import  get_prompt_globals

# Import the Flask app from config_api.py
from src.api.config_api import app

@app.route('/api/post-to-social', methods=['POST'])
def post_to_social():
    """
    API endpoint to post the generated content to selected social media platforms.
    
    Expected JSON format:
    {
        "post": {
            "Text": "Post text content",
            "Hashtags": ["#tag1", "#tag2"],
            "ImageAsset": "URL to image (optional)",
            "GifAsset": {
                "gif_url": "URL to GIF (optional)"
            }
        },
        "platforms": ["linkedin"]  # List of platforms to post to
    }
    
    Returns:
        JSON response with posting status
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'post' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing post data in request'
            }), 400
        
        post = data['post']
        platforms = data.get('platforms', ['linkedin'])
        results = {}
        
        # Assemble post content
        post_text = post.get("Text", "")
        hashtags = post.get("Hashtags", [])
        full_text = f"{post_text}\n{' '.join(hashtags)}" if hashtags else post_text
        
        gif_asset = post.get("GifAsset")
        image_url = post.get("ImageAsset")
        
        media_url = gif_asset.get("gif_url") if gif_asset else image_url
        media_type = "GIF" if gif_asset else "IMAGE" if image_url else None
        
        # Post to each platform
        if 'linkedin' in platforms:
            try:
                # Authenticate LinkedIn
                profile_id = get_linkedin_profile_id()
                if not profile_id:
                    results['linkedin'] = {
                        'status': 'error',
                        'message': 'Could not retrieve LinkedIn profile ID'
                    }
                else:
                    # Post to LinkedIn
                    if media_url and media_type:
                        # Uncomment to actually post to LinkedIn
                        # post_to_linkedin(
                        #     post_text=full_text,
                        #     profile_id=profile_id,
                        #     media_url=media_url,
                        #     media_type=media_type
                        # )
                        
                        # For now, just simulate success
                        results['linkedin'] = {
                            'status': 'success',
                            'message': 'LinkedIn post submitted successfully (simulation)',
                            'post_text': full_text,
                            'media_type': media_type,
                            'media_url': media_url
                        }
                        
                        # Update blog cache if blog data is available
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
                    else:
                        results['linkedin'] = {
                            'status': 'error',
                            'message': 'No valid media asset was available'
                        }
            except Exception as e:
                results['linkedin'] = {
                    'status': 'error',
                    'message': f'Failed to post to LinkedIn: {str(e)}'
                }
        
        # Return results
        return jsonify({
            'status': 'success',
            'message': 'Posting completed',
            'results': results
        }), 200
        
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error posting to social media: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500