import sys

import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
from utils.config_loader import config
from utils.index import get_env_variable
from utils import prompt_builder
from utils.prompt_builder import  get_prompt_globals
# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY: Optional[str] = get_env_variable("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ HUGGINGFACE_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# Get the shared global state

# ✅ LLM Configuration for Hugging Face
hf_config = config.get("user_profile",{}).get("llm", {}).get("HuggingFace", {})
# print("hfconfig",hf_config)
hf_text_model = hf_config.get("text_model", "mistralai/Mistral-7B-Instruct-v0.1")
hf_image_model = hf_config.get("image_model", "runwayml/stable-diffusion-v1-5")

temperature = hf_config.get("temperature", 0.7)
max_tokens = hf_config.get("max_tokens", 500)


def send_message_to_huggingface(prompt_text: str) -> dict:
    url = f"https://api-inference.huggingface.co/models/{hf_text_model}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": prompt_text,
        "parameters": {
            "temperature": temperature,
            "max_length": max_tokens,
        }
    }
    state = get_prompt_globals()

    prompt = state["prompt"]
    creative_prompt = state["creative_prompt"]
    gif_prompt = state["gif_prompt"]
    hashtags = state["hashtags"]
    system_instructions = state["system_instructions"]
    blog_content = state["blog_content"]
    print(f"📤 Sending prompt to Hugging Face model: {hf_text_model}")
    print(f"📝 Prompt:\n{prompt_text}\n")

    response = requests.post(url, headers=headers, json=data)
    print("Status Code",response.status_code)
    print("📥 Response JSON:",  response.reason)
    
    if response.status_code == 200:
        try:
            completion = response.json()[0].get("generated_text", "").strip()
          
            if completion == prompt_text.strip():
                print("⚠️ Generated text matches the prompt — likely failed to generate.")
                return {
                    "status": "failed",
                    "response": "Generated text is identical to the prompt. Check Model or Balacne / HF Subscription",
                    "details": {"completion": completion}
                }

            return {"status": "success", "response": completion}
        except Exception as e:
            print(f"❌ Failed to parse Hugging Face response: {e}")
            return {"status": "error", "response": "Invalid response format", "details": str(e)}
    else:
        error_details = response.json()
        print(f"❌ Hugging Face API error: {error_details}")
        return {
            "status": "failed",
            "response": "Error from Hugging Face API",
            "details": error_details
        }

        
def generate_image_with_huggingface(scoped_prompt: str) -> dict:
    if not hf_image_model:
        print("❌ No image model configured.")
        return {"status": "error", "response": "Image model not configured."}

    url = f"https://api-inference.huggingface.co/models/{hf_image_model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": scoped_prompt,
        "parameters": {
            "height": int(image_height),
            "width": int(image_width)
        }
    }

    print(f"🎨 Generating image with model: {hf_image_model}")
    print(f"📝 Image prompt:\n{scoped_prompt}\n")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        output = response.json()
        image_url = output.get("generated_image")

        if image_url:
            print(f"✅ Image generated successfully: {image_url}")
            return {"status": "success", "response": image_url}
        else:
            print("❌ No image URL returned.")
            return {"status": "failed", "response": "No image URL returned."}
    else:
        error_details = response.json()
        print(f"❌ Hugging Face image generation error: {error_details}")
        return {
            "status": "failed",
            "response": "Error generating image.",
            "details": error_details
        }


def run_huggingface_pipeline() -> dict:

    ai_config = config.get("user_profile",{}).get("ai", {})
    generate_image_enabled = config.get("creative",{}).get("generate_image",{}).get("enabled",{})



    text_result = send_message_to_huggingface(prompt)
    if text_result["status"] != "success":
        return {"status": "failed", "response": text_result["response"], "details": text_result.get("details")}

    result = {
        "status": "success",
        "response": text_result["response"]
    }

    if generate_image_enabled:
        image_result = generate_image_with_huggingface(creative_prompt)
        if image_result["status"] == "success":
            result["image_url"] = image_result["response"]
        else:
            result["image_error"] = image_result["response"]
    return result
