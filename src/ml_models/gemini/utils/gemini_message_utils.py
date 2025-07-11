from typing import List, Dict, Any

def create_text_part(text: str) -> Dict[str, str]:
    """! Creates a text part for a Gemini API request."""
    return {"text": text}

def create_content_request(parts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """! Creates a content block for a Gemini API request."""
    return [{"parts": parts}]
