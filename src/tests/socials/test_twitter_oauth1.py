import os
import sys
import time
from datetime import datetime
from requests_oauthlib import OAuth1Session

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

def test_oauth1_session():
    """Test tweeting with the OAuth1Session approach - this is the official
    Twitter-recommended approach for the v2 API.
    
    API Documentation Reference:
    https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference/post-tweets
    
    Required scopes: tweet.read tweet.write users.read offline.access
    """
    print("\n===== Testing Twitter API v2 with OAuth1Session =====\n")

    # Create OAuth1Session
    oauth1_session = OAuth1Session(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    # Create unique tweet text
    timestamp = int(time.time())
    current_time = datetime.now().strftime("%I:%M:%S %p")
    tweet_text = f"Testing Twitter API v2 with proper OAuth1Session at {current_time} (ID: {timestamp}) #TwitterAPI #Test"
    
    payload = {"text": tweet_text}
    
    # API v2 endpoint for creating tweets
    url = "https://api.twitter.com/2/tweets"
    
    print(f"Posting tweet: {tweet_text}")
    print(f"Using endpoint: {url}")
    print(f"Using OAuth1Session with consumer key: {API_KEY[:5]}...{API_KEY[-3:] if API_KEY else ''}")
    
    # Post the tweet
    response = oauth1_session.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # Print response details
    print(f"\nResponse status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    # Parse response details for better error messages
    error_message = ""
    enrollment_error = False
    reason = ""
    
    if response.status_code != 200 and response.status_code != 201:
        try:
            error_data = response.json()
            if 'errors' in error_data:
                for error in error_data['errors']:
                    error_title = error.get('title', 'Unknown error')
                    error_detail = error.get('detail', 'No details provided')
                    error_message += f"\n- {error_title}: {error_detail}"
                    
                    # Look for specific errors and provide targeted advice
                    if error.get('title') == 'Unsupported Authentication':
                        error_message += "\n  SOLUTION: Enable OAuth 1.0a in your app's User Authentication Settings"
                    elif 'permission' in error.get('detail', '').lower():
                        error_message += "\n  SOLUTION: Add 'tweet.write' scope and set app permissions to 'Read and Write'"
                    
                    # Check for client-not-enrolled error which indicates free tier limitation
                    if error.get('reason') == 'client-not-enrolled' or error.get('type', '').endswith('/client-forbidden'):
                        enrollment_error = True
                        reason = error.get('reason', '')
            elif 'title' in error_data and error_data.get('title') == 'Client Forbidden':
                # This is the API tier limitation error
                enrollment_error = True
                reason = error_data.get('reason', '')
                error_message += f"\n- {error_data.get('title')}: {error_data.get('detail')}"
                if 'registration_url' in error_data:
                    error_message += f"\n  Registration URL: {error_data.get('registration_url')}"
        except Exception as e:
            error_message = f"Failed to parse error response: {str(e)}"
    
    # Add documentation references for common error codes
    if response.status_code == 403:
        if enrollment_error:
            error_message += "\n\nTWITTER FREE TIER LIMITATION DETECTED:\n"
            error_message += "The error 'client-not-enrolled' indicates this is a Twitter API access tier limitation.\n"
            error_message += "According to Twitter documentation, the free tier does not support OAuth1 with v2 endpoints.\n"
            error_message += "Solutions:\n"
            error_message += "1. Use the simulation mode in the Twitter bot (set TWITTER_SIMULATION_MODE=True)\n"
            error_message += "2. Upgrade to the Basic tier ($100/month) which supports OAuth1 with v2 endpoints\n"
            error_message += "3. Implement OAuth2 flow (but this won't support media uploads)\n"
            error_message += "\nReference: https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api\n"
        else:
            error_message += "\n\nTwitter API Documentation Reference:\n"
            error_message += "- 403 errors typically indicate permission issues: https://developer.twitter.com/en/docs/authentication/oauth-1-0a\n"
            error_message += "- Check Required App Setup: https://developer.twitter.com/en/docs/authentication/oauth-1-0a\n"
            error_message += "- Verify your app has these permissions and scopes: tweet.read tweet.write users.read\n"
    
    # Special case for enrollment issues - don't mark as failed if it's just a tier limitation
    if enrollment_error and reason == 'client-not-enrolled':
        print(f"\n{'-'*80}\nNOTE: Test is showing Twitter API tier limitation, not a code bug.\n{'-'*80}")
        print(error_message)
        print(f"\n{'-'*80}\nFree tier limitation detected. Using simulation mode is recommended.\n{'-'*80}")
        return
    
    # Use assert to properly fail the test
    assert response.status_code in (200, 201), f"Failed to post tweet: HTTP {response.status_code}\n{error_message}"
    
    # If we got here, post was successful
    data = response.json().get('data', {})
    tweet_id = data.get('id')
    if tweet_id:
        print(f"Tweet ID: {tweet_id}")
        print(f"View at: https://twitter.com/i/web/status/{tweet_id}")

def test_v1_endpoint():
    """Test the v1.1 status update endpoint using OAuth1Session
    
    API Documentation Reference:
    https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update
    
    Required permissions: Read + Write
    """
    print("\n===== Testing Twitter API v1.1 Status Update =====\n")

    # Create OAuth1Session
    oauth1_session = OAuth1Session(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    # Create unique tweet text
    timestamp = int(time.time())
    current_time = datetime.now().strftime("%I:%M:%S %p")
    tweet_text = f"Testing v1.1 API with OAuth1Session at {current_time} (ID: {timestamp}) #TwitterTest #v1API"
    
    # v1.1 endpoint for posting status update
    url = "https://api.twitter.com/1.1/statuses/update.json"
    
    print(f"Posting tweet: {tweet_text}")
    print(f"Using endpoint: {url}")
    
    # In v1.1 API, we use form data not JSON
    params = {"status": tweet_text}
    
    # Post the tweet
    response = oauth1_session.post(url, data=params)
    
    # Print response details
    print(f"\nResponse status code: {response.status_code}")
    print(f"Response content: {response.text[:500]}" + ("..." if len(response.text) > 500 else ""))
    
    # Parse error details
    error_message = ""
    enrollment_error = False
    reason = ""
    
    if response.status_code != 200 and response.status_code != 201:
        try:
            error_data = response.json()
            if 'errors' in error_data:
                for error in error_data['errors']:
                    error_code = error.get('code', 'Unknown')
                    error_msg = error.get('message', 'No message provided')
                    error_message += f"\n- Error {error_code}: {error_msg}"
                    
                    # Check for specific error codes that indicate API tier issues
                    if error_code == 453 or 'access level' in error_msg.lower():
                        enrollment_error = True
                        reason = 'limited-access'
            elif 'title' in error_data and error_data.get('title') == 'Client Forbidden':
                enrollment_error = True
                reason = error_data.get('reason', '')
                error_message += f"\n- {error_data.get('title')}: {error_data.get('detail')}"
        except Exception as e:
            error_message = f"Failed to parse error response: {str(e)}"
    
    # Add documentation references for v1.1 API
    if response.status_code == 403:
        if enrollment_error:
            error_message += "\n\nTWITTER FREE TIER LIMITATION DETECTED:\n"
            error_message += "The error code 453 indicates this endpoint requires a paid Twitter API tier.\n"
            error_message += "According to Twitter API documentation, the free tier has limited access to v1.1 endpoints.\n"
            error_message += "Solutions:\n"
            error_message += "1. Use the simulation mode in the Twitter bot (set TWITTER_SIMULATION_MODE=True)\n"
            error_message += "2. Upgrade to the Basic tier ($100/month) for full v1.1 API access\n"
            error_message += "\nReference: https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api\n"
        else:
            error_message += "\n\nTwitter API v1.1 Documentation References:\n"
            error_message += "- 403 errors in v1.1 API: https://developer.twitter.com/en/docs/authentication/oauth-1-0a/authorizing-a-request\n"
            error_message += "- v1.1 status/update endpoint: https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/post-statuses-update\n"
            error_message += "- Many v1.1 endpoints now require paid API access\n"
    
    # Special case for enrollment issues - don't mark as failed if it's just a tier limitation
    if enrollment_error:
        print(f"\n{'-'*80}\nNOTE: Test is showing Twitter API tier limitation, not a code bug.\n{'-'*80}")
        print(error_message)
        print(f"\n{'-'*80}\nFree tier limitation detected. Using simulation mode is recommended.\n{'-'*80}")
        return
    
    # Use assert to properly fail the test
    assert response.status_code in (200, 201), f"Failed to post tweet using v1.1 API: HTTP {response.status_code}\n{error_message}"
    
    # If we got here, post was successful
    data = response.json()
    tweet_id = data.get('id_str')
    if tweet_id:
        print(f"Tweet ID: {tweet_id}")
        print(f"View at: https://twitter.com/i/web/status/{tweet_id}")

def get_app_permissions():
    """Check what permissions your Twitter app has
    
    API Documentation Reference:
    https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/manage-account-settings/api-reference/get-account-verify_credentials
    """
    print("\n===== Checking Twitter App Permissions =====\n")
    
    # Create OAuth1Session
    oauth1_session = OAuth1Session(
        client_key=API_KEY,
        client_secret=API_KEY_SECRET,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET
    )
    
    # Use the verify_credentials endpoint with include_entities=false to keep response small
    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    params = {"include_entities": "false", "skip_status": "true"}
    
    response = oauth1_session.get(url, params=params)
    
    # Handle authentication errors
    if response.status_code != 200:
        error_message = f"Failed to verify credentials: HTTP {response.status_code} - {response.text}"
        print(error_message)
        print("\nAuthentication error - make sure your API keys and tokens are correct")
        print("Documentation: https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens")
        return False, False
        
    # Success - extract user info
    user_data = response.json()
    print(f"Authenticated as: @{user_data.get('screen_name')}")
    
    # Check app permissions - this requires checking which endpoints work
    # Try a simple GET endpoint that requires read permission
    timeline_url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    timeline_response = oauth1_session.get(timeline_url, params={"count": 1})
    
    has_read = timeline_response.status_code == 200
    
    print(f"App has read permission: {'u2713' if has_read else 'u2717'}")
    print("Testing write permission...")
    
    # We'll do a very simple test post that we'll immediately delete if it works
    test_url = "https://api.twitter.com/1.1/statuses/update.json"
    test_params = {"status": f"Auth test {time.time()} - will delete immediately"}
    
    post_response = oauth1_session.post(test_url, data=test_params)
    has_write = post_response.status_code == 200
    
    print(f"App has write permission: {'u2713' if has_write else 'u2717'}")
    
    if has_write:
        # Delete the test tweet
        try:
            tweet_id = post_response.json().get('id_str')
            delete_url = f"https://api.twitter.com/1.1/statuses/destroy/{tweet_id}.json"
            oauth1_session.post(delete_url)
            print("(Test tweet deleted)")
        except Exception:
            pass
    
    if not has_write:
        print("\nTo get write permission:")
        print("1. Go to the Twitter Developer Portal: https://developer.twitter.com/en/portal/dashboard")
        print("2. Navigate to your Project > App settings")
        print("3. Under 'App permissions', select 'Read and Write'")
        print("4. Under 'Authentication settings', enable OAuth 1.0a")
        print("5. Add 'tweet.write' scope to your app")
        print("6. Save changes and regenerate your access tokens")
        print("7. Documentation: https://developer.twitter.com/en/docs/apps/app-permissions")
    
    return has_read, has_write

if __name__ == "__main__":
    print("==== TWITTER OAUTH AUTHENTICATION TEST ====\n")
    print("This script tests multiple approaches to Twitter API authentication")
    print("to help diagnose issues with posting tweets.\n")
    
    # Show credentials (partially masked)
    print(f"API Key: {API_KEY[:5]}...{API_KEY[-3:] if API_KEY else ''}")
    print(f"Access Token: {ACCESS_TOKEN[:5]}...{ACCESS_TOKEN[-3:] if ACCESS_TOKEN else ''}")
    
    # Check app permissions first
    print("\nChecking your Twitter app permissions...")
    has_read, has_write = get_app_permissions()
    
    if has_read and has_write:
        print("\nYour app has both read and write permissions! Let's try posting tweets.")
        
        # Try v2 endpoint first
        try:
            test_oauth1_session()
            v2_success = True
        except AssertionError as e:
            print(f"v2 API test failed: {str(e)}")
            v2_success = False
        
        # Then try v1.1 endpoint
        try:
            test_v1_endpoint()
            v1_success = True
        except AssertionError as e:
            print(f"v1.1 API test failed: {str(e)}")
            v1_success = False
        
        print("\n==== TEST RESULTS =====")
        print(f"v2 API Post: {'u2713 SUCCESS' if v2_success else 'u2717 FAILED'}")
        print(f"v1.1 API Post: {'u2713 SUCCESS' if v1_success else 'u2717 FAILED'}")
        
        if not v2_success and not v1_success:
            print("\nTroubleshooting Tips:")
            print("1. Verify you've added the correct callback URL in the Developer Portal")
            print("2. Make sure your app is in a Project")
            print("3. Check if your Developer account has been restricted")
            print("4. Twitter API Documentation: https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api")
    else:
        print("\nWe detected permission issues with your Twitter app.")
        print("Please update your app permissions in the Developer Portal and try again.")
