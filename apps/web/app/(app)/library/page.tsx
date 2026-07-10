import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { getLibraryItems } from "@/lib/api";
import { createLibraryItemAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

const CATEGORIES = [
  "Mission statement",
  "Organizational history",
  "Capability statement",
  "Program descriptions",
  "Evaluation plan",
  "Sustainability plan",
  "Budget narrative",
  "Boilerplate",
];

export default async function LibraryPage() {
  const items = await getLibraryItems();

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Reusable content</p>
          <h1>Content library</h1>
        </div>
        <Disclosure label="Add content">
          <h3>Add reusable content</h3>
          <ActionForm action={createLibraryItemAction} submitLabel="Save to library">
            <label className="field">
              <span className="field-label">Title *</span>
              <input className="input" name="title" required />
            </label>
            <label className="field">
              <span className="field-label">Category *</span>
              <select className="select" name="category" defaultValue="">
                <option value="" disabled>
                  Choose a category
                </option>
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span className="field-label">Content</span>
              <textarea className="textarea" name="body" rows={5} placeholder="Reusable narrative text…" />
            </label>
            <label className="field">
              <span className="field-label">Tags (comma-separated)</span>
              <input className="input" name="tags" placeholder="cybersecurity, AI literacy" />
            </label>
          </ActionForm>
        </Disclosure>
      </div>

      {items.length === 0 ? (
        <div className="card empty-state">
          <p>Your content library is empty.</p>
          <p className="muted">Save reusable narrative blocks — mission, capability statements, evaluation plans — to drop into proposals.</p>
        </div>
      ) : (
        <section className="grid cols-2">
          {items.map((item) => (
            <article className="card stack" key={item.id}>
              <span className="pill">{item.category}</span>
              <h2>{item.title}</h2>
              {item.body ? <p className="muted">{item.body.length > 240 ? `${item.body.slice(0, 240)}…` : item.body}</p> : null}
              {item.tags.length ? (
                <div className="toolbar">
                  {item.tags.map((tag) => (
                    <span className="pill" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
