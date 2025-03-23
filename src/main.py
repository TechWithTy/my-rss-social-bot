from src.utils.config_loader import config
from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.models.openai_generator import run_openai_pipeline
from src.utils.giphy import giphy_find_with_metadata, extract_social_upload_metadata
from src.utils.dispatch.dispatch_text import dispatch_text_pipeline
from src.utils.dispatch.dispatch_image import dispatch_image_pipeline
import asyncio

from src.data.example_ai_response import ai_img_example, ai_gif_example
from typing import Optional


def authenticate_linkedin() -> Optional[str]:
    profile_id = get_linkedin_profile_id()
    if not profile_id:
        raise ValueError("❌ Could not retrieve LinkedIn profile ID.")
    print("✅ LinkedIn authenticated.")
    return profile_id


def prepare_linkedin_post(text_model: str) -> dict:
    print("🚀 Generating LinkedIn post...")
    return dispatch_text_pipeline(text_model)


def attach_gif_to_post(post: dict) -> dict:
    gif_tags = post.get("GifSearchTags", [])
    print(f"🔍 GIF search tags: {gif_tags}")
    
    if gif_tags:
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


def post_to_linkedin_if_possible(post_text: str, media_url: Optional[str], media_type: Optional[str], profile_id: str):
    if media_url and media_type:
        post_to_linkedin(
            post_text=post_text,
            profile_id=profile_id,
            media_url=media_url,
            media_type=media_type
        )
    else:
        print("🚫 Skipping post — no valid media asset was available.")


def main(medium_username: str) -> None:
    try:
        linkedin_enabled = config['social_media_to_post_to']['linkedin'].get('enabled', False)
        text_model = config['ai']['text']['generate_text']['LLM']
        image_provider = config['ai']['creative']['generate_image']['LLM']

        if not linkedin_enabled:
            print("🔕 LinkedIn post generation complete (posting disabled).")
            return

        profile_id = authenticate_linkedin()
        post = prepare_linkedin_post(text_model)
        post = attach_gif_to_post(post)

        # Check for existing media before generating fallback
        image_url = post.get("ImageAsset")
        gif_asset = post.get("GifSearchTags")

        if not image_url and not gif_asset:
            print("⚠️ No media asset found — generating fallback image...")
            image_data = asyncio.run(dispatch_image_pipeline(image_provider))

            if image_data:
                if "ImageAsset" in image_data:
                    post["ImageAsset"] = image_data["ImageAsset"]
                elif "GifAsset" in image_data:
                    post["GifAsset"] = extract_social_upload_metadata(image_data["GifAsset"])
                else:
                    print("❌ Fallback asset generation failed.")


        # Re-assemble content with new media
        post_text, media_url, media_type = assemble_post_content(post)

        print("📝 Final post text:\n", post_text)
        print(f"📦 Media: {media_type} -> {media_url}")
        # post_to_linkedin_if_possible(post_text, media_url, media_type, profile_id)

    except Exception as e:
        print(f"❌ An error occurred in main: {e}")

if __name__ == "__main__":
    medium_username = config['user_profile'].get('medium_username')
    if medium_username:
        main(medium_username)
    else:
        print("⚠️ Medium username not found in config.")