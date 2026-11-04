// ARCS Pro billing (2026-11-04). Runs the REAL /api/stripe/webhook handler with
// signed events against a fake db that records writes, plus the briefLocked rule.
// Money paths: a subscriber must never hit the paywall, a non-payer must, and a
// cancel or lapse must drop the tier. A forged event must write nothing.
import { test, beforeEach, afterEach } from "node:test"
import assert from "node:assert/strict"
import { createHmac } from "node:crypto"
import { setImpl } from "./stubs/db.ts"
import { briefLocked, proUrlFor } from "../../src/lib/paywall.ts"

const SECRET = "whsec_test"
type Write = { model: string; where: unknown; data: Record<string, unknown> }
let writes: Write[] = []

const rec = (model: string) => ({
  updateMany: async (a: { where: unknown; data: Record<string, unknown> }) => { writes.push({ model, ...a }); return { count: 1 } },
})

function signed(event: unknown, secret = SECRET): Request {
  const body = JSON.stringify(event)
  const t = Math.floor(Date.now() / 1000)
  const sig = createHmac("sha256", secret).update(`${t}.${body}`).digest("hex")
  return new Request("http://x/api/stripe/webhook", { method: "POST", body, headers: { "stripe-signature": `t=${t},v1=${sig}` } })
}

async function post(event: unknown, secret?: string) {
  const { POST } = await import("../../src/app/api/stripe/webhook/route.ts")
  return POST(signed(event, secret) as never)
}

beforeEach(() => {
  writes = []
  process.env.STRIPE_WEBHOOK_SECRET = SECRET
  setImpl({ user: rec("user"), receipt: rec("receipt") })
})
afterEach(() => {
  setImpl(null)
  delete process.env.STRIPE_PAYMENT_LINK
  delete process.env.STRIPE_PRO_LINK
})

test("subscription checkout sets the user PRO, stores the customer, turns check-ins on", async () => {
  const res = await post({ type: "checkout.session.completed", data: { object: { mode: "subscription", client_reference_id: "u1", payment_status: "paid", customer: "cus_1" } } })
  assert.equal(res.status, 200)
  assert.deepEqual(writes, [{ model: "user", where: { id: "u1" }, data: { tier: "PRO", debriefOptIn: true, stripeCustomerId: "cus_1" } }])
})

test("one-time brief checkout still marks only the receipt paid", async () => {
  await post({ type: "checkout.session.completed", data: { object: { mode: "payment", client_reference_id: "r1", payment_status: "paid" } } })
  assert.equal(writes.length, 1)
  assert.equal(writes[0].model, "receipt")
  assert.deepEqual(writes[0].where, { id: "r1", paidAt: null })
})

test("cancelled subscription drops the user to FREE", async () => {
  await post({ type: "customer.subscription.deleted", data: { object: { customer: "cus_1", status: "canceled" } } })
  assert.deepEqual(writes, [{ model: "user", where: { stripeCustomerId: "cus_1" }, data: { tier: "FREE" } }])
})

test("unpaid subscription drops to FREE; active keeps PRO", async () => {
  await post({ type: "customer.subscription.updated", data: { object: { customer: "cus_1", status: "unpaid" } } })
  await post({ type: "customer.subscription.updated", data: { object: { customer: "cus_1", status: "active" } } })
  assert.deepEqual(writes.map((w) => w.data.tier), ["FREE", "PRO"])
})

test("past_due is a grace window: no tier change", async () => {
  await post({ type: "customer.subscription.updated", data: { object: { customer: "cus_1", status: "past_due" } } })
  assert.equal(writes.length, 0)
})

test("unpaid checkout writes nothing", async () => {
  await post({ type: "checkout.session.completed", data: { object: { mode: "subscription", client_reference_id: "u1", payment_status: "unpaid", customer: "cus_1" } } })
  assert.equal(writes.length, 0)
})

test("forged signature is refused and writes nothing", async () => {
  const res = await post({ type: "checkout.session.completed", data: { object: { mode: "subscription", client_reference_id: "u1", payment_status: "paid" } } }, "whsec_wrong")
  assert.equal(res.status, 400)
  assert.equal(writes.length, 0)
})

test("briefLocked: free with no links, locked for unpaid FREE, open for PRO or a paid receipt", () => {
  assert.equal(briefLocked({ paidAt: null }, "FREE"), false)
  process.env.STRIPE_PRO_LINK = "https://buy.stripe.com/test_pro"
  assert.equal(briefLocked({ paidAt: null }, "FREE"), true)
  assert.equal(briefLocked({ paidAt: null }, null), true)
  assert.equal(briefLocked({ paidAt: null }, "PRO"), false)
  assert.equal(briefLocked({ paidAt: new Date() }, "FREE"), false)
})

test("proUrlFor carries the user id to checkout", () => {
  assert.equal(proUrlFor("u1"), null)
  process.env.STRIPE_PRO_LINK = "https://buy.stripe.com/test_pro"
  assert.equal(proUrlFor("u1"), "https://buy.stripe.com/test_pro?client_reference_id=u1")
})
