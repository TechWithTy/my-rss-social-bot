"""
post_utils.py
- Post preparation, GIF/image handling, and content assembly utilities.
"""
from utils.dispatch.dispatch_text import dispatch_text_pipeline
from asset_fetch.giphy import giphy_find_with_metadata, extract_social_upload_metadata
from typing import Optional

async def prepare_linkedin_post(text_model: str) -> dict:
    print("🚀 Generating LinkedIn post...")
    return await dispatch_text_pipeline(text_model)


async def attach_gif_to_post(post: dict) -> dict:
    gif_tags = post.get("GifSearchTags", [])
    print(f"🔍 GIF search tags: {gif_tags}")

    if gif_tags:
        # If giphy_find_with_metadata ever becomes async, update this call
        gif_result = giphy_find_with_metadata(gif_tags)
        gif_obj = gif_result.get("result", {}).get("gif")
        if gif_obj:
            print("🎞️ Found GIF result, attaching metadata...")
            post["GifAsset"] = extract_social_upload_metadata(gif_obj)
        else:
            print("❌ No GIF found from Giphy.")
    return post


def assemble_post_content(post: dict) -> tuple[str, Optional[str], Optional[str]]:
    post_text = post.get("Text", "")
    hashtags = post.get("Hashtags", [])
    full_text = f"{post_text}\n{' '.join(hashtags)}" if hashtags else post_text

    gif_asset = post.get("GifAsset")
    image_url = post.get("ImageAsset")

    media_url = gif_asset.get("gif_url") if gif_asset else image_url
    media_type = "GIF" if gif_asset else "IMAGE" if image_url else None

    return full_text, media_url, media_type
