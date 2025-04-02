from src.utils.config.config_loader import config
from src.socials.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.socials.giphy import giphy_find_with_metadata, extract_social_upload_metadata
from src.utils.dispatch.dispatch_text import dispatch_text_pipeline
from src.utils.dispatch.dispatch_image import dispatch_image_pipeline
from src.utils.helpers.blog_rss_helper import (
    load_blog_cache,
    save_blog_cache,
)
from src.utils.helpers.post_cache_helper import add_linkedin_post, is_blog_already_posted
from src.utils.prompt_builder import init_globals_if_needed, get_prompt_globals
import asyncio
import traceback
from src.utils.index import get_env_variable
from typing import Optional


TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"


def authenticate_linkedin() -> Optional[str]:   
    profile_id = get_linkedin_profile_id()
    if not profile_id:
        raise ValueError("Could not retrieve LinkedIn profile ID.")
    print("LinkedIn authenticated.")
    return profile_id


def prepare_linkedin_post(text_model: str) -> dict:
    print("Generating LinkedIn post...")
    return dispatch_text_pipeline(text_model)


def attach_gif_to_post(post: dict) -> dict:
    gif_tags = post.get("GifSearchTags", [])
    print(f"GIF search tags: {gif_tags}")

    if gif_tags:
        gif_result = giphy_find_with_metadata(gif_tags)
        gif_obj = gif_result.get("result", {}).get("gif")
        if gif_obj:
            print("Found GIF result, attaching metadata...")
            post["GifAsset"] = extract_social_upload_metadata(gif_obj)
        else:
            print("No GIF found from Giphy.")
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


def post_to_linkedin_if_possible(
    post_text: str, media_url: Optional[str], media_type: Optional[str], profile_id: str
):
    if media_url and media_type:
        try:
            # Get blog_id from global state for reference
            state = get_prompt_globals()
            raw_blog = state.get("raw_blog", {})
            blog_id = raw_blog.get("id") if isinstance(raw_blog, dict) else None
            
            # Uncomment this line to actually post to LinkedIn
            # linkedin_response = post_to_linkedin(
            #     post_text=post_text,
            #     profile_id=profile_id,
            #     media_url=media_url,
            #     media_type=media_type
            # )
            # post_url = extract_post_url_from_response(linkedin_response) if linkedin_response else None
            
            # For development/testing purposes
            post_url = None  # In production this would come from the LinkedIn API response
            print("✅ LinkedIn post submitted successfully.")

            # Save the post to the LinkedIn post cache with media information
            add_linkedin_post(
                post_text=post_text, 
                blog_id=blog_id, 
                media_url=media_url,
                media_type=media_type,
                post_url=post_url
            )
            print("💾 LinkedIn post saved to cache.")
            
            # ✅ After successful post, update the blog cache
            if raw_blog:
                cached = load_blog_cache()

                # 🧠 Normalize the cache structure to always support cached["blogs"]
                if isinstance(cached, list):
                    print("⚠️ Cache is a list — converting to dict with blogs key.")
                    cached = {"blogs": cached}
                elif not isinstance(cached, dict):
                    print("⚠️ Invalid cache structure — resetting.")
                    cached = {"blogs": []}
                elif "blogs" not in cached:
                    cached["blogs"] = []

                print("🧠 Updating blog cache with new post ID...", raw_blog)
                cached["blogs"].insert(0, raw_blog)  # Prepend newest blog
                save_blog_cache(cached)
                print("💾 Blog successfully saved to cache.")

            else:
                print("⚠️ raw_blog missing from state — cache not updated.")

        except Exception as e:
            print("❌ Failed to post to LinkedIn:", e)
    else:
        print("🚫 Skipping post — no valid media asset was available.")


# Helper function to extract post URL from LinkedIn API response (placeholder)
def extract_post_url_from_response(response):
    """Extract post URL from LinkedIn API response if available."""
    # In a real implementation, this would parse the API response
    # LinkedIn API doesn't currently return the post URL directly
    # This is a placeholder for future implementation
    return None


def main(rss_source: str) -> None:
    if TEST_MODE:
        raise RuntimeError(
            "❌ main() should not run when TEST_MODE is enabled. Turn off TEST_MODE or run tests directly."
        )
    print("🚀 Starting main() with rss_source:", rss_source)
    try:
        is_new_blog = init_globals_if_needed()
        if not is_new_blog:
            print("🛑 No new blog detected — skipping generation and post.")
            return
        print("✅ Global state initialized.")
        
        # Get blog info from global state
        state = get_prompt_globals()
        raw_blog = state.get("raw_blog", {})
        blog_id = raw_blog.get("id") if isinstance(raw_blog, dict) else None
        
        # Check if this blog has already been posted to LinkedIn
        if blog_id and is_blog_already_posted(blog_id):
            print(f"🔄 Blog ID {blog_id} has already been posted to LinkedIn. Skipping duplicate post.")
            return

        linkedin_enabled = config["social_media_to_post_to"]["linkedin"].get(
            "enabled", False
        )
        text_model = config["ai"]["text"]["generate_text"]["LLM"]
        image_provider = config["ai"]["creative"]["generate_image"]["LLM"]

        print(f"🧠 Config - Text Model: {text_model}, Image Provider: {image_provider}")
        print(f"📲 LinkedIn Posting Enabled: {linkedin_enabled}")

        if not linkedin_enabled:
            print("🔕 LinkedIn post generation complete (posting disabled in config).")
            return

        print("🔐 Authenticating LinkedIn profile...")
        profile_id = authenticate_linkedin()

        print("🛠 Preparing post using model:", text_model)
        post = prepare_linkedin_post(text_model)
        
        # Check if post text was successfully generated
        if not post or not post.get("Text"):
            raise ValueError("❌ Failed to generate text for the post. Aborting process.")
            
        print("✏️ Generated post content:", post.get("Text"))

        post = attach_gif_to_post(post)
        print("🎞 GIF tags attached (if any):", post.get("GifSearchTags"))

        # Check for existing media before generating fallback
        image_url = post.get("ImageAsset")
        gif_asset = post.get("GifSearchTags")

        print("🧩 Checking for media asset...")
        if not image_url and not gif_asset:
            print(
                "⚠️ No media asset found — generating fallback image using:",
                image_provider,
            )
            image_data = asyncio.run(dispatch_image_pipeline(image_provider))

            print("📸 Fallback image data:", image_data)

            if image_data:
                if "ImageAsset" in image_data:
                    post["ImageAsset"] = image_data["ImageAsset"]
                    print("✅ ImageAsset added to post.")
                elif "GifAsset" in image_data:
                    post["GifAsset"] = extract_social_upload_metadata(
                        image_data["GifAsset"]
                    )
                    print("✅ GifAsset extracted and added to post.")
                else:
                    print(
                        "❌ Fallback asset generation failed. No usable image or gif."
                    )
            else:
                print("❌ No image data returned from fallback pipeline.")

        # Re-assemble content with new media
        post_text, media_url, media_type = assemble_post_content(post)

        print("📝 Final LinkedIn post content:")
        print("------------------------------------------------------")
        print(post_text)
        print("------------------------------------------------------")
        print(f"📦 Media: {media_type} -> {media_url}")

        post_to_linkedin_if_possible(post_text, media_url, media_type, profile_id)

    except Exception as e:
        print("❌ An error occurred in main:")
        traceback.print_exc()
        raise  # Re-raise the exception to ensure the function fails completely


if __name__ == "__main__":
    medium_username = config["user_profile"].get("medium_username")
    wix_url = config["user_profile"].get("wix_url")
    wordpress_url = config["user_profile"].get("wordpress_url")

    # Collect enabled sources
    enabled_sources = [
        source for source in [medium_username, wix_url, wordpress_url] if source
    ]

    # Ensure only ONE source is enabled at a time
    if len(enabled_sources) > 1:
        print(
            "Only one RSS source can be enabled at a time. Please check your config!"
        )
    elif enabled_sources:
        main(enabled_sources[0])  # Pass only the single enabled source
    else:
        print("RSS Feed URL or Username Not Given In Config!")
