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

        linkedin_post = run_openai_pipeline(parsed_blog)
        if not linkedin_post:
            raise ValueError("OpenAI did not return a valid LinkedIn post.")

        if linkedin_enabled:
            # 🔄 Uncomment to enable real posting
            # post_to_linkedin(
            #     post_text=linkedin_post,
            #     profile_id=profile_id,
            #     media_url="https://media.giphy.com/media/CWmQC59IC4HGYOdWJL/giphy.gif",
            #     media_type="GIF"
            # )
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
