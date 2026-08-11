import { test, expect } from "@playwright/test"

// arcs.care federated family — live E2E smoke + prospect-safety tripwire.
// Runs against absolute host URLs (the family spans subdomains, so no baseURL).
// Doubles as the manual "interactive sweep" and the CI drift-detector: a failure
// here on the deploy-verify workflow rolls the alias back and opens an Issue —
// that Issue is the receipt for a family drift/decay event (blight/neglect →
// dead link, leaked name, broken mount). Override host base with FAMILY_BASE
// (e.g. a preview) — defaults to production.

const H = (sub: string) => (process.env.FAMILY_BASE ?? "https://{sub}.arcs.care").replace("{sub}", sub)

const HUBS = [
  { url: H("playground") + "/", title: /Clair de Lune Playground/, spine: true },
  { url: H("monolith") + "/", title: /Three Heads/, spine: true },
]
const SUBPAGES = ["12d-orbital", "knowledge-lattice", "alexandria", "moire"].map((s) => ({
  url: H("playground") + "/" + s, title: /ARCS/, spine: false,
}))
const PAGES = [...HUBS, ...SUBPAGES]

// The tripwire, enforced in-browser: a prospect must never see these.
const NAME_LEAKS = /kleban|elsamadisi|rayan saleh|periscope|hotes|daniels|zensai|\byuri\b|\bahmed\b|skinner|trabulski|delaney|joe kim|louisville/i
const JARGON = /_ARTIFACTS|_STATE|_INBOX|_CANON|_DECISIONS|_PATTERNS|runtime\/specs|arcs_kinematics|forge_counterpart|schema\.prisma|data\.arcs-v9|performer-gauntlet/i

for (const p of PAGES) {
  test(`${p.url} — 200, no console errors, spine=${p.spine}`, async ({ page }) => {
    const errors: string[] = []
    page.on("console", (m) => { if (m.type() === "error" && !/status of 4\d\d/.test(m.text())) errors.push(m.text()) })
    page.on("pageerror", (e) => errors.push(e.message))

    const res = await page.goto(p.url, { waitUntil: "networkidle" })
    expect(res?.status(), `${p.url} status`).toBeLessThan(400)
    await expect(page).toHaveTitle(p.title)
    if (p.spine) await expect(page.locator("nav.arc-spine")).toBeVisible()
    expect(errors, `console errors:\n${errors.join("\n")}`).toEqual([])
  })

  test(`${p.url} — tripwire: no real names, dead claude.ai links, or insider jargon`, async ({ page }) => {
    await page.goto(p.url, { waitUntil: "networkidle" })
    const html = await page.content()
    expect(html, "real-name leak").not.toMatch(NAME_LEAKS)
    expect(html, "dead claude.ai/code link").not.toContain("claude.ai/code")
    expect(html, "insider jargon leak").not.toMatch(JARGON)
  })
}

test("playground spine links target the family subdomains (not claude.ai)", async ({ page }) => {
  await page.goto(H("playground") + "/", { waitUntil: "networkidle" })
  const hrefs = await page.locator("nav.arc-spine a").evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute("href")))
  expect(hrefs.some((h) => /forge\.arcs\.care/.test(h ?? ""))).toBeTruthy()
  expect(hrefs.some((h) => /monolith\.arcs\.care/.test(h ?? ""))).toBeTruthy()
  expect(hrefs.every((h) => !/claude\.ai/.test(h ?? ""))).toBeTruthy()
})

test("playground launch links route to the performer sub-pages", async ({ page }) => {
  await page.goto(H("playground") + "/", { waitUntil: "networkidle" })
  const hrefs = await page.locator("a.launch").evaluateAll((as) => as.map((a) => (a as HTMLAnchorElement).getAttribute("href")))
  expect(hrefs).toContain("/12d-orbital")
  expect(hrefs.length).toBe(4) // meta-audit head dropped for public
})

test("monolith — a head mounts and the Moiré filter toggles (the engine runs live)", async ({ page }) => {
  await page.goto(H("monolith") + "/", { waitUntil: "networkidle" })
  await page.locator('.marquee .mq[data-slug="orbital"]').click()
  await expect(page.locator('.stage iframe:not(.filterlay)')).toBeVisible()
  const filter = page.locator("#btn-moire")
  await filter.click()
  await expect(filter).toHaveAttribute("aria-pressed", "true")
  await expect(page.locator(".stage iframe.filterlay")).toBeAttached()
})
