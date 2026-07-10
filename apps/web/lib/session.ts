import "server-only";
import { cookies } from "next/headers";

export const SESSION_COOKIE = "ga_session";

export type SessionClaims = {
  sub: string;
  tenant_id: string;
  role: string;
  is_super_admin: boolean;
  exp: number;
};

export type Session = {
  token: string;
  claims: SessionClaims;
};

function decodeJwtClaims(token: string): SessionClaims | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), "=");
    const json = Buffer.from(padded, "base64").toString("utf8");
    const data = JSON.parse(json);
    if (typeof data.sub !== "string" || typeof data.tenant_id !== "string") return null;
    return {
      sub: data.sub,
      tenant_id: data.tenant_id,
      role: data.role ?? "Viewer",
      is_super_admin: Boolean(data.is_super_admin),
      exp: Number(data.exp ?? 0),
    };
  } catch {
    return null;
  }
}

/**
 * Read the current session from the httpOnly cookie. Returns null when there is
 * no valid, unexpired token. The JWT is verified server-side by the API on every
 * request; here we only decode claims for routing/UI, so no signature check.
 */
export async function getSession(): Promise<Session | null> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  if (!token) return null;
  const claims = decodeJwtClaims(token);
  if (!claims) return null;
  if (claims.exp && claims.exp * 1000 < Date.now()) return null;
  return { token, claims };
}

export async function requireSession(): Promise<Session> {
  const session = await getSession();
  if (!session) {
    throw new Error("UNAUTHENTICATED");
  }
  return session;
}

const cookieMaxAge = 60 * 60 * 12; // 12h, matches API ACCESS_TOKEN_EXPIRE_MINUTES default

export async function setSessionCookie(token: string): Promise<void> {
  const store = await cookies();
  store.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: cookieMaxAge,
  });
}

export async function clearSessionCookie(): Promise<void> {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
}
