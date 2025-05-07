from pydantic import BaseModel, Field
from typing import Dict

class UserSettings(BaseModel):
    """User preferences/settings as key-value pairs."""
    settings: Dict[str, str] = Field(default_factory=dict, description="User preferences/settings")
