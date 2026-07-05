"use client";

import { BrandLogo } from "@/components/BrandLogo";
import { LogIn } from "lucide-react";
import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";

function apiBaseUrl() {
  const configuredUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (configuredUrl) return configuredUrl;
  if (typeof window !== "undefined" && window.location.hostname.endsWith("grantatlas.ai")) {
    return "https://api.grantatlas.ai";
  }
  return "http://localhost:8000";
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch(`${apiBaseUrl()}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        setError("Invalid email or password.");
        return;
      }

      const token = await response.json();
      window.localStorage.setItem("grantatlas.access_token", token.access_token);
      window.localStorage.setItem("grantatlas.tenant_id", token.tenant_id);
      window.localStorage.setItem("grantatlas.role", token.role);
      router.push("/dashboard");
    } catch {
      setError("Sign in is unavailable. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-panel stack" onSubmit={handleSubmit}>
        <div className="stack">
          <BrandLogo />
          <h1>Sign in</h1>
        </div>
        <input className="input" type="email" placeholder="owner@example.com" aria-label="Email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        <input className="input" type="password" placeholder="Password" aria-label="Password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        {error ? <p className="form-error" role="alert">{error}</p> : null}
        <button className="button" type="submit" disabled={isSubmitting}>
          <LogIn size={18} />
          {isSubmitting ? "Signing in" : "Continue"}
        </button>
      </form>
    </main>
  );
}
