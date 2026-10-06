import { test, expect, type Page } from "@playwright/test"

// status.arcs.care live wiring (2026-10-06). The repo is private, so the page must never call
// api.github.com, and a failed or partial /api/pulse read must keep the static floor (with a
// "degraded" tag), never paint a false zero. The pulse endpoint is stubbed in every test.

const PULSE = "https://app.arcs.care/api/pulse"

async function open(page: Page, body: unknown, status = 200) {
  const github: string[] = []
  page.on("request", (r) => { if (r.url().includes("api.github.com")) github.push(r.url()) })
  await page.route(PULSE, (route) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) }))
  await page.goto("/status.html")
  await page.waitForLoadState("networkidle")
  return github
}

test("pulse down: floor stays, every section tagged degraded, no GitHub calls", async ({ page }) => {
  const github = await open(page, { error: "boom" }, 500)
  expect(github).toEqual([])
  await expect(page.locator("#su-lead-ship")).not.toHaveText("0")
  await expect(page.locator("#su-lead-total")).not.toHaveText("0")
  for (const id of ["dg-pulse", "dg-su", "dg-risk", "dg-tempo", "dg-gates"]) {
    await expect(page.locator(`#${id}`)).toHaveClass(/\bon\b/)
  }
  await expect(page.locator('[data-g="goal"]').first()).not.toHaveText("0")
})

test("partial payload: null sections keep the floor; live sections paint", async ({ page }) => {
  const floorShip = await (async () => { await open(page, { ok: false }); return page.locator("#su-lead-ship").textContent() })()
  await page.unrouteAll()
  await open(page, {
    ok: true, updated: new Date().toISOString(),
    commit: { sha: "abc1234", date: new Date().toISOString() }, commitsTotal: 4000, prsOpen: 7,
    deploy: { state: "success", date: new Date().toISOString() },
    debt: null, risks: null, tempo: [{ week: "2026-10-05", merges: 0 }], gates: null, evals: null,
    degraded: ["debt", "risks", "tempo", "gates"],
  })
  await expect(page.locator("#pl-prs")).toHaveText("7")
  await expect(page.locator("#sv-commits")).toHaveText("4,000")
  await expect(page.locator("#dg-pulse")).not.toHaveClass(/\bon\b/)
  await expect(page.locator("#su-lead-ship")).toHaveText(floorShip ?? "")
  await expect(page.locator("#dg-su")).toHaveClass(/\bon\b/)
  await expect(page.locator("#dg-tempo")).toHaveClass(/\bon\b/) // all-zero tempo is not drawn
})

test("full payload paints counts, risks, gates", async ({ page }) => {
  await open(page, {
    ok: true, updated: new Date().toISOString(),
    commit: { sha: "abc1234", date: new Date().toISOString() }, commitsTotal: 4000, prsOpen: 7,
    deploy: { state: "success", date: new Date().toISOString() },
    debt: { total: 60, open: 40, done: 20, byStatus: { open: 6, "in-progress": 10, decision: 24, done: 20 }, bySev: { P1: 1, P2: 10, P3: 29 } },
    risks: { "spend-cap": { sev: "P1", status: "done" } },
    tempo: [{ week: "2026-09-28", merges: 3 }, { week: "2026-10-05", merges: 9 }],
    gates: { receipts: 300, calibration: { n: 4, gate: 30, cohort: "external" }, goalMap: { n: 22, gate: 100 } },
    evals: null, degraded: [],
  })
  await expect(page.locator("#su-lead-ship")).toHaveText("20")
  await expect(page.locator("#su-lead-total")).toHaveText("60")
  await expect(page.locator('tr[data-risk="spend-cap"] [data-r="status"]')).toHaveText("RESOLVED")
  await expect(page.locator('[data-g="cal"]').first()).toHaveText("4")
  await expect(page.locator('[data-g="goal"]').first()).toHaveText("22")
  await expect(page.locator("#tempo-live .cad-col")).toHaveCount(2)
  for (const id of ["dg-su", "dg-risk", "dg-tempo", "dg-gates"]) {
    await expect(page.locator(`#${id}`)).not.toHaveClass(/\bon\b/)
  }
})
