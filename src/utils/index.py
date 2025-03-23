from bs4 import BeautifulSoup
from bs4.element import Tag
from bs4 import BeautifulSoup
from bs4.element import Tag
import os
from typing import Optional
from dotenv import load_dotenv

# ✅ Load environment variables from .env file (if running locally)
load_dotenv()

def parse_html_blog_content(html_content: str) -> str:
    """
    Strips HTML and returns plain text, links, images, and embedded media from blog content.
    Ideal for feeding into AI models.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Collect visible text
    text = soup.get_text(separator="\n", strip=True)

    # 2. Extract links
    links = []
    for a in soup.find_all("a", href=True):
        if isinstance(a, Tag):
            link_text = a.get_text(strip=True)
            href = a.get("href")
            if href:
                links.append(f"{link_text} ({href})")

    # 3. Extract images
    images = []
    for img in soup.find_all("img", src=True):
        if isinstance(img, Tag):
            alt = img.get("alt", "No alt text")
            src = img.get("src")
            if src:
                images.append(f"{alt} [Image] ({src})")

    # 4. Extract media (iframes, videos)
    media = []
    for tag in soup.find_all(["iframe", "video"], src=True):
        if isinstance(tag, Tag):
            src = tag.get("src")
            tag_type = tag.name.upper()
            if src:
                media.append(f"[{tag_type}] {src}")

    # Section formatting
    links_section = "\n\nLinks:\n" + "\n".join(links) if links else ""
    image_section = "\n\nImages:\n" + "\n".join(images) if images else ""
    media_section = "\n\nEmbedded Media:\n" + "\n".join(media) if media else ""
    print(f"{links_section}{image_section}{media_section}")
    return f"{text}\n\n {links_section}\n\n  + {media_section}\n\n + {media_section}"

def get_env_variable(key: str) -> Optional[str]:
    """
    Fetches an environment variable, prioritizing:
    1. Local environment (`.env` file)
    2. GitHub Actions secret (if running in GitHub workflow)

    Args:
        key (str): The name of the environment variable.

    Returns:
        Optional[str]: The environment variable value or None if not found.
    """
    return os.getenv(key, os.environ.get(key))