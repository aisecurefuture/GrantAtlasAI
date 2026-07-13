"use server";

import { redirect } from "next/navigation";
import { setSessionCookie, clearSessionCookie } from "@/lib/session";

const API_BASE_URL = process.env.API_SERVER_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type LoginState = { error: string | null };

export async function loginAction(_prev: LoginState, formData: FormData): Promise<LoginState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const next = String(formData.get("next") ?? "/dashboard");

  if (!email || !password) {
    return { error: "Enter your email and password." };
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ email, password }),
      cache: "no-store",
    });
  } catch {
    return { error: "Sign in is temporarily unavailable. Please try again." };
  }

  if (response.status === 429) {
    return { error: "Too many attempts. Please wait a few minutes and try again." };
  }
  if (!response.ok) {
    return { error: "Invalid email or password." };
  }

  const data = (await response.json()) as { access_token?: string };
  if (!data.access_token) {
    return { error: "Sign in failed. Please try again." };
  }

  await setSessionCookie(data.access_token);
  const safeNext = next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";
  redirect(safeNext);
}

export async function logoutAction(): Promise<void> {
  await clearSessionCookie();
  redirect("/login");
}

export type RegisterState = { error: string | null };

export async function registerAction(_prev: RegisterState, formData: FormData): Promise<RegisterState> {
  const organization_name = String(formData.get("organization_name") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const plan = String(formData.get("plan") ?? "");

  if (!organization_name || !name || !email || !password) {
    return { error: "Fill in all fields." };
  }
  if (!plan) {
    return { error: "Choose a subscription plan to continue." };
  }
  if (password.length < 10) {
    return { error: "Password must be at least 10 characters." };
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL.replace(/\/$/, "")}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ organization_name, name, email, password, plan }),
      cache: "no-store",
    });
  } catch {
    return { error: "Registration is temporarily unavailable. Please try again." };
  }

  if (!response.ok) {
    if (response.status === 409) return { error: "An account with this email already exists. Try signing in instead." };
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    return { error: body?.detail || "Registration failed. Please try again." };
  }

  const data = (await response.json()) as { access_token?: string };
  if (!data.access_token) return { error: "Registration failed. Please try again." };

  await setSessionCookie(data.access_token);
  redirect("/organization");
}
