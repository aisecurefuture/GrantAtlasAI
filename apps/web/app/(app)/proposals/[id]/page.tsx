import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getProposal } from "@/lib/api";

export const dynamic = "force-dynamic";

const KANBAN_COLUMNS = ["Not started", "Drafting", "Review", "Complete"];

function normalizeColumn(status: string | undefined): string {
  if (!status) return "Not started";
  const match = KANBAN_COLUMNS.find((c) => c.toLowerCase() === status.toLowerCase());
  return match ?? "Not started";
}

export default async function ProposalWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const proposal = await getProposal(id);

  const outline = proposal.outline ?? [];
  const columns: Record<string, string[]> = Object.fromEntries(KANBAN_COLUMNS.map((c) => [c, [] as string[]]));
  for (const section of outline) {
    columns[normalizeColumn(section.status)].push(section.heading);
  }

  return (
    <div className="stack">
      <Link className="toolbar muted" href="/proposals">
        <ArrowLeft size={16} />
        Back to proposals
      </Link>
      <div className="topbar">
        <div>
          <p className="eyebrow">Proposal workspace</p>
          <h1>{proposal.title}</h1>
        </div>
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Proposal outline</h2>
          {outline.length === 0 ? (
            <p className="muted">No outline sections yet.</p>
          ) : (
            outline.map((section) => (
              <div className="toolbar" key={section.heading} style={{ justifyContent: "space-between" }}>
                <span>{section.heading}</span>
                <span className="pill">{section.status ?? "Not started"}</span>
              </div>
            ))
          )}
        </div>
        <div className="card stack">
          <h2>Compliance matrix</h2>
          {proposal.compliance_matrix?.length ? (
            <table className="table">
              <tbody>
                {proposal.compliance_matrix.map((row, index) => (
                  <tr key={`${row.requirement}-${index}`}>
                    <td>{row.requirement}</td>
                    <td>{row.owner}</td>
                    <td>
                      <span className="pill">{row.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="muted">Compliance matrix is empty. Map each solicitation requirement to an owner and status.</p>
          )}
        </div>
      </section>

      <section className="kanban">
        {KANBAN_COLUMNS.map((name) => (
          <div className="kanban-column stack" key={name}>
            <h3>{name}</h3>
            {columns[name].length === 0 ? (
              <p className="muted">—</p>
            ) : (
              columns[name].map((task) => (
                <div className="card" key={task}>
                  {task}
                </div>
              ))
            )}
          </div>
        ))}
      </section>
    </div>
  );
}
