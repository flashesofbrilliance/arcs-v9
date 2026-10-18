#!/usr/bin/env node
// card_gutter_check.mjs — headless sibling of artifact_wrap_lint.py (Frustration Gate, AGENTS.md #13/#15).
// Fails when a text block (p, li, blockquote, ol, ul) inside a bordered card is more than
// GUTTER_PX narrower than the card's inner content width, at 360 / 790 / 1280: the dead right
// gutter that the static lint cannot see (an ol capped at max-width:var(--measure) in a full-width card).
// Excluded: single-line blocks (pills, labels, short items) and blocks whose parent is itself
// narrower than the card (grid/flex columns are the layout's choice, not a cap on the text).
// SECOND CHECK (2026-10-15, root cause of the raw-capture "narrow cards" miss): SIBLING EDGE. A card or text
// block in normal flow must end at the right edge its siblings reach.
// The first check's remedy ("the card carries the measure") shrinks a card to the measure; with a measure
// narrower than the lane that moves the dead right gutter up one level, between the card and the lane. No gate
// compared a card to its siblings. Flags a substantive flow block (bordered card or multi-line text) whose right
// edge is more than LANE_TOL_PX short of its widest sibling, at 790 and 1280. Skipped: children of grid/flex rows
// (the layout's choice), full-bleed siblings, centered blocks, inline and tiny blocks. Opt out deliberately with
// data-lane="narrow" (index pages: data-measure="index").
// Usage: node scripts/card_gutter_check.mjs <file.html>...   |   --selftest (bad fixture must fail, good must pass)
import { createRequire } from 'node:module'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const WIDTHS = [360, 790, 1280]
const GUTTER_PX = 40
const LANE_TOL_PX = 24
const LANE_WIDTHS = [790, 1280]

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

// Runs in the page. Returns [{tag, text, laneRight, right, short}]. SIBLING EDGE: among the flow blocks of one
// parent, a substantive block (bordered card or multi-line text) that ends more than `tol` short of its widest
// sibling is flagged. No lane is guessed, so centered .wrap containers, full-bleed bars, app shells and
// side-by-side columns are not mistaken for defects.
function laneInPage(tol) {
  const out = []
  const vw = document.documentElement.clientWidth
  const skipTag = /^(SCRIPT|STYLE|LINK|NOSCRIPT|TEMPLATE|SVG|CANVAS|BR|OPTION|SPAN|A|B|I|EM|STRONG|CODE|SMALL|BUTTON|SUMMARY|INPUT|LABEL|TD|TH|TR|THEAD|TBODY|CAPTION)$/i
  const borderW = (cs) => ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none')
  const sideBySide = (cs) => (/flex/.test(cs.display) && /^row/.test(cs.flexDirection)) || (/grid/.test(cs.display) && cs.gridTemplateColumns.trim().split(/\s+/).length > 1)
  const isFlowBlock = (el) => { const cs = getComputedStyle(el); return !skipTag.test(el.tagName) && /^(block|list-item|flow-root|table|flex|grid)$/.test(cs.display) && cs.position !== 'absolute' && cs.position !== 'fixed' && cs.position !== 'sticky' }
  const optedOut = (el) => !!el.closest('[data-lane="narrow"],[data-measure="index"]')
  const lines = (el) => { const r = document.createRange(); r.selectNodeContents(el); return new Set([...r.getClientRects()].filter((q) => q.width > 0).map((q) => Math.round(q.top / 4))).size }
  const substantive = (el) => borderW(getComputedStyle(el)) || lines(el) > 1
  const centered = (cs) => { const l = parseFloat(cs.marginLeft), r = parseFloat(cs.marginRight); return l > 8 && Math.abs(l - r) <= 8 }
  const visit = (parent) => {
    const pcs = getComputedStyle(parent)
    if (sideBySide(pcs)) return
    const blocks = [...parent.children].filter((c) => isFlowBlock(c) && c.getBoundingClientRect().width >= 160 && c.getBoundingClientRect().height >= 8)
    const edgeKids = blocks.filter((c) => c.getBoundingClientRect().width < vw - 2)
    if (edgeKids.length >= 2) {
      const R = Math.max(...edgeKids.map((c) => c.getBoundingClientRect().right))
      for (const c of edgeKids) {
        const r = c.getBoundingClientRect(), short = R - r.right, ccs = getComputedStyle(c)
        if (short > tol && !centered(ccs) && !optedOut(c) && substantive(c))
          out.push({ tag: c.tagName.toLowerCase() + (c.className && typeof c.className === 'string' ? '.' + c.className.split(' ')[0] : ''), text: c.textContent.trim().replace(/\s+/g, ' ').slice(0, 40), laneRight: Math.round(R), right: Math.round(r.right), short: Math.round(short) })
      }
    }
    for (const c of blocks) { if (!borderW(getComputedStyle(c)) && c.tagName !== 'DETAILS') visit(c) }
  }
  visit(document.querySelector('main') || document.body)
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
    const laneHits = []
    for (const w of LANE_WIDTHS) {
      await page.setViewportSize({ width: w, height: 900 })
      for (const h of await page.evaluate(laneInPage, LANE_TOL_PX)) laneHits.push({ w, ...h })
    }
    await page.close()
    if (laneHits.length) {
      bad += laneHits.length
      console.error(`✗ lane-edge: ${f} — ${laneHits.length} block(s) end short of their siblings`)
      for (const h of laneHits) console.error(`    @${h.w}px <${h.tag}> "${h.text}" ends at ${h.right}px, siblings reach ${h.laneRight}px (${h.short}px dead right gutter)`)
    }
    if (!hits.length) { if (!laneHits.length) console.log(`✓ card-gutter + lane-edge: ${f} clean`); continue }
    bad += hits.length
    console.error(`✗ card-gutter: ${f} — ${hits.length} dead-gutter block(s)`)
    for (const h of hits) console.error(`    @${h.w}px <${h.tag}> "${h.text}" is ${h.blockW}px in a ${h.cardInner}px card (${h.gutter}px dead right gutter)`)
  }
  await browser.close()
  if (bad) console.error('  Fix: drop the per-block max-width so text fills the card, AND keep every card on the lane edge (a card narrower than its lane siblings moves the gutter up a level). Pair a narrow measure with a second grid column, or opt out with data-lane="narrow" (AGENTS.md #13).')
  return bad ? 1 : 0
}

const args = process.argv.slice(2)
if (args[0] === '--selftest') {
  const dir = path.join(path.dirname(new URL(import.meta.url).pathname), '..', 'tests', 'fixtures', 'card-gutter')
  const origErr = console.error; console.error = () => {}
  const bad = await check([path.join(dir, 'bad.html')])
  const good = await check([path.join(dir, 'good.html')])
  console.error = origErr
  const badLane = await check([path.join(dir, 'bad-lane.html')])
  const goodLane = await check([path.join(dir, 'good-lane.html')])
  console.error = origErr
  if (bad === 1 && good === 0 && badLane === 1 && goodLane === 0) { console.log('✓ card-gutter selftest: bad fixtures fail, good fixtures pass (text-in-card and lane-edge)'); process.exit(0) }
  console.error(`✗ card-gutter selftest broken: bad=${bad} (want 1) good=${good} (want 0) badLane=${badLane} (want 1) goodLane=${goodLane} (want 0)`); process.exit(1)
}
if (!args.length) { console.error('usage: card_gutter_check.mjs <file.html>... | --selftest'); process.exit(2) }
process.exit(await check(args))
