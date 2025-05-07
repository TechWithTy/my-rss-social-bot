"""
text_pipeline_utils.py
Utility functions for the text dispatch pipeline logic, including provider routing and error handling.
"""
from typing import  Dict, Any
from utils.config.config_loader import config
from ml_models.pollinations_generator import generate_text, generate_text_advanced, call_openai_compatible_endpoint
from ml_models.openai_generator import OpenAIGenerator
from ml_models.huggingface.utils.huggingface_generator_utils import HuggingFaceGenerator
from ml_models.deepseek.utils.deepseek_generator_utils import DeepSeekGenerator
from ml_models.claude.utils.claude_generator_utils import ClaudeGenerator
import asyncio
import json
from utils.dispatch.text.text_utils import clean_post_text
from circuitbreaker import circuit

# * Provider handler: Pollinations_Text
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_pollinations_text(state: Dict[str, Any]) -> Dict[str, Any]:
    safe_prompt = state["prompt"]
    llm_response = await generate_text(prompt=safe_prompt)
    try:
        parsed_response = json.loads(llm_response)
        return parsed_response
    except json.JSONDecodeError:
        return {"Text": llm_response}

# * Provider handler: Pollinations_Text_Advanced
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_pollinations_text_advanced(state: Dict[str, Any]) -> Dict[str, Any]:
    advanced_cfg = config["user_profile"]["llm"]["Pollinations"]["native_post"]
    messages = advanced_cfg.get("messages", [])
    for msg in messages:
        if msg["role"] == "user":
            msg["content"] = state["prompt"]
    payload = {
        "messages": messages,
        "model": advanced_cfg.get("model", "mistral"),
        "seed": advanced_cfg.get("seed", 42),
        "system": advanced_cfg.get("system", "You're a helpful assistant."),
        "json": advanced_cfg.get("json", True),
        "stream": advanced_cfg.get("stream", False),
        "private": advanced_cfg.get("private", True),
        "reasoning_effort": advanced_cfg.get("reasoning_effort", "medium"),
    }
    llm_response = await generate_text_advanced(payload=payload)
    parsed = json.loads(llm_response) if not isinstance(llm_response, dict) else llm_response
    if parsed.get("status") == "success" and "response" in parsed:
        try:
            response_str = parsed["response"]
            if response_str.startswith("json ") and response_str.endswith('"'):
                response_str = response_str[5:-1]
            content_json = json.loads(response_str)
            if state.get("blog_url") and content_json.get("Text") and not any(url in content_json["Text"] for url in ["http://", "https://"]):
                content_json["Text"] += f"\n\nRead more: {state['blog_url']}"
            if content_json.get("Text"):
                content_json["Text"] = clean_post_text(content_json["Text"])
            return content_json
        except json.JSONDecodeError as e:
            return {"Text": parsed.get("response", ""), "error": str(e)}
    return parsed

# * Provider handler: Pollinations_Text_Completion
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_pollinations_text_completion(state: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_pollinations_payload(state)
    endpoint = config["user_profile"]["llm"]["Pollinations"]["openai_compatible"]["endpoint"]
    llm_response = await call_openai_compatible_endpoint(endpoint, payload=payload)
    tool_calls = llm_response["choices"][0]["message"]["tool_calls"]
    generate_post_call = next(call for call in tool_calls if call["function"]["name"] == "generate_post")
    post_data = json.loads(generate_post_call["function"]["arguments"])
    post_text = post_data["Text"]
    post_hashtags = post_data.get("Hashtags", [])
    generate_image_call = next((call for call in tool_calls if call["function"]["name"] == "generate_image"), None)
    fetch_gif_call = next((call for call in tool_calls if call["function"]["name"] == "fetch_gif"), None)
    if generate_image_call is not None:
        image_data = json.loads(generate_image_call["function"]["arguments"])
        image_description = image_data.get("description", "")
        ai_img_example = {
            "Text": post_text,
            "Creative": f"[IMG] {image_description}",
            "ImageAsset": (
                f"https://image.pollinations.ai/prompt={image_description.replace(' ', '%20')}"
                f"?width={image_data.get('width', 1024)}"
                f"&height={image_data.get('height', 1024)}"
                f"&model={image_data.get('model', 'realistic_v4')}&nologo=true"
            ),
            "Hashtags": post_hashtags,
        }
        return ai_img_example
    elif fetch_gif_call is not None:
        gif_data = json.loads(fetch_gif_call["function"]["arguments"])
        gif_tags = gif_data.get("tags", [])
        ai_gif_example = {
            "Text": post_text,
            "Hashtags": post_hashtags,
            "GifSearchTags": gif_tags,
        }
        return ai_gif_example
    return {"Text": post_text, "Hashtags": post_hashtags}

# * Provider handler: OpenAI
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_openai_text(state: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0)  # placeholder for async consistency
    return await OpenAIGenerator.send_message(state["prompt"])

# * Provider handler: HuggingFace
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_huggingface_text(state: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0)
    result = HuggingFaceGenerator.send_message(state["prompt"])
    return result.get("response", {})

# * Provider handler: DeepSeek
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_deepseek_text(state: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0)
    return await DeepSeekGenerator.send_message(state["prompt"])

# * Provider handler: Claude
@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_claude_text(state: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0)
    return await ClaudeGenerator.send_message(state["prompt"])

# * Fallback for unhandled providers or errors
def fallback_error_text(e: Exception) -> Dict[str, Any]:
    return {"Text": "Error occurred in text pipeline", "error": str(e)}

# * Helper: Build pollinations payload (moved from main pipeline)
def build_pollinations_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    pollinations_cfg = config["user_profile"]["llm"]["Pollinations"]["openai_compatible"]
    messages = pollinations_cfg.get("messages", [])
    for message in messages:
        if message["role"] == "user":
            message["content"] = state["prompt"]
    return {
        "model": pollinations_cfg["model"],
        "messages": messages,
        "temperature": pollinations_cfg.get("temperature", 1.0),
        "top_p": pollinations_cfg.get("top_p", 1.0),
        "frequency_penalty": pollinations_cfg.get("frequency_penalty", 0.0),
        "presence_penalty": pollinations_cfg.get("presence_penalty", 0.0),
        "max_completion_tokens": pollinations_cfg.get("max_completion_tokens", 256),
        "stop": pollinations_cfg.get("stop"),
        "seed": pollinations_cfg.get("seed"),
        "stream": pollinations_cfg.get("stream"),
        "stream_options": pollinations_cfg.get("stream_options"),
        "suffix": pollinations_cfg.get("suffix"),
        "tool_choice": pollinations_cfg.get("tool_choice"),
        "tools": pollinations_cfg.get("tools"),
        "n": pollinations_cfg.get("n", 1),
        "logit_bias": pollinations_cfg.get("logit_bias", {}),
        "logprobs": pollinations_cfg.get("logprobs"),
        "top_logprobs": pollinations_cfg.get("top_logprobs"),
        "user": pollinations_cfg.get("user"),
        "response_format": pollinations_cfg.get("response_format"),
        "metadata": pollinations_cfg.get("metadata"),
        "modalities": pollinations_cfg.get("modalities"),
        "parallel_tool_calls": pollinations_cfg.get("parallel_tool_calls"),
        "reasoning_effort": pollinations_cfg.get("reasoning_effort"),
        "service_tier": pollinations_cfg.get("service_tier"),
        "store": pollinations_cfg.get("store"),
        "prediction": pollinations_cfg.get("prediction"),
        "audio": pollinations_cfg.get("audio"),
        "function_call": pollinations_cfg.get("function_call"),
        "functions": pollinations_cfg.get("functions"),
        "search_context_size": pollinations_cfg.get("search_context_size"),
        "user_location": pollinations_cfg.get("user_location"),
        "web_search_options": pollinations_cfg.get("web_search_options"),
    }
