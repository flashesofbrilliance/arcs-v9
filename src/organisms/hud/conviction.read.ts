import { type FieldSource, type Reading } from './reading'

// No threshold: no reading until receipts are tagged real (0 tagged real as of 2026-10-18).
// Even a numeric signal in the source is not shown; the view prints "No signal".
export function readConviction(src: FieldSource | null | undefined): Reading {
  return { id: 'conviction', value: null, n: 0, threshold: null, grain: 1, asOf: src?.as_of_date ?? null, source: 'Receipt provenance tags' }
}
