import pytest
import asyncio

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.pollinations_async import (
    generate_image,
    list_image_models,
    generate_text,
    generate_text_advanced,
    generate_audio,
    list_text_models,
    fetch_image_feed,
    fetch_text_feed,
)
from data.example_blog import example_blog
from medium_bot import fetch_latest_medium_blog
from utils.index import parse_html_blog_content


def fetch_and_parse_blog(username: str) -> str | None:
    blog_content = fetch_latest_medium_blog(username)
    if not blog_content:
        print("ℹ️ No blog content found.")
        return None
    return parse_html_blog_content(blog_content)


TEST_PROMPT = "hello world"
TEST_IMAGE_PROMPT = "a futuristic city skyline at sunset"
TEST_PAYLOAD = {
    "prompt": TEST_PROMPT,
    "model": "llama2"  # This should match a valid model if required
}

@pytest.mark.asyncio
async def test_generate_image():
    url = await generate_image(TEST_IMAGE_PROMPT)
    assert url is not None
    print(f"✅ generate_image passed: {url}")


@pytest.mark.asyncio
async def test_list_image_models():
    models = await list_image_models()
    assert models is not None, "Expected models to be non-None"
    assert isinstance(models, list), "Expected a list of image model names"
    assert all(isinstance(m, str) for m in models), "All items should be strings"

@pytest.mark.asyncio
async def test_generate_text():
    result = await generate_text(TEST_PROMPT)
    assert result is not None and isinstance(result, str)
    print(f"✅ generate_text passed: {result[:60]}...")


@pytest.mark.asyncio
async def test_generate_text_advanced():
    result = await generate_text_advanced(TEST_PAYLOAD)
    assert result is not None and isinstance(result, dict)
    print(f"✅ generate_text_advanced passed. Keys: {list(result.keys())}")


@pytest.mark.asyncio
async def test_generate_audio():
    audio_url = await generate_audio(TEST_PROMPT, voice="nova")
    assert audio_url is not None
    print(f"✅ generate_audio passed: {audio_url}")



@pytest.mark.asyncio
async def test_list_text_models():
    models = await list_text_models()
    assert models is not None, "Expected models to be non-None"
    assert isinstance(models, list), "Expected a list of text model dictionaries"
    assert all(isinstance(m, dict) for m in models), "All items should be dictionaries"
    assert all("name" in m and "description" in m for m in models), "Each model should have 'name' and 'description'"



# @pytest.mark.asyncio
# async def test_fetch_image_feed():
#     feed = await fetch_image_feed()
#     assert feed is not None and isinstance(feed, dict)
#     print("✅ fetch_image_feed passed.")


# @pytest.mark.asyncio
# async def test_fetch_text_feed():
#     feed = await fetch_text_feed()
#     assert feed is not None and isinstance(feed, dict)
#     print("✅ fetch_text_feed passed.")
