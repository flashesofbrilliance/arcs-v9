# Dreaming pass 12 (nightly, 2026-11-15)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-15 at origin/main 3be53c85. Ran 2026-11-15 01:18 EST.
- Quiet-night check: 51 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 42 transcripts, 30 error clusters (>= 2 sessions), 39 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1396 docs, 140 dead cites, 115 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 49 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` on main (passes 1 to 9) and in the open draft PRs #2221 (pass 10: L1, L2) and #2260 (pass 11: N1, N2). RESIDUE-for-dream-2026-11-06.md already cited by passes 4 to 8; not re-used.
- KINTSUGI ranking: Project claude/KINTSUGI.md and RECEIPTS.md searched (RAG, not a full read) for induced-backlog conflicts: 0 KINTSUGI rows; 1 receipt (R-006, 2026-10-31: PR #1876 CONFLICTING on `_QUEUE/induced-backlog.jsonl`). Unverified against a full KINTSUGI read.
- Under 40 items after the slice: judged inline, no scouts. 29 of 30 clusters were covered by passes 1 to 11, already fixed, or false positives. One new cluster below.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| Q1 | `safe_merge.sh` refuses with `PR <n> is CONFLICTING with main` and stops there; the session then has to work out which files conflict and how to clear it. Likely common cause: `_QUEUE/induced-backlog.jsonl` has a local merge driver (`merge=backlog-by-id`, armed by `.claude/hooks/session-start.sh`), but GitHub's server-side mergeability check does not run custom drivers (unverified for this repo), so GitHub can report CONFLICTING for a conflict a local `git merge origin/main` resolves by row id. | 2 sessions in the window: e305247f 2026-11-13 20:36Z (PR 2227) and 22d2d282 2026-11-14 03:19Z (PR 2244, later CLOSED). PR 2227 touched `_QUEUE/induced-backlog.jsonl`; 2244 was titled `chore(backlog)`. 29 of the last 60 merged PRs touch that file (next most common, `src/ui-kit/kit-manifest.json`, is at 9). 210 commits to it in 14 days. Which files actually conflicted in 2227 and 2244 is unverified. | gotcha 22 (owner-only branch pushes); `scripts/backlog_merge_by_id.py` driver; safe_merge line 198 refuses but lists no files. | On CONFLICTING, before dying, run `git merge-tree --write-tree --name-only origin/main <head>` (git 2.52 on the Mac supports it) and print the conflicting paths. If the only path is `_QUEUE/induced-backlog.jsonl`, print the fix: in the owner session's worktree, `git merge origin/main` (the by-id driver resolves it), let hooks run, push, rerun safe_merge with the new head. Still never rebases or pushes itself. Add a fake-gh test case next to `run_case conflict`. | `scripts/safe_merge.sh` (line 198 and the self-test block near line 81) | `git merge-tree` uses git's built-in merge, not the custom driver, so it will still list the backlog file; the hint must say "resolvable locally", not "no conflict". |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): 39 hits in 19 sessions inside this 2-day window alone. Still the strongest unruled item.
- Pass 11 N1 (page tools on a `file://` tab): 8 hits in 6 sessions in the window. Pass 11 is still an open draft (#2260).
- Pass 10 L1 (`safe_merge: REFUSE: PR <n> is not OPEN`): 3 hits in 3 sessions (pass 11: 2). Pass 10 is still an open draft (#2221).
- Pass 2 f-string-with-backslash memory: new hit 65a01ecd 2026-11-13 20:40Z in `scripts/week_plan_build.py` (Mac python3 is 3.9.6, which rejects it). Already fixed: the file on main 3be53c85 compiles, and every `scripts/*.py` passes `py_compile` under 3.9.6. Recall gap only; no new proposal.

## Not proposed (watch)

- `safe_merge: REFUSE: PR <n> head is <sha>, expected <sha>` (2 sessions). e305247f 2026-11-13 (PR 2226): a real push mid-wait; the guard worked. 22d2d282 2026-11-09 (PR 2080): the expected sha was hand-padded with zeros (`4bd4e43357c0000...`). One session per shape; watch for a second hand-typed sha.
- Vercel `403 forbidden: You don't have permission to update the project` (2 sessions: 6055c769 2026-11-09, 5ce819e6 2026-10-18). Token scope, not a code fix; the error's recovery text names the CLI fallback.
- `The requested draft could not be found.` (2 sessions: ad8934f8 2026-10-28, 5adfa139 2026-11-09). Tool not identified from the cluster head; unverified.
- Corrections: 39 in the scan, newest 2026-11-13 (1 session). No new class with a second session.
- Corpus: 140 dead cites (flat), 115 stale verifications (flat). Orphans 49 (pass 11: 52), 0 awaiting a fate.

## False-positive shapes to drop from the scan

- User tool rejections (8 sessions in the window): consent, not an error. Ninth pass in a row; exclude "The user doesn't want to proceed" in dream_mine.py.
- `[resize_window] Viewport emulation cleared`, `[navigate] navigated to ...`, `head: illegal line count`: informational or repeats.
- With `--days 2`, the corrections list still returns rows back to 2026-10-15; the window filter seems not to apply to corrections (unverified; check `dream_mine.py`).
