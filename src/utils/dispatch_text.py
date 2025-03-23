
from utils.prompt_builder import build_prompt_payload
from utils.config_loader import config
from models.pollinations_generator import (
    generate_image,
    list_image_models,
    generate_text,
    generate_text_advanced,
    generate_audio,
    list_text_models,
    fetch_image_feed,
    fetch_text_feed,
    call_openai_compatible_endpoint)

from models.openai_generator import run_openai_pipeline
from models.huggingface_generator import run_huggingface_pipeline
from models.deepseek_generator import send_message_to_deepseek
from models.claude_generator import send_message_to_claude

prompt_payload = build_prompt_payload()
prompt = prompt_payload.get("content")
system_instructions = prompt_payload.get("system_instructions")



def build_pollinations_payload():
    pollinations_cfg = config['user_profile']['llm']['Pollinations']['openai_compatible']
    
    # Replace {blog_text} in the user message or prompt
    messages = pollinations_cfg.get("messages", [])
    for message in messages:
        if message['role'] == "user":
            message['content'] = prompt

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
        "web_search_options": pollinations_cfg.get("web_search_options")
    }


def dispatch_text_pipeline(provider: str,):
    match provider:
        case "Pollinations_Text":
            # Basic GET /{prompt}
            prompt = parsed_blog
            return asyncio.run(generate_text(prompt=prompt))

        case "Pollinations_Text_Advanced":
            # POST / with messages + model
            advanced_cfg = config['user_profile']['llm']['Pollinations']['native_post']
            messages = advanced_cfg.get("messages", [])
            for msg in messages:
                if msg["role"] == "user":
                    msg["content"] = parsed_blog
            payload = {
                "messages": messages,
                "model": advanced_cfg.get("model", "mistral"),
                "seed": advanced_cfg.get("seed", 42),
                "jsonMode": advanced_cfg.get("jsonMode", True),
                "private": advanced_cfg.get("private", True),
                "reasoning_effort": advanced_cfg.get("reasoning_effort", "medium")
            }
            return asyncio.run(generate_text_advanced("/", payload=payload))

        case "Pollinations_Text_Completion":
            # OpenAI-compatible Chat Completions
            payload = build_pollinations_payload()
            endpoint = config['user_profile']['llm']['Pollinations']['openai_compatible']['endpoint']
            return asyncio.run(call_openai_compatible_endpoint(endpoint, payload=payload))

        case "OpenAI":
            openai_cfg = config['user_profile']['llm']['OpenAI']
            payload = {
                "model": openai_cfg['text_model'],
                "messages": [{"role": "user", "content": parsed_blog}],
                "temperature": openai_cfg['temperature'],
                "top_p": openai_cfg['top_p']
            }
            return asyncio.run(run_openai_pipeline())

        case "HuggingFace":          
            return asyncio.run(run_huggingface_pipeline())

        case "DeepSeek":
            ds_cfg = config['user_profile']['llm']['DeepSeek']
            payload = {
                "model": ds_cfg['text_model'],
                "prompt": parsed_blog,
                "temperature": ds_cfg['temperature'],
                "top_p": ds_cfg['top_p'],
                "presence_penalty": ds_cfg['presence_penalty'],
                "frequency_penalty": ds_cfg['frequency_penalty'],
                "response_format": ds_cfg['response_format'],
                "max_tokens": ds_cfg['max_tokens']
            }
            return asyncio.run(send_message_to_deepseek())

        case "Claude":
            claude_cfg = config['user_profile']['llm']['Anthropic']
            payload = {
                "model": claude_cfg['text_model'],
                "max_tokens": claude_cfg['max_tokens'],
                "temperature": claude_cfg['temperature'],
                "top_p": claude_cfg['top_p'],
                "messages": [
                    {"role": "user", "content": parsed_blog}
                ],
                "system": claude_cfg['system']
            }
            return asyncio.run(send_message_to_claude())

        case _:
            raise ValueError(f"❌ Unsupported provider: {provider}")
