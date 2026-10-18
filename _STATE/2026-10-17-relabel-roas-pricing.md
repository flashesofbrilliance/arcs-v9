# Relabel draft: ROAS guarantee and pricing tiers (DRAFT DIFF, canon NOT edited)

Patch: `_STATE/2026-10-17-relabel-roas-pricing.patch` (20 insertions, 6 modified lines, 4 files). It applies cleanly to origin/main (`git apply --check`). Apply on a branch with `git apply _STATE/2026-10-17-relabel-roas-pricing.patch`; nothing in `_CANON` has been changed by this PR.

## What the patch does

It adds labels only. Every number stays; striking is a separate call for you.

| Where | Edit |
|---|---|
| Litepaper 333, Canon v1.1 842 and 3349, YellowPaper 57 | append "[Unvalidated target: asserted threshold, no control group; see Technical Overview Part III.]" |
| YellowPaper 390 | append "[Unvalidated: no guarantee terms have data behind them ...]" |
| Litepaper 455, Canon v1.1 916, YellowPaper 589 | add a Status line: "Design intent, not an offer ... do not quote it to a counterparty." (YellowPaper's goes above the Guarantee Structure code block, not inside it) |
| Canon v1.1 3399 | add a Status line flagging that the refund trigger here differs from the improvement-or-refund form elsewhere |
| Litepaper 413, Canon v1.1 881, YellowPaper 513 | add a Status line under each tier table: illustrative pricing, accuracy figures unvalidated, tier gap derives from them |
| White Paper 312 | append "[Unvalidated: not audited in Technical Overview Part III, no data in the repo.]" |

No new numerals are introduced, so the claims report is unchanged by the patch (70 UNVALIDATED, 848 UNCOVERED, checked with the patch applied).

## Inconsistencies found while drafting (not fixed, for you)

1. Two incompatible guarantee definitions: "improvement of the stated ROAS threshold or full refund" (Litepaper, Canon v1.1 916, YellowPaper 591) versus a refund when campaigns underperform baseline by more than a set margin (Canon v1.1 3399). The White Paper has a third: a doubling or money back.
2. The tier accuracy figures differ by document: single values in Canon v1.1 and the Litepaper, ranges in the YellowPaper, and the quoted performance gap differs too.
3. The same price appears for two different things: the top "Enterprise" subscription tier and the "Full" data-contribution tier in Canon v1.1 are both $2.5M.
4. Both guarantee forms depend on receipt attribution that the Technical Overview marks as asserted, and the product is described there as pre-commercial.

## Not touched

Dollar prices (plans, not claims), the remaining mentions of "performance guarantee" in prose (Litepaper 623, 672, 686, 697; Canon v1.1 115, 159, 212, 224, 925, 3664; YellowPaper 603 to 618, 756, 815), and any wording of the product's own copy. The labels at the three headline spots and at each definition should be enough for a reader to see the status wherever the figure is stated.

## Decisions for you

1. Apply the labels as drafted, or change the wording (for example "Unvalidated target" versus "Design intent").
2. Pick the one canonical guarantee form (or none) so the others can be struck.
3. Whether the prose mentions listed under "Not touched" get a label too.
