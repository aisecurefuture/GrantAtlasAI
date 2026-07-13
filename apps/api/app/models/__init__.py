import uuid
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(StrEnum):
    OWNER = "Owner"
    ADMIN = "Admin"
    GRANT_WRITER = "Grant Writer"
    REVIEWER = "Reviewer"
    VIEWER = "Viewer"


class OpportunityStatus(StrEnum):
    NEW = "New"
    MONITORING = "Monitoring"
    APPLIED = "Applied"
    SKIPPED = "Skipped"
    REQUIRES_PARTNER = "Requires Partner"


class RecommendedAction(StrEnum):
    APPLY = "Apply"
    PARTNER = "Partner"
    MONITOR = "Monitor"
    SKIP = "Skip"


class CaptureStatus(StrEnum):
    WATCHING = "Watching"
    QUALIFYING = "Qualifying"
    PURSUING = "Pursuing"
    PROPOSING = "Proposing"
    SUBMITTED = "Submitted"
    NO_BID = "No Bid"


class ContractAction(StrEnum):
    PURSUE = "Pursue"
    TEAM = "Team"
    WATCH = "Watch"
    NO_BID = "No Bid"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(80), default="Free Trial")
    subscription_status: Mapped[str] = mapped_column(String(80), default="trialing")
    trial_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255))
    usage_limits: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    onboarding_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="tenant", passive_deletes="all")
    profile: Mapped["OrganizationProfile"] = relationship(back_populates="tenant", uselist=False, passive_deletes="all")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.VIEWER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped[Tenant] = relationship(back_populates="users")


class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ein: Mapped[str | None] = mapped_column(String(32))
    uei: Mapped[str | None] = mapped_column(String(32))
    sam_status: Mapped[str | None] = mapped_column(String(120))
    grants_gov_status: Mapped[str | None] = mapped_column(String(120))
    nonprofit_status: Mapped[str | None] = mapped_column(String(120))
    mission: Mapped[str] = mapped_column(Text, default="")
    vision: Mapped[str] = mapped_column(Text, default="")
    programs: Mapped[list] = mapped_column(JSON, default=list)
    focus_areas: Mapped[list] = mapped_column(JSON, default=list)
    geographic_service_area: Mapped[str] = mapped_column(Text, default="")
    target_populations: Mapped[list] = mapped_column(JSON, default=list)
    past_performance: Mapped[str] = mapped_column(Text, default="")
    key_staff_bios: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant: Mapped[Tenant] = relationship(back_populates="profile")


class Opportunity(Base):
    __tablename__ = "opportunities"
    __table_args__ = (UniqueConstraint("tenant_id", "source", "opportunity_number", name="uq_opportunity_source_number"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    agency: Mapped[str] = mapped_column(String(255), default="")
    source: Mapped[str] = mapped_column(String(80), default="Manual", index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    opportunity_number: Mapped[str | None] = mapped_column(String(160))
    assistance_listing: Mapped[str | None] = mapped_column(String(120))
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    award_floor: Mapped[int | None] = mapped_column(Integer)
    award_ceiling: Mapped[int | None] = mapped_column(Integer)
    expected_awards: Mapped[int | None] = mapped_column(Integer)
    eligibility: Mapped[str] = mapped_column(Text, default="")
    cost_share_required: Mapped[bool] = mapped_column(Boolean, default=False)
    required_partners: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
    categories: Mapped[list] = mapped_column(JSON, default=list)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    attachments: Mapped[list] = mapped_column(JSON, default=list)
    contact_info: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[OpportunityStatus] = mapped_column(Enum(OpportunityStatus), default=OpportunityStatus.NEW)
    assigned_owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class OpportunityScore(Base):
    __tablename__ = "opportunity_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    mission_fit: Mapped[float] = mapped_column(Float, nullable=False)
    eligibility_fit: Mapped[float] = mapped_column(Float, nullable=False)
    deadline_urgency: Mapped[float] = mapped_column(Float, nullable=False)
    funding_size: Mapped[float] = mapped_column(Float, nullable=False)
    proposal_complexity: Mapped[float] = mapped_column(Float, nullable=False)
    partnership_fit: Mapped[float] = mapped_column(Float, nullable=False)
    past_performance_fit: Mapped[float] = mapped_column(Float, nullable=False)
    strategic_value: Mapped[float] = mapped_column(Float, nullable=False)
    probability_of_success: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_action: Mapped[RecommendedAction] = mapped_column(Enum(RecommendedAction), nullable=False)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    ai_narrative: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ContractOpportunity(Base):
    __tablename__ = "contract_opportunities"
    __table_args__ = (UniqueConstraint("tenant_id", "source", "notice_id", name="uq_contract_source_notice"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(80), default="SAM.gov", index=True)
    notice_id: Mapped[str | None] = mapped_column(String(160))
    solicitation_number: Mapped[str | None] = mapped_column(String(160))
    department: Mapped[str] = mapped_column(String(255), default="")
    subtier: Mapped[str] = mapped_column(String(255), default="")
    office: Mapped[str] = mapped_column(String(255), default="")
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    opportunity_type: Mapped[str] = mapped_column(String(160), default="")
    set_aside: Mapped[str | None] = mapped_column(String(255))
    set_aside_code: Mapped[str | None] = mapped_column(String(80))
    naics_code: Mapped[str | None] = mapped_column(String(12), index=True)
    classification_code: Mapped[str | None] = mapped_column(String(20), index=True)
    place_of_performance: Mapped[dict] = mapped_column(JSON, default=dict)
    description_url: Mapped[str | None] = mapped_column(String(1000))
    ui_link: Mapped[str | None] = mapped_column(String(1000))
    resource_links: Mapped[list] = mapped_column(JSON, default=list)
    point_of_contact: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[CaptureStatus] = mapped_column(Enum(CaptureStatus), default=CaptureStatus.WATCHING)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ContractScore(Base):
    __tablename__ = "contract_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_opportunity_id: Mapped[str] = mapped_column(ForeignKey("contract_opportunities.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    naics_fit: Mapped[float] = mapped_column(Float, nullable=False)
    psc_fit: Mapped[float] = mapped_column(Float, nullable=False)
    past_performance_fit: Mapped[float] = mapped_column(Float, nullable=False)
    set_aside_fit: Mapped[float] = mapped_column(Float, nullable=False)
    deadline_fit: Mapped[float] = mapped_column(Float, nullable=False)
    competition_fit: Mapped[float] = mapped_column(Float, nullable=False)
    strategic_value: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_action: Mapped[ContractAction] = mapped_column(Enum(ContractAction), nullable=False)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    ai_narrative: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class PastPerformanceProject(Base):
    __tablename__ = "past_performance_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer: Mapped[str] = mapped_column(String(255), default="")
    contract_number: Mapped[str | None] = mapped_column(String(120))
    naics_codes: Mapped[list] = mapped_column(JSON, default=list)
    classification_codes: Mapped[list] = mapped_column(JSON, default=list)
    value: Mapped[int | None] = mapped_column(Integer)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(Text, default="")
    outcomes: Mapped[list] = mapped_column(JSON, default=list)
    contact_reference: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TeamingPartner(Base):
    __tablename__ = "teaming_partners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    partner_type: Mapped[str] = mapped_column(String(120), default="Subcontractor")
    uei: Mapped[str | None] = mapped_column(String(32))
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    naics_codes: Mapped[list] = mapped_column(JSON, default=list)
    set_aside_statuses: Mapped[list] = mapped_column(JSON, default=list)
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CapturePlan(Base):
    __tablename__ = "capture_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_opportunity_id: Mapped[str] = mapped_column(ForeignKey("contract_opportunities.id", ondelete="CASCADE"), nullable=False, unique=True)
    status: Mapped[CaptureStatus] = mapped_column(Enum(CaptureStatus), default=CaptureStatus.QUALIFYING)
    bid_decision: Mapped[str] = mapped_column(String(80), default="Undecided")
    win_themes: Mapped[list] = mapped_column(JSON, default=list)
    customer_pain_points: Mapped[list] = mapped_column(JSON, default=list)
    competitor_notes: Mapped[str] = mapped_column(Text, default="")
    partner_strategy: Mapped[str] = mapped_column(Text, default="")
    compliance_matrix: Mapped[list] = mapped_column(JSON, default=list)
    color_team_reviews: Mapped[list] = mapped_column(JSON, default=list)
    tasks: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ProposalWorkspace(Base):
    __tablename__ = "proposal_workspaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    outline: Mapped[list] = mapped_column(JSON, default=list)
    compliance_matrix: Mapped[list] = mapped_column(JSON, default=list)
    required_attachments: Mapped[list] = mapped_column(JSON, default=list)
    tasks: Mapped[list] = mapped_column(JSON, default=list)
    budget: Mapped[dict] = mapped_column(JSON, default=dict)
    narrative_sections: Mapped[list] = mapped_column(JSON, default=list)
    internal_notes: Mapped[str] = mapped_column(Text, default="")
    reviewer_comments: Mapped[list] = mapped_column(JSON, default=list)
    version_history: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class LibraryItem(Base):
    __tablename__ = "library_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id", ondelete="SET NULL"), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(160), nullable=False)
    target_type: Mapped[str] = mapped_column(String(120), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(36))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
