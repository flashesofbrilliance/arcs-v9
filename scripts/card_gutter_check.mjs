#!/usr/bin/env node
// card_gutter_check.mjs — headless sibling of artifact_wrap_lint.py (Frustration Gate, AGENTS.md #13/#15).
// Fails when a text block (p, li, blockquote, ol, ul) inside a bordered card is more than
// GUTTER_PX narrower than the card's inner content width, at 360 / 790 / 1280: the dead right
// gutter that the static lint cannot see (an ol capped at max-width:var(--measure) in a full-width card).
// Excluded: single-line blocks (pills, labels, short items) and blocks whose parent is itself
// narrower than the card (grid/flex columns are the layout's choice, not a cap on the text).
// Usage: node scripts/card_gutter_check.mjs <file.html>...   |   --selftest (bad fixture must fail, good must pass)
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const WIDTHS = [360, 790, 1280]
const GUTTER_PX = 40

function loadPlaywright() {
  const roots = [process.cwd() + '/', process.env.PLAYWRIGHT_ROOT, '/Users/zharris/arcs-v9/'].filter(Boolean)
  for (const r of roots) {
    try { return createRequire(path.join(r, 'x.js'))('playwright') } catch {}
  }
  return null
}

// Runs in the page. Returns [{tag, text, cardInner, blockW, gutter}].
function inPage(gutterPx) {
  const out = []
  const borderW = (cs) => ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none')
  const cardOf = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) if (borderW(getComputedStyle(p))) return p
    return null
  }
  const lines = (el) => {
    const r = document.createRange(); r.selectNodeContents(el)
    return new Set([...r.getClientRects()].filter((q) => q.width > 0).map((q) => Math.round(q.top / 4))).size
  }
  const multi = (el) => /^(OL|UL)$/.test(el.tagName) ? [...el.querySelectorAll('li')].some((li) => lines(li) > 1) : lines(el) > 1
  for (const el of document.querySelectorAll('p,li,blockquote,ol,ul')) {
    const card = cardOf(el)
    if (!card || el.parentElement === null) continue
    const cs = getComputedStyle(card), cr = card.getBoundingClientRect()
    const innerRight = cr.right - parseFloat(cs.borderRightWidth) - parseFloat(cs.paddingRight)
    const parent = el.parentElement.getBoundingClientRect()
    if (parent.right < innerRight - 1) continue
    const gutter = innerRight - el.getBoundingClientRect().right
    if (gutter > gutterPx && multi(el))
      out.push({ tag: el.tagName.toLowerCase(), text: el.textContent.trim().replace(/\s+/g, ' ').slice(0, 50), cardInner: Math.round(innerRight - (cr.left + parseFloat(cs.borderLeftWidth) + parseFloat(cs.paddingLeft))), blockW: Math.round(el.getBoundingClientRect().width), gutter: Math.round(gutter) })
  }
  return out
}

async function check(files) {
  const pw = loadPlaywright()
  if (!pw) { console.error('card-gutter: playwright not resolvable (set PLAYWRIGHT_ROOT)'); return 2 }
  const browser = await pw.chromium.launch()
  let bad = 0
  for (const f of files) {
    const page = await browser.newPage()
    await page.goto(pathToFileURL(path.resolve(f)).href)
    const hits = []
    for (const w of WIDTHS) {
      await page.setViewportSize({ width: w, height: 900 })
      for (const h of await page.evaluate(inPage, GUTTER_PX)) hits.push({ w, ...h })
    }
    await page.close()
    if (!hits.length) { console.log(`✓ card-gutter: ${f} clean`); continue }
    bad += hits.length
    console.error(`✗ card-gutter: ${f} — ${hits.length} dead-gutter block(s)`)
    for (const h of hits) console.error(`    @${h.w}px <${h.tag}> "${h.text}" is ${h.blockW}px in a ${h.cardInner}px card (${h.gutter}px dead right gutter)`)
  }
  await browser.close()
  if (bad) console.error('  Fix: drop the per-block max-width so text fills the card; the card carries the measure (AGENTS.md #13).')
  return bad ? 1 : 0
}

const args = process.argv.slice(2)
if (args[0] === '--selftest') {
  const dir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'tests', 'fixtures', 'card-gutter')
  const origErr = console.error; console.error = () => {}
  const bad = await check([path.join(dir, 'bad.html')])
  const good = await check([path.join(dir, 'good.html')])
  console.error = origErr
  if (bad === 1 && good === 0) { console.log('✓ card-gutter selftest: bad fixture fails, good fixture passes'); process.exit(0) }
  console.error(`✗ card-gutter selftest broken: bad=${bad} (want 1) good=${good} (want 0)`); process.exit(1)
}
if (!args.length) { console.error('usage: card_gutter_check.mjs <file.html>... | --selftest'); process.exit(2) }
process.exit(await check(args))
