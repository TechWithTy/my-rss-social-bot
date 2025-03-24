
import sys
"""
    The function `test_run_huggingface_pipeline` is a pytest asynchronous test that checks the output of
    a Hugging Face text generation pipeline for specific conditions and prints the results.
"""
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from rss_feed.medium_bot import (
    get_medium_avatar,
    get_medium_blogs,
    fetch_latest_medium_blog,
)

TEST_USERNAME = "codingoni"  # Replace with your Medium username if needed

@pytest.mark.asyncio
async def test_get_medium_avatar():
    avatar_url = get_medium_avatar(TEST_USERNAME)
    print("🧑‍🎨 Avatar URL:", avatar_url)
    assert avatar_url.startswith("http")
    assert avatar_url.endswith(".png") or ".medium.com" in avatar_url

@pytest.mark.asyncio
async def test_get_medium_blogs():
    result = get_medium_blogs(TEST_USERNAME)
    print("📝 Medium Blogs:", result)
    assert isinstance(result, dict)
    assert "user_avatar" in result
    assert "blogs" in result
    assert isinstance(result["blogs"], list)
    assert len(result["blogs"]) > 0
    assert "title" in result["blogs"][0]

@pytest.mark.asyncio
async def test_fetch_latest_medium_blog():
    result = fetch_latest_medium_blog(TEST_USERNAME)
    print("🆕 Latest Blog:", result)
    if result is not None:
        assert "latest_blog" in result
        assert "user_avatar" in result
        assert isinstance(result["latest_blog_images"], list)
    else:
        print("ℹ️ No new blog found or feed unavailable (valid outcome)")
        assert result is None or isinstance(result, dict)
