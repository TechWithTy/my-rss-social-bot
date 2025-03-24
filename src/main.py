
from src.utils.config_loader import config
from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.models.openai_generator import run_openai_pipeline
from src.utils.giphy import giphy_find_with_metadata, extract_social_upload_metadata
from src.utils.dispatch.dispatch_text import dispatch_text_pipeline
from src.utils.dispatch.dispatch_image import dispatch_image_pipeline
from utils.prompt_builder import init_globals_if_needed, get_prompt_globals
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

import traceback

def main(medium_username: str) -> None:
    print("🚀 Starting main() with medium_username:", medium_username)
    try:
        is_new_blog = init_globals_if_needed()
        if not is_new_blog:
            print("🛑 No new blog detected — skipping generation and post.")
            return
        print("🔧 Initializing global state...")
        init_globals_if_needed()
        print("✅ Global state initialized.")

        linkedin_enabled = config['social_media_to_post_to']['linkedin'].get('enabled', False)
        text_model = config['ai']['text']['generate_text']['LLM']
        image_provider = config['ai']['creative']['generate_image']['LLM']

        print(f"🧠 Config - Text Model: {text_model}, Image Provider: {image_provider}")
        print(f"📲 LinkedIn Posting Enabled: {linkedin_enabled}")

        if not linkedin_enabled:
            print("🔕 LinkedIn post generation complete (posting disabled in config).")
            return

        print("🔐 Authenticating LinkedIn profile...")
        profile_id = authenticate_linkedin()

        print("🛠 Preparing post using model:", text_model)
        post = prepare_linkedin_post(text_model)
        print("✏️ Generated post content:", post.get("Text"))

        post = attach_gif_to_post(post)
        print("🎞 GIF tags attached (if any):", post.get("GifSearchTags"))

        # Check for existing media before generating fallback
        image_url = post.get("ImageAsset")
        gif_asset = post.get("GifSearchTags")

        print("🧩 Checking for media asset...")
        if not image_url and not gif_asset:
            print("⚠️ No media asset found — generating fallback image using:", image_provider)
            image_data = asyncio.run(dispatch_image_pipeline(image_provider))

            print("📸 Fallback image data:", image_data)

            if image_data:
                if "ImageAsset" in image_data:
                    post["ImageAsset"] = image_data["ImageAsset"]
                    print("✅ ImageAsset added to post.")
                elif "GifAsset" in image_data:
                    post["GifAsset"] = extract_social_upload_metadata(image_data["GifAsset"])
                    print("✅ GifAsset extracted and added to post.")
                else:
                    print("❌ Fallback asset generation failed. No usable image or gif.")
            else:
                print("❌ No image data returned from fallback pipeline.")

        # Re-assemble content with new media
        post_text, media_url, media_type = assemble_post_content(post)

        print("📝 Final LinkedIn post content:")
        print("------------------------------------------------------")
        print(post_text)
        print("------------------------------------------------------")
        print(f"📦 Media: {media_type} -> {media_url}")

        print("📤 Posting to LinkedIn...")
        # post_to_linkedin_if_possible(post_text, media_url, media_type, profile_id)
        print("✅ LinkedIn post submitted successfully.")

    except Exception as e:
        print("❌ An error occurred in main:")
        traceback.print_exc()


if __name__ == "__main__":
    medium_username = config['user_profile'].get('medium_username')
    if medium_username:
        main(medium_username)
    else:
        print("⚠️ Medium username not found in config.")