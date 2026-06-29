import { test, expect } from "@playwright/test"

// FE smoke test for the /recoil-report skill's "run a /debug loop and smoke
// test with Playwright" step. Checks key routes load, render real content,
// and throw no console errors — not a full test suite, a pre-deploy gate.

const ROUTES = ["/", "/recoil", "/recoil/demo", "/dashboard", "/history"]

for (const route of ROUTES) {
  test(`${route} loads without console errors`, async ({ page }) => {
    const errors: string[] = []
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text())
    })
    page.on("pageerror", (err) => errors.push(err.message))

    const response = await page.goto(route, { waitUntil: "networkidle" })
    expect(response?.status(), `${route} responded with an error status`).toBeLessThan(400)

    const bodyText = await page.locator("body").innerText()
    expect(bodyText.trim().length, `${route} rendered an empty body`).toBeGreaterThan(0)

    expect(errors, `${route} threw console errors:\n${errors.join("\n")}`).toEqual([])
  })
}

test("/recoil/demo renders the dynamic Recoil Report sections", async ({ page }) => {
  await page.goto("/recoil/demo", { waitUntil: "networkidle" })
  await expect(page.getByText("Demo Call — Smoke Test Fixture")).toBeVisible()
  await expect(page.getByText("Recovery Protocol")).toBeVisible()
})

test("/recoil/nonexistent-report-id 404s cleanly", async ({ page }) => {
  const response = await page.goto("/recoil/nonexistent-report-id")
  expect(response?.status()).toBe(404)
})
