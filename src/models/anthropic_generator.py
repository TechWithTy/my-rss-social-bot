from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable

# ✅ Load environment variables
load_dotenv()
ANTHROPIC_API_KEY: Optional[str] = get_env_variable("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("❌ CLAUDE_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# ✅ LLM Configuration for Claude
claude_config = config.get("llm", {}).get("Anthropic", {})
claude_model = claude_config.get("model", "claude-3-sonnet")
temperature = claude_config.get("temperature", 0.7)
max_tokens = claude_config.get("max_tokens", 500)

def send_message_to_claude(blog_content: str) -> Optional[str]:
    """Sends a blog post to Claude AI and returns the AI-generated LinkedIn post."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    # 🔧 Config Sections
    user_config = config.get("user_profile", {})
    social_config = config.get("social_media_to_post_to", {}).get("linkedin", {})

    # 🔧 Instructions
    system_instructions = claude_config.get("custom_system_instructions", 
        "You're an expert LinkedIn content strategist who crafts viral, engaging posts.")
    
    user_instructions = claude_config.get("custom_user_instructions", 
        "Make the post concise, actionable, and optimized for engagement.")

    linkedin_max_chars = social_config.get("maximum_characters", "")

    # 🧠 Viral Preferences
    viral = claude_config.get("viral_posting", {})
    viral_style_instructions = "\n".join([
        viral.get("attention_grabbing_intro", {}).get("description", ""),
        viral.get("emotional_storytelling", {}).get("description", ""),
        viral.get("relatable_experiences", {}).get("description", ""),
        viral.get("actionable_takeaways", {}).get("description", ""),
        viral.get("data-backed_claims", {}).get("description", ""),
        viral.get("extreme_statements", {}).get("description", "")
    ]).strip()

    # 🎯 User Profile
    target_audience = user_config.get("target_audience", "General audience")
    professional_summary = user_config.get("professional_summary", "")

    # 🧨 Viral Examples
    viral_examples = claude_config.get("viral_posts_i_liked", [])
    formatted_viral_examples = "\n".join([
        f"📢 Text: {post.get('text')}\n📊 Engagement: {post.get('engagement')}\n💡 Why it worked: {post.get('reason')}"
        for post in viral_examples
    ])
    viral_examples_instruction = f"\n\nHere are some viral post examples for inspiration:\n{formatted_viral_examples}" if viral_examples else ""

    # #️⃣ Hashtags
    hashtags_config = config.get("hashtags", {})
    default_hashtags = hashtags_config.get("default_tags", [])
    custom_hashtags = hashtags_config.get("custom_tags", [])
    hashtag_instructions = f"\n\nInclude these hashtags: {default_hashtags} Custom tags: {custom_hashtags}" if default_hashtags or custom_hashtags else ""

    # 🎨 Creative Options
    creative = claude_config.get("creative", {})
    generate_image = creative.get("generate_image", {}).get("enabled", False)
    image_prompt = creative.get("generate_image", {}).get("prompt", "")
    fetch_gif = creative.get("post_gif", {}).get("enabled", False)
    gif_prompt = creative.get("post_gif", {}).get("prompt", "")

    creative_instruction = (
        f"\n\n[Visual Prompt]: {image_prompt}" if generate_image else f"\n\n[GIF Prompt]: {gif_prompt}"
    ) if generate_image or fetch_gif else ""

    # 📨 Final Message Content
    content = (
        f"Summarize this blog post into an engaging LinkedIn post (MAX {linkedin_max_chars} chars if applicable):\n\n"
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
    
    # ✅ Request Payload
    data = {
        "model": claude_model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": content}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        completion = response.json().get("content", [{}])[0].get("text", "").strip()
        print("✅ Claude AI Response Generated!")
        return completion
    else:
        print("❌ Error sending request to Claude AI:", response.json())
        return None
