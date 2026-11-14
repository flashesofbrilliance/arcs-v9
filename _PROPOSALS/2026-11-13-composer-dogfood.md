---
title: Composer dogfood, the arrangement share on one cold render
date: 2026-11-13
seed: seed-atomic-composer (oracle seed 19)
backlog: composer-dogfood
verdict: 32% arrangement share (n=1, rule says build); throwaway reorder prototype built; seed stays HELD
---

# Composer dogfood: how much of a brief is arranging?

## Why
Seed 19 (`_PROPOSALS/2026-11-13-seed-atomic-composer-idea-loop.md`, on PR 2225) left one claim standing: a
block-sequence editor for the tabbed brief could halve the option-board time. Loki's objection was that the time
goes to copy, not arrangement. Neither side had a minute of measurement. This run measures one brief before
anything bigger gets built.

## The rule, pre-registered
Written into the `composer-dogfood` backlog row and committed (53bca6bf) before the first change was timed:
arrangement share = minutes spent choosing block order and block type ÷ total minutes on the page. Under 20%
composts the composer and the option board stays the method. 20% or more earns one throwaway prototype.

## The subject
Zach first picked `gravity.json`, then switched (relayed from the seed session, confirmed by him) to a **cold render
for Louisville**: a new tabbed brief built from the Louisville SSOT, so choosing blocks is real work, not a re-edit.
The Gravity round was dropped before any change was logged. The draft is `_ARTIFACTS/tabbed-brief/louisville-cold.json`.
It is a private draft: nothing went to the counterpart, and it needs the PII and gauntlet checks before any publish.

## The log
| # | Tag | Who | From | To | Seconds |
|---|---|---|---|---|---|
| 1 | ARRANGE | Zach | 12:14:30 | 12:16:10 | 100 |
| 2 | COPY | agent drafts v0 into the skeleton | 12:16:10 | 12:16:34 | 24 |
| 3 | (review, no change asked) | Zach | 12:16:34 | 12:19:41 | 187 |

Change 1 was the skeleton: three skeletons rendered side by side as previews (audit-first, question-first, one tab),
Zach picked A. He then reviewed v0 and ended the round ("Round done") with no change asked.

## Result
- Zach's minutes on the page: 311 seconds. ARRANGE: 100 seconds. **Share: 32%**, over the 20% line.
- Counting the agent's drafting time in the total gives 100 / 311 = 32% either way. The review step has no tag, so it
  sits in the denominator only.
- By the rule, the result earns the throwaway prototype, which was built (below).

## Why this does not settle the seed (held, not reconciled)
- **n = 1, and the most favourable case.** A cold render with zero copy rounds is where arranging is the biggest share
  of the work. The Gravity history, 48 of 65 commits copy, shows where a real brief's time goes once it is iterated.
  Loki's objection stands until a brief with copy rounds is timed.
- **The baseline is already short.** The arranging took 100 seconds, through a three-option picker. Seed 19's bar was
  "half the option-board time", so a composer would have to save about 50 seconds on a brief like this one.
- **Reorder rarely has anything to act on.** In `gravity.json`, 16 of 18 block slots hold one block. Louisville v0 has
  2 slots with 2 blocks. The choice that cost time was block type and tab layout, not order within a slot, and the
  prototype does not touch block type.

## The prototype (throwaway, scoped to the rule)
- `scripts/page_tune.py`: an RFC 6902 `move` op, limited to a reorder inside one array; moves run after every replace
  and add, because text pointers name the pre-move order. Self-test covers order and the cross-array refusal.
- `scripts/tabbed_brief_build.py`: in a `--tune` build only, each block in a slot with 2 or more blocks is wrapped in
  `<div data-blk="/slot/blocks/N">`. The public build is byte-identical to before (checked with `cmp` on Gravity).
- `src/ui-kit/token-tuner.js`: under `?edit`, up and down buttons on each `data-blk` block; each swap records a move,
  and Copy JSON lists the moves after the text replaces.
- **Proven:** an export of that shape (one text replace on a block, then two moves) applied with
  `tabbed_brief_build.py --apply` to a copy of the Louisville JSON, gave the expected order and edit; the result
  validates and builds with no hand edits.
- **Not proven:** the click path in a browser. The browser pane opened the local file as a snapshot without its
  `?edit` query, and serving it on localhost was refused, so the buttons were not clicked in a live page.

## Next
Hold the seed. Time two more briefs, each with at least one copy round, under the same rule before any further
composer build. If the share stays at 20% or more with copy included, the next build is a block-type swap, not reorder.
