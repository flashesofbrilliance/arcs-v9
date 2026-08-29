---
name: artifact-text-qa
description: The build-and-verify gate for any web artifact, landing page, website, dashboard, or visual that contains TEXT. Enforces the gold standard — WCAG 2.1 AA accessibility, semantic HTML5, accessible-tabs/ARIA patterns, and an automated visual-regression sweep that catches horizontal overflow and text clipping across the full width range and every view. Use whenever creating or editing an HTML artifact or UI with text. Exists because a text-wrapping/overflow regression kept recurring; measure it, don't eyeball it.
---

# Artifact text QA — the standards gate for text-bearing web work

Build to the gold standard, then **prove it with the two bundled tests**. Do not ship a text artifact on eyeballing alone.

## Run these two before shipping (and after any edit pass)

Both need playwright + chromium (installed on this machine at `/Users/zharris/arcs-v9/node_modules`). If the page lives outside that repo tree, symlink first: `ln -sfn /Users/zharris/arcs-v9/node_modules node_modules`.

```bash
node <skill-dir>/overflow-test.mjs  path/to/page.html   # layout: no overflow / no clip, all views x 13 widths
node <skill-dir>/axe-test.mjs       path/to/page.html   # accessibility: WCAG 2.1 A/AA via axe-core, all views
```

Each exits non-zero with a per-issue list. Ship only on a double PASS. Both auto-detect tabbed layouts (`.tab-link[data-tab]` + `#tab-*` panels) and sweep every tab.

## The bar (what "gold standard" means here)

### 1. No overflow, no clip — the recurring regression
At **every** width (mobile → wide) and on **every** view:
- The page never scrolls sideways (`scrollingElement.scrollWidth <= innerWidth`).
- No element's right edge exceeds the viewport — except children of an intentional horizontal scroller (a scrollable tab bar); the test excludes those.
- No text element is clipped by its own box (`scrollWidth > clientWidth`), and nothing is clipped by an `overflow:hidden` ancestor (a common silent one is a rounded "sheet" wrapper).

Root-cause fixes (patch the cause, never just nudge a width):
- **grid/flex child overflows** → child has default `min-width:auto`; set `min-width:0` on grid/flex children.
- **long token (email/URL/ID) overflows** → `overflow-wrap:anywhere` on that text.
- **`nowrap` label in a flex row overflows** → `min-width:0; overflow:hidden; text-overflow:ellipsis`, let the flexible sibling shrink (`flex:1 1 <small>`), and drop the font-size on mobile.
- **em-dash reads as a broken wrap** → remove em-dashes entirely; commas / periods / plain phrasing. (A space-padded em-dash lands at a line break and looks like a bug. It also violates the plain-language rule.)

### 2. WCAG 2.1 AA accessibility (axe must be clean)
- **Contrast:** body/label text ≥ 4.5:1, large text (≥24px, or ≥18.66px bold) ≥ 3:1. **Compute it, don't guess** — small grey labels and bright-accent small text are the usual failures. A quick node check:
  `node -e 'const L=h=>{h=h.replace("#","");if(h.length===3)h=[...h].map(x=>x+x).join("");const c=[0,2,4].map(i=>parseInt(h.substr(i,2),16)/255).map(v=>v<=.03928?v/12.92:((v+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]};const CR=(a,b)=>{const x=L(a),y=L(b);return((Math.max(x,y)+.05)/(Math.min(x,y)+.05)).toFixed(2)};console.log(CR("#616b78","#ffffff"))'`
  Reserve the bright accent for large display and fills; use a deeper tint for small accent text and for white-on-color buttons. On a colored surface, tint secondary text from that hue — never flat gray.
- **`lang`:** the document needs `lang`. On a claude.ai artifact you don't write `<html>`, so set it at runtime: `document.documentElement.lang = document.documentElement.lang || 'en'`.
- **Landmarks:** exactly one `<header>` (banner), one `<main id="maincontent">`, `<nav>`, `<footer>`; a "Skip to main content" link as the first focusable element.
- **Headings:** a real outline — one `<h1>`, section titles `<h2>`, card titles `<h3>`. Don't fake headings with styled `<div>`s.
- **Tabs = the WAI-ARIA tabs pattern**, not just roles: `role="tablist/tab/tabpanel"`, `aria-selected`, `aria-controls`, `id` + `aria-labelledby` linking, roving `tabindex` (selected 0, rest −1), and keyboard (ArrowLeft/Right/Up/Down, Home, End). If you can't implement the full pattern, use plain nav buttons instead — half a pattern is worse than none.
- **Focus & motion:** visible `:focus-visible` on every interactive element; honor `prefers-reduced-motion`.
- **Images/graphics:** `alt` on `<img>`; `role="img"` + `aria-label` on informational SVG/canvas; `aria-hidden` on purely decorative marks.

### 3. Semantic HTML5 + JS hygiene
- Buttons for actions, `<a href>` for navigation/links (external booking/social = real `<a target="_blank" rel="noopener">`).
- No inline event handlers; wire listeners in one script; guard `try/catch` around `localStorage`/`history`.
- Prefer deterministic, always-rendering markup (inline SVG) over canvas whose size depends on layout timing — a canvas that inits at zero width in a hidden/iframe context silently never paints. If canvas is required, self-heal (re-measure each frame + `ResizeObserver`).

### 4. Anti-slop (see design.md for the full list)
- **Type:** avoid the AI-default faces (Inter, Roboto, Space Grotesk, Geist, Plus Jakarta, Fraunces). Pick a distinctive pairing; a display face with character + a clean body + mono reserved for real data/measurement.
- Don't reach for the category defaults reflexively: a tracked uppercase eyebrow over *every* section, 01/02/03 numbering without a real sequence, same-size icon+heading+text cards as the whole page, gradient text, glass/blur as decoration, colored `border-left > 1px`. The brief can earn any of these; reaching for one on a free axis means you weren't deciding.

## When it fails
Fix the root cause, re-run both tests, and only then republish. The tests are the definition of done, not a formality.
