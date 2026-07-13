export type Opportunity = {
  id: string;
  tenant_id: string;
  title: string;
  agency: string;
  source: string;
  source_url: string | null;
  opportunity_number: string | null;
  assistance_listing: string | null;
  posted_date: string | null;
  close_date: string | null;
  award_floor: number | null;
  award_ceiling: number | null;
  expected_awards: number | null;
  eligibility: string;
  cost_share_required: boolean;
  required_partners: string;
  description: string;
  categories: string[];
  keywords: string[];
  status: string;
  last_updated_at: string;
  created_at: string;
  fit_score?: number | null;
  recommended_action?: string | null;
};

export type Score = {
  total_score: number;
  mission_fit: number;
  eligibility_fit: number;
  deadline_urgency: number;
  funding_size: number;
  proposal_complexity: number;
  partnership_fit: number;
  past_performance_fit: number;
  strategic_value: number;
  probability_of_success: number;
  recommended_action: string;
  reasons: string[];
  ai_narrative?: string | null;
};

export type OpportunityDetail = {
  opportunity: Opportunity;
  score: Score | null;
};

export type ContractOpportunity = {
  id: string;
  tenant_id: string;
  title: string;
  source: string;
  notice_id: string | null;
  solicitation_number: string | null;
  department: string;
  subtier: string;
  office: string;
  posted_date: string | null;
  response_deadline: string | null;
  opportunity_type: string;
  set_aside: string | null;
  set_aside_code: string | null;
  naics_code: string | null;
  classification_code: string | null;
  ui_link: string | null;
  status: string;
  last_updated_at: string;
  created_at: string;
  fit_score?: number | null;
  recommended_action?: string | null;
};

export type ContractScore = {
  total_score: number;
  naics_fit: number;
  psc_fit: number;
  past_performance_fit: number;
  set_aside_fit: number;
  deadline_fit: number;
  competition_fit: number;
  strategic_value: number;
  recommended_action: string;
  reasons: string[];
  ai_narrative?: string | null;
};

export type ComplianceRow = { requirement: string; owner: string; status: string };
export type ColorTeamReview = { name: string; due: string; status: string };
export type TaskItem = { title: string; status: string };

export type CapturePlan = {
  id: string;
  tenant_id: string;
  contract_opportunity_id: string;
  status: string;
  bid_decision: string;
  win_themes: string[];
  customer_pain_points: string[];
  competitor_notes: string;
  partner_strategy: string;
  compliance_matrix: ComplianceRow[];
  color_team_reviews: ColorTeamReview[];
  tasks: TaskItem[];
  created_at: string;
  updated_at: string;
};

export type ContractDetail = {
  contract: ContractOpportunity;
  score: ContractScore | null;
  capture_plan: CapturePlan | null;
};

export type OrganizationProfile = {
  id: string;
  tenant_id: string;
  organization_name: string;
  ein: string | null;
  uei: string | null;
  sam_status: string | null;
  grants_gov_status: string | null;
  nonprofit_status: string | null;
  mission: string;
  vision: string;
  programs: string[];
  focus_areas: string[];
  geographic_service_area: string;
  target_populations: string[];
  past_performance: string;
  key_staff_bios: Array<Record<string, unknown>>;
  updated_at: string;
};

export type LibraryItem = {
  id: string;
  tenant_id: string;
  title: string;
  category: string;
  body: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type TeamingPartner = {
  id: string;
  tenant_id: string;
  name: string;
  partner_type: string;
  uei: string | null;
  capabilities: string[];
  naics_codes: string[];
  set_aside_statuses: string[];
  contact_name: string | null;
  contact_email: string | null;
  notes: string;
  created_at: string;
};

export type PastPerformanceProject = {
  id: string;
  tenant_id: string;
  project_name: string;
  customer: string;
  contract_number: string | null;
  naics_codes: string[];
  classification_codes: string[];
  value: number | null;
  start_date: string | null;
  end_date: string | null;
  summary: string;
  outcomes: string[];
  contact_reference: Record<string, unknown>;
  created_at: string;
};

export type ProposalOutlineSection = { heading: string; guidance?: string; status?: string };

export type ProposalWorkspace = {
  id: string;
  tenant_id: string;
  opportunity_id: string;
  title: string;
  outline: ProposalOutlineSection[];
  compliance_matrix: ComplianceRow[];
  required_attachments: string[];
  tasks: TaskItem[];
  budget: Record<string, unknown>;
  narrative_sections: Array<{ heading: string; content: string }>;
  internal_notes: string;
  reviewer_comments: Array<Record<string, unknown>>;
  version_history: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
};

export type TenantSummary = {
  id: string;
  name: string;
  slug: string;
  plan: string;
  subscription_status: string;
  trial_end: string | null;
  is_active?: boolean;
  user_count?: number;
  opportunity_count?: number;
};

export type TenantUser = {
  id: string;
  email: string;
  name: string;
  role: string;
  is_active: boolean;
  created_at: string;
};

export type UsageSummary = {
  tenants: number;
  users: number;
  opportunities: number;
  contract_opportunities: number;
  proposals: number;
  recent_audit_events: number;
};

export type OnboardingStep = {
  key: string;
  title: string;
  description: string;
  done: boolean;
  cta_label: string;
  cta_href: string;
};

export type OnboardingStatus = {
  steps: OnboardingStep[];
  completed: number;
  total: number;
  all_complete: boolean;
  dismissed: boolean;
  organization_name: string;
};

export type BillingSummary = {
  plan: string;
  subscription_status: string;
  trial_end: string | null;
  stripe_configured: boolean;
  stripe_customer_connected: boolean;
  limits: Record<string, number | null>;
  usage: { users: number; saved_opportunities: number; proposal_workspaces: number };
  available_plans: Array<{ id: string; name: string; price_monthly: number; price_annual: number; seats: string; blurb: string }>;
};
