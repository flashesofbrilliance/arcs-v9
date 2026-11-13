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
- Chips: the design-system Badge (22px outer height, border-box, 0 10px, radius-xs, mono 700 at 0.1em, 13% fill, 35% border); StatusBadge is .chip.status. Gold chips only on limit rows ("How I could read it wrong").
- Grid: the R2 keyline lockup primitive; every two-column molecule starts its content column on the same keyline (the keyline check that PR 2219 adds).
- Measure: one shared px --measure for body text; ledes span full lane width matching their heading. Em-dashes 0.
- Pending (asked 2026-11-13, needs a pick): header order becomes quote first, lighter and possibly italic, then a divider with vertical padding, then the bold headline; attribution about 15% smaller. The oversized text block in the overview is too big and overpowering.
