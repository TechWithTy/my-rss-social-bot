from typing import Dict, Any

def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries with override taking precedence.
    
    Args:
        base: Base configuration dictionary
        override: Override dictionary with values to apply on top of base
        
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        # If both base and override have dict at this key, merge them recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        # Otherwise override takes precedence
        else:
            result[key] = value
            
    return result
