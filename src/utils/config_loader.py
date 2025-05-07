import os
import yaml
from typing import Dict, Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')

# ! Loads and deeply merges all YAML config files in the config/ directory
def load_config() -> Dict[str, Any]:
    config = {}
    for fname in sorted(os.listdir(CONFIG_DIR)):
        if fname.endswith('.yaml') or fname.endswith('.yml'):
            with open(os.path.join(CONFIG_DIR, fname), 'r', encoding='utf-8') as f:
                part = yaml.safe_load(f) or {}
                config = deep_merge_dicts(config, part)
    return config

# ! Recursively merges two dicts (b overrides a)
def deep_merge_dicts(a: dict, b: dict) -> dict:
    result = a.copy()
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge_dicts(result[k], v)
        else:
            result[k] = v
    return result

# * Usage Example:
# config = load_config()
# print(config)
