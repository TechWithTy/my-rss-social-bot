
import os
import requests
from typing import List, Optional


def giphy_find_valid_gif(search_terms: List[str]) -> Dict[str, Union[str, List[str]]]:
    """
    Searches Giphy for a list of terms and returns the first valid GIF URL found,
    along with the term(s) that produced results.

    Args:
        search_terms (List[str]): List of search terms.

    Returns:
        Dict[str, Union[str, List[str]]]: A dictionary with the first found GIF URL under 'gif_url',
        and a list of valid terms under 'valid_terms'.
    """
    api_key: Optional[str] = get_env_variable("GIPHY_ASSET_TOKEN")
    if not api_key:
        raise ValueError("GIPHY_ASSET_TOKEN is not set in the environment.")

    endpoint: str = "https://api.giphy.com/v1/gifs/search"
    valid_terms: List[str] = []

    for term in search_terms:
        params: Dict[str, Union[str, int]] = {
            "api_key": api_key,
            "q": term,
            "limit": 1,
            "rating": "g",
            "lang": "en"
        }
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            gifs = data.get("data")
            if gifs:
                gif_url = gifs[0]["images"]["original"]["url"]
                valid_terms.append(term)
                return {
                    "gif_url": gif_url,
                    "valid_terms": valid_terms
                }
        else:
            print(f"Error with term '{term}': {response.status_code} - {response.text}")

    return {
        "gif_url": "",
        "valid_terms": valid_terms
    }