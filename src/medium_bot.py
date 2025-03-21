from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

from typing import Optional
import requests
from bs4 import BeautifulSoup, Tag

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

        # ✅ Ensure avatar_tag is a Tag before calling .get()
        if isinstance(avatar_tag, Tag):
            avatar_url = avatar_tag.get("src")
            return avatar_url if isinstance(avatar_url, str) else None

    return None


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