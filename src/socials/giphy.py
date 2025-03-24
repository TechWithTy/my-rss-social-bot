

import sys
import os

# Add src to PYTHONPATH for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
from typing import List, Optional,Any,Dict,Union
from utils.index import get_env_variable

def giphy_find_with_metadata(search_terms: List[str]) -> Dict[str, Union[Dict, List[str]]]:
    api_key: Optional[str] = get_env_variable("GIPHY_ASSET_TOKEN")
    if not api_key:
        raise ValueError("GIPHY_ASSET_TOKEN is not set in the environment.")

    endpoint = "https://api.giphy.com/v1/gifs/search"
    valid_terms = []
    best_gif_data = None
    latest_datetime = ""

    for term in search_terms:
        params = {
            "api_key": api_key,
            "q": term,
            "limit": 5,
            "rating": "g",
            "lang": "en",
        }
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            result = response.json()
            gifs = result.get("data", [])
            for gif in gifs:
                dt = gif.get("import_datetime", "")
                if dt and dt > latest_datetime:
                    best_gif_data = {
                        "gif": gif,
                        "pagination": result.get("pagination", {}),
                        "meta": result.get("meta", {})
                    }
                    latest_datetime = dt
            if gifs:
                valid_terms.append(term)
        else:
            print(f"Failed search for term '{term}': {response.status_code}")

    return {
        "result": best_gif_data or {},
        "valid_terms": valid_terms
    }



def extract_social_upload_metadata(gif_object: Dict[str, Any]) -> Dict[str, str]:
    """
    Extracts MP4, web-friendly formats, and metadata for uploading to social platforms.

    Args:a
        gif_object (Dict[str, Any]): The Giphy GIF object.

    Returns:
        Dict[str, str]: A dictionary with keys like mp4_url, title, preview_image, etc.
    """
    original = gif_object.get("images", {}).get("original", {})
    preview = gif_object.get("images", {}).get("preview", {})
    mp4_url = original.get("mp4") or gif_object.get("images", {}).get("original_mp4", {}).get("mp4")
    gif_url = original.get("url")
    webp_url = original.get("webp")
    preview_mp4 = preview.get("mp4") or gif_object.get("images", {}).get("preview_gif", {}).get("url")

    metadata = {
        "title": gif_object.get("title", ""),
        "author": gif_object.get("username", "") or gif_object.get("user", {}).get("display_name", ""),
        "gif_url": gif_url,
        "mp4_url": mp4_url,
        "webp_url": webp_url,
        "width": original.get("width", ""),
        "height": original.get("height", ""),
        "preview_image": gif_object.get("images", {}).get("downsized_still", {}).get("url", ""),
        "preview_video": preview_mp4,
        "giphy_page": gif_object.get("url", ""),
        "embed_url": gif_object.get("embed_url", "")
    }

    return metadata
