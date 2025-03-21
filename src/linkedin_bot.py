import requests
import time
import os
from dotenv import load_dotenv

# Read API keys from environment variables (GitHub Secrets)
load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", os.environ.get("LINKEDIN_ACCESS_TOKEN"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY"))
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", os.environ.get("OPENAI_ASSISTANT_ID"))

# ✅ Declare `profile_id` globally at the start
profile_id = None  

def get_linkedin_profile_id():
    """Fetch and return LinkedIn Profile ID"""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile_id = response.json().get("sub")
        print(f"✅ LinkedIn Profile ID Retrieved: {profile_id}")
        return profile_id
    else:
        print("❌ Error fetching LinkedIn profile ID:", response.json())
        return None

def post_to_linkedin(post_text,profile_id):
    """Post to LinkedIn using the global profile_id"""

    if not profile_id:
        print("❌ Cannot post to LinkedIn: Profile ID is missing.")
        return

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    data = {
        "author": f"urn:li:person:{profile_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
    else:
        print("❌ Error posting to LinkedIn:", response.json())
