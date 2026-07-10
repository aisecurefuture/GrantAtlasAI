"use client";

import { useActionState, useEffect, useRef } from "react";
import type { ReactNode } from "react";
import type { ActionState } from "@/app/actions/data";

const initial: ActionState = { ok: false, error: null };

export function ActionForm({
  action,
  submitLabel,
  children,
  resetOnSuccess = true,
  hidden,
  className,
}: {
  action: (prev: ActionState, formData: FormData) => Promise<ActionState>;
  submitLabel: string;
  children: ReactNode;
  resetOnSuccess?: boolean;
  hidden?: Record<string, string>;
  className?: string;
}) {
  const [state, formAction, pending] = useActionState(action, initial);
  const ref = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state.ok && resetOnSuccess) ref.current?.reset();
  }, [state, resetOnSuccess]);

  return (
    <form ref={ref} action={formAction} className={className ? `stack ${className}` : "stack"}>
      {hidden
        ? Object.entries(hidden).map(([key, value]) => <input key={key} type="hidden" name={key} value={value} />)
        : null}
      {children}
      <div className="form-footer">
        <button className="button" type="submit" disabled={pending}>
          {pending ? "Saving…" : submitLabel}
        </button>
        {state.error ? (
          <span className="form-error" role="alert">
            {state.error}
          </span>
        ) : null}
        {state.ok && state.message ? (
          <span className="form-success" role="status">
            {state.message}
          </span>
        ) : null}
      </div>
    </form>
  );
}
