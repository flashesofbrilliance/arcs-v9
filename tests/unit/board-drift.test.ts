// Job Factory slice 2: Missed state + backlog drift. The gauntlet's rank-6 case is
// the one that matters most: zero board sessions and a growing backlog must FIRE.
import { test } from "node:test"
import assert from "node:assert/strict"
import { rowState, drift, weekdaysBetween, type DriftRow } from "../../src/lib/board-drift.ts"

const NOW = new Date("2026-10-15T12:00:00Z") // a Thursday
const daysAgo = (n: number) => new Date(NOW.getTime() - n * 864e5).toISOString()
const row = (id: string, scoredDaysAgo: number, extra: Partial<DriftRow> = {}): DriftRow =>
  ({ jobid: id, band: "CONSIDER", composite: 0.6, scoredAt: daysAgo(scoredDaysAgo), firstSeen: daysAgo(scoredDaysAgo), swipe: null, ...extra })

test("a scored row turns Missed at 7 days unswiped, not before", () => {
  assert.equal(rowState(row("a", 6.9), {}, NOW), "live")
  assert.equal(rowState(row("a", 7), {}, NOW), "missed")
  assert.equal(rowState(row("a", 30, { swipe: { at: daysAgo(1) } }), {}, NOW), "swiped")
  assert.equal(rowState(row("a", 30, { band: "UNSCORED", composite: null }), {}, NOW), "unscored")
})

test("clearing the pile marks older rows not_reviewed; revive brings one back; no swipe written", () => {
  const s = { missed_cleared_at: daysAgo(2), missed_revived: '["b"]' }
  assert.equal(rowState(row("a", 10), s, NOW), "not_reviewed")
  assert.equal(rowState(row("b", 10), s, NOW), "live")
  assert.equal(rowState(row("c", 1), s, NOW), "live") // scored after the clear
})

test("zero sessions + growing backlog FIRES (keyed on backlog, not on sessions)", () => {
  const rows = Array.from({ length: 45 }, (_, i) => row(`r${i}`, i % 5))
  const d = drift(rows, {}, NOW, 0.52)
  assert.equal(d.fire, true)
  assert.match(d.line!, /45 rows waiting/)
})

test("no swipe in 3 weekdays while rows arrive FIRES; a quiet board does not", () => {
  const swiped = row("old", 20, { swipe: { at: daysAgo(6) } })
  const fresh = row("new", 1)
  assert.equal(drift([swiped, fresh], {}, NOW, 0.52).fire, true)
  const recent = row("old", 20, { swipe: { at: daysAgo(1) } })
  assert.equal(drift([recent, fresh], {}, NOW, 0.52).fire, false)
})

test("a dismiss stays quiet until the signature changes", () => {
  const rows = Array.from({ length: 45 }, (_, i) => row(`r${i}`, 1))
  const d = drift(rows, {}, NOW, 0.52)
  const quiet = drift(rows, { drift_dismissed: d.signature! }, NOW, 0.52)
  assert.equal(quiet.fire, false); assert.equal(quiet.dismissed, true)
  const both = drift([...rows, row("x", 20, { swipe: { at: daysAgo(6) } })], { drift_dismissed: d.signature! }, NOW, 0.52)
  assert.equal(both.fire, true) // new crossing, new signature
})

test("rows below the board cutoff never count toward the backlog", () => {
  const rows = Array.from({ length: 60 }, (_, i) => row(`r${i}`, 1, { composite: 0.3 }))
  assert.equal(drift(rows, {}, NOW, 0.52).fire, false)
})

test("weekdays skip the weekend", () => {
  assert.equal(weekdaysBetween(new Date("2026-10-09T12:00:00Z"), new Date("2026-10-12T12:00:00Z")), 1) // Fri -> Mon
})
