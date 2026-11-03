import { grainOf, num, type Reading } from './reading'

export const CONSONANCE_THRESHOLD = 30

export interface ConsonanceSource {
  closed?: number            // closed receipts in the cohort
  meanNci?: number | null    // 0..1
  matchedRate?: number | null // 0..1
  asOf?: string | null
}

// Gap between stated confidence (mean NCI) and matched-outcome rate, per cohort.
// Needs 30 closed receipts (the Accountant rule). No source is wired yet, so n is 0.
export function readConsonance(src: ConsonanceSource | null | undefined): Reading {
  const closed = num(src?.closed) ?? 0
  const nci = num(src?.meanNci), hit = num(src?.matchedRate)
  const base = { id: 'consonance', threshold: CONSONANCE_THRESHOLD, source: 'Receipt.nciScore vs Outcome.matched', asOf: src?.asOf ?? null }
  if (closed <= 0 || nci === null || hit === null) return { ...base, value: null, n: closed, grain: grainOf(closed, CONSONANCE_THRESHOLD) }
  return { ...base, value: Math.abs(nci - hit), n: closed, grain: grainOf(closed, CONSONANCE_THRESHOLD) }
}
