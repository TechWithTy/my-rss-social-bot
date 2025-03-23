import sys
import os
import pytest
import asyncio

# Add src path for module resolution
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
from medium_bot import fetch_latest_medium_blog
from utils.index import parse_html_blog_content


def fetch_and_parse_blog(username: str) -> str | None:
    blog_content = fetch_latest_medium_blog(username, False)
    if not blog_content:
        print("ℹ️ No blog content found for user:", username)
        return None
    return parse_html_blog_content(blog_content)


# Constants for tests
TEST_PROMPT = "hello world"
TEST_IMAGE_PROMPT = "a futuristic city skyline at sunset"
TEST_PAYLOAD = {
    "model": "llama2",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "hello world"}
    ]
}



@pytest.mark.asyncio
async def test_generate_image():
    url = await generate_image(TEST_IMAGE_PROMPT)
    assert url is not None and url.startswith("http"), "❌ generate_image should return a valid image URL"
    print(f"✅ generate_image passed:\n{url}")


@pytest.mark.asyncio
async def test_list_image_models():
    models = await list_image_models()
    assert models, "❌ No models returned by list_image_models"
    assert isinstance(models, list), "❌ Expected a list of image models"
    assert all(isinstance(m, str) for m in models), "❌ Each image model should be a string"
    print(f"✅ list_image_models returned {len(models)} models")


@pytest.mark.asyncio
async def test_generate_text_advanced():
    result = await generate_text_advanced(TEST_PAYLOAD)

    print("🧪 generate_text_advanced raw result:", result)

    assert isinstance(result, dict), "❌ Expected result to be a dictionary"

    if "error" in result:
        pytest.fail(f"❌ API error: {result['error']}")

    assert "text" in result or "output" in result, "❌ Missing expected keys in response"
    print("✅ generate_text_advanced passed.")


@pytest.mark.asyncio
async def test_generate_text_advanced():
    result = await generate_text_advanced(TEST_PAYLOAD)

    print("🧪 generate_text_advanced result:", result)

    assert result is not None, "❌ Expected a non-null string response"
    assert isinstance(result, str), "❌ Expected result to be a string"
    assert result.strip(), "❌ Response string should not be empty"

    print("✅ generate_text_advanced passed.")



@pytest.mark.asyncio
async def test_generate_audio():
    audio_url = await generate_audio(TEST_PROMPT, voice="nova")
    assert isinstance(audio_url, str) and audio_url.startswith("http"), "❌ generate_audio should return a valid audio URL"
    print(f"✅ generate_audio passed:\n{audio_url}")


@pytest.mark.asyncio
async def test_list_text_models():
    models = await list_text_models()
    assert models, "❌ No text models returned"
    assert isinstance(models, list), "❌ Expected a list of text model dictionaries"
    assert all(isinstance(m, dict) for m in models), "❌ Each text model should be a dictionary"
    assert all("name" in m and "description" in m for m in models), "❌ Each model should have 'name' and 'description'"
    print(f"✅ list_text_models returned {len(models)} models")


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
