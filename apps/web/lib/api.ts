import type { ContractDetail, ContractOpportunity, Opportunity, OpportunityDetail } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const sampleOpportunities: Opportunity[] = [
  {
    id: "seed-tech-001",
    title: "Community Technology Education Capacity Grant",
    agency: "Manual Seed Funder",
    source: "Manual",
    close_date: new Date(Date.now() + 35 * 86400000).toISOString(),
    award_ceiling: 250000,
    eligibility: "Eligible applicants include nonprofit organizations and education institutions.",
    description: "Supports nonprofit cybersecurity education, AI literacy, student mentorship, and workforce development.",
    categories: ["Education", "Cybersecurity"],
    keywords: ["AI literacy", "cybersecurity", "workforce"],
    status: "New"
  },
  {
    id: "seed-ai-002",
    title: "Responsible AI Adoption for Educators",
    agency: "Foundation Preview",
    source: "Manual",
    close_date: new Date(Date.now() + 14 * 86400000).toISOString(),
    award_ceiling: 100000,
    eligibility: "Nonprofit and university partners may apply.",
    description: "Funds teacher AI literacy, curriculum development, and community safety workshops.",
    categories: ["AI literacy"],
    keywords: ["teachers", "responsible AI"],
    status: "Monitoring"
  }
];

export async function fetchOpportunities(token?: string): Promise<Opportunity[]> {
  if (!token) return sampleOpportunities;
  try {
    const response = await fetch(`${API_BASE_URL}/opportunities`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store"
    });
    if (!response.ok) return sampleOpportunities;
    return response.json();
  } catch {
    return sampleOpportunities;
  }
}

export async function fetchOpportunityDetail(id: string, token?: string): Promise<OpportunityDetail> {
  if (!token) {
    return {
      opportunity: sampleOpportunities.find((item) => item.id === id) ?? sampleOpportunities[0],
      score: {
        total_score: 86,
        mission_fit: 92,
        eligibility_fit: 84,
        deadline_urgency: 80,
        funding_size: 75,
        proposal_complexity: 85,
        partnership_fit: 85,
        past_performance_fit: 82,
        strategic_value: 88,
        probability_of_success: 81,
        recommended_action: "Apply",
        reasons: [
          "Mission overlap found for AI literacy, cybersecurity, education, and nonprofit.",
          "Eligibility language appears compatible with nonprofit or education applicants.",
          "Deadline is approaching within 45 days.",
          "Recommended action: Apply based on a transparent rules score of 86."
        ]
      }
    };
  }
  const response = await fetch(`${API_BASE_URL}/opportunities/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store"
  });
  if (!response.ok) throw new Error("Opportunity not found");
  return response.json();
}

export const sampleContracts: ContractOpportunity[] = [
  {
    id: "seed-sam-001",
    title: "Cybersecurity and AI Literacy Training Support",
    source: "Manual",
    notice_id: "SEED-SAM-001",
    solicitation_number: "FAKE-TRAINING-001",
    department: "Department of Education",
    subtier: "Office of Career, Technical, and Adult Education",
    office: "Program Support Office",
    response_deadline: new Date(Date.now() + 28 * 86400000).toISOString(),
    opportunity_type: "Sources Sought",
    set_aside: "Small Business",
    naics_code: "611430",
    classification_code: "U008",
    ui_link: "https://sam.gov/",
    status: "Qualifying"
  },
  {
    id: "seed-sam-002",
    title: "Nonprofit Cyber Resilience Technical Assistance",
    source: "SAM.gov",
    notice_id: "DEMO-SAM-002",
    solicitation_number: "DEMO-TA-002",
    department: "Department of Homeland Security",
    subtier: "Cybersecurity and Infrastructure Security Agency",
    office: "Acquisition Office",
    response_deadline: new Date(Date.now() + 41 * 86400000).toISOString(),
    opportunity_type: "Solicitation",
    set_aside: null,
    naics_code: "541519",
    classification_code: "D399",
    ui_link: "https://sam.gov/",
    status: "Watching"
  }
];

export async function fetchContracts(token?: string): Promise<ContractOpportunity[]> {
  if (!token) return sampleContracts;
  try {
    const response = await fetch(`${API_BASE_URL}/contracts`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store"
    });
    if (!response.ok) return sampleContracts;
    return response.json();
  } catch {
    return sampleContracts;
  }
}

export async function fetchContractDetail(id: string, token?: string): Promise<ContractDetail> {
  if (!token) {
    return {
      contract: sampleContracts.find((item) => item.id === id) ?? sampleContracts[0],
      score: {
        total_score: 84,
        naics_fit: 90,
        psc_fit: 88,
        past_performance_fit: 86,
        set_aside_fit: 70,
        deadline_fit: 82,
        competition_fit: 80,
        strategic_value: 84,
        recommended_action: "Pursue",
        reasons: [
          "Direct past performance match on NAICS 611430.",
          "Past performance includes PSC/classification U008.",
          "Response deadline has workable capture/proposal runway.",
          "Recommended action: Pursue based on v2 contract scoring score of 84."
        ]
      },
      capture_plan: {
        id: "capture-seed",
        status: "Qualifying",
        bid_decision: "Undecided",
        win_themes: ["Responsible AI literacy", "Cybersecurity education", "Veteran workforce pathway"],
        customer_pain_points: ["Practical training need", "Safe AI adoption", "Measurable workforce outcomes"],
        partner_strategy: "Validate small-business eligibility and consider teaming with Veteran Cyber Workforce Alliance.",
        compliance_matrix: [
          { requirement: "Training capability", owner: "Grant Writer", status: "Mapped" },
          { requirement: "Past performance", owner: "Owner", status: "Draft" }
        ],
        color_team_reviews: [
          { name: "Pink Team", due: "T-14 days", status: "Planned" },
          { name: "Red Team", due: "T-5 days", status: "Planned" }
        ],
        tasks: [
          { title: "Confirm set-aside eligibility", status: "To do" },
          { title: "Draft capability statement", status: "Drafting" }
        ]
      }
    };
  }
  const response = await fetch(`${API_BASE_URL}/contracts/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store"
  });
  if (!response.ok) throw new Error("Contract opportunity not found");
  return response.json();
}
