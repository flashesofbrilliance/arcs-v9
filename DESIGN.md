---
name: ARCS
description: Render through the fog to earned clarity: a dark-cockpit decision instrument.
colors:
  obsidian-bg: "#020408"
  panel: "#0d1117"
  elevated: "#111827"
  border-subtle: "#1e293b"
  text-primary: "#e2e8f0"
  text-secondary: "#94a3b8"
  text-muted: "#7a8699"
  text-dimmed: "#8391a7"
  true-north-cyan: "#00F0FF"
  coherent-green: "#00FF9D"
  locked-gold: "#FFD700"
  warning-orange: "#ff9d3c"
  ruin-red: "#FF4D6D"
  conviction-violet: "#A78BFA"
  paradox-magenta: "#E879F9"
typography:
  display:
    fontFamily: "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, 'Newsreader', serif"
    fontSize: "clamp(1.5rem, 4vw, 2.4rem)"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Inter', 'Inter Fallback', system-ui, -apple-system, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  body:
    fontFamily: "'Inter', 'Inter Fallback', system-ui, -apple-system, sans-serif"
    fontSize: "0.925rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
  label:
    fontFamily: "'JetBrains Mono', 'JetBrains Mono Fallback', 'IBM Plex Mono', 'IBM Plex Mono Fallback', ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, monospace"
    fontSize: "0.6875rem"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.14em"
rounded:
  xs: "3px"
  sm: "6px"
  md: "10px"
  lg: "16px"
  pill: "999px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "6": "24px"
  "8": "32px"
  "12": "48px"
components:
  panel:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "20px 22px"
  button-ghost:
    backgroundColor: "{colors.obsidian-bg}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.xs}"
    padding: "8px 12px"
  chip:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.xs}"
    padding: "3px 8px"
  input:
    backgroundColor: "{colors.elevated}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.sm}"
    padding: "10px 14px"
---

# Design System: ARCS

## Overview

**Creative North Star: "Render Through the Fog"**

ARCS renders at *earned fidelity*. Every surface is only as sharp as the evidence deserves, and it never lies about how certain it is. Clarity is not granted at load; it is earned as the fog lowers and the terrain resolves. This is the organizing law of the entire visual system: a coarse, honest reading always beats a confident fabrication. The screen obeys the same physics the product asks of its user, so the interface is not a container for the idea, it is the idea, drawn.

The world is obsidian and single-theme by design, a dark cockpit read under pressure. It is calm, precise, and serious play: instruments in skilled hands, not a SaaS dashboard. Color is never ornament; each hue is a *state*, and its rarity is what makes it legible. Depth is made of light, not cast shadow, because the goal is light through fixed form. The register is Myst, not onboarding: the world trusts the reader and expects them to rise to it.

The signature is the mark itself. **The ARCS mark is a Möbius strip emerging from a fog field onto a clean gold horizon line.** The Möbius is the house glyph, the tilde extruded: take the `~` (an approximate, a placeholder, a reserved vessel) and sweep it through the decision manifold with a half-twist, and you get an arrow-less, non-orientable surface made of arcs. The fog buries the horizon; lowering it earns the bearing. The mark animates the tagline, and everything else in the system is a still frame of that motion.

**Key Characteristics:**
- Earned fidelity: four render states (SHARP / DEGRADED / GRAIN / MOIRE) that degrade legibility to match evidence.
- Obsidian, single-theme, dark-cockpit; no light mode.
- Semantic color: every accent is a state, used on ≤10% of a screen.
- Glow, not shadow: depth is luminance, not cast darkness.
- Mono for instruments, serif for canon, sans for the body.
- The tilde (`~`) is the atomic glyph and the honesty marker.

## Colors

An obsidian ground carrying a small set of high-chroma signal colors, each of which *means* something. The palette is mostly neutral; the signal hues are rare on purpose.

### Primary
- **True North Cyan** (#00F0FF): the active bearing, the compass direction, selected/active state, the SHARP-state strip. The color of "this way is uphill."

### Secondary
- **Coherent Green** (#00FF9D): coherence and the GREEN Y-gate; a clarity-ridge, high-conviction reading. Rendered SHARP.
- **Locked Gold** (#FFD700): Court / LOCKED / one-way-door / the earned horizon line in the mark. Gravity, commitment, the bearing you can trust.
- **Ruin Red** (#FF4D6D): alert, the RED free-solo/ruin-exposure topology, the GRAIN state. Never used decoratively; it inverts meaning if misapplied.

### Tertiary
- **Warning Orange** (#ff9d3c): warnings and macro-tags, one step below ruin.
- **Conviction Violet** (#A78BFA): the DELTA state, a shift in conviction.
- **Paradox Magenta** (#E879F9): PARADOX / the Curator; the MOIRE render state's tint.

### Neutral
- **Obsidian** (#020408): the page ground. The world's floor.
- **Panel** (#0d1117): cards, modules, instruments.
- **Elevated** (#111827): inputs and hover states.
- **Border Subtle** (#1e293b): dividers, card strokes.
- **Text Primary** (#e2e8f0): primary reading.
- **Text Secondary** (#94a3b8): supporting copy.
- **Text Dimmed** (#8391a7) / **Text Muted** (#7a8699): metadata and mono labels. Both clear WCAG AA 4.5:1 on Obsidian, Panel and Elevated (raised 2026-10-04 from #64748b / #475569, which measured 4.31:1 and 2.71:1).

**The Semantic Color Rule.** Color is state, never decoration. Cyan is bearing, green is coherence, gold is locked, red is ruin, violet is conviction-shift, magenta is paradox. If a color would not survive being read as its state, it does not belong on the screen.

**The One Voice Rule.** Any single signal color occupies ≤10% of a screen. Rarity is the legibility. A screen lit up in cyan says nothing; one cyan bearing says everything.

## Typography

**Display Font:** Iowan Old Style / Palatino (serif): the canon and oral-history register (proverbs, the Tao, load-bearing quotes). Self-hosted fallback: Newsreader (`public/fonts/`), the canon serif of the literary page family (NFTT, Lore) and of rendered video, where the system serifs are absent.
**Body Font:** Inter (with system-ui fallback): all prose and reading.
**Label/Mono Font:** JetBrains Mono (with IBM Plex Mono): instrument labels, section indices, gauges, metadata.
**Fallback faces (not separate voices):** Inter Fallback, JetBrains Mono Fallback and IBM Plex Mono Fallback are the metric-matched faces next/font generates for the three declared fonts; SF Mono, SFMono-Regular, Menlo and Consolas are the system tail of the mono stack. They render only while or instead of the declared font loading.

**Character:** Three voices, strictly separated by job. Mono is the instrument legend (cold, tracked, uppercase). Sans is the calm reading voice. Serif is reserved for wisdom in transmissible form: the things meant to be carried in the mouth to the next person.

### Hierarchy
- **Display** (serif, 500, clamp(1.5rem, 4vw, 2.4rem), 1.2): proverbs, canon headers, load-bearing quotes.
- **Headline** (Inter 600, 1.15rem, 1.25): section titles.
- **Title** (Inter 600, 0.95rem): card and panel titles.
- **Body** (Inter 400, 0.925rem, 1.6, max ~70ch): all prose.
- **Label** (JetBrains Mono 700, 0.6875rem / 11px, +0.14em, UPPERCASE): instrument labels, section indices, gauge units. 11px is the floor for any functional text (raised 2026-10-08 from 0.625rem, which sat under the design detector's readability floor and could not satisfy both rules).

### Named Rules
**The Graded-Legend Rule.** Mono labels use six graded tiers (t1 to t6): as a tier rises, size increases and tracking decreases while weight holds, so a section heading never reads like a field label. Color stays caller-controlled because it is semantic. The lowest tier is 11px; nothing functional renders smaller.

**The One-Run Label Rule (2026-11-12).** A mono label is one run of text in one box. Never a `display:flex` row with loose words interleaved with spans: each text run and each element becomes its own flex item, so "BUILD TELEMETRY · DAY 0 → DAY 217 · AS OF Nov 12" breaks into ragged columns at narrow widths. Make the row a block with inline pieces (a tick is `inline-block`), or wrap the words in one `<span>`; keep dates and day counts `white-space:nowrap`. A label never sets itself below 11px or tracks wider than +0.14em. Gate: `scripts/page_gate.py` check `flex-text` (error on `--matrix full`, warning on quick), fixtures in `scripts/tests/test_page_gate_flex_text.py`.

**The Four-States Rule (2026-11-12).** Every interactive component has hover, focus-visible, pressed and disabled, in dark and light, with 44px targets on coarse pointers. Disabled keeps full-opacity text (see rule 3 below): it is carried by a dashed border and `not-allowed`, not by dimming. A click-to-open surface that is not a button gets `role`, `tabindex` and Enter/Space. The status page builder's self-test (`scripts/status_page_build.py --self-test`) fails when a component loses a state; there is no repo-wide gate for this yet.

**The Three-Voice Rule.** Mono = instrument, Sans = reading, Serif = canon. Never cross them: a proverb never renders in mono, a gauge label never in serif.

## Layout

Centered single-column documents on the obsidian ground: `max-width: 960px` for documents (760px for reading-dense surfaces like the Tao, 640px for forms). Container padding steps from 1rem (mobile) to 1.5–2rem. The spacing rhythm is a 4px base (steps 1–12). Instruments cluster in a sticky "control deck" at the top (blurred obsidian, `backdrop-filter: blur(10px)`, a single hairline border-bottom). Wide content (tables, timelines, manifolds) scrolls inside its own `overflow-x: auto` container; the page body never scrolls sideways. Density is instrument-tight, not airy: this is a cockpit, read at a glance.

## Elevation & Depth

Depth is **luminance, not cast shadow.** Surfaces are flat panels on the obsidian ground; separation comes from a one-step tonal lift (bg → panel → elevated) and a hairline border, not from drop shadows. The one exception is the **glow**: an active or locked instrument emits a restrained bloom of its own signal color.

### Camera and light (2026-11-12, Zach approved the draft in _PROPOSALS/2026-11-13-design-world-rules.md)

**The One-Camera Rule.** A surface drawn in 2.5D uses one fixed isometric camera: a tilt about the X axis only, 38 degrees with `perspective(1500px)`, tiles stay clickable. No yaw, no roll, no dolly. Under `prefers-reduced-motion` the camera is flat (0 degrees). One sanctioned second use: a receding floor plane drawn with a `vh`-based perspective (the status page presentation stage); it is a ground, not a camera, and carries its own comment. Gate: `scripts/page_gate.py` check `camera` (warning).

**The Key-Light Rule.** There is one key light, from above, and it is expressed as light, not as cast darkness (it sits inside the Glow-Not-Shadow Rule below): a raised or active surface gains a lighter tone and a top-edge highlight; a recessed well is darker with its shade at the top edge. Signal colour lives in the rim, the glyph, the label and the glow, never as a saturated fill. Blur radii and alphas stay inside the Shadow Vocabulary below; this rule adds a direction, not a new size.

### Shadow Vocabulary
- **Signal glow** (`box-shadow: 0 0 34px rgba(0,240,255,.07)` and kin): a present-but-restrained bloom under an active bearing or a locked panel. Alphas ~.07–.28, deliberately dialed down from hotter earlier values.
- **Locked bloom** (`box-shadow: 0 0 54px rgba(0,240,255,.16); border-color: rgba(0,240,255,.6)`): the crystalline "superionic" state, light through fixed form.

**The Glow-Not-Shadow Rule.** Depth is made of light, never of cast darkness. A surface at rest is flat. Elevation is a signal-colored glow that appears as a *response to state* (active, locked, focus), not an ambient default. Cast drop-shadows are banned.

## Shapes

Soft-tech corners: `xs 3px` (chips, ghost buttons), `sm 6px` (cards, inputs, most instruments), `md 10px` (feature panels), `lg 16px` (rare hero containers), `pill 999px` (toggles). Borders are single hairlines (`1px solid #1e293b`); the active/locked states shift the border color to a signal tint rather than thickening it. The recurring silhouette is the **arc**: the compass sweep, the gauge arc, the Möbius strand, the fog gradient band. Straight rules exist only as the horizon line and section dividers (a cyan-to-transparent gradient hairline). The house is made of arcs and one honest horizon.

## Components

### The Mark (signature)
- **Form:** a Möbius strip (arrow-less, non-orientable, drawn as interfering strand families) rising from a layered fog field onto a single gold horizon line at ~62% height.
- **Construction:** the tilde extruded: the `~` swept through the manifold with a half-twist. Two strand families (cyan `rgba(0,240,255,.30)` + gold `rgba(255,215,0,.16)`) offset by a moiré Δ; the interference pattern belongs to neither, which *is* the PARADOX/MOIRE state.
- **Behavior:** the fog is a variable. Lowering it earns the horizon (the bearing); clarity is never granted at rest. Drift (slow rotation) is the default idle; reduced-motion holds a still frame.
- **Wordmark:** `ARCS` in JetBrains Mono 700, +0.16–0.42em tracking, with the `A` or the leading glyph in True North Cyan. Never set the wordmark in serif or sans.

### Buttons
- **Shape:** `xs 3px` radius, ghost by default.
- **Ghost (primary usage):** transparent on obsidian, `1px solid #1e293b`, mono 700 uppercase label in text-secondary. Hover/focus shifts border and text to True North Cyan (`border-color: #00F0FF; color: #00F0FF`).
- **Active/On:** border + text in the relevant signal color with a faint tinted fill (`background: rgba(0,240,255,.08)`).
- **Focus:** `outline: 1px solid #00F0FF; outline-offset: -1px`, always visible, never removed.

### Chips
- **Style:** panel background, hairline border, mono micro-label (t1/t2). Status chips tint border + text to the signal color (`c-ok` green, `c-part` gold, `c-stale` red) with a ~7% tinted fill.

### Cards / Panels
- **Corner:** `sm 6px` (`md 10px` for feature panels).
- **Background:** panel (#0d1117) on obsidian; elevated (#111827) for nested inputs.
- **Border:** hairline #1e293b; active/locked shifts to a signal tint. Depth via glow (see Elevation), never drop-shadow.
- **Title:** mono 700 uppercase in a signal color; body in Inter.

### Inputs / Fields
- **Style:** elevated background, `sm 6px`, hairline border.
- **Focus:** border shifts to True North Cyan with a faint cyan glow; `accent-color` on ranges is cyan (gold for interference/offset controls).

### Gauges / Instruments (signature)
- **Form:** a numeric readout in mono tabular-nums with a mono unit label above; value colored by state (green≥70, gold≥45, red<45 for NCI-style). Arc gauges sweep the signal color.
- **Honesty:** assessed values render with a leading `~` and are dimmed one step. Measured values never carry the tilde.

### The Render-Scale (the system's defining behavior)
Every surface can render at four earned-fidelity states, mapped from the Y-gate:
- **SHARP** (GREEN/LOCKED): `opacity 1.0, weight 500, tracking 0`. Full contrast, fine grain.
- **DEGRADED** (YELLOW/FORK): `opacity 0.85, weight 400, tracking +0.01em`.
- **GRAIN** (SCRATCH/DELTA/DRIFT/RED): `opacity 0.70, weight 300, tracking +0.02em` + sparse speckle.
- **MOIRE** (PARADOX): `opacity 0.60, weight 300, tracking +0.03em` + interference overlay.

## Motion and safety

Calm and precise. Motion is a still frame in motion, never a flash. The numbers live in `src/ui-kit/recoil-report/_tokens.css` as `--mo-*` tokens, pages read them, and `scripts/motion_policy_gate.py` (pre-commit) fails a page that drifts from them.

| Token | Value | Meaning |
|---|---|---|
| `--mo-pose-rate` | 8 | Glitch poses per second (zoetrope). Never faster. |
| `--mo-flash-max` | 3 | General flashes per second, whole frame or any 1/16 region (WCAG 2.3.1 general flash). |
| `--mo-lum-swing` | 0.10 | Relative-luminance swing that counts as a flash. |
| `--mo-hold-min` | 180ms | An effect stays on screen at least this long after release. |
| `--mo-loop-min` | 170ms | Shortest repeating picture loop (stutter). |
| `--mo-shutter-ms` | 650ms | Pinhole shutter: time to fully admit a new picture after a hard change. |

**Durations and easing.** Transitions use these four tokens and no literal times or curves (promoted from proposed on 2026-10-19):

| Token | Value | Use |
|---|---|---|
| `--dur-fast` | 120ms | Hover, focus and pressed state changes. |
| `--dur-base` | 240ms | Panels, trays and disclosure opening or closing. |
| `--dur-sweep` | 1500ms | Slow ambient sweeps (scan line, fog lowering). Never on a control. |
| `--ease-out` | cubic-bezier(0.2, 0.7, 0.2, 1) | The one curve: quick start, soft landing. |

Under `prefers-reduced-motion: reduce`, durations drop to 0 and ambient sweeps stop; every state change stays visible as a still frame.

Rules: no repeating animation above `--mo-flash-max` unless it only moves position or scale; a strobe-like look is made from shutter angle and pose rate (aliasing), never from raw flashing; reduced motion holds a still frame; kids' mode keeps the loudness ceiling and these limits always on. Measured, not asserted: `phosphor_guard_check.mjs` reads these tokens from the page and fails on a violation under violent random tweaking.

## Phosphor, the instrument surface

Phosphor (dj.arcs.care) is an Operate and Experience surface: a family audio instrument that runs in one page. It inherits the kit tokens verbatim and adds only what an instrument needs. Source of truth for the page: `_ARTIFACTS/phosphor-src/` (built into `_ARTIFACTS/phosphor.html`; see AGENTS.md gotcha 21).

**Atoms.** Every control is one of seven, all built from the same tokens: button (`.btn`, mono caps label, 48 px tall on touch), big button (`.bb`, display face, preset chips), pad (`.pad` for the zoom grid and `#pbk` pads, at least 56 px, 64 px in the tray), slider (native range, 44 px hit height), switch (a radio pair or `aria-pressed` button), segmented choice (`.seg`), and the LCD readout (`.lcd`, tabular numbers). Sizes come only from `--fs-label`, `--fs-body`, `--fs-headline` and `--fs-display`; radii only from `--ds-r-xs/sm/md/lg/pill`; spacing from `--sp-1/2/3` and the lane gutter. No literal size, radius or inline `style` attribute in the markup.

**Composition.** One lane. The player (`#dock`) is fixed at the bottom and is the only chrome that follows you. Trays (`.tray`: Pads, Mix) open above the player, one at a time, close on Escape (focus returns to the button that opened them) and close when the player is hidden. Kid mode shows at most 24 controls at rest; everything else sits behind the Parent hold (1.5 s) and carries `data-min="4"`. The consent dialog is the only modal and makes the page inert behind it.

**State matrix.** rest: token border and `--elevated`. hover: cyan border. focus-visible: a 2 px cyan outline everywhere (one global rule). pressed (`aria-pressed=true`): cyan or gold tint plus a border, never opacity. disabled: dimmed token color and a dashed border, never opacity (contrast rule 3). locked (Eject): `data-lock` on the root hides the exit controls. active (finger down): a pad shows `.hit` for 140 ms. A state that only changes opacity is a defect.

**Motion.** The `--mo-*` tokens govern everything. Glitch poses run at 8 a second and never faster; picture effects scale with Picture strength and the Mix limits but never exceed the flash limit, which is measured on the shown frame and holds strength at Soft for three seconds when two flashes occur in a second. Reduced motion removes transitions and keeps every state change visible.

**The hidden attribute always wins** (`[hidden] { display: none !important; }`): a display rule once showed the pad picker and the Sing box to everyone. The hidden check reads what a person sees, not the attribute.

## Do's and Don'ts

### Do:
- **Do** render at earned fidelity: match the surface's sharpness to the evidence (SHARP only when GREEN/LOCKED).
- **Do** keep assessed values marked with a leading `~` and dimmed one step (the honesty invariant).
- **Do** use color as state only, on ≤10% of a screen (Semantic Color + One Voice Rules).
- **Do** convey depth with signal-colored glow as a response to state; keep surfaces flat at rest.
- **Do** separate the three voices strictly: mono for instruments, sans for reading, serif for canon.
- **Do** keep the world obsidian and single-theme.
- **Do** give every interactive element a visible cyan focus ring (WCAG 2.1 AA target).

### Don't:
- **Don't** render SHARP on thin evidence; a coarse honest reading beats a confident fabrication.
- **Don't** use a signal color decoratively, or let one flood the screen.
- **Don't** use cast drop-shadows for elevation.
- **Don't** set the wordmark or a proverb in the wrong voice (no serif wordmark, no mono proverb).
- **Don't** use em-dashes anywhere (plain-language rule wins even over canon voice; prefer commas, colons, periods, or the interpunct · ).
- **Don't** introduce a light theme on product surfaces. Paper documents use the sanctioned Light Paper world, at AA contrast.
- **Don't** let a per-engagement canon family's locked house grammar (e.g. the Louisville omakase world) leak into product surfaces.
- **Don't** set functional text under 11px.
- **Don't** hardcode a retired color. `#64748b` and `#475569` were retired 2026-10-04 (they fail AA on obsidian); inherit the tokens instead of redeclaring the palette.
- **Don't** write template syntax (`${...}`) into a static page; it renders as visible code. Expand it to markup, or build the DOM in a script.

## Sanctioned Visual Worlds

A surface may run its own locked visual world instead of this one, but only by being named here, with its reason. Anything not listed is held to this file, and a deviation is drift, not style. The design detector config (`.impeccable/config.json`) scopes its exemptions to these worlds rather than to single pages.

| World | Where | Its own grammar | Why it is separate |
|---|---|---|---|
| Recoil report kit | `src/ui-kit/recoil-report/` and the pages that inline `_tokens.css` | InstrumentSans, GeistMono, its own label grammar | Counterpart artifacts, locked before this file |
| Omakase family | `public/omakase/` | case `#0B0B0C`, dial `#E8E4DA`, gold `#C9A227`, vermillion `#E34F1C`; Helvetica, SF Mono | Per-engagement canon (PRODUCT.md) |
| NFTT literary posts | `public/blog-nftt-*.html` | The "With Life" literary template | Editorial essays, a reading world |
| PRL client pages | `public/prl-*.html` (prl-page-factory) | Todd's register: pilot checklist, BLUF first, its own greys and panel surfaces | Client-facing status family with its own locked system; a product-world codemod regressed all nine pages on 2026-10-08 |
| Light paper | Resumes, counterpart dossiers and full records, TIL posts (light-surface pages) | Paper grounds (`#ffffff` to about `#e9eef4`); accent teal `#00748e`; greys no lighter than `#6b757f` on white; every text color at least 4.6:1 on the darkest paper surface it sits on | Read and printed like paper, so a light ground is the honest medium. Sanctioned 2026-10-08 on condition of AA contrast, measured, not assumed |
| Instrument kit | Claude Design ARCS OS design system, `src/instrument/` | `#07090B` ground, teal `#4ABDB0`, sky `#7AD2FF`, ochre `#D7A65A`; Barlow Condensed, IBM Plex Mono | A tactical-instrument sub-system; repaired in place 2026-10-08 |

**The Inter Rule.** Inter is the body voice by design. The detector's "overused font" warning on Inter is answered once, here, not page by page.

## Ratchets and the Done Goal

Design debt on served surfaces only goes down. The done goal: every page surfaces.arcs.care serves is clean (0 design-detector findings, 0 visible em-dashes, wrap lint and token gate clean, 0 template leaks, 0 WCAG A/AA violations) except surfaces in a sanctioned world above.

- `scripts/design_debt_sweep.py` holds the per-page design baseline (`runtime/specs/design-debt-baseline.json`); pre-commit blocks any staged served page whose count rises.
- `tests/a11y-served.spec.ts` runs axe over every served page and holds the WCAG baseline (`runtime/specs/a11y-baseline.json`).
- Breaks are booked as break, repair, guard in `_PATTERNS/kintsugi-visual-grammar-seams.md`.
- Contrast is measured only by the rendered axe ratchet. The static detector's `low-contrast` rule is off (`.impeccable/config.json` ignoreRules, 2026-10-11): it cannot resolve `var()` colors, so it judged themed text against white or black, both hiding real failures and inventing false ones.

### Rules learned in the burn-down (2026-10-09 to 10-11)

1. **Measure the settled page.** WCAG checks run with reduced motion and a settle wait. A page sampled mid fade-in reads as 1.1:1 contrast; about 120 of 301 contrast nodes were animation frames, not defects. The a11y spec already does this; any new rendered gate must too.
2. **Give the root literal colors.** `html` and `body` carry the literal background and text color their tokens resolve to, not only `var()`. The static detector cannot resolve variables, so it judges text against white or black and both over-reports and misses real failures (forge-pattern: 97 findings to 42 once the root was literal).
3. **Show state with color, not opacity.** Inactive tabs, labels and links dimmed to 45 to 60% opacity fail contrast. Use a token that passes AA in every state. This includes the earned-fidelity fog render (Zach, 2026-10-11): fog text stays at full opacity and reads as fog through weight, tracking and grain (WORLD.md render scale).
4. **Underline links that sit in running text.** Color alone does not mark a link. Every page also declares a footer link rule, so no link falls back to browser-default blue.
5. **Roles match behavior.**
   - A row of toggle buttons is `role="group"` with `aria-current` or `aria-pressed`, never `role="tablist"`.
   - A tablist holds only `role="tab"` children; put other controls outside it (`display:contents` keeps the layout).
   - A closed overlay is `aria-hidden="true"` and `inert` together, toggled together.
   - An SVG that contains links is a labelled `role="group"`, not `role="img"`.
   - Inline links meet the 24px target size (a little vertical padding).
6. **Fix generated pages at the generator, and label every input.** A fix in the page alone is erased on the next render. Every input has a `<label for>` or an `aria-label`.
