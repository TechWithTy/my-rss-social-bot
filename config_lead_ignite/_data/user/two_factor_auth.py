from pydantic import BaseModel, Field
from typing import Optional

from enum import Enum
from typing import Optional, List

class TwoFactorMethod(str, Enum):
    sms = "sms"
    authenticator_app = "authenticator_app"
    email = "email"
    none = "none"

class TwoFactorAuth(BaseModel):
    """Represents a user's two-factor authentication settings."""
    enabled: bool = Field(False, description="Is two-factor authentication enabled?")
    method: TwoFactorMethod = Field(TwoFactorMethod.none, description="2FA method (e.g., SMS, authenticator app, email)")
    last_verified_at: Optional[str] = Field(None, description="Last verification timestamp (ISO 8601)")
    backup_codes: List[str] = Field(default_factory=list, description="Backup codes for 2FA")
    device_info: Optional[str] = Field(None, description="Device info for 2FA, if applicable")
    # todo: Add recovery options and audit fields
