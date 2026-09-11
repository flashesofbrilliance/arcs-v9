# Reading Room 1a — 4-width visual gate findings

**Verdict: PASS.** All three altitudes (Skim / Scan / The Trenches) hold at 1280, 790, 768, and
375 px. Zero horizontal page overflow in all 12 (width × altitude) combinations. Per-row export
round-trips a self-contained bundle. Freshness badge, two-shelf Skim, and dataviz palette all
render correctly.

- Session: 1a Reader (worktree `priceless-hopper-fbdd55`), fork base `229b9e8b`.
- Method: Playwright/Chromium headless (repo-root `node_modules`), `file://` load, click altitude
  toggle, `documentElement.scrollWidth - clientWidth` overflow probe + full-page screenshot per combo.
- Artifact: `_ARTIFACTS/atlas/atlas-almanac.html` (264 nodes), freshly rendered via
  `python3 scripts/research_render.py`.

## Overflow probe (scrollW − clientW), all 0 px

| Altitude | 1280 | 790 | 768 | 375 |
|----------|------|-----|-----|-----|
| Skim     | 0    | 0   | 0   | 0   |
| Scan     | 0    | 0   | 0   | 0   |
| Trenches | 0    | 0   | 0   | 0   |

## Export round-trip (Trenches ↓ button)

`button.exp` renders only in Trenches (`renderTrenches()`, `research_render.py:372`) — not in Skim
(correct; Skim is the two-shelf overview). Clicking the first `.exp` fired a download:

- `almanac-blacksmith-application-bundle.html`, 3180 bytes
- self-contained: **true** (no external `http` `src`/`link` refs)
- valid HTML document: true

## Eyeball pass

- **Two-shelf Skim** (FOUNDATIONAL / LOAD-BEARING): renders correctly at all widths; ranking + eyebrows legible.
- **Freshness badge**: header line "rendered 2026-09-07 · graded 2026-09-04 · 20 slices not fresh" renders at every width.
- **Freshness-by-slice table** (`.fresh`): epoch × domain matrix with dated per-slice stamps + `dirty N`, legible.
- **Dataviz palette**: Live (green) / Drifted (gold) / Stale (grey) / Unverified (dim) — distinguishable and AA-legible on `#020408` at all widths, in both the stacked bars and the legend.
- **Epoch axis** (Scan): NODES BY EPOCH × STATUS, 2026-04…2026-09 + undated, no label collision.
- **~790 wrap band**: no measure/wrap regression; prose measure holds, no split emphasis, no mono overflow.

## Minor, non-blocking (optional polish for 1b — do NOT block the gate)

1. **375 px — long unbroken token wraps the trailing epoch label.** In Trenches, a node title
   containing a long token (e.g. `RECRUITHAUS_AMMO_PASSWORD`) pushes the inline epoch stamp to wrap
   as "202 / 09". Stays inside the card (page overflow 0); purely cosmetic.
   - Selector: `.node` title row (Trenches card header), width 375.
   - Proposed fix: `overflow-wrap:anywhere` on the title span, or move the epoch stamp to its own line under the title at narrow widths.

2. **375 px — freshness table shows 2 of 4 columns; rest reachable only by in-container scroll.**
   `.fresh{overflow-x:auto}` (`research_render.py:177`) is correct per WORLD.md (wide tables scroll
   in their own container; body never scrolls — confirmed, overflow 0). A mobile reader may not
   discover the horizontal scroll.
   - Selector: `.fresh`, width 375.
   - Proposed fix (optional): a subtle right-edge scroll affordance/gradient, or a "scroll →" hint. Not required.

Neither item blocks Phase 1a closure.

## Scope caveat (peer-review noted)

This is a **static single-state** gate: it screenshots the default filter at each altitude and
exercises one export click. It does **not** click-through the interactive bar filters
("CLICK A BAR TO FILTER") or assert overflow under a *filtered* row set. Fine for a visual-overflow
+ layout gate; "PASS" should not be read as interaction-tested. Optional belt-and-suspenders for a
later pass: assert `body.scrollWidth <= width` under each filtered state too, so a future
filter-induced wide row can't slip the static probe.
