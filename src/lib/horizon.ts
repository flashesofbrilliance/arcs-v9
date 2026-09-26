// Horizon → review/reminder timing.
//
// Both Receipt create paths (src/app/api/compass/route.ts and
// src/app/api/receipts/save/route.ts) previously wrote a blind T+7
// `reminderDate` and left the canonical `horizon` and `reviewDate` columns
// null — 0/249 rows in prod carried either, as of 2026-09-24, despite
// `@@index([horizon])` sitting on the (always-null) column. That made the
// outcome-capture / debrief timing engine blind: a THIS_QUARTER or
// ONE_TO_THREE_YEARS decision was nudged to "did this land?" 7 days out, long
// before it could plausibly have resolved.
//
// This module is the single source of truth for (1) normalizing the legacy
// `window` enum to the canonical `horizon` enum, and (2) deriving a
// horizon-appropriate review date. Both create paths import it so they cannot
// drift. See _QUEUE/induced-backlog.jsonl :: outcome-loop-timing-wiring-*.

export type WindowEnum = "TODAY" | "THIS_WEEK" | "THIS_QUARTER" | "ONE_TO_THREE_YEARS"

// Legacy `window` enum → canonical schema `horizon` enum. Per
// prisma/schema.prisma: window is the legacy field (TODAY|THIS_WEEK|…),
// horizon is the canonical, indexed field (TODAY|WEEK|QUARTER|YEARS).
const WINDOW_TO_HORIZON: Record<string, string> = {
  TODAY: "TODAY",
  THIS_WEEK: "WEEK",
  THIS_QUARTER: "QUARTER",
  ONE_TO_THREE_YEARS: "YEARS",
}

export function normalizeHorizon(window: string | null | undefined): string | null {
  if (!window) return null
  return WINDOW_TO_HORIZON[window] ?? null
}

// Days from the decision to the "did this land?" check, by window. The debrief
// / outcome-capture nudge fires on this offset, so it must scale with the
// decision's actual resolution window — not a flat week.
const HORIZON_REVIEW_DAYS: Record<string, number> = {
  TODAY: 2,
  THIS_WEEK: 7,
  THIS_QUARTER: 90,
  ONE_TO_THREE_YEARS: 365,
}

// Fallback when the window is unknown/unrecognized. Matches the historical
// default so an unmapped value degrades to the old behavior rather than
// something surprising.
export const DEFAULT_REVIEW_DAYS = 7

export function reviewDaysForWindow(window: string | null | undefined): number {
  if (!window) return DEFAULT_REVIEW_DAYS
  return HORIZON_REVIEW_DAYS[window] ?? DEFAULT_REVIEW_DAYS
}

// The review date (a DateTime) for a decision, from its window and a base time.
// Persisted to Receipt.reviewDate.
export function reviewDateForWindow(window: string | null | undefined, from: Date = new Date()): Date {
  return new Date(from.getTime() + reviewDaysForWindow(window) * 86400000)
}

// The `reminderDate` string (YYYY-MM-DD) the debrief pipeline keys off (both
// the compass-time inline send and the long-horizon cron in
// src/app/api/cron/debrief/route.ts compare against it). Prefers a
// model-supplied ISO date when present (the prep.outcomeHorizon path), else
// derives from the window. Never a blind T+7 for a long-horizon decision.
export function reminderDateForWindow(
  window: string | null | undefined,
  modelReminderIso?: string | null,
  from: Date = new Date(),
): string {
  if (typeof modelReminderIso === "string" && modelReminderIso.trim()) {
    return modelReminderIso.slice(0, 10)
  }
  return reviewDateForWindow(window, from).toISOString().slice(0, 10)
}
