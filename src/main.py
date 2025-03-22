from src.config_loader import config
from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.models.openai_generator import (
    create_openai_thread,
    send_message_to_openai,
    run_openai_assistant,
    wait_for_openai_response,
    get_openai_response
)
from src.medium_bot import fetch_latest_medium_blog
from src.utils.index import parse_html_blog_content
from src.utils.giphy import giphy_find_with_metadata ,extract_social_upload_metadata


def fetch_and_parse_blog(username: str) -> str | None:
    blog_content = fetch_latest_medium_blog(username)
    if not blog_content:
        print("ℹ️ No blog content found.")
        return None
    return parse_html_blog_content(blog_content)


def run_openai_pipeline(blog_content: str) -> str | None:
    thread_id = create_openai_thread()
    if not thread_id:
        print("❌ Failed to create OpenAI thread.")
        return None

    send_message_to_openai(thread_id, blog_content)
    run_id = run_openai_assistant(thread_id)
    if not run_id:
        print("❌ Failed to run OpenAI assistant.")
        return None

    wait_for_openai_response(thread_id, run_id)
    return get_openai_response(thread_id)


def main(medium_username: str) -> None:
    try:
        linkedin_enabled = config['social_media_to_post_to']['linkedin'].get('enabled', False)
        print(f"🔄 LinkedIn Enabled: {linkedin_enabled} | Medium: {medium_username}")

        profile_id = get_linkedin_profile_id()
        if not profile_id:
            raise ValueError("Could not retrieve LinkedIn profile ID.")
        print("✅ LinkedIn authenticated.")

        parsed_blog = fetch_and_parse_blog(medium_username)
        if not parsed_blog:
            return

       

        if linkedin_enabled: 
            linkedin_post = run_openai_pipeline(parsed_blog)
            if not linkedin_post:
                raise ValueError("OpenAI did not return a valid LinkedIn post.")

        gif_tags = linkedin_post.get("GifSearchTags")

        # 🔍 Handle GIF search
        if gif_tags:
            gif_result = giphy_find_with_metadata(gif_tags)
            gif_obj = gif_result.get("gif")
            if gif_obj:
                linkedin_post["GifAsset"] = extract_social_upload_metadata(gif_obj)

        # 🖼️ Handle Image asset
        image_url = linkedin_post.get("ImageAsset")

        # ✅ Choose valid asset for posting
        media_url = None
        media_type = None
        linkedin_post_text = linkedin_post.get("Text", "")
        hashtags = linkedin_post.get("Hashtags", [])

        # Turn hashtag list into string: "#AI #ML #Tech"
        hashtags_text = " ".join(hashtags)

        # Final post text with hashtags appended
        linkedin_post_text = f"{linkedin_post_text}\n{hashtags_text}" if hashtags_text else linkedin_post_text
        
        if linkedin_post.get("GifAsset"):
            media_url = linkedin_post["GifAsset"].get("mp4_url")
            media_type = "GIF"
        elif image_url:
            media_url = image_url
            media_type = "IMAGE"

        # 🔄 Post only if there's valid media
        if media_url and media_type:
            post_to_linkedin(
                post_text=linkedin_post,
                profile_id=profile_id,
                media_url=media_url,
                media_type=media_type
            )

            print("✅ Successfully posted to LinkedIn!")
        else:
            print("🔕 LinkedIn post generation complete (posting disabled).")
            print(f"\n📋 Suggested Post:\n{linkedin_post}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    medium_username = config['user_profile'].get('medium_username')
    if medium_username:
        main(medium_username)
    else:
        print("⚠️ Medium username not found in config.")
