from src.linkedin_bot import get_linkedin_profile_id, post_to_linkedin
import requests
import time
import os
from dotenv import load_dotenv
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", os.environ.get("OPENAI_ASSISTANT_ID"))

# ✅ Declar

def create_openai_thread():
    """Creates an OpenAI Assistant thread"""
    url = "https://api.openai.com/v1/threads"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print("❌ Error creating OpenAI thread:", response.json())
        return None

def send_message_to_openai(thread_id, blog_content):
    """Sends a blog post to OpenAI Assistant"""
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

def run_openai_assistant(thread_id):
    """Runs the OpenAI Assistant on the thread"""
    url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    data = {"assistant_id": OPENAI_ASSISTANT_ID}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["id"]
    else:
        print("❌ Error running assistant:", response.json())
        return None

def wait_for_openai_response(thread_id, run_id):
    """Waits for OpenAI Assistant to process the request"""
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
            return None
        time.sleep(5)

def get_openai_response(thread_id):
    """Fetches the response from OpenAI Assistant"""
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
            return messages[0]["content"][0]["text"]["value"]
    print("❌ Error fetching response:", response.json())
    return None
