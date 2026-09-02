import { test, expect } from "@playwright/test"

// E2E gate for the blacksmith.arcs.care application bundle (the founder-facing
// pitch, the /observatory director's cut, and the /resume). Runs against the
// live host by default; override with BLACKSMITH_BASE_URL to test a preview.
//
// Three gates in one spec:
//  1. smoke      - 200, real content, key strings, no console/page errors
//  2. air-gap    - the constitutional boundary as a test: the public pages
//                  must NEVER leak the recruiter or the founders' names
//  3. responsive - no horizontal overflow at four widths (the measure/wrap
//                  regression class lives at the intermediate widths presets skip)

const BASE = process.env.BLACKSMITH_BASE_URL ?? "https://blacksmith.arcs.care"

const PAGES = [
  { path: "/", title: /Zach Harris/, must: ["Staff Product Engineer", "a developer I already am", "The seam I sit on", "The kitchen"] },
  { path: "/observatory", title: /Director's Cut/, must: ["Director's Cut", "honest, agentic pipeline", "Replay the build", "what is not on this page"] },
]

// The résumé is delivered as a downloadable PDF, not a responsive HTML page.
test("/blacksmith-resume.pdf is served for download", async ({ request }) => {
  const res = await request.get((process.env.BLACKSMITH_BASE_URL ?? "https://blacksmith.arcs.care") + "/blacksmith-resume.pdf")
  expect(res.status(), "resume PDF not reachable").toBeLessThan(400)
  expect((res.headers()["content-type"] || ""), "resume is not served as a PDF").toContain("pdf")
})

// Air-gap trip-words that must not appear anywhere in the public HTML.
const FORBIDDEN = ["Amy", "Szymarek", "Recruit Haus", "Paraform", "Jayaprakash", "Aayush", "reverse-listen", "resonance model"]

const WIDTHS = [
  { name: "mobile", width: 375, height: 812 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "narrow", width: 790, height: 900 },
  { name: "desktop", width: 1280, height: 900 },
]

for (const p of PAGES) {
  test(`${p.path} smoke + content + air-gap`, async ({ page }) => {
    const errors: string[] = []
    // 4xx subresource logs are Chrome noise (e.g. an auth-gated probe); only
    // 5xx and real page errors fail the gate.
    page.on("console", (m) => { if (m.type() === "error" && !/status of 4\d\d/.test(m.text())) errors.push(m.text()) })
    page.on("pageerror", (e) => errors.push(e.message))

    const res = await page.goto(BASE + p.path, { waitUntil: "networkidle" })
    expect(res?.status(), `${p.path} responded with an error status`).toBeLessThan(400)
    await expect(page).toHaveTitle(p.title)

    const body = await page.locator("body").innerText()
    expect(body.trim().length, `${p.path} rendered an empty body`).toBeGreaterThan(0)
    for (const s of p.must) expect(body, `${p.path} missing expected copy: "${s}"`).toContain(s)

    // Constitutional air-gap: no recruiter / founder / persuasion-layer leaks.
    const html = await page.content()
    for (const w of FORBIDDEN) expect(html, `${p.path} AIR-GAP LEAK: found "${w}"`).not.toContain(w)

    // House rule: no em-dashes on hiring-facing surfaces.
    expect(body, `${p.path} contains an em-dash`).not.toContain("—")

    expect(errors, `${p.path} threw console errors:\n${errors.join("\n")}`).toEqual([])
  })

  for (const w of WIDTHS) {
    test(`${p.path} no horizontal overflow @ ${w.name} (${w.width}px)`, async ({ page }) => {
      await page.setViewportSize({ width: w.width, height: w.height })
      await page.goto(BASE + p.path, { waitUntil: "networkidle" })
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `${p.path} @ ${w.name}: page scrolls horizontally by ${overflow}px (wrap/grid regression)`).toBeLessThanOrEqual(1)
      await page.screenshot({ path: `test-results/blacksmith${(p.path.replace(/\//g, "_") || "_home")}-${w.name}.png`, fullPage: true })
    })
  }
}
