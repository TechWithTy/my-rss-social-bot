import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
import os
from tabulate import tabulate
from utils.helpers.blog_rss_helper import (
    load_blog_cache,
    is_blog_cache_valid,
    extract_blog_media,
)
import traceback

TEMP_FOLDER = "_temp"
LAST_BLOG_FILE = os.path.join(TEMP_FOLDER, "last_post.txt")


def get_medium_avatar(username: str) -> str:
    """
    Fetch the Medium user's avatar by scraping their profile page.

    Args:
        username (str): Medium username (without '@')

    Returns:
        str: URL of the user's profile avatar or a default avatar.
    """
    profile_url = f"https://medium.com/@{username}"

    try:
        response = requests.get(profile_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Look for the Open Graph image tag (og:image) which contains the avatar
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except Exception as e:
        print(f"Error fetching avatar: {e}")

    # Return default avatar if not found
    return "https://cdn-images-1.medium.com/fit/c/64/64/1*2Y7paYtPz5-Nj0zTLOzSwg.png"


def get_medium_blogs(username: str) -> Dict[str, Any]:
    """
    Fetches blog posts from a Medium user's RSS feed, including their profile avatar, images, videos, and embeds.

    Args:
        username (str): Medium username (without '@')

    Returns:
        dict: Contains 'user_avatar' (str) and 'blogs' (list of blog posts)
    """
    medium_feed_url = f"https://medium.com/feed/@{username}"
    feed = feedparser.parse(medium_feed_url)

    # Fetch user avatar
    user_avatar = get_medium_avatar(username)
    print("User Avatar:", user_avatar)

    blogs: List[Dict[str, Any]] = []

    for entry in feed.entries:
        # ✅ Ensure `categories` is always a List[str]
        if hasattr(entry, "tags"):
            categories = [
                tag["term"]
                for tag in entry.tags
                if isinstance(tag, dict) and "term" in tag
            ]
        else:
            categories = ["Uncategorized"]

        content_html = (
            entry.content[0].value if hasattr(entry, "content") else entry.summary
        )

        # Extract media (images, videos, embeds)
        image_url, video_url, embed_url = None, None, None
        if content_html:
            soup = BeautifulSoup(content_html, "html.parser")

            # Extract first image
            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag else None

            # Extract first video (iframe embeds)
            iframe_tag = soup.find("iframe")
            video_url = iframe_tag["src"] if iframe_tag else None

            # Extract first embedded post (e.g., Twitter, Instagram, Medium embeds)
            embed_tag = soup.find("blockquote")
            embed_url = (
                embed_tag.find("a")["href"]
                if embed_tag and embed_tag.find("a")
                else None
            )

        blogs.append(
            {
                "id": entry.id,
                "title": entry.title,
                "link": entry.link,
                "categories": ", ".join(str(category) for category in categories)
                if categories
                else "Uncategorized",
                "author": entry.author if hasattr(entry, "author") else username,
                "published": entry.published,
                "summary": entry.summary,
                "content": content_html,
                "image": image_url,  # First image found
                "video": video_url,  # First video found (if any)
                "embed": embed_url,  # First embedded post (if any)
            }
        )

    return {"user_avatar": user_avatar, "blogs": blogs}


def display_blogs_table(blogs: List[Dict[str, Any]]) -> None:
    """
    Display blog posts in a formatted table using tabulate.

    Args:
        blogs (List[Dict[str, Any]]): List of blog post dictionaries.
    """
    if not blogs:
        print("No blogs found.")
        return

    table_data = [
        [idx + 1, blog["title"], blog["categories"], blog["published"], blog["link"]]
        for idx, blog in enumerate(blogs)
    ]

    headers = ["#", "Title", "Categories", "Published", "Link"]
    print(tabulate(table_data, headers, tablefmt="grid"))


def fetch_latest_medium_blog(username: str) -> Optional[Dict[str, Any]]:
    try:
        print(f"\n🔄 Starting Medium blog fetch for user: {username}")

        # Check cache
        print("🔍 Checking blog cache...")
        cache_valid = is_blog_cache_valid()
        print(f"🔍 Cache validity: {cache_valid}")

        cached_data = load_blog_cache() if cache_valid else None
        cached_latest_id = (
            cached_data["blogs"][0]["id"]
            if cached_data and cached_data.get("blogs")
            else None
        )
        print(f"🔍 Cached latest blog ID: {cached_latest_id}")

        # Fetch fresh data
        print("🌐 Fetching fresh Medium blogs...")
        fresh_data = get_medium_blogs(username)

        if not fresh_data:
            print("❌ Error: No data returned from get_medium_blogs")
            return None

        print(f"🌐 Received fresh data with keys: {fresh_data.keys()}")

        fresh_blogs = fresh_data.get("blogs", [])
        print(f"🌐 Found {len(fresh_blogs)} blogs in feed")

        if not fresh_blogs:
            print("❌ No blogs found in the feed.")
            return None

        fresh_latest_id = fresh_blogs[0]["id"]
        print(f"🆕 Fresh latest blog ID: {fresh_latest_id}")

        # Compare cached vs fresh
        if cached_latest_id == fresh_latest_id:
            print("🟢 Latest blog already cached. No new blog to parse.")
            return None

        print("🆕 New blog detected. Processing...")
        blogs_data = fresh_data
        latest_blog = blogs_data["blogs"][0]

        print(f"📰 Latest blog title: {latest_blog.get('title')}")
        print(f"🔗 Latest blog link: {latest_blog['link']}")
        print(f"🔗 Latest blog Content: {latest_blog['content']}")

        # Extract media
        print("🖼️ Extracting blog media...")
        media = extract_blog_media(latest_blog["content"])
        print(
            f"🖼️ Found {len(media['links'])} links, {len(media['images'])} images, {len(media['videos'])} videos"
        )

        # Get user avatar
        print("👤 Fetching user avatar...")
        avatar_url = get_medium_avatar(username)
        print(f"👤 Avatar URL: {avatar_url}")

        return {
            "user_avatar": avatar_url,
            "all_blogs": blogs_data["blogs"],
            "latest_blog": latest_blog,
            "latest_blog_direct_link": latest_blog["link"],
            "latest_blog_links": media["links"],
            "latest_blog_images": media["images"],
            "latest_blog_videos": media["videos"],
        }

    except Exception as e:
        print(f"\n❌ Error fetching Medium blog:")
        print(f"❌ Exception type: {type(e).__name__}")
        print(f"❌ Exception message: {str(e)}")
        print("❌ Stack trace:")
        print(traceback.format_exc())
        return None
