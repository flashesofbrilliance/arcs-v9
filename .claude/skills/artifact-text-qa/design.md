# design.md — rules for text-bearing web artifacts

The standing rules for any website / landing page / dashboard / visual with text. The
companion `SKILL.md` explains how to satisfy them; the two `*-test.mjs` harnesses prove them.
**Definition of done = both tests PASS.** Author to these rules, then verify — never eyeball alone.

## R1 — No overflow, no clipped text (the recurring regression; check this every time)
At every viewport width (360 → 1440) and on every tab/view: the page never scrolls
horizontally, no element (outside an intentional horizontal scroller) crosses the viewport
edge, and no text is clipped by its box or by an `overflow:hidden` ancestor (rounded "sheet"
wrappers are the usual silent clipper).
Root causes to fix, not nudge: grid/flex children need `min-width:0`; long tokens need
`overflow-wrap:anywhere`; `nowrap` labels in a flex row need `min-width:0` + ellipsis + a
shrinkable sibling + a smaller mobile font.
**Run:** `node overflow-test.mjs page.html`

## R1b — Break points are design (the OTHER half of "the wrapping bug")
Overflow tests pass and the complaint persists? Look at WHERE lines break, not whether they fit.
A highlighted/accent clause that wraps mid-phrase ("backed / by real data") reads as broken even
though geometry is clean — no automated sweep catches it. Rule: an accent/highlighted clause owns
its lines. Give it explicit `<br class="br">` at clause boundaries (hide `.br` under ~700px),
set `text-wrap: pretty` on p/li/blockquote globally, and VERIFY BY READING the rendered line
breaks at desktop and mobile widths. This is the zachharris.xyz lesson: three green test runs
"proved" a bug fixed that was an ugly break point all along.
Same pathology in BOLD: a long <b> span that wraps leaves a bold fragment opening the next
line, which reads as a rendering error. Bold compact anchors (a number, a name, a short
sentence), never a whole clause; verify with getClientRects().length === 1 at desktop measure.

## R2 — No em-dashes
A space-padded em-dash lands at a line break and reads as a broken wrap (this is what "the
wrapping bug" usually is), and it violates the plain-language rule. Use commas, periods, or
plain phrasing. The overflow test fails the build if any `—` is present in rendered text.

## R3 — WCAG 2.1 AA (axe must be clean across every view)
Contrast ≥4.5:1 body/labels (≥3:1 large) — compute it; reserve bright accent for large/fills,
deep tint for small text and white-on-color buttons; tint secondary text on colored surfaces
from the hue, never flat gray. Set `document.documentElement.lang`. One `<header>`/`<main>`/
`<footer>` + `<nav>`, a skip link, a real `<h1>→<h2>→<h3>` outline (never styled-div headings),
the full WAI-ARIA tabs pattern with keyboard support, visible focus, `prefers-reduced-motion`,
and alt/`role="img"`/`aria-hidden` as appropriate.
**Run:** `node axe-test.mjs page.html`

## R4 — Semantic HTML5 + robust JS
Buttons for actions, `<a>` for links, `rel="noopener"` on `target="_blank"`. Guard
`history`/`localStorage` in try/catch. Prefer inline SVG over layout-timing-dependent canvas
(a canvas that inits at zero width never paints); if canvas is required, self-heal via
per-frame re-measure + `ResizeObserver`.

## R5 — Anti-slop (premium by construction)
- Avoid the AI-default faces: Inter, Roboto, Space Grotesk, Geist, Plus Jakarta Sans, Fraunces.
  Choose a distinctive display + clean body pairing; reserve monospace for real data/measurement,
  not as a "technical" costume.
- These are category defaults, not bans — the brief can earn any, but reaching for one on a free
  axis means you stopped deciding: a tracked uppercase eyebrow over *every* section; 01/02/03
  numbering with no real sequence; same-size icon+heading+text cards as the whole page structure;
  the hero big-number/stat template; gradient text (emphasis is weight/size); glass & blur as
  decoration; a colored `border-left`/`right` > 1px; zero-offset colored halos as "depth."
- Information hierarchy is stacked most-relevant → least-relevant. On a services/offer page that
  is usually: what I do → how it works → what it costs → supporting detail/deliverable. Read the
  stack top-to-bottom and ask "is each block more decision-relevant than the one below it?"

## R5b — Artifact-frame survival rules (claude.ai published artifacts)
The published artifact runs in a cross-origin iframe with its own lifecycle. Hard-won facts:
- The shell reveals the page only after an init handshake that can take 10-16s (worse with many
  comment threads). Nothing you author fixes that; don't chase it as a page bug.
- A body-level Google-Fonts `<link rel=stylesheet>` render-blocks the WHOLE page (artifacts have
  no author head). Always load it async: `media="print" onload="this.media='all'"` + noscript.
- Inline scripts may run late or unreliably in the frame. CORE FUNCTION MUST NOT NEED JS:
  tab/panel switching = hidden radio inputs + labels (pure CSS), JS only as hash-sync
  enhancement. Prove it with a `javaScriptEnabled:false` Playwright run.
- Synthetic input from browser-extension automation (CDP) does NOT route into the artifact's
  OOPIF — clicks and scrolls silently hit the shell. You cannot prove or disprove in-frame
  interactivity that way; test interactivity headless against the file, or by hand.

## R5c — Responsive media sizes in fixed cells, and touch targets clear 44px
Two mobile/tablet regressions the overflow gate does NOT catch, both proven on zachharris.xyz:
- **Images that resize per viewport.** A logo/image row built with `flex-wrap` + `justify-content:space-between`
  lets wide items width-clamp at narrow widths, shrinking their height non-uniformly so the "same" logo is a
  different size at each breakpoint. Fix: a fixed `grid-template-columns:repeat(N,1fr)` (step N down at breakpoints,
  e.g. 6/3/2), each image `height:<fixed>;width:auto;max-width:100%;object-fit:contain;justify-self:center`. PROVE it
  by measuring `getBoundingClientRect().height` of every image across a width sweep — the numbers must be identical
  at every width (tune per-logo heights for optical balance, then re-measure).
- **Sub-44px interactive controls.** Nav CTAs, chips, wrapped tab labels, and secondary buttons routinely compute
  to ~35-43px. Give real controls `display:inline-flex;align-items:center;min-height:44px` and enough padding.
  Measure the rendered heights at 390px; primary conversion controls especially must clear 44px.

## R6 — Verify, then ship
The two harnesses are the gate. A green overflow test + a green axe test is the minimum bar to
publish or hand off a text artifact. If you changed fonts, colors, or structure, re-run both —
font-metric changes reflow text and can reintroduce R1.
