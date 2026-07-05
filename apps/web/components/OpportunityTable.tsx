import Link from "next/link";
import { CalendarDays } from "lucide-react";
import type { Opportunity } from "@/lib/types";

function scoreClass(score: number) {
  if (score >= 80) return "high";
  if (score >= 55) return "medium";
  return "low";
}

export function OpportunityTable({ opportunities }: { opportunities: Opportunity[] }) {
  return (
    <div className="card">
      <table className="table">
        <thead>
          <tr>
            <th>Opportunity</th>
            <th>Source</th>
            <th>Deadline</th>
            <th>Award</th>
            <th>Status</th>
            <th>Fit</th>
          </tr>
        </thead>
        <tbody>
          {opportunities.map((opportunity, index) => {
            const fit = index === 0 ? 86 : 72;
            return (
              <tr key={opportunity.id}>
                <td>
                  <Link href={`/opportunities/${opportunity.id}`}>
                    <strong>{opportunity.title}</strong>
                  </Link>
                  <div className="muted">{opportunity.agency}</div>
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
                  <span className="pill">{opportunity.status}</span>
                </td>
                <td>
                  <span className={`pill ${scoreClass(fit)}`}>{fit}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
