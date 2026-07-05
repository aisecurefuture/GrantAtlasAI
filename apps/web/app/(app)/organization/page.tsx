export default function OrganizationPage() {
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Tenant profile</p>
          <h1>Gratitech Research & Charitable Endeavor Corp.</h1>
        </div>
        <button className="button">Save</button>
      </div>
      <section className="grid cols-2">
        <div className="card stack">
          <h2>Registration</h2>
          <input className="input" defaultValue="EIN pending validation" aria-label="EIN" />
          <input className="input" defaultValue="UEI pending validation" aria-label="UEI" />
          <input className="input" defaultValue="SAM.gov status pending" aria-label="SAM.gov status" />
          <input className="input" defaultValue="Grants.gov status pending" aria-label="Grants.gov status" />
        </div>
        <div className="card stack">
          <h2>Mission</h2>
          <textarea
            className="textarea"
            rows={9}
            defaultValue="Advance public-benefit AI literacy, cybersecurity education, and responsible technology adoption."
          />
        </div>
      </section>
      <section className="card stack">
        <h2>Focus areas</h2>
        <div className="toolbar">
          {[
            "AI safety education",
            "Cybersecurity education",
            "AI literacy",
            "Workforce development",
            "Community AI safety",
            "Veteran technology training",
            "Teacher AI literacy"
          ].map((area) => (
            <span className="pill" key={area}>{area}</span>
          ))}
        </div>
      </section>
    </div>
  );
}

