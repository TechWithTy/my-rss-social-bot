from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable
from src.utils import prompt_builder
from src.utils.prompt_builder import build_prompt_payload

# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY: Optional[str] = get_env_variable("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ HUGGINGFACE_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# ✅ LLM Configuration for Hugging Face
hf_config = config.get("user_profile",{}).get("llm", {}).get("HuggingFace", {})
hf_text_model = hf_config.get("text_model", "meta-llama/Meta-Llama-3-8B")
temperature = hf_config.get("temperature", 0.7)
max_tokens = hf_config.get("max_tokens", 500)
   
prompt_payload = build_prompt_payload()
prompt = prompt_payload.get("content")
prompt_creative = prompt_payload.get("creative_prompt")

def send_message_to_huggingface(blog_content: str) -> Optional[str]:
    """Sends a blog post to Hugging Face API and returns the AI-generated LinkedIn post."""
    url = f"https://api-inference.huggingface.co/models/{hf_text_model}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

  

    print('Message Content:\n\n', prompt)

    # ✅ Request Payload
    data = {
        "inputs": prompt,
        "parameters": {
            "temperature": temperature,
            "max_length": max_tokens,
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()[0].get("generated_text", "").strip()
        print("✅ Hugging Face Response Generated!")
        return completion
    else:
        print("❌ Error sending request to Hugging Face API:", response.json())
        return None


ai_config = config.get("ai", {})

generate_image_config = creative_config.get("generate_image", {})
generate_image_enabled = generate_image_config.get("enabled", False)
image_prompt = generate_image_config.get("prompt", "")
image_size = generate_image_config.get("width", "1024")
image_size = generate_image_config.get("height", "1024")

image_model = hf_config.get("image_model", "meta-llama/Meta-Llama-3-8B")

def generate_image_with_huggingface() -> Optional[str]:
    """
    Generates an AI image using a Hugging Face model and returns the image URL.

    Returns:
        Optional[str]: URL to the generated image (if successful), else None.
    """
    if not image_model:
        print("❌ Image generation is disabled in the YAML config.")
        return None

    print(f"🎨 Generating image with model: {image_model}")

    url = f"https://api-inference.huggingface.co/models/{image_model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": prompt_creative ,
        "parameters": {
            "height": int(image_size.split("x")[0]),
            "width": int(image_size.split("x")[1])
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        output = response.json()
        image_url = output.get("generated_image", None)

        if image_url:
            print(f"✅ Image generated successfully: {image_url}")
            return image_url
        else:
            print("❌ No image URL returned in response.")
            return None
    else:
        print("❌ Error generating image:", response.json())
        return None




def run_huggingface_pipeline(username: str) -> Optional[dict]:
    """Main pipeline that fetches blog content, generates text, and optionally generates an image using Hugging Face."""
    # Step 1: Get the blog content
    

    # Step 3: Generate LinkedIn text post
    post_text = send_message_to_huggingface(prompt_text)
    if not post_text:
        print("❌ Failed to generate LinkedIn post via Hugging Face.")
        return None

    result = {
        "text": post_text
    }

    # Step 4: Optionally generate image
    if generate_image_enabled:
        image_url = generate_image_with_huggingface(prompt_creative)
        if image_url:
            result["image_url"] = image_url

    return result
