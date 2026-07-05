import { BrandLogo } from "@/components/BrandLogo";
import { LogIn } from "lucide-react";

export default function LoginPage() {
  return (
    <main className="login-page">
      <form className="login-panel stack">
        <div className="stack">
          <BrandLogo />
          <h1>Sign in</h1>
        </div>
        <input className="input" type="email" placeholder="owner@example.com" aria-label="Email" autoComplete="email" />
        <input className="input" type="password" placeholder="Password" aria-label="Password" autoComplete="current-password" />
        <button className="button" type="submit">
          <LogIn size={18} />
          Continue
        </button>
      </form>
    </main>
  );
}
