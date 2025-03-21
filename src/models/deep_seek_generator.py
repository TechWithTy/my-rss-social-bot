from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable

# ✅ Load environment variables
load_dotenv()

DEEPSEEK_API_KEY: Optional[str] = get_env_variable("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("❌ DEEPSEEK_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# ✅ LLM Configuration
deepseek_model = config["user_profile"]["llm"]["DeepSeek"]["model"]
temperature = config["user_profile"]["llm"]["DeepSeek"]["temperature"]
max_tokens = config["user_profile"]["llm"]["DeepSeek"]["max_tokens"]

def send_message_to_deepseek(blog_content: str) -> Optional[str]:
    """Sends a blog post to DeepSeek AI and returns the AI-generated LinkedIn post."""
    url = "https://api.deepseek.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # 🔧 Config Sections
    user_config = config.get("user_profile", {})
    openai_config = config.get("openai", {})
    social_config = config.get("social_media_to_post_to", {}).get("linkedin", {})

    # 🔧 Instructions
    system_instructions = openai_config.get("custom_system_instructions") or (
        "You're a professional copywriter helping turn blog posts into viral LinkedIn content."
    )
    user_instructions = openai_config.get("custom_user_instructions") or (
        "Make the post concise, actionable, and emotionally resonant."
    )

    linkedin_enabled = social_config.get("enabled", False)
    linkedin_max_chars = social_config.get("maximum_characters", "")

    # 🧠 Viral Preferences
    viral = openai_config.get("viral_posting", {})
    viral_style_instructions = "\n".join([
        viral.get("attention_grabbing_intro", {}).get("description", ""),
        viral.get("emotional_storytelling", {}).get("description", ""),
        viral.get("relatable_experiences", {}).get("description", ""),
        viral.get("actionable_takeaways", {}).get("description", ""),
        viral.get("data-backed_claims", {}).get("description", ""),
        viral.get("extreme_statements", {}).get("description", "")
    ]).strip()

    # 🎯 User Profile
    target_audience = user_config.get("target_audience", "")
    professional_summary = user_config.get("professional_summary", "")

    # 🧨 Viral Examples
    viral_examples = openai_config.get("viral_posts_i_liked", [])
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
    hashtag_instructions = (
        f"\n\nInclude these default hashtags:\n{default_hashtags}\n"
        f"Custom tags (optional):\n{custom_hashtags}"
        if default_hashtags or custom_hashtags else ""
    )

    # 🎨 Creative Options
    creative = openai_config.get("creative", {})
    generate_image_cfg = creative.get("generate_image", {})
    post_gif_cfg = creative.get("post_gif", {})

    generate_image = generate_image_cfg.get("enabled", False)
    fetch_gif = post_gif_cfg.get("enabled", False)
    image_prompt = generate_image_cfg.get("prompt", "")
    gif_prompt = post_gif_cfg.get("prompt", "")

    if generate_image and fetch_gif:
        creative_instruction = (
            f"\n\nYou may choose to either generate an AI image ({image_prompt}) or fetch a GIF ({gif_prompt}) "
            "that enhances the blog content."
        )
    elif generate_image:
        creative_instruction = f"\n\n[Visual Prompt]: {image_prompt}"
    elif fetch_gif:
        creative_instruction = f"\n\n[GIF Prompt]: {gif_prompt}"
    else:
        creative_instruction = ""

    # 📨 Final Message Content
    content = (
        f"Summarize this blog post into an engaging "
        f"{'LinkedIn (' + str(linkedin_max_chars) + ' MAXIMUM chars) ' if linkedin_enabled else ''}post:\n\n"
        f"{blog_content}\n\n"
        f"For target audience: {target_audience}\n"
        f"About the writer: {professional_summary}\n\n"
        f"{user_instructions}\n\n"
        f"{viral_examples_instruction}\n\n"
        f"Viral Methodologies To use:\n{viral_style_instructions}\n\n"
        f"{hashtag_instructions}\n\n"
        f"{creative_instruction}"
    )

    print('Message Content:\n\n', content)
    
    data = {
        "model": deepseek_model,
        "prompt": content,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        completion = response.json().get("choices", [{}])[0].get("text", "").strip()
        print("✅ DeepSeek AI Response Generated!")
        return completion
    else:
        print("❌ Error sending request to DeepSeek AI:", response.json())
        return None
