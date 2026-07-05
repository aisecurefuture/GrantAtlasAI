const projects = [
  {
    name: "Responsible Technology Training Pilot",
    customer: "Community education coalition",
    value: "$125,000",
    naics: ["611430", "541519"],
    psc: ["U008", "D399"],
    outcomes: ["Trained 250 participants", "Published open-source safety materials", "Improved cyber hygiene practices"]
  }
];

export default function PastPerformancePage() {
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">V2 capture assets</p>
          <h1>Past performance</h1>
        </div>
        <button className="button">Add project</button>
      </div>
      <section className="grid cols-2">
        {projects.map((project) => (
          <article className="card stack" key={project.name}>
            <h2>{project.name}</h2>
            <p className="muted">{project.customer} · {project.value}</p>
            <div className="toolbar">
              {project.naics.map((code) => <span className="pill" key={code}>NAICS {code}</span>)}
              {project.psc.map((code) => <span className="pill" key={code}>PSC {code}</span>)}
            </div>
            {project.outcomes.map((outcome) => <p key={outcome}>{outcome}</p>)}
          </article>
        ))}
      </section>
    </div>
  );
}
