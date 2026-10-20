// Le Woof Desk (lewoof.arcs.care/desk). The rules Hila relies on: who is listed today,
// who is never contacted again, when a group passes, and that nothing is readable or
// writable without the passcode cookie.
import { test } from "node:test"
import assert from "node:assert/strict"
import { NextRequest } from "next/server"
import { AMMO_COOKIE, ammoToken } from "../../src/lib/ammo-gate.ts"
import { applyTouch, nextTouchDays, scorecard, todayList, touchSchema, type DeskAccount } from "../../src/lib/lewoof-desk.ts"
// @ts-expect-error plain .mjs script
import { parseCsv, toSql } from "../../scripts/lewoof_desk_seed.mjs"

const NOW = new Date("2026-10-21T15:00:00Z")
const acct = (o: Partial<DeskAccount>): DeskAccount => ({
  id: "x", section: "pet-boutique", rank: 1, name: "Shop", website: null, contactPage: null, flags: null, score: 50,
  contactName: null, contactTitle: null, email: null, phone: null, phoneNote: null, hook: null, notes: null,
  stage: "new", touches: 0, lastResult: null, nextTouch: null, ...o,
})

test("today: opted-out and lost accounts are never listed, even when a touch is due", () => {
  const list = todayList([
    acct({ id: "a", stage: "opted_out", email: "a@x.co", nextTouch: new Date("2026-10-01") }),
    acct({ id: "b", stage: "lost", email: "b@x.co", nextTouch: new Date("2026-10-01") }),
    acct({ id: "c", stage: "touched", email: "c@x.co", nextTouch: new Date("2026-10-20") }),
  ], NOW)
  assert.deepEqual(list.map((t) => t.id), ["c"])
})

test("today: due follow-ups come first, then at most five new accounts by score", () => {
  const fresh = Array.from({ length: 8 }, (_, i) => acct({ id: `n${i}`, rank: i, score: 10 + i, email: `n${i}@x.co` }))
  const due = acct({ id: "d", stage: "touched", phone: "555", nextTouch: new Date("2026-10-21") })
  const list = todayList([...fresh, due], NOW)
  assert.equal(list[0].id, "d")
  assert.equal(list.length, 6)
  assert.deepEqual(list.slice(1).map((t) => t.id), ["n7", "n6", "n5", "n4", "n3"])
})

test("today: a new account with no email, phone or contact page is not listed (nothing guessed)", () => {
  assert.deepEqual(todayList([acct({ id: "z" })], NOW), [])
  assert.equal(todayList([acct({ id: "p", contactPage: "https://x.co/contact" })], NOW)[0].channel, "contact_page")
})

test("today: a follow-up not yet due is not listed", () => {
  assert.deepEqual(todayList([acct({ id: "f", stage: "touched", email: "f@x.co", nextTouch: new Date("2026-10-30") })], NOW), [])
})

test("touch: opt-out clears the next touch and stage; order sets a reorder date about six weeks out", () => {
  const stop = applyTouch({ stage: "touched", touches: 1 }, "opted_out", NOW)
  assert.equal(stop.stage, "opted_out")
  assert.equal(stop.nextTouch, null)
  const order = applyTouch({ stage: "replied", touches: 2 }, "order", NOW)
  assert.equal(order.stage, "ordered")
  assert.equal(order.nextTouch!.toISOString().slice(0, 10), "2026-12-02")
})

test("touch: past seven touches the cadence slows to monthly and is never a break-up", () => {
  assert.equal(nextTouchDays("no_reply", 7), 35)
  assert.equal(nextTouchDays("no_reply", 3), 3)
  assert.equal(nextTouchDays("strong", 2), 2)
  assert.notEqual(nextTouchDays("weak", 8), null)
})

test("scorecard: not judged before 20 contacts; 3 strong of 25 passes; 1 of 25 is a tie; none fails", () => {
  const mk = (n: number, strong: number, section = "pet-boutique") => {
    const accounts = Array.from({ length: n }, (_, i) => acct({ id: `${section}${i}`, section, touches: 1 }))
    const results = accounts.slice(0, strong).map((a) => ({ accountId: a.id, result: "strong" }))
    return scorecard(accounts, results)[0]
  }
  assert.equal(mk(19, 19).verdict, "needs_more_contacts")
  assert.equal(mk(25, 3).verdict, "pass")
  assert.equal(mk(25, 1).verdict, "tie")
  assert.equal(mk(25, 0).verdict, "fail")
  assert.equal(mk(25, 3).strong, 3)
})

test("scorecard: an account counts once, at its best result", () => {
  const accounts = [acct({ id: "a", touches: 3 })]
  const row = scorecard(accounts, [{ accountId: "a", result: "weak" }, { accountId: "a", result: "strong" }, { accountId: "a", result: "order" }])[0]
  assert.equal(row.strong, 1)
  assert.equal(row.orders, 1)
})

test("input: only known results and kinds are accepted, and notes are capped", () => {
  assert.equal(touchSchema.safeParse({ accountId: "a", kind: "call", result: "strong" }).success, true)
  assert.equal(touchSchema.safeParse({ accountId: "a", kind: "call", result: "won" }).success, false)
  assert.equal(touchSchema.safeParse({ accountId: "a", kind: "sms", result: "weak" }).success, false)
  assert.equal(touchSchema.safeParse({ accountId: "a", kind: "note", result: "weak", note: "x".repeat(501) }).success, false)
})

test("route: no cookie, a wrong cookie, or an unset secret returns 401 before any query runs", async () => {
  process.env.RECRUITHAUS_AMMO_PASSWORD = "unit-test-passcode"
  const { GET, POST } = await import("../../src/app/api/lewoof/desk/route.ts")
  const req = (method: string, cookie?: string, body?: string) =>
    new NextRequest("https://lewoof.arcs.care/api/lewoof/desk", { method, headers: { host: "lewoof.arcs.care", ...(cookie ? { cookie: `${AMMO_COOKIE}=${cookie}` } : {}) }, body })
  assert.equal((await GET(req("GET"))).status, 401)
  assert.equal((await GET(req("GET", "deadbeef"))).status, 401)
  assert.equal((await POST(req("POST", undefined, "{}"))).status, 401)
  delete process.env.RECRUITHAUS_AMMO_PASSWORD
  assert.equal((await GET(req("GET", await ammoToken("unit-test-passcode")))).status, 401)
})

test("route: with the cookie, a malformed or oversized POST is rejected before the database", async () => {
  process.env.RECRUITHAUS_AMMO_PASSWORD = "unit-test-passcode"
  const { POST } = await import("../../src/app/api/lewoof/desk/route.ts")
  const cookie = await ammoToken("unit-test-passcode")
  const post = (body: string) => new NextRequest("https://lewoof.arcs.care/api/lewoof/desk", { method: "POST", headers: { host: "lewoof.arcs.care", cookie: `${AMMO_COOKIE}=${cookie}` }, body })
  assert.equal((await POST(post("not json"))).status, 400)
  assert.equal((await POST(post(JSON.stringify({ accountId: "a", kind: "call", result: "won" })))).status, 400)
  assert.equal((await POST(post("x".repeat(5000)))).status, 413)
})

test("proxy: /desk on the lewoof host is gated, and opens the desk page with the cookie", async () => {
  process.env.RECRUITHAUS_AMMO_PASSWORD = "unit-test-passcode"
  const { default: proxy } = await import("../../src/proxy.ts")
  const rewritten = (res: Response) => { const h = res.headers.get("x-middleware-rewrite"); return h ? new URL(h).pathname : null }
  const r = (cookie?: string) => new NextRequest("https://lewoof.arcs.care/desk", { headers: { host: "lewoof.arcs.care", ...(cookie ? { cookie: `${AMMO_COOKIE}=${cookie}` } : {}) } })
  assert.equal(rewritten(await proxy(r())), "/lewoof-gate.html")
  assert.equal(rewritten(await proxy(r(await ammoToken("unit-test-passcode")))), "/lewoof-desk.html")
})

test("seed: only the four account sections become rows; quotes are escaped; email source only with an email", () => {
  const csv = [
    "Section,Rank,Account,Type,Score,Flags (stores / channels),Website,Public contact page,Contact,Title,Email (ZoomInfo),Phone,Phone note,Source,Notes",
    `Endemic: pet boutique,1,O'Brien's Pets,Shop,78,"2 stores, wholesale",x.co,https://x.co/c,Jane Doe,Owner,jane@x.co,,,"ZoomInfo, accuracy 90",`,
    "Endemic: pet boutique,2,No Email Shop,Shop,60,,y.co,https://y.co/c,,,,,,ignored source,",
    "Sampling onramp,0,SoPost,Program,,,,,,,,,,,",
    "Retail access,0,Petco,Chain,,,,,,,,,,,",
  ].join("\n")
  const sql = toSql(parseCsv(csv))
  assert.equal(sql.length, 2)
  assert.match(sql[0], /'LW-B-001'/)
  assert.match(sql[0], /O''Brien''s Pets/)
  assert.match(sql[0], /ON CONFLICT \("id"\) DO NOTHING/)
  assert.match(sql[0], /'2 stores, wholesale'/)
  assert.doesNotMatch(sql[1], /ignored source/)
})
