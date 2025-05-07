import requests
from typing import List, Optional, Dict, Any
from utils.index import get_env_variable

# ! Untested: Needs integration and test coverage.
def shutterstock_search_images(query: str, per_page: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Search Shutterstock for high-quality images matching the query.
    Returns a list of image data dicts or None if not found.
    """
    api_key = get_env_variable("SHUTTERSTOCK_API_KEY")
    if not api_key:
        raise ValueError("SHUTTERSTOCK_API_KEY is not set in the environment.")

    endpoint = "https://api.shutterstock.com/v2/images/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"query": query, "per_page": per_page}
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data")

def shutterstock_find_first_image_from_tags(tags: List[str], per_page: int = 5) -> Optional[Dict[str, Any]]:
    """
    Tries each tag in order, returns the first image result dict found, else None.
    """
    for tag in tags:
        results = shutterstock_search_images(tag, per_page=per_page)
        if results:
            return results[0]
    return None

# todo: Add more utility functions for Shutterstock as needed.
