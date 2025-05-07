"""
workflow.py
- Orchestrates the main workflow for the RSS-to-social bot.
- High-level entry point for running the workflow as a function.
"""
from src.socials.utils.linkedin_utils import authenticate_linkedin, post_to_linkedin_if_possible
from src.utils.post_utils import prepare_linkedin_post, attach_gif_to_post, assemble_post_content
from src.utils.config.config_loader import config
from src.utils.prompt_builder import init_globals_if_needed


from typing import Optional, Dict

# * Step 1: Initialize global state

def initialize_global_state() -> None:
    """
    Initializes any required global state for the workflow.
    """
    init_globals_if_needed()
    print("* Global state initialized.")

# * Step 2: Authenticate and get LinkedIn profile ID

def get_linkedin_profile_id_or_fail() -> str:
    """
    Authenticates with LinkedIn and returns the profile ID, or raises an error if not found.
    """
    profile_id = authenticate_linkedin()
    if not profile_id:
        print("❌ LinkedIn authentication failed: No profile ID.")
        raise RuntimeError("LinkedIn authentication failed.")
    return profile_id

# * Step 3: Generate the post (text)

async def generate_post_or_fail(text_model: str) -> Dict:
    """
    Generates a social post using the configured text model. Fails if no text is generated.
    """
    post = await prepare_linkedin_post(text_model=text_model)
    if not post or not post.get("Text"):
        print("❌ Text generation failed: No post content was generated.")
        raise RuntimeError("Text generation failed: No post content was generated.")
    return post

# * Step 4: Attach media (GIF/image) assets

async def attach_media_assets(post: Dict) -> Dict:
    """
    Attaches GIF or image assets to the post if available.
    """
    return await attach_gif_to_post(post)

# * Step 5: Assemble post content for publishing

async def assemble_post_for_publishing(post: Dict) -> tuple[str, Optional[str], Optional[str]]:
    """
    Assembles the final post content, media URL, and media type.
    """
    return assemble_post_content(post)

# * Step 6: Post to LinkedIn

def post_to_linkedin_pipeline(post_text: str, media_url: Optional[str], media_type: Optional[str], profile_id: str) -> None:
    """
    Handles posting the content to LinkedIn, including error handling.
    """
    post_to_linkedin_if_possible(post_text, media_url, media_type, profile_id)

# * Main orchestrator (pipeline)
async def run_rss_to_social_workflow(rss_source: str = None) -> None:
    """
    Main workflow for fetching blog content, generating a social post, attaching media, and posting to LinkedIn.
    Args:
        rss_source (str, optional): RSS feed URL or identifier. Uses config default if None.
    """
    try:
        initialize_global_state()
        profile_id = get_linkedin_profile_id_or_fail()
        text_model = config["ai"]["text"]["generate_text"]["LLM"]
        post = await generate_post_or_fail(text_model)
        post = await attach_media_assets(post)
        post_text, media_url, media_type = await assemble_post_for_publishing(post)
        post_to_linkedin_pipeline(post_text, media_url, media_type, profile_id)
        print("✅ Workflow completed.")
    except Exception as e:
        print(f"! Workflow failed: {e}")
        raise
