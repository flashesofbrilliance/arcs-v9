// /api/pulse public payload: counts only (never titles, paths, keys, names, balances), and
// a failed or implausibly empty read is null, never 0, so status.arcs.care keeps its floor.
// Fail-on-bad: every unsafe fixture below must be caught by assertPublicSafe.
import { test } from "node:test"
import assert from "node:assert/strict"
import {
  assertPublicSafe, PUBLIC_ITEMS, publicItems, riskStates, shapeGates, shapeTempo, summarizeDebt, weekStarts,
  type DebtIssue,
} from "../../src/lib/pulse.ts"

const issue = (number: number, state: "OPEN" | "CLOSED", ...labels: string[]): DebtIssue => ({ number, state, labels: ["debt", ...labels] })
const ISSUES = [
  issue(1000, "OPEN", "sev:P2", "status:decision"),
  issue(1019, "OPEN", "sev:P2", "status:decision"),
  issue(973, "OPEN", "sev:P2", "status:in-progress"),
  issue(1, "OPEN", "sev:P3", "status:open"),
  issue(2, "CLOSED", "sev:P1", "status:done"),
  issue(3, "CLOSED", "sev:P2", "status:in-progress"), // closed wins over a stale label
]

function samplePayload() {
  return {
    ok: true,
    updated: "2026-10-06T15:00:00.000Z",
    commit: { sha: "90747c2", date: "2026-10-06T14:00:00Z" },
    commitsTotal: 3575,
    prsOpen: 12,
    deploy: { state: "success", date: "2026-10-06T14:05:00Z" },
    debt: summarizeDebt(ISSUES),
    risks: riskStates(ISSUES),
    tempo: shapeTempo(["2026-09-28", "2026-10-05"], [130, 198]),
    gates: shapeGates({ receipts: 267, externalReceipts: 10, closed: { founder: 3, external: 0, anonymous: 0 } }),
    evals: null,
    degraded: [] as string[],
  }
}

test("debt summary counts status labels; closed issues are done", () => {
  const d = summarizeDebt(ISSUES)!
  assert.deepEqual(d.byStatus, { open: 1, "in-progress": 1, decision: 2, done: 2 })
  assert.equal(d.total, 6); assert.equal(d.open, 4)
  assert.deepEqual(d.bySev, { P1: 0, P2: 3, P3: 1 }) // open only
})

test("no false zeros: empty or failed reads are null, not 0", () => {
  assert.equal(summarizeDebt([]), null)
  assert.equal(summarizeDebt(null), null)
  assert.equal(riskStates([]), null)
  assert.equal(shapeTempo(["a", "b"], [0, 0]), null, "all-zero weeks is a failed read")
  assert.equal(shapeTempo(["a", "b"], [3, null]), null, "a missing week voids the series")
  assert.equal(shapeGates(null), null)
  assert.equal(shapeGates({ receipts: 0, externalReceipts: 0, closed: { founder: 0, external: 0, anonymous: 0 } }), null)
})

test("gates count external decisions, not founder QA", () => {
  const g = shapeGates({ receipts: 267, externalReceipts: 10, closed: { founder: 3, external: 0, anonymous: 0 } })!
  assert.deepEqual(g.calibration, { n: 0, gate: 30, cohort: "external" })
  assert.deepEqual(g.goalMap, { n: 10, gate: 100 })
})

test("risk rows carry only sev/status under neutral slugs", () => {
  assert.deepEqual(riskStates(ISSUES), {
    "spend-cap": { sev: "P2", status: "decision" },
    "write-lock": { sev: "P2", status: "decision" },
    "ci-spend": { sev: "P2", status: "in-progress" },
  })
})

test("weekStarts returns Monday-start UTC weeks ending this week", () => {
  assert.deepEqual(weekStarts(new Date("2026-10-07T12:00:00Z"), 3), ["2026-09-21", "2026-09-28", "2026-10-05"])
})

test("a realistic payload passes the public-safety check", () => {
  assert.deepEqual(assertPublicSafe(samplePayload()), [])
})

test("public-safety check catches every leak class (fail-on-bad)", () => {
  const leaks: Array<[string, (p: ReturnType<typeof samplePayload>) => unknown]> = [
    ["issue title key", (p) => ({ ...p, debt: { ...p.debt, title: "x" } })],
    ["issue body key", (p) => ({ ...p, body: "x" })],
    ["commit message", (p) => ({ ...p, commit: { ...p.commit, message: "fix" } })],
    ["email", (p) => ({ ...p, deploy: { state: "someone@example.com", date: "x" } })],
    ["anthropic key", (p) => ({ ...p, deploy: { state: "sk-ant-abcdef123456", date: "x" } })],
    ["github token", (p) => ({ ...p, deploy: { state: "ghp_abcdefghijk1234", date: "x" } })],
    ["file path", (p) => ({ ...p, deploy: { state: "see scripts/oracle.py", date: "x" } })],
    ["env file", (p) => ({ ...p, deploy: { state: "in .env.local", date: "x" } })],
    ["key location", (p) => ({ ...p, deploy: { state: "ANTHROPIC_API_KEY", date: "x" } })],
    ["balance", (p) => ({ ...p, deploy: { state: "$412 left", date: "x" } })],
    ["counterpart name key", (p) => ({ ...p, counterpart: "x" })],
  ]
  for (const [name, mut] of leaks) {
    assert.ok(assertPublicSafe(mut(samplePayload())).length > 0, `${name} must be caught`)
  }
})

test("publicItems: curated labels land on the card for the issue's LIVE status", () => {
  const items = publicItems(ISSUES)
  assert.deepEqual(items, {
    decision: [PUBLIC_ITEMS[1000], PUBLIC_ITEMS[1019]],
    open: [],
    "in-progress": [PUBLIC_ITEMS[973]],
    done: [],
  })
  const closed = publicItems([issue(1000, "CLOSED", "status:decision")])
  assert.deepEqual(closed?.done, [PUBLIC_ITEMS[1000]]) // closed wins over a stale label
})

test("publicItems: a failed or unmapped read is null, never empty groups", () => {
  assert.equal(publicItems(null), null)
  assert.equal(publicItems([]), null)
  assert.equal(publicItems([issue(424242, "OPEN", "status:open")]), null)
})

test("publicItems: every public label passes the public-safety check and none is a tracker title", () => {
  const all = Object.values(PUBLIC_ITEMS)
  assert.equal(new Set(all).size, all.length)
  assert.deepEqual(assertPublicSafe({ items: { open: all } }), [])
  assert.ok(assertPublicSafe({ items: { open: ["see src/lib/pulse.ts"] } }).length > 0)
  assert.ok(assertPublicSafe({ items: { title: ["x"] } }).length > 0)
})
