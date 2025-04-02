import sys

import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Optional
import requests
import os
from dotenv import load_dotenv
from utils.config.config_loader import config
from utils.index import get_env_variable
from utils.prompt_builder import get_prompt_globals, init_globals_for_test

# ✅ Load environment variables
load_dotenv()
ANTHROPIC_API_KEY: Optional[str] = get_env_variable("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError(
        "❌ ANTHROPIC_API_KEY is missing! Set it in your .env file or GitHub Secrets."
    )
TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"

if TEST_MODE:
    init_globals_for_test()

# ✅ LLM Configuration for Claude
claude_config = config.get("user_profile", {}).get("llm", {}).get("Anthropic", {})
claude_model = claude_config.get("text_model", "claude-3-sonnet")
temperature = claude_config.get("temperature", 0.7)
max_tokens = claude_config.get("max_tokens", 500)


def send_message_to_claude() -> dict:
    """Sends a blog post to Claude AI and returns a structured result."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    state = get_prompt_globals()
    prompt = state["prompt"]
    creative_prompt = state["creative_prompt"]
    gif_prompt = state["gif_prompt"]
    hashtags = state["hashtags"]
    system_instructions = state["system_instructions"]
    blog_content = state["blog_content"]

    if not prompt:
        print("No Prompt Given Claude")
        return {"status": "error", "message": "No prompt given"}

    print("📤 Sending message to Claude...")
    print("📝 Prompt:\n", prompt)

    # ✅ Request Payload
    data = {
        "model": claude_model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("📥 Status Code:", response.status_code)
        print("📦 Headers:", dict(response.headers))

        try:
            response_json = response.json()
            print("🧠 Response JSON:", response_json)
        except Exception as e:
            print("❌ Failed to parse Claude response JSON:", e)
            return {
                "status": "error",
                "response": "Invalid JSON response",
                "status_code": response.status_code,
                "raw": response.text,
            }

        if response.status_code == 200:
            content_blocks = response_json.get("content", [])
            if content_blocks and isinstance(content_blocks, list):
                text = content_blocks[0].get("text", "").strip()
                print("✅ Claude AI response parsed successfully.")
                return {
                    "status": "success",
                    "response": text,
                    "status_code": 200,
                    "raw": response_json,
                }
            else:
                print("❌ Unexpected content format in Claude response.")
                return {
                    "status": "error",
                    "response": "Claude returned an unexpected content format.",
                    "status_code": 200,
                    "raw": response_json,
                }
        else:
            print("❌ Claude API returned an error:", response_json)
            return {
                "status": "failed",
                "response": response_json.get("error", "Unknown error from Claude API"),
                "status_code": response.status_code,
                "raw": response_json,
            }

    except requests.RequestException as req_err:
        print("❌ Request error while sending to Claude:", str(req_err))
        return {
            "status": "error",
            "response": "Request exception occurred",
            "status_code": None,
            "raw": str(req_err),
        }
