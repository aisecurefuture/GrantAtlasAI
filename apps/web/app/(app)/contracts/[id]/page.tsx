import Link from "next/link";
import { ArrowLeft, CheckCircle2, Sparkles } from "lucide-react";
import { getContract } from "@/lib/api";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { generateContractNarrativeAction, saveCapturePlanAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

const CAPTURE_STATUSES = ["Watching", "Qualifying", "Pursuing", "Proposing", "Submitted", "No Bid"];

export default async function ContractDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { contract, score, capture_plan: capturePlan } = await getContract(id);

  return (
    <div className="stack">
      <Link className="toolbar muted" href="/contracts">
        <ArrowLeft size={16} />
        Back to contracts
      </Link>

      <div className="topbar">
        <div>
          <p className="eyebrow">{contract.source} · {contract.opportunity_type || "Contract"}</p>
          <h1>{contract.title}</h1>
          <p className="muted">{[contract.department, contract.office].filter(Boolean).join(" · ") || "Agency TBD"}</p>
        </div>
        {score ? (
          <div className="score-block">
            <div className="score">{Math.round(score.total_score)}</div>
            <span className="pill high">{score.recommended_action}</span>
          </div>
        ) : null}
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Why this score</h2>
          {score ? (
            <>
              {score.ai_narrative ? (
                <div className="ai-narrative">
                  <span className="ai-tag"><Sparkles size={14} /> AI analysis</span>
                  <p>{score.ai_narrative}</p>
                </div>
              ) : null}
              <ul className="reasons">
                {score.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <ActionForm
                action={generateContractNarrativeAction}
                submitLabel={score.ai_narrative ? "Regenerate AI analysis" : "Generate AI analysis"}
                hidden={{ contract_id: id }}
                resetOnSuccess={false}
              >
                <span />
              </ActionForm>
            </>
          ) : (
            <p className="muted">Add past performance and an organization profile to score this contract.</p>
          )}
        </div>
        <div className="card stack">
          <h2>Score breakdown</h2>
          {score ? (
            <ScoreBreakdown
              rows={[
                { label: "NAICS fit", value: score.naics_fit },
                { label: "PSC fit", value: score.psc_fit },
                { label: "Past performance", value: score.past_performance_fit },
                { label: "Set-aside fit", value: score.set_aside_fit },
                { label: "Deadline runway", value: score.deadline_fit },
                { label: "Competition", value: score.competition_fit },
                { label: "Strategic value", value: score.strategic_value },
              ]}
            />
          ) : (
            <p className="muted">Breakdown appears once scored.</p>
          )}
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Solicitation</h2>
          <p><strong>Response deadline:</strong> {contract.response_deadline ? new Date(contract.response_deadline).toLocaleDateString() : "TBD"}</p>
          <p><strong>Set-aside:</strong> {contract.set_aside ?? "None listed"}</p>
          <p><strong>Solicitation #:</strong> {contract.solicitation_number ?? "TBD"}</p>
          <p><strong>NAICS / PSC:</strong> {contract.naics_code ?? "—"} / {contract.classification_code ?? "—"}</p>
          {contract.ui_link ? (
            <a className="button secondary" href={contract.ui_link} target="_blank" rel="noreferrer">View on SAM.gov</a>
          ) : null}
        </div>
        <div className="card stack">
          <h2>Capture plan</h2>
          <p><strong>Status:</strong> {capturePlan?.status ?? "Not started"}</p>
          <p><strong>Bid decision:</strong> {capturePlan?.bid_decision ?? "Undecided"}</p>
          {capturePlan?.win_themes?.length ? (
            <div className="stack" style={{ gap: 6 }}>
              {capturePlan.win_themes.map((theme) => (
                <div className="toolbar" key={theme}><CheckCircle2 size={16} />{theme}</div>
              ))}
            </div>
          ) : (
            <p className="muted">No win themes captured yet.</p>
          )}
          {capturePlan?.partner_strategy ? <p className="muted">{capturePlan.partner_strategy}</p> : null}
          <Disclosure label={capturePlan ? "Update capture plan" : "Start capture plan"}>
            <h3>Capture plan</h3>
            <ActionForm action={saveCapturePlanAction} submitLabel="Save capture plan" hidden={{ contract_id: id }} resetOnSuccess={false}>
              <div className="grid cols-2">
                <label className="field">
                  <span className="field-label">Status</span>
                  <select className="select" name="status" defaultValue={capturePlan?.status ?? "Qualifying"}>
                    {CAPTURE_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </label>
                <label className="field">
                  <span className="field-label">Bid decision</span>
                  <select className="select" name="bid_decision" defaultValue={capturePlan?.bid_decision ?? "Undecided"}>
                    <option>Undecided</option>
                    <option>Bid</option>
                    <option>No Bid</option>
                  </select>
                </label>
              </div>
              <label className="field">
                <span className="field-label">Win themes (one per line)</span>
                <textarea className="textarea" name="win_themes" rows={3} defaultValue={(capturePlan?.win_themes ?? []).join("\n")} />
              </label>
              <label className="field">
                <span className="field-label">Customer pain points (one per line)</span>
                <textarea className="textarea" name="customer_pain_points" rows={2} defaultValue={(capturePlan?.customer_pain_points ?? []).join("\n")} />
              </label>
              <label className="field">
                <span className="field-label">Partner strategy</span>
                <textarea className="textarea" name="partner_strategy" rows={2} defaultValue={capturePlan?.partner_strategy ?? ""} />
              </label>
            </ActionForm>
          </Disclosure>
        </div>
      </section>
    </div>
  );
}
