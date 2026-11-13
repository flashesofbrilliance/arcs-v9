# Dreaming pass 10 (nightly, 2026-11-13 UTC)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-13 at origin/main 6b63b4f8. Ran 2026-11-12 22:10 EST; branch and file dated by UTC (2026-11-13) because claude/dream-2026-11-12 already exists from pass 9.
- Quiet-night check: 296 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 66 transcripts, 22 error clusters (>= 2 sessions), 29 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1385 docs, 139 dead cites, 115 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 45 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` on main (passes 1 to 9; PRs #2061 to #2162 all MERGED, none open). RESIDUE-for-dream-2026-11-06.md already cited by passes 4 to 8; not re-used.
- KINTSUGI ranking: Project claude/KINTSUGI.md searched (RAG, not a full read) for safe_merge and ship_docs: 0 matching rows. Ranking is by evidence strength. Unverified against a full KINTSUGI read.
- Under 40 items: judged inline, no scouts. 18 of 22 clusters were covered by passes 1 to 9 or are false positives. Two new clusters traced to a root cause in the transcripts; both below.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| L1 | Two sessions race to merge the same PR; the loser's `safe_merge.sh` dies with `REFUSE: PR <n> is not OPEN` and then spends a call finding out who merged it. | 2 sessions. 22d2d282 2026-11-13 01:47:45Z ran `safe_merge.sh 2216 a715c92e`; PR 2216 had merged at 01:47:35Z (10s earlier), mergedBy flashesofbrilliance, by its owner session per the 22d2d282 wrap-up. 5adfa139 2026-11-11 22:41:59Z ran `safe_merge.sh 2143 b333b077`; PR 2143 had merged at 22:41:14Z, and session 7c50ca85 committed "PR 2143 merged" at 22:41:38Z. Both followed with a `gh pr view --json state,mergedAt,mergedBy` call. All read this pass. | `check_head` at scripts/safe_merge.sh:128 refuses any non-OPEN state with one message. AGENTS.md rule 22 (line 158) gives one owner per PR branch for pushes, not merges. | (a) In `check_head`, when state is MERGED, print `safe_merge: ALREADY MERGED by <login> at <mergedAt>, merge <oid>, head matches pin: yes/no` and exit 3 (distinct from REFUSE 1), so the caller knows at once and does not file a duplicate receipt. (b) Optional: extend rule 22 to merges ("only the PR's owner session runs safe_merge on it"). | scripts/safe_merge.sh (a); AGENTS.md (b) | Low for (a): exit code changes only for an already-merged PR; any caller that treats nonzero as failure still stops. (b) touches a rule file: Zach's call. |
| L2 | `ship_docs.sh` called with no title, exits 2 on usage, then rerun with a title. | 2 sessions. 7c50ca85 2026-11-11 22:41:38Z (`./scripts/ship_docs.sh 2>&1 \| tail -6`), retried 22:42:57Z. 634f3418 2026-11-12 14:46:19Z (same bare call), retried 14:46:23Z. Each cost one round trip plus a tail that hid nothing useful. All read this pass. | Usage check at scripts/ship_docs.sh:21. | When `$1` is empty, default TITLE to the last commit subject with any `[NCI:...]` tag stripped (`git log -1 --format=%s`), echo `ship_docs: title defaulted to "<subject>"`, and continue. Keep exit 2 when there are no commits ahead of origin/main. | scripts/ship_docs.sh | Low: a multi-commit branch gets the newest subject as PR title, which may undersell it. Both observed cases were single-commit docs branches whose retry title equalled the commit subject. |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): now 40 hits in 23 sessions (pass 9: 32 in 17). Still the strongest unruled item.
- Pass 6 `JSONDecodeError: Expecting value`: now 4 sessions (pass 9: 3).
- Pass 5 F5 (write hook blocks writes into another worktree): 3 sessions, no new hits.
- Pass 9 watch `fatal: Needed a single revision`: now 3 sessions, 2 recent (5adfa139 2026-11-08, 4c093fb0 2026-11-12 21:08Z). Cause not traced this pass; unverified. Candidate for pass 11.
- Pass 7 I3 (hardcoded preview ports): 2 sessions, no new hits.
- Pass 9 K1 and K2 (surface catalog pathspec, leak check in pre-commit): no new CI failures in this window.

## Not proposed (watch)

- Built-in rm safety-check denial (4 hits, 2 sessions: 6eea3885 2026-11-12, 5adfa139 2026-11-08). The 6eea3885 hits are on compound commands with `rm` in a loop; the guard worked as designed. No fix to propose.
- `send_message` called without `session_id` (2 sessions: 5492f2a4 2026-11-13, 5adfa139 2026-11-10). Calling context not found in the transcript scan; unverified.
- `computer` input `too_big` (2 sessions, one from 2026-07-20). Stale.
- 29 corrections: no new class with a second session found inline. Unverified beyond a skim of the cluster heads.
- Corpus: 139 dead cites (+2 on pass 9), 115 stale verifications (flat). Orphans 45 (+3), 0 awaiting a fate. Not isolated.

## False-positive shapes to drop from the scan

- User tool rejections (12 sessions): consent, not an error. Seventh pass in a row; exclude "The user doesn't want to proceed" in dream_mine.py.
- `Exit code: SKILL.md` (2 sessions): a listing that exited 1, clustered on its first output line. Cluster on the error line, not the first stdout line.
- `[resize_window] Viewport emulation cleared`, `head: illegal line count -- 0`: repeats.
- `safe_merge: REFUSE ... gates=FAILURE`: cluster on the failing CI step name (repeat from pass 9).
