from typing import Dict, Any, Optional
from src.utils.helpers.prompt.prompt_sources import fetch_and_parse_blog
from src.utils.helpers.prompt.prompt_instructions import get_default_instructions, get_system_instructions, get_user_instructions
from src.utils.helpers.prompt.prompt_globals import get_prompt_globals
from src.utils.config.config_loader import config
from src.utils.helpers.blog_rss_helper import load_blog_cache
from src.utils.helpers.post_cache_helper import is_blog_already_posted
from src.utils.index import get_env_variable
from src.utils.index import parse_html_blog_content
import random

TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"

def build_prompt_payload(blog_content: str, blog_url: str = "", **kwargs) -> Optional[Dict[str, Any]]:
    # * Use config loaded from main config.yaml
    """
    Build the prompt payload for the AI model using blog content, system/user instructions, and config.
    """
    if not blog_content:
        print("Blog Content Empty", blog_content)
        return None

    # Instructions
    default_instructions = get_default_instructions()
    system_instructions = get_system_instructions()
    user_instructions = get_user_instructions()

    linkedin_config = config.get("social_media_to_post_to", {}).get("linkedin", {})
    user_config = config.get("user_profile", {})
    ai_config = config.get("ai", {})

    linkedin_enabled = linkedin_config.get("enabled", False)
    linkedin_max_chars = linkedin_config.get("maximum_characters", "")
    linkedin_min_chars = linkedin_config.get("minimum_characters", "")
    formatting_instructions = linkedin_config.get("formatting_instructions", "")
    target_audience = user_config.get("target_audience", "")
    professional_summary = user_config.get("professional_summary", "")

    # Viral Methodologies
    viral = ai_config.get("viral_posting", {})
    viral_style_instructions = "\n".join([
        viral.get("attention_grabbing_intro", {}).get("description", ""),
        viral.get("emotional_storytelling", {}).get("description", ""),
        viral.get("relatable_experiences", {}).get("description", ""),
        viral.get("actionable_takeaways", {}).get("description", ""),
        viral.get("data-backed_claims", {}).get("description", ""),
        viral.get("extreme_statements", {}).get("description", ""),
    ]).strip()

    # Viral Examples
    viral_examples = ai_config.get("viral_posts_i_liked", [])
    formatted_viral_examples = ""
    for post in viral_examples:
        formatted_viral_examples += (
            f"\n---\n"
            f"Text: {post.get('text')}\n"
            f"Engagement: {post.get('engagement')}\n"
            f"Creative: {post.get('creative')}\n"
            f"Asset: {post.get('creative_asset')}\n"
            f"Why it worked: {post.get('reason')}\n"
        )
    viral_examples_instruction = (
        f"\n\nHere are some viral post examples for inspiration:\n{formatted_viral_examples}"
        if formatted_viral_examples else ""
    )

    # Hashtags
    hashtags_config = config.get("hashtags", {})
    default_hashtags = hashtags_config.get("default_tags", [])
    custom_hashtags = hashtags_config.get("custom_tags", [])
    hashtags = default_hashtags + custom_hashtags
    hashtag_instructions = (
        f"\n\nInclude these default hashtags:\n{default_hashtags}\n"
        f"Custom tags (optional):\n{custom_hashtags}"
        if hashtags else ""
    )

    # Creative Options
    creative = ai_config.get("creative", {})
    generate_image_cfg = creative.get("generate_image", {})
    post_gif_cfg = creative.get("fetch_gif", {})
    generate_image = generate_image_cfg.get("enabled", False)
    fetch_gif = post_gif_cfg.get("enabled", False)
    image_prompt = generate_image_cfg.get("prompt", "")
    dimensions_width = generate_image_cfg.get("width", "")
    dimensions_height = generate_image_cfg.get("height", "")
    image_model = generate_image_cfg.get("model", "")
    gif_prompt = post_gif_cfg.get("prompt", "")
    if generate_image and fetch_gif:
        creative_instruction = (
            f"\n\nGenerate an AI image using prompt: ({image_prompt})\n"
            f"width: {dimensions_width}, height: {dimensions_height}, model: {image_model}"
            if random.choice([True, False])
            else f"\n\nFetch a GIF using prompt: ({gif_prompt})"
        ) + " that enhances the blog content."
    elif generate_image:
        creative_instruction = (
            f"\n\nGenerate an AI image using prompt: ({image_prompt})\n"
            f"width: {dimensions_width}, height: {dimensions_height}, model: {image_model}"
        )
    elif fetch_gif:
        creative_instruction = f"\n\n[GIF Prompt]: {gif_prompt}"
    else:
        creative_instruction = ""

    blog_url_instruction = (
        f"\n\nInclude the original blog URL in the post: {blog_url}" if blog_url else ""
    )
    content = (
        f"{system_instructions}"
        f"{user_instructions}"
        f"{default_instructions}"
        f"Summarize this blog post into an engaging "
        f"{'LinkedIn (' + str(linkedin_min_chars) + ' MINIMUM chars, ' + str(linkedin_max_chars) + ' MAXIMUM chars) ' if linkedin_enabled else ''}post:\n\n"
        f"{blog_content}\n\n"
        f"For target audience: {target_audience}\n"
        f"About the writer: {professional_summary}\n"
        f"{viral_examples_instruction}\n"
        f"Viral Methodologies To use:\n{viral_style_instructions}\n"
        f"{hashtag_instructions}\n"
        f"{creative_instruction}"
        f"{blog_url_instruction}"
        f"Formatting Instructions:\n{formatting_instructions}\n"
    )
    prompt_build_payload = {
        "content": content.strip(),
        "creative_prompt": image_prompt.strip(),
        "gif_prompt": gif_prompt.strip(),
        "hashtags": hashtags,
        "system_instructions": system_instructions,
        "user_instructions": user_instructions,
        "default_instructions": default_instructions,
        "blog_content": blog_content,
    }
    print("\n========== Final Prompt build_prompt_payload ==========")
    for i, line in enumerate(prompt_build_payload["content"].splitlines(), 1):
        print(f"{i:03}: {line}")
    print("========== END PROMPT build_prompt_payload ==    ========")
    return prompt_build_payload


def init_globals_if_needed() -> bool:
    """
    Initialize global state for the prompt pipeline if new blog is found.
    Returns True if new blog is ready, False if already posted or no new blog.
    """
    print("Initializing global state...")
    prompt_globals = get_prompt_globals()
    print("Current global state before update:", prompt_globals)
    blog_data = fetch_and_parse_blog()
    if not blog_data:
        print("No blog data returned from fetch_and_parse_blog")
        return False
    print("Blog data fetched successfully:")
    print("Blog ID:", blog_data["id"])
    print("Blog Content Length:", len(blog_data["content"]))
    blog_id = blog_data["id"]
    cached = load_blog_cache()
    print("Global Cache Check:", {k: v for k, v in cached.items() if k != "blogs"})
    # Normalize cached structure
    if isinstance(cached, list):
        cached = {"blogs": cached}
    elif not isinstance(cached, dict):
        print("Cache is invalid. Resetting.")
        cached = {"blogs": []}
    # 🛑 Check if this blog has already been posted
    if is_blog_already_posted(blog_id):
        print(f"🔄 Blog ID {blog_id} has already been posted to LinkedIn. Skipping duplicate post.")
        return False
    # ✅ Proceed with processing if blog is new
    prompt_payload = build_prompt_payload(
        blog_data["content"], blog_url=blog_data.get("direct_link", "")
    )
    if not prompt_payload:
        print("No prompt payload returned.")
        return False
    prompt_globals.update(
        {
            "prompt": prompt_payload.get("content"),
            "creative_prompt": prompt_payload.get("creative_prompt"),
            "gif_prompt": prompt_payload.get("gif_prompt"),
            "hashtags": prompt_payload.get("hashtags", []),
            "system_instructions": prompt_payload.get("system_instructions"),
            "blog_content": prompt_payload.get("blog_content"),
            "raw_blog": blog_data["raw"],
            "blog_url": blog_data.get("direct_link", ""),
        }
    )
    # print("Global state after update:", prompt_globals)
    print(f"✅ Successfully stored blog ID {blog_id} in LinkedIn post cache.")
    return True


def init_globals_for_test() -> None:
    """
    Initialize global state for prompt building in test mode.
    """
    if not TEST_MODE:
        raise RuntimeError("init_globals_for_test() should only be used in TEST_MODE (.env boolean)")
    cached = load_blog_cache()
    if not cached:
        print("No cached blog found. Fetching fresh one for test.")
        from rss_feed.medium_bot import fetch_latest_medium_blog
        from utils.config.config_loader import config as test_config
        medium_username = test_config.get("user_profile", {}).get("medium_username")
        fresh = fetch_latest_medium_blog(medium_username)
        if not fresh or not fresh["latest_blog"]["content"]:
            raise RuntimeError("Could not fetch fresh blog content for tests.")
        blog_content_raw = fresh["latest_blog"]["content"]
    else:
        blog_content_raw = cached["blogs"][0]["content"]
        if not blog_content_raw:
            raise RuntimeError("Cached blog has no 'content' key.")
    prompt_globals = get_prompt_globals()
    prompt_globals["blog_content"] = parse_html_blog_content(blog_content_raw)
    preview = blog_content_raw[:300] + "..." if blog_content_raw and len(blog_content_raw) > 300 else blog_content_raw
    print("Parsed HTML Text Prompt Builder:", preview)
    prompt_payload = build_prompt_payload(blog_content_raw)
    if not prompt_payload:
        raise RuntimeError("No prompt payload could be generated.")
    prompt_globals.update(
        {
            "prompt": prompt_payload.get("content"),
            "creative_prompt": prompt_payload.get("creative_prompt"),
            "gif_prompt": prompt_payload.get("gif_prompt"),
            "hashtags": prompt_payload.get("hashtags", []),
            "system_instructions": prompt_payload.get("system_instructions"),
        }
    )
    print("PromptBuilder Test Ran ", prompt_globals["prompt"])
