import Link from "next/link";
import { CalendarDays } from "lucide-react";
import type { Opportunity } from "@/lib/types";

function scoreClass(score: number) {
  if (score >= 78) return "high";
  if (score >= 55) return "medium";
  return "low";
}

function actionClass(action: string | null | undefined) {
  if (action === "Apply" || action === "Pursue") return "high";
  if (action === "Skip" || action === "No Bid") return "low";
  return "medium";
}

export function OpportunityTable({ opportunities }: { opportunities: Opportunity[] }) {
  if (opportunities.length === 0) {
    return (
      <div className="card empty-state">
        <p>No opportunities yet.</p>
        <p className="muted">Import from Grants.gov or add one manually to see explainable fit scores here.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <table className="table">
        <thead>
          <tr>
            <th>Opportunity</th>
            <th>Source</th>
            <th>Deadline</th>
            <th>Award ceiling</th>
            <th>Status</th>
            <th>Fit</th>
          </tr>
        </thead>
        <tbody>
          {opportunities.map((opportunity) => {
            const fit = typeof opportunity.fit_score === "number" ? Math.round(opportunity.fit_score) : null;
            return (
              <tr key={opportunity.id}>
                <td>
                  <Link href={`/opportunities/${opportunity.id}`}>
                    <strong>{opportunity.title}</strong>
                  </Link>
                  <div className="muted">{opportunity.agency || "Agency TBD"}</div>
                </td>
                <td>{opportunity.source}</td>
                <td>
                  <span className="toolbar">
                    <CalendarDays size={16} />
                    {opportunity.close_date ? new Date(opportunity.close_date).toLocaleDateString() : "TBD"}
                  </span>
                </td>
                <td>{opportunity.award_ceiling ? `$${opportunity.award_ceiling.toLocaleString()}` : "TBD"}</td>
                <td>
                  <span className={`pill ${actionClass(opportunity.recommended_action)}`}>
                    {opportunity.recommended_action ?? opportunity.status}
                  </span>
                </td>
                <td>{fit === null ? <span className="pill">—</span> : <span className={`pill ${scoreClass(fit)}`}>{fit}</span>}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
