---
version: 0.1.0
date: 2026-10-30
status: PROPOSED (rules only; no code changed)
supersedes: the `pocket` skin in runtime/specs/grammar-chips.json (grammar branch claude/sharp-visvesvaraya-c391ba)
parent: _PROPOSALS/2026-10-30-unified-design-system-reconcile.md
---

# Instrument construction rules: what the real hardware does, and what our Pocket skin gets wrong

Zach, 2026-10-30: "the DJ / teenage instruments theme isn't great tbh", then "check out their actual hardware and lets try and refine the construction rules".

## Sources and how sure each claim is

- **Fetched (2026-10-30):** the Teenage Engineering product pages for EP-133 and OP-1 and the OP-1 layout guide. They give materials, dimensions and control groups, but almost no visual detail (most of the layout is in images).
- **Fetched, second-hand:** design-system write-ups. These say the site uses 1px grey rules between catalogue cells instead of cards and shadows, and that the brand leans on monospaced type. Both are third-party claims, not TE's own.
- **From prior knowledge of the hardware (not re-verified today):** the encoder colours, key finish, legend placement and display type below. Before any rule ships, check each one against product photos.

## What the hardware does

1. **Flat, matte surfaces.** The OP-1 is a bead-blasted aluminium slab, and the EP-133 is a moulded polymer panel (PA66 key housings, per the spec page). Neither has a gradient or gloss. Depth comes from real height: keys stand proud of the deck. Light falls on them, nothing is painted on.
2. **Keys are flat-topped modules on one strict grid.** The keys and pads share one pitch with even gutters. Size changes only in whole grid steps; there are no in-between sizes.
3. **Colour means function, and only function.** The OP-1 has four colour-coded encoders (the layout guide's rule: a green on-screen element is changed by the green encoder). The rest of the unit is greyscale. One accent (orange) marks the key you act with. Colour is never decoration.
4. **Legends are small, uppercase and set like a technical drawing.** Primary labels sit on or next to the key. Shift functions sit under the key, smaller and in a second ink. Numbered callouts (1 to 19 in the OP-1 guide) name each control group.
5. **The display is a segment or pixel field, not a glossy screen.** EP-133's "super segment hybrid display" is a fixed set of segments that are on or off. LEDs are small points that light only when a state is true.
6. **Grouping is by blank space and alignment, not boxes.** The OP-1 guide's four groups (master, tape, display and encoders, sound and keys) are separated by position on the chassis, not by frames around them.
7. **Spec-sheet framing.** The dimensions, weight, travel (3.20 mm) and actuation force (50 gf) are published as data. The product talks in numbers.

## Where our Pocket skin breaks those rules

Read from `skins.pocket` in the grammar spec (grammar branch, 2026-10-30).

| Pocket skin today | Hardware rule it breaks | Fix |
|---|---|---|
| `key: linear-gradient(135deg,#1e293b,#111827)` | 1, matte and flat | A solid key face, one tone lighter than the deck. No gradient. |
| Two cast shadows on every key (`0 1px 2px`, `0 2px 4px`) | 1, height is real, not painted | One 1px bottom edge (`inset 0 -1px 0`) for the key lip. No blur. |
| 4px double-ring bezel on every chip | 6, group by space, not boxes | No bezel on chips. One hairline frame around the whole panel only. |
| Grain overlay at .05 to .07 | 1, the surface is clean | No grain on instrument panels (grain stays a fidelity signal: GRAIN render only). |
| 10px key radius against 3px chips | 2, one grid, whole steps | Radius from one scale: 2px for chips and keys, 4px for panels. |
| A breathing LED glow (field skin) | 5, LEDs are on or off | A solid 6px dot, on or off. Live = blink at one fixed rate, or a static ring. No glow radius. |

The HUD default that landed in d5b31ae2 (hairline, tone corner ticks, no glow, no shadow) is already close to the hardware. The instrument rules below extend HUD; they do not add a third look.

## Construction rules (proposed tokens and CSS)

**Grid**
- One base unit `--u: 4px`. Every size, gap and pad is a multiple of `--u`.
- A key module is `--key: 11u` (44px, also the touch-target floor). Gutter `--gut: 2u` (8px).
- Panels use a column grid: `grid-template-columns: repeat(auto-fill, minmax(calc(var(--key) * 2 + var(--gut)), 1fr))`. Modules span whole columns only.
- Responsive: one column of modules at 360, then 2, 4, 8 columns at the existing breakpoints. Modules never scale fractionally; columns are added instead.

**Surfaces and borders**
- Deck `--deck` (the page surface), key face `--key-face` one step lighter, well `--well: #0a0f15` (already in `Landing.tsx:191`).
- Borders are 1px hairlines in `--border`. One frame per panel; none on items inside it. Groups are separated by a `2 * --gut` blank gap, not a rule.
- No `box-shadow` with blur anywhere on instrument surfaces. The allowed insets: `inset 0 1px 0` top highlight (from `ScopeHud.tsx:45`) and `inset 0 -1px 0` key lip.

**Colour**
- Greyscale for every surface. Tone colour only on: the glyph, the tag, the corner ticks, and an LED. This matches the grammar rule "signal colour tints border, tag and glyph only".
- One action accent per view: the primary action key. Keep cyan, the existing focus colour, unless Zach wants TE orange (orange is now LIMIT ⚑, so reusing it would collide; recommend no).

**Type and legends**
- Legends: mono, uppercase, `0.6875rem` (the grammar's tag size), tracking `0.08em`. The secondary (shift) legend sits under the item at the same size in `--text-secondary`.
- Numbers are tabular (`font-variant-numeric: tabular-nums`) everywhere.
- Numbered callouts for groups ("01 / 06" already on /proof) are the TE callout pattern; keep it.

**Indicators**
- LED: a 6px circle. Off is `--border`; on is the tone colour. There is no third state.
- Live: blink at 1 Hz with 50% duty, or hold steady. The blink stops under `prefers-reduced-motion`. Use `--mo-*` tokens and stay under the flash limit in DESIGN.md "Motion and safety".
- Readouts are segment-style: mono digits on `--well`, fixed width, no animation between values (a value changes, it does not tween).

**Motion**
- Press: `transform: translateY(1px)` and the key lip goes to 0, over `--dur-micro`. Nothing else moves.
- No hover glow. Hover raises the border to `--text-secondary`.
- Panels open in place (the /proof zoom levels); height animates over `--dur-*`, no fade on text.

## What changes where

1. Grammar spec: replace `skins.pocket` with `skins.instrument` built from the rules above, or drop pocket and fold these rules into HUD. The grammar session owns the spec, so this is its edit. Recommend folding into HUD: one look, fewer skins.
2. dj.arcs.care (Phosphor, built from `_ARTIFACTS/phosphor-src/`): the Pocket skin there is a sanctioned world. Apply the same fixes only if Zach wants the DJ page itself rebuilt. The Phosphor release-hold process applies.
3. Kit tokens to add: `--u`, `--key`, `--gut`, `--key-face`, `--well`, `--hud-highlight`, `--key-lip`. One JSON source, per the decision recorded in the parent proposal.

## Open for Zach

1. DECIDED 2026-10-30 (Zach: "Fold into HUD"): the instrument rules fold into HUD. One look; `skins.pocket` leaves the shared spec.
2. Rebuild dj.arcs.care's own Pocket skin to these rules, or leave that page as it is?
3. Before shipping, check the rules marked "prior knowledge" against product photos (encoder colours, legend placement). Should a session pull photos and check them?

## Sources

- [teenage.engineering, EP-133 product page](https://teenage.engineering/products/ep-133) (materials, key force and travel, display)
- [teenage.engineering, OP-1 product page](https://teenage.engineering/products/op-1) (aluminium body, flush glass display, encoders)
- [teenage.engineering, OP-1 layout guide](https://teenage.engineering/guides/op-1/original/layout) (19 controls in four groups; the colour-coded encoder rule)
- [shadcn.io, teenage engineering design system](https://www.shadcn.io/design/teenage-engineering) (third party: 1px grey catalogue rules)
- [blakecrosley.com, Teenage Engineering guide](https://blakecrosley.com/de/guides/design/teenage-engineering) (third party: monospaced type; depth without skeuomorphism)

## Applied, and three conflicts open for Zach (2026-10-30)

The fold into HUD landed in 188a7ba3 on PR 1877 (grammar branch). `skins.pocket` is gone from the spec, the emitter, the specimen and GrammarChip.tsx; Phosphor's own Pocket skin is untouched. Not adopted, because DESIGN.md says otherwise and the Impeccable detector enforces DESIGN.md:

1. **Radius.** This doc says 2px for chips and keys and 4px for panels. DESIGN.md's scale is xs 3px and sm 6px, and 2px tripped the detector earlier today. The spec keeps 3/6. Recommend: keep DESIGN.md (the difference is not visible at chip size).
2. **Legend tracking.** This doc says 0.08em. DESIGN.md's mono label tiers are 0.12 to 0.16em, so tags stay at 0.14em. Recommend: keep DESIGN.md.
3. **Field skin LED.** The opt-in field skin still has a breathing glow, which breaks "LED on or off". Recommend: remove the glow and give field the same on/off LED, so no skin breaks the rule.

**DECIDED 2026-10-30 (Zach: "Yes, all three"):** keep DESIGN.md radius (3px chips, 6px panels) and 0.14em tag tracking; remove the field skin's breathing glow so every LED is on or off. The grammar session applies the field change on PR 1877.
