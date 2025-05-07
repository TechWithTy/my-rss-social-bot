import requests
from typing import List, Optional, Dict, Any
from utils.index import get_env_variable

# ! Untested: Needs integration and test coverage.
def unsplash_search_images(query: str, per_page: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Search Unsplash for high-quality images matching the query.
    Returns a list of image data dicts or None if not found.
    """
    access_key = get_env_variable("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise ValueError("UNSPLASH_ACCESS_KEY is not set in the environment.")

    endpoint = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": per_page,
        "client_id": access_key
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("results")

def unsplash_find_first_image_from_tags(tags: List[str], per_page: int = 5) -> Optional[Dict[str, Any]]:
    """
    Tries each tag in order, returns the first image result dict found, else None.
    """
    for tag in tags:
        results = unsplash_search_images(tag, per_page=per_page)
        if results:
            return results[0]
    return None

# todo: Add more utility functions for Unsplash as needed.
