/** Minimal type shims for the audit layer.
 * Only the shapes the auditor actually reads are defined here.
 * Don't treat this as the full compass/LLM output contract — that lives
 * in the route's parsed object and the SYSTEM prompt OUTPUT SHAPE.
 */

/** What the compass route's parsed LLM output looks like, as consumed by the translator. */
export interface ReceiptJSON {
  coherence_pct?: number | string
  nci_score?: number | string
  is_satoshi?: boolean
  true_north?: string
  reasoning?: {
    fated?: {
      facts?: string
      assumptions?: string
      tradeoffs?: string
      emotions?: string
      direction?: string
    }
    court?: Array<{ name?: string; verdict?: string; detail?: string }>
    geometry?: {
      macros_on?: string[]
      macros_off?: string[]
    }
  }
  meta?: {
    macro_tags?: string[]
  }
}

/** What the audit client's runAudit() receives from the route. */
export interface AuditRequestShape {
  question: string
  horizon: string
  stakes: string
  clarityMode: string
  doorClass: string
  llmOutput: ReceiptJSON
  prep?: { confidence?: string; adversarialInput?: string } | null
  sessionVersion: number
  traceId: string
}
