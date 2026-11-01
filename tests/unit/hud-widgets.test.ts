// HUD widget reads (row hud-widget-views-admin-mount). Known-bad and known-good fixtures.
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import { isGrain } from "../../src/organisms/hud/reading.ts"
import { readFidelity } from "../../src/organisms/hud/fidelity.read.ts"
import { readClarity } from "../../src/organisms/hud/clarity.read.ts"
import { readCoherence } from "../../src/organisms/hud/coherence.read.ts"
import { readConviction } from "../../src/organisms/hud/conviction.read.ts"
import { readConsonance } from "../../src/organisms/hud/consonance.read.ts"

test("honesty known-bad: n below threshold is grain; known-good: at threshold is sharp", () => {
  const field = JSON.parse(fs.readFileSync("src/data/universe-field.json", "utf8"))
  const low = { dimensions: { clarity: { nodes_clear: 2, nodes: 4 }, coherence: { diamonds: 1 } }, nodes: [] }
  assert.equal(isGrain(readClarity(low)), true)
  assert.equal(readClarity(low).n, 4)
  assert.equal(isGrain(readCoherence(low)), true)
  assert.equal(readFidelity(low).value, null)
  assert.equal(isGrain(readClarity(field)), false)
  assert.equal(isGrain(readCoherence(field)), false)
  assert.equal(isGrain(readFidelity(field)), false)
  assert.equal(readClarity(field).value, 53 / 81)
})

test("conviction always no signal; consonance grain below 30 closed, sharp at 30", () => {
  assert.equal(isGrain(readConviction({ dimensions: { conviction: { signal: 0.9 } } })), true)
  assert.equal(readConviction(null).value, null)
  assert.equal(isGrain(readConsonance({ closed: 29, meanNci: 0.8, matchedRate: 0.5 })), true)
  assert.equal(isGrain(readConsonance({ closed: 30, meanNci: 0.8, matchedRate: 0.5 })), false)
  assert.equal(readConsonance(undefined).n, 0)
})

test("reads tolerate null and malformed sources", () => {
  for (const r of [readFidelity(null), readClarity({} as never), readCoherence({ dimensions: { clarity: { nodes: "x" as never } } })]) {
    assert.equal(r.value, null)
    assert.ok(Number.isFinite(r.grain))
  }
})
