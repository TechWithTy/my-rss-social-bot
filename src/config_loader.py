import yaml
from typing import Dict, Any

def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    """Loads the user configuration from YAML."""
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# ✅ Load config globally
config = load_config()
