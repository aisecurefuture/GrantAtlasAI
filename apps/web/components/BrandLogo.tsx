import Link from "next/link";

type BrandLogoProps = {
  href?: string;
  label?: string;
  showWordmark?: boolean;
  tone?: "dark" | "light";
  className?: string;
};

function GrantAtlasMark({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" role="img" aria-label="GrantAtlas mark">
      <rect width="64" height="64" rx="15" fill="#102033" />
      <path d="M13 22c9.5-5.4 21-5.4 38 0" fill="none" stroke="#6BB7FF" strokeWidth="3.2" strokeLinecap="round" />
      <path d="M13 32c11.5-4.7 24.5-4.7 38 0" fill="none" stroke="#D8ECFF" strokeWidth="2.4" strokeLinecap="round" opacity="0.88" />
      <path d="M13 42c9.5 5.4 21 5.4 38 0" fill="none" stroke="#42D7BE" strokeWidth="3.2" strokeLinecap="round" />
      <path d="M32 11v42" fill="none" stroke="#D8ECFF" strokeWidth="2.2" strokeLinecap="round" opacity="0.72" />
      <path d="M20 48 45 19" fill="none" stroke="#37A2FF" strokeWidth="5" strokeLinecap="round" />
      <path d="M45 19 43.5 31.5 33.4 22.8Z" fill="#42D7BE" />
      <circle cx="21" cy="48" r="4.2" fill="#F8FBFF" />
      <circle cx="21" cy="48" r="2" fill="#37A2FF" />
    </svg>
  );
}

export function BrandLogo({ href, label = "GrantAtlas.ai", showWordmark = true, tone = "dark", className = "" }: BrandLogoProps) {
  const content = (
    <>
      <GrantAtlasMark className="brand-logo-mark" />
      {showWordmark ? (
        <span className="brand-logo-wordmark" data-tone={tone}>
          <span>GrantAtlas</span>
          <span className="brand-logo-dot">.ai</span>
        </span>
      ) : null}
    </>
  );

  if (href) {
    return (
      <Link href={href} className={`brand-logo ${className}`} aria-label={label}>
        {content}
      </Link>
    );
  }

  return (
    <div className={`brand-logo ${className}`} aria-label={label}>
      {content}
    </div>
  );
}

