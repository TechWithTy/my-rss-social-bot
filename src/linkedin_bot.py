from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

ACCESS_TOKEN: Optional[str] = os.getenv("LINKEDIN_ACCESS_TOKEN")


def get_linkedin_profile_id() -> Optional[str]:
    """
    Fetch and return LinkedIn Profile ID.

    Returns:
        Optional[str]: The LinkedIn Profile ID, or None if an error occurs.
    """
    if not ACCESS_TOKEN:
        print("❌ Error: Missing LinkedIn access token.")
        return None

    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile_id = response.json().get("sub")
        if isinstance(profile_id, str):
            print(f"✅ LinkedIn Profile ID Retrieved: {profile_id}")
            return profile_id
    print("❌ Error fetching LinkedIn profile ID:", response.json())
    return None


def upload_linkedin_media(profile_id: str, media_url: str, media_type: str) -> Optional[str]:
    """
    Uploads media (image, GIF, or video) to LinkedIn and returns a media URN.

    Args:
        profile_id (str): LinkedIn Profile ID
        media_url (str): The direct URL of the media file
        media_type (str): "IMAGE", "GIF", or "VIDEO"

    Returns:
        Optional[str]: The LinkedIn media URN if successful, else None.
    """
    if not ACCESS_TOKEN:
        print("❌ Error: Missing LinkedIn access token.")
        return None

    upload_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # ✅ Validate media type
    recipe_map: Dict[str, str] = {
        "IMAGE": "urn:li:digitalmediaRecipe:feedshare-image",
        "GIF": "urn:li:digitalmediaRecipe:feedshare-image",  # GIFs are treated as images
        "VIDEO": "urn:li:digitalmediaRecipe:feedshare-video"
    }
    
    if media_type not in recipe_map:
        print("❌ Invalid media type. Choose IMAGE, GIF, or VIDEO.")
        return None

    media_request = {
        "registerUploadRequest": {
            "recipes": [recipe_map[media_type]],
            "owner": f"urn:li:person:{profile_id}",
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    }

    response = requests.post(upload_url, headers=headers, json=media_request)
    if response.status_code == 200:
        response_data = response.json()
        upload_urn = response_data["value"]["asset"]
        upload_endpoint = response_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]

        # ✅ Upload the actual media file
        media_response = requests.post(upload_endpoint, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, data=requests.get(media_url).content)

        if media_response.status_code == 201:
            print(f"✅ {media_type} uploaded successfully! URN: {upload_urn}")
            return upload_urn

        print(f"❌ Error uploading {media_type} to LinkedIn:", media_response.json())
        return None

    print("❌ Error requesting LinkedIn upload URL:", response.json())
    return None


def post_to_linkedin(post_text: str, profile_id: str, media_url: Optional[str] = None, media_type: str = "NONE") -> None:
    """
    Post to LinkedIn with optional media (image, GIF, or video).

    Args:
        post_text (str): The text content of the LinkedIn post.
        profile_id (str): The LinkedIn profile ID.
        media_url (Optional[str], optional): The URL of the media. Defaults to None.
        media_type (str, optional): The type of media ("IMAGE", "GIF", "VIDEO", "ARTICLE", "NONE"). Defaults to "NONE".
    """
    if not ACCESS_TOKEN:
        print("❌ Error: Missing LinkedIn access token.")
        return

    if not profile_id:
        print("❌ Cannot post to LinkedIn: Profile ID is missing.")
        return

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # ✅ Default payload without media
    data: Dict[str, Any] = {
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

    # ✅ Upload media and get URN if needed
    if media_url and media_type in ["IMAGE", "GIF", "VIDEO"]:
        media_urn = upload_linkedin_media(profile_id, media_url, media_type)
        if media_urn:
            data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{"status": "READY", "media": media_urn}]
            data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE" if media_type in ["IMAGE", "GIF"] else "VIDEO"
        else:
            print("❌ Failed to upload media. Posting without media.")

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
    else:
        print("❌ Error posting to LinkedIn:", response.json())
