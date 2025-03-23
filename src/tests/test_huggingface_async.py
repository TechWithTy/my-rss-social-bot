import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from models.huggingface_generator import run_huggingface_pipeline

@pytest.mark.asyncio
async def test_run_huggingface_pipeline():
    result = run_huggingface_pipeline()  # username for blog content

    assert isinstance(result, dict), "Expected pipeline to return a dict"
    assert result.get("status") != "failed", f"❌ Hugging Face text generation failed: {result.get('response')}"
    assert isinstance(result.get("response"), str), "Expected 'response' to be a string"
    assert len(result.get("response").strip()) > 0, "Text response is empty"

    print("\n📝 Hugging Face text:", result)
    # print("\n📝 Hugging Face text:", result.get("response"))

    if "image_url" in result:
        assert result["image_url"].startswith("http"), "Expected a valid image URL"
        print("\n🖼️ Hugging Face image:", result["image_url"])
