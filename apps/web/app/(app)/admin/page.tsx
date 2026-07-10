import { getAdminTenants, getAdminUsage } from "@/lib/api";

export const dynamic = "force-dynamic";

function statusClass(status: string) {
  if (status === "active" || status === "trialing") return "high";
  if (status === "past_due" || status === "unpaid") return "medium";
  if (status === "canceled") return "low";
  return "";
}

export default async function AdminPage() {
  const [usage, tenants] = await Promise.all([getAdminUsage(), getAdminTenants()]);

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Platform operations</p>
          <h1>Super-admin</h1>
        </div>
      </div>

      <section className="grid cols-4">
        <div className="card metric"><span className="muted">Tenants</span><strong>{usage.tenants}</strong></div>
        <div className="card metric"><span className="muted">Users</span><strong>{usage.users}</strong></div>
        <div className="card metric"><span className="muted">Opportunities</span><strong>{usage.opportunities}</strong></div>
        <div className="card metric"><span className="muted">Contracts</span><strong>{usage.contract_opportunities}</strong></div>
      </section>
      <section className="grid cols-2">
        <div className="card metric"><span className="muted">Proposals</span><strong>{usage.proposals}</strong></div>
        <div className="card metric"><span className="muted">Audit events</span><strong>{usage.recent_audit_events}</strong></div>
      </section>

      <section className="card">
        <h2 style={{ marginBottom: 12 }}>Tenants</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Tenant</th>
              <th>Plan</th>
              <th>Status</th>
              <th>Users</th>
              <th>Opportunities</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((tenant) => (
              <tr key={tenant.id}>
                <td>
                  <strong>{tenant.name}</strong>
                  <div className="muted">{tenant.slug}</div>
                </td>
                <td>{tenant.plan}</td>
                <td>
                  <span className={`pill ${statusClass(tenant.subscription_status)}`}>{tenant.subscription_status}</span>
                </td>
                <td>{tenant.user_count ?? "—"}</td>
                <td>{tenant.opportunity_count ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
