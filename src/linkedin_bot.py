import requests
import time
import os
from dotenv import load_dotenv

# Read API keys from environment variables (GitHub Secrets)
load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", os.environ.get("LINKEDIN_ACCESS_TOKEN"))


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

import requests
import os
import json

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

def upload_linkedin_media(profile_id, media_url, media_type):
    """
    Uploads media (image/video) to LinkedIn and returns a media URN.
    LinkedIn requires a media upload before attaching it to a post.
    
    Returns:
        media_urn (str): The LinkedIn URN of the uploaded media.
    """
    upload_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Define the media upload request
    media_request = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],  
            "owner": f"urn:li:person:{profile_id}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    response = requests.post(upload_url, headers=headers, json=media_request)

    if response.status_code == 200:
        response_data = response.json()
        upload_urn = response_data["value"]["asset"]
        upload_endpoint = response_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]

        # Upload the actual media file
        image_response = requests.post(upload_endpoint, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, data=requests.get(media_url).content)

        if image_response.status_code == 201:
            print(f"✅ Media uploaded successfully! URN: {upload_urn}")
            return upload_urn
        else:
            print("❌ Error uploading media to LinkedIn:", image_response.json())
            return None
    else:
        print("❌ Error requesting LinkedIn upload URL:", response.json())
        return None

def post_to_linkedin(post_text, profile_id, media_url=None, media_type="NONE"):
    """
    Post to LinkedIn with optional media (image/video/article).

    Parameters:
        post_text (str): The text content of the LinkedIn post.
        profile_id (str): The LinkedIn profile ID.
        media_url (str, optional): The URL of the media (must be uploaded first).
        media_type (str, optional): The type of media ("IMAGE", "VIDEO", "ARTICLE", "NONE"). Default is "NONE".
    """

    if not profile_id:
        print("❌ Cannot post to LinkedIn: Profile ID is missing.")
        return

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Default payload without media
    data = {
        "author": f"urn:li:person:{profile_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": media_type
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    # Upload media and get URN if needed
    if media_url and media_type in ["IMAGE", "VIDEO"]:
        media_urn = upload_linkedin_media(profile_id, media_url, media_type)
        if media_urn:
            data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": media_urn
                }
            ]
        else:
            print("❌ Failed to upload media. Posting without media.")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
    else:
        print("❌ Error posting to LinkedIn:", response.json())
