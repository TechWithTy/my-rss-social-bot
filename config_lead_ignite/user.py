from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Integrations
from config._data.user.analytics import SocialAnalytics
from config._data.user.research import TopicResearchResult
from config._data.user.blogs.plan import BlogPlan
from config._data.user.blogs.posted import PostedBlog
from config._data.user.calendar.calendar import BlogCalendar
from config._data.user.billing.billing import BillingInfo
from config._data.user.ai_actions.ai_actions import AIUsageLog
from config._data.user.subscription import Subscription
from config._data.user.core import PII, ContactInfo, LocationInfo, SecuritySettings, OnboardingStatus

from config._data.user.company_info import CompanyInfo
from config._data.user.marketing_profile import MarketingProfile
from config._data.user.social_links import SocialLinks
from config._data.user.platform_access import PlatformAccess
from config._data.user.user_settings import UserSettings
from config._data.user.saved_search import SavedSearch
from config._data.user.notification_preferences import NotificationPreferences
from config._data.user.integration import Integration
from config._data.user.billing_history import BillingHistoryItem
from config._data.user.two_factor_auth import TwoFactorAuth
from config._data.user.team_member import TeamMember
from config._data.user.kanban_state import KanbanState
from config._data.user.kanban_task import KanbanTask

# Credits and Plans
# Utility classes and enums moved to config._data.user.utils

    



# --- CompanyInfo model is now imported from config._data.user.company_info ---


# --- MarketingProfile model is now imported from config._data.user.marketing_profile ---

# --- UserSettings model is now imported from config._data.user.user_settings ---


class User(BaseModel):
    """Full user profile, grouped by logical domain and extended with analytics, research, blogs, and calendar.
    // todo: Add DB-level unique constraint on user_id, email, and tenant_id/org_id.
    // Note: Each user is tied to a single company/org (one-to-one relationship).
    // SaaS: Supports invitations, team management, plan history, feature flags, and soft deletes.
    """
    tenant_id: str = Field(..., description="Unique tenant/org identifier for multi-tenancy")  # ! Must match company.tenant_id
    # --- Core fields at root ---
    pii: PII
    contact: ContactInfo
    location: LocationInfo
    security: SecuritySettings
    onboarding: OnboardingStatus
    # --- End core fields ---
    company: CompanyInfo
    marketing: MarketingProfile
    socials: SocialLinks
    platform: PlatformAccess
    preferences: UserSettings

    # Extended fields
    saved_searches: list[SavedSearch] = Field(default_factory=list, description="User's saved searches")
    notification_preferences: Optional[NotificationPreferences] = Field(None, description="Notification preferences")
    integrations: list[Integration] = Field(default_factory=list, description="Connected integrations")
    billing_history: list[BillingHistoryItem] = Field(default_factory=list, description="User's billing history")
    two_factor_auth: Optional[TwoFactorAuth] = Field(None, description="Two-factor authentication settings")
    team_members: list[TeamMember] = Field(default_factory=list, description="Team members associated with the user")
    security_settings: Optional[SecuritySettings] = Field(None, description="Additional security settings")
    kanban_states: list[KanbanState] = Field(default_factory=list, description="Kanban board states for the user")
    kanban_tasks: list[KanbanTask] = Field(default_factory=list, description="Kanban tasks for the user")

    analytics: Optional[SocialAnalytics] = Field(None, description="Aggregated analytics for all social platforms")
    research: Optional[list[TopicResearchResult]] = Field(default_factory=list, description="Research results for topics of interest")
    blogs_planned: Optional[list[BlogPlan]] = Field(default_factory=list, description="Planned blog posts")
    blogs_posted: Optional[list[PostedBlog]] = Field(default_factory=list, description="Posted blog content")
    calendar: Optional[BlogCalendar] = Field(None, description="User's blog/calendar schedule")
    subscription: Subscription = Field(..., description="User subscription, plan, and credit allocation")
    billing_info: Optional[BillingInfo] = Field(None, description="User billing and payment information")
    ai_usage_log: Optional[AIUsageLog] = Field(default_factory=AIUsageLog, description="AI usage and actions tracking for the user")
    # Invitation system
    invitations: Optional[list] = Field(default_factory=list, description="Pending invitations for this user (list of orgs/tenant_ids)")
    # Team management (roles/permissions handled in PlatformAccess)
    teams: Optional[list] = Field(default_factory=list, description="List of tenant_ids for all orgs/teams this user belongs to")
    # Plan upgrade/downgrade tracking
    plan_history: Optional[list] = Field(default_factory=list, description="History of plan changes (list of dicts with plan info and timestamps)")
    # Feature flags
    feature_flags: Optional[dict] = Field(default_factory=dict, description="Feature flags for staged rollouts (key: flag name, value: enabled)")
    # Soft delete/archival
    is_deleted: bool = Field(False, description="Soft delete flag for user")
    archived_at: Optional[str] = Field(None, description="Archival timestamp (ISO 8601)")

    @classmethod
    def validate_unique(cls, users: list, user_id: str, email: str, tenant_id: str) -> bool:
        """
        // ! Validate uniqueness of user_id, email, and tenant_id (in-memory check only).
        // ! Must enforce at DB level for production.
        """
        for user in users:
            if user.pii.user_id == user_id or user.contact.email == email or user.tenant_id == tenant_id:
                return False
        return True

    class Config:
        use_enum_values = True