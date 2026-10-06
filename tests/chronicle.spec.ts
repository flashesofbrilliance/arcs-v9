import { test, expect } from "@playwright/test"
import { execFileSync } from "node:child_process"
import { pathToFileURL } from "node:url"
import fs from "node:fs"
import path from "node:path"

// Same pinned-Chromium escape hatch as tests/almanac.spec.ts.
const PINNED = process.env.ALMANAC_CHROMIUM ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
if (fs.existsSync(PINNED)) test.use({ launchOptions: { executablePath: PINNED } })

// Gate for the CHRONICLE render (scripts/chronicle_render.py -> _ARTIFACTS/atlas/chronicle.html),
// Reading Room tenant #3. Loaded over file:// like the Almanac; the gated route only serves the
// committed file.
//
//  1. smoke       - five books in order, five fathom controls, every book carries a Shavasana,
//                   per-epoch counts render (the "scrub Apr to Sep with per-epoch health" gate).
//  2. fathoms     - one depth at a time: fathom N shows only layer N, in EVERY book, and each
//                   depth reads differently (distinct text), so switching is never a no-op.
//  3. responsive  - no horizontal overflow at four widths on EACH fathom, plus the lede spans
//                   the lane like its heading (AGENTS gotcha 13c).

const ROOT = path.resolve(__dirname, "..")
const OUT = path.join(ROOT, "_ARTIFACTS/atlas/chronicle.html")
const BOOKS = ["genesis", "exodus", "leviticus", "numbers", "deuteronomy"]
const FATHOMS = [1, 2, 3, 4, 5]
const WIDTHS = [
  { name: "mobile", width: 375, height: 812 },
  { name: "narrow", width: 790, height: 900 },
  { name: "tablet", width: 1024, height: 900 },
  { name: "desktop", width: 1280, height: 900 },
]

// Re-render fresh when the full history is present (the render reads every book boundary back to
// Day 0). CI checks out shallow, where 471d5739 does not exist: there the gate tests the committed
// render, whose freshness is the author's `chronicle_render.py --check` before commit.
test.beforeAll(() => {
  try {
    execFileSync("git", ["cat-file", "-e", "471d5739^{commit}"], { cwd: ROOT, stdio: "pipe" })
  } catch {
    return
  }
  execFileSync("python3", ["scripts/chronicle_render.py"], { cwd: ROOT, stdio: "pipe" })
})

const fileUrl = () => pathToFileURL(OUT).href

test("chronicle renders five books, five fathoms, a Shavasana per book, per-epoch counts", async ({ page }) => {
  const errors: string[] = []
  page.on("pageerror", (e) => errors.push(e.message))
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()) })
  await page.goto(fileUrl(), { waitUntil: "load" })

  const ids = await page.locator("article.book").evaluateAll((els) => els.map((e) => e.id))
  expect(ids).toEqual(BOOKS)
  await expect(page.locator("[data-fathom-btn]")).toHaveCount(5)
  await expect(page.locator("article.book .shav")).toHaveCount(5)

  // Per-epoch health: every book shows a numeric commit count, Apr to Sep in order.
  await page.locator('[data-fathom-btn="4"]').click()
  for (const id of BOOKS) {
    const dd = await page.locator(`#${id} .stats dd`).first().innerText()
    expect(Number(dd), `${id} commit count not numeric`).toBeGreaterThan(0)
  }
  const body = await page.locator("body").innerText()
  expect(body, "em-dash in visible copy").not.toContain("—")
  expect(errors, errors.join("\n")).toEqual([])
})

test("each fathom is its own view, in every book", async ({ page }) => {
  await page.goto(fileUrl(), { waitUntil: "load" })
  for (const id of BOOKS) {
    const seen = new Set<string>()
    for (const n of FATHOMS) {
      await page.locator(`[data-fathom-btn="${n}"]`).click()
      for (const d of FATHOMS) {
        const layer = page.locator(`#${id} .f[data-depth="${d}"]`)
        if (d === n) await expect(layer, `${id}: fathom ${n} should show depth ${d}`).toBeVisible()
        else await expect(layer, `${id}: fathom ${n} should hide depth ${d}`).toBeHidden()
      }
      seen.add(await page.locator(`#${id} .f[data-depth="${n}"]`).innerText())
    }
    expect(seen.size, `${id}: two fathoms render identical text`).toBe(FATHOMS.length)
  }
})

for (const n of FATHOMS) {
  for (const w of WIDTHS) {
    test(`no horizontal overflow @ fathom ${n} · ${w.name} (${w.width}px)`, async ({ page }) => {
      await page.setViewportSize({ width: w.width, height: w.height })
      await page.goto(fileUrl(), { waitUntil: "load" })
      await page.locator(`[data-fathom-btn="${n}"]`).click()
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `chronicle @ fathom ${n}/${w.name}: scrolls by ${overflow}px`).toBeLessThanOrEqual(1)
      // Lede spans the lane: its right edge within 24px of the h1's container edge.
      const gap = await page.evaluate(() => {
        const l = document.querySelector(".lede")!.getBoundingClientRect()
        const lane = document.querySelector(".wrap")!.getBoundingClientRect()
        const pad = parseFloat(getComputedStyle(document.querySelector(".wrap")!).paddingRight)
        return lane.right - pad - l.right
      })
      expect(gap, `lede is ${gap}px short of the lane`).toBeLessThanOrEqual(24)
      await page.screenshot({ path: `test-results/chronicle-f${n}-${w.name}.png`, fullPage: true })
    })
  }
}
