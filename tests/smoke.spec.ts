import { test, expect } from "@playwright/test"

// FE smoke test for the /recoil-report skill's "run a /debug loop and smoke
// test with Playwright" step. Checks key routes load, render real content,
// and throw no console errors — not a full test suite, a pre-deploy gate.

const ROUTES = ["/", "/recoil", "/recoil/demo", "/dashboard", "/history"]

for (const route of ROUTES) {
  test(`${route} loads without console errors`, async ({ page }) => {
    const errors: string[] = []
    page.on("console", (msg) => {
      // Chrome auto-logs every 4xx subresource as a console error. Auth-gated
      // probes (e.g. /api/history 401 for anonymous visitors, which the client
      // handles by showing the sign-in prompt) are expected behavior, not
      // regressions — only 5xx and real page errors fail the gate.
      if (msg.type() === "error" && !/status of 4\d\d/.test(msg.text())) errors.push(msg.text())
    })
    page.on("pageerror", (err) => errors.push(err.message))

    const response = await page.goto(route, { waitUntil: "networkidle" })
    expect(response?.status(), `${route} responded with an error status`).toBeLessThan(400)

    const bodyText = await page.locator("body").innerText()
    expect(bodyText.trim().length, `${route} rendered an empty body`).toBeGreaterThan(0)

    expect(errors, `${route} threw console errors:\n${errors.join("\n")}`).toEqual([])
  })
}

// Recoil reports sit behind the Auth.js sign-in gate (the shared-password
// /recoil/unlock gate was retired): a signed-out visit to any /recoil/[id],
// existing or not, redirects to /compass?next=/recoil/<id>. Deliberately
// identical for both so the gate doesn't leak which report ids exist.
test("/recoil/demo redirects to the sign-in gate", async ({ page }) => {
  await page.goto("/recoil/demo", { waitUntil: "networkidle" })
  await expect(page).toHaveURL(/\/compass\?next=\/recoil\//)
})

test("/recoil/nonexistent-report-id gates identically (no id-existence leak)", async ({ page }) => {
  await page.goto("/recoil/nonexistent-report-id", { waitUntil: "networkidle" })
  await expect(page).toHaveURL(/\/compass\?next=\/recoil\//)
})
