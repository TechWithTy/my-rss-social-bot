from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable

# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY: Optional[str] = get_env_variable("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("❌ HUGGINGFACE_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

# ✅ LLM Configuration for Hugging Face
hf_config = config.get("user_profile",{}).get("llm", {}).get("HuggingFace", {})
hf_text_model = hf_config.get("text_model", "meta-llama/Meta-Llama-3-8B")
temperature = hf_config.get("temperature", 0.7)
max_tokens = hf_config.get("max_tokens", 500)

def send_message_to_huggingface(blog_content: str) -> Optional[str]:
    """Sends a blog post to Hugging Face API and returns the AI-generated LinkedIn post."""
    url = f"https://api-inference.huggingface.co/models/{hf_text_model}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    # 🔧 Config Sections
    user_config = config.get("user_profile", {})
    hf_config = config.get("llm", {}).get("HuggingFace", {})
    social_config = config.get("social_media_to_post_to", {}).get("linkedin", {})

    # 🔧 Instructions
    system_instructions = hf_config.get("custom_system_instructions", 
        "You're an expert LinkedIn content strategist who crafts viral, engaging posts.")
    
    user_instructions = hf_config.get("custom_user_instructions", 
        "Make the post concise, actionable, and optimized for engagement.")

    linkedin_max_chars = social_config.get("maximum_characters", "")

    # 🧠 Viral Preferences
    viral = hf_config.get("viral_posting", {})
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
    viral_examples = hf_config.get("viral_posts_i_liked", [])
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
    creative = hf_config.get("creative", {})
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
        "inputs": content,
        "parameters": {
            "temperature": temperature,
            "max_length": max_tokens,
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()[0].get("generated_text", "").strip()
        print("✅ Hugging Face Response Generated!")
        return completion
    else:
        print("❌ Error sending request to Hugging Face API:", response.json())
        return None


ai_config = config.get("ai", {})
image_config = hf_config.get("image_generation", {})
# 🎨 Creative Configurations
creative_config = ai_config.get("creative", {})
# ✅ Load Hugging Face Image Generation Config
generate_image_config = creative_config.get("generate_image", {})
generate_image_enabled = generate_image_config.get("enabled", False)
image_prompt = generate_image_config.get("prompt", "")
image_size = generate_image_config.get("size", "1024x1024")
image_model = hf_config.get("image_model", "meta-llama/Meta-Llama-3-8B")

def generate_image_with_huggingface() -> Optional[str]:
    """
    Generates an AI image using a Hugging Face model and returns the image URL.

    Returns:
        Optional[str]: URL to the generated image (if successful), else None.
    """
    if not image_model:
        print("❌ Image generation is disabled in the YAML config.")
        return None

    print(f"🎨 Generating image with model: {image_model}")

    url = f"https://api-inference.huggingface.co/models/{image_model}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": image_prompt,
        "parameters": {
            "height": int(image_size.split("x")[0]),
            "width": int(image_size.split("x")[1])
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        output = response.json()
        image_url = output.get("generated_image", None)

        if image_url:
            print(f"✅ Image generated successfully: {image_url}")
            return image_url
        else:
            print("❌ No image URL returned in response.")
            return None
    else:
        print("❌ Error generating image:", response.json())
        return None