# counterpart-onepager: the Brooks one-pager, rebuilt from the kit

The Brooks audit one-pager is now a template plus a data file. `brooks.json` holds every word; the
`counterpart-onepager` template (src/ui-kit/templates.json) and `scripts/counterpart_onepager_build.py` hold the
shape. Rebuild with `python3 scripts/counterpart_onepager_build.py`; `--check` fails when the page and its data
disagree. Never hand-edit `_ARTIFACTS/brooks-audit-onepager.html`.

Parity: the rebuilt page against the hand-built one (copied 2026-11-04 15:27 from the contract-work worktree),
full-page Chrome screenshots at 1280, 790 and 375 px, dark and light: 0 differing pixels at every width, and the PNGs
were byte-identical (`parity/diff.json` keeps both hashes). The visible text matches character for character
(5,801 characters) and the body markup is unchanged. Only the CSS was regrouped by part, and four unused rules were
dropped (`.scoremeta`, `.qa` and its children, `.proof`, `.hrow .ref`).

## Inventory: each section against the kit

| Section | Kit parts | Net-new shape | Second real case? | Fate |
|---|---|---|---|---|
| Hero | 29 tile, 28 chip | Title, serif verdict, aside | Same roles as the candidate-brief hero | Page roles in the template |
| Adobo case | 24 segmented control | Case switcher: radios drive panels, pure CSS | None found (no other `:checked ~ .panels`) | Candidate |
| Every section head | none | Headline-plus-deck lockup | None (`.deck` elsewhere is a sticky nav bar) | Candidate |
| What I heard | none | Heard/check paired-row grid, phone prefix | None (no other "You said" grid) | Candidate |
| Getting started | 08 receipt table, adapted; 33 led; 32 evidence ref | Sans-value receipt rows | Partial: postmortem-manufactured-role has `.td-val.prose`, but at 12.5px in `#94a3b8`, not body size in `text` | Candidate; promoting it means choosing which values win |
| Three questions | none | Question-and-answer card (h3 and a paragraph each) | None searched | Candidate (added 2026-11-05 with the Nov 5 copy; the Getting started table above left the page then, its CSS stays for the next page) |
| One question | 31 callout | Callout with a step-size paragraph | n/a | Page override |
| Full checklist | none | Depth checklist (details + numbered criteria, added items in gold) | Not searched beyond this page family | Candidate |
| Header button | none | Theme toggle | Yes: the myally family (public/myally*.html), same button, saved choice, light remap | **Promoted: 39** |
| Header button, icon form | 39 theme toggle | Sun and moon icon button over 39's toggle logic | None (Brooks only) | Candidate (2026-11-05) |
| Print | none | US Letter print block, 2 pages, checklist opened for print | None searched | Candidate (2026-11-05); sizes and gaps derive from the screen tokens |
| Storyboard sign-off | none | ARCS Field OS wordmark | Yes: public/honest.html, identical markup | **Promoted: 38** |

Promoted as specimen pages (spec in `src/ui-kit/specimens/`, built by `scripts/kit_specimen.py`):

- **38 Wordmark** (atom). `@prim` block taken from the storyboard, with the kit's mono token in place of the page
  alias. The storyboard now embeds it. honest.html keeps its own copy (13px, `--dimmed`); it can embed the block
  when someone next touches that page.
- **39 Theme Toggle** (molecule). `@prim` block (light remap, button, print) plus the head and tail scripts in the
  spec; the generator fills in the storage key per page. The one-pager now embeds it. The myally pages keep their
  `--pg-*` palette, so the spec says to leave them as they are.

## Storyboard frames at the video kit levels

Levels from `_PATTERNS/2026-10-30-readme-to-video-resonance-rules.md`: frame = atom in time (already an organism in
space), clip = frames timed to one take, throughline = one claim, arc = order of throughlines, full video = page.

| Frame | Space parts | Page source in brooks.json | Clip (take) |
|---|---|---|---|
| Opening | 38 wordmark, horizon line (candidate) | none | silent 1.5 s |
| Beat 1 | title + serif lede (the hero lockup at video scale) | `hero.title`, `hero.verdict` | voiced |
| Rungs 1 to 3 | Breadcrumb chain with drawn SVG arrows (candidate) | section headings, as rungs | silent 1.2 s each |
| Beat 2 | Stat line (candidate), turn: claim, arrow, outcome (candidate) | `sections[1].rows[0]`, `hero.aside` | voiced |
| Beat 3 | 24 segmented control (static `.on` state), record lines (candidate) | `sections[0]` case 1 | voiced |
| Beat 4a | Now/Next/Later rail (candidate) | receipt rows "What you get", "After" | voiced |
| Beat 4b | 29 tiles, 28 chip, 31 callout | `hero.tiles`, `hero.chip`, `ask` | voiced |
| Closing | chain with final rung, ask headline, reply chips (candidate), 28 chip, signature with 38 wordmark | `ask`, `sections[0].cases[].label`, `footer` | silent 4 s |

- Throughlines: four, one per rung (What I heard, What I'd check, What you get, Your call). Each throughline
  carries one claim and its frames.
- Arc (template): the rung order. It matches the page's section order, apart from the ask, which the page puts last.
- Full video (page): this arc filled from brooks.json. The storyboard copy is still hand-placed; making frames read
  brooks.json is the next step if a second counterpart video comes.

Searched and not a second case: the crumb on public/todd-logictree.html (a sticky nav bar with text separators),
`.rail` on the observatory and forge pages (no Now/Next/Later shape), `.opt` on todd-logictree (a list item).


## Outcome fields (2026-11-09)

The data file may carry an `outcome` block. It is never rendered. It names the backlog job the page serves and maps
each claim the page makes to the parts and data paths that carry it (`kit:NN-slug`, `candidate:<shape>`, `page:hero`).
`--check` refuses a block whose job row is missing, whose part or data path does not exist, or that leaves a
rendered block unclaimed. `--receipt` prints an ex-ante `decision_receipt` template: one unconfirmed line per
claim, the claim-to-part map in `refs`, and the backlog row's fates as the outcomes to score at close. Judgment
fields stay `<REQUIRED ...>`, and the script writes nothing.

Why: a part's second real case should be a second closed outcome on the same job, not a second page with similar
CSS. With claims keyed to parts, a close can say which part carried the claim that landed or missed. With only a
few counterparts so far, any score is a count, not odds.
## Gates

Pass: `counterpart_onepager_build.py --check`, `component_source_gate` (one-pager on counterpart-onepager, 8
signatures; 38 and 39 on kit-specimen), `token_source_gate`, `inline_token_sync --check`, `kit_primitive_sync --check`,
`kit_specimen.py --check`, `kit_pull.py manifest --check`, `page_gate --counterpart` on the one-pager, `page_gate` on
the storyboard and both specimens, Impeccable detector at 0 on the one-pager and both specimens.

Seams:
- `kit_primitive_sync --check` failed on main before this change: it held every kit `@prim` block against
  phosphor.html, so molecules 27 to 37 (which are not Phosphor's) always failed. The pre-commit hook only runs it for
  21 to 26, so nobody noticed. Fixed here: phosphor is checked only for Instrument Lab blocks, and every page that
  marks a block is checked against the kit. A kit rule the page never uses may be left out; public/good-audit-check.html
  leaves out the unused `.section-label` line. The check was shown to fail on a broken block before it was trusted.
- Storyboard: 1 Impeccable finding (`tight-leading`, 1.25) was there before this change too. It is on display-size
  frame lines (`.what`, `.v-stat`), so it is waived for this file only, not fixed: the storyboard's type is the original
  session's call.
- Design-debt ratchet: the first commit of the one-pager counted 13 findings against 0 at HEAD, because the page was
  new to git. All 13 were on the hand-built page already. 10 are the kit 39 light palette, a deliberate second palette,
  so `design-system-color` is waived for the one-pager and the 39 specimen (the brand profile already exempts it).
  3 are page font sizes off the DESIGN.md ramp: tile values at 1.6rem (1rem on a phone) and phone segment labels at
  0.85rem. They are waived for this file only and not repaired, because changing them would break the 0-pixel parity.
  To repair: move the three sizes onto ramp tokens in the generator, rebuild, re-shoot parity, and delete the
  font-size waiver in `.impeccable/config.json`. This seam belongs in `_PATTERNS/kintsugi-visual-grammar-seams.md`,
  but that file now fails the citation gate on any edit: it links 7 pages that PR #2025 retired.
