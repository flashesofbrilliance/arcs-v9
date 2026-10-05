// DB receipt -> presentational CompassResult, shared by the owner brief page and
// the token-shared view (/shared/brief).

import type { CompassResult } from "@/lib/mockCompass"

export function safeParse<T>(v: unknown, fallback: T): T {
  if (typeof v !== "string") return (v as T) ?? fallback
  try { return JSON.parse(v) as T } catch { return fallback }
}

// DB receipt (camelCase, JSON-string fields) → presentational CompassResult
export function toCompassResult(receipt: Record<string, unknown>, tributaries: unknown[]): CompassResult {
  const raw = safeParse<Record<string, unknown>>(receipt.rawResponse, {})
  const rawReasoning = (raw.reasoning ?? {}) as Record<string, unknown>
  return {
    receipt_id: String(receipt.id ?? ""),
    question: String(receipt.decision ?? ""),
    true_north: String(receipt.trueNorth ?? ""),
    why: safeParse<string[]>(receipt.whyBullets, []),
    nci_score: Number(receipt.nciScore ?? 50),
    coherence_pct: (receipt.coherencePct as number) ?? undefined,
    is_satoshi: Boolean(receipt.isSatoshi),
    decision_mode: String(receipt.mode ?? ""),
    door_class: String(receipt.doorClass ?? "TWO_WAY"),
    y_state: String(receipt.yState ?? "GREEN"),
    render_resolution: String(receipt.renderResolution ?? "SHARP"),
    nci_delta: null,
    macro_tags: safeParse<string[]>(receipt.macroTags, []),
    tributaries: tributaries as CompassResult["tributaries"],
    reasoning: {
      fated: safeParse(receipt.fated, undefined),
      paths: safeParse(receipt.paths, undefined),
      court: safeParse(receipt.court, undefined),
      court_verdict: (receipt.courtVerdict as string) ?? undefined,
      advisors: (rawReasoning.advisors as CompassResult["reasoning"]["advisors"]) ?? undefined,
    },
  } as CompassResult
}
