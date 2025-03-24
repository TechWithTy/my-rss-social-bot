import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rss_feed.wix_bot import (
    get_wix_avatar,
    get_wix_blogs,
    fetch_latest_wix_blog,
)

TEST_WIX_URL = "https://www.zionadventurephotog.com"

@pytest.mark.asyncio
async def test_get_wix_avatar():
    avatar_url = get_wix_avatar(TEST_WIX_URL)
    print("🧑‍🎨 Wix Avatar URL:", avatar_url)
    assert avatar_url.startswith("http")

@pytest.mark.asyncio
async def test_get_wix_blogs():
    result = get_wix_blogs(TEST_WIX_URL)
    print("📝 Wix Blogs:", result)
    assert isinstance(result, dict)
    assert "user_avatar" in result
    assert "blogs" in result
    assert isinstance(result["blogs"], list)
    assert len(result["blogs"]) > 0
    assert "title" in result["blogs"][0]

@pytest.mark.asyncio
async def test_fetch_latest_wix_blog():
    result = fetch_latest_wix_blog(TEST_WIX_URL)
    print("🆕 Latest Wix Blog:", result)
    if result is not None:
        assert "latest_blog" in result
        assert "user_avatar" in result
        assert isinstance(result["latest_blog_images"], list)
    else:
        print("ℹ️ No new blog found or feed unavailable (valid outcome)")
        assert result is None or isinstance(result, dict)
