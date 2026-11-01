import { grainOf, num, type FieldSource, type Reading } from './reading'

export const CLARITY_THRESHOLD = 10

// Share of lattice nodes that are clear. n = nodes.
export function readClarity(src: FieldSource | null | undefined): Reading {
  const d = src?.dimensions?.clarity
  const clear = num(d?.nodes_clear), nodes = num(d?.nodes)
  const base = { id: 'clarity', threshold: CLARITY_THRESHOLD, source: 'universe-field.json dimensions.clarity', asOf: src?.as_of_date ?? null }
  if (clear === null || nodes === null || nodes <= 0) return { ...base, value: null, n: 0, grain: 1 }
  return { ...base, value: clear / nodes, n: nodes, grain: grainOf(nodes, CLARITY_THRESHOLD) }
}
