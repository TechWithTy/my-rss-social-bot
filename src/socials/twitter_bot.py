import os
import json
import shutil
import requests
import base64
import tempfile
from typing import Optional, List, Dict, Any
from requests_oauthlib import OAuth1
from urllib.parse import urlencode

# Twitter API credentials from environment variables
API_KEY = os.environ.get("TWITTER_API_KEY")
API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("TWITTER_REDIRECT_URI", "https://localhost:3000/callback")
SIMULATION_MODE = os.environ.get("TWITTER_SIMULATION_MODE", "False").lower() == "true"
USE_FREE_TIER = os.environ.get("TWITTER_USE_FREE_TIER", "True").lower() == "true"
VERBOSE_MODE = os.environ.get("TWITTER_VERBOSE_MODE", "False").lower() == "true"


def get_oauth2_token() -> Optional[str]:
    """
    Get an OAuth 2.0 token using client ID and secret with the client credentials flow.
    This is the recommended method for Twitter API v2 access on the free tier.
    
    Returns:
        Optional[str]: OAuth 2.0 token if successful, None otherwise
    """
    if SIMULATION_MODE:
        print("Running in simulation mode, returning fake OAuth2 token")
        return "SIMULATED_OAUTH2_TOKEN"
        
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing Twitter Client ID or Client Secret")
        print("\u274c ERROR: Cannot get OAuth2 token without proper credentials")
        print("Make sure TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET are set in your .env file")
        return None
        
    url = "https://api.twitter.com/2/oauth2/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # For the free tier, we must use client_credentials grant type
    # This provides an app-only token with limited scopes but works without user login
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            print("Successfully obtained OAuth2 token for Twitter API")
            return access_token
        else:
            # Explicitly fail with a clear error message when we get authentication issues
            print(f"\u274c ERROR: Failed to obtain OAuth2 token. Status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Twitter API error: {error_data}")
                
                # Check for specific errors and provide helpful messages
                if "invalid_client" in response.text:
                    print("Invalid client credentials - check your CLIENT_ID and CLIENT_SECRET")
                elif "unauthorized_client" in response.text:
                    print("Client not authorized - verify your app has proper permissions")
                
                # Handle free tier limitations
                if response.status_code == 403 or response.status_code == 401:
                    print("\n\u26a0\ufe0f FREE TIER LIMITATION DETECTED:\n")
                    print("Twitter's free tier has limited OAuth2 capabilities.")
                    print("You might need to:")
                    print("1. Upgrade to a paid tier for full API access")
                    print("2. Use TWITTER_SIMULATION_MODE=True for testing")
                    print("3. Check that your app has the correct permissions in the Twitter Developer Portal")
            except Exception:
                print(f"Response text: {response.text}")
            return None
    except Exception as e:
        print(f"\u274c ERROR: Error getting OAuth2 token: {e}")
        return None


def initiate_oauth2_flow() -> str:
    """
    Initiate the OAuth 2.0 authorization flow for Twitter.
    This generates the authorization URL that the user must visit to grant permission.
    
    Returns:
        str: The authorization URL for the user to visit
    """
    if not CLIENT_ID or not REDIRECT_URI:
        raise ValueError("Missing CLIENT_ID or REDIRECT_URI environment variables")
    
    # Twitter OAuth2 authorization URL
    auth_url = "https://twitter.com/i/oauth2/authorize"
    
    # Required scopes for tweeting
    # tweet.read and tweet.write are needed for posting tweets
    # offline.access is needed to get a refresh token
    scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]
    
    # Parameters for the authorization request
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": "state",  # You should generate a random state value for security
        "code_challenge": "challenge",  # For PKCE, should be derived from code_verifier
        "code_challenge_method": "plain"  # Should be S256 in production
    }
    
    # Construct the full authorization URL
    authorization_url = f"{auth_url}?{urlencode(params)}"
    
    print("\nAuthorization URL:")
    print(authorization_url)
    print("\nPlease visit this URL to authorize the application.")
    print("After authorization, you will be redirected to your redirect URI with a code parameter.")
    
    return authorization_url


def exchange_code_for_token(code: str, code_verifier: str = "challenge") -> Dict[str, Any]:
    """
    Exchange the authorization code for an access token.
    
    Args:
        code (str): The authorization code received from the callback
        code_verifier (str): The code verifier used in the PKCE flow
        
    Returns:
        Dict[str, Any]: The token response containing access_token, refresh_token, etc.
    """
    if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
        raise ValueError("Missing required environment variables for token exchange")
    
    # Twitter token endpoint
    token_url = "https://api.twitter.com/2/oauth2/token"
    
    # Prepare the request payload
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }
    
    # Basic authentication with client_id and client_secret
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(token_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            print("Successfully obtained OAuth2 tokens")
            
            # Save tokens securely (in a real application)
            # This is just a placeholder - you should store these securely
            oauth2_tokens = {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data.get("expires_in"),
                "scope": token_data.get("scope")
            }
            
            return oauth2_tokens
        else:
            print(f"Error exchanging code for token: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        print(f"Exception during token exchange: {e}")
        return {}


def get_bearer_token() -> Optional[str]:
    """
    Get a bearer token for the Twitter API using the API key and secret.
    If BEARER_TOKEN is provided in environment variables, use that instead.
    
    Returns:
        Optional[str]: Bearer token if successful, None otherwise
    """
    # If bearer token is provided directly, use it
    if BEARER_TOKEN:
        return BEARER_TOKEN
        
    # Otherwise, try to get a bearer token using API key and secret
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
    Note: This requires a paid Twitter API subscription to work.
    
    Args:
        media_url (str): URL of the media to upload
        
    Returns:
        Optional[str]: Media ID if successful, None otherwise
    """
    print("\u26a0ufe0f Note: Media uploads require Twitter API paid tier access")
    
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


def post_tweet_with_bearer(text: str, media_ids: Optional[List[str]] = None) -> bool:
    """
    Post a tweet using Twitter API v2 with bearer token authentication.
    This endpoint is available in the free tier of the Twitter API.
    
    Args:
        text (str): The text content of the tweet (max 280 characters)
        media_ids (Optional[List[str]]): List of media IDs to attach to the tweet
        
    Returns:
        bool: True if successful, False otherwise
    """
    if SIMULATION_MODE:
        print("\n==== SIMULATION MODE: Tweet would be posted with Bearer Token ====")
        print(f"Tweet text: {text}")
        if media_ids:
            print(f"Media IDs: {media_ids}")
        print("Note: No actual API call was made (SIMULATION_MODE=True)")
        return True
        
    # Get bearer token
    bearer_token = get_bearer_token() or get_oauth2_token()
    if not bearer_token:
        print("\u274c Missing Twitter Bearer Token or unable to obtain one")
        return False

    # Twitter v2 API endpoint for posting tweets
    url = "https://api.twitter.com/2/tweets"
    
    # Truncate text if it exceeds 280 characters
    if len(text) > 280:
        text = text[:277] + "..."
    
    # Prepare request payload according to Twitter API v2 documentation
    payload = {"text": text}
    
    # Add media if provided (note: this might not work with free tier API)
    if media_ids and len(media_ids) > 0:
        print("\u26a0ufe0f Note: Media attachments may not work on free tier Twitter API")
        payload["media"] = {"media_ids": media_ids}
        print(f"Adding media to tweet payload: {media_ids}")
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    print(f"Posting tweet with bearer token: {text}")
    print(f"Full payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {headers}")
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=payload,
            headers=headers
        )
        
        # Print response status for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code in (200, 201):
            response_data = response.json()
            if response_data.get("data") and response_data["data"].get("id"):
                tweet_id = response_data["data"]["id"]
                print(f"\u2705 Tweet posted successfully! ID: {tweet_id}")
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                print(f"You can view the tweet at: {tweet_url}")
                return True
            else:
                print(f"\u26a0ufe0f Unusual success response: {response_data}")
                return True  # Still return True as it was a success status code
        else:
            print(f"\u274c Error posting tweet: {response.status_code} - {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
                
                # Check for specific errors and provide helpful messages
                if "client credentials" in response.text.lower() or "bearer token" in response.text.lower():
                    print("\u26a0ufe0f This endpoint may require OAuth 1.0a authentication instead of bearer token.")
                    print("Trying alternative authentication method...")
                    return post_tweet(text, media_ids)
                        
            except Exception as json_error:
                print(f"Failed to parse error response: {json_error}")
            return False
    except Exception as e:
        print(f"\u274c Exception posting tweet: {str(e)}")
        return False


def post_tweet(text: str, media_ids: Optional[List[str]] = None) -> bool:
    """
    Post a tweet using Twitter API v2 with OAuth 1.0a authentication.
    This endpoint is available in the free tier of the Twitter API.
    
    Args:
        text (str): The text content of the tweet (max 280 characters)
        media_ids (Optional[List[str]]): List of media IDs to attach to the tweet
        
    Returns:
        bool: True if successful, False otherwise
    """
    if SIMULATION_MODE:
        print("\n==== SIMULATION MODE: Tweet would be posted with OAuth1 ====")
        print(f"Tweet text: {text}")
        if media_ids:
            print(f"Media IDs: {media_ids}")
        print("Note: No actual API call was made (SIMULATION_MODE=True)")
        return True
        
    # Validate API credentials
    if not all([API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        print("\u274c Missing Twitter API credentials")
        return False

    # Twitter v2 API endpoint for posting tweets
    url = "https://api.twitter.com/2/tweets"
    
    # Create OAuth1 authentication for user context
    auth = create_oauth1_auth()
    
    # Truncate text if it exceeds 280 characters
    if len(text) > 280:
        text = text[:277] + "..."
    
    # Add a hashtag to make the test tweet more visible
    if "test" in text.lower() and "#test" not in text.lower():
        text = f"{text} #TestTweet"
    
    # Prepare request payload according to Twitter API v2 documentation
    payload = {"text": text}
    
    # Add media if provided (note: this might not work with free tier API)
    if media_ids and len(media_ids) > 0:
        print("\u26a0ufe0f Note: Media attachments may not work on free tier Twitter API")
        payload["media"] = {"media_ids": media_ids}
        print(f"Adding media to tweet payload: {media_ids}")
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Posting tweet with OAuth 1.0a: {text}")
    print(f"Full payload: {json.dumps(payload, indent=2)}")
    print(f"Using OAuth1 authentication with key: {API_KEY[:5]}...")
    
    try:
        # Make the request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth
        )
        
        # Print response status for debugging
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code in (200, 201):
            response_data = response.json()
            if response_data.get("data") and response_data["data"].get("id"):
                tweet_id = response_data["data"]["id"]
                print(f"\u2705 Tweet posted successfully! ID: {tweet_id}")
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                print(f"You can view the tweet at: {tweet_url}")
                return True
            else:
                print(f"\u26a0ufe0f Unusual success response: {response_data}")
                return True  # Still return True as it was a success status code
        else:
            print(f"\u274c Error posting tweet: {response.status_code} - {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
                
                # Check for specific errors and provide helpful messages
                errors = error_data.get("errors", [])
                for error in errors:
                    error_msg = error.get("message", "").lower()
                    if "media_id" in error_msg:
                        print("\u26a0ufe0f Media ID error detected. This requires Twitter API paid tier.")
                    elif "duplicate content" in error_msg:
                        print("\u26a0ufe0f Duplicate content error. Twitter doesn't allow identical tweets.")
                    elif "access to a subset" in error_msg:
                        print("\u26a0ufe0f API access level error. Free tier limits which endpoints you can access.")
                    elif "oauth1 app permissions" in error_msg:
                        print("\u26a0ufe0f Your Twitter App needs 'Read and Write' permissions.")
                        print("Please update your app permissions in the Twitter Developer Portal.")
                        
            except Exception as json_error:
                print(f"Failed to parse error response: {json_error}")
            return False
    except Exception as e:
        print(f"\u274c Exception posting tweet: {str(e)}")
        return False


def post_tweet_with_oauth2(text: str, media_ids: Optional[List[str]] = None, oauth2_token: Optional[str] = None) -> bool:
    """
    Post a tweet using Twitter API v2 with OAuth 2.0 authentication.
    This is supported on the free tier of the Twitter API, but with limitations.
    
    Args:
        text (str): The text content of the tweet (max 280 characters)
        media_ids (Optional[List[str]]): List of media IDs to attach to the tweet
        oauth2_token (Optional[str]): OAuth2 token to use, if not provided will get a new one
        
    Returns:
        bool: True if successful, False otherwise
    """
    if SIMULATION_MODE:
        print("\n==== SIMULATION MODE: Tweet would be posted with OAuth2 ====")
        print(f"Tweet text: {text}")
        if media_ids:
            print(f"Media IDs: {media_ids}")
        print("Note: No actual API call was made (SIMULATION_MODE=True)")
        return True
    
    # Get or use provided OAuth2 token
    token = oauth2_token or get_oauth2_token()
    if not token:
        print("\n\u274c AUTHENTICATION ERROR: Failed to obtain OAuth2 token")
        print("Twitter's free tier requires valid OAuth2 credentials.")
        print("Make sure TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET are set correctly.")
        return False
    
    # Twitter v2 API endpoint for posting tweets
    url = "https://api.twitter.com/2/tweets"
    
    # Truncate text if it exceeds 280 characters
    if len(text) > 280:
        text = text[:277] + "..."
    
    # Prepare request payload according to Twitter API v2 documentation
    payload = {"text": text}
    
    # Media attachments are not supported with the free tier OAuth2 token
    # Include them in the payload but warn that they likely won't work
    if media_ids and len(media_ids) > 0:
        print("\u26a0\ufe0f Warning: Media attachments are not supported with OAuth2 on free tier")
        print("Media uploads require OAuth1 authentication and a paid Twitter API tier")
        # Still include them in case the user has the appropriate tier
        payload["media"] = {"media_ids": media_ids}
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Posting tweet with OAuth2: {text}")
    
    try:
        # Make the request
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response status for debugging
        print(f"Response status: {response.status_code}")
        
        if response.status_code in (200, 201):
            response_data = response.json()
            if response_data.get("data") and response_data["data"].get("id"):
                tweet_id = response_data["data"]["id"]
                print(f"\u2705 Tweet posted successfully! ID: {tweet_id}")
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                print(f"You can view the tweet at: {tweet_url}")
                return True
            else:
                print(f"\u26a0\ufe0f Unusual success response: {response_data}")
                return True  # Still return True as it was a success status code
        else:
            print(f"\n\u274c ERROR: Failed to post tweet with OAuth2. Status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
                
                # Better error handling for specific cases
                if response.status_code == 401:
                    print("\n\u274c AUTHENTICATION ERROR: OAuth2 token invalid or expired")
                    print("This usually means your credentials are incorrect or expired.")
                    print("Check your TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET.")
                    return False
                    
                elif response.status_code == 403:
                    print("\n\u274c PERMISSIONS ERROR: Forbidden action")
                    print("This usually means your app doesn't have permission to post tweets.")
                    print("Check that your app has the 'tweet.write' scope in the Twitter Developer Portal.")
                    
                    # Check for specific errors in the response
                    if "client-not-enrolled" in str(error_data) or "client-forbidden" in str(error_data):
                        print("\n\u26a0\ufe0f FREE TIER LIMITATION DETECTED")
                        print("The error 'client-not-enrolled' or 'client-forbidden' indicates this is a")
                        print("Twitter API access tier limitation. The free tier has limited capabilities.")
                        print("Options:")
                        print("1. Use TWITTER_SIMULATION_MODE=True for testing")
                        print("2. Upgrade to a paid tier for full API access")
                    return False
                
                # Generic error messages based on response content    
                if "Unauthorized" in str(error_data) or "invalid token" in str(error_data).lower():
                    print("\u26a0\ufe0f OAuth2 token invalid or expired. Try refreshing the token.")
                elif "permission" in str(error_data).lower():
                    print("\u26a0\ufe0f The OAuth2 token doesn't have the required permissions.")
                    print("Make sure your app has 'tweet.write' scope.")
                elif "rate limit" in str(error_data).lower():
                    print("\u26a0\ufe0f Rate limit exceeded. Twitter's free tier has strict rate limits.")
                    print("Try again later or upgrade to a paid tier.")
            except Exception as json_error:
                print(f"Failed to parse error response: {json_error}")
                print(f"Raw response: {response.text}")
            return False
    except Exception as e:
        print(f"\n\u274c EXCEPTION: Error posting tweet with OAuth2: {str(e)}")
        return False


def post_to_twitter(message: str, media_url: Optional[str] = None) -> bool:
    """
    Post a message to Twitter with optional media.
    For free tier access, tries OAuth2 first, then falls back to other methods.
    
    Args:
        message (str): The message to post
        media_url (Optional[str]): URL of media to include in the post
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        media_ids = None
        
        # Check if we should try to upload media (media uploads might not work in free tier)
        if media_url and not USE_FREE_TIER:  # Skip media upload if using free tier
            print(f"\nAttempting to upload media from URL: {media_url}")
            media_id = upload_media_from_url(media_url)
            if media_id:
                media_ids = [media_id]
                print(f"Media uploaded successfully with ID: {media_id}")
            else:
                print("\u26a0\ufe0f Failed to upload media, continuing with text-only tweet")
        elif media_url and USE_FREE_TIER:
            print("\u26a0\ufe0f Media uploads are not supported on the free Twitter API tier")
            print("Set TWITTER_USE_FREE_TIER=False to attempt media uploads (requires paid tier)")
        
        # Try posting with OAuth2 first (recommended for free tier)
        if USE_FREE_TIER:
            print("\n==== Attempting to post with OAuth2 (preferred for free tier) ====")
            # Get token and post tweet
            oauth2_token = get_oauth2_token()
            if not oauth2_token:
                print("\n\u274c OAuth2 authentication failed")
                print("This is likely due to invalid credentials or Twitter API limitations.")
                print("Check that TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET are set correctly.")
                
                # Fall back to other methods if OAuth2 fails
                print("\n\u26a0\ufe0f Trying alternative authentication methods...")
                success = post_tweet(message, media_ids)
                if not success:
                    print("\n\u274c All posting attempts failed")
                    print("If you're using the free tier, you may be encountering Twitter API limitations.")
                    print("Consider enabling simulation mode with TWITTER_SIMULATION_MODE=True for testing.")
                return success
            
            # We have a token, try to post
            success = post_tweet_with_oauth2(message, media_ids, oauth2_token)
            if success:
                return True
            else:
                print("\n\u274c OAuth2 posting failed, trying alternative methods...")
                # Only fall back if OAuth2 failed for reasons other than obvious auth errors
                return post_tweet(message, media_ids)
        else:
            # Use standard methods if not explicitly using free tier
            print("\n==== Attempting to post with OAuth1 ====")
            success = post_tweet(message, media_ids)
            if not success:
                print("\n\u274c OAuth1 posting failed, trying OAuth2...")
                return post_tweet_with_oauth2(message, media_ids)
            return success
            
    except Exception as e:
        print(f"\n\u274c ERROR: Exception when posting to Twitter: {str(e)}")
        # If we're in development/debug mode, print full stack trace
        if 'VERBOSE_MODE' in globals() and VERBOSE_MODE:
            import traceback
            traceback.print_exc()
        return False


# Example usage
if __name__ == "__main__":
    # Post a simple text tweet - this should work with free tier
    post_to_twitter("Test tweet from the X/Twitter API - text only!")
    
    # Post a tweet with media - this may require paid tier access
    # post_to_twitter("Test tweet with an image!", "https://example.com/image.jpg")
