export default function AdminPage() {
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Platform operations</p>
          <h1>Super-admin dashboard</h1>
        </div>
      </div>
      <section className="grid cols-4">
        <div className="card metric"><span className="muted">Tenants</span><strong>1</strong></div>
        <div className="card metric"><span className="muted">Users</span><strong>1</strong></div>
        <div className="card metric"><span className="muted">Ingestion jobs</span><strong>0</strong></div>
        <div className="card metric"><span className="muted">Errors</span><strong>0</strong></div>
      </section>
      <section className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Tenant</th>
              <th>Plan</th>
              <th>Status</th>
              <th>Support</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Gratitech Research & Charitable Endeavor Corp.</td>
              <td>Free Trial</td>
              <td><span className="pill high">Trialing</span></td>
              <td><span className="pill">Audit required</span></td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}

