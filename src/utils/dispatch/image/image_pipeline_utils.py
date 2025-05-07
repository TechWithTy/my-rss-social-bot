"""
image_pipeline_utils.py
Utility functions for the image dispatch pipeline logic, including provider routing and error handling.
"""
from typing import Optional, Dict
from utils.config.config_loader import config
from ml_models.pollinations_generator import generate_image, generate_image_advanced
from ml_models.openai_generator import OpenAIGenerator
from ml_models.huggingface.utils.huggingface_generator_utils import HuggingFaceGenerator
from socials.giphy import giphy_find_with_metadata
from circuitbreaker import circuit

@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_pollinations_image_get(creative_prompt_output: str) -> Dict[str, str]:
    cfg = config["user_profile"]["llm"]["Pollinations"]["pollinations_image_get"]
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

@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_pollinations_image(creative_prompt_output: str) -> Dict[str, str]:
    image_url = await generate_image(prompt=creative_prompt_output)
    return {"ImageAsset": image_url} if image_url else {"error": "Image generation failed"}

@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_openai_image(creative_prompt_output: str) -> Dict[str, str]:
    image_url = OpenAIGenerator.generate_image(prompt=creative_prompt_output)
    return {"ImageAsset": image_url} if image_url else {"error": "OpenAI image generation failed"}

@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_huggingface_image(creative_prompt_output: str) -> Dict[str, str]:
    result = HuggingFaceGenerator.generate_image(prompt=creative_prompt_output)
    url = result.get("response")
    return {"ImageAsset": url} if url else {"error": "HuggingFace image generation failed"}

@circuit(failure_threshold=3, recovery_timeout=60)
async def handle_giphy_image(gif_tags: Optional[Dict]) -> Dict[str, str]:
    if gif_tags:
        giphy_response = giphy_find_with_metadata(gif_tags.get("GifSearchTags", []))
        gif_obj = giphy_response.get("result", {}).get("gif")
        return {"GifAsset": gif_obj} if gif_obj else {"error": "No matching GIF found"}
    return {"error": "GIF tags generation failed"}

# * Fallback for unhandled providers or errors
def fallback_error_image(e: Exception) -> Dict[str, str]:
    fallback_url = "https://image.pollinations.ai/prompt/Error%20placeholder%20image%20with%20technical%20elements?width=1024&height=1024&nologo=true"
    return {"ImageAsset": fallback_url, "error": str(e)}
