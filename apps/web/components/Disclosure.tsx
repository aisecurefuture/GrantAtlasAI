"use client";

import { Plus, X } from "lucide-react";
import { useState } from "react";
import type { ReactNode } from "react";

export function Disclosure({
  label,
  children,
  variant = "primary",
}: {
  label: string;
  children: ReactNode;
  variant?: "primary" | "secondary";
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="disclosure">
      <button
        type="button"
        className={variant === "primary" ? "button" : "button secondary"}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        {open ? <X size={18} /> : <Plus size={18} />}
        {open ? "Close" : label}
      </button>
      {open ? <div className="disclosure-panel card">{children}</div> : null}
    </div>
  );
}
