// Gate regression for percent-encoded paths (2026-11-05). The platform decodes a path once
// before it serves a public/ file, so /%63ia-brief.html reached the cia brief while the
// proxy's raw startsWith('/cia-brief') saw "%63ia" and let it through. The proxy now decodes
// before any gate check; a malformed escape is a 400, never a pass.
import { test } from "node:test"
import assert from "node:assert/strict"
import { NextRequest } from "next/server"

process.env.RECRUITHAUS_AMMO_PASSWORD = "unit-test-passcode"
process.env.CIA_PASSCODE = "unit-test-cia"
const { default: proxy } = await import("../../src/proxy.ts")

const req = (host: string, path: string) => new NextRequest(`https://${host}${path}`, { headers: { host } })
const rewritten = (res: Response) => {
  const h = res.headers.get("x-middleware-rewrite")
  return h ? new URL(h).pathname : null
}

test("encoded paths to a cia file still show the cia gate", async () => {
  for (const path of ["/%63ia-brief.html", "/cia%2Dbrief.html", "/%63%69%61-brief.html"]) {
    assert.equal(rewritten(await proxy(req("app.arcs.care", path))), "/cia-gate.html", path)
  }
})

test("encoded paths to a Le Woof file still show the Le Woof gate", async () => {
  for (const path of ["/%6Cewoof-playbook.html", "/lewoof%2Dintake.html"]) {
    assert.equal(rewritten(await proxy(req("app.arcs.care", path))), "/lewoof-gate.html", path)
  }
})

test("a malformed escape is refused, not passed through", async () => {
  const res = await proxy(req("app.arcs.care", "/%E0%A4%A.html"))
  assert.equal(res.status, 400)
})
