// Recruiter ammo-tier gate — a lightweight, single-secret passcode gate for the
// recruithaus.arcs.care /ammo surface (the gated companion to the open pitch page).
//
// Why this exists (and why it is NOT the /recoil Auth.js gate): the ammo tier is
// meant to be opened by an *external* recruiter (Amy) with a shared passcode, not
// by an ADMIN_EMAILS session. The old RECOIL_PASSWORD cookie was retired because
// it sat disclosed in git history; this gate keeps the secret in an env var
// (RECRUITHAUS_AMMO_PASSWORD) and never writes it into the repo. The cookie stores
// a SHA-256 token derived from the secret, never the secret itself, so a leaked
// cookie does not reveal the passcode. Web Crypto only, so the same helper runs in
// both the Edge middleware (proxy.ts) and the Node route handler.
//
// Threat model: deterrence + non-discoverability for a trusted counterpart, not
// secrecy against a determined attacker. Founder identities are referred to by
// lens/archetype (never by name) even inside the gate, per the air-gap doctrine.

export const AMMO_COOKIE = "rh_ammo"

/** SHA-256 hex of the secret, domain-separated so the token is unique to this gate. */
export async function ammoToken(secret: string): Promise<string> {
  const data = new TextEncoder().encode("rh-ammo:" + secret)
  const digest = await crypto.subtle.digest("SHA-256", data)
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
}

/** True only if the cookie value matches the token derived from the configured secret. */
export async function ammoUnlocked(
  cookieValue: string | undefined,
  secret: string | undefined,
): Promise<boolean> {
  if (!cookieValue || !secret) return false
  const expected = await ammoToken(secret)
  if (cookieValue.length !== expected.length) return false
  // Length-matched constant-ish compare (values are non-secret hex digests).
  let diff = 0
  for (let i = 0; i < expected.length; i++) {
    diff |= cookieValue.charCodeAt(i) ^ expected.charCodeAt(i)
  }
  return diff === 0
}
