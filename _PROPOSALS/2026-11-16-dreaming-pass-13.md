# Dreaming pass 13 (nightly, 2026-11-16)

Proposals only. Nothing here is applied until Zach rules.

## Header

- Worktree: /tmp/dream-2026-11-16 at origin/main 2ed37a11.
- Scans: `dream_mine.py --days 2 --min-sessions 2` (25 transcripts, 10 error clusters, 8 corrections); `dream_mine.py --corpus --stale-days 45` (1402 docs, 140 dead cites, 116 verifications older than 45d, 0 near-duplicate memory pairs); `orphanage.py --check` (47 orphans, 7 cited, 0 unregistered, 0 awaiting a fate).
- Slice: dropped everything ruled or proposed in passes 1 to 12, including open draft PRs #2221 (pass 10), #2260 (pass 11), #2267 (pass 12). RESIDUE-for-dream-2026-11-06.md is already cited by passes 4, 6, 7, 8, 9, so it was not re-read.
- Survivors: 2 proposals, 3 evidence updates, 1 watch item.

## Proposals

| id | pattern | evidence | existing guard | proposal (file) | risk |
|----|---------|----------|----------------|-----------------|------|
| T1 | A dated triage hold expires and CI `gates` fails on every branch, main included, with no warning beforehand. Happened 2026-11-14 (5 orphan tools on row `jtbd-graph-triage-2026-10-20`; session 97844597 found PR 2266 blocked by it; 65a01ecd hit `gates=FAILURE` on 2026-11-15 12:36Z; fixed by 42c0739e / 8350d7e8). **It is about to happen again:** `runtime/specs/jtbd-graph-triage.json` holds 34 entries, 32 of them with `resolve_by` 2026-11-17 (28 on row `jtbd-standing-tools`, 3 on `jtbd-graph-triage-2026-10-20`, 1 on `uikit-recoil-player`). Verified this pass: `universe_jtbd_adapter.py --check` passes today; the same check with `date.today()` patched to 2026-11-18 FAILS with 32 `TRIAGE-EXPIRED` (orphan-tool 30 new, orphan-job 2 new, blocker-no-resolve-by 1 new). If CI runs on UTC, the first red run is any push after 2026-11-18 00:00 UTC (2026-11-17 7 PM ET); runner timezone unverified. | `apply_triage` in `scripts/jtbd_graph_gates.py` (line 428) passes a hold until `resolve_by`, then fails. Nothing reports a hold that is close to its date. | (a) Now, Zach's call: before 11-17 evening ET, either give the 32 held findings their job rows or re-date the holds (within `TRIAGE_MAX_DAYS`). (b) Guard: in `apply_triage` (`scripts/jtbd_graph_gates.py`), return a `TRIAGE-DUE-SOON` note for any hold with `resolve_by` within 3 days, printed by `universe_jtbd_adapter.py --check` as a non-failing line, plus a self-test fixture. Optional: the morning preflight greps for it. | (a) Re-dating without fixing just moves the cliff. (b) A warn line can be ignored like any other; low risk, stdlib only. |
| T2 | `safe_merge.sh` rule 3b refuses a kit PR whose base lacks main's kit-input commits, then names a fixed recipe (rebase onto main, `kit_pull.py manifest`, `kit_periodic_table.py`, commit, push) that each session types by hand. | 2 sessions on 2026-11-15, 15 minutes apart: e0b6dd1e 13:37Z (PR 2261, 1 commit behind), 455ff6db 13:52Z (PR 2270, 6 commits behind). Both PRs later merged. Rule 3b landed 2026-11-13 (0e4e614b), so this is its first two days. | The refusal message itself (`scripts/safe_merge.sh` line 189). No script runs the recipe. | Add `scripts/kit_rebase_refresh.sh <branch>`: refuse on a dirty tree or a branch the session does not own, rebase onto origin/main, run the two generators, commit `chore(kit): refresh manifest after rebase`, print the new head for `safe_merge.sh`. Point the refusal message at it. Unverified: whether the two generators are deterministic enough that two parallel kit PRs do not keep re-conflicting. | A scripted rebase on a shared branch can surprise a second session; the owner check and dirty-tree refusal limit that. Only 2 sessions, so Zach may prefer to watch one more week. |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2 refusal, exit 126, recall gap on `long-inline-shell-goes-in-a-script-file`): now 29 hits across 12 sessions in the scan window. Still the largest error cluster. Unruled.
- Pass 10 L1 (two sessions race to merge one PR; `REFUSE: PR <n> is not OPEN`): now 3 sessions (22d2d282 PR 2216, 455ff6db PR 2265 on 2026-11-14, 5492f2a4). Unruled.
- Pass 1 B1 (`feedback-counterpart-text-first-person-singular-no-royal-we`): a fresh correction in session 97844597 on 2026-11-15 18:46Z (Zach: the royal form is wrong, it reads as him speaking about himself in the third person). Unverified which text it corrected; the preceding assistant turn was a PR 2266 status note. 1 session, so evidence only.

## Not proposed (watch)

- Correction in 22d2d282 on 2026-11-13: primer terms may be missing from the wiki (tooltip back-propagation into the DB vs a cache issue). 1 session; no repeat yet.

## False-positive shapes to drop from the scan

- `Exit code <n>` with no text (2 sessions) carries no signal; already flagged in pass 5. Still not filtered by `dream_mine.py`.
- "The user doesn't want to proceed with this tool use" (4 sessions) is a user rejection, not a failure; flagged in passes 4 and 7 to 12.
