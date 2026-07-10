import { BrandLogo } from "@/components/BrandLogo";
import { LoginForm } from "@/components/LoginForm";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const params = await searchParams;
  const next = typeof params.next === "string" && params.next.startsWith("/") ? params.next : "/dashboard";

  return (
    <main className="login-page">
      <div className="login-panel stack">
        <div className="stack" style={{ gap: 8 }}>
          <BrandLogo />
          <h1>Sign in</h1>
          <p className="muted">The map to federal funding — grants and contracts in one workspace.</p>
        </div>
        <LoginForm next={next} />
      </div>
    </main>
  );
}
