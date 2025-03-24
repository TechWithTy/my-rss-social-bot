import sys
"""
    The function `test_run_huggingface_pipeline` is a pytest asynchronous test that checks the output of
    a Hugging Face text generation pipeline for specific conditions and prints the results.
"""
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import asyncio
from linkedin_bot import (
    get_linkedin_profile_id,
    get_linkedin_profile,
    upload_linkedin_media,
    post_to_linkedin
)

@pytest.mark.asyncio
async def test_get_linkedin_profile_id_async():
    profile_id = get_linkedin_profile_id()
    print("🆔 Profile ID:", profile_id)
    assert profile_id is not None
    assert isinstance(profile_id, str)
    assert len(profile_id) > 5

@pytest.mark.asyncio
async def test_get_linkedin_profile_async():
    profile = get_linkedin_profile()
    print("🧾 Profile:", profile)
    assert isinstance(profile, dict)
    assert "given_name" in profile
    assert "email" in profile

@pytest.mark.asyncio
async def test_upload_linkedin_media_image_async():
    profile_id = get_linkedin_profile_id()
    test_image_url = "https://placekitten.com/600/400"  # Replace with your actual media URL
    urn = upload_linkedin_media(profile_id, test_image_url, "IMAGE")
    print("🖼️ Media URN:", urn)
    assert urn is not None
    assert "urn:li:digitalmediaAsset" in urn

@pytest.mark.asyncio
async def test_upload_linkedin_media_gif_async():
    profile_id = get_linkedin_profile_id()
    test_gif_url = "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
    urn = upload_linkedin_media(profile_id, test_gif_url, "GIF")
    print("🎞️ GIF URN:", urn)
    assert urn is not None
    assert "urn:li:digitalmediaAsset" in urn

@pytest.mark.asyncio
async def test_upload_linkedin_media_video_async():
    profile_id = get_linkedin_profile_id()
    test_video_url = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
    urn = upload_linkedin_media(profile_id, test_video_url, "VIDEO")
    print("🎬 Video URN:", urn)
    assert urn is not None
    assert "urn:li:digitalmediaAsset" in urn

@pytest.mark.asyncio
async def test_post_to_linkedin_async():
    profile_id = get_linkedin_profile_id()
    test_text = "📢 Hello from automated test post!"
    post_to_linkedin(test_text, profile_id, media_url=None, media_type="NONE")
    assert True  # If no exception was raised, the post was successful
