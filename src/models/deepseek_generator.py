import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Optional
import requests
import os
from dotenv import load_dotenv
from utils.config_loader import config
from utils.index import get_env_variable
from utils.prompt_builder import  get_prompt_globals,init_globals_for_test# ✅ Load environment variables
load_dotenv()

DEEPSEEK_API_KEY: Optional[str] = get_env_variable("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ DEEPSEEK_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    init_globals_for_test()
# Initialize the state




def send_message_to_deepseek() -> dict:
    """
    Sends a blog post to DeepSeek AI and returns a result dict with status, response, and metadata.
    """
    # Get the shared global state
    state = get_prompt_globals()

    # Access individual variables
    prompt = state["prompt"]
    creative_prompt = state["creative_prompt"]
    gif_prompt = state["gif_prompt"]
    hashtags = state["hashtags"]
    system_instructions = state["system_instructions"]
    blog_content = state["blog_content"]
    if not prompt:
        print("No Prompt Given DeepSeek")
        return {
            "status": "error",
            "message": "No prompt given"
        }

    deep_seek_config = config.get("user_profile", {}).get("llm", {}).get("DeepSeek", {})
    deep_seek_text_model = deep_seek_config.get("text_model", "deepseek-chat")
    temperature = deep_seek_config.get("temperature", 0.7)
    max_tokens = deep_seek_config.get("max_tokens", 500)
    top_p = deep_seek_config.get("top_p", 0.95)
    frequency_penalty = deep_seek_config.get("frequency_penalty", 0.0)
    presence_penalty = deep_seek_config.get("presence_penalty", 0.0)
    response_format = deep_seek_config.get("response_format", "json_object")
    tool_choice = deep_seek_config.get("tool_choice", "auto")
    logprobs = deep_seek_config.get("logprobs", False)
    top_logprobs = deep_seek_config.get("top_logprobs", 5)
    tools = deep_seek_config.get("tools", "function")

 

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    print("🦈 DeepSeek System Prompt",system_instructions)
    print("🦈 DeepSeek Global Prompt",prompt)

    payload = {
        "model": deep_seek_text_model,  # Ensure this variable matches one of the available models, e.g., "deepseek-chat"
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,  # Ensure this is a float ≤ 2
        "max_tokens": max_tokens,  # Ensure this is an integer between 1 and 8192
        "top_p": top_p,  # Ensure this is a float between 0 and 1
        "frequency_penalty": frequency_penalty,  # Ensure this is a float between -2 and 2
        "presence_penalty": presence_penalty,  # Ensure this is a float between -2 and 2
        "response_format": {"type": response_format},  # Typically "text" or "json_object"
        "tool_choice": tool_choice,  # Ensure this matches the expected tool choice, e.g., "none" or "auto"
        "logprobs": logprobs,  # Boolean indicating whether to return log probabilities
        # Include 'tools', 'stop', 'stream', 'stream_options', and 'top_logprobs' if required by your application
    }


    # Only add tools if valid and required by the model
    if tools == "function":
        payload["tools"] = [{
            "type": "function",
            "function": {
                "name": "placeholder_function",
                "description": "A placeholder function as required by the DeepSeek API.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }]
    if logprobs:
        payload["top_logprobs"] = top_logprobs

    print("📤 Sending request to DeepSeek...")
    print("🔧 Payload:", payload)

    response = requests.post(url, headers=headers, json=payload)

    print("📥 Status Code:", response.status_code)
    print("📦 Headers:", dict(response.headers))

    try:
        response_data = response.json()
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
        print(f"🧠 Headers: {dict(response.headers)}")
        print(f"🦈 DeepSeek Failed - Status: {response.status_code} | Reason: {response.reason} | Text: {response.text}")
        return {
            "status": "error",
            "response": "Invalid JSON response",
            "details": {
                "status_code": response.status_code,
                "text": response.text,
                "error": str(e)
            }
        }

    if response.status_code == 200:
        completion = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        print("🦈 Deep Seek Completion")
        if completion == prompt.strip():
            return {
                "status": "failed",
                "response": "Completion is identical to prompt. Likely an error.",
                "details": {
                    "status_code": response.status_code,
                    "raw": response_data
                }
            }

        return {
            "status": "success",
            "response": completion,
            "details": {
                "status_code": response.status_code,
                "raw": response_data
            }
        }

    return {
        "status": "failed",
        "response": response_data.get("error", "Unknown error from DeepSeek"),
        "details": {
            "status_code": response.status_code,
            "raw": response_data
        }
    }
