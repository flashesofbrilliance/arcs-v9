import { test, expect } from "@playwright/test"
import { execFileSync } from "node:child_process"
import { pathToFileURL } from "node:url"
import fs from "node:fs"
import path from "node:path"

// This environment ships a pinned Chromium whose version differs from the one @playwright/test
// would auto-download (blocked here). Point launch at the pre-installed binary when present;
// fall back to Playwright's bundled browser (CI has a matching one). Override with ALMANAC_CHROMIUM.
const PINNED = process.env.ALMANAC_CHROMIUM ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
if (fs.existsSync(PINNED)) test.use({ launchOptions: { executablePath: PINNED } })

// 1a gate — the 4-width visual check for the ALMANAC render (scripts/research_render.py).
//
// The Almanac is a self-contained, data-inline HTML artifact read over file:// — internal
// research, deliberately NOT a hosted route ("render LOCAL, keep local"). So this gate does
// not use SMOKE_BASE_URL; it renders the artifact fresh and loads it from disk.
//
// Two gates:
//  1. smoke        — the 1a features render: the `rendered … · graded …` provenance header
//                    (one honest stamp, not two contradictory "graded" ones), the three Reader
//                    altitudes, the per-slice freshness readout, and the Scan epoch axis.
//  2. responsive   — no horizontal overflow at four widths, on EACH altitude. The measure/wrap
//                    regression class lives at the intermediate widths the standard presets skip
//                    (790), and in the Scan charts (epoch axis × domain filter) that Skim never
//                    shows — so we switch altitude and re-check, not just load the default view.
//
// A full-page screenshot is captured per (altitude × width) into test-results/ as the visual
// record that closes the gate.

const ROOT = path.resolve(__dirname, "..")
const OUT = path.join(ROOT, "_ARTIFACTS/atlas/atlas-almanac.html")

const ALTITUDES = ["skim", "scan", "trenches"] as const
const WIDTHS = [
  { name: "mobile", width: 375, height: 812 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "narrow", width: 790, height: 900 },
  { name: "desktop", width: 1280, height: 900 },
]

// Render the Almanac fresh so the gate always tests current output, never a stale artifact.
test.beforeAll(() => {
  execFileSync("python3", ["scripts/research_render.py"], { cwd: ROOT, stdio: "pipe" })
})

const fileUrl = () => pathToFileURL(OUT).href

test("almanac renders the 1a features (header · altitudes · freshness · epoch axis)", async ({ page }) => {
  const errors: string[] = []
  page.on("pageerror", (e) => errors.push(e.message))
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()) })

  await page.goto(fileUrl(), { waitUntil: "load" })

  // One honest provenance stamp: rendered-date AND graded-date, plus the not-fresh count.
  const header = await page.locator("body").innerText()
  expect(header, "missing the `rendered … · graded …` provenance header").toMatch(/rendered\s+\d{4}-\d{2}-\d{2}\s*·\s*graded\s+\d{4}-\d{2}-\d{2}/)
  expect(header, "missing the slices-not-fresh readout").toMatch(/slices?\s+not\s+fresh/i)

  // The three Reader altitudes are all present and switchable.
  for (const alt of ALTITUDES) {
    await expect(page.locator(`[data-alt="${alt}"]`), `altitude control "${alt}" missing`).toHaveCount(1)
  }

  // Scan carries the epoch axis (per 1a) and the freshness matrix summary.
  await page.locator('[data-alt="scan"]').click()
  await expect(page.locator("#scan"), "Scan panel did not become visible").toBeVisible()
  const epochToggles = await page.locator('#scan [onclick^="toggleEpoch"]').count()
  expect(epochToggles, "Scan is missing the epoch axis (no epoch toggles)").toBeGreaterThan(0)
  await expect(page.locator("#scan .fresh").first(), "Scan freshness summary missing").toBeVisible()

  // Per-slice freshness readout renders (dated "graded …" stamp) on Trenches rows. Rows are
  // collapsed by default (depth on demand), so assert the stamps exist, not that they're visible.
  await page.locator('[data-alt="trenches"]').click()
  await expect(page.locator("#trenches")).toBeVisible()
  const stamps = await page.locator("#trenches .fs-g").count()
  expect(stamps, "per-slice freshness stamps missing on Trenches rows").toBeGreaterThan(0)

  expect(errors, `almanac threw console/page errors:\n${errors.join("\n")}`).toEqual([])
})

for (const alt of ALTITUDES) {
  for (const w of WIDTHS) {
    test(`no horizontal overflow @ ${alt} · ${w.name} (${w.width}px)`, async ({ page }) => {
      await page.setViewportSize({ width: w.width, height: w.height })
      await page.goto(fileUrl(), { waitUntil: "load" })
      await page.locator(`[data-alt="${alt}"]`).click()
      await expect(page.locator(`#${alt}`)).toBeVisible()
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(
        overflow,
        `almanac @ ${alt}/${w.name}: page scrolls horizontally by ${overflow}px (wrap/grid regression)`,
      ).toBeLessThanOrEqual(1)
      await page.screenshot({ path: `test-results/almanac-${alt}-${w.name}.png`, fullPage: true })
    })
  }
}
