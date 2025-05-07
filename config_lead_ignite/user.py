# Modular imports for all user-related models (Lead Ignite)
from pydantic import BaseModel, Field
from typing import Optional, List

# --- Core user identity and settings ---
from config_lead_ignite._data.user.core import (
    PII, ContactInfo, LocationInfo,  OnboardingStatus
)

# --- Company and marketing ---
from config_lead_ignite._data.user.company.company_info import CompanyInfo
from config_lead_ignite._data.user.context.marketing_profile import MarketingProfile

# --- Socials and links ---
from config_lead_ignite._data.user.socials.social_links import SocialLinks


# --- Saved searches, notification preferences, integrations ---
from config_lead_ignite._data.user.cache.saved_search import SavedSearch

# --- Billing and subscription ---

from config_lead_ignite._data.user.billing.global_billing import GlobalBilling

# --- Two-factor auth and security ---

# --- Team and invitations ---
from config_lead_ignite._data.user.team.global_team import GlobalTeam
# todo: Import Invitation model when implemented



# --- Analytics, research, blogs ---
from config_lead_ignite._data.user.analytics.global_analytics import GlobalAnalytics
from config_lead_ignite._data.user.research.global_research_stats import GlobalResearchStats
from config_lead_ignite._data.user.kanban.global_kanban import GlobalKanban
from config_lead_ignite._data.user.blogs.global_blog import GlobalBlog
from config_lead_ignite._data.user.ai_config.global_ai_config import GlobalAIConfig
from config_lead_ignite._data.user.settings.global_user_settings import GlobalUserSettings
from config_lead_ignite._data.user.campaign.global_campaign import GlobalCampaign
from config_lead_ignite._data.user.context.global_ai_context import GlobalAIContext

# --- End imports ---

class User(BaseModel):
    # --- Core fields at root ---
    pii: PII
    contact: ContactInfo
    location: LocationInfo
    onboarding: OnboardingStatus
    company: CompanyInfo
    marketing: MarketingProfile
    socials: SocialLinks
    campaigns: GlobalCampaign = Field(default_factory=GlobalCampaign, description="User's global campaign")
    # --- Extended fields ---
    blogs: GlobalBlog = Field(default_factory=GlobalBlog, description="User's global blog")
    saved_searches: List[SavedSearch] = Field(default_factory=list, description="User's saved searches")
    billing: GlobalBilling = Field(default_factory=GlobalBilling, description="User's billing history")
    kanban: GlobalKanban = Field(default_factory=GlobalKanban, description="User's global kanban")
    analytics: Optional[GlobalAnalytics] = Field(None, description="Aggregated analytics for all social platforms")
    research: List[GlobalResearchStats] = Field(default_factory=list, description="Research results for topics of interest")
    ai_context: Optional[GlobalAIContext] = Field(None, description="AI context for the user")
    ai_config: Optional[GlobalAIConfig] = Field(None, description="AI context for the user")
    teams: List[GlobalTeam] = Field(default_factory=list, description="List of tenant_ids for all orgs/teams this user belongs to")

    # Feature flags
    feature_flags: dict = Field(default_factory=dict, description="Feature flags for staged rollouts (key: flag name, value: enabled)")
    # Soft delete/archival
    is_deleted: bool = Field(False, description="Soft delete flag for user")
    archived_at: Optional[str] = Field(None, description="Archival timestamp (ISO 8601)")
    user_settings: Optional[GlobalUserSettings] = Field(None, description="User settings")

    @classmethod
    def validate_unique(cls, users: List['User'], user_id: str, email: str, tenant_id: str) -> bool:
        """
        // ! Validate uniqueness of user_id, email, and tenant_id (in-memory check only).
        // ! Must enforce at DB level for production.
        """
        for user in users:
            if user.pii.user_id == user_id or user.contact.email == email or getattr(user, 'tenant_id', None) == tenant_id:
                return False
        return True

    class Config:
        use_enum_values = True