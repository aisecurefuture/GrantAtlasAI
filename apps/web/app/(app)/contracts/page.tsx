import Link from "next/link";
import { Search } from "lucide-react";
import { getContracts } from "@/lib/api";
import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { ingestSamGovAction, createContractAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

function fitClass(v: number | null | undefined) {
  if (typeof v !== "number") return "";
  if (v >= 78) return "high";
  if (v >= 55) return "medium";
  return "low";
}

export default async function ContractsPage({ searchParams }: { searchParams: Promise<{ q?: string; naics?: string }> }) {
  const params = await searchParams;
  const q = params.q ?? "";
  const naics = params.naics ?? "";
  const contracts = await getContracts({ q, naics });

  const pursue = contracts.filter((c) => c.recommended_action === "Pursue").length;
  const team = contracts.filter((c) => c.recommended_action === "Team").length;
  const naicsMatches = new Set(contracts.map((c) => c.naics_code).filter(Boolean)).size;

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Contract capture (SAM.gov)</p>
          <h1>Contract opportunities</h1>
        </div>
        <div className="toolbar">
          <Disclosure label="Import SAM.gov" variant="secondary">
            <h3>Import from SAM.gov</h3>
            <p className="muted">Requires a configured SAM.gov API key. Scores each contract on NAICS/PSC fit and your past performance.</p>
            <ActionForm action={ingestSamGovAction} submitLabel="Import & score">
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">Title keyword</span>
                  <input className="input" name="query" placeholder="cybersecurity" />
                </label>
                <label className="field">
                  <span className="field-label">NAICS (optional)</span>
                  <input className="input" name="naics" placeholder="611430" />
                </label>
              </div>
            </ActionForm>
          </Disclosure>
          <Disclosure label="Add contract">
            <h3>Add a contract opportunity</h3>
            <ActionForm action={createContractAction} submitLabel="Add & score">
              <label className="field">
                <span className="field-label">Title *</span>
                <input className="input" name="title" required />
              </label>
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">Department / agency</span>
                  <input className="input" name="department" />
                </label>
                <label className="field">
                  <span className="field-label">Response deadline</span>
                  <input className="input" type="date" name="response_deadline" />
                </label>
              </div>
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">NAICS</span>
                  <input className="input" name="naics_code" placeholder="611430" />
                </label>
                <label className="field">
                  <span className="field-label">PSC / classification</span>
                  <input className="input" name="classification_code" placeholder="U008" />
                </label>
              </div>
              <label className="field">
                <span className="field-label">Set-aside</span>
                <input className="input" name="set_aside" placeholder="Small Business" />
              </label>
            </ActionForm>
          </Disclosure>
        </div>
      </div>

      <section className="grid cols-4">
        <div className="card metric"><span className="muted">Pursue</span><strong>{pursue}</strong><span className="pill high">High fit</span></div>
        <div className="card metric"><span className="muted">Team</span><strong>{team}</strong><span className="pill medium">Partner-led</span></div>
        <div className="card metric"><span className="muted">Tracked</span><strong>{contracts.length}</strong><span className="pill">Contracts</span></div>
        <div className="card metric"><span className="muted">NAICS codes</span><strong>{naicsMatches}</strong><span className="pill">Distinct</span></div>
      </section>

      <div className="section-head">
        <h2>Capture pipeline</h2>
        <form className="toolbar" method="get">
          <div className="input toolbar" style={{ padding: "0 12px" }}>
            <Search size={16} />
            <input
              name="q"
              defaultValue={q}
              placeholder="Title, agency, NAICS"
              aria-label="Search contracts"
              style={{ border: 0, outline: "none", minHeight: 38, background: "transparent" }}
            />
          </div>
          <button className="button secondary" type="submit">Search</button>
        </form>
      </div>

      {contracts.length === 0 ? (
        <div className="card empty-state">
          <p>No contract opportunities yet.</p>
          <p className="muted">Import from SAM.gov (needs an API key) or add one manually.</p>
        </div>
      ) : (
        <section className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Opportunity</th>
                <th>NAICS</th>
                <th>PSC</th>
                <th>Deadline</th>
                <th>Status</th>
                <th>Fit</th>
              </tr>
            </thead>
            <tbody>
              {contracts.map((contract) => {
                const fit = typeof contract.fit_score === "number" ? Math.round(contract.fit_score) : null;
                return (
                  <tr key={contract.id}>
                    <td>
                      <Link href={`/contracts/${contract.id}`}><strong>{contract.title}</strong></Link>
                      <div className="muted">{contract.department || "Agency TBD"}</div>
                    </td>
                    <td>{contract.naics_code ?? "—"}</td>
                    <td>{contract.classification_code ?? "—"}</td>
                    <td>{contract.response_deadline ? new Date(contract.response_deadline).toLocaleDateString() : "TBD"}</td>
                    <td><span className="pill">{contract.recommended_action ?? contract.status}</span></td>
                    <td>{fit === null ? <span className="pill">—</span> : <span className={`pill ${fitClass(fit)}`}>{fit}</span>}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
