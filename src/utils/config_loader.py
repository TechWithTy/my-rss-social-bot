import yaml
import os
from typing import Dict, Any

def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Loads the user configuration from YAML.
    Checks multiple possible locations for the config file.
    """
    # List of possible locations for the config file
    possible_paths = [
        file_path,  # Current directory
        os.path.join(os.path.dirname(__file__), "../..", file_path),  # Project root
        os.path.join(os.path.dirname(__file__), "../../_configs", file_path),  # _configs directory
    ]
    
    # Try each path until we find the file
    for path in possible_paths:
        try:
            with open(path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            continue
    
    # For testing environments, return a default empty config if file not found
    print(f"Warning: Config file '{file_path}' not found. Using default empty config for testing.")
    return {}

# Load config globally
config = load_config()
