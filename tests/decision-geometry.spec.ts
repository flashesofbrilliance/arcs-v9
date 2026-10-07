import { test, expect } from "@playwright/test"

// Smoke gate for the decision-geometry explorer and its feed.
//  1. feed     - GET /api/geometry answers JSON with the fidelity field and, in dev
//                (admin passthrough) or when GEOMETRY_PUBLIC is on, a receipts array;
//                the public shape must be text-free and id-free.
//  2. page     - the explorer renders, binds its controls, and either ingests the feed
//                (phase badge leaves LOADING) or shows the honest "No feed" banner.
//                It must never draw a fake corpus.
//  3. responsive - no horizontal overflow at four widths (the intermediate band included).
// Runs against SMOKE_BASE_URL (default http://localhost:3000, see playwright.config.ts).

test("GET /api/geometry answers with a fidelity and a well-formed shape", async ({ request }) => {
  const res = await request.get("/api/geometry")
  expect([200, 401, 503]).toContain(res.status())
  if (res.status() === 401) return // GEOMETRY_PUBLIC=false and no session: the honest refusal
  if (res.status() === 503) { expect((await res.json()).error).toBe("feed unavailable"); return } // no reachable database (CI): honest, with a code
  const body = await res.json()
  expect(["admin", "owner", "public"]).toContain(body.fidelity)
  expect(Array.isArray(body.receipts)).toBeTruthy()
  for (const r of body.receipts.slice(0, 20)) {
    expect(typeof r.i).toBe("number")
    expect(typeof r.d).toBe("number")
    expect(r.geo).toBeTruthy()
    if (body.fidelity === "public") {
      // text-free and id-free by contract
      expect(r.q).toBeUndefined(); expect(r.tn).toBeUndefined(); expect(r.ent).toBeUndefined(); expect(r.id).toBeUndefined()
      expect(typeof r.s).toBe("number")
      expect(r.t).toHaveLength(10)
      if (r.geo.kairos) expect(r.geo.kairos.txt).toBeNull()
    }
  }
})

test("/pf-decision-geometry.html renders and never fakes a corpus", async ({ page }) => {
  const errors: string[] = []
  page.on("pageerror", (e) => errors.push(String(e)))
  await page.goto("/pf-decision-geometry.html")
  await expect(page.locator("#stage canvas")).toBeVisible()
  await expect(page.locator("#zoom")).toBeVisible()
  await expect(page.locator("#clar")).toBeVisible()
  // the phase badge leaves LOADING either way: a real feed, or the honest NO FEED state
  await expect(page.locator("#phase")).not.toHaveText("LOADING", { timeout: 20000 })
  const phase = await page.locator("#phase").textContent()
  const stats = await page.locator("#stats").textContent()
  if (phase === "NO FEED") {
    await expect(page.locator("#banner")).toContainText("No feed")
  } else {
    expect(stats).toMatch(/receipts <?b?>?\d+/)
    expect(stats).toContain("corpus tier")
  }
  // the 720 protocol modal opens and carries the ladder
  await page.locator("#proto-btn").click()
  await expect(page.locator("#modal")).toHaveClass(/open/)
  await expect(page.locator("#modal")).toContainText("Diamond rule")
  await page.keyboard.press("Escape")
  await expect(page.locator("#modal")).not.toHaveClass(/open/)
  // morph cycles the projection label
  await page.locator("#morph").click()
  await expect(page.locator("#morph")).toContainText("B")
  expect(errors, "page errors: " + errors.join(" | ")).toHaveLength(0)
})

for (const width of [375, 790, 1024, 1440]) {
  test(`no horizontal overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 })
    await page.goto("/pf-decision-geometry.html")
    await page.waitForTimeout(800)
    const over = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
    expect(over, `document overflows by ${over}px at ${width}px`).toBeLessThanOrEqual(0)
  })
}

test("playground lists the explorer", async ({ page }) => {
  await page.goto("/playground.html")
  await expect(page.locator('a.launch[href="/decision-geometry"]')).toBeVisible()
})
