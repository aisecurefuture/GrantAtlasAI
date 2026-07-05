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
        <input className="input" type="email" defaultValue="owner@gratitech.org" aria-label="Email" />
        <input className="input" type="password" defaultValue="ChangeMe123!" aria-label="Password" />
        <button className="button" type="submit">
          <LogIn size={18} />
          Continue
        </button>
      </form>
    </main>
  );
}
