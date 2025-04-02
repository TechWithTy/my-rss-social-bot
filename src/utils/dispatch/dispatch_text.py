from utils.config.config_loader import config
from models.pollinations_generator import (
    generate_text,
    generate_text_advanced,

    call_openai_compatible_endpoint,
)
import urllib.parse
from models.openai_generator import run_openai_pipeline
from models.huggingface_generator import run_huggingface_pipeline
from models.deepseek_generator import send_message_to_deepseek
from models.claude_generator import send_message_to_claude
import asyncio
import json
from utils.prompt_builder import init_globals_for_test, get_prompt_globals, _prompt_globals
from utils.index import get_env_variable


TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"

if TEST_MODE:
    init_globals_for_test()

state = get_prompt_globals()

prompt = state["prompt"]
creative_prompt = state["creative_prompt"]
gif_prompt = state["gif_prompt"]
hashtags = state["hashtags"]
system_instructions = state["system_instructions"]
blog_content = state["blog_content"]
openai_config = config.get("user_profile", {}).get("llm", {}).get("OpenAI", {})


def handle_pollinations_text_completion():
    # Build the request payload (adjust as needed)
    payload = build_pollinations_payload()
    endpoint = config["user_profile"]["llm"]["Pollinations"]["openai_compatible"][
        "endpoint"
    ]

    # Make the async call to your OpenAI-like endpoint
    llm_response = asyncio.run(
        call_openai_compatible_endpoint(endpoint, payload=payload)
    )
    tool_calls = llm_response["choices"][0]["message"]["tool_calls"]

    # Get the generate_post call
    generate_post_call = next(
        call for call in tool_calls if call["function"]["name"] == "generate_post"
    )
    post_data = json.loads(generate_post_call["function"]["arguments"])
    post_text = post_data["Text"]
    post_hashtags = post_data.get("Hashtags", [])

    # Try to find generate_image call (may or may not exist)
    generate_image_call = next(
        (call for call in tool_calls if call["function"]["name"] == "generate_image"),
        None,
    )

    # Try to find fetch_gif call (may or may not exist)
    fetch_gif_call = next(
        (call for call in tool_calls if call["function"]["name"] == "fetch_gif"), None
    )

    # If you have an image call
    if generate_image_call is not None:
        image_data = json.loads(generate_image_call["function"]["arguments"])
        image_description = image_data.get("description", "")

        # Build an example "image" JSON response
        ai_img_example = {
            "Text": post_text,
            "Creative": f"[IMG] {image_description}",
            # Example: building a hypothetical image URL using the description
            "ImageAsset": (
                f"https://image.pollinations.ai/prompt={image_description.replace(' ', '%20')}"
                f"?width={image_data.get('width', 1024)}"
                f"&height={image_data.get('height', 1024)}"
                f"&model={image_data.get('model', 'realistic_v4')}&nologo=true"
            ),
            "Hashtags": post_hashtags,
        }

        print(
            "Pollinations_Text_OPENAI LLM Response (image):",
            ai_img_example["ImageAsset"],
        )
        return ai_img_example

    # Else if you have a gif call
    elif fetch_gif_call is not None:
        gif_data = json.loads(fetch_gif_call["function"]["arguments"])
        gif_tags = gif_data.get("tags", [])

        # Build an example "gif" JSON response
        ai_gif_example = {
            "Text": post_text,
            "Hashtags": post_hashtags,
            "GifSearchTags": gif_tags,
        }

        print(
            "Pollinations_Text_OPENAI LLM Response (gif):",
            ai_gif_example["GifSearchTags"],
        )
        return ai_gif_example

    # If neither is found, just return the post text or handle however you like
    return {"Text": post_text, "Hashtags": post_hashtags}


def build_pollinations_payload():
    pollinations_cfg = config["user_profile"]["llm"]["Pollinations"][
        "openai_compatible"
    ]

    # Replace {blog_text} in the user message or prompt
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


def clean_post_text(text: str) -> str:
    """Clean and format the post text for better readability.

    Args:
        text: The raw text from the AI response

    Returns:
        Cleaned and properly formatted text
    """
    if not text:
        return ""
    print(
        "Cleaning post text..."
        + " "
        + (text[:100] + "..." if len(text) > 100 else text)
    )

    return text.strip()


def dispatch_text_pipeline(
    provider: str,
):
    print("Dispatch Text State - Prompt:", state["prompt"])
    print("Dispatch Text State - Raw Blog:", state.get("raw_blog"))
    print("Dispatch Text State - Blog Content:", state.get("blog_content"))
    match provider:
        case "Pollinations_Text":
            print("Pollinations_Text_Extracted", state["prompt"])
            safe_prompt = urllib.parse.quote(state["prompt"])
            llm_response = asyncio.run(generate_text(prompt=safe_prompt))
            print("Pollinations_Text LLM Response", type(llm_response), llm_response)

            try:
                parsed_response = json.loads(llm_response)
                return parsed_response
            except json.JSONDecodeError as e:
                print("❌ Failed to parse JSON:", e)
                return {"Text": llm_response}  # fallback if it's just plain text

        case "Pollinations_Text_Advanced":
            # POST / with messages + model
            print("Pollinations_Text_Extracted", state["prompt"])
            advanced_cfg = config["user_profile"]["llm"]["Pollinations"]["native_post"]
            print("Pollinations_Text_Advanced: advanced_cfg", advanced_cfg)
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
                # "referer": advanced_cfg.get(
                #     "referer", "https://www.cybershoptech.com/"
                # ),
            }

            llm_response = asyncio.run(generate_text_advanced(payload=payload))
            # Check if llm_response is already a dictionary to avoid parsing error
            if isinstance(llm_response, dict):
                parsed = llm_response
            else:
                parsed = json.loads(llm_response)
            print("Pollinations_Text_Advanced LLM Parsed", parsed)

            # The actual content is nested in the 'response' field as a JSON string
            if parsed.get("status") == "success" and "response" in parsed:
                try:
                    # Check if the response is surrounded by a "json" string
                    if parsed["response"].startswith("json ") and parsed[
                        "response"
                    ].endswith('"'):
                        print('Removing "json" string from response')
                        parsed["response"] = parsed["response"][5:-1]
                    # Extract and parse the inner JSON from the 'response' field
                    content_json = json.loads(parsed["response"])
                    print("✅ Successfully parsed inner JSON content:", content_json)

                    # If blog URL exists in state, append it to the Text field
                    if state.get("blog_url") and content_json.get("Text"):
                        # Add the blog URL to the post text if it doesn't already contain a URL
                        if not any(
                            url in content_json["Text"]
                            for url in ["http://", "https://"]
                        ):
                            blog_url = state["blog_url"]
                            content_json["Text"] = (
                                f"{content_json['Text']}\n\nRead more: {blog_url}"
                            )
                            print(f"✅ Added blog URL to post: {blog_url}")

                    # Clean and format the post text
                    if content_json.get("Text"):
                        content_json["Text"] = clean_post_text(content_json["Text"])
                        print("Cleaned and formatted post text")

                    return content_json
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing inner response JSON: {e}")
                    # Return raw response as fallback
                    return {"Text": parsed.get("response", ""), "error": str(e)}

            # Fallback if the expected structure isn't found
            return parsed

        case "Pollinations_Text_Completion":
            # OpenAI-compatible Chat Completions
            return handle_pollinations_text_completion()

        case "OpenAI":
            openai_cfg = config["user_profile"]["llm"]["OpenAI"]
            payload = {
                "model": openai_cfg["text_model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": openai_cfg["temperature"],
                "top_p": openai_cfg["top_p"],
            }
            _prompt_globals["prompt"] = payload["messages"][0]["content"]
            return asyncio.run(run_openai_pipeline())

        case "HuggingFace":
            print("🤗 Hugging Face")
            result = run_huggingface_pipeline()
            print("🤗 Hugging Face Result", result.get("result"))
            llm_response = result.get("response")  # corrected typo
            print(
                "HF Response 🤗 "
                + str(type(llm_response).__name__)
                + " "
                + str(llm_response)
            )
            return llm_response

        case "DeepSeek":
            ds_cfg = config["user_profile"]["llm"]["DeepSeek"]
            payload = {
                "model": ds_cfg["text_model"],
                "prompt": state["prompt"],
                "temperature": ds_cfg["temperature"],
                "top_p": ds_cfg["top_p"],
                "presence_penalty": ds_cfg["presence_penalty"],
                "frequency_penalty": ds_cfg["frequency_penalty"],
                "response_format": ds_cfg["response_format"],
                "max_tokens": ds_cfg["max_tokens"],
            }
            llm_response = send_message_to_deepseek()
            print("🦈 Deep Seek Response", llm_response)
            return llm_response

        case "Claude":
            claude_cfg = config["user_profile"]["llm"]["Anthropic"]
            payload = {
                "model": claude_cfg["text_model"],
                "max_tokens": claude_cfg["max_tokens"],
                "temperature": claude_cfg["temperature"],
                "top_p": claude_cfg["top_p"],
                "messages": [{"role": "user", "content": state["prompt"]}],
                "system": claude_cfg["system"],
            }
            llm_response = send_message_to_claude()
            print("🎅 Claude Response", llm_response)
            return llm_response

        case _:
            raise ValueError(f"❌ Unsupported provider: {provider}")
