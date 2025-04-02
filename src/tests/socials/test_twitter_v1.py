import os
import sys
import time
import requests
from requests_oauthlib import OAuth1

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Twitter API credentials
API_KEY = os.environ.get("TWITTER_API_KEY")
API_KEY_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

def test_post_v1_api():
    """Test posting using the v1.1 API endpoint
    This sometimes works better with the free tier API access
    """
    print("\n===== Testing Twitter v1.1 API =====\n")
    
    # Use the old v1.1 API endpoint for statuses/update
    url = "https://api.twitter.com/1.1/statuses/update.json"
    
    # Create unique tweet text
    timestamp = int(time.time())
    tweet_text = f"Testing v1.1 API endpoint at {timestamp} #TwitterTest"
    
    # Set up authentication
    auth = OAuth1(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    # Create payload (v1.1 API uses form data, not JSON)
    payload = {"status": tweet_text}
    
    print(f"Posting tweet: {tweet_text}")
    print(f"Using v1.1 API endpoint: {url}")
    
    # Send request
    response = requests.post(url, data=payload, auth=auth)
    
    # Print response details
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text[:500]}" + ("..." if len(response.text) > 500 else ""))
    
    if response.status_code in (200, 201):
        print("\nSUCCESS! Tweet posted successfully using v1.1 API.")
        try:
            data = response.json()
            tweet_id = data.get('id_str')
            if tweet_id:
                print(f"Tweet ID: {tweet_id}")
                print(f"View at: https://twitter.com/i/web/status/{tweet_id}")
        except Exception as e:
            print(f"Couldn't parse tweet ID: {e}")
        return True
    else:
        print("\nFAILED to post tweet using v1.1 API.")
        print("This could be due to:")
        print("1. Free tier API limitations (many v1.1 endpoints require paid access)")
        print("2. Incorrect API keys or access tokens")
        print("3. App permission issues")
        print("\nPlease check the Twitter Developer Portal to ensure you have the correct:")
        print("- App permissions (should be 'Read and Write')")
        print("- API access level (Basic, Elevated, or Enterprise)")
        return False

def test_verify_credentials():
    """Test verifying your Twitter credentials
    This can help identify permission issues
    """
    print("\n===== Testing Twitter Credentials =====\n")
    
    # Use the verify_credentials endpoint to check auth and permissions
    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    
    # Set up authentication
    auth = OAuth1(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    print(f"Checking credentials using endpoint: {url}")
    
    # Send request
    response = requests.get(url, auth=auth)
    
    # Print response details
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        print("\nSUCCESS! Your Twitter credentials are valid.")
        try:
            data = response.json()
            screen_name = data.get('screen_name')
            user_id = data.get('id_str')
            if screen_name:
                print(f"Authenticated as: @{screen_name} (ID: {user_id})")
            # Check if the user has write access
            if 'status' in data:
                print("Your account has posting capabilities.")
            else:
                print("INFO: Couldn't detect posting capabilities from verify_credentials response.")
        except Exception as e:
            print(f"Couldn't parse user data: {e}")
        return True
    else:
        print("\nFAILED to verify Twitter credentials.")
        print("Response content:", response.text[:300] + ("..." if len(response.text) > 300 else ""))
        return False

if __name__ == "__main__":
    print("==== TWITTER API V1.1 TEST ====\n")
    print("This script tests Twitter API with v1.1 endpoints, which sometimes")
    print("work better with free tier access than the v2 endpoints.\n")
    
    # Show credentials (partially masked)
    print(f"API Key: {API_KEY[:5]}...{API_KEY[-3:] if API_KEY else ''}")
    print(f"Access Token: {ACCESS_TOKEN[:5]}...{ACCESS_TOKEN[-3:] if ACCESS_TOKEN else ''}\n")
    
    # Verify credentials first
    verify_success = test_verify_credentials()
    
    # Only try posting if verification succeeded
    if verify_success:
        post_success = test_post_v1_api()
        print(f"\nPost tweet result: {'SUCCESS' if post_success else 'FAILED'}")
    else:
        print("\nSkipping tweet post test due to credential verification failure.")
    
    print("\n==== TEST COMPLETE ====\n")
    if not verify_success:
        print("NOTE: If you've just regenerated your API keys and tokens, try waiting")
        print("a few minutes before testing again, as changes may take time to propagate.")
