import Link from "next/link";
import { BrandLogo } from "@/components/BrandLogo";
import { RegisterForm } from "@/components/RegisterForm";

const PLANS = [
  { id: "Starter", price: "$149/mo", seats: "2 users", blurb: "Discovery, fit scoring, and pipeline." },
  { id: "Professional", price: "$349/mo", seats: "5 users", blurb: "Proposals, content library, capture plans." },
  { id: "Growth", price: "$749/mo", seats: "15 users", blurb: "Partner CRM, past performance, reporting." },
  { id: "Enterprise", price: "Custom", seats: "Custom seats", blurb: "Universities, municipalities, multi-team." },
] as const;

export default async function RegisterPage({ searchParams }: { searchParams: Promise<{ plan?: string }> }) {
  const params = await searchParams;
  const preselected = PLANS.find((p) => p.id.toLowerCase() === (params.plan ?? "").toLowerCase())?.id ?? "Professional";

  return (
    <main className="login-page">
      <div className="login-panel stack" style={{ width: "min(720px, 100%)" }}>
        <div className="stack" style={{ gap: 8 }}>
          <BrandLogo />
          <h1>Start your 14-day free trial</h1>
          <p className="muted">
            Pick a plan, create your workspace, and start scoring opportunities. No credit card required during the
            trial — billing starts only if you subscribe.
          </p>
        </div>
        <RegisterForm plans={PLANS.map((p) => ({ ...p }))} preselected={preselected} />
        <p className="muted">
          Already have an account? <Link href="/login">Sign in</Link>
        </p>
      </div>
    </main>
  );
}
