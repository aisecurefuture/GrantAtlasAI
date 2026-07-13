import Link from "next/link";
import { Search, DownloadCloud } from "lucide-react";
import { OpportunityTable } from "@/components/OpportunityTable";
import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { OnboardingChecklist } from "@/components/OnboardingChecklist";
import { getOnboardingStatus, getOpportunities, getProposals } from "@/lib/api";
import { createOpportunityAction, ingestGrantsGovAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

function daysUntil(date: string | null): number | null {
  if (!date) return null;
  return Math.ceil((new Date(date).getTime() - Date.now()) / 86400000);
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; source?: string; status?: string }>;
}) {
  const params = await searchParams;
  const q = params.q ?? "";
  const source = params.source ?? "";
  const status = params.status ?? "";

  const [opportunities, proposals, onboarding] = await Promise.all([
    getOpportunities({ q, source, status }),
    getProposals().catch(() => []),
    getOnboardingStatus().catch(() => null),
  ]);

  const scored = opportunities.filter((o) => typeof o.fit_score === "number");
  const topFit = scored.length ? Math.round(Math.max(...scored.map((o) => o.fit_score as number))) : null;
  const applyCount = opportunities.filter((o) => o.recommended_action === "Apply").length;
  const closingSoon = opportunities.filter((o) => {
    const d = daysUntil(o.close_date);
    return d !== null && d >= 0 && d <= 30;
  }).length;

  return (
    <>
      {onboarding && !onboarding.dismissed ? <OnboardingChecklist status={onboarding} /> : null}
      <div className="topbar">
        <div>
          <p className="eyebrow">Funding intelligence</p>
          <h1>Pipeline</h1>
        </div>
        <div className="toolbar">
          <Disclosure label="Import Grants.gov" variant="secondary">
            <h3>Import from Grants.gov</h3>
            <p className="muted">
              Pulls live opportunities and scores each one against your organization profile. Use a single broad
              keyword — leaving it empty searches all recently posted grants.
            </p>
            <ActionForm
              action={ingestGrantsGovAction}
              submitLabel="Import & score"
              pendingLabel="Importing from Grants.gov… (can take up to a minute)"
            >
              <label className="field">
                <span className="field-label">Keyword (optional)</span>
                <input className="input" name="query" placeholder="e.g. cybersecurity" />
              </label>
            </ActionForm>
          </Disclosure>
          <Disclosure label="Add opportunity">
            <h3>Add opportunity manually</h3>
            <ActionForm action={createOpportunityAction} submitLabel="Add & score">
              <label className="field">
                <span className="field-label">Title *</span>
                <input className="input" name="title" required />
              </label>
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">Agency / funder</span>
                  <input className="input" name="agency" />
                </label>
                <label className="field">
                  <span className="field-label">Close date</span>
                  <input className="input" type="date" name="close_date" />
                </label>
              </div>
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">Award ceiling ($)</span>
                  <input className="input" name="award_ceiling" inputMode="numeric" placeholder="250000" />
                </label>
                <label className="field">
                  <span className="field-label">Categories (comma-separated)</span>
                  <input className="input" name="categories" placeholder="Education, Cybersecurity" />
                </label>
              </div>
              <label className="field">
                <span className="field-label">Eligibility</span>
                <textarea className="textarea" name="eligibility" rows={2} />
              </label>
              <label className="field">
                <span className="field-label">Description</span>
                <textarea className="textarea" name="description" rows={3} />
              </label>
            </ActionForm>
          </Disclosure>
        </div>
      </div>

      <section className="grid cols-4">
        <div className="card metric">
          <span className="muted">Top fit score</span>
          <strong>{topFit ?? "—"}</strong>
          <span className="pill high">{applyCount} Apply</span>
        </div>
        <div className="card metric">
          <span className="muted">Closing in 30 days</span>
          <strong>{closingSoon}</strong>
          <span className="pill medium">Deadlines</span>
        </div>
        <div className="card metric">
          <span className="muted">Tracked opportunities</span>
          <strong>{opportunities.length}</strong>
          <span className="pill">Pipeline</span>
        </div>
        <div className="card metric">
          <span className="muted">Active proposals</span>
          <strong>{proposals.length}</strong>
          <span className="pill">Workspaces</span>
        </div>
      </section>

      <div className="section-head" style={{ marginTop: 28 }}>
        <div>
          <h2>Grant opportunities</h2>
          <p className="muted" style={{ margin: "4px 0 0" }}>
            Grants.gov and manual entries. Looking for federal contracts?{" "}
            <Link href="/contracts">SAM.gov contract opportunities →</Link>
          </p>
        </div>
        <form className="toolbar" method="get">
          <div className="input toolbar" style={{ padding: "0 12px" }}>
            <Search size={16} />
            <input
              name="q"
              defaultValue={q}
              placeholder="Keyword, agency, eligibility"
              aria-label="Search opportunities"
              style={{ border: 0, outline: "none", minHeight: 38, background: "transparent" }}
            />
          </div>
          <select className="select" name="source" defaultValue={source} aria-label="Source">
            <option value="">All sources</option>
            <option value="Grants.gov">Grants.gov</option>
            <option value="Manual">Manual</option>
          </select>
          <button className="button secondary" type="submit">
            <DownloadCloud size={16} />
            Apply filters
          </button>
        </form>
      </div>
      <OpportunityTable opportunities={opportunities} />
    </>
  );
}
