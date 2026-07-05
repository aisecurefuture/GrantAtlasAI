const items = [
  ["Mission Statement", "Mission statement"],
  ["Organizational History", "Organizational history"],
  ["Cybersecurity Capability Statement", "Capability statement"],
  ["AI Literacy Program", "Program descriptions"],
  ["Evaluation Plan", "Evaluation plan"],
  ["Sustainability Plan", "Sustainability plan"]
];

export default function LibraryPage() {
  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Reusable content</p>
          <h1>Proposal library</h1>
        </div>
        <button className="button">Add item</button>
      </div>
      <section className="grid cols-2">
        {items.map(([title, category]) => (
          <article className="card stack" key={title}>
            <span className="pill">{category}</span>
            <h2>{title}</h2>
            <p className="muted">
              Gratitech reusable narrative content for AI safety education, cybersecurity education, workforce development,
              and responsible technology adoption proposals.
            </p>
          </article>
        ))}
      </section>
    </div>
  );
}

