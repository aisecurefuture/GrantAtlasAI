import "server-only";
import { getSession } from "./session";
import type {
  CapturePlan,
  ContractDetail,
  ContractOpportunity,
  LibraryItem,
  OrganizationProfile,
  Opportunity,
  OpportunityDetail,
  PastPerformanceProject,
  ProposalWorkspace,
  TeamingPartner,
  TenantSummary,
  UsageSummary,
} from "./types";

/**
 * Server-to-server base URL. Inside Docker the web container reaches the API at
 * http://api:8000; locally it is http://localhost:8000. This is never exposed to
 * the browser — all data fetching happens in server components / server actions.
 */
const API_BASE_URL = process.env.API_SERVER_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

type FetchOptions = {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  cache?: RequestCache;
};

function buildUrl(path: string, query?: FetchOptions["query"]): string {
  const url = new URL(path.replace(/^\//, ""), API_BASE_URL.endsWith("/") ? API_BASE_URL : `${API_BASE_URL}/`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function apiRequest<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const session = await getSession();
  const headers: Record<string, string> = { Accept: "application/json" };
  if (session) headers.Authorization = `Bearer ${session.token}`;
  if (options.body !== undefined) headers["Content-Type"] = "application/json";

  let response: Response;
  try {
    response = await fetch(buildUrl(path, options.query), {
      method: options.method ?? "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      cache: options.cache ?? "no-store",
    });
  } catch {
    throw new ApiError(0, "The GrantAtlas API is unreachable. Please try again shortly.");
  }

  if (response.status === 204) return undefined as T;

  const text = await response.text();
  const data = text ? safeJson(text) : null;

  if (!response.ok) {
    let detail = response.statusText || "Request failed";
    if (data && typeof data === "object" && "detail" in data) {
      const d = (data as { detail?: unknown }).detail;
      if (typeof d === "string" && d) detail = d;
    }
    throw new ApiError(response.status, detail);
  }
  return data as T;
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// ---- Reads (server components) ----

export const getOpportunities = (query?: { q?: string; status?: string; source?: string }) =>
  apiRequest<Opportunity[]>("/opportunities", { query });

export const getOpportunity = (id: string) => apiRequest<OpportunityDetail>(`/opportunities/${id}`);

export const getContracts = (query?: { q?: string; status?: string; naics?: string }) =>
  apiRequest<ContractOpportunity[]>("/contracts", { query });

export const getContract = (id: string) => apiRequest<ContractDetail>(`/contracts/${id}`);

export const getOrganizationProfile = () => apiRequest<OrganizationProfile>("/organization/profile");

export const getLibraryItems = () => apiRequest<LibraryItem[]>("/library");

export const getPartners = () => apiRequest<TeamingPartner[]>("/partners");

export const getPastPerformance = () => apiRequest<PastPerformanceProject[]>("/past-performance");

export const getProposals = () => apiRequest<ProposalWorkspace[]>("/proposals");

export const getProposal = (id: string) => apiRequest<ProposalWorkspace>(`/proposals/${id}`);

export const getBillingSummary = () => apiRequest<import("./types").BillingSummary>("/billing/summary");

export const getAdminTenants = () => apiRequest<TenantSummary[]>("/admin/tenants");

export const getAdminUsage = () => apiRequest<UsageSummary>("/admin/usage");

// ---- Writes (server actions) ----

export const apiSend = <T>(path: string, method: string, body?: unknown, query?: FetchOptions["query"]) =>
  apiRequest<T>(path, { method, body, query });

export type { CapturePlan };
