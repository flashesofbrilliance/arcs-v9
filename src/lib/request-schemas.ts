import { z } from "zod"

// Every thread id is minted by crypto.randomUUID(); anything else is refused
// (re-minted), so a caller cannot pick a guessable, low-entropy id.
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
export const isThreadId = (v: unknown): v is string => typeof v === "string" && UUID_RE.test(v)

// Request-body schemas for the decision routes (ledger CMP-020). Kept out of
// the route files so tests can import them without Next/Prisma.

// Receipt.provenance: "real" | "test". Set by the owner only, never guessed
// (prisma/schema.prisma); the Accountant splits cohorts on it. Null is not a
// value a caller can send: an owner corrects a tag by re-tagging.
export const ProvenanceValue = z.enum(["real", "test"])

// POST /api/receipts/[receiptId]/provenance body.
export const ProvenanceBody = z.object({ provenance: ProvenanceValue })

// POST /api/compass envelope. Unknown keys are stripped; the route still
// narrows nested prep fields by hand and clamps long text.
export const CompassBody = z.object({
  question: z.string().max(8000),
  horizon: z.string().max(32).nullish().transform((v) => v ?? undefined),
  stakes: z.string().max(32).nullish().transform((v) => v ?? undefined),
  prepId: z.string().max(64).nullish(),
  prep: z.record(z.string(), z.unknown()).nullish(),
  parentReceiptId: z.string().max(64).nullish(),
  // Which of the parent's three tributaries the question came from (0 meta,
  // 1 challenge, 2 adjacent; AGENTS.md "DEWY pipeline"). Persisted as
  // Receipt.parentTributaryIndex only when the parent itself is accepted (see
  // tributaryIndexFor). A string "1" is refused: the dashboard parses the
  // ?tributary= param before sending, so a number is the only honest shape.
  tributaryIndex: z.number().int().min(0).max(2).nullish(),
  // No length cap: a bad id must reach resolveOwnedSessionId and be re-minted
  // (409 session_reassigned), never fail the whole parse with a 400.
  sessionId: z.string().nullish(),
  clarityMode: z.string().max(32).nullish().transform((v) => v ?? undefined),
  // Owner-declared provenance + resolve-by date (YYYY-MM-DD). Both optional; see Receipt.provenance.
  provenance: ProvenanceValue.nullish(),
  resolveBy: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).nullish(),
})

// Lineage edge for the persisted receipt: the tributary index is meaningful
// only on a receipt whose parent was accepted (owned by the caller). When the
// parent is dropped (missing, foreign, or an anonymous run), the index is
// dropped with it, so a bare index can never point at a parent that was refused.
export function tributaryIndexFor(parentAccepted: boolean, index: number | null | undefined): number | null {
  return parentAccepted && typeof index === "number" ? index : null
}

// POST /api/prep. Hand parsing let a non-string entity 500 on .trim().
const optText = (max: number) => z.string().trim().max(max).nullish().transform((v) => v || null)
export const PrepBody = z.object({
  stakes: z.string().max(32).nullish(),
  horizon: z.string().max(32).nullish(),
  protecting: z.array(z.string().max(200)).max(8).nullish(),
  confidence: z.number().finite().min(0).max(100).nullish(),
  entity: optText(500),
  adversarialInput: optText(2000),
  outcomeHorizon: optText(500),
})

// POST /api/receipts/save envelope: required text is typed and capped; the
// route narrows the rest of the client-attested bearing field by field.
export const SaveBody = z.object({
  bearing: z.looseObject({
    question: z.string().max(8000),
    true_north: z.string().max(4000),
  }),
})
