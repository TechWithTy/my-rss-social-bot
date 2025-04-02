import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from socials.twitter_bot import get_oauth2_token, post_tweet_with_oauth2, post_to_twitter


class TestTwitterOAuth2Errors(unittest.TestCase):
    """Test cases for verifying Twitter OAuth2 error handling and failure modes."""
    
    @patch('socials.twitter_bot.requests.post')
    def test_oauth2_token_failure(self, mock_post):
        """Test that get_oauth2_token fails properly with invalid credentials."""
        # Mock the response for an authentication failure
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'error': 'invalid_client',
            'error_description': 'Invalid client credentials'
        }
        mock_response.text = 'Invalid client credentials'
        mock_post.return_value = mock_response
        
        # Set environment variables for testing
        with patch.dict(os.environ, {
            'TWITTER_CLIENT_ID': 'invalid_client_id',
            'TWITTER_CLIENT_SECRET': 'invalid_client_secret',
            'TWITTER_SIMULATION_MODE': 'False'
        }):
            # Call the function and verify it fails as expected
            token = get_oauth2_token()
            # This should fail with a clear error message
            self.assertIsNone(token, 'Token should be None when authentication fails')
            
            # Force a failure with a message when we get an OAuth2 error
            if token is None:
                print("\n\n🔴 OAUTH2 AUTHENTICATION ERROR: Could not obtain token with invalid credentials")
                print("This is expected behavior in Twitter's free tier with invalid credentials")
                print("In a real application, this should be handled gracefully")
                # Uncomment below to make the test actually fail
                # self.fail("OAuth2 authentication failed as expected")
    
    @patch('socials.twitter_bot.get_oauth2_token')
    @patch('socials.twitter_bot.requests.post')
    def test_post_tweet_with_invalid_oauth2_token(self, mock_post, mock_get_token):
        """Test posting a tweet with an invalid OAuth2 token."""
        # Mock OAuth2 token retrieval to succeed but API call to fail
        mock_get_token.return_value = 'fake_invalid_token'
        
        # Mock the API response for an unauthorized request
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'errors': [{
                'message': 'Unauthorized',
                'code': 32
            }]
        }
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        # Set environment variables for testing
        with patch.dict(os.environ, {
            'TWITTER_SIMULATION_MODE': 'False'
        }):
            # Call the function and verify it fails as expected
            result = post_tweet_with_oauth2('Test tweet with invalid token')
            self.assertFalse(result, 'Posting should fail with invalid token')
            
            # Force a failure with a message to show the actual error
            if not result:
                print("\n\n🔴 OAUTH2 POSTING ERROR: Failed to post tweet with invalid token")
                print("This is expected behavior in Twitter's free tier with invalid tokens")
                print("The error should be properly handled in the application code")
                # Uncomment below to make the test actually fail
                # self.fail("Posting with OAuth2 failed as expected")
    
    @patch('socials.twitter_bot.get_oauth2_token')
    @patch('socials.twitter_bot.post_tweet')  # Mock the fallback method
    def test_post_to_twitter_fallback_on_oauth2_failure(self, mock_post_tweet, mock_get_token):
        """Test that post_to_twitter falls back to OAuth1 when OAuth2 fails."""
        # Mock OAuth2 token retrieval to fail
        mock_get_token.return_value = None
        
        # Mock OAuth1 posting to succeed
        mock_post_tweet.return_value = True
        
        # Set environment variables for testing
        with patch.dict(os.environ, {
            'TWITTER_USE_FREE_TIER': 'True',
            'TWITTER_SIMULATION_MODE': 'False'
        }):
            # Call the function and verify it falls back successfully
            result = post_to_twitter('Test fallback to OAuth1')
            
            # Verify OAuth1 was called as a fallback
            mock_post_tweet.assert_called_once()
            self.assertTrue(result, 'Posting should succeed with fallback')
            
            # Show the fallback process explicitly
            print("\n\n🟡 OAUTH2 FALLBACK: Successfully fell back to OAuth1 when OAuth2 failed")
            print("This demonstrates the correct fallback behavior in the application")
    
    @patch('socials.twitter_bot.requests.post')
    def test_free_tier_permissions_error_failure(self, mock_post):
        """Test that demonstrates a Twitter API free tier limitation failure."""
        # First mock call for OAuth2 token
        mock_token_response = MagicMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {'access_token': 'fake_token'}
        
        # Second mock call for tweet posting - free tier limitation
        mock_tweet_response = MagicMock()
        mock_tweet_response.status_code = 403
        mock_tweet_response.json.return_value = {
            'errors': [{
                'message': 'client-not-enrolled',
                'code': 32
            }]
        }
        mock_tweet_response.text = 'client-not-enrolled'  
        
        # Configure the mock to return different responses for different calls
        mock_post.side_effect = [mock_token_response, mock_tweet_response]
        
        # Set environment variables for testing
        with patch.dict(os.environ, {
            'TWITTER_CLIENT_ID': 'test_client_id',
            'TWITTER_CLIENT_SECRET': 'test_client_secret',
            'TWITTER_USE_FREE_TIER': 'True',
            'TWITTER_SIMULATION_MODE': 'False'
        }):
            # This should fail with a clear error about free tier limitations
            tweet_text = "Test tweet showing free tier API limitations"
            success = post_tweet_with_oauth2(tweet_text)
            
            # The function should return False, but we want to show a clear failure
            self.assertFalse(success, "Expected posting to fail due to free tier limitations")
            
            # Force the test to fail with a clear error message
            print("\n\n🔴 FREE TIER API LIMITATION: Cannot post tweet with OAuth2 on the free tier")
            print("The 'client-not-enrolled' error indicates you need to upgrade to a paid API tier")
            print("This test is explicitly failing to highlight this limitation")
            self.fail("Twitter API free tier limitation prevented tweet posting")


if __name__ == '__main__':
    unittest.main()
