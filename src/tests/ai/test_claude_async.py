import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.claude_generator import send_message_to_claude

from utils.prompt_builder import init_globals_for_test, get_prompt_globals # ✅ This will ensure blog + prompt vars are initialized

# Initialize the state
init_globals_for_test()

# Get the shared global state
state = get_prompt_globals()

prompt = state["prompt"]
creative_prompt = state["creative_prompt"]
gif_prompt = state["gif_prompt"]
hashtags = state["hashtags"]
system_instructions = state["system_instructions"]
blog_content = state["blog_content"]

@pytest.mark.asyncio
async def test_send_message_to_claude():
    sample_blog = (
        "Claude AI is making waves in 2024. Here's how it's revolutionizing AI-driven communication in tech and business."
    )

    result = send_message_to_claude()

    assert isinstance(result, dict), "❌ Expected result to be a dictionary"

    print("\n📬 Claude Test Response:")
    print("📊 Status:", result.get("status"))
    print("📥 Response:", result.get("response"))
    print("📦 Message:", result.get("message"))

    print("🔍 Status Code:", result.get("status_code"))

    if result.get("status") == "success":
        assert isinstance(result.get("response"), str), "❌ Claude response should be a string"
        assert len(result.get("response").strip()) > 0, "❌ Claude response should not be empty"
    else:
        # Log full details on error
        print("❌ Claude returned an error.")
        print("🧾 Full Error Info:", result.get("raw"))
        pytest.fail(f"Claude failed: {result.get('response')}")
