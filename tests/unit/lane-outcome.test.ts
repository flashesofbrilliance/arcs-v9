// Job Factory slice 3: closing a Lane row. A loss needs a reason from the one
// board taxonomy; an offer may carry one; anything off-list is refused.
import { test } from "node:test"
import assert from "node:assert/strict"
import { parseOutcome, outcomeNote, reasonOf, FATES } from "../../src/lib/lane-outcome.ts"

test("a loss without a reason is refused", () => {
  for (const fate of ["reject", "ghosted", "withdrawn"]) assert.ok("error" in parseOutcome({ fate }), fate)
})

test("an offer needs no reason", () => {
  assert.deepEqual(parseOutcome({ fate: "offer" }), { fate: "offer", reason: null, note: null })
})

test("off-list fate or reason is refused", () => {
  assert.ok("error" in parseOutcome({ fate: "hired" }))
  assert.ok("error" in parseOutcome({ fate: "reject", reason: "vibes" }))
  assert.ok("error" in parseOutcome(null))
})

test("fates map onto the schema's closed:* values", () => {
  assert.equal(FATES.offer, "closed:won")
  assert.equal(FATES.reject, "closed:lost")
  assert.equal(FATES.withdrawn, "closed:learned")
})

test("note round-trips so Debrief can count by reason", () => {
  const o = parseOutcome({ fate: "reject", reason: "comp", note: "  band capped at 180  " })
  assert.ok(!("error" in o))
  const n = outcomeNote(o as Exclude<typeof o, { error: string }>)
  assert.equal(n, "comp · band capped at 180")
  assert.equal(reasonOf(n), "comp")
  assert.equal(reasonOf("free text from before slice 3"), null)
  assert.equal(reasonOf(null), null)
})
