// HUD widgets (row hud-widget-views-admin-mount). Fixtures fixed before the views were built.
import { test } from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import { snap, fitCell, orientationOf } from "../../src/organisms/hud/snap.ts"
import { isGrain } from "../../src/organisms/hud/reading.ts"
import { readFidelity } from "../../src/organisms/hud/fidelity.read.ts"
import { readClarity } from "../../src/organisms/hud/clarity.read.ts"
import { readCoherence } from "../../src/organisms/hud/coherence.read.ts"
import { readConviction } from "../../src/organisms/hud/conviction.read.ts"
import { readConsonance } from "../../src/organisms/hud/consonance.read.ts"

const LAND: Array<[number, number, number, number]> = [
  [0, 0, 0, 0], [95, 95, 0, 0], [96, 96, 1, 1], [100, 200, 1, 2], [500, 300, 5, 3], [1000, 700, 10, 7],
  [2303, 1151, 23, 11], [2304, 1152, 23, 11], [-5, -5, 0, 0], [1e9, 1e9, 23, 11], [191, 0, 1, 0], [192, 288, 2, 3],
]
const PORT: Array<[number, number, number, number]> = [
  [0, 0, 0, 0], [79, 79, 0, 0], [80, 80, 1, 1], [100, 200, 1, 2], [400, 300, 5, 3], [559, 1199, 6, 14],
  [639, 1279, 7, 15], [640, 1280, 7, 15], [-5, -5, 0, 0], [1e9, 1e9, 7, 15], [160, 0, 2, 0], [240, 320, 3, 4],
]

test("snap known-good: 12 points per orientation map exactly", () => {
  for (const [x, y, col, row] of LAND) assert.deepEqual(snap(x, y, "landscape"), { col, row }, `landscape ${x},${y}`)
  for (const [x, y, col, row] of PORT) assert.deepEqual(snap(x, y, "portrait"), { col, row }, `portrait ${x},${y}`)
})

test("snap known-bad: non-finite returns null, never NaN", () => {
  for (const v of [NaN, Infinity, -Infinity]) {
    assert.equal(snap(v, 0, "landscape"), null)
    assert.equal(snap(0, v, "portrait"), null)
  }
})

test("fitCell: zero-size viewport clamps to 0,0, no NaN", () => {
  assert.deepEqual(fitCell({ col: 5, row: 5 }, 0, 0, "landscape"), { col: 0, row: 0 })
  assert.deepEqual(fitCell({ col: NaN, row: 5 }, NaN, 800, "landscape"), { col: 0, row: 5 })
  assert.deepEqual(fitCell({ col: 23, row: 11 }, 960, 480, "landscape", 2, 3), { col: 8, row: 2 })
  assert.equal(orientationOf(390, 844), "portrait")
  assert.equal(orientationOf(1280, 800), "landscape")
})

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
