from typing import Optional, Dict, Any, List
import requests
import os
from dotenv import load_dotenv
from utils.config_loader import config
from utils.index import get_env_variable
from utils import prompt_builder
from utils.prompt_builder import build_prompt_payload,prompt,creative_prompt,system_instructions
# ✅ Load environment variables
load_dotenv()

DEEPSEEK_API_KEY: Optional[str] = get_env_variable("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ DEEPSEEK_API_KEY is missing! Set it in your .env file or GitHub Secrets.")
def send_message_to_deepseek() -> dict:
    """
    Sends a blog post to DeepSeek AI and returns a result dict with status, response, and metadata.
    """

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

    payload = {
        "model": deep_seek_text_model,
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "response_format": {"type": response_format},
        "tool_choice": tool_choice,
        "logprobs": logprobs,
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
        print("🧠 Response JSON:", response_data)
    except Exception as e:
        print("❌ Failed to parse JSON:", e)
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
