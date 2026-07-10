import { Disclosure } from "@/components/Disclosure";
import { ActionForm } from "@/components/ActionForm";
import { getPartners } from "@/lib/api";
import { createPartnerAction } from "@/app/actions/data";

export const dynamic = "force-dynamic";

export default async function PartnersPage() {
  const partners = await getPartners();

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Teaming network</p>
          <h1>Partners</h1>
        </div>
        <Disclosure label="Add partner">
          <h3>Add a teaming partner</h3>
          <ActionForm action={createPartnerAction} submitLabel="Add partner">
            <label className="field">
              <span className="field-label">Name *</span>
              <input className="input" name="name" required />
            </label>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">Partner type</span>
                <select className="select" name="partner_type" defaultValue="Subcontractor">
                  <option>Subcontractor</option>
                  <option>Prime</option>
                  <option>Teaming partner</option>
                  <option>Mentor</option>
                </select>
              </label>
              <label className="field">
                <span className="field-label">UEI</span>
                <input className="input" name="uei" />
              </label>
            </div>
            <label className="field">
              <span className="field-label">Capabilities (comma-separated)</span>
              <input className="input" name="capabilities" placeholder="veteran training, cybersecurity instruction" />
            </label>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">NAICS codes</span>
                <input className="input" name="naics_codes" placeholder="611430, 541519" />
              </label>
              <label className="field">
                <span className="field-label">Set-aside statuses</span>
                <input className="input" name="set_aside_statuses" placeholder="SDVOSB, Small Business" />
              </label>
            </div>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">Contact name</span>
                <input className="input" name="contact_name" />
              </label>
              <label className="field">
                <span className="field-label">Contact email</span>
                <input className="input" type="email" name="contact_email" />
              </label>
            </div>
            <label className="field">
              <span className="field-label">Notes</span>
              <textarea className="textarea" name="notes" rows={2} />
            </label>
          </ActionForm>
        </Disclosure>
      </div>

      {partners.length === 0 ? (
        <div className="card empty-state">
          <p>No teaming partners yet.</p>
          <p className="muted">Build a network of subs and primes so capture plans can match set-aside and NAICS gaps.</p>
        </div>
      ) : (
        <section className="grid cols-2">
          {partners.map((partner) => (
            <article className="card stack" key={partner.id}>
              <div className="toolbar">
                <span className="pill">{partner.partner_type}</span>
                {partner.set_aside_statuses.map((status) => (
                  <span className="pill high" key={status}>
                    {status}
                  </span>
                ))}
              </div>
              <h2>{partner.name}</h2>
              {partner.naics_codes.length ? <p className="muted">NAICS {partner.naics_codes.join(", ")}</p> : null}
              {partner.capabilities.length ? (
                <div className="toolbar">
                  {partner.capabilities.map((capability) => (
                    <span className="pill" key={capability}>
                      {capability}
                    </span>
                  ))}
                </div>
              ) : null}
              {partner.contact_name || partner.contact_email ? (
                <p className="muted">
                  {[partner.contact_name, partner.contact_email].filter(Boolean).join(" · ")}
                </p>
              ) : null}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
