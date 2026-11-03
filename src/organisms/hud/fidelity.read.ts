import { grainOf, num, type FieldSource, type Reading } from './reading'

export const FIDELITY_THRESHOLD = 10

// Mean per-node evidence certainty: 1 - uncertainty, uncertainty = 1 - min(1, evidence/10),
// evidence = mapped files + commits in 28 days (ruling D4 definition). n = total evidence.
export function readFidelity(src: FieldSource | null | undefined): Reading {
  const nodes = src?.nodes
  const base = { id: 'fidelity', threshold: FIDELITY_THRESHOLD, source: 'universe-field.json nodes', asOf: src?.as_of_date ?? null }
  if (!Array.isArray(nodes) || nodes.length === 0) return { ...base, value: null, n: 0, grain: 1 }
  let sum = 0, n = 0
  for (const nd of nodes) {
    const ev = (num(nd.files) ?? 0) + (num(nd.sig?.frequency?.last_28d) ?? 0)
    n += ev
    sum += Math.min(1, ev / 10)
  }
  return { ...base, value: sum / nodes.length, n, grain: grainOf(n, FIDELITY_THRESHOLD) }
}
