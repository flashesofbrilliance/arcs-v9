// Job Factory slice 3 (2026-10-05): a card dropped into the Lane's Outcome column
// closes with a fate and a reason, written as a LaneOutcome row. One reason list
// for the whole board: the left-swipe WHY tags and the outcome reasons are the
// same taxonomy, so Debrief can count losses by reason across both.
// Outcomes are human-only: a receipt cannot close itself (AGENTS.md outcome row),
// so the lane route refuses an outcome write from the pipeline token.

export const REASONS = ["comp", "location", "role shape", "seniority", "culture", "company", "timing", "other"] as const

// fate key -> LaneOutcome.fate (schema: closed:won | closed:lost | closed:learned)
export const FATES = {
  offer: "closed:won",
  reject: "closed:lost",
  ghosted: "closed:lost",
  withdrawn: "closed:learned",
} as const
export type FateKey = keyof typeof FATES

export type OutcomeInput = { fate: FateKey; reason: string | null; note: string | null }

// Validate a client body. A loss (reject, ghosted, withdrawn) needs a reason from
// REASONS; an offer may carry one (what won it) but does not have to.
export function parseOutcome(body: unknown): OutcomeInput | { error: string } {
  const b = (body ?? {}) as Record<string, unknown>
  const fate = String(b.fate ?? "")
  if (!(fate in FATES)) return { error: `fate must be one of ${Object.keys(FATES).join(", ")}` }
  const reason = b.reason == null || b.reason === "" ? null : String(b.reason)
  if (reason !== null && !(REASONS as readonly string[]).includes(reason)) return { error: `reason must be one of ${REASONS.join(", ")}` }
  if (fate !== "offer" && reason === null) return { error: "a reason is required for reject, ghosted, or withdrawn" }
  const note = b.note == null ? null : String(b.note).trim().slice(0, 500) || null
  return { fate: fate as FateKey, reason, note }
}

// actualNote holds "reason" or "reason · note"; Debrief counts by the part before " · ".
export function outcomeNote(o: OutcomeInput): string | null {
  if (!o.reason && !o.note) return null
  return [o.reason, o.note].filter(Boolean).join(" · ")
}

export function reasonOf(actualNote: string | null | undefined): string | null {
  if (!actualNote) return null
  const head = actualNote.split(" · ")[0]
  return (REASONS as readonly string[]).includes(head) ? head : null
}
