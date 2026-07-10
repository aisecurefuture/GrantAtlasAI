import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { getPastPerformance } from "@/lib/api";
import { createPastPerformanceAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

export default async function PastPerformancePage() {
  const projects = await getPastPerformance();

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Capture assets</p>
          <h1>Past performance</h1>
        </div>
        <Disclosure label="Add project">
          <h3>Add a past performance record</h3>
          <ActionForm action={createPastPerformanceAction} submitLabel="Add project">
            <label className="field">
              <span className="field-label">Project name *</span>
              <input className="input" name="project_name" required />
            </label>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">Customer</span>
                <input className="input" name="customer" />
              </label>
              <label className="field">
                <span className="field-label">Contract number</span>
                <input className="input" name="contract_number" />
              </label>
            </div>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">NAICS codes</span>
                <input className="input" name="naics_codes" placeholder="611430, 541519" />
              </label>
              <label className="field">
                <span className="field-label">PSC codes</span>
                <input className="input" name="classification_codes" placeholder="U008, D399" />
              </label>
            </div>
            <label className="field">
              <span className="field-label">Value ($)</span>
              <input className="input" name="value" inputMode="numeric" placeholder="125000" />
            </label>
            <label className="field">
              <span className="field-label">Summary</span>
              <textarea className="textarea" name="summary" rows={3} />
            </label>
            <label className="field">
              <span className="field-label">Outcomes (one per line)</span>
              <textarea className="textarea" name="outcomes" rows={3} placeholder="Trained 250 participants&#10;Published open-source materials" />
            </label>
          </ActionForm>
        </Disclosure>
      </div>

      {projects.length === 0 ? (
        <div className="card empty-state">
          <p>No past performance records yet.</p>
          <p className="muted">Add projects with NAICS/PSC codes so contract scoring can credit your relevant experience.</p>
        </div>
      ) : (
        <section className="grid cols-2">
          {projects.map((project) => (
            <article className="card stack" key={project.id}>
              <h2>{project.project_name}</h2>
              <p className="muted">
                {[project.customer, project.value ? `$${project.value.toLocaleString()}` : null].filter(Boolean).join(" · ")}
              </p>
              <div className="toolbar">
                {project.naics_codes.map((code) => (
                  <span className="pill" key={`n-${code}`}>
                    NAICS {code}
                  </span>
                ))}
                {project.classification_codes.map((code) => (
                  <span className="pill" key={`p-${code}`}>
                    PSC {code}
                  </span>
                ))}
              </div>
              {project.summary ? <p>{project.summary}</p> : null}
              {project.outcomes.map((outcome) => (
                <p key={outcome} className="muted">
                  • {outcome}
                </p>
              ))}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
