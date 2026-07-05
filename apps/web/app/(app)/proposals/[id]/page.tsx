export default function ProposalWorkspacePage() {
  const columns = {
    "To do": ["Confirm NOFO requirements", "Draft compliance matrix", "Collect IRS determination letter"],
    Drafting: ["Mission fit narrative", "Program model", "Evaluation plan"],
    Review: ["Budget narrative"],
    Complete: ["Organization history"]
  };

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Proposal workspace</p>
          <h1>Community Technology Education Capacity Grant</h1>
        </div>
        <button className="button">Export</button>
      </div>
      <section className="grid cols-2">
        <div className="card stack">
          <h2>Proposal outline</h2>
          {["Executive summary", "Need statement", "Program design", "Evaluation", "Sustainability", "Budget narrative"].map((item) => (
            <p key={item}>{item}</p>
          ))}
        </div>
        <div className="card stack">
          <h2>Compliance matrix</h2>
          <table className="table">
            <tbody>
              <tr>
                <td>Eligibility</td>
                <td><span className="pill high">Mapped</span></td>
              </tr>
              <tr>
                <td>Attachments</td>
                <td><span className="pill medium">Needs review</span></td>
              </tr>
              <tr>
                <td>Budget</td>
                <td><span className="pill">Draft</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <section className="kanban">
        {Object.entries(columns).map(([name, tasks]) => (
          <div className="kanban-column stack" key={name}>
            <h3>{name}</h3>
            {tasks.map((task) => (
              <div className="card" key={task}>
                {task}
              </div>
            ))}
          </div>
        ))}
      </section>
    </div>
  );
}

