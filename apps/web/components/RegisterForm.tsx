"use client";

import { UserPlus } from "lucide-react";
import { useActionState, useState } from "react";
import { registerAction, type RegisterState } from "@/app/actions/auth";

const initialState: RegisterState = { error: null };

type Plan = { id: string; price: string; seats: string; blurb: string };

export function RegisterForm({ plans, preselected }: { plans: Plan[]; preselected: string }) {
  const [state, formAction, pending] = useActionState(registerAction, initialState);
  const [plan, setPlan] = useState(preselected);

  return (
    <form className="stack" action={formAction}>
      <input type="hidden" name="plan" value={plan} />
      <div className="plan-picker" role="radiogroup" aria-label="Subscription plan">
        {plans.map((p) => (
          <button
            key={p.id}
            type="button"
            role="radio"
            aria-checked={plan === p.id}
            className="plan-option"
            data-selected={plan === p.id}
            onClick={() => setPlan(p.id)}
          >
            <strong>{p.id}</strong>
            <span className="plan-price">{p.price}</span>
            <span className="muted">{p.seats}</span>
            <span className="muted plan-blurb">{p.blurb}</span>
          </button>
        ))}
      </div>

      <div className="grid cols-2">
        <label className="field">
          <span className="field-label">Organization name *</span>
          <input className="input" name="organization_name" required maxLength={255} />
        </label>
        <label className="field">
          <span className="field-label">Your name *</span>
          <input className="input" name="name" required maxLength={255} />
        </label>
      </div>
      <div className="grid cols-2">
        <label className="field">
          <span className="field-label">Work email *</span>
          <input className="input" type="email" name="email" autoComplete="email" required />
        </label>
        <label className="field">
          <span className="field-label">Password * (10+ characters)</span>
          <input className="input" type="password" name="password" autoComplete="new-password" minLength={10} required />
        </label>
      </div>

      {state.error ? (
        <p className="form-error" role="alert">
          {state.error}
        </p>
      ) : null}
      <button className="button" type="submit" disabled={pending}>
        <UserPlus size={18} />
        {pending ? "Creating your workspace…" : `Start free trial on ${plan}`}
      </button>
    </form>
  );
}
