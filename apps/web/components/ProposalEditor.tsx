"use client";

import { Plus, Save, Sparkles, Trash2 } from "lucide-react";
import { useState, useTransition } from "react";
import { draftProposalSectionAction, saveProposalAction, type ProposalSavePayload } from "@/app/actions/data";
import type { ProposalWorkspace } from "@/lib/types";

const SECTION_STATUSES = ["Not started", "Drafting", "Review", "Complete"];
const COMPLIANCE_STATUSES = ["Unmapped", "Mapped", "Draft", "Needs review", "Complete"];

type OutlineRow = { heading: string; status: string };
type ComplianceRow = { requirement: string; owner: string; status: string };

export function ProposalEditor({ proposal }: { proposal: ProposalWorkspace }) {
  const [title, setTitle] = useState(proposal.title);
  const [outline, setOutline] = useState<OutlineRow[]>(
    (proposal.outline ?? []).map((s) => ({ heading: s.heading, status: s.status ?? "Not started" })),
  );
  const [matrix, setMatrix] = useState<ComplianceRow[]>(
    (proposal.compliance_matrix ?? []).map((r) => ({
      requirement: r.requirement ?? "",
      owner: r.owner ?? "",
      status: r.status ?? "Unmapped",
    })),
  );
  const [drafts, setDrafts] = useState<Record<string, string>>(
    Object.fromEntries((proposal.narrative_sections ?? []).map((s) => [s.heading, s.content])),
  );
  const [notes, setNotes] = useState(proposal.internal_notes ?? "");
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null);
  const [pending, startTransition] = useTransition();
  const [draftingHeading, setDraftingHeading] = useState<string | null>(null);

  function save() {
    const payload: ProposalSavePayload = {
      title: title.trim() || proposal.title,
      outline: outline.filter((s) => s.heading.trim()),
      compliance_matrix: matrix.filter((r) => r.requirement.trim()),
      narrative_sections: outline
        .filter((s) => s.heading.trim() && drafts[s.heading]?.trim())
        .map((s) => ({ heading: s.heading, content: drafts[s.heading] })),
      internal_notes: notes,
    };
    startTransition(async () => {
      const result = await saveProposalAction(proposal.id, payload);
      setMessage(result.ok ? { ok: true, text: result.message ?? "Saved." } : { ok: false, text: result.error ?? "Save failed." });
    });
  }

  function draftSection(heading: string) {
    if (!heading.trim() || draftingHeading) return;
    setDraftingHeading(heading);
    setMessage(null);
    startTransition(async () => {
      const result = await draftProposalSectionAction(proposal.id, heading, "");
      if (result.ok && result.content !== undefined) {
        setDrafts((prev) => ({ ...prev, [heading]: result.content as string }));
        setMessage({ ok: true, text: `Drafted "${heading}". Review and edit before submitting.` });
      } else {
        setMessage({ ok: false, text: result.error ?? "Drafting failed." });
      }
      setDraftingHeading(null);
    });
  }

  return (
    <div className="stack">
      <div className="topbar">
        <div style={{ flex: 1, minWidth: 260 }}>
          <p className="eyebrow">Proposal workspace</p>
          <input
            className="input title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            aria-label="Proposal title"
          />
        </div>
        <div className="toolbar">
          {message ? (
            <span className={message.ok ? "form-success" : "form-error"} role="status">
              {message.text}
            </span>
          ) : null}
          <button className="button" onClick={save} disabled={pending}>
            <Save size={16} />
            {pending ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h2>Proposal outline</h2>
          {outline.map((section, index) => (
            <div className="editor-row" key={index}>
              <input
                className="input"
                value={section.heading}
                onChange={(e) => setOutline(outline.map((s, i) => (i === index ? { ...s, heading: e.target.value } : s)))}
                aria-label={`Section ${index + 1} heading`}
              />
              <select
                className="select"
                value={section.status}
                onChange={(e) => setOutline(outline.map((s, i) => (i === index ? { ...s, status: e.target.value } : s)))}
                aria-label={`Section ${index + 1} status`}
              >
                {SECTION_STATUSES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
              <button
                className="button secondary icon-button"
                onClick={() => setOutline(outline.filter((_, i) => i !== index))}
                aria-label={`Remove section ${index + 1}`}
                type="button"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
          <button
            className="button secondary"
            type="button"
            onClick={() => setOutline([...outline, { heading: "", status: "Not started" }])}
          >
            <Plus size={16} />
            Add section
          </button>
        </div>

        <div className="card stack">
          <h2>Compliance matrix</h2>
          {matrix.map((row, index) => (
            <div className="editor-row compliance" key={index}>
              <input
                className="input"
                placeholder="Requirement"
                value={row.requirement}
                onChange={(e) => setMatrix(matrix.map((r, i) => (i === index ? { ...r, requirement: e.target.value } : r)))}
                aria-label={`Requirement ${index + 1}`}
              />
              <input
                className="input"
                placeholder="Owner"
                value={row.owner}
                onChange={(e) => setMatrix(matrix.map((r, i) => (i === index ? { ...r, owner: e.target.value } : r)))}
                aria-label={`Requirement ${index + 1} owner`}
              />
              <select
                className="select"
                value={row.status}
                onChange={(e) => setMatrix(matrix.map((r, i) => (i === index ? { ...r, status: e.target.value } : r)))}
                aria-label={`Requirement ${index + 1} status`}
              >
                {COMPLIANCE_STATUSES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
              <button
                className="button secondary icon-button"
                onClick={() => setMatrix(matrix.filter((_, i) => i !== index))}
                aria-label={`Remove requirement ${index + 1}`}
                type="button"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
          <button
            className="button secondary"
            type="button"
            onClick={() => setMatrix([...matrix, { requirement: "", owner: "", status: "Unmapped" }])}
          >
            <Plus size={16} />
            Add requirement
          </button>
        </div>
      </section>

      <section className="card stack">
        <div>
          <h2>Narrative sections</h2>
          <p className="muted" style={{ margin: "4px 0 0" }}>
            AI drafts each section from your organization profile and content library, grounded in this funder&apos;s
            priorities. It never invents facts — it inserts <code>[INSERT: …]</code> placeholders where you must add
            specifics. Always review before submitting.
          </p>
        </div>
        {outline.filter((s) => s.heading.trim()).length === 0 ? (
          <p className="muted">Add outline sections above, then draft narrative content for each.</p>
        ) : (
          outline
            .filter((s) => s.heading.trim())
            .map((section) => (
              <div className="stack narrative-section" key={section.heading} style={{ gap: 8 }}>
                <div className="section-head" style={{ marginBottom: 0 }}>
                  <h3>{section.heading}</h3>
                  <button
                    className="button secondary"
                    type="button"
                    onClick={() => draftSection(section.heading)}
                    disabled={pending}
                  >
                    <Sparkles size={15} />
                    {draftingHeading === section.heading
                      ? "Drafting… (can take a minute)"
                      : drafts[section.heading]
                        ? "Redraft with AI"
                        : "Draft with AI"}
                  </button>
                </div>
                <textarea
                  className="textarea"
                  rows={drafts[section.heading] ? 10 : 4}
                  value={drafts[section.heading] ?? ""}
                  onChange={(e) => setDrafts((prev) => ({ ...prev, [section.heading]: e.target.value }))}
                  placeholder="Draft with AI, or write this section directly…"
                  aria-label={`${section.heading} narrative`}
                />
              </div>
            ))
        )}
      </section>

      <section className="card stack">
        <h2>Internal notes</h2>
        <textarea
          className="textarea"
          rows={5}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Working notes, review comments, submission logistics…"
        />
      </section>

      <section className="kanban">
        {SECTION_STATUSES.map((column) => (
          <div className="kanban-column stack" key={column}>
            <h3>{column}</h3>
            {outline.filter((s) => s.status === column && s.heading.trim()).length === 0 ? (
              <p className="muted">—</p>
            ) : (
              outline
                .filter((s) => s.status === column && s.heading.trim())
                .map((s) => (
                  <div className="card" key={s.heading}>
                    {s.heading}
                  </div>
                ))
            )}
          </div>
        ))}
      </section>
    </div>
  );
}
