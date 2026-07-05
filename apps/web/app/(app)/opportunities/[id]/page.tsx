import { ArrowLeft, ClipboardCheck, FileText, UserPlus } from "lucide-react";
import Link from "next/link";
import { fetchOpportunityDetail } from "@/lib/api";

export default async function OpportunityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const detail = await fetchOpportunityDetail(id);
  const { opportunity, score } = detail;
  return (
    <div className="stack">
      <Link className="toolbar muted" href="/dashboard">
        <ArrowLeft size={16} />
        Back to dashboard
      </Link>
      <div className="topbar">
        <div>
          <p className="eyebrow">{opportunity.source}</p>
          <h1>{opportunity.title}</h1>
          <p className="muted">{opportunity.agency}</p>
        </div>
        {score ? <div className="score">{Math.round(score.total_score)}</div> : null}
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Fit analysis</h2>
          {score?.reasons.map((reason) => (
            <p key={reason} className="muted">
              {reason}
            </p>
          ))}
          <div className="toolbar">
            <span className="pill high">{score?.recommended_action ?? "Review"}</span>
            <span className="pill">Eligibility {score ? Math.round(score.eligibility_fit) : "TBD"}</span>
            <span className="pill">Mission {score ? Math.round(score.mission_fit) : "TBD"}</span>
          </div>
        </div>
        <div className="card stack">
          <h2>Deadline timeline</h2>
          <p>
            <strong>Close date:</strong>{" "}
            {opportunity.close_date ? new Date(opportunity.close_date).toLocaleDateString() : "TBD"}
          </p>
          <p>
            <strong>Award ceiling:</strong>{" "}
            {opportunity.award_ceiling ? `$${opportunity.award_ceiling.toLocaleString()}` : "TBD"}
          </p>
          <p className="muted">{opportunity.eligibility}</p>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Suggested proposal strategy</h2>
          <p>{opportunity.description}</p>
          <div className="toolbar">
            {opportunity.categories.map((category) => (
              <span className="pill" key={category}>
                {category}
              </span>
            ))}
          </div>
        </div>
        <div className="card stack">
          <h2>Application checklist</h2>
          {[
            ["Confirm eligibility", ClipboardCheck],
            ["Map reusable narrative sections", FileText],
            ["Validate partner needs", UserPlus]
          ].map(([label, Icon]) => {
            const TypedIcon = Icon as typeof ClipboardCheck;
            return (
              <div className="toolbar" key={label as string}>
                <TypedIcon size={18} />
                <span>{label as string}</span>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

