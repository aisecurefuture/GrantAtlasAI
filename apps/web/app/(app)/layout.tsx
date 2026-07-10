import { redirect } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { getSession } from "@/lib/session";
import { getOrganizationProfile } from "@/lib/api";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await getSession();
  if (!session) redirect("/login");

  let workspaceName = "Your workspace";
  try {
    const profile = await getOrganizationProfile();
    if (profile?.organization_name) workspaceName = profile.organization_name;
  } catch {
    // Profile may not exist yet for a brand-new tenant; fall back to a neutral label.
  }

  return (
    <div className="app-shell">
      <Sidebar
        workspaceName={workspaceName}
        role={session.claims.role}
        isSuperAdmin={session.claims.is_super_admin}
      />
      <main className="main">{children}</main>
    </div>
  );
}
