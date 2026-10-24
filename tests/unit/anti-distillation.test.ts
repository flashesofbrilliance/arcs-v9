// Compass anti-distillation controls (rulings 2026-10-20). Each control has a
// known-bad fixture that must FAIL its gate and a known-good that must PASS
// (AGENTS.md gotcha 15).
import { test, beforeEach } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import { OWNER_FIELDS, shapeForOwner } from "../../src/lib/compass-shape.ts"
import { noteAnonymousCall, utcDay } from "../../src/lib/anon-counter.ts"
import { calls } from "./stubs/db.ts"
import { setSession } from "./stubs/auth.ts"

process.env.ANTHROPIC_API_KEY ??= "test-key"

// ── Gate: owner response may carry only the allowlist ───────────────────────────
const leakedKeys = (body: Record<string, unknown>) =>
  Object.keys(body).filter((k) => !(OWNER_FIELDS as readonly string[]).includes(k))

const FULL = {
  ok: true, receipt_id: "r1", persisted: true, session_id: "s1", session_version: 1,
  true_north: "t", why: ["w"], tributaries: ["a", "b", "c"], nci_score: 72,
  reasoning: { court: [], advisors: [], geometry: {}, nci_breakdown: {} },
  nci_by_lens: {}, nci_self_grade: "B", y_conviction: 0.5, nci_delta: null,
}

test("owner gate: known-bad (today's full response) fails, shaped output passes", () => {
  assert.ok(leakedKeys(FULL).length > 0, "full response must trip the gate")
  assert.deepEqual(leakedKeys(shapeForOwner(FULL)), [])
  const shaped = shapeForOwner(FULL)
  for (const k of ["true_north", "why", "tributaries", "nci_score", "receipt_id", "session_id"]) assert.ok(k in shaped, k)
})

// ── Gate: the counter is log-only ───────────────────────────────────────────────
const isLogOnly = (r: Record<string, unknown>) =>
  Object.keys(r).every((k) => k === "day" || k === "instanceCount")

test("counter gate: a blocking counter fails, the real one passes at a huge count", () => {
  assert.equal(isLogOnly({ day: "x", instanceCount: 1, block: true }), false)
  let last: Record<string, unknown> = {}
  for (let i = 0; i < 500; i++) last = noteAnonymousCall(Date.UTC(2026, 9, 20))
  assert.equal(isLogOnly(last), true)
  assert.equal(last.instanceCount, 500)
  assert.equal(noteAnonymousCall(Date.UTC(2026, 9, 21)).instanceCount, 1, "rolls at UTC midnight")
  assert.equal(utcDay(Date.UTC(2026, 9, 20, 23, 59)), "2026-10-20")
})

// ── Route level: owner is trimmed, anonymous is untouched, nobody is blocked ────
const post = (ip: string) =>
  new Request("http://t/api/compass", {
    method: "POST",
    headers: { "content-type": "application/json", "x-forwarded-for": ip },
    body: JSON.stringify({ question: "Should I take the job?" }),
  })

beforeEach(() => { calls.length = 0; setSession(null) })

test("route: signed-in POST returns only product fields plus ids", async () => {
  setSession({ user: { id: "u1", email: "u1@example.com" } })
  const { POST } = await import("../../src/app/api/compass/route.ts")
  const res = await POST(post("10.9.0.1") as never)
  assert.equal(res.status, 200, await res.clone().text())
  const json = await res.json()
  assert.deepEqual(leakedKeys(json), [])
  assert.ok(json.true_north && json.why && Array.isArray(json.tributaries) && json.nci_score === 72)
})

test("route: anonymous POST is unchanged until _sealed ships (WRITE-LOCK 1 pending) and is never blocked by the counter", async () => {
  const { POST } = await import("../../src/app/api/compass/route.ts")
  for (let i = 0; i < 3; i++) {
    const res = await POST(post(`10.9.1.${i}`) as never)
    assert.equal(res.status, 200)
    if (i === 0) assert.ok("reasoning" in (await res.json()))
  }
})

// ── Observatory: the risk-register row is gone, file sizes stay ─────────────────
const NEEDLE = /computeYGate unaudited/
test("observatory gate: bad fixture trips, shipped client files pass, sizes kept", () => {
  assert.ok(NEEDLE.test('{id:"risk-6",risk:"computeYGate unaudited logic"}'))
  for (const f of ["src/app/observatory/page.tsx", "public/observatory/data.arcs-v9.json", "public/observatory/data.arcs-v9-gh.json"]) {
    assert.ok(!NEEDLE.test(fs.readFileSync(f, "utf8")), f)
  }
  assert.ok(fs.readFileSync("src/app/observatory/page.tsx", "utf8").includes("ygate.ts 248"))
})
