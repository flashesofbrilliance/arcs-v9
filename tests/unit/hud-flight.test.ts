// Row hud-atlas-v2-flight (R11): the HUD v2 flight reads an arcs.atlas.v2 file, scrubs it in time, and
// earns its fidelity from the file's own rule. Fixture: the Gasmi J5 export (17 nodes, 12 edges, 2 kairos).
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import { toFlight, tierReads, facetsAt, nodeAt, wrapDeg, project, mmss } from "../../src/app/hud/flight.ts"

const raw = JSON.parse(fs.readFileSync("runtime/recoil/generated/2026-10-29-gasmi.atlas.json", "utf8"))
const f = toFlight(raw)!

test("v2 loads as a flight; v1 does not (it keeps the terrace-only loader)", () => {
  assert.ok(f)
  assert.equal(f.nodes.length, 17)
  assert.equal(f.edges.length, 12)
  assert.equal(f.maxS, 1668)
  const v1 = JSON.parse(fs.readFileSync("_ARTIFACTS/forge-monday-fde/takehome/atlas.json", "utf8"))
  assert.equal(toFlight(v1), null)
})

test("at the end of the call, the live fidelity equals the render J5 wrote into every tier", () => {
  const reads = tierReads(f, f.maxS)
  assert.deepEqual(reads.map((r) => r.render), raw.tiers.map((t: { render: string }) => t.render))
  assert.deepEqual(reads.map((r) => r.edges), raw.tiers.map((t: { edges: number }) => t.edges))
})

test("scrubbing back shrinks fidelity: before the first edge every populated tier is grain, n = 0", () => {
  const reads = tierReads(f, 0)
  assert.equal(facetsAt(f, 0), 0)
  assert.deepEqual(reads.map((r) => r.render), ["FLAT", "FLAT", "FLAT", "GRAIN", "GRAIN"], "atoms and people not yet said; beliefs at s=0 and unanchored decisions are present")
  assert.ok(reads.every((r) => r.edges === 0))
  assert.ok(facetsAt(f, 1000) < facetsAt(f, f.maxS), "facets grow with time")
  assert.ok(nodeAt(f.nodes.find((n) => n.id === "decision:n1")!, 0), "a node with t null shows at every time")
})

test("kairos list matches the file (and so the SSOT, by the schema) in time order", () => {
  assert.deepEqual(f.kairos.map((k) => k.id), ["k02", "k01"])
  assert.deepEqual(new Set(f.kairos.map((k) => k.id)), new Set(raw.kairos.map((k: { id: string }) => k.id)))
})

test("empty atlas renders flat: every tier FLAT, n = 0, no facets", () => {
  const empty = { ...raw, nodes: [], edges: [], kairos: [], unanchored: [], tiers: raw.tiers.map((t: object) => ({ ...t, docs: 0, edges: 0, n: 0, render: "FLAT", gate: "fail" })) }
  const e = toFlight(empty)!
  assert.equal(e.maxS, 0)
  assert.ok(tierReads(e, 0).every((r) => r.render === "FLAT" && r.edges === 0))
  assert.equal(facetsAt(e, 0), 0)
})

test("orbit wraps a full 360 and a quarter turn swaps x for depth", () => {
  assert.equal(wrapDeg(370), 10)
  assert.equal(wrapDeg(-30), 330)
  const p0 = project([1, 0, 0], 0, 100, 0, 0), p90 = project([1, 0, 0], 90, 100, 0, 0)
  assert.equal(Math.round(p0.x), 100)
  assert.equal(Math.round(p90.x), 0)
  assert.equal(Math.round(p90.z), 1)
  assert.equal(mmss(1668), "27:48")
})
