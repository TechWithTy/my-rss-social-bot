import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import random
from typing import Dict, Any, List, Tuple, Optional
from utils.config_loader import config
from rss_feed.medium_bot import fetch_latest_medium_blog
from rss_feed.wix_bot import fetch_latest_wix_blog
from rss_feed.wordpress_bot import fetch_latest_wordpress_blog
from utils.index import get_env_variable

from utils.index import parse_html_blog_content
from utils.blog_rss_helper import load_blog_cache

TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"
_prompt_globals = {
    "prompt": None,
    "creative_prompt": None,
    "gif_prompt": None,
    "hashtags": [],
    "system_instructions": None,
    "blog_content": None,
}

ai_config = config.get("ai", {})
user_config = config.get("user_profile", {})
social_config = config.get("social_media_to_post_to", {}).get("linkedin", {})

medium_username = user_config.get("medium_username")
wix_url = user_config.get("wix_url")
wordpress_url = user_config.get("wordpress_url")


def fetch_and_parse_blog() -> Optional[dict]:
    """
    Fetch the latest blog from the first available source in order of priority:
    Medium → Wix → WordPress.

    Returns:
        Optional[dict]: Latest blog data if found, otherwise None.
    """
    sources = {
        "Medium": (medium_username, fetch_latest_medium_blog),
        "Wix": (wix_url, fetch_latest_wix_blog),
        "WordPress": (wordpress_url, fetch_latest_wordpress_blog),
    }

    response = None  # Initialize response to avoid undefined variable error

    for platform, (identifier, fetch_function) in sources.items():
        if identifier:
            print(f"Fetching from {platform}...")
            response = fetch_function(identifier)
            if response:
                break  # Stop at the first valid response

    if response is None:
        print("No new blogs to parse — already up to date.")
        return None

    blog_json = response.get("latest_blog", {})
    blog_content = blog_json.get("content")
    blog_id = blog_json.get("id")

    if not blog_content:
        print("No blog content found in the latest blog.")
        return None

    cleaned_blog_content = parse_html_blog_content(blog_content)

    return {"id": blog_id, "content": cleaned_blog_content, "raw": blog_json}


def build_prompt_payload(blog_content: str) -> Dict[str, Any]:
    if not blog_content:
        print("Blog Content Empty", blog_content)
        return None

    # Instructions
    default_instructions = ai_config.get("default_response_instructions") or (
        "Return EITHER a generated JSON image (Creative and ImageAsset) if a creative prompt is provided OR GifSearchTags if not—never both. Example response: { \"Text\": \"Your message here.\", \"Creative\": \"[IMG] A relevant visual description.\", \"ImageAsset\": \"https://image.pollinations.ai/prompt/{description}?width={width}&height={height}&seed={seed}&model=flux-realistic&nologo=true\", \"Hashtags\": [\"#Relevant\", \"#Contextual\", \"#GeneralTopic\"] } or { \"Text\": \"Message.\", \"Hashtags\": [\"#tag\", \"#tag\", \"#tag\"], \"GifSearchTags\": [\"term one\", \"term two\", \"term three\"] }"
    )
    system_instructions = ai_config.get("custom_system_instructions") or (
        "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
    )
    user_instructions = ai_config.get("custom_user_instructions") or (
        "Make the post concise, actionable, and emotionally resonant."
    )
    

    linkedin_enabled = social_config.get("enabled", False)
    linkedin_max_chars = social_config.get("maximum_characters", "")

    # User Profile
    target_audience = user_config.get("target_audience", "")
    professional_summary = user_config.get("professional_summary", "")

    # Viral Methodologies
    viral = ai_config.get("viral_posting", {})
    viral_style_instructions = "\n".join(
        [
            viral.get("attention_grabbing_intro", {}).get("description", ""),
            viral.get("emotional_storytelling", {}).get("description", ""),
            viral.get("relatable_experiences", {}).get("description", ""),
            viral.get("actionable_takeaways", {}).get("description", ""),
            viral.get("data-backed_claims", {}).get("description", ""),
            viral.get("extreme_statements", {}).get("description", ""),
        ]
    ).strip()

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
        if formatted_viral_examples
        else ""
    )

    # Hashtags
    hashtags_config = config.get("hashtags", {})
    default_hashtags = hashtags_config.get("default_tags", [])
    custom_hashtags = hashtags_config.get("custom_tags", [])
    hashtags = default_hashtags + custom_hashtags

    hashtag_instructions = (
        f"\n\nInclude these default hashtags:\n{default_hashtags}\n"
        f"Custom tags (optional):\n{custom_hashtags}"
        if hashtags
        else ""
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

    # Final Prompt
    content = (
        f"{system_instructions}"
        f"{default_instructions}"
        f"{user_instructions}"
        f"Summarize this blog post into an engaging "
        f"{'LinkedIn (' + str(linkedin_max_chars) + ' MAXIMUM chars) ' if linkedin_enabled else ''}post:\n\n"
        f"{blog_content}\n\n"
        f"For target audience: {target_audience}\n"
        f"About the writer: {professional_summary}\n"
        f"{viral_examples_instruction}\n"
        f"Viral Methodologies To use:\n{viral_style_instructions}\n"
        f"{hashtag_instructions}\n"
        f"{creative_instruction}\n"
        f"{default_instructions}"
    )

    return {
        "content": content.strip(),
        "creative_prompt": image_prompt.strip(),
        "gif_prompt": gif_prompt.strip(),
        "hashtags": hashtags,
        "system_instructions": system_instructions,
        "user_instructions": user_instructions,
        "default_instructions": default_instructions,
        "blog_content": blog_content,
    }


def get_prompt_globals():
    return _prompt_globals


def init_globals_if_needed() -> bool:
    global _prompt_globals

    blog_data = fetch_and_parse_blog()
    if not blog_data:
        return False

    blog_id = blog_data["id"]
    cached = load_blog_cache()

    # Normalize cached structure
    if isinstance(cached, list):  # legacy or empty structure
        cached = {"blogs": cached}
    elif not isinstance(cached, dict):
        print("Cache is invalid. Resetting.")
        cached = {"blogs": []}

    print("Global Cache Check:", cached)

    # Now this is safe
    cached_blog_ids = [b["id"] for b in cached.get("blogs", [])]

    if blog_id in cached_blog_ids:
        print(f"Blog with ID {blog_id} already processed.")
        return False

    prompt_payload = build_prompt_payload(blog_data["content"])
    if not prompt_payload:
        print("No prompt payload returned.")
        return False

    _prompt_globals.update(
        {
            "prompt": prompt_payload.get("content"),
            "creative_prompt": prompt_payload.get("creative_prompt"),
            "gif_prompt": prompt_payload.get("gif_prompt"),
            "hashtags": prompt_payload.get("hashtags", []),
            "system_instructions": prompt_payload.get("system_instructions"),
            "blog_content": prompt_payload.get("blog_content"),
            "raw_blog": blog_data["raw"],  # Needed for saving later
        }
    )

    return True


def init_globals_for_test():
    global _prompt_globals
    if not TEST_MODE:
        raise RuntimeError(
            "init_globals_for_test() should only be used in TEST_MODE (.env boolean)"
        )

    cached = load_blog_cache()

    if not cached:
        print("No cached blog found. Fetching fresh one for test.")
        fresh = fetch_latest_medium_blog(medium_username)
        if not fresh or not fresh["latest_blog"]["content"]:
            raise RuntimeError("Could not fetch fresh blog content for tests.")
        blog_content_raw = fresh["latest_blog"]["content"]
    else:
        blog_content_raw = cached["blogs"][0]["content"]
        if not blog_content_raw:
            raise RuntimeError("Cached blog has no 'content' key.")

    _prompt_globals["blog_content"] = parse_html_blog_content(blog_content_raw)

    prompt_payload = build_prompt_payload(blog_content_raw)
    if not prompt_payload:
        raise RuntimeError("No prompt payload could be generated.")

    _prompt_globals.update(
        {
            "prompt": prompt_payload.get("content"),
            "creative_prompt": prompt_payload.get("creative_prompt"),
            "gif_prompt": prompt_payload.get("gif_prompt"),
            "hashtags": prompt_payload.get("hashtags", []),
            "system_instructions": prompt_payload.get("system_instructions"),
        }
    )

    print("PromptBuilder Test Ran ", _prompt_globals["prompt"])
