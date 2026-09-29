// Ledger YG-005 — unit tests for src/lib/ygate.ts (core Y-gate scoring, pure function).
// Pins the render-scale contract from WORLD.md and each manifold condition's effect.
import { test } from "node:test"
import assert from "node:assert/strict"
import { computeYGate } from "../../src/lib/ygate.ts"

const path = (id: string, status = "open") => ({ id, title: id, detail: "", tag: "", status })
const conds = (r: ReturnType<typeof computeYGate>) => JSON.parse(r.yConditions).map((c: any) => c.dim)

test("clean high-NCI run: GREEN / HIGH / STABLE / SHARP / LOCKED", () => {
  const r = computeYGate({ nci_score: 80 }, null, null)
  assert.equal(r.yPolarity, "GREEN")
  assert.equal(r.yConviction, "HIGH")
  assert.equal(r.yStability, "STABLE")
  assert.equal(r.renderResolution, "SHARP")
  assert.equal(r.driftState, "LOCKED")
  assert.equal(r.manifoldCurvature, "STEEP")
  assert.equal(r.flowTopology, "CONVERGENT")
  assert.equal(r.yState, r.yPolarity)
  assert.deepEqual(conds(r), [])
})

test("missing nci defaults to 50 -> YELLOW / MEDIUM / DEGRADED", () => {
  const r = computeYGate({}, null, null)
  assert.equal(r.yPolarity, "YELLOW")
  assert.equal(r.yConviction, "MEDIUM")
  assert.equal(r.renderResolution, "DEGRADED")
  assert.equal(r.gradientMagnitude, 0.5)
})

test("NCI < 40 -> SCRATCH / LOW / GRAIN / FLAT (dim 1)", () => {
  const r = computeYGate({ nci_score: 30 }, null, null)
  assert.equal(r.yPolarity, "SCRATCH")
  assert.equal(r.yConviction, "LOW")
  assert.equal(r.renderResolution, "GRAIN")
  assert.equal(r.manifoldCurvature, "FLAT")
  assert.ok(conds(r).includes(1))
})

test("two viable paths at low NCI -> PARADOX / MOIRE (dims 3+4)", () => {
  const r = computeYGate({ nci_score: 55, reasoning: { paths: [path("a"), path("b")] } }, null, null)
  assert.equal(r.yPolarity, "PARADOX")
  assert.equal(r.renderResolution, "MOIRE")
  assert.equal(r.yStability, "SHIFTING")
  assert.deepEqual(conds(r).sort(), [3, 4])
})

test("blocked paths are not viable", () => {
  const r = computeYGate({ nci_score: 80, reasoning: { paths: [path("a"), path("b", "blocked")] } }, null, null)
  assert.equal(r.yPolarity, "GREEN")
})

test("three viable paths at high NCI -> FORK / DIVERGENT / GRAIN", () => {
  const r = computeYGate({ nci_score: 80, reasoning: { paths: [path("a"), path("b"), path("c")] } }, null, null)
  assert.equal(r.yPolarity, "FORK")
  assert.equal(r.flowTopology, "DIVERGENT")
  assert.equal(r.renderResolution, "GRAIN") // SHIFTING stability outranks FORK's DEGRADED
})

test("Court BLOCK -> RED -> DELTA / LOW / CLIFF / INVERTED", () => {
  const r = computeYGate({ nci_score: 80, reasoning: { court: [{ name: "x", verdict: "BLOCK", detail: "" }] } }, null, null)
  assert.equal(r.yPolarity, "DELTA")
  assert.equal(r.yConviction, "LOW")
  assert.equal(r.flowTopology, "CLIFF")
  assert.equal(r.manifoldCurvature, "INVERTED")
})

test("Court tension (non-BLOCK) is YELLOW, not RED", () => {
  const r = computeYGate({ nci_score: 80, reasoning: { court: [{ name: "x", verdict: "WARN", detail: "" }] } }, null, null)
  assert.equal(r.yPolarity, "YELLOW")
  assert.equal(r.yStability, "CONTESTED")
})

test("ruin language in FATED -> RED (dim 9)", () => {
  const r = computeYGate({ nci_score: 80, reasoning: { fated: { tradeoffs: "risk of Irreversible Loss" } } }, null, null)
  assert.ok(conds(r).includes(9))
  assert.equal(r.yPolarity, "DELTA")
})

test("prep confidence 1 forces SCRATCH / LOW (dim 10)", () => {
  const r = computeYGate({ nci_score: 90 }, { confidence: 1 }, null)
  assert.equal(r.yPolarity, "SCRATCH")
  assert.equal(r.yConviction, "LOW")
  assert.ok(conds(r).includes(10))
})

test("TODAY + HIGH stakes adds irreversibility check (dim 5)", () => {
  const r = computeYGate({ nci_score: 80 }, { horizon: "TODAY", stakes: "HIGH" }, null)
  assert.ok(conds(r).includes(5))
  assert.equal(r.yPolarity, "YELLOW")
})

test("COURT mode without prep asks for calibration (dim 12)", () => {
  assert.ok(conds(computeYGate({ nci_score: 80, decision_mode: "COURT" }, null, null)).includes(12))
  assert.ok(!conds(computeYGate({ nci_score: 80, decision_mode: "COURT" }, {}, null)).includes(12))
})

test("unresolved parent flags re-evaluation (dim 6)", () => {
  assert.ok(conds(computeYGate({ nci_score: 80 }, null, { yState: "DELTA" })).includes(6))
  assert.ok(!conds(computeYGate({ nci_score: 80 }, null, { yState: "GREEN" })).includes(6))
})

test("conviction shift vs parent -> DELTA with prev + trigger", () => {
  const r = computeYGate({ nci_score: 80 }, null, { nciScore: 50 })
  assert.equal(r.yConvictionPrev, "MEDIUM")
  assert.equal(r.yPolarity, "DELTA")
  assert.ok(r.yDeltaTrigger)
  const same = computeYGate({ nci_score: 80 }, null, { nciScore: 70 })
  assert.equal(same.yConvictionPrev, null)
  assert.equal(same.yPolarity, "GREEN")
})

test("session versions: v3 LOOPING/CONTESTED, v5 DRIFTING (dim 8)", () => {
  const v3 = computeYGate({ nci_score: 80 }, null, null, 3)
  assert.equal(v3.flowTopology, "LOOPING")
  assert.equal(v3.yStability, "CONTESTED")
  const v5 = computeYGate({ nci_score: 80 }, null, null, 5)
  assert.equal(v5.driftState, "DRIFTING")
  assert.ok(conds(v5).includes(8))
})

test("yGateScore carries the WORLD.md visual treatment for its resolution", () => {
  const table: Record<string, number> = { SHARP: 1.0, DEGRADED: 0.85, GRAIN: 0.7, MOIRE: 0.6 }
  for (const nci of [20, 50, 55, 80]) {
    const paths = nci === 55 ? [path("a"), path("b")] : []
    const r = computeYGate({ nci_score: nci, reasoning: { paths } }, null, null)
    const s = JSON.parse(r.yGateScore)
    assert.equal(s.render_resolution, r.renderResolution)
    assert.equal(s.visual_treatment.opacity, table[r.renderResolution])
  }
})

test("deterministic: same input, same output", () => {
  const input = { nci_score: 61, reasoning: { paths: [path("a")] } }
  assert.deepEqual(computeYGate(input, null, null), computeYGate(input, null, null))
})
