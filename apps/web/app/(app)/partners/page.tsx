const partners = [
  {
    name: "Veteran Cyber Workforce Alliance",
    type: "Teaming partner",
    naics: ["611430", "541519"],
    statuses: ["SDVOSB", "Small Business"],
    capabilities: ["veteran training", "cybersecurity instructors", "workforce placement"]
  }
];

export default function PartnersPage() {
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">V2 teaming</p>
          <h1>Partner database</h1>
        </div>
        <button className="button">Add partner</button>
      </div>
      <section className="grid cols-2">
        {partners.map((partner) => (
          <article className="card stack" key={partner.name}>
            <div className="toolbar">
              <span className="pill">{partner.type}</span>
              {partner.statuses.map((status) => <span className="pill high" key={status}>{status}</span>)}
            </div>
            <h2>{partner.name}</h2>
            <p className="muted">NAICS {partner.naics.join(", ")}</p>
            <div className="toolbar">
              {partner.capabilities.map((capability) => <span className="pill" key={capability}>{capability}</span>)}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

