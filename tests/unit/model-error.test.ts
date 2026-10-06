// modelError: a failed model call becomes a 503 carrying the API's own reason and a code.
// The usage-limit case is the 2026-10-05 production incident, verbatim.
import { test } from "node:test"
import assert from "node:assert/strict"
import { modelError } from "../../src/lib/claude-models.ts"

const usageLimit = { status: 400, error: { type: "error", error: { type: "invalid_request_error", message: "You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC." } } }

test("usage limit -> 503, code usage_limit, message kept, not retryable", async () => {
  const r = modelError(usageLimit); const j = await r.json()
  assert.equal(r.status, 503); assert.equal(j.code, "usage_limit"); assert.equal(j.retryable, false)
  assert.match(j.error, /regain access on 2026-11-01/)
})

test("429 is rate_limited and retryable; 529 is overloaded", async () => {
  assert.deepEqual(((await modelError({ status: 429, message: "slow down" }).json()) as { code: string; retryable: boolean }).code, "rate_limited")
  assert.equal(((await modelError({ status: 429, message: "x" }).json()) as { retryable: boolean }).retryable, true)
  assert.equal(((await modelError({ status: 529, message: "Overloaded" }).json()) as { code: string }).code, "overloaded")
})

test("a non-API throw still yields a readable 503", async () => {
  const j = (await modelError(new Error("socket hang up")).json()) as { code: string; error: string }
  assert.equal(j.code, "model_error"); assert.match(j.error, /socket hang up/)
})
