# Wave 0 decision cards (lane C, drafted 2026-10-18, unreviewed)

Drafted by Claude for Zach. No row, registry or ADR was edited. Each card is the question, the options, the evidence, the abort and the rollback, so a ruling takes a minute. Fates are yours.

## 1. adr-085-acceptance-redecide (door: two-way, overdue since 2026-10-13)

**Question.** Accept ADR-085 and make the locked merge train the default merge path (migration step 3), keep it PROPOSED, or withdraw it?

**Options.**
- **Accept both**: flips `--lock` to default in the train script plus the warn-tier lease check in pre-commit, as its own PR with its own receipt.
- **Accept the ADR, defer step 3**: record acceptance, keep trains opt-in another week.
- **Keep proposed**: the data does not support a ruling yet.
- **Withdraw**.

**Evidence (tallied 2026-10-18, read-only).**
- 491 PR merges landed on main since 2026-10-06 (git, first-parent "Merge pull request"), plus 3 other first-parent commits.
- 20 PRs merged via a train, by decision_receipt rows named "merge train" (21 rows; the 21st, PR 874, is the train script itself, not a train). 16 on 2026-10-06, 4 on 2026-10-10, none from 10-11 to 10-18.
- So about 4 percent of merges went through a train (20 of 491), and zero in the last eight days, while merges peaked at 107 a day. Opt-in trains were used on two days, then stopped.
- The ADR asked for a week of opt-in trains with every refusal and takeover logged. This data shows two days of use, not a week, and I did not find a refusal or takeover log.

**Reading.** Making the train the only merge path (step 3) would reverse a pattern where almost all merges bypass it. That is evidence for "defer step 3" or "keep proposed", not "accept both". Whether to accept the ADR itself is separate and is your call.

**Caveats.** Trains whose receipt was never filed are missed, so 20 is a floor. The receipt match is on the words "train" or "merge train", which could include a stray non-train row. I did not read each receipt's merged refs.

**Abort.** Do not edit the ADR-085 status on incomplete data. **Rollback.** Revert the status edit and log a correcting receipt; do not delete the earlier one.

## 2. rc-ops-001-graduation-ruling (door: one-way)

**Question.** For each of RC-OPS-001's four criteria, met or not? Status becomes PROMOTED only if all four are, otherwise it stays GRADUATION_INITIATED with named gaps.

**Evidence.**
- The prerequisite row `hyperstition-rc-criteria-run` is DONE 2026-10-08; PRs 592 and 612 merged.
- The criteria audit (2026-09-27) proposed values but wrote none, and criterion 2 became measurable once 612 landed.
- Unblocks `hyperstition-pipeline-first-graduate`.

**Options per criterion.** Met, not met (name the gap), or need more evidence (name which).

**Not drafted.** I did not re-read the four criteria or the audit file, so I do not restate them here. Open the audit and the improved detector report with this card.

**Abort.** Write no criteria_status without your explicit ruling on each criterion. **Rollback.** Revert the registry edit, but canon propagation may already have copied the status (unverified), so check the propagation queue before calling it undone.

## 3. agent-receipts-audit-first-conversion (door: one-way, send)

**Question.** Is anyone ready to be offered the first Agent Receipts Audit now, and who?

**Evidence.**
- The prerequisite `kintsugi-public-falsification-count` is DONE 2026-10-08; the count and belief-log link went live on the audit page (PR 591).
- Unblocks 4 rows downstream, including the Accountant's external cohort (currently zero closed outcomes).
- The row names no candidate. I found none and did not look further.

**Options.** (a) Name a counterpart and I draft the offer and the ex-ante receipt, nothing sent. (b) Hold until a counterpart exists. (c) Withdraw the row.

**Abort.** Nothing goes out unless the ex-ante receipt is logged and you have read the draft; stop on any unconfirmed claim in it. **Rollback.** None once sent; the only undo is a correcting follow-up you write.

## Not a card: the filing hub

Per your ruling, `filing-*` stays a human track outside the line. Its 16-downstream hub is still the largest blocker in the graph, so it deserves its own standing view, not rows in this wave.
