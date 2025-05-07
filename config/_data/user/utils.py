from pydantic import BaseModel, Field, conint
from typing import Optional, List, Dict
from enum import Enum

class CreditUsage(BaseModel):
    """Tracks user credit usage for API, posts, analytics, etc."""
    total_credits: conint(ge=0) = Field(0, description="Total credits available")
    used_credits: conint(ge=0) = Field(0, description="Credits used so far")
    last_reset: Optional[str] = Field(None, description="Last time credits were reset (ISO 8601)")
    usage_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="History of credit usage events")

class PlanOption(str, Enum):
    free = "free"
    pro = "pro"
    business = "business"
    enterprise = "enterprise"

class RoleType(str, Enum):
    admin = "admin"
    user = "user"
    marketer = "marketer"
    viewer = "viewer"

class Permission(str, Enum):
    view_dashboard = "view_dashboard"
    edit_profile = "edit_profile"
    manage_users = "manage_users"
    create_campaign = "create_campaign"
    view_reports = "view_reports"
    billing_access = "billing_access"
    admin_privileges = "admin_privileges"
