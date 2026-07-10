import Link from "next/link";
import { getProposals } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ProposalsPage() {
  const proposals = await getProposals();

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Proposal workspaces</p>
          <h1>Proposals</h1>
          <p className="muted">Start a proposal from any opportunity's detail page to spin up a workspace here.</p>
        </div>
      </div>

      {proposals.length === 0 ? (
        <div className="card empty-state">
          <p>No proposal workspaces yet.</p>
          <p className="muted">Open an opportunity in your pipeline and choose “Create proposal workspace.”</p>
          <Link className="button" href="/dashboard">
            Go to pipeline
          </Link>
        </div>
      ) : (
        <section className="grid cols-2">
          {proposals.map((proposal) => {
            const sections = proposal.outline?.length ?? 0;
            const done = (proposal.outline ?? []).filter((s) => s.status === "Complete").length;
            return (
              <Link className="card stack proposal-card" href={`/proposals/${proposal.id}`} key={proposal.id}>
                <h2>{proposal.title}</h2>
                <p className="muted">
                  {sections} section{sections === 1 ? "" : "s"} · {done} complete
                </p>
                <span className="pill">Updated {new Date(proposal.updated_at).toLocaleDateString()}</span>
              </Link>
            );
          })}
        </section>
      )}
    </div>
  );
}
