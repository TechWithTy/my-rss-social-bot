"""
image_utils.py
Utility functions for image dispatch pipeline.
"""
from typing import Optional
import httpx

# * Helper: Build a fallback prompt for images
def build_fallback_prompt(prompt: Optional[str], blog_content: Optional[str]) -> str:
    """
    Returns a suitable prompt for image generation, falling back to blog content or a generic prompt if needed.
    """
    if not prompt or not isinstance(prompt, str):
        if blog_content:
            return f"Create an image relevant to: {blog_content[:200]}"
        else:
            return "Create a professional business image with technology elements"
    return prompt

# * Helper: Compose the final prompt string for image generation
def compose_final_prompt(prompt: str, blog_content: Optional[str], creative_prompt: Optional[str], hashtags: Optional[str]) -> str:
    parts = [prompt]
    if blog_content:
        parts.append(blog_content[:500])
    if creative_prompt:
        parts.append(creative_prompt)
    if hashtags:
        parts.append(hashtags)
    return "\n\n".join(parts)

# * Helper: URL-encode prompt for Pollinations API
def url_encode_prompt(prompt: str) -> str:
    return httpx.QueryParams({"prompt": prompt}).get("prompt")
