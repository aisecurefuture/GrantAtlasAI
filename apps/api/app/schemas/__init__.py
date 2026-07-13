from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    role: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    is_super_admin: bool

    model_config = {"from_attributes": True}


class RegisterIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    plan: str


class TenantUserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUserCreateIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    role: str = "Viewer"


class TenantUserCreateOut(BaseModel):
    user: TenantUserOut
    temporary_password: str


class TenantUserUpdateIn(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class AccountDeleteIn(BaseModel):
    confirm_organization_name: str


class AdminTenantCreateIn(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    owner_name: str = Field(min_length=1, max_length=255)
    owner_email: EmailStr
    plan: str = "Free Trial"


class AdminTenantCreateOut(BaseModel):
    tenant_id: str
    owner: TenantUserOut
    temporary_password: str


class OrganizationProfileIn(BaseModel):
    organization_name: str
    ein: str | None = None
    uei: str | None = None
    sam_status: str | None = None
    grants_gov_status: str | None = None
    nonprofit_status: str | None = None
    mission: str = ""
    vision: str = ""
    programs: list[Any] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)
    geographic_service_area: str = ""
    target_populations: list[str] = Field(default_factory=list)
    past_performance: str = ""
    key_staff_bios: list[Any] = Field(default_factory=list)


class OrganizationProfileOut(OrganizationProfileIn):
    id: str
    tenant_id: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class OpportunityIn(BaseModel):
    title: str
    agency: str = ""
    source: str = "Manual"
    source_url: str | None = None
    opportunity_number: str | None = None
    assistance_listing: str | None = None
    posted_date: datetime | None = None
    close_date: datetime | None = None
    award_floor: int | None = None
    award_ceiling: int | None = None
    expected_awards: int | None = None
    eligibility: str = ""
    cost_share_required: bool = False
    required_partners: str = ""
    description: str = ""
    categories: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    attachments: list[Any] = Field(default_factory=list)
    contact_info: dict[str, Any] = Field(default_factory=dict)


class OpportunityOut(OpportunityIn):
    id: str
    tenant_id: str
    status: str
    last_updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ScoreOut(BaseModel):
    total_score: float
    mission_fit: float
    eligibility_fit: float
    deadline_urgency: float
    funding_size: float
    proposal_complexity: float
    partnership_fit: float
    past_performance_fit: float
    strategic_value: float
    probability_of_success: float
    recommended_action: str
    reasons: list[str]
    ai_narrative: str | None = None

    model_config = {"from_attributes": True}


class OpportunityListItemOut(OpportunityOut):
    fit_score: float | None = None
    recommended_action: str | None = None


class OpportunityDetailOut(BaseModel):
    opportunity: OpportunityOut
    score: ScoreOut | None


class ContractOpportunityIn(BaseModel):
    title: str
    source: str = "Manual"
    notice_id: str | None = None
    solicitation_number: str | None = None
    department: str = ""
    subtier: str = ""
    office: str = ""
    posted_date: datetime | None = None
    response_deadline: datetime | None = None
    opportunity_type: str = ""
    set_aside: str | None = None
    set_aside_code: str | None = None
    naics_code: str | None = None
    classification_code: str | None = None
    place_of_performance: dict[str, Any] = Field(default_factory=dict)
    description_url: str | None = None
    ui_link: str | None = None
    resource_links: list[str] = Field(default_factory=list)
    point_of_contact: list[Any] = Field(default_factory=list)
    active: bool = True


class ContractOpportunityOut(ContractOpportunityIn):
    id: str
    tenant_id: str
    status: str
    last_updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractScoreOut(BaseModel):
    total_score: float
    naics_fit: float
    psc_fit: float
    past_performance_fit: float
    set_aside_fit: float
    deadline_fit: float
    competition_fit: float
    strategic_value: float
    recommended_action: str
    reasons: list[str]
    ai_narrative: str | None = None

    model_config = {"from_attributes": True}


class ContractListItemOut(ContractOpportunityOut):
    fit_score: float | None = None
    recommended_action: str | None = None


class ContractDetailOut(BaseModel):
    contract: ContractOpportunityOut
    score: ContractScoreOut | None
    capture_plan: "CapturePlanOut | None" = None


class PastPerformanceProjectIn(BaseModel):
    project_name: str
    customer: str = ""
    contract_number: str | None = None
    naics_codes: list[str] = Field(default_factory=list)
    classification_codes: list[str] = Field(default_factory=list)
    value: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    summary: str = ""
    outcomes: list[str] = Field(default_factory=list)
    contact_reference: dict[str, Any] = Field(default_factory=dict)


class PastPerformanceProjectOut(PastPerformanceProjectIn):
    id: str
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TeamingPartnerIn(BaseModel):
    name: str
    partner_type: str = "Subcontractor"
    uei: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    naics_codes: list[str] = Field(default_factory=list)
    set_aside_statuses: list[str] = Field(default_factory=list)
    contact_name: str | None = None
    contact_email: str | None = None
    notes: str = ""


class TeamingPartnerOut(TeamingPartnerIn):
    id: str
    tenant_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CapturePlanIn(BaseModel):
    contract_opportunity_id: str
    status: str = "Qualifying"
    bid_decision: str = "Undecided"
    win_themes: list[str] = Field(default_factory=list)
    customer_pain_points: list[str] = Field(default_factory=list)
    competitor_notes: str = ""
    partner_strategy: str = ""
    compliance_matrix: list[Any] = Field(default_factory=list)
    color_team_reviews: list[Any] = Field(default_factory=list)
    tasks: list[Any] = Field(default_factory=list)


class CapturePlanOut(CapturePlanIn):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProposalWorkspaceIn(BaseModel):
    opportunity_id: str
    title: str
    outline: list[Any] = Field(default_factory=list)
    compliance_matrix: list[Any] = Field(default_factory=list)
    required_attachments: list[Any] = Field(default_factory=list)
    tasks: list[Any] = Field(default_factory=list)
    budget: dict[str, Any] = Field(default_factory=dict)
    narrative_sections: list[Any] = Field(default_factory=list)
    internal_notes: str = ""


class ProposalWorkspaceUpdateIn(BaseModel):
    title: str | None = None
    outline: list[Any] | None = None
    compliance_matrix: list[Any] | None = None
    required_attachments: list[Any] | None = None
    tasks: list[Any] | None = None
    budget: dict[str, Any] | None = None
    narrative_sections: list[Any] | None = None
    internal_notes: str | None = None


class ProposalWorkspaceOut(ProposalWorkspaceIn):
    id: str
    tenant_id: str
    reviewer_comments: list[Any]
    version_history: list[Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LibraryItemIn(BaseModel):
    title: str
    category: str
    body: str = ""
    tags: list[str] = Field(default_factory=list)


class LibraryItemOut(LibraryItemIn):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BillingPlanOut(BaseModel):
    id: str
    name: str
    price_monthly: int
    price_annual: int
    seats: str
    blurb: str


class BillingUsageOut(BaseModel):
    users: int
    saved_opportunities: int
    proposal_workspaces: int


class BillingSummaryOut(BaseModel):
    plan: str
    subscription_status: str
    trial_end: datetime | None
    stripe_configured: bool
    stripe_customer_connected: bool
    limits: dict[str, int | None]
    usage: BillingUsageOut
    available_plans: list[BillingPlanOut]
