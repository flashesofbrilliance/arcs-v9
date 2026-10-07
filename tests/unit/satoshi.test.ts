// Satoshi base-rate guard (src/lib/satoshi.ts). Pins the bar the model is held
// to, the prompt line that states it, and that the bar is wired into the real
// /api/compass handler (not only described): the route runs end to end against
// the stubs with a canned reply that over-claims the flag.
import { test, beforeEach, afterEach } from "node:test"
import assert from "node:assert/strict"
import { satoshiGate, SATOSHI_RULE, SATOSHI_MIN_NCI, SATOSHI_STAKES, SATOSHI_BASE_RATE } from "../../src/lib/satoshi.ts"
import { CANNED } from "./stubs/anthropic.ts"
import { calls } from "./stubs/db.ts"
import { setSession } from "./stubs/auth.ts"

process.env.ANTHROPIC_API_KEY ??= "test-key"

test("the bar: claimed, HIGH stakes, nci at or above the minimum", () => {
  assert.equal(satoshiGate({ claimed: true, nciScore: SATOSHI_MIN_NCI, stakes: "HIGH" }), true)
  assert.equal(satoshiGate({ claimed: true, nciScore: 94, stakes: "HIGH" }), true)
})

test("the prod inflation shape is cleared: PLAN-grade MEDIUM stakes, nci 78", () => {
  assert.equal(satoshiGate({ claimed: true, nciScore: 78, stakes: "MEDIUM" }), false)
  assert.equal(satoshiGate({ claimed: true, nciScore: 94, stakes: "LOW" }), false)
})

test("nci below the minimum is cleared even at HIGH stakes", () => {
  assert.equal(satoshiGate({ claimed: true, nciScore: SATOSHI_MIN_NCI - 1, stakes: "HIGH" }), false)
})

test("the gate never promotes: an unclaimed flag stays false at any score", () => {
  assert.equal(satoshiGate({ claimed: false, nciScore: 99, stakes: "HIGH" }), false)
  assert.equal(satoshiGate({ claimed: undefined, nciScore: 99, stakes: "HIGH" }), false)
})

test("untrusted shapes clear the flag: string true, lowercase stakes, non-numeric score", () => {
  assert.equal(satoshiGate({ claimed: "true", nciScore: 90, stakes: "HIGH" }), false)
  assert.equal(satoshiGate({ claimed: true, nciScore: 90, stakes: "high" }), false)
  assert.equal(satoshiGate({ claimed: true, nciScore: "90", stakes: "HIGH" }), false)
  assert.equal(satoshiGate({ claimed: true, nciScore: NaN, stakes: "HIGH" }), false)
  assert.equal(satoshiGate({ claimed: true, nciScore: 90, stakes: null }), false)
})

test("the prompt line states the same bar the gate enforces, with a base-rate anchor", () => {
  assert.ok(SATOSHI_RULE.startsWith("is_satoshi:"))
  assert.ok(SATOSHI_RULE.includes(SATOSHI_BASE_RATE))
  assert.ok(/1 in 50/.test(SATOSHI_RULE))
  assert.ok(SATOSHI_RULE.includes(`STAKES ${SATOSHI_STAKES}`))
  assert.ok(SATOSHI_RULE.includes(`at least ${SATOSHI_MIN_NCI}`))
  assert.ok(!SATOSHI_RULE.includes("—"), "no em-dashes in the prompt line")
})

// Route-level: the real handler, offline. The anthropic stub answers with CANNED
// (nci 72) and the test makes it over-claim is_satoshi. Stakes come from the
// request body, which is what the route uses for mode and door.
const post = (body: unknown, ip: string) =>
  new Request("http://t/api/compass", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: JSON.stringify(body),
  })
const canned = { ...CANNED } as Record<string, unknown>

beforeEach(() => {
  calls.length = 0
  setSession(null)
  ;(CANNED as Record<string, unknown>).is_satoshi = true
})
afterEach(() => {
  for (const k of Object.keys(CANNED)) delete (CANNED as Record<string, unknown>)[k]
  Object.assign(CANNED, canned)
})

test("/api/compass clears an over-claimed flag at the default MEDIUM stakes", async () => {
  const { POST } = await import("../../src/app/api/compass/route.ts")
  const res = await POST(post({ question: "Should I rename the product?" }, "10.1.0.1") as never)
  assert.equal(res.status, 200, await res.clone().text())
  const json = await res.json()
  assert.equal(json.decision_mode, "PLAN")
  assert.equal(json.is_satoshi, false)
})

test("/api/compass keeps the flag at HIGH stakes with nci at the bar", async () => {
  ;(CANNED as Record<string, unknown>).nci_score = SATOSHI_MIN_NCI
  const { POST } = await import("../../src/app/api/compass/route.ts")
  const res = await POST(post({ question: "Should I sell the company?", stakes: "HIGH" }, "10.1.0.2") as never)
  assert.equal(res.status, 200, await res.clone().text())
  const json = await res.json()
  assert.equal(json.decision_mode, "COURT")
  assert.equal(json.is_satoshi, true)
})

test("/api/compass clears the flag at HIGH stakes when nci is under the bar", async () => {
  ;(CANNED as Record<string, unknown>).nci_score = SATOSHI_MIN_NCI - 1
  const { POST } = await import("../../src/app/api/compass/route.ts")
  const res = await POST(post({ question: "Should I sell the company?", stakes: "HIGH" }, "10.1.0.3") as never)
  assert.equal(res.status, 200, await res.clone().text())
  assert.equal((await res.json()).is_satoshi, false)
})
