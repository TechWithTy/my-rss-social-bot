from typing import Optional, Dict, Any
import requests
import time
import os
from dotenv import load_dotenv
from src.config_loader import config
from src.utils.index import get_env_variable

# ✅ Load environment variables
load_dotenv()

env_path = ".env"

OPENAI_API_KEY: Optional[str] = get_env_variable("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID: Optional[str] = get_env_variable("OPENAI_ASSISTANT_ID")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing! Set it in your .env file or GitHub Secrets.")

def create_openai_assistant() -> str:
    """Creates a new OpenAI Assistant using YAML configuration if none exists."""
    url = "https://api.openai.com/v1/assistants"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    openai_config = config.get("user_profile", {}).get("llm", {}).get("OpenAI", {})
        
    assistant_name = openai_config.get("name", "LinkedIn Content Assistant")
    model = openai_config.get("model", "gpt-4o")
    instructions = openai_config.get("custom_system_instructions", "You are a professional copywriter...")
    temperature = openai_config.get("temperature", 1.0)
    top_p = openai_config.get("top_p", 1.0)

    data = {
        "name": assistant_name,
        "model": model,
        "instructions": instructions,
        "temperature": temperature,
        "top_p": top_p,
        "response_format": "auto"
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        assistant_id = response.json().get("id")
        print(f"✅ OpenAI Assistant created: {assistant_id} ⚠️Save this to .env or github secrets to reuse")
        return assistant_id
    else:
        print("❌ Error creating OpenAI Assistant:", response.json())
        raise RuntimeError("Failed to create OpenAI Assistant.")

# ✅ Ensure an Assistant ID exists
if not OPENAI_ASSISTANT_ID:
    print("🔹 No Assistant ID found. Creating one now...")
    OPENAI_ASSISTANT_ID = create_openai_assistant()

def create_openai_thread() -> Optional[str]:
    """Creates an OpenAI Assistant thread and returns the thread ID."""
    url = "https://api.openai.com/v1/threads"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print("❌ Error creating OpenAI thread:", response.json())
        return None

def send_message_to_openai(thread_id: str, blog_content: str, ) -> None:
    """Sends a blog post to OpenAI Assistant with instructions, creative cues, and viral preferences from config."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    # 🔧 Config sections
    openai_config = config.get("openai", {})
    user_config = config.get("user_profile", {})
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

    openai_config = config.get("ai", {})
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
    post_gif_cfg = creative.get("fetch_gif", {})

    generate_image = generate_image_cfg.get("enabled", False)
    fetch_gif = post_gif_cfg.get("enabled", False)
    image_prompt = generate_image_cfg.get("prompt", "")
    gif_prompt = post_gif_cfg.get("prompt", "")

    if generate_image and fetch_gif:
        creative_instruction = (
           f"\n\n{'Generate an AI image using prompt: (' + image_prompt + ')' if __import__('random').choice([True, False]) else 'Fetch a GIF using prompt: (' + gif_prompt + ')'} that enhances the blog content."

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
        f"{viral_examples_instruction}\n\n"
        f"Viral Methodologies To use:\n{viral_style_instructions}\n\n"
        f"{hashtag_instructions}\n\n"
        f"{creative_instruction}\n\n"
        f"{user_instructions}\n\n"
       
    )
    print('Message Content:\n\n', content)
    data = {
        "role": "user",
        "content": content,
        "attachments": [],
        "metadata": {
            "system_instructions": system_instructions
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Message sent successfully!")
    else:
        print("❌ Error sending message:", response.json())



def run_openai_assistant(thread_id: str) -> Optional[str]:
    """Runs the OpenAI Assistant and returns the run ID."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {"assistant_id": OPENAI_ASSISTANT_ID}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print("❌ Error running assistant:", response.json())
        return None


def wait_for_openai_response(thread_id: str, run_id: str) -> None:
    """Waits for OpenAI Assistant to process the request."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    while True:
        response = requests.get(url, headers=headers)
        status = response.json().get("status", "")
        if status == "completed":
            break
        elif status in ["failed", "cancelled"]:
            print("❌ Assistant failed:", response.json())
            return
        time.sleep(5)


def get_openai_response(thread_id: str) -> Optional[str]:
    """Fetches the response from OpenAI Assistant and returns the text content."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        messages = response.json().get("data", [])
        
        if messages:
            first_message = messages[0]
            content_list = first_message.get("content", [])

            if content_list and isinstance(content_list, list):
                text_content = content_list[0].get("text", {}).get("value")
                return text_content if isinstance(text_content, str) else None

    print("❌ Error fetching response:", response.json())
    return None
