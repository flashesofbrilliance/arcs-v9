import type { Session } from "next-auth"

// Interim RBAC — an email allowlist standing in for a real User.role field.
// The recoil surface (/recoil index + /recoil/[reportId]) is internal: User0
// today, admin roles later. Until a role column exists, membership is the
// comma-separated ADMIN_EMAILS env var, checked against the signed-in session.
//
// Doctrine (matches ADR-001 soft-auth used across /api and /recoil/[reportId]):
//   • production → only listed emails are admin (fail-closed if the var is unset)
//   • development → pass-through, so local visual QA needs no magic-link session
// Callers gate on isAdmin(session) in prod and skip the check in dev.

export function adminEmails(): string[] {
  return (process.env.ADMIN_EMAILS ?? "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean)
}

export function isAdminEmail(email: string | null | undefined): boolean {
  if (!email) return false
  return adminEmails().includes(email.toLowerCase())
}

export function isAdmin(session: Session | null): boolean {
  return isAdminEmail(session?.user?.email)
}
