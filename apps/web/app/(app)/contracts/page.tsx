import Link from "next/link";
import { BriefcaseBusiness, Filter, Search } from "lucide-react";
import { fetchContracts } from "@/lib/api";

export default async function ContractsPage() {
  const contracts = await fetchContracts();
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">V2 capture management</p>
          <h1>Contract opportunities</h1>
        </div>
        <div className="toolbar">
          <button className="button secondary" title="Filter contracts">
            <Filter size={18} />
            Filter
          </button>
          <button className="button" title="Import from SAM.gov">
            <BriefcaseBusiness size={18} />
            SAM.gov
          </button>
        </div>
      </div>

      <section className="grid cols-4">
        <div className="card metric"><span className="muted">Pursue</span><strong>1</strong><span className="pill high">High fit</span></div>
        <div className="card metric"><span className="muted">Team</span><strong>1</strong><span className="pill medium">Partner-led</span></div>
        <div className="card metric"><span className="muted">NAICS matches</span><strong>2</strong><span className="pill">611430</span></div>
        <div className="card metric"><span className="muted">Reviews</span><strong>2</strong><span className="pill">Planned</span></div>
      </section>

      <div className="section-head">
        <h2>SAM.gov pipeline</h2>
        <div className="input toolbar">
          <Search size={16} />
          <span className="muted">Title, agency, NAICS, PSC</span>
        </div>
      </div>

      <section className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Opportunity</th>
              <th>NAICS</th>
              <th>PSC</th>
              <th>Deadline</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {contracts.map((contract) => (
              <tr key={contract.id}>
                <td>
                  <Link href={`/contracts/${contract.id}`}><strong>{contract.title}</strong></Link>
                  <div className="muted">{contract.department}</div>
                </td>
                <td>{contract.naics_code ?? "TBD"}</td>
                <td>{contract.classification_code ?? "TBD"}</td>
                <td>{contract.response_deadline ? new Date(contract.response_deadline).toLocaleDateString() : "TBD"}</td>
                <td><span className="pill">{contract.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
