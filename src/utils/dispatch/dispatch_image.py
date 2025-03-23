from typing import Optional, Dict
import httpx
import asyncio
import json
from utils.prompt_builder import build_prompt_payload, prompt, creative_prompt, system_instructions, blog_content
from utils.config_loader import config
from models.pollinations_generator import generate_image, generate_image_advanced,fetch_with_retries
from models.openai_generator import generate_openai_image
from models.huggingface_generator import generate_image_with_huggingface
from models.deepseek_generator import send_message_to_deepseek
from models.claude_generator import send_message_to_claude
from utils.giphy import giphy_find_with_metadata  # ensure this is available

FLUX_BASE_IMAGE_URL = "https://image.pollinations.ai"

async def generate_image_description() -> Optional[str]:
    if blog_content:
        prompt = f"{creative_prompt}\n\nBLOG:\n{blog_content.strip()}"
        encoded_prompt = httpx.QueryParams({"prompt": prompt}).get("prompt")
        url = f"{FLUX_BASE_IMAGE_URL}/{encoded_prompt}"
        async with httpx.AsyncClient() as client:
            response = await fetch_with_retries(url, client)
            return response.text.strip() if response else None
    else:
        return None
async def generate_gif_tags() -> Optional[Dict[str, list]]:
    if blog_content:
        prompt = f"{system_instructions}\n\nBLOG:\n{blog_content.strip()}"
        encoded_prompt = httpx.QueryParams({"prompt": prompt}).get("prompt")
        url = f"{FLUX_BASE_IMAGE_URL}/{encoded_prompt}"
        async with httpx.AsyncClient() as client:
            response = await fetch_with_retries(url, client)
            if response:
                try:
                    return response.json()
                except Exception:
                    return {"GifSearchTags": [tag.strip() for tag in response.text.split(",") if tag.strip()]}
    else:
        return None

async def dispatch_image_pipeline(provider: str) -> Optional[Dict[str, str]]:
    creative_prompt_output = await generate_image_description()

    match provider:
        case "Pollinations_Image":
            print("🖼️ Pollinations_Image", creative_prompt_output)
            image_url = await generate_image(prompt=creative_prompt_output)
            return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}

        case "Pollinations_Image_Get":
            print("🎨 Pollinations Image GET Setup")
            cfg = config['user_profile']['llm']['Pollinations']['pollinations_image_get']
            image_url = await generate_image_advanced(
                prompt=creative_prompt_output,
                model=cfg.get("model", "flux"),
                seed=cfg.get("seed", 42),
                width=cfg.get("width", 1024),
                height=cfg.get("height", 1024),
                nologo=cfg.get("nologo", True),
                private=cfg.get("private", True),
                enhance=cfg.get("enhance", False),
                safe=cfg.get("safe", True),
            )
            return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}

        case "OpenAI":
            image_url = generate_openai_image(prompt=creative_prompt_output)
            return {"ImageAsset": image_url} if image_url else {"error": "OpenAI image generation failed"}

        case "HuggingFace":
            result = generate_image_with_huggingface(prompt=creative_prompt_output)
            url = result.get("response")
            return {"ImageAsset": url} if url else {"error": "HuggingFace image generation failed"}

        case "Giphy":
            gif_tags = await generate_gif_tags()
            if gif_tags:
                giphy_response = giphy_find_with_metadata(gif_tags.get("GifSearchTags", []))
                gif_obj = giphy_response.get("result", {}).get("gif")
                return {"GifAsset": gif_obj} if gif_obj else {"error": "No matching GIF found"}
            return {"error": "GIF tags generation failed"}

        case _:
            raise ValueError(f"❌ Unsupported provider: {provider}")
