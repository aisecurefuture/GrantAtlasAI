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

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


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
