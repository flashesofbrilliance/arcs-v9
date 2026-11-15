---
title: "The unattended door: what mechanizing ARCS protocols actually changed"
version: v1 (I.D.E.A. pass 2 draft)
date: 2026-11-15
status: PROPOSAL. Nothing here is wired. Fates and rule changes are Zach's.
evidence: facts.md in this folder (F1 to F28, seams S1 to S13)
---

# The unattended door

## Bottom line

ARCS does a step when the step falls due at a moment someone is already standing there. It drops the step when the step falls due later, after everyone has left the room.

Receipts get filed on 98% of merges and rows get closed on 73% of merged PRs, though no tool performs either act: the merging session is present when they fall due. Ripe rows, receipt outcomes, dated bets and counterpart sends fall due days later, when no session is present, and they close at roughly zero.

The fix is not another detector. ARCS already has the detectors, and it has measured this gap at least three times. Each time the fix was filed as one more later step, and it decayed the same way. The fix is to move each later step into a moment that already happens, or to stop storing what can be computed.

## The evidence

Each row is one protocol step, measured on full history (origin/main 3f9b9f9, unshallowed).

| Step | When it falls due | Who is present then | Done | Source |
|---|---|---|---|---|
| File a decision receipt for a merge | at the merge | the merging session | 310 of 316 PRs since 11-01 (98%) | S10 |
| Set a row DONE after its PR merges | at or near the merge | the merging session | 99 of 136 rows citing a merged PR (73%) | S10 |
| Pass pre-commit gates | at the commit | the committing session | every commit (hard block) | F18 |
| Promote a row whose dependencies cleared | whenever the last dependency closes | nobody | 0 of 19 eligible (HOLDING 8, OPEN 11) | S5 |
| Act on a review_by date | on the date | nobody | 36 rows past due, oldest 10-25 | F7 |
| Record an outcome on a compass receipt | days after the decision | nobody | 5 real of 277 (1.8%) | F16 |
| Score a SessionReceipt bet | on its scoreBackDate | nobody | 0 of 4 past due | F16, n=4 renders grain |
| Resolve a decision receipt's unconfirmed lines | later, when the world answers | nobody | 1,657 of 1,683 carry open lines; 0 resolved as of 10-18 | F15, S8 |
| Send a drafted counterpart note, then score its bets | after Zach sends | Zach, outside any session | Harrison 6 days late; Brian, MyAlly, Louisville, PRL dates passed; 5 artifacts carry bets, 1 has a scoring row | F21, F22 |

The counterexample worth keeping: LaneOutcome closes 2 of 2 (n=2, grain). Whether they were closed in the session that produced them is unverified; if so, they fit the reading.

## The recursion

The gap is not new. It has been found and filed, and the filing decayed.

1. 2026-10-17: outcome closure measured at about 1.1% (`_PATTERNS/2026-10-17-claims-versus-proof.md`).
2. 2026-10-18: `receipt_outcome_queue.py` built; 834 of 854 receipts carried open lines, none resolved.
3. Row `outcome-capture-rate-keel-gap` closed DONE with the verdict "not a build gap, humans are not closing the loop".
4. Row `echo-scheduled-receipts`, which would have fired the nudge at the right moment, was COMPOSTED on 11-05 because nobody moved it.
5. Row `backlog-fate-triage-2026-10-18`, built to put ripe rows in front of Zach, has been READY for four weeks.

A detector with no reader at the due moment is a later step. A later step decays. So does any fix shaped like one.

## What this is not

These readings were tested and died. They stay here as repaired seams.

- **"Protocols are followed in proportion to how much the tool does."** Killed. Close-on-merge has no tool and runs at 73%. `safe_merge.sh` does not write receipts ("Not written by this script", line 241); sessions do, and 20% of receipts came through other tools.
- **"58% NCI:SKIP is avoidance."** Killed. SKIP is sanctioned for docs and chores (ADR-035:57-61). On full history SKIP is 78%; at most 8% are candidate violations and 38 carry no reason.
- **"Integration tax is compounding."** Withdrawn. Sync-from-main merges track merge volume (W43 46, W46 81), spiky rather than rising.
- **"12 of 96 gates only test themselves."** Withdrawn. Only `backlog_ripeness` and `open_loops` are verified self-test-only.

## Induced backlog

Ranked by leverage per unit of effort. "Door" is two-way (reversible) or one-way. Each row names the existing rows it must not duplicate.

| # | Row id (proposed) | What it does | Evidence | Door | Do not duplicate |
|---|---|---|---|---|---|
| 1 | `ripeness-reads-state` | `backlog_ripeness.py` reads the `state` enum, never `status_note`; add a self-test fixture with a DONE row whose note does not start with a terminal word | S5: 36 terminal rows not skipped, 3 live rows skipped | two-way | none |
| 2 | `backlog-derived-state` | READY-by-dependency and DONE-by-merged-PR are computed at read time in `backlog_graph.py`, `open_loops.py` and `scrum.py`; stored state keeps only human states (HELD, COMPOSTED, SUPERSEDED, fates); `backlog_status_check.py` warns when stored contradicts derived | S5 (19 rows), S10 (37 open rows cite a merged PR), 2 to 8% of PRs are bookkeeping | two-way, but it changes a rule | `backlog-fate-triage-2026-10-18`, `scrum-master-ritual` |
| 3 | `groom-reads-ripeness` | the groom agenda lists HELD rows whose resume trigger fired (5 today) and rows past review_by (36) | F20: `scrum.py` has no ripeness input | two-way | `backlog-fate-triage-2026-10-18` (fold into it) |
| 4 | revive `echo-scheduled-receipts` | the close-time prompt rides a moment that already happens: the weekday morning note (`arcs-open-loops-morning-note`) and session start list what falls due today (SessionReceipt scoreBackDate, dated bets, rows whose note says "Zach sends") | F16, F21, F22, S8 | two-way | `universe-outcome-capture`, `receipt-real-interview-closes`, `harrison-recoil-close-score` |
| 5 | `ex-ante-bets-to-ledger` | dated probabilities written on artifact pages are filed as SessionReceipt rows with a scoreBackDate when the page is built, so row 4 can see them | F22: 5 artifacts carry bets, 1 has a row | two-way | none found |
| 6 | `history-tools-refuse-shallow` | scripts that count git history (`receipt_coverage.py`, night-moves, `prior_art`, any weekly count) exit non-zero on a shallow clone unless `--allow-shallow` | S10: this pass undercounted by 60 to 87% before the skeptic caught it | two-way | none |
| 7 | `shared-page-secret-sweep` | one pass over shared and pinned artifacts for passcodes in page source and personal contact lines; extend the recoil share gate pattern | F28 | two-way to sweep; rotating a passcode is one-way | `recoil-public-share-gate` (recoil pages only) |
| 8 | `first-dollar-price-anchor` | price the audit, add one payment link, verify the CTA hop | F24: named in 3 artifacts, no executing row | one-way (public price) | `paid-brief-first-dollar`, `agent-receipts-audit-first-conversion` |

Cut on purpose: an NCI reason gate (38 commits, low value); a new handoff-staleness detector (it would be one more later step; run the molt instead); regenerating stale pinned snapshots (unpin or archive them by hand).

## Ripe now

By the status spec's own definitions these 19 rows already meet READY. Graduating them is bookkeeping, not a fate.

- HOLDING (8): agent-receipts-audit-first-conversion, merge-train-only-path, receipt-real-interview-closes, jtbd-graph-s5-feedback, cia-recoil-close-michael-intro, recoil-kairos-7s-test, recoil-ship-twin, seat-binding-design-log
- OPEN (11): doc-gate-false-positive-cleanup, cia-technical-screen-prep, rfp-ship-resume-tailor-rebase, rfp-ship-engine-branch-reconcile, librarian-apex-spine-tier-class, card-catalog-q4-rerun-with-receipts, token-tuner-why-prompt, compounding-model-prereg, session-overlay-recurring, recoil-skills-on-runner, open-loops-ssot-drift-line

`recoil-kairos-7s-test` is the last dependency in front of `recoil-brian-acceptance`.

## Decisions for Zach

1. Approve row 2's rule: READY and merged-PR DONE become computed, not written.
2. Resume or keep holding the 5 HELD rows whose triggers fired: rc-ops-001-graduation-ruling, asm-003-cold-molt-decided, compass-anti-distillation-build, hud-evidence-grain-d4, oracle-sync-namespace.
3. The sends only you can make: the Harrison follow-up, the Brian note, the MyAlly agreement's 23 pending suggestions.
4. The stranded decisions: 7 debt-tracker items aged about 40 days, two past their own deadlines.
5. The price for row 8.

## Method

Two passes per ADR-086. Pass 1 mined the backlog, git and the receipt ledger in the shell and read 19 pinned artifacts through one agent. Pass 2 put the fact sheet before the I.D.E.A. seats (Alchemist, Librarian, Detective, Curator) and the Staff of Chiefs (Loki, Bayesian), plus Grug and the claims skeptic. Two pre-registered kill lines ran; one fired. Five facts broke and were repaired in view (S1 to S13). The deepest break was the analyst's own: a shallow clone.
