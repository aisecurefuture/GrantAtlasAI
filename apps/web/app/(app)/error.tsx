"use client";

import { RefreshCcw } from "lucide-react";

export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const unauthenticated = error.message === "UNAUTHENTICATED";

  return (
    <div className="card empty-state" role="alert">
      <p>{unauthenticated ? "Your session has expired." : "Something went wrong loading this page."}</p>
      <p className="muted">
        {unauthenticated
          ? "Sign in again to continue."
          : "The GrantAtlas API may be briefly unavailable. Try again in a moment."}
      </p>
      {unauthenticated ? (
        <a className="button" href="/login">
          Sign in
        </a>
      ) : (
        <button className="button" onClick={() => reset()}>
          <RefreshCcw size={16} />
          Try again
        </button>
      )}
    </div>
  );
}
