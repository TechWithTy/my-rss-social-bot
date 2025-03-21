from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin

def main(blog_content):
    """Main function to process a blog post and post to LinkedIn"""
    global profile_id  

    print("🔹 Fetching LinkedIn Profile ID...")
    profile_id = get_linkedin_profile_id()  # Store profile_id

    if not profile_id:
        print("❌ Failed to retrieve LinkedIn profile ID. Exiting.")
        return

    print("✅ Successfully Authenticated with LinkedIn!")

    # Simulate AI-generated post text (Replace with real AI logic)
    linkedin_post = "🚀 AI-generated LinkedIn post from OpenAI Assistant!"

    print("🔹 Posting to LinkedIn...")
    post_to_linkedin( linkedin_post,profile_id)
    print("✅ Successfully posted to LinkedIn!")

# Example Blog Post
example_blog_content = """
    AI is transforming industries worldwide.
"""
main(example_blog_content)
