"use client";

import Link from "next/link";
import { ArrowRight, Check, PartyPopper, X } from "lucide-react";
import { useTransition } from "react";
import { dismissOnboardingAction } from "@/app/actions/data";
import type { OnboardingStatus } from "@/lib/types";

export function OnboardingChecklist({ status }: { status: OnboardingStatus }) {
  const [pending, startTransition] = useTransition();

  if (status.dismissed) return null;

  const pct = Math.round((status.completed / status.total) * 100);
  const nextStep = status.steps.find((s) => !s.done);

  function dismiss() {
    startTransition(async () => {
      await dismissOnboardingAction();
    });
  }

  return (
    <section className="onboarding card" aria-label="Getting started checklist">
      <div className="onboarding-head">
        <div className="stack" style={{ gap: 4 }}>
          <p className="eyebrow" style={{ margin: 0 }}>
            {status.all_complete ? "You're all set" : "Getting started"}
          </p>
          <h2>
            {status.all_complete ? (
              <>
                <PartyPopper size={20} style={{ verticalAlign: "-3px", marginRight: 6 }} />
                {status.organization_name} is ready to win funding
              </>
            ) : (
              `Welcome, ${status.organization_name}`
            )}
          </h2>
          <p className="muted">
            {status.all_complete
              ? "Every setup step is done. Dismiss this to reclaim the space — you can always revisit each area from the sidebar."
              : "A few quick steps unlock scoring, AI drafting, and your funding pipeline."}
          </p>
        </div>
        <button
          className="button ghost onboarding-dismiss"
          type="button"
          onClick={dismiss}
          disabled={pending}
          title="Dismiss getting started"
        >
          <X size={16} />
          {pending ? "Hiding…" : "Dismiss"}
        </button>
      </div>

      <div className="onboarding-progress">
        <div className="onboarding-progress-track">
          <div className="onboarding-progress-fill" style={{ width: `${Math.max(4, pct)}%` }} />
        </div>
        <span className="onboarding-progress-label">
          {status.completed} of {status.total} complete
        </span>
      </div>

      <ol className="onboarding-steps">
        {status.steps.map((step) => {
          const isNext = !step.done && step.key === nextStep?.key;
          return (
            <li key={step.key} className={`onboarding-step${step.done ? " done" : ""}${isNext ? " next" : ""}`}>
              <span className="onboarding-check" aria-hidden="true">
                {step.done ? <Check size={16} /> : <span className="onboarding-dot" />}
              </span>
              <div className="onboarding-step-body">
                <strong>{step.title}</strong>
                <span className="muted">{step.description}</span>
              </div>
              {step.done ? (
                <span className="pill high onboarding-step-status">Done</span>
              ) : (
                <Link className={isNext ? "button" : "button secondary"} href={step.cta_href}>
                  {step.cta_label}
                  <ArrowRight size={15} />
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}
