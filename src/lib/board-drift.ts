// Job Factory slice 2 (2026-10-05): the Missed state and the backlog drift signal.
// Pure functions over board rows + JobBoardSetting values, shared by the board,
// GET /api/jobs/drift (read by the 8:15 morning task) and the unit tests.
//
// Missed: a scored row unswiped for MISSED_DAYS after it was scored. Not a swipe,
// never a preference: the system only stops pretending the row is fresh.
// Clearing the pile (Zach's one tap) marks rows scored before that moment as
// "not reviewed"; revive puts one row back. Neither writes a JobSwipe.
//
// Drift keys on the BACKLOG, not on sessions, so it still fires when Zach stops
// opening the board (the gauntlet's rank-6 fix): live rows above BACKLOG_MAX, or
// no swipe for NO_SWIPE_WEEKDAYS weekdays while new rows kept arriving. A dismiss
// stays quiet until the signal's signature changes (a new threshold crossing).

export const MISSED_DAYS = 7
export const BACKLOG_MAX = 40
export const NO_SWIPE_WEEKDAYS = 3
const DAY = 864e5

export type DriftRow = { jobid: string; band: string; composite: number | null; scoredAt?: string | null; firstSeen: string; swipe?: { at: string } | null }
export type BoardSettings = Record<string, string | undefined>
export type RowState = "live" | "missed" | "not_reviewed" | "swiped" | "unscored"

function revived(settings: BoardSettings): Set<string> {
  try { return new Set(JSON.parse(settings.missed_revived ?? "[]")) } catch { return new Set() }
}

export function rowState(r: DriftRow, settings: BoardSettings, now: Date): RowState {
  if (r.swipe) return "swiped"
  if (r.band === "UNSCORED" || r.composite == null) return "unscored"
  if (revived(settings).has(r.jobid)) return "live"
  const scored = Date.parse(r.scoredAt ?? r.firstSeen)
  const cleared = settings.missed_cleared_at ? Date.parse(settings.missed_cleared_at) : null
  if (cleared != null && scored <= cleared) return "not_reviewed"
  return now.getTime() - scored >= MISSED_DAYS * DAY ? "missed" : "live"
}

// Weekdays strictly after `from` up to and including `to` (Mon-Fri only).
export function weekdaysBetween(from: Date, to: Date): number {
  let n = 0
  const d = new Date(Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate()))
  const end = Date.UTC(to.getUTCFullYear(), to.getUTCMonth(), to.getUTCDate())
  while ((d.setUTCDate(d.getUTCDate() + 1), d.getTime()) <= end) { const w = d.getUTCDay(); if (w !== 0 && w !== 6) n++ }
  return n
}

export type Drift = { fire: boolean; dismissed: boolean; signature: string | null; line: string | null; live: number; missed: number; notReviewed: number; weekdaysSinceSwipe: number | null; newSinceSwipe: number }

export function drift(rows: DriftRow[], settings: BoardSettings, now: Date, cutoff: number): Drift {
  const onBoard = rows.filter((r) => r.composite != null && r.composite >= cutoff)
  const states = onBoard.map((r) => rowState(r, settings, now))
  const live = states.filter((s) => s === "live").length
  const missed = states.filter((s) => s === "missed").length
  const notReviewed = states.filter((s) => s === "not_reviewed").length
  const swipeTimes = rows.map((r) => r.swipe?.at).filter(Boolean).map((t) => Date.parse(t!))
  const lastSwipe = swipeTimes.length ? new Date(Math.max(...swipeTimes)) : null
  const weekdaysSinceSwipe = lastSwipe ? weekdaysBetween(lastSwipe, now) : null
  const newSinceSwipe = rows.filter((r) => !lastSwipe || Date.parse(r.firstSeen) > lastSwipe.getTime()).length

  const reasons: string[] = []
  if (live + missed > BACKLOG_MAX) reasons.push(`backlog>${BACKLOG_MAX}`)
  if (weekdaysSinceSwipe != null && weekdaysSinceSwipe >= NO_SWIPE_WEEKDAYS && newSinceSwipe > 0) reasons.push(`noswipe>=${NO_SWIPE_WEEKDAYS}`)
  const signature = reasons.length ? reasons.join("|") : null
  const dismissed = signature != null && settings.drift_dismissed === signature
  const parts: string[] = []
  if (reasons.some((x) => x.startsWith("backlog"))) parts.push(`${live + missed} rows waiting on a swipe`)
  if (reasons.some((x) => x.startsWith("noswipe"))) parts.push(`no swipe in ${weekdaysSinceSwipe} weekdays while ${newSinceSwipe} new rows arrived`)
  const line = signature ? `Rows are piling up faster than you swipe: ${parts.join("; ")}. Narrow the alerts, raise the cutoff, or shrink the daily queue?` : null
  return { fire: signature != null && !dismissed, dismissed, signature, line, live, missed, notReviewed, weekdaysSinceSwipe, newSinceSwipe }
}
