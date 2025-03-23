
from utils.prompt_builder import build_prompt_payload,prompt,creative_prompt,system_instructions,blog_content
from utils.config_loader import config
from models.pollinations_generator import (
  
    generate_image,
    generate_image_advanced,
   )
import urllib.parse
from models.openai_generator import run_openai_pipeline
from models.huggingface_generator import run_huggingface_pipeline
from models.deepseek_generator import send_message_to_deepseek
from models.claude_generator import send_message_to_claude
import asyncio
import json
from typing import Optional
import httpx
from utils.fetch import fetch_with_retries  # Assuming you have this helper
from models.openai_generator import generate_openai_image  # Missing in import
from models.huggingface_generator import generate_image_with_huggingface  # Missing in import



async def generate_image_description() -> Optional[str]:
    """
    Generates a creative image description based on blog content and prompt instructions.
    Returns a short descriptive string.
    """
    prompt = f"{creative_prompt}\n\nBLOG:\n{blog_content.strip()}"
    encoded_prompt = httpx.QueryParams({"prompt": prompt}).get("prompt")  # URL-safe

    url = f"{BASE_TEXT_URL}/{encoded_prompt}"
    async with httpx.AsyncClient() as client:
        response = await fetch_with_retries(url, client)
        return response.text.strip() if response else None


creative_prompt_output = asyncio.run(generate_image_description())

async def dispatch_image_pipeline(provider: str):
        match provider:
            case "Pollinations_Image":
                print("🖼️ Pollinations_Image", creative_prompt_output)
                image_url = await generate_image(prompt=creative_prompt_output)
                return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}

            case "Pollinations_Image_Get":
                print("🎨 Pollinations Image GET Setup")
                cfg = config['user_profile']['llm']['Pollinations']['pollinations_image_get']

                image_url = await generate_advanced_image(
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
                image_url = await generate_image(prompt=creative_prompt_output)
                print("🖼️ Pollinations_Image", creative_prompt_output, image_url)
                return image_url

            case "HuggingFace":
                print("🤗 Hugging Face")          
                result = generate_image_with_huggingface()
                url = result.get("response")
                print("🤗 Hugging Face Image Result", url)          
                
            
                return url 

            case _:
                raise ValueError(f"❌ Unsupported provider: {provider}")
