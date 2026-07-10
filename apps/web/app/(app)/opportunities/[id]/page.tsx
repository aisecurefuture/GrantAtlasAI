import { ArrowLeft, Sparkles } from "lucide-react";
import Link from "next/link";
import { getOpportunity } from "@/lib/api";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { ActionForm } from "@/components/ActionForm";
import { createProposalAction, generateOpportunityNarrativeAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

function actionClass(action?: string) {
  if (action === "Apply") return "high";
  if (action === "Skip") return "low";
  return "medium";
}

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { opportunity, score } = await getOpportunity(id);

  return (
    <div className="stack">
      <Link className="toolbar muted" href="/dashboard">
        <ArrowLeft size={16} />
        Back to pipeline
      </Link>
      <div className="topbar">
        <div>
          <p className="eyebrow">{opportunity.source}</p>
          <h1>{opportunity.title}</h1>
          <p className="muted">{opportunity.agency || "Agency TBD"}</p>
        </div>
        {score ? (
          <div className="score-block">
            <div className="score">{Math.round(score.total_score)}</div>
            <span className={`pill ${actionClass(score.recommended_action)}`}>{score.recommended_action}</span>
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
                  <span className="ai-tag">
                    <Sparkles size={14} /> AI analysis
                  </span>
                  <p>{score.ai_narrative}</p>
                </div>
              ) : null}
              <ul className="reasons">
                {score.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <ActionForm
                action={generateOpportunityNarrativeAction}
                submitLabel={score.ai_narrative ? "Regenerate AI analysis" : "Generate AI analysis"}
                hidden={{ opportunity_id: id }}
                resetOnSuccess={false}
              >
                <span />
              </ActionForm>
            </>
          ) : (
            <p className="muted">
              No score yet — add your organization profile so GrantAtlas can score this opportunity against your mission,
              eligibility, and past performance.
            </p>
          )}
        </div>
        <div className="card stack">
          <h2>Score breakdown</h2>
          {score ? (
            <ScoreBreakdown
              rows={[
                { label: "Mission fit", value: score.mission_fit },
                { label: "Eligibility fit", value: score.eligibility_fit },
                { label: "Deadline urgency", value: score.deadline_urgency },
                { label: "Funding size", value: score.funding_size },
                { label: "Past performance", value: score.past_performance_fit },
                { label: "Strategic value", value: score.strategic_value },
                { label: "Probability of success", value: score.probability_of_success },
              ]}
            />
          ) : (
            <p className="muted">Breakdown appears once scored.</p>
          )}
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Opportunity details</h2>
          <p>
            <strong>Close date:</strong>{" "}
            {opportunity.close_date ? new Date(opportunity.close_date).toLocaleDateString() : "TBD"}
          </p>
          <p>
            <strong>Award ceiling:</strong>{" "}
            {opportunity.award_ceiling ? `$${opportunity.award_ceiling.toLocaleString()}` : "TBD"}
          </p>
          <p>
            <strong>Eligibility:</strong> {opportunity.eligibility || "Not specified."}
          </p>
          {opportunity.description ? <p className="muted">{opportunity.description}</p> : null}
          {opportunity.source_url ? (
            <a className="button secondary" href={opportunity.source_url} target="_blank" rel="noreferrer">
              View source listing
            </a>
          ) : null}
        </div>
        <div className="card stack">
          <h2>Start a proposal</h2>
          <p className="muted">Spin up a proposal workspace with a standard federal outline, pre-linked to this opportunity.</p>
          <ActionForm action={createProposalAction} submitLabel="Create proposal workspace" hidden={{ opportunity_id: id }}>
            <label className="field">
              <span className="field-label">Proposal title</span>
              <input className="input" name="title" defaultValue={`${opportunity.title} — Proposal`} required />
            </label>
          </ActionForm>
        </div>
      </section>
    </div>
  );
}
