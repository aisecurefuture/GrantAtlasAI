import { getAdminTenants, getAdminUsage } from "@/lib/api";
import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { adminCreateTenantAction, adminDeleteTenantAction, adminSetTenantActiveAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

const PLANS = ["Free Trial", "Starter", "Professional", "Growth", "Enterprise"];

function statusClass(status: string, active?: boolean) {
  if (active === false) return "low";
  if (status === "active" || status === "trialing") return "high";
  if (status === "past_due" || status === "unpaid") return "medium";
  if (status === "canceled" || status === "deactivated") return "low";
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
        <Disclosure label="Add tenant">
          <h3>Create a tenant</h3>
          <p className="muted">Creates the organization with an Owner account. A temporary password is shown once.</p>
          <ActionForm action={adminCreateTenantAction} submitLabel="Create tenant">
            <label className="field">
              <span className="field-label">Organization name *</span>
              <input className="input" name="organization_name" required />
            </label>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">Owner name *</span>
                <input className="input" name="owner_name" required />
              </label>
              <label className="field">
                <span className="field-label">Owner email *</span>
                <input className="input" type="email" name="owner_email" required />
              </label>
            </div>
            <label className="field">
              <span className="field-label">Plan</span>
              <select className="select" name="plan" defaultValue="Free Trial">
                {PLANS.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
          </ActionForm>
        </Disclosure>
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
              <th>Actions</th>
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
                  <span className={`pill ${statusClass(tenant.subscription_status, tenant.is_active)}`}>
                    {tenant.is_active === false ? "deactivated" : tenant.subscription_status}
                  </span>
                </td>
                <td>{tenant.user_count ?? "—"}</td>
                <td>{tenant.opportunity_count ?? "—"}</td>
                <td>
                  <div className="stack" style={{ gap: 6 }}>
                    <ActionForm
                      action={adminSetTenantActiveAction}
                      submitLabel={tenant.is_active === false ? "Reactivate" : "Deactivate"}
                      hidden={{ tenant_id: tenant.id, activate: tenant.is_active === false ? "true" : "false" }}
                      resetOnSuccess={false}
                      className="row-form"
                    >
                      <span />
                    </ActionForm>
                    <Disclosure label="Delete…" variant="secondary">
                      <h3>Delete {tenant.name}</h3>
                      <p className="muted">Permanently removes the tenant and all of its data. Cannot be undone.</p>
                      <ActionForm
                        action={adminDeleteTenantAction}
                        submitLabel="Delete permanently"
                        hidden={{ tenant_id: tenant.id }}
                      >
                        <label className="field">
                          <span className="field-label">Type DELETE to confirm</span>
                          <input className="input" name="confirm" placeholder="DELETE" required />
                        </label>
                      </ActionForm>
                    </Disclosure>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
