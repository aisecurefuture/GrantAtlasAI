import { getBillingSummary } from "@/lib/api";
import { BillingPlans } from "@/components/BillingPlans";

export const dynamic = "force-dynamic";

function usagePct(used: number, limit: number | null): number | null {
  if (limit === null || limit === undefined) return null;
  if (limit === 0) return 100;
  return Math.min(100, Math.round((used / limit) * 100));
}

export default async function BillingPage() {
  const summary = await getBillingSummary();

  const usageRows = [
    { label: "Users", used: summary.usage.users, limit: summary.limits.users ?? null },
    { label: "Saved opportunities", used: summary.usage.saved_opportunities, limit: summary.limits.saved_opportunities ?? null },
    { label: "Proposal workspaces", used: summary.usage.proposal_workspaces, limit: summary.limits.proposal_workspaces ?? null },
  ];

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Subscription</p>
          <h1>Billing</h1>
        </div>
        <span className={`pill ${summary.subscription_status === "active" ? "high" : "medium"}`}>
          {summary.plan} · {summary.subscription_status}
        </span>
      </div>

      {!summary.stripe_configured ? (
        <div className="card notice">
          <strong>Stripe isn&apos;t configured on this environment.</strong>
          <p className="muted">
            Add your Stripe secret key and price IDs to enable checkout and the customer portal. Plans below reflect published pricing.
          </p>
        </div>
      ) : null}

      <section className="card stack">
        <h2>Current usage</h2>
        {usageRows.map((row) => {
          const pct = usagePct(row.used, row.limit);
          return (
            <div className="score-bar-row" key={row.label}>
              <span className="score-bar-label">{row.label}</span>
              <span className="score-bar-track">
                {pct === null ? (
                  <span className="score-bar-fill high" style={{ width: "8%" }} />
                ) : (
                  <span className={`score-bar-fill ${pct >= 90 ? "low" : pct >= 70 ? "medium" : "high"}`} style={{ width: `${Math.max(4, pct)}%` }} />
                )}
              </span>
              <span className="score-bar-value">
                {row.used}
                {row.limit === null ? " / ∞" : ` / ${row.limit}`}
              </span>
            </div>
          );
        })}
      </section>

      <BillingPlans
        plans={summary.available_plans}
        currentPlan={summary.plan}
        stripeConfigured={summary.stripe_configured}
        customerConnected={summary.stripe_customer_connected}
      />
    </div>
  );
}
