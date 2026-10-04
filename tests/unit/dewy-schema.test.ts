// Enforces runtime/specs/dewy-receipt-schema-v1.json (draft-07), which nothing checked before
// (platform-standards audit, 2026-10-04). The JSON file is compiled with zod's fromJSONSchema,
// so the file itself is the contract: no hand-written mirror to drift from it.
//
// Two kinds of test live here:
//   1. conformance: representative receipts and the REAL computeYGate output must validate.
//   2. KNOWN DRIFT: places where the Prisma Receipt model stores values the schema rejects.
//      These are reported, not fixed. Each asserts the drift still exists, so reconciling
//      either side fails the test and forces whoever fixed it to delete the drift entry.
import { test } from "node:test"
import assert from "node:assert/strict"
import { readFileSync } from "node:fs"
import { z } from "zod"
import { computeYGate } from "../../src/lib/ygate.ts"

const json = JSON.parse(readFileSync(new URL("../../runtime/specs/dewy-receipt-schema-v1.json", import.meta.url), "utf8"))
const Receipt = z.fromJSONSchema(json)
const sub = (name: string) => z.fromJSONSchema(json.properties[name])
const paths = (r: { success: boolean; error?: { issues: { path: PropertyKey[] }[] } }) =>
  (r.error?.issues ?? []).map(i => i.path.join("."))

const valid = () => ({
  receipt_id: "ARCS-ORIENT-2026-05-26T13:01:00Z-a3f9c21b",
  surface: "ORIENT",
  version: "0.1.0",
  sharp_question: "Should I take the offer before Friday?",
  dewy_vector: {
    D: "Accept or decline the offer",
    E: { self: "me", other: ["hiring manager"] },
    W: { horizon: "WEEK", lock_date: "2026-05-29", inferred: false },
    Y: { polarity: "YELLOW", conviction: "MEDIUM", stability: "CONTESTED" },
  },
  y_gate_score: { polarity: "YELLOW", conviction: "MEDIUM", stability: "CONTESTED", render_resolution: "DEGRADED" },
  nci_score: { composite: 62, grade: "C+", by_lens: { clarity: 14, conviction: 10, coherence: 13, consequence: 12, cadence: 13 } },
  true_north: "Ask for 48 hours and one comp lever",
  why: ["Deadline is soft", "Comp gap is negotiable"],
  loki: "Asking for time signals low enthusiasm",
  bar: { ruin_risk: "low", asymmetry: "upside", reversibility: "two-way" },
  render_resolution: "DEGRADED",
  validation_state: "PASS",
  session_ts: "2026-05-26T13:01:00Z",
})

test("schema file is draft-07 and compiles", () => {
  assert.equal(json.$schema, "http://json-schema.org/draft-07/schema#")
  assert.equal(json.additionalProperties, false)
})

test("a fully populated ORIENT receipt validates", () => {
  const r = Receipt.safeParse(valid())
  assert.ok(r.success, JSON.stringify(paths(r)))
})

test("optional fields validate when present", () => {
  const r = Receipt.safeParse({
    ...valid(), horizon: "WEEK", stakes: "MEDIUM", mode: "PLAN", clarity_mode: "RICH",
    macros_run: ["LAB", "BAR"], drift_state: "ON_TRACK", inferred_fields: ["W.horizon"],
    collision_fields: [], fidelity_header: "Contested terrain", prep_session_id: "p1", parent_receipt_id: "r0",
  })
  assert.ok(r.success, JSON.stringify(paths(r)))
})

test("every required field is enforced", () => {
  for (const key of json.required as string[]) {
    const v: Record<string, unknown> = valid()
    delete v[key]
    assert.equal(Receipt.safeParse(v).success, false, `missing ${key} should fail`)
  }
})

test("bounds and enums reject bad values", () => {
  const bad: [string, Record<string, unknown>][] = [
    ["unknown top-level key", { extra: 1 }],
    ["receipt_id pattern", { receipt_id: "R-123" }],
    ["sharp_question > 280", { sharp_question: "x".repeat(281) }],
    ["why empty", { why: [] }],
    ["why > 5", { why: ["a", "b", "c", "d", "e", "f"] }],
    ["composite > 100", { nci_score: { ...valid().nci_score, composite: 101 } }],
    ["lens > 20", { nci_score: { ...valid().nci_score, by_lens: { ...valid().nci_score.by_lens, cadence: 21 } } }],
    ["render_resolution enum", { render_resolution: "BLURRY" }],
    ["validation_state enum", { validation_state: "OK" }],
    ["session_ts not date-time", { session_ts: "yesterday" }],
    ["macros_run enum", { macros_run: ["SAGE"] }],
  ]
  for (const [name, patch] of bad) {
    assert.equal(Receipt.safeParse({ ...valid(), ...patch }).success, false, name)
  }
})

// The real producer: every yGateScore computeYGate emits must satisfy the schema's y_gate_score,
// and its polarity / drift state must be values the schema knows.
const scenarios: [string, Parameters<typeof computeYGate>][] = [
  ["high NCI", [{ nci_score: 80 }, null, null]],
  ["default NCI", [{}, null, null]],
  ["low NCI", [{ nci_score: 30 }, null, null]],
  ["court BLOCK", [{ nci_score: 80, reasoning: { court: [{ name: "x", verdict: "BLOCK", detail: "" }] } }, null, null]],
  ["two open paths", [{ nci_score: 55, paths: [{ id: "a", title: "a", detail: "", tag: "", status: "open" }, { id: "b", title: "b", detail: "", tag: "", status: "open" }] }, null, null]],
]

test("computeYGate output conforms to y_gate_score, Y.polarity and drift_state", () => {
  const YGate = sub("y_gate_score")
  const Polarity = z.fromJSONSchema(json.properties.dewy_vector.properties.Y.properties.polarity)
  const Drift = sub("drift_state")
  for (const [name, args] of scenarios) {
    const out = computeYGate(...args)
    const g = YGate.safeParse(JSON.parse(out.yGateScore))
    assert.ok(g.success, `${name}: ${JSON.stringify(paths(g))}`)
    assert.ok(Polarity.safeParse(out.yPolarity).success, `${name}: polarity ${out.yPolarity}`)
    assert.ok(Drift.safeParse(out.driftState).success, `${name}: driftState ${out.driftState}`)
    assert.ok(sub("render_resolution").safeParse(out.renderResolution).success, `${name}: ${out.renderResolution}`)
  }
})

// ── KNOWN DRIFT (Prisma model vs schema) ─────────────────────────────────────────────────
// Reported 2026-10-04, deliberately NOT fixed here. Delete an entry when it is reconciled.

test("KNOWN DRIFT: legacy Receipt.window values are not schema horizons", () => {
  // prisma Receipt.window stores TODAY | THIS_WEEK | THIS_QUARTER | ONE_TO_THREE_YEARS;
  // the schema's horizon is TODAY | WEEK | QUARTER | YEAR | YEARS. Only TODAY overlaps.
  const H = sub("horizon")
  for (const w of ["THIS_WEEK", "THIS_QUARTER", "ONE_TO_THREE_YEARS"]) assert.equal(H.safeParse(w).success, false, w)
})

test("KNOWN DRIFT: surface EPHEMERAL_SAVE is written but not in the schema enum", () => {
  // src/app/api/receipts/save/route.ts writes surface: "EPHEMERAL_SAVE" (ADR-049)
  assert.equal(sub("surface").safeParse("EPHEMERAL_SAVE").success, false)
})

test("KNOWN DRIFT: Prisma lets schema-required fields be null", () => {
  // receiptId, sharpQuestion, dewyVector, loki, bar, nciGrade, nciByLens, yGateScore, sessionTs
  // are nullable in prisma/schema.prisma; the schema requires their projections. A row
  // missing loki (null) cannot be projected to a valid receipt.
  const v: Record<string, unknown> = valid()
  delete v.loki
  assert.equal(Receipt.safeParse(v).success, false)
})
