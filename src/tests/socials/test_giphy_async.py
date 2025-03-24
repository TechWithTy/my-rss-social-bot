import sys
import os
import pytest

# Add src to PYTHONPATH for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from socials.giphy import giphy_find_with_metadata, extract_social_upload_metadata  # adjust path as needed
from utils.index import get_env_variable

@pytest.mark.asyncio
async def test_giphy_find_with_metadata_success():
    terms = ["celebration", "dance", "win"]
    result = giphy_find_with_metadata(terms)
    
    print("🧠 Giphy Response:", result)

    assert isinstance(result, dict)
    assert "result" in result
    assert "valid_terms" in result

    gif_data = result["result"].get("gif", {})
    assert isinstance(gif_data, dict)
    assert gif_data.get("type") == "gif"

    assert len(result["valid_terms"]) > 0
    assert any(term in terms for term in result["valid_terms"])


@pytest.mark.asyncio
async def test_extract_social_upload_metadata_from_giphy_gif():
    terms = ["funny"]
    search_result = giphy_find_with_metadata(terms)
    gif_data = search_result["result"].get("gif", {})

    assert gif_data, "No GIF returned from Giphy search."

    metadata = extract_social_upload_metadata(gif_data)

    print("📦 Extracted Metadata:", metadata)

    assert metadata["gif_url"].startswith("http")
    assert metadata["mp4_url"].startswith("http")
    assert metadata["webp_url"].startswith("http")
    assert metadata["giphy_page"].startswith("http")
    assert "title" in metadata
    assert "preview_image" in metadata
