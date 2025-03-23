import sys
import os
import pytest

# Add src to PYTHONPATH for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.deepseek_generator import send_message_to_deepseek

@pytest.mark.asyncio
async def test_send_message_to_deepseek():
    sample_blog = (
        "In 2024, emerging AI tools have changed how we work. "
        "Here are 5 innovations you can't afford to ignore if you're in tech."
    )

    result = send_message_to_deepseek(sample_blog)

    assert isinstance(result, dict), "❌ Expected result to be a dictionary"

    # If request failed, log it and fail the test
    if result.get("status") != "success":
        print("⚠️ DeepSeek returned a failure")
        print("📥 Response:", result.get("response"))
        print("🧾 Details:", result.get("details"))
        pytest.fail("❌ DeepSeek request did not succeed")

    response_text = result.get("response")

    assert isinstance(response_text, str), "❌ 'response' should be a string"
    assert len(response_text.strip()) > 0, "❌ 'response' should not be empty"

    print("\n🧠 DeepSeek AI Response:\n", response_text)
