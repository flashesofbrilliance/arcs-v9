---
title: "The unattended door: what mechanizing ARCS protocols actually changed"
version: v2 (I.D.E.A. pass 3 draft)
date: 2026-11-15
status: PROPOSAL. Nothing here is wired. Fates and rule changes are Zach's.
evidence: facts.md in this folder (F1 to F28, seams S1 to S16; seams supersede the F lines they name)
baseline: origin/main 3f9b9f9, full clone. Main has since moved to c246b66e (#2274, a docs-only handoff molt, not reviewed here); the backlog file is unchanged.
---

# The unattended door

## Bottom line

ARCS can schedule detection. It cannot schedule judgment.

A mechanical step that falls due later gets done when a scheduler owns it: six cron workflows ran about 151 times on their due dates with nobody present. A step that needs judgment gets done only when it falls due at a moment someone is already acting. Receipts are filed for 98% of merges because the merging session is there. Ripe rows, receipt outcomes, dated bets and counterpart sends fall due later, and they close at roughly zero, even when a report puts them in front of a reader.

ARCS has measured this gap at least three times. Each fix was filed as one more later step, and it decayed the same way. The repair is to put each judgment step inside an act that already happens, the way pre-commit sits inside the commit, and to stop writing by hand what can be computed.

## The evidence

| Step | Falls due | Present then | Done | Source |
|---|---|---|---|---|
| File a decision receipt for a merge | at the merge | the merging session (acting) | 310 of 316 PRs merged since 11-01 (98%) | S10 |
| Set a row DONE when its PR merges | at the merge | the merging session (acting) | 99 of 136 rows that cite a merged PR (73%) | S10 |
| Pass pre-commit gates | at the commit | the committing session (acting) | blocks wherever the hook is armed; bypassable with --no-verify and absent on GitHub-side merges | F18 |
| Run a scheduled check | on its cron | a scheduler | about 151 scheduled runs across 6 workflows, mostly green | S14 |
| Fix what a scheduled check found | after it goes red | nobody | no-squash red 10-11 to 10-14, no fix inside the streak | S14 |
| Promote a row whose dependencies and trigger cleared | when the last one clears | a reader: the morning note already lists ripe rows | 0 of 10 structurally ripe rows promoted | S15 |
| Act on a review_by date | on the date | nobody | 36 rows past due, oldest 10-25 | F7 |
| Record an outcome on a compass receipt | days after the decision | nobody | 5 real of 277 (1.8%) | F16 |
| Score a SessionReceipt bet | on its scoreBackDate | nobody | 0 of 4 past due (n=4, grain) | F16 |
| Resolve a receipt's unconfirmed lines | when the world answers | nobody | 1,657 of 1,683 carry open lines; none resolved as of 10-18 | F15, S8 |
| Send a drafted counterpart note, then score its bets | after Zach sends | Zach, outside any session | Harrison follow-up 6 days late; Brian, MyAlly, Louisville and PRL dates passed; 5 artifacts carry bets, 1 has a scoring row | F21, F22 |

Reading is not acting. The morning note already prints the ripe rows (`open_loops.py:223-233`), and nothing moved.

## The recursion, in three lines

On 10-17 outcome closure was measured at about 1.1%, and on 10-18 `receipt_outcome_queue.py` found 834 of 854 receipts with open lines and none resolved. The row that would fire the nudge at the right moment, `echo-scheduled-receipts`, was composted on 11-05 because nobody moved it. The row built to put ripe rows in front of Zach, `backlog-fate-triage-2026-10-18`, has been READY for four weeks.

## What died on the way

Kept as repaired seams, so the next pass does not rebuild them.

- **"Followed in proportion to how much the tool does."** Killed. Close-on-merge runs at 73% with no tool at the moment. `safe_merge.sh` prints the receipt and never writes it (line 241). `backlog_ripeness.py --apply-closes` can close rows, and did close 6, but only when someone ran it.
- **"Steps that fall due later are dropped."** Narrowed. Cron jobs do later steps; the response to what they find is what decays.
- **"58% NCI:SKIP is avoidance."** Killed. SKIP is sanctioned for docs and chores (ADR-035:57-61). On full history SKIP is 78%; about 8.5% are candidate violations; 36 carry no reason.
- **"Integration tax is compounding."** Withdrawn. Sync merges track merge volume (W43 46, W44 15, W45 21, W46 81).
- **"12 of 96 gates only test themselves."** Withdrawn. Two are: `backlog_ripeness` and `open_loops`.
- **"19 ripe rows are bookkeeping."** Withdrawn. The status spec needs the trigger fired as well; 10 qualify.
- The analyst's own break: the first counts ran on a shallow clone and undercounted history by 60 to 87%.

## Induced backlog

In order. Door is two-way (reversible) or one-way.

| # | Row id (proposed) | What it does | Evidence | Door | Do not duplicate |
|---|---|---|---|---|---|
| 1 | `ripeness-reads-state` | `backlog_ripeness.py` reads the `state` enum, never `status_note`; a cleared dependency no longer overrides a trigger that names a human event; self-test fixtures for both | S5: 36 terminal rows not skipped, 3 live rows skipped; S15: OR-joined clauses ripen `cia-recoil-close-michael-intro` | two-way | none |
| 2 | `backlog-derived-ready` | READY is computed at read time, never written, for rows whose trigger is structured (a dependency, a date, a PR) and whose door is two-way. One shared function, imported by every reader of `state`; a pre-commit check lists those readers; a stored-vs-derived contradiction blocks on changed rows. DONE stays a human act, offered as a groom suggestion from an explicit `closes_pr` field | S15, S16: derived DONE from prose would have marked `recoil-kairos-7s-test` done from PR 2173 and surfaced a counterpart send as ready | two-way; changes a rule | `scrum-master-ritual` |
| 3 | amend `backlog-fate-triage-2026-10-18` | the groom agenda lists HELD rows whose dependencies cleared, with the human trigger each still needs, and rows past review_by | F7, F20: `scrum.py` has no ripeness input | two-way | it is the existing row |
| 4 | `act-time-bet-gate` | before `/recoil-prep`, `/precall-page` or `/recoil-ship` acts on a counterpart, it lists that counterpart's due bets and unsent drafts and asks for each to be scored or deferred with a date; the skill proceeds either way, but it records the choice | thesis: put the judgment inside the next act; F21, F22; the morning note already failed as a reading moment | two-way | `harrison-recoil-close-score`, `universe-outcome-capture` |
| 5 | `ex-ante-bets-to-ledger` | dated probabilities on artifact pages are filed as SessionReceipt rows when the page is built, so row 4 has them to list | F22: 5 artifacts carry bets, 1 has a row | two-way | none found |
| 6 | `history-tools-refuse-shallow` | scripts that count git history exit non-zero on a shallow clone unless given `--allow-shallow` | S10 | two-way | none |

Cut on purpose: a morning-note nudge for outcomes (a reading moment, already shown to fail); a handoff-staleness detector (one more later step); an NCI reason gate (36 commits); regenerating stale pinned snapshots (unpin them instead). Two rows moved to decisions: the secret sweep (live exposure, not backlog leverage) and the price anchor (a one-way public price).

## Ripe now

Ten rows have every dependency DONE and a structured trigger that fired, and none is a one-way door: `recoil-kairos-7s-test`, `recoil-skills-on-runner`, `jtbd-graph-s5-feedback`, `doc-gate-false-positive-cleanup`, `rfp-ship-resume-tailor-rebase`, `rfp-ship-engine-branch-reconcile`, `librarian-apex-spine-tier-class`, `card-catalog-q4-rerun-with-receipts`, `session-overlay-recurring`, `open-loops-ssot-drift-line`.

Four more have dependencies done but wait on a human or outside event: both `cia-*` rows (a call not yet booked), `token-tuner-why-prompt` (Zach using breadcrumbs on a real page) and `seat-binding-design-log` (a pick log landing).

`recoil-brian-acceptance` waits on two rows: `recoil-kairos-7s-test` (ripe) and `recoil-brian-ssot` (READY, unclaimed).

## Decisions for Zach

1. **Secret sweep, now.** Passcodes sit in page source on two pinned artifacts (one client-side, one inline) and contact details in a link-shared pitch footer (F28, agent-read, unverified here). Rotating a passcode is one-way.
2. **Send the Harrison follow-up.** It is six days late and its scoring check is due 11-16.
3. **Approve row 2's rule:** READY is computed, not written, under the conditions in the table.
4. **Claim `five-person-outcome-test`.** It has been READY and unclaimed for 11 days, and three HELD rows wait on it (`rc-ops-001-graduation-ruling`, `asm-003-cold-molt-decided`, `hud-evidence-grain-d4`). The other two HELD rows wait on your own word: WRITE-LOCK 1 for `compass-anti-distillation-build` and a new oracle namespace for `oracle-sync-namespace`.
5. The other sends only you can make: the Brian note and the MyAlly agreement's 23 pending suggestions.
6. The 7 debt-tracker decisions aged about 40 days, two past their own deadlines.
7. A price for the audit, if you want the first-dollar row back.

## Method

Two passes per ADR-086 (DRAFT). Pass 1 mined the backlog, full git history and the receipt ledger in the shell, and read 19 pinned artifacts through one agent. The I.D.E.A. seats (Alchemist, Librarian, Detective, Curator), the Staff of Chiefs (Loki, Bayesian, Conductor), base and worst scenario runs, Grug and the claims skeptic attacked the fact sheet and then this draft. Two pre-registered kill lines ran; one fired and one held at its boundary. At least nine facts broke and were repaired in view (S1 to S16). The ripe count fell from 24 to 19 to 10, each step from an attack.
