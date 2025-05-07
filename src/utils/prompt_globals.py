"""
prompt_globals.py
- Global state management for prompt building and workflow.
"""
from typing import Any, Dict, Optional
from utils.index import get_env_variable

TEST_MODE = get_env_variable("TEST_MODE").lower() == "true"
_prompt_globals: Dict[str, Any] = {
    "prompt": None,
    "creative_prompt": None,
    "gif_prompt": None,
    "hashtags": [],
    "system_instructions": None,
    "blog_content": None,
}

def get_prompt_globals() -> Dict[str, Any]:
    return _prompt_globals

def set_prompt_global(key: str, value: Any) -> None:
    _prompt_globals[key] = value

def reset_prompt_globals() -> None:
    global _prompt_globals
    _prompt_globals = {
        "prompt": None,
        "creative_prompt": None,
        "gif_prompt": None,
        "hashtags": [],
        "system_instructions": None,
        "blog_content": None,
    }
