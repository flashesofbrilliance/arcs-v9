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
