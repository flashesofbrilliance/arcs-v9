// Job Factory slice 6: named trust. Company match only; titles never; a pointer, not a name.
import { test } from "node:test"
import assert from "node:assert/strict"
import { normalizeCompany, buildTrustIndex, trustFor } from "../../src/lib/trust.ts"

const idx = buildTrustIndex([
  { id: "champ-1", company: "Stripe, Inc." },
  { id: "champ-2", company: "stripe" },
  { id: "champ-3", company: "" },
  { id: "champ-4", company: "Anthropic PBC" },
])

test("company suffixes and punctuation normalize away", () => {
  assert.equal(normalizeCompany("Stripe, Inc."), "stripe")
  assert.equal(normalizeCompany("Acme Labs LLC"), "acme")
  assert.equal(normalizeCompany("Johnson & Johnson"), "johnson and johnson")
})

test("a matching company returns ids and a count, never a name", () => {
  const t = trustFor("STRIPE", idx)
  assert.deepEqual(t, { count: 2, ids: ["champ-1", "champ-2"] })
  assert.ok(!JSON.stringify(t).match(/[A-Z][a-z]+ [A-Z][a-z]+/))
})

test("no match, or a champion with no company, gives no trust", () => {
  assert.equal(trustFor("Plaid", idx), null)
  assert.equal(trustFor("", idx), null)
})

test("a title is not a company: 'VP Product' never matches anything", () => {
  assert.equal(trustFor("VP Product", idx), null)
})
