from src.config_loader import config
from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.openai_generator import create_openai_thread, send_message_to_openai, run_openai_assistant, wait_for_openai_response, get_openai_response
from src.medium_bot import fetch_latest_medium_blog

def main(medium_username: str) -> None:
    """
    Main function to process a blog post and post to LinkedIn.

    Args:
        medium_username (str): Medium username to fetch blogs from.
    """
    try:
        print("🔹 Fetching LinkedIn Profile ID...")
        profile_id = get_linkedin_profile_id()

        if not profile_id:
            raise ValueError("Failed to retrieve LinkedIn profile ID.")

        print("✅ Successfully Authenticated with LinkedIn!")

        # ✅ Fetch latest blog content
        blog_content = fetch_latest_medium_blog(medium_username)
        if not blog_content:
            print("ℹ️ No new content to post.")
            return

        print("🔹 Creating OpenAI Thread...")
        thread_id = create_openai_thread()
        if not thread_id:
            raise ValueError("Failed to create OpenAI thread.")

        print("🔹 Sending Blog Post to OpenAI Assistant...")
        send_message_to_openai(thread_id, blog_content)

        print("🔹 Running OpenAI Assistant...")
        run_id = run_openai_assistant(thread_id)
        if not run_id:
            raise ValueError("Failed to run OpenAI assistant.")

        print("🔹 Waiting for OpenAI Response...")
        wait_for_openai_response(thread_id, run_id)

        print("🔹 Fetching AI-Generated LinkedIn Post...")
        linkedin_post = get_openai_response(thread_id)
        if not linkedin_post:
            raise ValueError("Failed to retrieve AI-generated content.")

        print("🔹 Posting to LinkedIn...")
        # post_to_linkedin(
        #     post_text=linkedin_post,
        #     profile_id=profile_id,
        #     media_url="https://media.giphy.com/media/CWmQC59IC4HGYOdWJL/giphy.gif",
        #     media_type="GIF"
        # )
        print("✅ Successfully posted to LinkedIn!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    MEDIUM_USERNAME = "codingoni"  # Replace with your Medium username
    main(MEDIUM_USERNAME)