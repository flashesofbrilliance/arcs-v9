// Feature flags — PLG / RBAC rollout gates.
//
// Env-driven and dependency-free (no new deps per repo policy). Each flag reads
// an env var with a default tuned to the current PLG phase. When RBAC lands,
// flip the env var (or replace this module with the Vercel Flags SDK / a real
// RBAC check) without touching call sites.
//
// publicHistory:
//   false (default, current PLG model) → per-user isolation: GET /api/history
//          requires a session and filters to the caller's own receipts (ADR-001).
//          Sign-up is the lead-capture hook (history + sharing are gated).
//   true  (set PUBLIC_HISTORY=true) → ungated demo mode: recent receipts
//          returned globally with no auth. Use only for a public demo build.

export const flags = {
  // Default OFF → history is tokenized per authenticated user. Set PUBLIC_HISTORY=true for demo.
  publicHistory: process.env.PUBLIC_HISTORY === "true",
} as const

export type Flags = typeof flags
