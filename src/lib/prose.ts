// Deterministic backstop for model-authored prose shown to users. The prompts already
// ask for no dashes and no internal codes; this makes the rule hold when the model
// drifts, and lets stored text (briefs, receipts written before the rule) render clean
// without rewriting the frozen row. It never rewrites meaning, only punctuation and
// internal enum spellings.

// Spaced em/en dashes, and unspaced em-dashes between words, become a colon for the
// first break in a sentence-free span and a comma after that.
export function scrubProse(text: string | null | undefined): string {
  if (!text) return text ?? ""
  let seen = 0
  return text
    .replace(/\s*[—―]\s*|\s+–\s+/g, () => (seen++ === 0 ? ": " : ", "))
    .replace(/\bONE_WAY\b/g, "one-way")
    .replace(/\bTWO_WAY\b/g, "two-way")
    .replace(/: ([,.;:])/g, "$1")
}

export function scrubProseArray(items: unknown): string[] {
  return Array.isArray(items) ? items.map((x) => scrubProse(typeof x === "string" ? x : String(x ?? ""))) : []
}

// Dash-only pass for structured JSON: rewrites punctuation in every string leaf but
// leaves enum values (ONE_WAY, decision_mode) alone, since those are read as codes.
// The user's own words (question / decision) are theirs and are never rewritten.
const USER_AUTHORED_KEYS = new Set(["question", "decision"])

function scrubDashes(text: string): string {
  let seen = 0
  return text
    .replace(/\s*[—―]\s*|\s+–\s+/g, () => (seen++ === 0 ? ": " : ", "))
    .replace(/: ([,.;:])/g, "$1")
}

export function scrubDeep<T>(value: T, key?: string): T {
  if (typeof value === "string") return (key && USER_AUTHORED_KEYS.has(key) ? value : scrubDashes(value)) as T
  if (Array.isArray(value)) return value.map((v) => scrubDeep(v)) as T
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value as Record<string, unknown>).map(([k, v]) => [k, scrubDeep(v, k)])) as T
  }
  return value
}

function scrubJsonText(raw: unknown): unknown {
  if (typeof raw !== "string" || !raw) return raw
  try { return JSON.stringify(scrubDeep(JSON.parse(raw))) } catch { return raw }
}

// Read-path backstop for a stored Receipt row: receipts written before the
// write-time scrub still carry em-dashes in model prose. Rewrites the response
// only; the frozen row is untouched.
export function scrubReceiptProse<R extends Record<string, unknown>>(receipt: R | null | undefined): R | null | undefined {
  if (!receipt) return receipt
  const out: Record<string, unknown> = { ...receipt }
  if (typeof out.trueNorth === "string") out.trueNorth = scrubProse(out.trueNorth)
  if (typeof out.courtVerdict === "string") out.courtVerdict = scrubDashes(out.courtVerdict)
  for (const k of ["whyBullets", "fated", "paths", "court", "rawResponse"]) out[k] = scrubJsonText(out[k])
  if (Array.isArray(out.children)) {
    out.children = out.children.map((c) =>
      c && typeof c === "object" && typeof (c as Record<string, unknown>).trueNorth === "string"
        ? { ...(c as Record<string, unknown>), trueNorth: scrubProse((c as Record<string, unknown>).trueNorth as string) }
        : c)
  }
  return out as R
}
