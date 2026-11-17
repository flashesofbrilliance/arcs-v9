// Salary screen (Zach, 2026-11-16): the floor is $180K, judged against the TOP of a posted range.
// A role passes when its max reaches the floor; a range that tops out below it gates the role.
// Fixtures are real strings from the jobs board on 2026-11-16.
import { test } from "node:test"
import assert from "node:assert/strict"
import { parseUsdRange, compScreen } from "../../src/lib/comp-screen.ts"

test("parses the range shapes the board carries", () => {
  assert.deepEqual(parseUsdRange("$145K – $195K • Offers Equity • Offers Bonus"), { min: 145000, max: 195000 })
  assert.deepEqual(parseUsdRange("$166,000 - $214,000"), { min: 166000, max: 214000 })
  assert.deepEqual(parseUsdRange("$204,400-$352,000"), { min: 204400, max: 352000 })
  assert.deepEqual(parseUsdRange("paying up to $204K/year"), { min: null, max: 204000 })
  assert.deepEqual(parseUsdRange("starting at $175K/year"), { min: 175000, max: null })
  assert.deepEqual(parseUsdRange("$160K-$180K"), { min: 160000, max: 180000 })
  assert.deepEqual(parseUsdRange("est $145K-$175K (Jack & Jill)"), { min: 145000, max: 175000 })
})

test("non-USD and unstated pay are never parsed as USD", () => {
  assert.equal(parseUsdRange("CAD $155,000–$230,000"), null)
  assert.equal(parseUsdRange("est. £85,000–£110,000"), null)
  assert.equal(parseUsdRange("Competitive SaaS package"), null)
  assert.equal(parseUsdRange(null), null)
})

test("screen uses the upper bound: max at or above the floor passes", () => {
  assert.equal(compScreen("$160K-$180K", 180000).below, false) // Sayari: max equals the floor
  assert.equal(compScreen("$145K – $195K", 180000).below, false) // ClarityPay
  assert.equal(compScreen("est $145K-$175K", 180000).below, true) // Runlayer: tops out under
  assert.equal(compScreen("$120,000–$150,000", 180000).below, true) // Rebuild
})

test("no stated max is never gated", () => {
  assert.equal(compScreen("starting at $175K/year", 180000).below, false)
  assert.equal(compScreen("CAD $155,000–$230,000", 180000).below, false)
  assert.equal(compScreen(null, 180000).below, false)
})
