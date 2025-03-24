import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from models.openai_generator import run_openai_pipeline
from utils.prompt_builder import init_globals_for_test
# Initialize the state
init_globals_for_test()

@pytest.mark.asyncio


async def test_run_openai_pipeline(initialized_prompt_state):
    prompt = initialized_prompt_state["prompt"]
    assert prompt is not None, "❌ Prompt is still None"
    print("👁️Open Ai Test print",prompt)
    result = run_openai_pipeline()
    assert isinstance(result, dict), "Expected result to be a dictionary"
    assert result.get("status") != "failed", f"❌ Assistant failed: {result.get('response')}"
    assert result.get("status") == "success", f"❌ Pipeline did not complete successfully: {result}"
    assert isinstance(result.get("response"), str), "Expected 'response' to be a string"
    assert len(result.get("response").strip()) > 0, "Response text should not be empty"

    print("\n✅ Assistant Output:\n", result["response"])
