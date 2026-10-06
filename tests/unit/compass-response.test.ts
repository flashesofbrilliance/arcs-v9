// The dashboard's non-OK /api/compass handling: an HTTP answer is definitive, so the
// receipt-recovery poll (~20s) never runs and the card shows the server's own copy.
import { test } from "node:test"
import assert from "node:assert/strict"
import { compassFailure, FALLBACK } from "../../src/lib/compass-response.ts"
import { modelErrorBody, classifyModelError } from "../../src/lib/model-error.ts"
import { MODEL_ERROR_CODES } from "../../src/lib/model-error-codes.ts"

test("a 200 is not a failure", () => {
  assert.equal(compassFailure(true, { receipt_id: "r1" }), null)
})

test("every mapped model error skips the poll and shows the mapped copy", () => {
  const fixtures: Record<string, unknown> = {
    usage_limit: { status: 400, error: { error: { message: "You have reached your specified API usage limits." } } },
    rate_limited: { status: 429 }, overloaded: { status: 529 }, auth: { status: 401 },
    network: Object.assign(new Error("fetch failed"), { name: "APIConnectionError" }),
    upstream_error: { status: 500 }, model_error: new Error("odd"),
  }
  for (const code of MODEL_ERROR_CODES) {
    const info = classifyModelError(fixtures[code])
    assert.equal(info.code, code)
    const f = compassFailure(false, modelErrorBody(info))
    assert.ok(f, code)
    assert.equal(f.poll, false)
    assert.equal(f.code, code)
    assert.equal(f.message, info.message)
  }
})

test("other HTTP refusals (400/429 rate limit/409) also skip the poll and keep the server copy", () => {
  for (const body of [{ error: "invalid request body" }, { error: "Too many requests - the compass needs a moment. Try again shortly." }, { error: "x", code: "session_reassigned" }]) {
    const f = compassFailure(false, body)
    assert.ok(f); assert.equal(f.poll, false); assert.equal(f.message, body.error)
  }
})

test("an empty or odd body falls back to calm copy, never a blank card", () => {
  for (const body of [null, undefined, {}, { error: "" }, { error: 42 }, "html"]) {
    const f = compassFailure(false, body)
    assert.ok(f); assert.equal(f.message, FALLBACK); assert.equal(f.poll, false)
  }
})
