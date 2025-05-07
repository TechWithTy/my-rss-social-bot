import requests
from typing import List, Optional, Dict, Any
from utils.index import get_env_variable

# ! Untested: Needs integration and test coverage.
def adobe_stock_search_images(query: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Search Adobe Stock for high-quality images matching the query.
    Returns a list of image data dicts or None if not found.
    """
    api_key = get_env_variable("ADOBE_STOCK_API_KEY")
    if not api_key:
        raise ValueError("ADOBE_STOCK_API_KEY is not set in the environment.")

    endpoint = "https://stock.adobe.io/Rest/Media/1/Search/Files"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    params = {"search_parameters[words]": query, "search_parameters[limit]": limit}
    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("files")

def adobe_stock_find_first_image_from_tags(tags: List[str], limit: int = 5) -> Optional[Dict[str, Any]]:
    """
    Tries each tag in order, returns the first image result dict found, else None.
    """
    for tag in tags:
        results = adobe_stock_search_images(tag, limit=limit)
        if results:
            return results[0]
    return None

# todo: Add more utility functions for Adobe Stock as needed.
