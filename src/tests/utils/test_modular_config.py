import pytest
from src.utils.config.config_provider import load_modular_config

def test_load_modular_config_logs():
    config = load_modular_config()
    print("Loaded config:", config)
    assert isinstance(config, dict)
    # Check that user_profile is present and has expected keys
    assert "user_profile" in config, f"user_profile missing! Config: {config}"
    user_profile = config["user_profile"]
    assert "medium_username" in user_profile, f"medium_username missing! user_profile: {user_profile}"
    assert user_profile["medium_username"] == "codingoni"
