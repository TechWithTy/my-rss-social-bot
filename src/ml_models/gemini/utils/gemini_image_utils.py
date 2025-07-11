import base64
from pathlib import Path
from typing import Dict

def create_image_part(mime_type: str, data: str) -> Dict[str, Dict[str, str]]:
    """! Creates an image part for a Gemini API request from base64 data."""
    return {"inline_data": {"mime_type": mime_type, "data": data}}

def load_image_as_base64(file_path: Path) -> str:
    """! Loads an image from a file and encodes it as a base64 string."""
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")
