from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
from src.openai_generator import create_openai_thread, send_message_to_openai, run_openai_assistant, wait_for_openai_response, get_openai_response

def main(blog_content):
    """Main function to process a blog post and post to LinkedIn"""
    global profile_id  

    print("🔹 Fetching LinkedIn Profile ID...")
    profile_id = get_linkedin_profile_id()  # Store profile_id

    if not profile_id:
        print("❌ Failed to retrieve LinkedIn profile ID. Exiting.")
        return

    print("✅ Successfully Authenticated with LinkedIn!")

    print("🔹 Creating OpenAI Thread...")
    thread_id = create_openai_thread()
    if not thread_id:
        return

    print("🔹 Sending Blog Post to OpenAI Assistant...")
    send_message_to_openai(thread_id, blog_content)

    print("🔹 Running OpenAI Assistant...")
    run_id = run_openai_assistant(thread_id)
    if not run_id:
        return

    print("🔹 Waiting for OpenAI Response...")
    wait_for_openai_response(thread_id, run_id)

    print("🔹 Fetching AI-Generated LinkedIn Post...")
    linkedin_post = get_openai_response(thread_id)
    if not linkedin_post:
        print("❌ Failed to retrieve AI-generated content. Exiting.")
        return

    print("🔹 Posting to LinkedIn...")
    post_to_linkedin(
        linkedin_post,
        profile_id,
       media_url="https://media.giphy.com/media/CWmQC59IC4HGYOdWJL/giphy.gif?cid=790b7611342yvb7ylvrt42rl1ahn808whlbwtdt2cvm8w0f4&ep=v1_gifs_search&rid=giphy.gif&ct=g",  # Must be a direct image/GIF URL
    media_type="GIF"
    )
    print("✅ Successfully posted to LinkedIn!")

# Example Blog Post (Replace with actual content)
example_blog_content = """
    Artificial Intelligence (AI) is revolutionizing industries worldwide.
    From automation to deep learning, AI is helping businesses make data-driven decisions.
    Explore how AI is transforming technology in our latest blog post.
"""
main(example_blog_content)
