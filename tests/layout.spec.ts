import { test, expect } from "@playwright/test"

// Layout smoke test — catches overflow/wrap regressions that the console-error
// smoke check can't see (e.g. buttons overflowing the viewport on narrow
// widths). Runs under both the "desktop" and "mobile-portrait" projects.
test("home tributary buttons stay within the viewport", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" })

  const buttons = page.locator("text=Where to navigate next").locator("xpath=ancestor::div[1]/following-sibling::div[1]//button")
  const count = await buttons.count()
  if (count === 0) test.skip(true, "no tributaries rendered for this fixture")

  const viewportWidth = page.viewportSize()?.width ?? 0
  for (let i = 0; i < count; i++) {
    const box = await buttons.nth(i).boundingBox()
    if (!box) continue
    expect(box.x + box.width, `button ${i} overflows viewport width ${viewportWidth}`).toBeLessThanOrEqual(viewportWidth)
  }
})
