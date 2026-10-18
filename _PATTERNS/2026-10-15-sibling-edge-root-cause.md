# Debug report: why the wrapping bug survived banked memories and gates (sibling edge)

Date: 2026-10-15. Method: the engineering plugin's debug flow (reproduce, isolate, diagnose, fix, prevent), with DOM measurement, not by eye.

## Reproduction

- **Expected:** every block in the page lane of `_ARTIFACTS/raw-capture.html` ends at the same right edge at 1280px.
- **Actual:** at 1280px the hero, instrument, readouts and note end at x=1193 (a 1120px lane). The altitude cards and footer end at x=795 (722px). That is a 398px dead right gutter on one page. At 790px the shortfall is 36px.
- **Introduced by:** my own change to satisfy a failing pre-commit gate (`scripts/card_gutter_check.mjs`), which printed "the card carries the measure". I set the card container to the 680px measure plus padding.

## Root cause

Three causes, all in the rules and not only in the instance.

1. **The banked remedy is not safe to apply recursively.** The memory `text-wrapping-defect-class-and-gate` fixes mode 4 (narrow measure inside a wide container) by making the container's inner width equal the measure. `card_gutter_check.mjs` prints the same remedy. Applied to a card in a wider lane, it produces mode 4 again one level up, between the card and its siblings.
2. **No gate compared a block with its siblings.** `card_gutter_check.mjs` compared text with its card. The hero lede check in `scripts/page_gate.py` compared a lede with its heading. The text-in-card gate even excludes blocks "whose parent is itself narrower than the card" as the layout's choice. A card narrower than its lane siblings is in neither check.
3. **A recurrence was left ungated.** The 2026-09-14 recurrence note in the memory `design-full-width-lede-matches-heading` says no new gate was proposed and the standing rule stands. `_PATTERNS/2026-09-08-frustration-gate-pattern.md` and AGENTS.md gotcha 15 say a recurring class gets a mechanical check by round 2.

Contributing process failure: I viewed the page only in a narrow pane, where card and lane edges coincide, and never at 1280px, which the memory calls for.

## Fix

- `_ARTIFACTS/raw-capture.html`: the cards and footer now fill the lane, per the standing full-width preference.
- `scripts/card_gutter_check.mjs`: a second check, sibling edge. A substantive flow block (bordered card or multi-line text) that ends more than 24px short of its widest sibling fails at 790px and 1280px. Excluded: children of grid or flex rows, full-bleed siblings, centered blocks, inline and tiny blocks. Opt out with `data-lane="narrow"` (index pages keep `data-measure="index"`).
- A first version guessed a lane and was wrong. Sampling 5 of its first 18 flags found 3 false positives (a centered `.wrap` under a full-bleed header, and rows in a side panel). It was rewritten to compare siblings only; the same 3 pages then passed and the 2 real ones still failed.
- First version of the sibling check also missed the incident cards because it skipped every flex parent; found by running the check on the pre-fix file, then fixed to skip only row-direction flex and multi-column grid.

## Prevention

- Fail-on-bad and pass-on-good: `node scripts/card_gutter_check.mjs --selftest` now covers `tests/fixtures/card-gutter/bad-lane.html` and `good-lane.html` as well as the original pair.
- The incident file (`git show` of the pre-fix page) fails the check at both widths with the 398px figure, and the fixed page passes.
- Corpus measurement and the decision on blocking versus warning are recorded in the section below.

## Corpus measurement (2026-10-15)

Pre-registered kill: if the check flags more than 30 percent of existing pages, it is too noisy and stays warning-only.
- Run: `scripts/card_gutter_check.mjs` over `_ARTIFACTS/*.html` and `public/*.html`, 214 pages, 790px and 1280px.
- Result: 25 of 214 flagged (11.7 percent). Kill not met. The check blocks only newly added artifacts and public pages in the pre-commit hook, so the 25 existing pages are not blocked.
- Hand classification of 6 flagged pages: 3 clear defects (a subtitle or lede capped far short of its siblings: `_ARTIFACTS/arcs-tao-alchemist.html`, `_ARTIFACTS/pitch-us-bundle-ia.html`, `public/good-case-six-week-outage.html`); 1 index page that needs the `data-measure="index"` opt-out under the 2026-09-29 exception (`public/good-series-lore.html`); 1 borderline 60px gap (`public/saul-followup.html`); 1 deliberate editorial breakout where the hero sits on the measure and the figures run wider (`public/blog-nftt-receipts-or-it-didnt-happen.html`). Roughly 5 of 6 were true or marker-fixable. One was a design choice the gate cannot tell from a defect, so it needs the opt-out.
- Limit: a sample of 6, not the full 25; the other 19 were not read.
- The 25 existing pages are queued in `_QUEUE/induced-backlog.jsonl` as `lane-edge-existing-25`.
