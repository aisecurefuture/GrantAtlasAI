"use client";

import { useActionState } from "react";
import { startCheckoutAction, openBillingPortalAction, type ActionState } from "@/app/actions/data";
import type { BillingSummary } from "@/lib/types";

const initial: ActionState = { ok: false, error: null };

export function BillingPlans({
  plans,
  currentPlan,
  stripeConfigured,
  customerConnected,
}: {
  plans: BillingSummary["available_plans"];
  currentPlan: string;
  stripeConfigured: boolean;
  customerConnected: boolean;
}) {
  const [checkoutState, checkout, checkingOut] = useActionState(startCheckoutAction, initial);
  const [portalState, portal, openingPortal] = useActionState(openBillingPortalAction, initial);

  return (
    <section className="stack">
      <div className="section-head" style={{ marginBottom: 0 }}>
        <h2>Plans</h2>
        {customerConnected ? (
          <form action={portal}>
            <button className="button secondary" type="submit" disabled={openingPortal}>
              {openingPortal ? "Opening…" : "Manage subscription"}
            </button>
          </form>
        ) : null}
      </div>
      {checkoutState.error ? <p className="form-error">{checkoutState.error}</p> : null}
      {portalState.error ? <p className="form-error">{portalState.error}</p> : null}

      <div className="pricing-grid">
        {plans.map((plan) => {
          const isCurrent = plan.name === currentPlan;
          return (
            <article className="pricing-card" data-featured={plan.id === "Professional"} key={plan.id}>
              <div className="pricing-card-head">
                <h3>{plan.name}</h3>
                {isCurrent ? <span className="pill high">Current</span> : null}
              </div>
              <div>
                <strong>${plan.price_monthly}</strong>
                <span className="muted">/mo</span>
              </div>
              <p className="pricing-detail">${plan.price_annual}/mo billed annually · {plan.seats}</p>
              <p>{plan.blurb}</p>
              <form action={checkout}>
                <input type="hidden" name="plan" value={plan.id} />
                <button className="button" type="submit" disabled={!stripeConfigured || checkingOut || isCurrent}>
                  {isCurrent ? "Active plan" : checkingOut ? "Starting…" : plan.id === "Enterprise" ? "Contact sales" : "Choose plan"}
                </button>
              </form>
            </article>
          );
        })}
      </div>
    </section>
  );
}
