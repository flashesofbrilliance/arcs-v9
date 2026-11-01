import { grainOf, num, type FieldSource, type Reading } from './reading'

export const COHERENCE_THRESHOLD = 10

// Lattice property under its own name: diamonds per node. n = nodes.
export function readCoherence(src: FieldSource | null | undefined): Reading {
  const diamonds = num(src?.dimensions?.coherence?.diamonds)
  const nodes = num(src?.dimensions?.clarity?.nodes)
  const base = { id: 'coherence', threshold: COHERENCE_THRESHOLD, source: 'universe-field.json dimensions.coherence', asOf: src?.as_of_date ?? null }
  if (diamonds === null || nodes === null || nodes <= 0) return { ...base, value: null, n: 0, grain: 1 }
  return { ...base, value: diamonds / nodes, n: nodes, grain: grainOf(nodes, COHERENCE_THRESHOLD) }
}
