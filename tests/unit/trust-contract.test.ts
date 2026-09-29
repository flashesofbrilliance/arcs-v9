// Ledger TC-004 — regression test for trust contract §1 (ADR-049):
// "anonymous sessions: nothing is stored / no auth = no write path".
// Runs the REAL /api/prep and /api/compass handlers with no session and asserts
// zero Prisma writes and zero emails. The signed-in case is the control: it must
// write, which proves the stub would catch a write if one happened.
import { test, beforeEach } from "node:test"
import assert from "node:assert/strict"
import { calls, isWrite } from "./stubs/db.ts"
import { setSession } from "./stubs/auth.ts"
import { sent } from "./stubs/resend.ts"

process.env.ANTHROPIC_API_KEY ??= "test-key"
const writes = () => calls.filter(c => isWrite(c.op))
const post = (url: string, body: unknown) =>
  new Request(url, { method: "POST", headers: { "content-type": "application/json", "x-forwarded-for": `10.0.0.${Math.floor(Math.random() * 250)}` }, body: JSON.stringify(body) })

beforeEach(() => { calls.length = 0; sent.length = 0; setSession(null) })

test("anonymous /api/prep writes nothing", async () => {
  const { POST } = await import("../../src/app/api/prep/route.ts")
  const res = await POST(post("http://t/api/prep", { stakes: "HIGH", horizon: "TODAY", confidence: 3 }) as any)
  const json = await res.json()
  assert.equal(json.persisted, false)
  assert.equal(json.prep_id, null)
  assert.deepEqual(writes(), [])
})

test("anonymous /api/compass writes nothing and sends no email", async () => {
  const { POST } = await import("../../src/app/api/compass/route.ts")
  const res = await POST(post("http://t/api/compass", { question: "Should I take the job?", prep: { stakes: "HIGH" } }) as any)
  assert.equal(res.status, 200, await res.clone().text())
  const json = await res.json()
  assert.equal(json.receipt_id ?? null, null)
  assert.deepEqual(writes(), [])
  assert.equal(sent.length, 0)
  assert.equal(res.headers.get("set-cookie"), null)
})

test("control: signed-in /api/prep DOES write (stub detects writes)", async () => {
  setSession({ user: { id: "u1", email: "u1@example.com" } })
  const { POST } = await import("../../src/app/api/prep/route.ts")
  await POST(post("http://t/api/prep", { stakes: "LOW" }) as any)
  assert.ok(writes().some(w => w.model === "prepSession" && w.op === "create"))
})
