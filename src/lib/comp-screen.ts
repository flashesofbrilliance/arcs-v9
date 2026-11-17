// Salary screen for the jobs board (Zach, 2026-11-16). The floor lives in runtime/specs/target-role-scan.json
// (rubric.comp_floor_usd) and is judged against the TOP of a posted range: a role whose max reaches the floor
// passes, a range that tops out below it is gated. "Starting at" pay and non-USD pay have no USD max, so they
// are never gated. Pure functions; tests in tests/unit/comp-screen.test.ts.

export type UsdRange = { min: number | null; max: number | null }

const NON_USD = /\b(CAD|GBP|EUR|AUD|INR|SGD|JPY)\b|£|€|C\$|A\$/i

function toUsd(n: string, k: string | undefined): number {
  const v = Number(n.replace(/,/g, ""))
  return Math.round(k ? v * 1000 : v)
}

export function parseUsdRange(text: string | null | undefined): UsdRange | null {
  const s = String(text ?? "")
  if (!s || NON_USD.test(s)) return null
  const amounts = [...s.matchAll(/\$\s?(\d{2,3}(?:,\d{3})*(?:\.\d+)?)\s?([kK])?/g)].map((m) => toUsd(m[1], m[2]))
    .filter((v) => v >= 20000)
  if (!amounts.length) return null
  if (/\bup to\b/i.test(s) && amounts.length === 1) return { min: null, max: amounts[0] }
  if (/\b(starting at|from)\b/i.test(s) && amounts.length === 1) return { min: amounts[0], max: null }
  if (amounts.length === 1) return { min: amounts[0], max: amounts[0] }
  return { min: Math.min(amounts[0], amounts[1]), max: Math.max(amounts[0], amounts[1]) }
}

export function compScreen(text: string | null | undefined, floor: number): { below: boolean; max: number | null } {
  const r = parseUsdRange(text)
  const max = r?.max ?? null
  return { below: max !== null && max < floor, max }
}

export const COMP_GATE = "Posted pay range tops out below the floor"
