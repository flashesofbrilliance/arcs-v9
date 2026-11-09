// Gate regression for louisville.arcs.care (2026-11-05). Two gates on one host:
//   1. /proposal (the Louisville Brands audit proposal) has its own passcode that opens nothing else,
//   2. everything else on the host (the root pitch suite, /omakase) sits behind LOUISVILLE_PASSCODE,
//   3. the proposal files and louisville.html are locked on every host, encoded paths included,
//   4. the earlier ammo and lewoof passthroughs cannot leak the pitch suite, and an unset secret
//      keeps everything locked (fail closed).
import { test } from "node:test"
import assert from "node:assert/strict"
import { NextRequest } from "next/server"
import { LOUISVILLE_GATE, LOUISVILLE_PROPOSAL_GATE, gateToken } from "../../src/lib/passcode-gate.ts"

const ROOT = "unit-test-louisville"
const PROPOSAL = "unit-test-louisville-proposal"
process.env.LOUISVILLE_PASSCODE = ROOT
process.env.LOUISVILLE_PROPOSAL_PASSCODE = PROPOSAL
process.env.RECRUITHAUS_AMMO_PASSWORD = "unit-test-passcode"
const { default: proxy } = await import("../../src/proxy.ts")

const H = "louisville.arcs.care"
const req = (host: string, path: string, cookies: Record<string, string> = {}) => {
  const cookie = Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join("; ")
  return new NextRequest(`https://${host}${path}`, { headers: { host, ...(cookie ? { cookie } : {}) } })
}
const rewritten = (res: Response) => {
  const h = res.headers.get("x-middleware-rewrite")
  return h ? new URL(h).pathname : null
}
const passed = (res: Response) => res.headers.get("x-middleware-next") === "1"
const GATE = "/louisville-gate.html"
const PGATE = "/louisville-proposal-gate.html"
const rootCookie = async () => ({ [LOUISVILLE_GATE.cookie]: await gateToken(LOUISVILLE_GATE.ns, ROOT) })
const propCookie = async () => ({ [LOUISVILLE_PROPOSAL_GATE.cookie]: await gateToken(LOUISVILLE_PROPOSAL_GATE.ns, PROPOSAL) })

test("locked: with no cookie the root, omakase and stray paths show the root gate", async () => {
  for (const path of ["/", "/omakase", "/omakase/atom", "/anything", "/apix", "/lewoof-gate.html", "/lewoof-x", "/recruithaus-ammo", "/schriner-ammo"]) {
    assert.equal(rewritten(await proxy(req(H, path))), GATE, path)
  }
})

test("locked: with no cookie /proposal and its PDF show the proposal gate", async () => {
  assert.equal(rewritten(await proxy(req(H, "/proposal"))), PGATE)
  assert.equal(rewritten(await proxy(req(H, "/proposal/outside-read.pdf"))), PGATE)
})

test("locked: proposal files and louisville.html cannot be fetched directly on any host", async () => {
  for (const host of ["app.arcs.care", "arcs.care", H, "cia.arcs.care"]) {
    for (const path of ["/louisville-proposal.html", "/louisville-proposal.pdf", "/%6Couisville-proposal.html", "/louisville%2Dproposal.pdf"]) {
      assert.equal(rewritten(await proxy(req(host, path))), PGATE, `${host}${path}`)
    }
    assert.equal(rewritten(await proxy(req(host, "/louisville.html"))), GATE, `${host}/louisville.html`)
  }
})

test("open: gate pages, the unlock APIs and real static files stay reachable", async () => {
  assert.ok(passed(await proxy(req(H, GATE))))
  assert.ok(passed(await proxy(req(H, PGATE))))
  assert.ok(passed(await proxy(req(H, "/api/louisville/unlock"))))
  assert.ok(passed(await proxy(req(H, "/api/louisville-proposal/unlock"))))
  assert.ok(passed(await proxy(req(H, "/robots.txt"))))
  assert.ok(passed(await proxy(req(H, "/icon.svg"))))
})

test("the proposal cookie opens the proposal and nothing else", async () => {
  const c = await propCookie()
  assert.equal(rewritten(await proxy(req(H, "/proposal", c))), "/louisville-proposal.html")
  assert.equal(rewritten(await proxy(req(H, "/proposal/outside-read.pdf", c))), "/louisville-proposal.pdf")
  for (const path of ["/", "/omakase", "/omakase/atom", "/louisville.html"]) {
    assert.equal(rewritten(await proxy(req(H, path, c))), GATE, path)
  }
})

test("the root cookie opens the pitch suite and not the proposal", async () => {
  const c = await rootCookie()
  assert.equal(rewritten(await proxy(req(H, "/", c))), "/louisville.html")
  assert.ok(passed(await proxy(req(H, "/omakase", c))))
  assert.ok(passed(await proxy(req(H, "/omakase/atom", c))))
  assert.equal(rewritten(await proxy(req(H, "/proposal", c))), PGATE)
})

test("fail closed: with no secrets configured, well-formed cookies stay locked", async () => {
  const p = await propCookie(), r = await rootCookie()
  delete process.env.LOUISVILLE_PASSCODE
  delete process.env.LOUISVILLE_PROPOSAL_PASSCODE
  try {
    assert.equal(rewritten(await proxy(req(H, "/proposal", p))), PGATE)
    assert.equal(rewritten(await proxy(req(H, "/", r))), GATE)
  } finally {
    process.env.LOUISVILLE_PASSCODE = ROOT
    process.env.LOUISVILLE_PROPOSAL_PASSCODE = PROPOSAL
  }
})
