// Row atlas-v2-schema-export (R9): the HUD ziggurat loader still loads arcs.atlas.v1 files, and an
// arcs.atlas.v2 export (scripts/recoil_stage_j5.py) loads its tiers through the same contract.
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import { parseAtlas, toZigTiers } from "../../src/app/hud/atlas.ts"

const read = (p: string) => fs.readFileSync(p, "utf8")

test("v1 file still loads: the monday FDE take-home atlas gives 12 terraces", () => {
  const got = parseAtlas(read("_ARTIFACTS/forge-monday-fde/takehome/atlas.json"))
  assert.ok("atlas" in got, "v1 atlas parses")
  const tiers = toZigTiers(got.atlas)
  assert.equal(tiers.length, 12)
  assert.equal(tiers[0].name, "Pre-work")
  assert.equal(tiers[0].docs, 5)
  assert.ok(tiers.every((t) => ["pass", "warn", "fail"].includes(t.gate)))
})

test("v2 file loads its tiers: the Gasmi J5 export gives the five terraces with node counts", () => {
  const raw = JSON.parse(read("runtime/recoil/generated/2026-10-29-gasmi.atlas.json"))
  const got = parseAtlas(JSON.stringify(raw))
  assert.ok("atlas" in got, "v2 atlas parses")
  const tiers = toZigTiers(got.atlas)
  assert.deepEqual(tiers.map((t) => t.name), ["Atoms", "People", "Claims", "Beliefs", "Decisions"])
  assert.deepEqual(tiers.map((t) => t.docs), raw.tiers.map((t: { docs: number }) => t.docs))
  assert.equal(tiers[2].gate, "fail", "an empty tier (FLAT) shows as a fail terrace, not hidden")
})

test("known-bad: wrong schema, no tiers and bad JSON are refused", () => {
  assert.ok("error" in parseAtlas(JSON.stringify({ schema: "arcs.atlas.v3", tiers: [{}] })))
  assert.ok("error" in parseAtlas(JSON.stringify({ schema: "arcs.atlas.v2", tiers: [] })))
  assert.ok("error" in parseAtlas("{not json"))
})
