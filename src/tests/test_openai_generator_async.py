import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from models.openai_generator import run_openai_pipeline

@pytest.mark.asyncio
async def test_run_openai_pipeline():
    sample_blog = (
        "In today’s fast-paced world of AI, staying ahead means learning fast. "
        "Here are 5 tools every beginner should master in 2024. Let’s dive in!"
    )

    result = run_openai_pipeline(sample_blog)

    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert result.get("status") != "failed", f"❌ Assistant failed: {result.get('response')}"
    assert result.get("status") == "success", f"❌ Pipeline did not complete successfully: {result}"
    assert isinstance(result.get("response"), str), "Expected 'response' to be a string"
    assert len(result.get("response").strip()) > 0, "Response text should not be empty"

    print("\n✅ Assistant Output:\n", result["response"])
