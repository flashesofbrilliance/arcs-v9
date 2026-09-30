import { test, expect } from "@playwright/test"
import { pathToFileURL } from "node:url"
import fs from "node:fs"
import path from "node:path"

// NFTT visual gate. Every post is a single static HTML file under public/ that clones a shared
// <style> block. Two regressions this catches:
//  1. class-drift: the body uses a class (e.g. `.topbar`) the page's own <style> never defines,
//     because the head was cloned from a sibling with a different masthead grammar. The page
//     renders as unstyled browser defaults and no overflow gate notices. (2026-09-29.)
//  2. wrap/overflow at the four widths, with a full-page screenshot per width as the visual record.
// Loads over file:// so it runs without a server. NFTT_ONLY=<slug> narrows to one post.

const PINNED = process.env.ALMANAC_CHROMIUM ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
if (fs.existsSync(PINNED)) test.use({ launchOptions: { executablePath: PINNED } })

const PUB = path.join(__dirname, "..", "public")
const ONLY = process.env.NFTT_ONLY
const POSTS = fs.readdirSync(PUB)
  .filter((f) => /^blog-nftt-.+\.html$/.test(f) && f !== "blog-nftt-index.html")
  .filter((f) => !ONLY || f === `blog-nftt-${ONLY}.html`)
const WIDTHS = [375, 790, 1024, 1280]
// Known debt (pre-existing, not a new regression): a class used with no rule. Remove an entry when fixed.
const KNOWN_UNSTYLED: Record<string, string[]> = { "blog-nftt-post-1-brief.html": ["arc-ladder"] }

function undefinedClasses(html: string): string[] {
  const css = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => m[1]).join("\n")
  const body = html.replace(/<style[^>]*>[\s\S]*?<\/style>/g, "").replace(/<script[\s\S]*?<\/script>/g, "")
  const used = new Set<string>()
  for (const m of body.matchAll(/class="([^"]+)"/g)) for (const c of m[1].split(/\s+/)) if (c) used.add(c)
  return [...used].filter((c) => !new RegExp(`\\.${c.replace(/[-]/g, "\\-")}(?![\\w-])`).test(css))
}

for (const file of POSTS) {
  const html = fs.readFileSync(path.join(PUB, file), "utf8")
  const url = pathToFileURL(path.join(PUB, file)).href

  test(`${file}: every body class is styled`, () => {
    expect(undefinedClasses(html).filter((c) => !(KNOWN_UNSTYLED[file] ?? []).includes(c)), "classes used in markup with no rule in the page's <style>").toEqual([])
  })

  for (const w of WIDTHS) {
    test(`${file}: no overflow + screenshot @${w}`, async ({ page }) => {
      await page.setViewportSize({ width: w, height: 900 })
      await page.goto(url)
      const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
      expect(over, "horizontal overflow px").toBeLessThanOrEqual(0)
      await page.screenshot({ path: `test-results/nftt/${file.replace(".html", "")}@${w}.png`, fullPage: true })
    })
  }
}
