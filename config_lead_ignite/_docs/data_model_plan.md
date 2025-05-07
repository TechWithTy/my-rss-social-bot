# Data Model Schema Plan

## Principles
- **Type-safe, Pydantic-first**
- **Modular, extensible, DRY**
- **CQRS & Clean Architecture ready**
- **All timestamps, soft delete, and audit fields included**

---

## 1. User Entity (Aggregate Root)
- `id: UUID`
- `username: str`
- `email: str`
- `password_hash: str`
- `is_active: bool`
- `is_deleted: bool`
- `created_at: datetime`
- `updated_at: datetime`

### 1.1 UserProfile (One-to-One)
- `user_id: UUID`
- `first_name: str`
- `last_name: str`
- `contact_info: ContactInfo`
- `location: LocationInfo`
- `preferences: UserSettings`
- `socials: SocialLinks`
- `company: CompanyInfo`
- `onboarding: OnboardingStatus`
- `feature_flags: dict`
- `archived_at: Optional[datetime]`

### 1.2 Security (One-to-One)
- `user_id: UUID`
- `two_factor_auth: TwoFactorAuth`
- `security_settings: SecuritySettings`

### 1.3 Subscription (One-to-One)
- `user_id: UUID`
- `subscription_type: SubscriptionType`
- `status: SubscriptionStatus`
- `started_at: datetime`
- `ends_at: datetime`
- `plan_history: List[PlanChange]`

### 1.4 Billing (One-to-One)
- `user_id: UUID`
- `billing_info: BillingInfo`
- `billing_history: List[BillingHistoryItem]`
- `payment_methods: List[PaymentDetails]`

### 1.5 Integrations (One-to-Many)
- `user_id: UUID`
- `integrations: List[Integration]`

### 1.6 Analytics (One-to-One)
- `user_id: UUID`
- `analytics: SocialAnalytics`

### 1.7 Teams (Many-to-Many)
- `user_id: UUID`
- `team_id: UUID`

---

## 2. Content & Workflow

### Blog
- `id: UUID`
- `user_id: UUID`
- `status: BlogStatus`
- `content: str`
- `created_at: datetime`
- `posted_at: Optional[datetime]`
- `calendar: Optional[BlogCalendar]`

### Kanban
- `user_id: UUID`
- `states: List[KanbanState]`
- `tasks: List[KanbanTask]`

### Research
- `user_id: UUID`
- `topics: List[TopicResearchResult]`

---

## 3. Automation & AI
- `ai_usage_log: List[AIUsageLog]`
- `notification_preferences: NotificationPreferences`
- `saved_searches: List[SavedSearch]`
- `invitations: List[Invitation]`

---

## 4. Shared/Supporting Models
- ContactInfo (phone, email, etc.)
- LocationInfo (country, state, city, etc.)
- SocialLinks (twitter, linkedin, etc.)
- CompanyInfo (name, industry, etc.)
- UserSettings (preferences, notification, etc.)
- SecuritySettings (password policies, etc.)
- TwoFactorAuth (enabled, methods, etc.)
- Integration (type, connected_at, etc.)
- BillingInfo (address, payment method, etc.)
- BillingHistoryItem (amount, date, status)
- PaymentDetails (provider, last4, etc.)
- PlanChange (from, to, changed_at)
- TeamMember (role, joined_at)
- KanbanState, KanbanTask
- BlogPlan, PostedBlog, BlogCalendar
- TopicResearchResult
- AIUsageLog
- Invitation

---

## 5. Audit & Soft Delete
- All models include `created_at`, `updated_at`, `is_deleted`, `archived_at` where appropriate.

---

## 6. Directory Structure Example

```
config_lead_ignite/
  _data/
    user/
      core.py
      profile.py
      security.py
      subscription.py
      billing.py
      integrations.py
      analytics.py
      teams.py
      kanban.py
      blog.py
      research.py
      ai_usage.py
      invitation.py
      shared/
        contact_info.py
        location_info.py
        ...
```

---

## Next Steps
1. Review and finalize the entity list and relationships
2. Draft Pydantic models for each entity and sub-entity
3. Implement models in the corresponding modules
4. Add tests for serialization, validation, and edge cases
5. Write migration scripts if needed for existing data
