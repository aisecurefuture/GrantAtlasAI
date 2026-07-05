import Link from "next/link";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import { fetchContractDetail } from "@/lib/api";

export default async function ContractDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const detail = await fetchContractDetail(id);
  const { contract, score, capture_plan: capturePlan } = detail;
  return (
    <div className="stack">
      <Link className="toolbar muted" href="/contracts">
        <ArrowLeft size={16} />
        Back to contracts
      </Link>

      <div className="topbar">
        <div>
          <p className="eyebrow">{contract.source} · {contract.opportunity_type}</p>
          <h1>{contract.title}</h1>
          <p className="muted">{contract.department} · {contract.office}</p>
        </div>
        {score ? <div className="score">{Math.round(score.total_score)}</div> : null}
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Contract fit</h2>
          {score?.reasons.map((reason) => <p className="muted" key={reason}>{reason}</p>)}
          <div className="toolbar">
            <span className="pill high">{score?.recommended_action ?? "Watch"}</span>
            <span className="pill">NAICS {contract.naics_code ?? "TBD"}</span>
            <span className="pill">PSC {contract.classification_code ?? "TBD"}</span>
          </div>
        </div>
        <div className="card stack">
          <h2>Capture snapshot</h2>
          <p><strong>Response deadline:</strong> {contract.response_deadline ? new Date(contract.response_deadline).toLocaleDateString() : "TBD"}</p>
          <p><strong>Set-aside:</strong> {contract.set_aside ?? "None listed"}</p>
          <p><strong>Solicitation:</strong> {contract.solicitation_number ?? "TBD"}</p>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Win themes</h2>
          {(capturePlan?.win_themes ?? []).map((theme) => (
            <div className="toolbar" key={theme}><CheckCircle2 size={18} />{theme}</div>
          ))}
        </div>
        <div className="card stack">
          <h2>Partner strategy</h2>
          <p className="muted">{capturePlan?.partner_strategy ?? "No partner strategy captured yet."}</p>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Compliance matrix</h2>
          <table className="table">
            <tbody>
              {(capturePlan?.compliance_matrix ?? []).map((row) => (
                <tr key={row.requirement}>
                  <td>{row.requirement}</td>
                  <td>{row.owner}</td>
                  <td><span className="pill">{row.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="card stack">
          <h2>Color team reviews</h2>
          {(capturePlan?.color_team_reviews ?? []).map((review) => (
            <div className="toolbar" key={review.name}>
              <span className="pill">{review.status}</span>
              <strong>{review.name}</strong>
              <span className="muted">{review.due}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

