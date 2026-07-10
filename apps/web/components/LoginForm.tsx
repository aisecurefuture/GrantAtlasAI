"use client";

import { LogIn } from "lucide-react";
import { useActionState } from "react";
import { loginAction, type LoginState } from "@/app/actions/auth";

const initialState: LoginState = { error: null };

export function LoginForm({ next }: { next: string }) {
  const [state, formAction, pending] = useActionState(loginAction, initialState);

  return (
    <form className="stack" action={formAction}>
      <input type="hidden" name="next" value={next} />
      <label className="field">
        <span className="field-label">Email</span>
        <input
          className="input"
          type="email"
          name="email"
          placeholder="owner@example.org"
          aria-label="Email"
          autoComplete="email"
          required
        />
      </label>
      <label className="field">
        <span className="field-label">Password</span>
        <input
          className="input"
          type="password"
          name="password"
          placeholder="Your password"
          aria-label="Password"
          autoComplete="current-password"
          required
        />
      </label>
      {state.error ? (
        <p className="form-error" role="alert">
          {state.error}
        </p>
      ) : null}
      <button className="button" type="submit" disabled={pending}>
        <LogIn size={18} />
        {pending ? "Signing in…" : "Continue"}
      </button>
    </form>
  );
}
