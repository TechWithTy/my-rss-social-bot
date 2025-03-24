from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup, Tag  # ✅ Import `Tag` explicitlyfrom tabulate import tabulate
import os
from tabulate import tabulate
from utils.medium_helper import (
    load_blog_cache,
    save_blog_cache,
    delete_blog_cache,
    is_blog_cache_valid,
    extract_blog_media
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
    Fetches blog posts from a Medium user's RSS feed along with their profile avatar.

    Args:
        username (str): Medium username (without '@')

    Returns:
        dict: Contains 'user_avatar' (str) and 'blogs' (list of blog posts)
    """
    medium_feed_url = f"https://medium.com/feed/@{username}"
    feed = feedparser.parse(medium_feed_url)

    # Fetch user avatar
    user_avatar = get_medium_avatar(username)
    print("User AVatar",  user_avatar,username)
    blogs: List[Dict[str, Any]] = []
    for entry in feed.entries:
        # ✅ Ensure `categories` is always a List[str]
        if hasattr(entry, "tags"):
            categories = [tag["term"] for tag in entry.tags if isinstance(tag, dict) and "term" in tag]
        else:
            categories = ["Uncategorized"]

        content_html = entry.content[0].value if hasattr(entry, "content") else entry.summary

        blogs.append({
            "id": entry.id,
            "title": entry.title,
            "link": entry.link,
            "categories": ", ".join(str(category) for category in categories) if categories else "Uncategorized",
            "author": entry.author if hasattr(entry, "author") else username,
            "published": entry.published,
            "summary": entry.summary,
            "content": content_html,
        })

    return {
        "user_avatar": user_avatar,
        "blogs": blogs
    }


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
    print("fetch_latest_medium_blog() called from:\n", "".join(traceback.format_stack()))
    try:
        print("🔹 Checking blog cache validity...")
        cached_data = load_blog_cache() if is_blog_cache_valid() else None
        cached_latest_id = (
            cached_data["blogs"][0]["id"]
            if cached_data and cached_data.get("blogs")
            else None
        )

        print("🔄 Fetching fresh Medium blogs...")
        fresh_data = get_medium_blogs(username)
        fresh_blogs = fresh_data.get("blogs", [])
        if not fresh_blogs:
            print("❌ No blogs found in the feed.")
            return None

        fresh_latest_id = fresh_blogs[0]["id"]

        # Debug logs to trace comparison
        print(f"🧾 Cached blog ID: {cached_latest_id}")
        print(f"🆕 Fresh blog ID: {fresh_latest_id}")

        if cached_latest_id == fresh_latest_id:
            print("🟢 Latest blog already cached. No new blog to parse.")
            return None  # Exit here with a clear message

        # Otherwise, we have a new blog entry
        print("🆕 New blog detected")

        # At this point, fresh_data should be our new blogs_data
        blogs_data = fresh_data
        latest_blog = blogs_data["blogs"][0]

        media = extract_blog_media(latest_blog["content"])

        return {
            "user_avatar": get_medium_avatar(username),
            "all_blogs": blogs_data["blogs"],
            "latest_blog": latest_blog,
            "latest_blog_links": media["links"],
            "latest_blog_images": media["images"],
            "latest_blog_embeds": media["embeds"],
        }

    except Exception as e:
        print(f"❌ Error fetching Medium blogs: {e}")
        return None
