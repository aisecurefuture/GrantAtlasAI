import { ActionForm } from "@/components/ActionForm";
import { Disclosure } from "@/components/Disclosure";
import { getOrganizationProfile, getTeamUsers } from "@/lib/api";
import {
  createTeamUserAction,
  deactivateAccountAction,
  deleteAccountAction,
  saveOrganizationAction,
  updateTeamUserAction,
} from "@/app/actions/data";
import { getSession } from "@/lib/session";
import type { OrganizationProfile, TenantUser } from "@/lib/types";

export const dynamic = "force-dynamic";

const ROLES = ["Owner", "Admin", "Grant Writer", "Reviewer", "Viewer"];

export default async function OrganizationPage() {
  const session = await getSession();
  const canManage = session ? ["Owner", "Admin"].includes(session.claims.role) || session.claims.is_super_admin : false;
  const isOwner = session ? session.claims.role === "Owner" || session.claims.is_super_admin : false;

  let profile: OrganizationProfile | null = null;
  try {
    profile = await getOrganizationProfile();
  } catch {
    profile = null;
  }

  let team: TenantUser[] = [];
  if (canManage) {
    try {
      team = await getTeamUsers();
    } catch {
      team = [];
    }
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

      {canManage ? (
        <section className="card stack">
          <div className="section-head" style={{ marginBottom: 0 }}>
            <h2>Team</h2>
            <Disclosure label="Add user">
              <h3>Add a team member</h3>
              <p className="muted">
                A temporary password is generated and shown once — share it securely and have them change it later.
              </p>
              <ActionForm action={createTeamUserAction} submitLabel="Add user">
                <div className="grid cols-2">
                  <label className="field">
                    <span className="field-label">Name *</span>
                    <input className="input" name="name" required />
                  </label>
                  <label className="field">
                    <span className="field-label">Email *</span>
                    <input className="input" type="email" name="email" required />
                  </label>
                </div>
                <label className="field">
                  <span className="field-label">Role</span>
                  <select className="select" name="role" defaultValue="Viewer">
                    {ROLES.map((r) => (
                      <option key={r}>{r}</option>
                    ))}
                  </select>
                </label>
              </ActionForm>
            </Disclosure>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {team.map((member) => (
                <tr key={member.id}>
                  <td>
                    <strong>{member.name}</strong>
                    <div className="muted">{member.email}</div>
                  </td>
                  <td>
                    <ActionForm
                      action={updateTeamUserAction}
                      submitLabel="Update"
                      hidden={{ user_id: member.id }}
                      resetOnSuccess={false}
                      className="row-form"
                    >
                      <select className="select" name="role" defaultValue={member.role}>
                        {ROLES.map((r) => (
                          <option key={r}>{r}</option>
                        ))}
                      </select>
                    </ActionForm>
                  </td>
                  <td>
                    <span className={`pill ${member.is_active ? "high" : "low"}`}>
                      {member.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td>
                    <ActionForm
                      action={updateTeamUserAction}
                      submitLabel={member.is_active ? "Deactivate" : "Reactivate"}
                      hidden={{ user_id: member.id, is_active: member.is_active ? "false" : "true" }}
                      resetOnSuccess={false}
                      className="row-form"
                    >
                      <span />
                    </ActionForm>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      {isOwner ? (
        <section className="card stack danger-zone">
          <h2>Danger zone</h2>
          <p className="muted">
            Deactivating blocks all sign-ins but keeps your data — contact support to reactivate. Deleting permanently
            removes your organization and every record it owns. Neither can be undone by your team.
          </p>
          <div className="toolbar">
            <Disclosure label="Deactivate account" variant="secondary">
              <h3>Deactivate this organization</h3>
              <p className="muted">All users will be signed out and unable to log in. Data is retained.</p>
              <ActionForm action={deactivateAccountAction} submitLabel="Deactivate organization">
                <label className="field">
                  <span className="field-label">Type DEACTIVATE to confirm</span>
                  <input className="input" name="confirm" placeholder="DEACTIVATE" required />
                </label>
              </ActionForm>
            </Disclosure>
            <Disclosure label="Delete account" variant="secondary">
              <h3>Permanently delete this organization</h3>
              <p className="muted">
                Removes all opportunities, contracts, proposals, library content, partners, and users. This cannot be
                undone.
              </p>
              <ActionForm action={deleteAccountAction} submitLabel="Delete everything permanently">
                <label className="field">
                  <span className="field-label">Type your organization name ({profile?.organization_name ?? "…"}) to confirm</span>
                  <input className="input" name="confirm_organization_name" required />
                </label>
              </ActionForm>
            </Disclosure>
          </div>
        </section>
      ) : null}
    </div>
  );
}
