// Gate regression for lewoof.arcs.care (2026-10-07). The Le Woof playbook holds partner
// deal terms and the intake page holds a counterparty's contact details, so:
//   1. the whole lewoof host is locked behind the shared passcode (root and /invoicing),
//   2. every Le Woof file (/lewoof-*, /lewoof.html) is locked on EVERY host (public/ files
//      are directly fetchable), and
//   3. the gate page and /api stay open, other hosts still route as before, and an unset
//      secret keeps everything locked (fail closed).
import { test } from "node:test"
import assert from "node:assert/strict"
import { NextRequest } from "next/server"
import { AMMO_COOKIE, ammoToken } from "../../src/lib/ammo-gate.ts"

const SECRET = "unit-test-passcode"
process.env.RECRUITHAUS_AMMO_PASSWORD = SECRET
const { default: proxy } = await import("../../src/proxy.ts")

const req = (host: string, path: string, cookie?: string) =>
  new NextRequest(`https://${host}${path}`, { headers: { host, ...(cookie ? { cookie: `${AMMO_COOKIE}=${cookie}` } : {}) } })
const rewritten = (res: Response) => {
  const h = res.headers.get("x-middleware-rewrite")
  return h ? new URL(h).pathname : null
}
const passed = (res: Response) => res.headers.get("x-middleware-next") === "1"
const GATE = "/lewoof-gate.html"

test("locked: the lewoof root and /invoicing show the gate", async () => {
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/"))), GATE)
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/invoicing"))), GATE)
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/anything-else"))), GATE)
})

test("locked: Le Woof files cannot be fetched directly on any host", async () => {
  for (const host of ["app.arcs.care", "arcs.care", "lewoof.arcs.care", "squad.arcs.care"]) {
    for (const path of ["/lewoof-playbook.html", "/lewoof-intake.html", "/lewoof.html"]) {
      assert.equal(rewritten(await proxy(req(host, path))), GATE, `${host}${path}`)
    }
  }
})

test("open: the gate page, the unlock API and shared icons stay reachable", async () => {
  assert.ok(passed(await proxy(req("lewoof.arcs.care", "/lewoof-gate.html"))))
  assert.ok(passed(await proxy(req("app.arcs.care", "/lewoof-gate.html"))))
  assert.ok(passed(await proxy(req("lewoof.arcs.care", "/api/recruithaus/unlock"))))
  assert.ok(passed(await proxy(req("lewoof.arcs.care", "/icon.svg"))))
})

test("unlocked: root serves the playbook and /invoicing serves the intake page", async () => {
  const c = await ammoToken(SECRET)
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/", c))), "/lewoof-playbook.html")
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/invoicing", c))), "/lewoof-intake.html")
  assert.ok(passed(await proxy(req("app.arcs.care", "/lewoof-playbook.html", c))))
})

test("a wrong cookie does not unlock", async () => {
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/", "deadbeef"))), GATE)
  const other = await ammoToken("a-different-secret")
  assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/", other))), GATE)
})

test("fail closed: with no secret configured, even a well-formed cookie stays locked", async () => {
  const c = await ammoToken(SECRET)
  delete process.env.RECRUITHAUS_AMMO_PASSWORD
  try {
    assert.equal(rewritten(await proxy(req("lewoof.arcs.care", "/", c))), GATE)
    assert.equal(rewritten(await proxy(req("app.arcs.care", "/lewoof-intake.html", c))), GATE)
  } finally {
    process.env.RECRUITHAUS_AMMO_PASSWORD = SECRET
  }
})

test("other hosts keep their routing", async () => {
  assert.equal(rewritten(await proxy(req("squad.arcs.care", "/"))), "/squad.html")
  assert.equal(rewritten(await proxy(req("resume.arcs.care", "/"))), "/resume.html")
})

test('next.config.ts has no host rewrite for lewoof.arcs.care (it would bypass the proxy gate)', async () => {
  const { readFileSync } = await import('node:fs')
  const cfg = readFileSync(new URL('../../next.config.ts', import.meta.url), 'utf8')
  assert.equal(/lewoof/i.test(cfg), false)
})
