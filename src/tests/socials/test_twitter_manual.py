import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv
from socials.twitter_bot import post_tweet, post_to_twitter

# Load environment variables
load_dotenv()

# Generate a unique hashtag to avoid duplicate tweets
unique_id = os.urandom(4).hex()

# Test posting a simple text-only tweet
def test_text_only_tweet():
    print("\nTesting text-only tweet...")
    message = f"This is a test tweet for the RSS-to-Social Bot. Please ignore. #{unique_id}"
    success = post_tweet(message)
    print(f"Tweet posted successfully: {success}")
    return success

# Test posting a tweet with a simple placeholder image
def test_tweet_with_media():
    print("\nTesting tweet with media...")
    message = f"This is a test tweet with media for the RSS-to-Social Bot. Please ignore. #{unique_id}"
    media_url = "https://placehold.co/600x400/png"
    success = post_to_twitter(message, media_url)
    print(f"Tweet with media posted successfully: {success}")
    return success

if __name__ == "__main__":
    print("\n=== Twitter Manual Testing ===\n")
    print("Note: Free tier API access may restrict some functionality")
    print("Twitter API credentials:")
    print(f"API Key: {'✓ Set' if os.environ.get('TWITTER_API_KEY') else '✗ Missing'}")
    print(f"API Secret: {'✓ Set' if os.environ.get('TWITTER_API_KEY_SECRET') else '✗ Missing'}")
    print(f"Access Token: {'✓ Set' if os.environ.get('TWITTER_ACCESS_TOKEN') else '✗ Missing'}")
    print(f"Access Token Secret: {'✓ Set' if os.environ.get('TWITTER_ACCESS_TOKEN_SECRET') else '✗ Missing'}")
    
    # Run tests
    text_success = test_text_only_tweet()
    media_success = test_tweet_with_media()
    
    # Summary
    print("\n=== Test Results ===")
    print(f"Text-only tweet: {'✓ Success' if text_success else '✗ Failed'}")
    print(f"Tweet with media: {'✓ Success' if media_success else '✗ Failed'}")
    
    if text_success and not media_success:
        print("\nNote: Media upload may be restricted on free tier Twitter API.")
        print("Text-only tweets are working correctly!")
    elif not text_success:
        print("\nError: Text-only tweets failed. Check your API credentials and permissions.")
    else:
        print("\nAll tests passed successfully!")
