"""
prompt_instructions.py
- Handles retrieval and assembly of system, user, and default instructions for prompts.
"""
from typing import Dict, Any
from src.utils.config.config_loader import config

def get_default_instructions() -> str:
    ai_config = config.get("ai", {})
    return ai_config.get("default_response_instructions") or (
        'Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both. Example response: { "Text": "Your message here.", "Creative": "[IMG] A relevant visual description.", "ImageAsset": "https://image.pollinations.ai/prompt/{description}?width={width}&height={height}&seed={seed}&model=flux-realistic&nologo=true", "Hashtags": ["#Relevant", "#Contextual", "#GeneralTopic"] } or { "Text": "Message.", "Hashtags": ["#tag", "#tag", "#tag"], "GifSearchTags": ["term one", "term two", "term three"] }'
    )

def get_system_instructions() -> str:
    ai_config = config.get("ai", {})
    return ai_config.get("custom_system_instructions") or (
        "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
    )

def get_user_instructions() -> str:
    ai_config = config.get("ai", {})
    return ai_config.get("custom_user_instructions") or (
        "Make the post concise, actionable, and emotionally resonant."
    )
