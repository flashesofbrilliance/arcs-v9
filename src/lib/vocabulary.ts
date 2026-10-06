// The Ahmed order: one vocabulary shared by the receipt page, the brief page
// and the decision_receipt ledger. Same concept, same word, same position.
// Spec + source map: runtime/specs/ahmed-order-vocabulary.md
// Change a user-facing label here and nowhere else.

export type AhmedSlot = "verdict" | "reasons" | "questions" | "tasks" | "evidence"

export interface SlotVocabulary {
  /** Render position, 1 = top. Evidence is always behind the fold. */
  order: number
  /** The ONE user-facing label. */
  label: string
  /** Receipt/Brief fields that fill the slot on the pages. */
  pageFields: readonly string[]
  /** decision_receipt columns that fill the slot in the ledger. */
  ledgerColumns: readonly string[]
  /** How many items the slot holds; null = one statement. */
  count: number | null
  /** Rendered collapsed (behind the fold). */
  folded: boolean
}

export const AHMED_ORDER: Record<AhmedSlot, SlotVocabulary> = {
  verdict: {
    order: 1,
    label: "True North",
    pageFields: ["trueNorth", "yState", "renderResolution", "mode", "doorClass", "stakes"],
    ledgerColumns: ["question", "mode", "stakes"],
    count: null,
    folded: false,
  },
  reasons: {
    order: 2,
    label: "Reasons",
    pageFields: ["whyBullets"],
    ledgerColumns: ["what_confirmed"],
    count: 3,
    folded: false,
  },
  questions: {
    order: 3,
    label: "Open questions",
    pageFields: ["atgTributaries", "situationFraming"],
    ledgerColumns: ["what_unconfirmed"],
    count: 3,
    folded: false,
  },
  tasks: {
    order: 4,
    label: "Next moves",
    pageFields: ["paths", "horizon"],
    ledgerColumns: ["horizon"],
    count: null,
    folded: false,
  },
  evidence: {
    order: 5,
    label: "Evidence",
    pageFields: ["fated", "court", "courtVerdict", "nciScore", "coherencePct", "macroTags", "version", "parentId", "createdAt"],
    ledgerColumns: ["refs", "event_at", "operator", "source_repo"],
    count: null,
    folded: true,
  },
} as const

/** The decision being made: a call, a bet or a choice (one-way or two-way door).
 *  Shown above True North as its subject line. */
export const SUBJECT_LABEL = "Decision"

export const AHMED_SLOTS: readonly AhmedSlot[] = (Object.keys(AHMED_ORDER) as AhmedSlot[])
  .sort((a, b) => AHMED_ORDER[a].order - AHMED_ORDER[b].order)

export const slotLabel = (slot: AhmedSlot): string => AHMED_ORDER[slot].label
