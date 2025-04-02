import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
import os
from tabulate import tabulate
import traceback
from utils.helpers.blog_rss_helper import extract_blog_media  # reuse your media utility

# You can adapt this if your WordPress site structure is different
def get_wordpress_avatar(base_url: str) -> str:
    """
    Fetches avatar or icon image from a WordPress site via meta tag.

    Args:
        base_url (str): The base URL of the WordPress blog.

    Returns:
        str: Avatar/icon URL or a fallback image.
    """
    try:
        response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except Exception as e:
        print(f"Error fetching WordPress avatar: {e}")

    return "https://s.w.org/about/images/logos/wordpress-logo-notext-rgb.png"


def get_wordpress_blogs(base_url: str, tag: str = None) -> Dict[str, Any]:
    """
    Fetches blog posts from a WordPress RSS feed.

    Args:
        base_url (str): The base URL of the WordPress site.
        tag (str, optional): A tag to filter posts.

    Returns:
        dict: Contains 'user_avatar' and 'blogs' list
    """
    feed_url = f"{base_url.rstrip('/')}/tag/{tag}/feed" if tag else f"{base_url.rstrip('/')}/feed"

    feed = feedparser.parse(feed_url)
    user_avatar = get_wordpress_avatar(base_url)

    blogs: List[Dict[str, Any]] = []

    for entry in feed.entries:
        tags_list = [tag["term"] for tag in entry.get("tags", [])] if "tags" in entry else []
        content_html = entry.content[0].value if "content" in entry else entry.get("summary", "")

        blogs.append({
            "id": entry.get("id", entry.get("link")),
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "tags": tags_list,
            "categories": ", ".join(tags_list),
            "author": entry.get("author", "No author"),
            "published": entry.get("published", "No publish date"),
            "summary": entry.get("summary", "No summary"),
            "content": content_html
        })

    return {
        "user_avatar": user_avatar,
        "blogs": blogs
    }


def display_blogs_table(blogs: List[Dict[str, Any]]) -> None:
    if not blogs:
        print("No blogs found.")
        return

    table_data = [
        [idx + 1, blog["title"], blog["categories"], blog["published"], blog["link"]]
        for idx, blog in enumerate(blogs)
    ]
    headers = ["#", "Title", "Categories", "Published", "Link"]
    print(tabulate(table_data, headers, tablefmt="grid"))


def fetch_latest_wordpress_blog(base_url: str, tag: Optional[str] = None) -> Optional[Dict[str, Any]]:
    print("fetch_latest_wordpress_blog() called from:\n", "".join(traceback.format_stack()))

    try:
        fresh_data = get_wordpress_blogs(base_url, tag=tag)
        fresh_blogs = fresh_data.get("blogs", [])

        if not fresh_blogs:
            print("❌ No blogs found in the feed.")
            return None

        latest_blog = fresh_blogs[0]
 
        media = extract_blog_media(latest_blog["content"])

        return {
            "user_avatar": fresh_data["user_avatar"],
            "all_blogs": fresh_data["blogs"],
            "latest_blog": latest_blog,
            "latest_blog_links": media["links"],
            "latest_blog_images": media["images"],
            "latest_blog_embeds": media["embeds"]
        }

    except Exception as e:
        print(f"❌ Error fetching WordPress blogs: {e}")
        return None


if __name__ == "__main__":
    wp_site = "https://wordpress.org/news"
    data = fetch_latest_wordpress_blog(wp_site)
    if data:
        display_blogs_table(data["all_blogs"])
