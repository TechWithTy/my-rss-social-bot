import os
import json
from typing import Optional, List, Dict
from bs4 import BeautifulSoup

# Define the directory and ensure it exists
TEMP_FOLDER = '_temp'
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Define the storage file path within the _temp directory
STORAGE_FILE = os.path.join(TEMP_FOLDER, 'blog_cache.json')

def load_blog_cache() -> List[Dict]:
    """Loads the blog cache from JSON file."""
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("⚠️ Cache file is corrupted. Returning empty cache.")
            return []

def save_blog_cache(blog_entries: List[Dict]) -> None:
    """Saves blog cache to JSON file."""
    with open(STORAGE_FILE, 'w') as file:
        json.dump(blog_entries, file, indent=2)

def delete_blog_cache() -> None:
    """Deletes the blog cache file if it exists."""
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
        print("🗑️ Blog cache deleted.")
    else:
        print("ℹ️ No blog cache file to delete.")

def is_blog_cache_valid() -> bool:
    """
    Checks if the blog cache file exists and contains a valid Medium blog dictionary structure.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    print(f"🧪 Checking if cache file exists at: {STORAGE_FILE}")
    if not os.path.exists(STORAGE_FILE):
        print("❌ Cache file does not exist.")
        return False

    try:
        with open(STORAGE_FILE, 'r') as file:
            raw = file.read()
            print(f"📦 Raw cache content:\n{raw[:300]}...")
            data = json.loads(raw)
            print(f"✅ Parsed data type: {type(data).__name__}")

            if not isinstance(data, dict) or "blogs" not in data:
                print("❌ Invalid structure. Expected dict with 'blogs' key.")
                return False

            blogs = data["blogs"]
            if not isinstance(blogs, list):
                print("❌ 'blogs' key is not a list.")
                return False

            missing_ids = [post for post in blogs if "id" not in post]
            if missing_ids:
                print(f"❌ These entries are missing 'id':\n{missing_ids}")
                return False

            print("✅ Blog cache is valid.")
            return True

    except Exception as e:
        print(f"❌ Error reading or parsing cache file: {e}")
        return False

def extract_blog_media(content_html: str) -> Dict[str, List[str]]:
    """Extracts links, images, and embeds from the blog content."""
    soup = BeautifulSoup(content_html, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    images = [img['src'] for img in soup.find_all('img', src=True)]
    embeds = [script['src'] for script in soup.find_all('script', src=True)]
    return {
        "links": links,
        "images": images,
        "embeds": embeds
    }
