"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { apiSend, ApiError } from "@/lib/api";
import type { Opportunity, ProposalWorkspace } from "@/lib/types";

export type ActionState = { ok: boolean; error: string | null; message?: string };

const OK: ActionState = { ok: true, error: null };

function fail(error: unknown): ActionState {
  if (error instanceof ApiError) {
    if (error.status === 403) return { ok: false, error: "You don't have permission to do that." };
    return { ok: false, error: error.message };
  }
  return { ok: false, error: "Something went wrong. Please try again." };
}

function str(formData: FormData, key: string): string {
  return String(formData.get(key) ?? "").trim();
}

function list(formData: FormData, key: string): string[] {
  return str(formData, key)
    .split(/[\n,]/)
    .map((v) => v.trim())
    .filter(Boolean);
}

function intOrNull(formData: FormData, key: string): number | null {
  const raw = str(formData, key);
  if (!raw) return null;
  const n = Number(raw.replace(/[,$]/g, ""));
  return Number.isFinite(n) ? Math.round(n) : null;
}

// ---------------- Opportunities ----------------

export async function createOpportunityAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const title = str(formData, "title");
  if (!title) return { ok: false, error: "Title is required." };
  try {
    await apiSend<Opportunity>("/opportunities", "POST", {
      title,
      agency: str(formData, "agency"),
      source: str(formData, "source") || "Manual",
      close_date: str(formData, "close_date") || null,
      award_ceiling: intOrNull(formData, "award_ceiling"),
      eligibility: str(formData, "eligibility"),
      description: str(formData, "description"),
      categories: list(formData, "categories"),
      keywords: list(formData, "keywords"),
    });
    revalidatePath("/dashboard");
    return { ...OK, message: "Opportunity added and scored." };
  } catch (error) {
    return fail(error);
  }
}

export async function ingestGrantsGovAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const query = str(formData, "query");
  try {
    const imported = await apiSend<Opportunity[]>("/opportunities/ingest/grants-gov", "POST", undefined, { query });
    revalidatePath("/dashboard");
    return { ...OK, message: `Imported ${imported.length} opportunit${imported.length === 1 ? "y" : "ies"} from Grants.gov.` };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Contracts ----------------

export async function ingestSamGovAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const query = str(formData, "query");
  const naics = str(formData, "naics");
  try {
    const imported = await apiSend<unknown[]>("/contracts/ingest/sam-gov", "POST", undefined, {
      query,
      naics: naics || undefined,
    });
    revalidatePath("/contracts");
    return { ...OK, message: `Imported ${imported.length} contract opportunit${imported.length === 1 ? "y" : "ies"} from SAM.gov.` };
  } catch (error) {
    return fail(error);
  }
}

export async function createContractAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const title = str(formData, "title");
  if (!title) return { ok: false, error: "Title is required." };
  try {
    await apiSend("/contracts", "POST", {
      title,
      source: "Manual",
      department: str(formData, "department"),
      response_deadline: str(formData, "response_deadline") || null,
      opportunity_type: str(formData, "opportunity_type"),
      naics_code: str(formData, "naics_code") || null,
      classification_code: str(formData, "classification_code") || null,
      set_aside: str(formData, "set_aside") || null,
    });
    revalidatePath("/contracts");
    return { ...OK, message: "Contract opportunity added and scored." };
  } catch (error) {
    return fail(error);
  }
}

export async function saveCapturePlanAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const contractId = str(formData, "contract_id");
  if (!contractId) return { ok: false, error: "Missing contract reference." };
  try {
    await apiSend(`/contracts/${contractId}/capture-plan`, "POST", {
      contract_opportunity_id: contractId,
      status: str(formData, "status") || "Qualifying",
      bid_decision: str(formData, "bid_decision") || "Undecided",
      win_themes: list(formData, "win_themes"),
      customer_pain_points: list(formData, "customer_pain_points"),
      partner_strategy: str(formData, "partner_strategy"),
    });
    revalidatePath(`/contracts/${contractId}`);
    return { ...OK, message: "Capture plan saved." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Organization ----------------

export async function saveOrganizationAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const organization_name = str(formData, "organization_name");
  if (!organization_name) return { ok: false, error: "Organization name is required." };
  try {
    await apiSend("/organization/profile", "PUT", {
      organization_name,
      ein: str(formData, "ein") || null,
      uei: str(formData, "uei") || null,
      sam_status: str(formData, "sam_status") || null,
      grants_gov_status: str(formData, "grants_gov_status") || null,
      nonprofit_status: str(formData, "nonprofit_status") || null,
      mission: str(formData, "mission"),
      vision: str(formData, "vision"),
      programs: list(formData, "programs"),
      focus_areas: list(formData, "focus_areas"),
      geographic_service_area: str(formData, "geographic_service_area"),
      target_populations: list(formData, "target_populations"),
      past_performance: str(formData, "past_performance"),
    });
    revalidatePath("/organization");
    revalidatePath("/dashboard");
    return { ...OK, message: "Organization profile saved. New scores will use this profile." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Library ----------------

export async function createLibraryItemAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const title = str(formData, "title");
  const category = str(formData, "category");
  if (!title || !category) return { ok: false, error: "Title and category are required." };
  try {
    await apiSend("/library", "POST", {
      title,
      category,
      body: str(formData, "body"),
      tags: list(formData, "tags"),
    });
    revalidatePath("/library");
    return { ...OK, message: "Content saved to your library." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Partners ----------------

export async function createPartnerAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const name = str(formData, "name");
  if (!name) return { ok: false, error: "Partner name is required." };
  try {
    await apiSend("/partners", "POST", {
      name,
      partner_type: str(formData, "partner_type") || "Subcontractor",
      uei: str(formData, "uei") || null,
      capabilities: list(formData, "capabilities"),
      naics_codes: list(formData, "naics_codes"),
      set_aside_statuses: list(formData, "set_aside_statuses"),
      contact_name: str(formData, "contact_name") || null,
      contact_email: str(formData, "contact_email") || null,
      notes: str(formData, "notes"),
    });
    revalidatePath("/partners");
    return { ...OK, message: "Partner added to your teaming network." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Past performance ----------------

export async function createPastPerformanceAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const project_name = str(formData, "project_name");
  if (!project_name) return { ok: false, error: "Project name is required." };
  try {
    await apiSend("/past-performance", "POST", {
      project_name,
      customer: str(formData, "customer"),
      contract_number: str(formData, "contract_number") || null,
      naics_codes: list(formData, "naics_codes"),
      classification_codes: list(formData, "classification_codes"),
      value: intOrNull(formData, "value"),
      summary: str(formData, "summary"),
      outcomes: list(formData, "outcomes"),
    });
    revalidatePath("/past-performance");
    return { ...OK, message: "Past performance record added." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Proposals ----------------

export async function createProposalAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const opportunity_id = str(formData, "opportunity_id");
  const title = str(formData, "title");
  if (!opportunity_id) return { ok: false, error: "Choose an opportunity to build a proposal for." };
  if (!title) return { ok: false, error: "Proposal title is required." };
  let created: ProposalWorkspace;
  try {
    created = await apiSend<ProposalWorkspace>("/proposals", "POST", {
      opportunity_id,
      title,
      outline: [
        { heading: "Executive Summary", status: "Not started" },
        { heading: "Statement of Need", status: "Not started" },
        { heading: "Project Design & Methodology", status: "Not started" },
        { heading: "Organizational Capacity", status: "Not started" },
        { heading: "Budget & Budget Narrative", status: "Not started" },
        { heading: "Evaluation Plan", status: "Not started" },
      ],
    });
  } catch (error) {
    return fail(error);
  }
  revalidatePath("/proposals");
  redirect(`/proposals/${created.id}`);
}

// ---------------- AI analysis ----------------

export async function generateOpportunityNarrativeAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const id = str(formData, "opportunity_id");
  if (!id) return { ok: false, error: "Missing opportunity reference." };
  try {
    await apiSend(`/opportunities/${id}/ai-narrative`, "POST");
    revalidatePath(`/opportunities/${id}`);
    return { ...OK, message: "AI analysis generated." };
  } catch (error) {
    return fail(error);
  }
}

export async function generateContractNarrativeAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const id = str(formData, "contract_id");
  if (!id) return { ok: false, error: "Missing contract reference." };
  try {
    await apiSend(`/contracts/${id}/ai-narrative`, "POST");
    revalidatePath(`/contracts/${id}`);
    return { ...OK, message: "AI analysis generated." };
  } catch (error) {
    return fail(error);
  }
}

// ---------------- Billing ----------------

export async function startCheckoutAction(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const plan = str(formData, "plan");
  if (!plan) return { ok: false, error: "Choose a plan." };
  let url: string;
  try {
    const result = await apiSend<{ url: string }>("/billing/checkout", "POST", undefined, { plan });
    url = result.url;
  } catch (error) {
    return fail(error);
  }
  redirect(url);
}

export async function openBillingPortalAction(_prev: ActionState, _formData: FormData): Promise<ActionState> {
  let url: string;
  try {
    const result = await apiSend<{ url: string }>("/billing/portal", "POST");
    url = result.url;
  } catch (error) {
    return fail(error);
  }
  redirect(url);
}
