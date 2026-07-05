export type Opportunity = {
  id: string;
  title: string;
  agency: string;
  source: string;
  close_date: string | null;
  award_ceiling: number | null;
  eligibility: string;
  description: string;
  categories: string[];
  keywords: string[];
  status: string;
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
};

export type OpportunityDetail = {
  opportunity: Opportunity;
  score: Score | null;
};

export type ContractOpportunity = {
  id: string;
  title: string;
  source: string;
  notice_id: string | null;
  solicitation_number: string | null;
  department: string;
  subtier: string;
  office: string;
  response_deadline: string | null;
  opportunity_type: string;
  set_aside: string | null;
  naics_code: string | null;
  classification_code: string | null;
  ui_link: string | null;
  status: string;
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
};

export type CapturePlan = {
  id: string;
  status: string;
  bid_decision: string;
  win_themes: string[];
  customer_pain_points: string[];
  partner_strategy: string;
  compliance_matrix: Array<{ requirement: string; owner: string; status: string }>;
  color_team_reviews: Array<{ name: string; due: string; status: string }>;
  tasks: Array<{ title: string; status: string }>;
};

export type ContractDetail = {
  contract: ContractOpportunity;
  score: ContractScore | null;
  capture_plan: CapturePlan | null;
};
