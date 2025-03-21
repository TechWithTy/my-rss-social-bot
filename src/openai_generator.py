from typing import Optional, Dict, Any
import requests
import time
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID: Optional[str] = os.getenv("OPENAI_ASSISTANT_ID")


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


def send_message_to_openai(thread_id: str, blog_content: str) -> None:
    """Sends a blog post to OpenAI Assistant."""
    url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {
        "role": "user",
        "content": f"Summarize this blog post into an engaging LinkedIn post:\n\n{blog_content}"
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
