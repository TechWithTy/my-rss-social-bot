import os
import json
import shutil
import requests
import tempfile
from typing import Optional, List
from requests_oauthlib import OAuth1

# Twitter API credentials from environment variables
API_KEY = os.environ.get("TWITTER_API_KEY")
API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")


def get_bearer_token() -> Optional[str]:
    """
    Get a bearer token for the Twitter API using the API key and secret.
    
    Returns:
        Optional[str]: Bearer token if successful, None otherwise
    """
    url = "https://api.twitter.com/oauth2/token"
    auth = (API_KEY, API_KEY_SECRET)
    data = {"grant_type": "client_credentials"}
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
    
    try:
        response = requests.post(url, auth=auth, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Error getting bearer token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting bearer token: {e}")
        return None


def get_user_id(username: str, bearer_token: str) -> Optional[str]:
    """
    Get the Twitter user ID for a given username.
    
    Args:
        username (str): Twitter username
        bearer_token (str): Twitter API bearer token
        
    Returns:
        Optional[str]: User ID if found, None otherwise
    """
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("data") and data["data"].get("id"):
                return data["data"]["id"]
        print(f"Error getting user ID: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Error getting user ID: {e}")
        return None


def upload_media_from_url(media_url: str) -> Optional[str]:
    """
    Download media from URL and upload to Twitter.
    
    Args:
        media_url (str): URL of the media to upload
        
    Returns:
        Optional[str]: Media ID if successful, None otherwise
    """
    # Twitter media upload endpoint
    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    
    # Create OAuth1 auth object
    auth = OAuth1(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    # Create a temporary file to store the downloaded media
    temp_file = None
    try:
        # Download the media from the URL
        response = requests.get(media_url, stream=True)
        if response.status_code != 200:
            print(f"Error downloading media: {response.status_code} - {response.text}")
            return None
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        
        # Write the content to the file
        shutil.copyfileobj(response.raw, temp_file)
        temp_file.close()
        
        # Upload the media to Twitter
        with open(temp_file.name, 'rb') as media:
            files = {'media': media}
            response = requests.post(upload_url, files=files, auth=auth)
            
            if response.status_code == 200:
                media_id = response.json().get('media_id_string')
                print(f"Media uploaded successfully. Media ID: {media_id}")
                return media_id
            else:
                print(f"Error uploading media: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None
    finally:
        # Clean up the temporary file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


def create_oauth1_auth():
    """
    Create and return an OAuth1 authentication object for Twitter API.
    
    Returns:
        OAuth1: OAuth1 authentication object
    """
    return OAuth1(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )


def post_tweet(text: str, media_ids: Optional[List[str]] = None) -> bool:
    """
    Post a tweet with optional media using Twitter API v2.
    
    Args:
        text (str): The text content of the tweet (max 280 characters)
        media_ids (Optional[List[str]]): List of media IDs to attach to the tweet
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("Missing Twitter API credentials")
        return False

    # Twitter v2 API endpoint for posting tweets
    url = "https://api.twitter.com/2/tweets"
    
    # Create OAuth1 authentication - Twitter API v2 requires OAuth 1.0a for user context
    auth = create_oauth1_auth()
    
    # Truncate text if it exceeds 280 characters
    if len(text) > 280:
        text = text[:277] + "..."
    
    # Prepare request payload according to Twitter API v2 documentation
    payload = {"text": text}
    
    # Add media if provided (only works with higher tier API access)
    if media_ids and len(media_ids) > 0:
        payload["media"] = {"media_ids": media_ids}
        print("Adding media to tweet payload")
    
    headers = {"Content-Type": "application/json"}
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth
        )
        
        # Print full response for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        if response.status_code in (200, 201):
            response_data = response.json()
            if response_data.get("data") and response_data["data"].get("id"):
                tweet_id = response_data["data"]["id"]
                print(f"✅ Tweet posted successfully! ID: {tweet_id}")
                return True
            else:
                print(f"⚠️ Unusual success response: {response_data}")
                return True  # Still return True as it was a success status code
        else:
            print(f"❌ Error posting tweet: {response.status_code} - {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except Exception as json_error:
                print(f"Failed to parse error response: {json_error}")
            return False
    except Exception as e:
        print(f"❌ Exception posting tweet: {str(e)}")
        return False


def post_to_twitter(message: str, media_url: Optional[str] = None) -> bool:
    """
    Post a message to Twitter with optional media.
    
    Args:
        message (str): The message to post
        media_url (Optional[str]): URL of media to include in the post
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # If media URL is provided, upload it first
        media_id = None
        if media_url:
            print(f"Uploading media from URL: {media_url}")
            media_id = upload_media_from_url(media_url)
            if not media_id:
                print("Failed to upload media, will post without media")
        
        # Prepare media IDs list if media was uploaded successfully
        media_ids = [media_id] if media_id else None
        
        # Post the tweet
        return post_tweet(message, media_ids)
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Post a simple text tweet
    post_to_twitter("Test tweet from the X/Twitter API!")
    
    # Post a tweet with media
    # post_to_twitter("Test tweet with an image!", "https://example.com/image.jpg")
