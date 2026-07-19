/**
 * Owner allowlist for internal, authenticated-only surfaces (e.g. /internal).
 *
 * Zero-trust (ADR-032): gate on the SPECIFIC owner, not merely "any logged-in
 * user" — the app has open magic-link signup, so a session alone is not authority.
 * Deny by default: an email is authorized only if it's on the allowlist.
 *
 * Configure via the INTERNAL_EMAILS env var (comma-separated) in Vercel; the
 * fallback is the repo owner (already public in commit metadata). Set the env to
 * whatever address you actually sign in with — if it doesn't match, you're denied
 * (fail-safe), which is the correct behavior.
 */
export const INTERNAL_ALLOW: string[] = (process.env.INTERNAL_EMAILS ?? "zach.harris@gmail.com")
  .split(",")
  .map((s) => s.trim().toLowerCase())
  .filter(Boolean);

export function isOwner(email: string | null | undefined): boolean {
  if (!email) return false;
  return INTERNAL_ALLOW.includes(email.toLowerCase());
}
