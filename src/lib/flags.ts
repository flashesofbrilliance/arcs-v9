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
  // Default OFF → Profile Scan (/scan) is a staging-only surface for scan.arcs.care.
  // Set SCAN_ENABLED=true to render it. See ADR-028.
  scanEnabled: process.env.SCAN_ENABLED === "true",
  // Default OFF → the in-app outcome-capture nudge (ripe-to-close banner on the
  // dashboard) is dogfood-gated. Copy is draft-first and must clear a Zach
  // bless before it reaches any real user, so it ships dark. The DASHBOARD reads
  // NEXT_PUBLIC_OUTCOME_NUDGE (client-inlined) to mount the banner; this
  // server-side mirror is for any server gate. Flip both to widen (the
  // write-lock-paradox governor: narrow default, widen only on evidence).
  outcomeNudge: process.env.OUTCOME_NUDGE === "true",
  // Default OFF → the v1.1 copy of the ephemeral-receipt save nudge (named
  // exchange + a real "Let it go" dismiss) ships dark; OFF renders the July
  // 2026 banner unchanged. Draft-first: Zach blesses the copy before this is
  // flipped for any real user. The RECEIPT PAGE reads
  // NEXT_PUBLIC_RECEIPT_SAVE_NUDGE_V11 (client-inlined); this is the server
  // mirror. Spec: _SPECS/receipt-save-nudge-v1.md §6.3.
  receiptSaveNudgeV11: process.env.RECEIPT_SAVE_NUDGE_V11 === "true",
} as const

export type Flags = typeof flags
