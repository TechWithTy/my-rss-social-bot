import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rss_feed.wordpress_bot import (
    get_wordpress_avatar,
    get_wordpress_blogs,
    fetch_latest_wordpress_blog,
)

TEST_WP_URL = "https://wordpress.org/news"

@pytest.mark.asyncio
async def test_get_wordpress_avatar():
    avatar_url = get_wordpress_avatar(TEST_WP_URL)
    print("🧑‍🎨 WordPress Avatar URL:", avatar_url)
    assert avatar_url.startswith("http")

@pytest.mark.asyncio
async def test_get_wordpress_blogs():
    result = get_wordpress_blogs(TEST_WP_URL)
    print("📝 WordPress Blogs:", result)
    assert isinstance(result, dict)
    assert "user_avatar" in result
    assert "blogs" in result
    assert isinstance(result["blogs"], list)
    assert len(result["blogs"]) > 0
    assert "title" in result["blogs"][0]

@pytest.mark.asyncio
async def test_fetch_latest_wordpress_blog():
    result = fetch_latest_wordpress_blog(TEST_WP_URL)
    print("🆕 Latest WP Blog:", result)
    if result is not None:
        assert "latest_blog" in result
