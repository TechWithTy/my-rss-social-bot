from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup, Tag  # ✅ Import `Tag` explicitlyfrom tabulate import tabulate
import os
from tabulate import tabulate

TEMP_FOLDER = "_temp"
LAST_BLOG_FILE = os.path.join(TEMP_FOLDER, "last_post.txt")

def get_medium_avatar(username: str) -> Optional[str]:
    """
    Fetches the Medium user's profile avatar.

    Args:
        username (str): Medium username (without '@')

    Returns:
        Optional[str]: URL of the user's avatar or None if not found.
    """
    profile_url = f"https://medium.com/@{username}"
    response = requests.get(profile_url, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        avatar_tag = soup.find("img", {"class": "avatar-image"})

        # ✅ Ensure `avatar_tag` is a valid `Tag` before calling `.get()`
        if isinstance(avatar_tag, Tag):
            avatar_url = avatar_tag.get("src")
            return str(avatar_url) if avatar_url else None  # ✅ Ensure return type is `Optional[str]`

    return None  # ✅ Return `None` if no avatar is found

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




def ensure_temp_folder_exists() -> None:
    """Ensures the _temp folder exists."""
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)


def read_last_medium_blog() -> Optional[str]:
    """Reads the last processed blog post from a file in _temp."""
    ensure_temp_folder_exists()  # ✅ Ensure the folder exists before reading
    
    if os.path.exists(LAST_BLOG_FILE):
        with open(LAST_BLOG_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    
    return None


def write_last_medium_blog(blog_id: str) -> None:
    """Writes the last processed blog post to a file in _temp."""
    ensure_temp_folder_exists()  # ✅ Ensure the folder exists before writing
    
    with open(LAST_BLOG_FILE, "w", encoding="utf-8") as file:
        file.write(blog_id)
    
    print(f"✅ Saved last blog post ID: {blog_id}")


def delete_last_medium_blog() -> None:
    """Deletes the last processed blog post file from _temp."""
    if os.path.exists(LAST_BLOG_FILE):
        os.remove(LAST_BLOG_FILE)
        print("🗑️ Deleted last blog post record.")
    else:
        print("⚠️ No last blog post file found to delete.")
        
def fetch_latest_medium_blog(username: str,saveState: bool) -> Optional[str]:
    """
    Fetches the latest blog post from a Medium RSS feed.

    Args:
        username (str): Medium username.

    Returns:
        Optional[str]: Latest blog content if new, otherwise None.
    """
    try:
        print("🔹 Fetching latest blog post from Medium...")
        blogs = get_medium_blogs(username)["blogs"]

        if not blogs:
            print("❌ No blogs found. Exiting.")
            return None

        latest_blog = blogs[0]  # Most recent post
        last_processed_blog = read_last_medium_blog()

        if latest_blog["id"] == last_processed_blog:
            print("ℹ️ No new blog posts found.")
            return None

        # ✅ Save the new blog ID
        if saveState:
         write_last_medium_blog(latest_blog["id"])

        return latest_blog["content"]
    except Exception as e:
        print(f"❌ Error fetching Medium blogs: {e}")
        return None
