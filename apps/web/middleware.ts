import { NextResponse, type NextRequest } from "next/server";

const SESSION_COOKIE = "ga_session";

const APP_PREFIXES = [
  "/dashboard",
  "/opportunities",
  "/contracts",
  "/proposals",
  "/library",
  "/past-performance",
  "/partners",
  "/organization",
  "/admin",
];

type Claims = { role?: string; is_super_admin?: boolean; exp?: number };

// Edge-safe JWT claim decode (no signature check — the API verifies on every call).
function decodeClaims(token: string): Claims | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), "=");
    return JSON.parse(atob(padded)) as Claims;
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(SESSION_COOKIE)?.value;
  const claims = token ? decodeClaims(token) : null;
  const isValid = Boolean(claims && (!claims.exp || claims.exp * 1000 > Date.now()));

  const isAppRoute = APP_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));

  if (isAppRoute && !isValid) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  if ((pathname === "/admin" || pathname.startsWith("/admin/")) && isValid && !claims?.is_super_admin) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  if ((pathname === "/login" || pathname === "/register") && isValid) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/login",
    "/register",
    "/dashboard/:path*",
    "/opportunities/:path*",
    "/contracts/:path*",
    "/proposals/:path*",
    "/library/:path*",
    "/past-performance/:path*",
    "/partners/:path*",
    "/organization/:path*",
    "/admin/:path*",
  ],
};
