// Parse the guide model's reply into the fields a PrepGuide row needs. Pure, no I/O, so it is unit-tested
// (tests/unit/guide-response.test.ts). A reply that is not JSON, or lacks a field the row needs, is a named
// failure the route answers with 502 (retry), never an uncaught throw that surfaces as a bare 500.

export type GuideReply = {
  guide_title: string
  bet_label: string
  total_prep_hours: string
  outcome_target?: { outcome_statement: string; leading_indicator: string; kpi_label: string; failure_signal: string }
  stages: unknown[]
}

export type GuideParse = { ok: true; guide: GuideReply } | { ok: false; reason: string }

const OT_KEYS = ["outcome_statement", "leading_indicator", "kpi_label", "failure_signal"] as const

export function parseGuideReply(raw: string): GuideParse {
  const cleaned = raw.replace(/^```(?:json)?\n?/, "").replace(/\n?```$/, "").trim()
  let v: unknown
  try {
    v = JSON.parse(cleaned)
  } catch {
    return { ok: false, reason: "not JSON" }
  }
  if (!v || typeof v !== "object" || Array.isArray(v)) return { ok: false, reason: "not a JSON object" }
  const o = v as Record<string, unknown>
  for (const k of ["guide_title", "bet_label", "total_prep_hours"] as const) {
    if (typeof o[k] !== "string") return { ok: false, reason: `${k} missing or not text` }
  }
  if (!Array.isArray(o.stages) || o.stages.length === 0) return { ok: false, reason: "stages missing or empty" }
  const ot = o.outcome_target
  if (ot !== undefined) {
    if (!ot || typeof ot !== "object" || Array.isArray(ot)) return { ok: false, reason: "outcome_target not an object" }
    const t = ot as Record<string, unknown>
    for (const k of OT_KEYS) if (typeof t[k] !== "string") return { ok: false, reason: `outcome_target.${k} not text` }
  }
  return { ok: true, guide: o as unknown as GuideReply }
}
