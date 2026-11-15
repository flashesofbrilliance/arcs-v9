---
title: "The unattended door: what mechanizing ARCS protocols actually changed"
version: v3 (final after three I.D.E.A. passes)
date: 2026-11-15
status: PROPOSAL. Nothing here is wired. Fates and rule changes are Zach's.
evidence: facts.md in this folder (F1 to F28, seams S1 to S17; seams supersede the F lines they name)
baseline: origin/main 3f9b9f9, full clone. Main has since moved to c246b66e (#2274, a docs-only handoff molt, not reviewed here); the backlog file is unchanged.
---

# The unattended door

## Bottom line

ARCS can schedule checks, and it can schedule a model's judgment. It cannot schedule a person's judgment.

Six scheduled workflows ran about 151 times with nobody present, and a nightly model pass ran 9 nights out of 9. A step that needs a person gets done only when it falls due at a moment someone is already acting. Decision receipts (the record filed for each merge or publish) are filed for 98% of merges, because the merging session is there. The steps that fall due later all close at close to zero: backlog rows whose blockers cleared, outcomes on past decisions, dated bets (probabilities written before a call), and notes Claude drafted that only Zach can send.

The largest case is one row. `five-person-outcome-test`, putting the compass in front of five outside people and closing each loop, has been READY and unclaimed for 11 days. 106 of the 149 held backlog rows wait on it, and Zach's own 11-04 ruling freezes new scripts, agents, skills and gates until it reads. **The ask: run that test. In the meantime, fix the one detector bug, sweep two pages for passcodes, and make the Harrison send.**

## The evidence

| Step | Falls due | Present then | Done | Source |
|---|---|---|---|---|
| File a decision receipt for a merge | at the merge | the merging session | 310 of 316 PRs merged since 11-01 (98%) | S10 |
| Set a row DONE when its PR merges | at the merge | the merging session | 99 of 136 rows that cite a merged PR (73%) | S10 |
| Pass pre-commit gates | at the commit | the committing session | blocks wherever the hook is armed; bypassable, and absent on GitHub-side merges | F18 |
| Run a scheduled check | on its cron | a scheduler | about 151 runs across 6 workflows, mostly green | S14 |
| Run the nightly model pass (dreaming) | each night | a scheduler | 9 of 9 nights, 11-07 to 11-15 | S17 |
| Adopt what the model pass found | after it lands | nobody | 6 passes merged in one 31-minute sitting, up to 5 days late; 3 not merged | S17 |
| Fix what a scheduled check found | after it goes red | nobody | no-squash red 10-11 to 10-14, no fix inside the streak | S14 |
| Promote a row whose blockers cleared | when the last one clears | nobody; the morning note prints only a count and one name | 0 of 17 eligible rows promoted | S15, S17 |
| Act on a review_by date | on the date | nobody | 36 rows past due, oldest 10-25 | F7 |
| Record an outcome on a compass decision | days later | nobody | 5 real of 277 (1.8%); 0 from outside users | F16, F25 |
| Score a dated bet | on its date | nobody | 0 of 4 past due (n=4, grain) | F16 |
| Send a drafted counterpart note, then score it | after Zach sends | Zach, outside any session | Harrison follow-up 6 days late; Brian, MyAlly, Louisville and PRL dates passed | F21, F22 |

The gap has been found before. Outcome closure measured about 1% on 10-17 and 10-18; the row that would have fired the nudge at the right moment was composted on 11-05 because nobody moved it; the row built to put ripe rows in front of Zach has been READY for four weeks.

What did not survive testing: "a step gets done in proportion to how much the tool does" (closing a row on merge has no tool and runs at 73%; `safe_merge.sh` prints a receipt and never writes one), and "78% NCI:SKIP is avoidance" (SKIP is sanctioned for docs and chores; about 8.5% are candidate violations). Both are kept with the other repaired seams in facts.md.

## What to do, sorted by the freeze

The 11-04 ruling: no new scripts, agents, skills or gates until the five-person test reads; a recurring bug class still earns a Frustration Gate.

### Allowed now

| # | Action | Evidence | Door |
|---|---|---|---|
| A | **Run the five-person outcome test.** Tools are routed (`scripts/outcome_funnel.py`, the Accountant operators); its kill line is already written: fewer than 2 of 5 logging an outcome by day 21 pauses the build order | F25, S17: gates 106 of 149 held rows; for 90 it is the only gate | two-way |
| B | **Sweep pinned and shared pages for passcodes and contact lines.** Two pinned pages carry passcodes in their source; a link-shared pitch carries personal contact details (agent-read, unverified here) | F28 | sweep two-way; rotating a passcode one-way |
| C | **Send the Harrison follow-up.** Six days late; its scoring check is due 11-16 | F21 | one-way (a send) |
| D | **Fix `backlog_ripeness.py`** (a bug in an existing script, not a new tool): read the `state` field, never the prose note, and stop a cleared dependency from returning RIPE before the trigger is read (lines 63-64, 172-173). Add fixtures for both. Zach's call whether the Frustration Gate exception covers it | S5: 36 finished rows read as live, 3 live rows skipped; S15 | two-way |
| E | **Amend `backlog-fate-triage-2026-10-18`** (an existing row) so the groom lists held rows whose blockers cleared, with the human trigger each still needs, and rows past review_by | F7, F20 | two-way |
| F | **Graduate the 17 ripe rows to READY.** Bookkeeping, not a fate | S15, S17 | two-way |

### After the test reads

| # | Row (proposed) | What it does | Evidence |
|---|---|---|---|
| 1 | `backlog-derived-ready` | READY is computed when the backlog is read, never written, for rows with a structured trigger (a dependency, a date, a PR) and a two-way door. One shared function imported by every reader of `state`; a check that lists those readers; a stored-versus-computed mismatch blocks on changed rows. DONE stays a human act, suggested in the groom from an explicit `closes_pr` field | S16: computing DONE from prose would have marked `recoil-kairos-7s-test` done from PR 2173 and surfaced a counterpart send as ready |
| 2 | `send-time-bet-check` | before a new send to a counterpart, list that counterpart's due bets and unsent drafts and record each as scored or deferred to a date; read the bets from the artifact pages. Place it in the step every send passes | S17: the recoil skills would see only one of four named counterparts; whether every lane runs the counterpart gauntlet is unverified |
| 3 | `history-tools-refuse-shallow` | scripts that count git history exit non-zero on a shallow clone unless told otherwise | S10: this analysis first undercounted by 60 to 87% |

## Ripe now

All blockers DONE, trigger fired, two-way door (17):

- **dependency or PR triggers (10):** `recoil-kairos-7s-test`, `recoil-skills-on-runner`, `jtbd-graph-s5-feedback`, `doc-gate-false-positive-cleanup`, `rfp-ship-resume-tailor-rebase`, `rfp-ship-engine-branch-reconcile`, `librarian-apex-spine-tier-class`, `card-catalog-q4-rerun-with-receipts`, `session-overlay-recurring`, `open-loops-ssot-drift-line`
- **date triggers (7):** `accountant-weekly-first-unattended`, `line-triage-reads-gates-one-way`, `ready-now-door-decision-split`, `receipt-coverage-resolved-split`, `issue-sync-native-blocked-by`, `readiness-card-decision-test`, `backlog-tiebreak-rule`

Notes carried by three of them: `recoil-kairos-7s-test`'s timed read is a person; `jtbd-graph-s5-feedback` needs two dated checks and Zach's yes; `open-loops-ssot-drift-line` is not yet approved.

Blockers done but waiting on a person or an outside event (4): both `cia-*` rows (a call not yet booked), `token-tuner-why-prompt` (Zach using breadcrumbs on a real page), `seat-binding-design-log` (a pick log landing).

`recoil-brian-acceptance` waits on two rows: `recoil-kairos-7s-test` (ripe) and `recoil-brian-ssot` (READY, unclaimed).

## Also waiting on Zach

- Two held rows wait on his word: WRITE-LOCK 1 for `compass-anti-distillation-build`, a new oracle namespace for `oracle-sync-namespace`.
- The Brian note and the MyAlly agreement's 23 pending suggestions.
- Seven debt-tracker decisions aged about 40 days, two past their own deadlines.
- A price for the audit, if he wants a first-dollar row.

## Method

The backlog, full git history and the receipt ledger were mined in the shell and 19 pinned artifacts were read by one agent; then three I.D.E.A. passes (Alchemist, Librarian, Detective, Curator, Loki, Bayesian, Conductor, base and worst scenarios, Grug, claims skeptic) attacked the facts and each draft, breaking at least ten claims, each repaired in facts.md.
