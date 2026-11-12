// The guide route turns the model's text into a PrepGuide row. A reply that is not JSON, or JSON
// missing a field the row needs, must come back as a named failure (the route answers 502, retry),
// never as an uncaught throw that surfaces as a bare 500.
import { test } from "node:test"
import assert from "node:assert/strict"
import { parseGuideReply } from "../../src/lib/guide-response.ts"

const good = {
  guide_title: "Prep for the Acme call",
  bet_label: "Bet: they want a pilot",
  total_prep_hours: "2 h",
  outcome_target: { outcome_statement: "a", leading_indicator: "b", kpi_label: "c", failure_signal: "d" },
  stages: [{ id: "s1" }],
}

test("a well-formed reply parses, with or without a code fence", () => {
  for (const raw of [JSON.stringify(good), "```json\n" + JSON.stringify(good) + "\n```"]) {
    const r = parseGuideReply(raw)
    assert.equal(r.ok, true)
    if (r.ok) {
      assert.equal(r.guide.guide_title, good.guide_title)
      assert.deepEqual(r.guide.stages, good.stages)
      assert.equal(r.guide.outcome_target?.kpi_label, "c")
    }
  }
})

test("outcome_target is optional", () => {
  const { outcome_target: _, ...rest } = good
  const r = parseGuideReply(JSON.stringify(rest))
  assert.equal(r.ok, true)
  if (r.ok) assert.equal(r.guide.outcome_target, undefined)
})

test("text that is not JSON is a failure, not a throw", () => {
  for (const raw of ["", "Sure! Here is your guide:", '{"guide_title": "cut off', "[1,2]", "null"]) {
    const r = parseGuideReply(raw)
    assert.equal(r.ok, false, raw)
  }
})

test("JSON missing a field the row needs is a failure", () => {
  const cases: Record<string, unknown>[] = [
    { ...good, guide_title: undefined },
    { ...good, bet_label: 3 },
    { ...good, total_prep_hours: null },
    { ...good, stages: [] },
    { ...good, stages: "s1" },
    { ...good, outcome_target: "none" },
    { ...good, outcome_target: { ...good.outcome_target, kpi_label: 7 } },
  ]
  for (const c of cases) assert.equal(parseGuideReply(JSON.stringify(c)).ok, false, JSON.stringify(c))
})
