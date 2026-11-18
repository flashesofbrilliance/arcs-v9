// status.arcs.care server-rendered pulse (2026-11-17): a reader that skips JavaScript must see live
// numbers, never "loading…". Runs against the real public/status.html, so a markup change that
// breaks the fill fails here.
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { fillPulse } from "../../src/lib/status-ssr.ts"

const HTML = readFileSync(new URL("../../public/status.html", import.meta.url), "utf8")
const P = {
  ok: true,
  updated: "2026-11-18T00:30:00.000Z",
  commit: { sha: "2220079", date: "2026-11-18T00:15:00Z" },
  commitsTotal: 7291,
  prsOpen: 2,
  deploy: { state: "success", date: "2026-11-18T00:20:00Z" },
}
const cell = (html: string, id: string) => html.match(new RegExp(`id="${id}">([^<]*)<`))?.[1]

test("the shipped page needs the fill (fail-on-bad)", () => {
  assert.equal(cell(HTML, "pl-commit"), "loading…")
})

test("a full pulse fills every cell and the footer", () => {
  const out = fillPulse(HTML, P)
  assert.ok(!out.includes(">loading…<"), "a pulse cell still says loading…")
  assert.equal(cell(out, "pl-commit"), "2220079")
  assert.equal(cell(out, "pl-count"), "7,291")
  assert.equal(cell(out, "sv-commits"), "7,291")
  assert.equal(cell(out, "pl-prs"), "2")
  assert.equal(cell(out, "pl-deploy"), "SUCCESS")
  assert.equal(cell(out, "pl-deploy-when"), "2026-11-18 00:20 UTC")
  assert.match(cell(out, "pulse-foot") ?? "", /data as of 2026-11-18 00:30 UTC/)
})

test("a failed or partial pulse keeps the floor and never paints a false zero", () => {
  const floor = cell(HTML, "sv-commits")
  for (const p of [null, { ok: false }, { ok: true, updated: P.updated, commit: null, commitsTotal: 0, prsOpen: null, deploy: null }]) {
    const out = fillPulse(HTML, p)
    assert.equal(cell(out, "sv-commits"), floor)
    assert.equal(cell(out, "pl-count"), "n/a")
    assert.equal(cell(out, "pulse-foot"), cell(HTML, "pulse-foot"), "a dead read must not claim 'data as of'")
    assert.ok(!out.includes(">loading…<"))
  }
})

test("values are escaped", () => {
  const out = fillPulse(HTML, { ...P, deploy: { state: "<b>x", date: P.deploy.date } })
  assert.equal(cell(out, "pl-deploy"), "&lt;B&gt;X")
})
