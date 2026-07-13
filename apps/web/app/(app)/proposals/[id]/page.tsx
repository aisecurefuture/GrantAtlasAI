import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { getProposal } from "@/lib/api";
import { ProposalEditor } from "@/components/ProposalEditor";

export const dynamic = "force-dynamic";

export default async function ProposalWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const proposal = await getProposal(id);

  return (
    <div className="stack">
      <Link className="toolbar muted" href="/proposals">
        <ArrowLeft size={16} />
        Back to proposals
      </Link>
      <ProposalEditor proposal={proposal} />
    </div>
  );
}
