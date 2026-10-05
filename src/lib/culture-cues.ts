// Culture evidence for the jobs scorer (Job Factory slice 1, 2026-10-05).
// A zero-token regex pass over the JD, run before the model: every hit is kept
// as the sentence it came from, so the culture score cites the posting instead
// of the model's impression. The phrase lists live in the rubric spec
// (runtime/specs/target-role-scan.json -> rubric.culture_cues), not here.
// Patterns are wrapped in word-edge lookarounds (a \b would refuse "top 1%"): the 2025 prototype's bare /ai/
// matched "said" and "email", which is the failure this exists to prevent.

export type Cue = { id: string; label: string; pattern: string }
export type CultureCues = { positive: Cue[]; negative: Cue[]; cap_neg?: number; cap_value?: number; gate?: string }
export type CultureHits = { pos: string[]; neg: string[] }

const QUOTE_MAX = 160

function sentences(jd: string): string[] {
  return jd.replace(/\s+/g, " ").split(/(?<=[.!?;•])\s+|\s[-•·]\s/).map((s) => s.trim()).filter(Boolean)
}

function quote(sentence: string, at: number): string {
  if (sentence.length <= QUOTE_MAX) return sentence
  const start = Math.max(0, Math.min(at - 60, sentence.length - QUOTE_MAX))
  return `${start > 0 ? "…" : ""}${sentence.slice(start, start + QUOTE_MAX).trim()}${start + QUOTE_MAX < sentence.length ? "…" : ""}`
}

// One hit per cue (the first sentence it fires in), formatted "Label: quote".
function scan(jd: string, cues: Cue[]): string[] {
  const out: string[] = []
  const ss = sentences(jd)
  for (const c of cues) {
    const re = new RegExp(`(?<!\\w)(?:${c.pattern})(?!\\w)`, "i")
    for (const s of ss) {
      const m = re.exec(s)
      if (m) { out.push(`${c.label}: ${quote(s, m.index)}`); break }
    }
  }
  return out
}

export function extractCultureCues(jd: string, cues: CultureCues): CultureHits {
  return { pos: scan(jd || "", cues.positive), neg: scan(jd || "", cues.negative) }
}

// Mechanical guard rail: enough negative phrases cap the culture dim and fire
// the grind gate. Returns new dims/gates; never raises a score.
export function applyCultureGuard(dims: Record<string, number>, gates: string[], hits: CultureHits, cues: CultureCues): { dims: Record<string, number>; gates: string[] } {
  const capNeg = cues.cap_neg ?? 2
  if (hits.neg.length < capNeg) return { dims, gates }
  const capValue = cues.cap_value ?? 1
  const next = { ...dims, culture: Math.min(Number(dims.culture) || 0, capValue) }
  const g = cues.gate && !gates.includes(cues.gate) ? [...gates, cues.gate] : gates
  return { dims: next, gates: g }
}

export function cultureNote(hits: CultureHits): string {
  if (!hits.pos.length && !hits.neg.length) return "Culture phrases found: none in the posting (score culture from what the JD shows; absence is not a positive)."
  return `Culture phrases found (quoted from the JD; anchor the culture score to these):\n${[...hits.pos.map((h) => `+ ${h}`), ...hits.neg.map((h) => `- ${h}`)].join("\n")}`
}

// jdHits is TEXT JSON written by several producers: an object of quad -> hits
// (target-role pipeline) or an array of claim ids (scout dossiers). Merge the
// culture keys in without dropping either shape.
export function mergeJdHits(existing: string | null | undefined, hits: CultureHits): string {
  let base: Record<string, unknown> = {}
  try {
    const v = existing ? JSON.parse(existing) : null
    if (Array.isArray(v)) base = { scout_claims: v }
    else if (v && typeof v === "object") base = v as Record<string, unknown>
  } catch { /* unparseable: start clean, the old value was not usable */ }
  return JSON.stringify({ ...base, culture_pos: hits.pos, culture_neg: hits.neg })
}
