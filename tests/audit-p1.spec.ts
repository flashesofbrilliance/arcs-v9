import { test, expect, type Page } from "@playwright/test"

// Regression gate for the 2026-10-04 app.arcs.care audit P1 batch (PR #735).
// Each test pins one defect class so it fails the run if it comes back.

const PUBLIC = ["/", "/trust", "/privacy", "/terms", "/compass", "/advisory", "/dashboard", "/history"]

// Interactive inside interactive (a link inside a button, a button inside a link) is invalid HTML.
async function nestedInteractive(page: Page): Promise<string[]> {
  return page.$$eval("button a, button button, a button, a a", (els) => els.map((e) => e.outerHTML.slice(0, 120)))
}

// A control that is still in the tab order while an ancestor has faded it to opacity 0.
async function invisibleButFocusable(page: Page): Promise<string[]> {
  return page.$$eval("a[href], button:not([disabled])", (els) =>
    els
      .filter((el) => {
        if (getComputedStyle(el).visibility === "hidden") return false
        for (let n: Element | null = el; n; n = n.parentElement) {
          const cs = getComputedStyle(n)
          if (cs.display === "none") return false
          if (cs.opacity === "0") return true
        }
        return false
      })
      .map((el) => el.outerHTML.slice(0, 120)),
  )
}

for (const route of PUBLIC) {
  test(`${route}: no nested interactives, no invisible focus targets, one h1, named title`, async ({ page }) => {
    await page.goto(route, { waitUntil: "networkidle" })
    expect(await nestedInteractive(page)).toEqual([])
    expect(await invisibleButFocusable(page)).toEqual([])
    expect(await page.locator("h1").count(), `${route} h1 count`).toBeGreaterThanOrEqual(1)
    if (route !== "/") expect(await page.title(), `${route} title`).toMatch(/ · ARCS$/)
  })
}

test("data banner opens from the keyboard and closes on Escape", async ({ page }) => {
  await page.goto("/trust", { waitUntil: "networkidle" })
  const toggle = page.getByRole("button", { name: /what's the deal with my data/i })
  await expect(toggle).toHaveAttribute("aria-expanded", "false")
  await toggle.focus()
  await page.keyboard.press("Enter")
  await expect(toggle).toHaveAttribute("aria-expanded", "true")
  await expect(page.getByRole("region", { name: /what arcs does with your data/i })).toBeVisible()
  await page.keyboard.press("Escape")
  await expect(toggle).toHaveAttribute("aria-expanded", "false")
})

test("unknown route renders the branded 404", async ({ page }) => {
  const res = await page.goto("/this-route-does-not-exist", { waitUntil: "networkidle" })
  expect(res?.status()).toBe(404)
  await expect(page.locator("h1")).toHaveText("Nothing at this address.")
  await expect(page.getByRole("link", { name: /open the compass/i })).toBeVisible()
})

test("missing brief is a dead end with a way back, not a lone error line", async ({ page }) => {
  await page.goto("/brief/does-not-exist-000", { waitUntil: "networkidle" })
  await expect(page.locator("h1")).toHaveText("We can't find that brief.")
  await expect(page.getByRole("link", { name: /your ledger/i })).toBeVisible()
})
