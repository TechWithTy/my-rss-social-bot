

import feedparser
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

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
        categories = [tag["term"] for tag in entry.tags] if hasattr(entry, "tags") else ["Uncategorized"]
        content_html = entry.content[0].value if hasattr(entry, "content") else entry.summary

        blogs.append({
            "id": entry.id,
            "title": entry.title,
            "link": entry.link,
            "categories": ", ".join(categories),
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


# Example Usage
username = "codingoni"  # Change this to any Medium username
result = get_medium_blogs(username)

# Print the user avatar URL
print(f"\n🔹 User Avatar: {result['user_avatar']}")

# Display blogs in a table
display_blogs_table(result["blogs"])
