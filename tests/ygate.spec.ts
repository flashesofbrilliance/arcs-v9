import { test, expect } from "@playwright/test"
import { computeYGate } from "../src/lib/ygate"

// Ledger YG-005: unit coverage for the Y-gate manifold (pure function, was
// untested). Table-driven against the canonical polarity/conviction/stability
// enums. Where WORLD.md and the code disagree (e.g. FORK renders GRAIN via
// SHIFTING stability, not DEGRADED), the code is canonical — see memory
// "kinematic manifold: code wins over doc".

const parsed = (over: Record<string, unknown> = {}) => ({
  nci_score: 80,
  decision_mode: "PLAN",
  reasoning: { court: [], paths: [{ status: "selected" }], fated: {} },
  ...over,
})

test("clean high-coherence run → GREEN/HIGH/STABLE, LOCKED drift, SHARP render", () => {
  const y = computeYGate(parsed(), null, null, 0)
  expect(y.yPolarity).toBe("GREEN")
  expect(y.yConviction).toBe("HIGH")
  expect(y.yStability).toBe("STABLE")
  expect(y.driftState).toBe("LOCKED")
  expect(y.renderResolution).toBe("SHARP")
  expect(y.yState).toBe(y.yPolarity) // yState mirrors polarity (compat)
})

test("nci < 40 with no fork → SCRATCH/LOW, GRAIN render", () => {
  const y = computeYGate(parsed({ nci_score: 30 }), null, null, 0)
  expect(y.yPolarity).toBe("SCRATCH")
  expect(y.yConviction).toBe("LOW")
  expect(y.renderResolution).toBe("GRAIN")
})

test("two viable paths at decent coherence → FORK, SHIFTING (renders GRAIN per code)", () => {
  const y = computeYGate(
    parsed({ nci_score: 70, reasoning: { court: [], paths: [{ status: "a" }, { status: "b" }], fated: {} } }),
    null, null, 0
  )
  expect(y.yPolarity).toBe("FORK")
  expect(y.yStability).toBe("SHIFTING")
  expect(y.renderResolution).toBe("GRAIN")
})

test("two viable paths + low coherence → PARADOX, MOIRE render", () => {
  const y = computeYGate(
    parsed({ nci_score: 55, reasoning: { court: [], paths: [{ status: "a" }, { status: "b" }], fated: {} } }),
    null, null, 0
  )
  expect(y.yPolarity).toBe("PARADOX")
  expect(y.renderResolution).toBe("MOIRE")
})

test("Court BLOCK verdict → RED condition → DELTA polarity, LOW conviction", () => {
  const y = computeYGate(
    parsed({ reasoning: { court: [{ verdict: "BLOCK" }], paths: [{ status: "selected" }], fated: {} } }),
    null, null, 0
  )
  expect(y.yPolarity).toBe("DELTA")
  expect(y.yConviction).toBe("LOW")
  expect(y.renderResolution).toBe("GRAIN")
  expect(JSON.parse(y.yConditions).some((c: { severity: string }) => c.severity === "RED")).toBe(true)
})

test("ruin language in FATED → RED condition regardless of coherence", () => {
  const y = computeYGate(
    parsed({ reasoning: { court: [], paths: [{ status: "selected" }], fated: { tradeoffs: "risk of irreversible loss here" } } }),
    null, null, 0
  )
  expect(y.yPolarity).toBe("DELTA")
  expect(JSON.parse(y.yConditions).some((c: { label: string }) => c.label.includes("Ruin risk"))).toBe(true)
})

test("prep confidence=1 (entering lost) → SCRATCH/LOW even at high nci", () => {
  const y = computeYGate(parsed(), { confidence: 1 }, null, 0)
  expect(y.yPolarity).toBe("SCRATCH")
  expect(y.yConviction).toBe("LOW")
})

test("session v5+ → drift sentinel fires: YELLOW polarity, DRIFTING state", () => {
  const y = computeYGate(parsed(), null, null, 5)
  expect(y.yPolarity).toBe("YELLOW")
  expect(y.driftState).toBe("DRIFTING")
  expect(JSON.parse(y.yConditions).some((c: { dim: number }) => c.dim === 8)).toBe(true)
})

test("conviction shift vs parent → DELTA with yConvictionPrev recorded", () => {
  const y = computeYGate(parsed({ nci_score: 50 }), null, { nciScore: 80 }, 1)
  expect(y.yConvictionPrev).toBe("HIGH")
  expect(y.yConviction).toBe("MEDIUM")
  expect(y.yPolarity).toBe("DELTA")
  expect(y.yDeltaTrigger).not.toBeNull()
})

test("yGateScore JSON carries render treatment consistent with resolution", () => {
  const y = computeYGate(parsed(), null, null, 0)
  const score = JSON.parse(y.yGateScore)
  expect(score.render_resolution).toBe(y.renderResolution)
})
