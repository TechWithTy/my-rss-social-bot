import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, List, Any, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
import traceback
from utils.medium_helper import extract_blog_media  # reuse your media utility


def get_wix_avatar(base_url: str) -> str:
    """
    Fetch a Wix site avatar using Open Graph image if available.

    Args:
        base_url (str): The Wix site URL.

    Returns:
        str: Image URL or a default placeholder.
    """
    try:
        response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
    except Exception as e:
        print(f"Error fetching Wix avatar: {e}")

    return "https://static.wixstatic.com/media/3ed8f1_default.jpg"  # default fallback image


def get_wix_blogs(base_url: str) -> Dict[str, Any]:
    """
    Fetches blog posts from a Wix RSS feed.

    Args:
        base_url (str): The base URL of the Wix blog.

    Returns:
        dict: Contains 'user_avatar' and 'blogs' list.
    """
    feed_url = f"{base_url.rstrip('/')}/blog-feed.xml"

    try:
        response = requests.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        print(f"Request error: {e}")
        return {"user_avatar": "", "blogs": []}

    feed = feedparser.parse(response.content)
    if feed.bozo:
        print(f"❌ Error parsing feed: {feed.bozo_exception}")
        return {"user_avatar": "", "blogs": []}

    user_avatar = get_wix_avatar(base_url)
    blogs: List[Dict[str, Any]] = []

    for entry in feed.entries:
        tags_list = [tag["term"] for tag in entry.get("tags", [])] if "tags" in entry else []
        content_html = entry.get("content", [{}])[0].get("value", "") if "content" in entry else entry.get("summary", "")

        blogs.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "link": entry.get("link"),
            "tags": tags_list,
            "categories": ", ".join(tags_list),
            "author": entry.get("author", "No author"),
            "published": entry.get("published"),
            "summary": entry.get("summary"),
            "content": content_html
        })

    return {
        "user_avatar": user_avatar,
        "blogs": blogs
    }


def fetch_latest_wix_blog(base_url: str) -> Optional[Dict[str, Any]]:
    print("fetch_latest_wix_blog() called from:\n", "".join(traceback.format_stack()))
    try:
        fresh_data = get_wix_blogs(base_url)
        fresh_blogs = fresh_data.get("blogs", [])

        if not fresh_blogs:
            print("❌ No blogs found in the feed.")
            return None

        latest_blog = fresh_blogs[0]

        media = extract_blog_media(latest_blog["content"])

        return {
            "user_avatar": fresh_data["user_avatar"],
            "all_blogs": fresh_blogs,
            "latest_blog": latest_blog,
            "latest_blog_links": media["links"],
            "latest_blog_images": media["images"],
            "latest_blog_embeds": media["embeds"]
        }

    except Exception as e:
        print(f"❌ Error fetching Wix blogs: {e}")
        return None

# if __name__ == "__main__":
#     wix_site = "https://www.zionadventurephotog.com"
#     data = fetch_latest_wix_blog(wix_site)

#     if data:
#         from tabulate import tabulate
#         table_data = [
#             [i+1, blog["title"], blog["categories"], blog["published"], blog["link"]]
#             for i, blog in enumerate(data["all_blogs"])
#         ]
#         print(tabulate(table_data, headers=["#", "Title", "Categories", "Published", "Link"], tablefmt="grid"))
