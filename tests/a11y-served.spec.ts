import { test, expect } from "@playwright/test"
import AxeBuilder from "@axe-core/playwright"
import { pathToFileURL } from "node:url"
import fs from "node:fs"
import path from "node:path"

// WCAG ratchet for every static page surfaces.arcs.care serves (axe-core, WCAG 2.0/2.1/2.2 A and AA).
// Done goal (2026-10-08): every served page clean except reasoned exemptions. This spec measures the
// WCAG half; scripts/design_debt_sweep.py measures the design half. Each page's violation count may only
// go DOWN against runtime/specs/a11y-baseline.json. Re-baseline after a fix lands:
//   UPDATE_A11Y_BASELINE=1 npx playwright test tests/a11y-served.spec.ts
// Pages load by file URL (no server), so third-party fonts and absolute assets may not load; contrast is
// computed against the page's own CSS, which is what the rule is about.

const ROOT = path.resolve(__dirname, "..")
const CATALOG = path.join(ROOT, "runtime/specs/surface-catalog.json")
const BASELINE = path.join(ROOT, "runtime/specs/a11y-baseline.json")
const UPDATE = process.env.UPDATE_A11Y_BASELINE === "1"
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]

const rows: { file?: string | null }[] = JSON.parse(fs.readFileSync(CATALOG, "utf8")).rows
const pages = [...new Set(rows.map((r) => r.file).filter((f): f is string => !!f && f.endsWith(".html") && fs.existsSync(path.join(ROOT, f))))].sort()
const baseline: Record<string, { violations: number; nodes: number; rules: Record<string, number> }> =
  fs.existsSync(BASELINE) ? JSON.parse(fs.readFileSync(BASELINE, "utf8")).pages : {}
const fresh: typeof baseline = {}

test.describe.configure({ mode: "serial" })

for (const file of pages) {
  test(`a11y ratchet: ${file}`, async ({ page }) => {
    await page.goto(pathToFileURL(path.join(ROOT, file)).href, { waitUntil: "load" })
    const r = await new AxeBuilder({ page }).withTags(TAGS).analyze()
    const rules: Record<string, number> = {}
    for (const v of r.violations) rules[v.id] = v.nodes.length
    const nodes = Object.values(rules).reduce((a, b) => a + b, 0)
    fresh[file] = { violations: r.violations.length, nodes, rules }
    if (UPDATE) return
    const was = baseline[file]
    if (!was) return // a page added to the catalog after the baseline: recorded on the next update
    expect(nodes, `${file}: WCAG violation nodes rose ${was.nodes} -> ${nodes} (${Object.keys(rules).join(", ")})`).toBeLessThanOrEqual(was.nodes)
  })
}

test.afterAll(() => {
  if (!UPDATE) return
  const totals = Object.values(fresh).reduce((t, p) => ({ violations: t.violations + p.violations, nodes: t.nodes + p.nodes, clean: t.clean + (p.nodes ? 0 : 1) }), { violations: 0, nodes: 0, clean: 0 })
  fs.writeFileSync(BASELINE, JSON.stringify({ version: "0.1.0", tags: TAGS, totals: { ...totals, pages: Object.keys(fresh).length }, pages: fresh }, null, 1) + "\n")
})
