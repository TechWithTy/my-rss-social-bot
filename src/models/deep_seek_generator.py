from typing import Optional, Dict, Any, List
import requests
import os
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable

# ✅ Load environment variables
load_dotenv()

DEEPSEEK_API_KEY: Optional[str] = get_env_variable("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ DEEPSEEK_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# ✅ LLM Configuration
deepseek_config = config["user_profile"]["llm"]["DeepSeek"]
deepseek_model = deepseek_config["model"]
temperature = deepseek_config["temperature"]
max_tokens = deepseek_config["max_tokens"]
top_p = deepseek_config["top_p"]
frequency_penalty = deepseek_config["frequency_penalty"]
presence_penalty = deepseek_config["presence_penalty"]
response_format = deepseek_config["response_format"]
tool_choice = deepseek_config["tool_choice"]
logprobs = deepseek_config["logprobs"]
top_logprobs = deepseek_config["top_logprobs"]
tools = deepseek_config.get("tools", "function")


def send_message_to_deepseek(blog_content: str) -> Optional[str]:
    """
    Sends a blog post to DeepSeek AI and returns the AI-generated LinkedIn post.

    Parameters:
        blog_content (str): The blog post content to be summarized.

    Returns:
        Optional[str]: AI-generated post or None if the request fails.
    """

    deep_seek_config = config.get("user_profile",{}).get("llm", {}).get("DeepSeek", {})
    deep_seek_text_model =deep_seek_config.get("text_model", "meta-llama/Meta-Llama-3-8B")
    temperature = deep_seek_config.get("temperature", 0.7)
    max_tokens = deep_seek_config.get("max_tokens", 500)
    top_p = deep_seek_config.get("top_p", 0.95)
    frequency_penalty = deep_seek_config.get("frequency_penalty", 0)
    presence_penalty = deep_seek_config.get(" presence_penalty", 0)
    response_format = deep_seek_config.get("response_format","json_object" )
    tool_choice = deep_seek_config.get("tool_choice","auto" )
    logrobs = deep_seek_config.get('logrobs',False)
    top_logrobs = deep_seek_config.get('top_logrobs',5)
    top_logrobs = deep_seek_config.get('tools',"function")

    prompt_payload = build_prompt_payload()
    prompt = prompt_payload.get("content")
    prompt_creative = prompt_payload.get("creative_prompt")
    system_instructions = prompt_payload.get("system_instructions")

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # 🔧 Config Sections
   

    print('Message Content:\n\n', content)
    
    # ✅ Request Payload
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
        "top_logprobs": top_logprobs,
        "tools": [{"type": tools}]
    }

    # ✅ Send Request
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        completion = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        print("✅ DeepSeek AI Response Generated!")
        return completion
    else:
        print("❌ Error sending request to DeepSeek AI:", response.json())
        return None
