# Zach's style ledger (Gravity candidate site and every ARCS visual surface)

Written 2026-11-13 by the session that relays Zach's picks. This is the one place his stylistic rulings live (canonical copy: `_PATTERNS/zach-style-ledger.md`; add each new ruling here, dated, in the change that applies it), so the impeccable skill and the brand-line-producer agent judge against the same list. Read it before rendering anything. Read WORLD.md (tonal register: Myst, not SaaS onboarding; calm, precise, serious play; earned fidelity; text never dimmed), DESIGN.md, and the ARCS OS Design System artifact (https://claude.ai/artifact/1DnaMvAFvSspGFTvh1f2wi) too. Where they disagree with this ledger, this ledger is Zach's newer word; log the seam, don't silently pick.

## Method (standing)
- Every visual change: render each changed block as 3 pixel-true options (A/B/C) in an inline show_widget picker, with real design-system tokens and the page's real copy, a strength dial when an effect has one, and a "Send my picks" button. Zach picks; then build. Name each block's atomic layer (atom, molecule, organism, template, page).
- RCA first. Fix defects at the source (kit part, token, generator) with a gate that fails the whole class; never a page shim.
- Never invent facts, quotes, numbers or dates. Placeholders are labelled as placeholders.
- Before shipping: repo gates (artifact_wrap_lint, page_gate, kit_primitive_sync --kit, and the keyline check from PR 2219), then brand-line-producer, then impeccable critique. Sweep 360 to 1440 incl. 700 to 1000, both themes.

## Rulings so far (Gravity site, 2026-11-13)
- Navigation: myAlly-style top nav; burger menu at 900px and below. No hairline glow on the sticky nav, dark or light.
- Glass, at 0.75x strength: Header C (rim glow), Stats B (sheen plus emboss), Week One C (deboss well), Folds B (sheen plus emboss), Evidence rows A (flat).
- Light mode: wells sit lighter than their ground, no exception.
- Dark mode: no banding in fold gradients (sheen pinned to 56px).
- Quotes: serif, swash quote marks drawn as SVG.
- Chips: the design-system Badge (22px outer height, border-box, 0 10px, the 4px badge radius --ds-r-badge, 11px mono 700 text --fs-label at 0.1em, 13% fill, 35% border; the 4px radius picked 2026-11-13; the design system's 10px text was tried and kept at 11px after the legibility check blocked it on counterpart pages); StatusBadge is .chip.status. Gold chips only on limit rows ("How I could read it wrong").
- Grid: the R2 keyline lockup primitive; every two-column molecule starts its content column on the same keyline (the keyline check that PR 2219 adds).
- Measure: one shared px --measure for body text; ledes span full lane width matching their heading. Em-dashes 0.
- Header (picked option B, 2026-11-13): the quote comes first, in italic Newsreader serif in --text-secondary (a token, never opacity). The attribution is right-aligned at 0.85x body size. A hairline rule follows, with the pane gap (24px) above and below it. Then the headline at weight 700.
  - Seam: weight 700 overrides the 2026-11-12 "Inter semibold" headline ruling, for this header only.
  - Attribution size (Zach, 2026-11-13): 0.85x body (about 12.6px), kept off the four-step type ramp on purpose. Closed; do not snap it to --fs-label.
  - Quote marks (Zach, 2026-11-13, "Let's go with your suggestion"): the header keeps lighter font-glyph quote marks, not SVG swashes. This overrides the Quotes ruling for the header only.
- Overview: the oversized text block was too big and overpowering. It becomes the four-up proof lockup (kit 71, PR 2240).
- Folds: one rule per boundary; cards inside a fold take no top rule side by side, and rules between stacked cards only (Zach, 2026-11-15, "Wedge rules: A").

## Rulings (belief log, status.arcs.care/beliefs, 2026-11-13 to 2026-11-15)
- Braided lanes (kit 73, PR 2266; filed as 72, renumbered 2026-11-15 when the week strip took 72 on main): layout C picked 2026-11-13 (ledger lanes, thin evidence set apart under a divider, two-slider week window).
- Lane colours (Zach, 2026-11-15, "Keep coloured lanes"): each belief domain keeps its own colour (Rulebook cyan, How I work green, Security red, Client reads violet, Shipping magenta, Stress tests orange, Infrastructure blue, Public pages grey). The brand gate's objection, that signal colours do category work here (green on disproven beliefs), is ruled on: colour names the domain on this chart, the gold ring stays the only rule signal. Closed; do not neutralise the dots.
- Voice (Zach, 2026-11-15, "the royal we is the wrong thing... it seems like I am speaking about myself in the third person"): the belief log speaks in first person singular ("Every belief I changed my mind about", lane "How I work"). One author, so no "we". Closed.
