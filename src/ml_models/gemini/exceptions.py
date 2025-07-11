class GeminiError(Exception):
    """Base exception class for the Gemini SDK."""
    pass

class AuthenticationError(GeminiError):
    """Raised when authentication fails."""
    pass

class RateLimitError(GeminiError):
    """Raised when the API rate limit is exceeded."""
    pass

class APIError(GeminiError):
    """Raised for general API errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
