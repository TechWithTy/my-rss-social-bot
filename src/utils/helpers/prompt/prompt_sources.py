"""
prompt_sources.py
- Handles fetching and parsing blog content from Medium, Wix, and WordPress.
"""
from typing import Optional, Dict, Any
from utils.config.config_loader import config
from rss_feed.medium_bot import fetch_latest_medium_blog
from rss_feed.wix_bot import fetch_latest_wix_blog
from rss_feed.wordpress_bot import fetch_latest_wordpress_blog
from utils.index import parse_html_blog_content

user_config = config.get("user_profile", {})
medium_username = user_config.get("medium_username")
wix_url = user_config.get("wix_url")
wordpress_url = user_config.get("wordpress_url")

def fetch_and_parse_blog() -> Optional[dict]:
    """
    Fetch the latest blog from the first available source in order of priority: Medium → Wix → WordPress.
    Returns:
        Optional[dict]: Latest blog data if found, otherwise None.
    """
    sources = {
        "Medium": (medium_username, fetch_latest_medium_blog),
        "Wix": (wix_url, fetch_latest_wix_blog),
        "WordPress": (wordpress_url, fetch_latest_wordpress_blog),
    }
    print("Fetching blog from Medium, Wix, or WordPress...")
    response = None
    for platform, (identifier, fetch_function) in sources.items():
        if identifier:
            print(f"Fetching from {platform}...")
            response = fetch_function(identifier)
            if response:
                print(f"Successfully fetched blog from {platform}")
                break
    if response is None:
        print("No new blogs to parse — already up to date.")
        return None
    blog_json = response.get("latest_blog", {})
    blog_content = blog_json.get("content")
    blog_id = blog_json.get("id")
    blog_direct_link = response.get("latest_blog_direct_link")
    if not blog_content:
        print("No blog content found in the latest blog.")
        return None
    cleaned_blog_content = parse_html_blog_content(blog_content)
    return {
        "id": blog_id,
        "content": cleaned_blog_content,
        "raw": blog_json,
        "direct_link": blog_direct_link,
    }
