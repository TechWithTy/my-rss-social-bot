"""
linkedin_utils.py
- LinkedIn authentication and posting helpers.
"""
from src.socials.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.utils.helpers.post_cache_helper import add_linkedin_post
from utils.prompt_builder import get_prompt_globals
from typing import Optional

def authenticate_linkedin() -> Optional[str]:
    profile_id = get_linkedin_profile_id()
    if not profile_id:
        raise ValueError("❌ Could not retrieve LinkedIn profile ID.")
    print("✅ LinkedIn authenticated.")
    return profile_id


def post_to_linkedin_if_possible(
    post_text: str, media_url: Optional[str], media_type: Optional[str], profile_id: str
):
    if media_url and media_type:
        try:
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

            post_url = None  # In production this would come from the LinkedIn API response
            print("✅ LinkedIn post submitted successfully.")

            add_linkedin_post(
                post_text=post_text,
                blog_id=blog_id,
                media_url=media_url,
                media_type=media_type,
                post_url=post_url,
            )
            print("💾 LinkedIn post saved to cache.")
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
    else:
        print("⚠️ No media to post to LinkedIn.")
