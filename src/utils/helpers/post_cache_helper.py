import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Define the directory and ensure it exists
TEMP_FOLDER = '_temp'
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Define the storage file path within the _temp directory
LINKEDIN_POST_STORAGE_FILE = os.path.join(TEMP_FOLDER, 'linkedin_post_cache.json')

def load_linkedin_post_cache() -> Dict[str, Any]:
    """
    Loads the LinkedIn post cache from JSON file.
    
    Returns:
        Dict[str, Any]: Dictionary containing post history with 'posts' list
    """
    if not os.path.exists(LINKEDIN_POST_STORAGE_FILE):
        return {"posts": []}
    
    with open(LINKEDIN_POST_STORAGE_FILE, 'r') as file:
        try:
            data = json.load(file)
            # Ensure proper structure
            if isinstance(data, list):
                # Convert old format to new structure
                return {"posts": data}
            elif isinstance(data, dict) and "posts" in data:
                return data
            else:
                # Initialize with proper structure
                return {"posts": []}
        except json.JSONDecodeError:
            print("⚠️ LinkedIn post cache file is corrupted. Returning empty cache.")
            return {"posts": []}

def save_linkedin_post_cache(post_data: Dict[str, Any]) -> None:
    """
    Saves LinkedIn post cache to JSON file.
    
    Args:
        post_data (Dict[str, Any]): Dictionary containing post history with 'posts' list
    """
    # Ensure proper structure
    if not isinstance(post_data, dict):
        post_data = {"posts": post_data if isinstance(post_data, list) else []}
    elif "posts" not in post_data:
        post_data["posts"] = []
        
    with open(LINKEDIN_POST_STORAGE_FILE, 'w') as file:
        json.dump(post_data, file, indent=2)

def delete_linkedin_post_cache() -> None:
    """
    Deletes the LinkedIn post cache file if it exists.
    """
    if os.path.exists(LINKEDIN_POST_STORAGE_FILE):
        os.remove(LINKEDIN_POST_STORAGE_FILE)
        print("🗑️ LinkedIn post cache deleted.")
    else:
        print("ℹ️ No LinkedIn post cache file to delete.")

def add_linkedin_post(post_text: str, blog_id: Optional[str], media_url: Optional[str] = None, media_type: Optional[str] = None, post_url: Optional[str] = None) -> None:
    """
    Adds a LinkedIn post to the cache with metadata and tracking information.
    
    Args:
        post_text (str): The text content of the posted message
        blog_id (Optional[str]): Reference to the blog ID this post was created from
        media_url (Optional[str]): URL of the image, GIF, or video used in the post
        media_type (Optional[str]): Type of media (IMAGE, GIF, VIDEO)
        post_url (Optional[str]): URL of the LinkedIn post if available
    """
    cache = load_linkedin_post_cache()
    
    # Create post record
    post_record = {
        "platform": "linkedin",
        "post_text": post_text,
        "blog_id": blog_id,
        "media_url": media_url,
        "media_type": media_type,
        "post_url": post_url,
        "timestamp": datetime.now().isoformat(),
        "id": f"post_{len(cache['posts']) + 1}"
    }
    
    # Add to the beginning of the list (most recent first)
    cache["posts"].insert(0, post_record)
    
    # Save updated cache
    save_linkedin_post_cache(cache)
    print("💾 LinkedIn post successfully saved to cache.")

def is_linkedin_post_cache_valid() -> bool:
    """
    Checks if the LinkedIn post cache file exists and contains a valid structure.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    print(f"🧪 Checking if LinkedIn post cache file exists at: {LINKEDIN_POST_STORAGE_FILE}")
    if not os.path.exists(LINKEDIN_POST_STORAGE_FILE):
        print("❌ LinkedIn post cache file does not exist.")
        return False

    try:
        with open(LINKEDIN_POST_STORAGE_FILE, 'r') as file:
            raw = file.read()
            print(f"📦 Raw LinkedIn post cache content:\n{raw[:300]}...")
            data = json.loads(raw)
            
            if not isinstance(data, dict) or "posts" not in data:
                print("❌ Invalid structure. Expected dict with 'posts' key.")
                return False

            posts = data["posts"]
            if not isinstance(posts, list):
                print("❌ 'posts' key is not a list.")
                return False

            print("✅ LinkedIn post cache is valid.")
            return True

    except Exception as e:
        print(f"❌ Error reading or parsing LinkedIn post cache file: {e}")
        return False


def is_blog_already_posted(blog_id: str) -> bool:
    """
    Check if a blog with the given ID has already been posted to LinkedIn.
    
    Args:
        blog_id (str): The blog ID to check
        
    Returns:
        bool: True if the blog has already been posted, False otherwise
    """
    if not blog_id:
        return False
        
    try:
        cache = load_linkedin_post_cache()
        
        # Check if any post in cache has the same blog_id
        for post in cache.get("posts", []):
            if post.get("blog_id") == blog_id:
                print(f"⚠️ Blog ID {blog_id} has already been posted to LinkedIn")
                return True
                
        return False
    except Exception as e:
        print(f"❌ Error checking for duplicate blog posts: {e}")
        return False
