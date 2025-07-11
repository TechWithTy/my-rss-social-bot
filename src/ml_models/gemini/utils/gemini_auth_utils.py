import os
from dotenv import load_dotenv
from ..exceptions import AuthenticationError

load_dotenv()

def get_gemini_api_key() -> str:
    """Retrieves the Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AuthenticationError("GEMINI_API_KEY not found in environment variables.")
    return api_key
