// What POST /api/compass returns to a signed-in owner (anti-distillation
// ruling 5, option A, 2026-10-20): the product fields plus ids. The full model
// output stays server-side and reaches the owner through the owner-gated
// receipt and brief endpoints the UI already reads. A free magic-link account
// therefore no longer equals full-schema sampling.

export const OWNER_FIELDS = [
  "ok", "receipt_id", "persisted", "session_id", "session_version",
  "true_north", "why", "tributaries", "nci_score",
] as const

export function shapeForOwner(full: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  for (const k of OWNER_FIELDS) if (k in full) out[k] = full[k]
  return out
}
