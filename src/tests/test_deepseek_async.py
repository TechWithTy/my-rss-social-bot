import sys
import os
import pytest

# Add src to PYTHONPATH for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.deepseek_generator import send_message_to_deepseek
from utils.prompt_builder import init_globals_for_test, get_prompt_globals

# Initialize the state
init_globals_for_test()



@pytest.mark.asyncio
async def test_send_message_to_deepseek():
    

    result = send_message_to_deepseek()
    print("🦈 DeepSeek Result",result)
    assert isinstance(result, dict), "❌ Expected result to be a dictionary"

    # If request failed, log it and fail the test
    if result.get("status") != "success":
        print("⚠️ DeepSeek returned a failure",result)
        print("📥 Response:", result.get("response"))
        print("🧾 Details:", result.get("details"))
        error_message = result.get("details", {}).get("raw", {}).get("error", {}).get("message")
        pytest.fail("❌ DeepSeek request did not succeed " + error_message)

    response_text = result.get("response")

    assert isinstance(response_text, str), "❌ 'response' should be a string"
    assert len(response_text.strip()) > 0, "❌ 'response' should not be empty"

    print("\n🧠 DeepSeek AI Response:\n", response_text)
