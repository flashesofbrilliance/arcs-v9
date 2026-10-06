// Model-call failures: a stable code + calm copy reach the client; the provider's own
// body and request_id never do. The usage-limit fixture is the 2026-10-05 production
// incident, verbatim. Fail-on-bad: every fixture's client payload is scanned for the
// upstream text, error type and request id.
import { test, beforeEach } from "node:test"
import assert from "node:assert/strict"
import { classifyModelError, modelErrorResponse, reportModelError, _resetAlertThrottle } from "../../src/lib/model-error.ts"
import { modelError } from "../../src/lib/claude-models.ts"
import { sent } from "./stubs/resend.ts"
import { failNext } from "./stubs/anthropic.ts"

const RAW = "You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC."
const RID = "req_011CTestLeak"
const usageLimit = { status: 400, requestID: RID, error: { type: "error", request_id: RID, error: { type: "invalid_request_error", message: RAW } } }

const FIXTURES: [string, unknown, string][] = [
  ["usage limit 400", usageLimit, "usage_limit"],
  ["429", { status: 429, requestID: RID, error: { error: { type: "rate_limit_error", message: "Number of request tokens has exceeded your per-minute rate limit secret-org-123" } } }, "rate_limited"],
  ["529", { status: 529, requestID: RID, error: { error: { type: "overloaded_error", message: "Overloaded secret-org-123" } } }, "overloaded"],
  ["401", { status: 401, requestID: RID, error: { error: { type: "authentication_error", message: "invalid x-api-key secret-org-123" } } }, "auth"],
  ["network", Object.assign(new Error("Connection error. fetch failed secret-org-123"), { name: "APIConnectionError" }), "network"],
  ["500", { status: 500, requestID: RID, error: { error: { type: "api_error", message: "Internal server error secret-org-123" } } }, "upstream_error"],
  ["unknown throw", new Error("socket weirdness secret-org-123"), "model_error"],
]
const LEAKS = [RAW, RID, "usage limits", "invalid_request_error", "secret-org-123", "x-api-key", "regain access"]

function assertClean(body: string) {
  for (const l of LEAKS) assert.ok(!body.includes(l), `client payload leaked ${JSON.stringify(l)}: ${body}`)
  assert.match(body, /Your fork is held\. Nothing was lost\./)
}

let errs: string[] = []
const realErr = console.error
beforeEach(() => { _resetAlertThrottle(); sent.length = 0; errs = []; console.error = (...a: unknown[]) => { errs.push(a.join(" ")) } })

for (const [name, e, code] of FIXTURES) {
  test(`${name} -> code ${code}, no provider text in the payload`, async () => {
    assert.equal(classifyModelError(e).code, code)
    const r = modelErrorResponse("t", e)
    assert.equal(r.status, code === "rate_limited" ? 429 : 503)
    const body = await r.text()
    assertClean(body)
    assert.equal(JSON.parse(body).code, code)
    console.error = realErr
  })
}

test("the jobs-route modelError export is the same safe mapper", async () => {
  const body = await modelError(usageLimit).text()
  assertClean(body); assert.equal(JSON.parse(body).code, "usage_limit"); assert.equal(JSON.parse(body).retryable, false)
  console.error = realErr
})

test("server log carries the full upstream + request_id under [MODEL_OUTAGE]", () => {
  reportModelError("compass", usageLimit)
  console.error = realErr
  const line = errs.find((l) => l.includes("[MODEL_OUTAGE]")) ?? ""
  assert.match(line, /route=compass code=usage_limit status=400/)
  assert.ok(line.includes(RID) && line.includes("regain access on 2026-11-01"), line)
})

test("usage limit alerts admins once per window (prod only); rate limits never alert", () => {
  const env = { ...process.env }
  Object.assign(process.env, { NODE_ENV: "production", ADMIN_EMAILS: "a@example.com", AUTH_RESEND_KEY: "k" })
  try {
    reportModelError("compass", usageLimit); reportModelError("brief", usageLimit)
    reportModelError("compass", { status: 429 })
    assert.equal(sent.length, 1)
    assert.match((sent[0] as { subject: string }).subject, /\[MODEL_OUTAGE\] usage_limit on compass/)
  } finally { process.env = env; console.error = realErr }
})

test("compass route: an upstream usage limit reaches the client as calm copy only", async () => {
  const { POST } = await import("../../src/app/api/compass/route.ts")
  process.env.ANTHROPIC_API_KEY ??= "test-key"
  failNext(usageLimit)
  const req = new Request("http://t/api/compass", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ question: "Should I take the job?" }) })
  const res = await POST(req as any)
  console.error = realErr
  assert.equal(res.status, 503)
  const body = await res.text()
  assertClean(body)
  assert.equal(JSON.parse(body).code, "usage_limit")
})
