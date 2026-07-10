import { ActionForm } from "@/components/ActionForm";
import { getOrganizationProfile } from "@/lib/api";
import { saveOrganizationAction } from "@/app/actions/data";
import type { OrganizationProfile } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function OrganizationPage() {
  let profile: OrganizationProfile | null = null;
  try {
    profile = await getOrganizationProfile();
  } catch {
    profile = null;
  }

  return (
    <div className="stack">
      <div className="topbar">
        <div>
          <p className="eyebrow">Tenant profile</p>
          <h1>Organization</h1>
          <p className="muted">Your profile powers every fit score. Keep the mission, focus areas, and past performance current.</p>
        </div>
      </div>

      <ActionForm action={saveOrganizationAction} submitLabel="Save profile" resetOnSuccess={false}>
        <section className="grid cols-2">
          <div className="card stack">
            <h2>Identity & registration</h2>
            <label className="field">
              <span className="field-label">Organization name *</span>
              <input className="input" name="organization_name" defaultValue={profile?.organization_name ?? ""} required />
            </label>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">EIN</span>
                <input className="input" name="ein" defaultValue={profile?.ein ?? ""} />
              </label>
              <label className="field">
                <span className="field-label">UEI</span>
                <input className="input" name="uei" defaultValue={profile?.uei ?? ""} />
              </label>
            </div>
            <div className="grid cols-2">
              <label className="field">
                <span className="field-label">SAM.gov status</span>
                <input className="input" name="sam_status" defaultValue={profile?.sam_status ?? ""} />
              </label>
              <label className="field">
                <span className="field-label">Grants.gov status</span>
                <input className="input" name="grants_gov_status" defaultValue={profile?.grants_gov_status ?? ""} />
              </label>
            </div>
            <label className="field">
              <span className="field-label">Nonprofit status</span>
              <input className="input" name="nonprofit_status" defaultValue={profile?.nonprofit_status ?? ""} placeholder="501(c)(3)" />
            </label>
          </div>
          <div className="card stack">
            <h2>Mission & vision</h2>
            <label className="field">
              <span className="field-label">Mission</span>
              <textarea className="textarea" name="mission" rows={4} defaultValue={profile?.mission ?? ""} />
            </label>
            <label className="field">
              <span className="field-label">Vision</span>
              <textarea className="textarea" name="vision" rows={4} defaultValue={profile?.vision ?? ""} />
            </label>
          </div>
        </section>

        <section className="card stack">
          <h2>Capabilities</h2>
          <div className="grid cols-2">
            <label className="field">
              <span className="field-label">Focus areas (comma or newline separated)</span>
              <textarea className="textarea" name="focus_areas" rows={3} defaultValue={(profile?.focus_areas ?? []).join(", ")} />
            </label>
            <label className="field">
              <span className="field-label">Programs</span>
              <textarea className="textarea" name="programs" rows={3} defaultValue={(profile?.programs ?? []).join(", ")} />
            </label>
          </div>
          <div className="grid cols-2">
            <label className="field">
              <span className="field-label">Target populations</span>
              <textarea className="textarea" name="target_populations" rows={2} defaultValue={(profile?.target_populations ?? []).join(", ")} />
            </label>
            <label className="field">
              <span className="field-label">Geographic service area</span>
              <input className="input" name="geographic_service_area" defaultValue={profile?.geographic_service_area ?? ""} />
            </label>
          </div>
          <label className="field">
            <span className="field-label">Past performance summary</span>
            <textarea className="textarea" name="past_performance" rows={4} defaultValue={profile?.past_performance ?? ""} />
          </label>
        </section>
      </ActionForm>
    </div>
  );
}
