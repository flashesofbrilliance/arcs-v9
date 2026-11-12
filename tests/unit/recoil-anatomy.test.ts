// The two recoil renders (React WarRoomReport, single-file HTML scripts/recoil_page.py) read one
// anatomy plan. This fails when the TypeScript plan and its Python twin differ on any committed
// six-tab SSOT, or when the TS fidelity table drifts from the schema's x-fidelity rule.
import { test } from "node:test"
import assert from "node:assert/strict"
import { execFileSync } from "node:child_process"
import fs from "node:fs"
import path from "node:path"
import os from "node:os"
import { anatomy, FIDELITY_BY_GRADE, FIDELITY_Y_OVERRIDE, gradeChip } from "../../src/document/recoil/anatomy.ts"

const DIR = path.join(process.cwd(), "runtime", "recoil", "generated")
const FIXTURES = ["2026-10-29-gasmi.json", "2026-09-14-schriner.json", "2026-07-23-warroom-sample.json", "2026-10-16-concourse.json"]

test("fidelity table matches the schema x-fidelity rule", () => {
  const schema = JSON.parse(fs.readFileSync("runtime/specs/recoil-ssot-v2.schema.json", "utf-8"))
  assert.deepEqual(FIDELITY_BY_GRADE, schema["x-fidelity"].by_grade)
  assert.deepEqual(FIDELITY_Y_OVERRIDE, schema["x-fidelity"].y_override)
})

test("not scored and grade D render grain with n, never red", () => {
  assert.deepEqual(gradeChip(undefined), { tone: "steel", label: "Not scored · n = 0" })
  assert.deepEqual(gradeChip({ letter: "D", basis: "x", n: 2 }), { tone: "steel", label: "Grade D · n = 2" })
})

for (const f of FIXTURES) {
  const file = path.join(DIR, f)
  if (!fs.existsSync(file)) continue
  test(`TS and Python plans agree: ${f}`, () => {
    const py = JSON.parse(execFileSync("python3", ["scripts/recoil_page.py", file, "--plan"], { encoding: "utf-8" }))
    const ts = anatomy(JSON.parse(fs.readFileSync(file, "utf-8")))
    assert.deepEqual(JSON.parse(JSON.stringify(ts)), py)
    assert.ok(ts.glance.length <= 5 && ts.glance[0].key === "Next move")
  })
}

test("TS and Python plans agree on a v2 record with verbs, grades and PARADOX", () => {
  const g = (letter: string, n?: number) => ({ letter, basis: "test", ...(n == null ? {} : { n }) })
  const pass = (v: string, letter: string) => ({ verdict: `${v} verdict. Second sentence.`, cites: ["a1"], grade: g(letter, 2) })
  const doc = {
    schema: "arcs.recoil.ssot.v2",
    meta: { report_id: "t-v2", date: "2026-11-12", counterpart: "Pat" },
    opportunity: { y_state: "PARADOX", nci_prior: null, nci_post: null },
    beliefs: [{ id: "P1", claim: "c", inference: "OBS", confidence: [null, 0.4], conviction: "LOW", verdict: "v", grade: g("A") }],
    next_steps: [{ owner: "Pat", text: "Call back." }],
    call: { atoms: [] },
    verbs: Object.fromEntries(["analyze", "assess", "evaluate", "synthesize", "recapitulate"].map((v, i) => [v, pass(v, "ABCDE"[i])])),
    page: { header: { title: "T" }, tabs: [{ id: "x", label: "Extra" }], blocks: [{ type: "prose", tab: "x", p: ["Hello there."] }] },
  }
  const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "anat-")), "t-v2.json")
  fs.writeFileSync(file, JSON.stringify(doc))
  const py = JSON.parse(execFileSync("python3", ["scripts/recoil_page.py", file, "--plan"], { encoding: "utf-8" }))
  const ts = anatomy(doc)
  assert.deepEqual(JSON.parse(JSON.stringify(ts)), py)
  assert.equal(ts.header.chips[0].tone, "magenta")
  assert.ok(ts.header.nciGrain)
  assert.deepEqual(ts.groups.find((x) => x.name === "Evidence")!.folds.map((f) => f.chip.tone), ["green", "green", "gold", "steel", "steel"])
})
