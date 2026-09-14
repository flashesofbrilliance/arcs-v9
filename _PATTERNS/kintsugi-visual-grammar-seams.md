## 2026-09-14 · `public/jack-rain-resume.html` (Jack Dillé/Rain tailored resume, Ahmed grammar)

Found by: pre-commit design detector, new-page block. Same class of finding as the ext page above
(this file is a same-day sibling, same kit).

| # | Break | Found by | Repair | Guard |
|---|---|---|---|---|
| 1 | Em-dash in `<title>` ("Zach Harris — Resume for Rain") | detector | Changed to a comma | detector in pre-commit |
| 2 | Two low-contrast findings (`--dimmed` 4.0-4.3:1 on bg/panel) on `.contact-line`, `.role-dates`, and one step-t label | detector | Switched to `--text-secondary` (6.x:1), same fix class as seam 1 on the ext page | detector in pre-commit |
| 3 | `design-system-font`/`-font-size`/`-color`/`-radius`/`dark-glow` findings | detector | Not repaired, same acceptance as `public/jack-rain-ext.html` below: inherits `_tokens.css`, a separate locked kit from DESIGN.md | ledger only, same acceptance as the `06-beat-stepper` 3px rail entry below |

## 2026-09-14 · `public/jack-rain-ext.html` (Jack Dillé/Rain application pitch page)

Found by: pre-commit design detector, new-page block.

| # | Break | Found by | Repair | Guard |
|---|---|---|---|---|
| 1 | Two low-contrast/undersized-text findings (`--dimmed` 4.3:1 on bg, tag/meta-line text under the 11px functional floor) | detector | Tag pills bumped 9.5px→11px, meta-line 10.5px→11.5px with `--text-secondary` instead of `--dimmed`, seam labels and legend text bumped to 11-12px | detector in pre-commit |
| 2 | Remaining findings across `design-system-font`, `design-system-font-size`, `design-system-color`, `design-system-radius` (fonts/sizes/colors/radii "not declared in" or "outside" DESIGN.md) | detector | Not repaired. This page (and its internal companion `runtime/warroom/jack-rain.html`) inherits `src/ui-kit/recoil-report/_tokens.css` verbatim (the recoil-report family's own locked kit, per `token_source_gate.py`), which is a deliberately separate per-engagement visual world from the app's DESIGN.md ramp (PRODUCT.md: "per-engagement canon families may carry their own locked visual world... does not leak into product surfaces"). Forcing DESIGN.md's app-surface type/color/radius scale onto a recoil-report artifact would fight the kit it is required to inherit from. Scoped via `impeccable hooks ignore-value <rule> "*" --file <path>` for all four rules, both files, in `.impeccable/config.json` | ledger only, same acceptance as the `06-beat-stepper` 3px rail entry below |
| 3 | Two zero-offset LED-glow findings on `runtime/warroom/jack-rain.html` (`dark-glow`, `#00ff9d`/`#00F0FF`) | detector | Not repaired. This is the shipped status-LED pattern from `src/app/jobs/[jobid]/page.tsx`'s `led()` helper (`boxShadow: 0 0 8px 1px ${color}`), reused identically for BAND/GATES/SWIPE/FORGE indicators, not new decoration | `ignore-value dark-glow "*" --file runtime/warroom/jack-rain.html` in `.impeccable/config.json`, ledger for the "why" |

**Accepted, not repaired:** DESIGN.md-ramp mismatches on any page whose token source is
`_tokens.css` (the recoil-report kit), not DESIGN.md. The two visual worlds are not yet
reconciled; reconciling them belongs to `/design-sync`, not to a single artifact.

# Kintsugi seams ledger: visual grammar

> ROM primitive #6, the Kintsugi Immune System, applied to product-surface UI: **repair seams
> visibly; no silent patching of integrity failures; show the break and the gold.** Every design
> repair on an ARCS surface is booked here as break → how found → repair → guard, with the commit.
> A repair with no guard is listed as such, honestly, until one exists. Append-only. Newest first.

## How to use this file

- When a design audit, inspection round, or reader report finds a break, book it here BEFORE
  the fix is committed, then fix it, then fill in the guard.
- "Guard" names the mechanism that now fails the class, not the instance: a pre-commit gate, the
  design detector, a token, a kit primitive. "Inspection round" is an honest guard label meaning
  a human or a screenshot sweep is still the only thing that catches it.
- The page itself carries one visible gold line naming its seams (the footer on TIL surfaces;
  a `<!-- KINTSUGI SEAMS -->` header block in the source on any surface). Readers of a page that
  claims honesty get to see where it broke.
- Immune system: `scripts/git-hooks/pre-commit` runs the Impeccable design detector over staged
  pages when the launcher is installed on the machine (`~/.claude/skills/impeccable/scripts/impeccable`).
  New pages block on any finding; modified pages whose HEAD version already carried the finding
  warn (ratchet). Machines without the launcher skip cleanly and the seam is caught at the next
  machine that has it.

## 2026-09-11 · `_ARTIFACTS/til-01-warmth-routes-you.html` (TIL Ep 01 prototype)

Found by: `/impeccable audit` (detector + contrast table) and one batched inspection round at
1280 / 790 / 375. Commit: see `git log -- _ARTIFACTS/til-01-warmth-routes-you.html`.

| # | Break | Found by | Repair | Guard |
|---|---|---|---|---|
| 1 | Ten small mono labels (`--muted` 2.5 to 2.7:1, `--dimmed` 4.0 to 4.3:1) under the 4.5:1 floor | detector, 10 hits | New reading-layer token `--label:#8797ad` (6.1:1 on bg, 5.7:1 on surface) used for every small label; `--muted`/`--dimmed` reserved for non-text | detector in pre-commit |
| 2 | Tracked-caps eyebrow above the h1 (craft-floor ban) | detector | Removed. The topbar is the only chrome above the title | detector in pre-commit |
| 3 | Zero-offset cyan glow on the topbar dot | detector | Removed; the kit glow tokens stay available for signal, not decoration | detector in pre-commit |
| 4 | Three typefaces (Inter for UI labels, Newsreader, JetBrains Mono) | audit read | Two: serif for what happened, mono for what it measured. Beat titles and twin text moved to serif | ledger only (candidate: font-family count in a page gate) |
| 5 | Five bordered cards (wager, instrument, score, three tributaries, thread) competing with the two real instruments | distill read | Tributaries as hairline rows with a radio dot; thread as plain rows; score as one cyan rule. Only the wager and the instrument keep a frame | ledger only |
| 6 | Pull-quote repeated the rule strip verbatim | distill read | Lifted the surviving line from section II ("Time was the only thing...") and cut it from the prose so it appears once | ledger only |
| 7 | Tributary buttons were `display:grid` with a bare text node; the node became a third grid item and fell into the 18px dot column, one word per line at every width | inspection round (button height 517px at 1280) | Content wrapped in one `<span class="t">` so the grid has exactly two items | inspection round (not yet mechanized; candidate: a "no control taller than 3× its font-size × lines" check) |
| 8 | Forty-odd meaning-carrying labels at 9 to 10px (topbar, badges, section labels, beat tags, twin labels, table keys, footer) under the detector's 11px functional-text floor; the audit's first detector output was truncated at 120 lines, so this class only surfaced on the finish scan | detector (finish scan) | Every label raised to 11px or above, tracking eased as size grew, three long uppercase labels shortened to label length, footer to 11.5px | detector in pre-commit |
| 9 | The immune system itself failed silent: the detector exits non-zero when it has findings, my hook appended a fallback `[]` to its output, the JSON became unparseable, the count read 0, and a seeded bad page passed the pre-commit block | e2e test of the hook (a seeded HEAD copy of the page returned exit 0) | Capture the launcher output regardless of exit code; a parse failure prints a loud warning naming the manual command instead of counting as zero | e2e test in the ship notes; the hook now cannot count a parse failure as clean |
| 10 | The cold open: a standfirst blurred at rest that sharpened on scroll, with a tiny caps byline beneath it. Zach: "weird / bad design." The one authored motion moment read as a rendering fault, and the byline duplicated the footer | reader (Zach) | Blur and scroll handler removed; byline removed (provenance already in the footer). Earned fidelity stays where it is legible: the beats and the dial | ledger; rule of thumb added below |

**Rule from seam 10:** never express "low fidelity" by degrading the reader's own text. Grain, blur, and dimming belong on the instrument's rows (where the reader can compare states), never on the opening paragraph, where the only available reading is "broken."

**Accepted, not repaired:** the 3px left rail on kit beat rows (`06-beat-stepper`) trips the detector's "side-tab accent border" default. It is the kit's own primitive and the incumbent world; the decision whether the kit keeps it belongs to the design system (`/design-sync`), not to one page. Booked here so the disagreement is visible rather than suppressed.

**Process seam:** reading the first 120 lines of a detector run and calling it the audit is itself a break. The finish scan is read in full, always.

Also repaired in the same pass, not counted as seams because no reader could have hit them:
44px minimum touch targets on the wager buttons and label; `aria-pressed` on every toggle;
`aria-live` on the score and the instrument readout; `aria-valuetext` on the dial; form controls
inherit the page type (the range input had resolved to Arial); `::selection`, caret, and
scrollbar themed from the palette; tabular numerals on every measurement.

## Earlier seams on the same family, booked retroactively

| Date | Surface | Break | Repair | Guard |
|---|---|---|---|---|
| 2026-09-11 | `_ARTIFACTS/postmortem-manufactured-role.html` first cut | Re-authored the ARCS palette by copying a sibling HUD's `--palette-*` block; one palette in four places, two vocabularies | Rebuilt on `_tokens.css` verbatim plus five kit primitives; one net-new primitive added to the kit as a `@dsCard` file | `scripts/token_source_gate.py` in pre-commit (blocks new pages; legacy HUDs warn under ratchet) |
| 2026-09-11 | NFTT chrome vs kit | Token values drifted (surface, text, muted) between the essay template and the kit | Reading layer tokens (`--surface-reading`, `--text-reading`, `--muted-reading`, `--cyan-dim`, `--redact`, `--border-2`) added on top of `_tokens.css` in the TIL page; the kit file itself not yet changed | backlog: promote the reading layer into `_tokens.css` via `/design-sync` |
