// Feature flags — PLG / RBAC rollout gates.
//
// Env-driven and dependency-free (no new deps per repo policy). Each flag reads
// an env var with a default tuned to the current PLG phase. When RBAC lands,
// flip the env var (or replace this module with the Vercel Flags SDK / a real
// RBAC check) without touching call sites.
//
// publicHistory:
//   true  (default, current PLG/demo phase) → GET /api/history is ungated:
//          recent receipts returned globally, no auth, no userId filter.
//   false (set PUBLIC_HISTORY=false once RBAC is ready) → per-user isolation:
//          requires a session, filters to the caller's own receipts (ADR-001).

export const flags = {
  // Default ON until RBAC for the PLG motion is ready. Set PUBLIC_HISTORY=false to gate.
  publicHistory: process.env.PUBLIC_HISTORY !== "false",
} as const

export type Flags = typeof flags
