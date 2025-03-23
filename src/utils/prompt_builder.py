import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import random
from typing import Dict, Any, List, Tuple
from utils.config_loader import config
from medium_bot import fetch_latest_medium_blog
from utils.index import parse_html_blog_content

def fetch_and_parse_blog(username: str) -> str | None:
    blog_content = fetch_latest_medium_blog(username,False)
    if not blog_content:
        print("ℹ️ No blog content found.")
        return None
    return parse_html_blog_content(blog_content)
    

def build_prompt_payload() -> Dict[str, Any]:
    ai_config = config.get("ai", {})
    user_config = config.get("user_profile", {})
    social_config = config.get("social_media_to_post_to", {}).get("linkedin", {})

    medium_username = user_config.get('medium_username')
    
    blog_content = fetch_and_parse_blog(medium_username)
    # 🔧 Instructions
    system_instructions = ai_config.get("custom_system_instructions") or (
        "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
    )
    user_instructions = ai_config.get("custom_user_instructions") or (
        "Make the post concise, actionable, and emotionally resonant."
    )

    linkedin_enabled = social_config.get("enabled", False)
    linkedin_max_chars = social_config.get("maximum_characters", "")

    # 🎯 User Profile
    target_audience = user_config.get("target_audience", "")
    professional_summary = user_config.get("professional_summary", "")

    # 🧨 Viral Methodologies
    viral = ai_config.get("viral_posting", {})
    viral_style_instructions = "\n".join([
        viral.get("attention_grabbing_intro", {}).get("description", ""),
        viral.get("emotional_storytelling", {}).get("description", ""),
        viral.get("relatable_experiences", {}).get("description", ""),
        viral.get("actionable_takeaways", {}).get("description", ""),
        viral.get("data-backed_claims", {}).get("description", ""),
        viral.get("extreme_statements", {}).get("description", "")
    ]).strip()

    # 🧠 Viral Examples
    viral_examples = ai_config.get("viral_posts_i_liked", [])
    formatted_viral_examples = ""
    for post in viral_examples:
        formatted_viral_examples += (
            f"\n---\n"
            f"📢 Text: {post.get('text')}\n"
            f"📊 Engagement: {post.get('engagement')}\n"
            f"🎨 Creative: {post.get('creative')}\n"
            f"🔗 Asset: {post.get('creative_asset')}\n"
            f"💡 Why it worked: {post.get('reason')}\n"
        )

    viral_examples_instruction = (
        f"\n\nHere are some viral post examples for inspiration:\n{formatted_viral_examples}"
        if formatted_viral_examples else ""
    )

    # #️⃣ Hashtags
    hashtags_config = config.get("hashtags", {})
    default_hashtags = hashtags_config.get("default_tags", [])
    custom_hashtags = hashtags_config.get("custom_tags", [])
    hashtags = default_hashtags + custom_hashtags

    hashtag_instructions = (
        f"\n\nInclude these default hashtags:\n{default_hashtags}\n"
        f"Custom tags (optional):\n{custom_hashtags}"
        if hashtags else ""
    )

    # 🎨 Creative Options
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

    # 📨 Final Prompt
    content = (
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
        f"{user_instructions}"
      
    )

    return {
        "content": content.strip(),
        "creative_prompt": image_prompt.strip(),
        "gif_prompt": gif_prompt.strip(),
        "hashtags": hashtags,
        "system_instructions": system_instructions
    }
