# Dreaming pass 15 (2026-11-18)

Nightly pass on the Mac, worktree /tmp/dream-2026-11-18 at origin/main 48346027. Proposals only; nothing applied.

## Scans
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 65 transcripts, 31 error clusters, 19 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1467 docs, 141 dead cites, 119 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 48 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- Follow-up: a read-only script matched each new error result to the tool call behind it in the session transcripts (721a0ba0, 8cacf4e7, 22d2d282, bbee6309).

## Slice
Dropped as already ruled or proposed (passes 1 to 14): bash 3.2 shell refusals and the shape-guard hook message, Chrome tab-group and "No tab available" (pass 14 U1, guard shipped), `file://` tab (pass 11 N1), `TypeError: unhashable type` and `string indices must be integers` (pass 14 U2), every `safe_merge` REFUSE family (passes 10, 12, 13), `substring not found` and the pre-commit seam message (passes 5 to 9), isolated-worktree Write hook (pass 5), `Needed a single revision` (pass 11 N2), `send_message` without `session_id` (pass 13 watch), rm safety check (pass 14 watch, still 2 sessions in this window).
Dropped as noise: tool-use rejections (user choice), `Request timed out` (no common tool), interrupted calls, navigate and resize_window notices (not errors), bare `Exit code <n>`, `File does not exist` (2 sessions, different files, no shared cause found).
Residue file `/Users/zharris/Downloads/gauntlet-2026-11-06/RESIDUE-for-dream-2026-11-06.md`: already cited by passes 4 to 14; unchanged since 2026-11-06. Not reused.
Corrections: 19, all single-session or already covered (tone, scope, stop-polishing). None reaches 2 sessions on one theme.

## Proposals

| id | pattern | prevalence | existing memory | proposal |
|----|---------|------------|-----------------|----------|
| V1 | The `daily-reps-picklist` scheduled task guesses column names for the APPLY PICKS query: `o.id`, `o.comp`, `s."jobId"`. Prod says `42703: column s.jobId does not exist`, then `column o.id does not exist`; the run then reads `information_schema.columns` and retries. Three wasted SQL calls per run. | 2 sessions, both scheduled runs: 721a0ba0 2026-11-16 13:56Z, 8cacf4e7 2026-11-17 13:55Z (identical failing query both days). | Task step 2 says only `left join "JobSwipe" on jobid`. `memory/job-search-swipe-board.md` names the tables, not the columns. Verified in `prisma/schema.prisma`: the key is `jobid` on both models; there is no `id` or `comp` column (comp lives in `salary` and `"compBand"`). | Edit `/Users/zharris/.claude/scheduled-tasks/daily-reps-picklist/SKILL.md` step 2: paste the working query the runs converged on, e.g. `select o.jobid, o.title, o.company, o.salary, o."compBand", o.url, o.source, o.composite, o."firstSeen" from "JobOpportunity" o left join "JobSwipe" s on s.jobid = o.jobid where o.band='PURSUE' and s.jobid is null and o."laneStatus" is null order by o."firstSeen" desc, o.composite desc nulls last limit 40;` plus "columns per prisma/schema.prisma; never guess `id`". |
| V2 | Same task: the note title format "Reps YYYY-MM-DD (Day)" is ambiguous. Runs create the note with the full weekday ("Reps 2026-11-17 (Tuesday)") and the next run looks up yesterday with the short form ("Reps 2026-11-16 (Mon)", "Reps 2026-11-13 (Fri)"): `AppleScript error ... Notes got an error`, then a `list_notes` and a second lookup. Missing the note means step 5 TALLY can log `"source":"none"` for a day Zach did fill in. | 2 sessions: 721a0ba0 2026-11-16 13:59Z (`(Fri)` failed, `(Friday)` retried), 8cacf4e7 2026-11-17 13:55Z (`(Mon)` failed; `add_note` then used `(Tuesday)`). | None. | Edit the same SKILL.md, steps 5 and 7: fix the title as `Reps YYYY-MM-DD (Weekday)` with the full English weekday (the output of `date +'Reps %F (%A)'`), and for yesterday's lookup "list_notes, match on the `Reps YYYY-MM-DD` prefix, never rebuild the suffix". |
| V3 | A commit refused by pre-commit is followed in the same Bash call by `git push` and `gh pr create`, because the commit is piped to `grep` or followed by `;`. The push sends nothing and `gh` fails with `No commits between main and claude/...`. | 3 calls in 2 sessions: 22d2d282 2026-11-09 18:41Z and 2026-11-13 19:52Z (`git commit ... > log; echo "exit $?"; ... git push ...; gh pr create`), bbee6309 2026-11-17 21:44Z (`git commit ... \| grep -E "FAIL"; git log; git push ...; gh pr create`). | `memory/pipe-to-tail-hides-failed-step-in-and-chain.md` (MEMORY.md line 173) states the rule; it did not fire in any of the 3. Recall gap: needs a gate, not a new memory. | Add a check to `.claude/hooks/cruise-control-bash-guard.py` (or a new PreToolUse Bash hook beside `bash32-shape-guard.py`): deny a command that contains `git commit` and later `git push` or `gh pr create`, when the commit is piped (`\|`) or followed by `;` and the command has no `set -o pipefail` or `&&` chain from commit to push. Message: "commit, push and PR as one && chain, or use scripts/ship_docs.sh". Fail open, with a `--self-test` like `chrome-tab-guard.py`. |

Risk, V1 and V2: the scheduled task file lives outside git (`~/.claude/scheduled-tasks/`), so the edit has no PR trail; record it as a receipt. Per ROOTSTRAP, task edits happen in a live turn only.
Risk, V3: a regex over shell text can deny a legitimate command (for example a commit message that quotes "gh pr create"); keep the match on unquoted tokens and fail open on parse errors.

Unverified: how many KINTSUGI rows each would have prevented. That ledger lives in the claude.ai project, not in this repo, so the ranking is by session count and wasted calls. Unverified for V2: whether a TALLY line was ever logged as `none` because of the lookup miss (reps-log.jsonl not checked).

## Watch, not proposed
- Corpus: 141 dead cites (pass 14: 140), 119 stale verifications (flat). Orphans 48 (pass 14: 47), 0 awaiting a fate.
- rm safety-check refusals: 2 sessions in this window; cause still unverified.

## False-positive shapes to drop from the scan
- `[navigate] Navigated to ...` and `[resize_window] Viewport emulation cleared ...`: status notices, not errors.
- `safe_merge: waiting (checks=PENDING ...)`: a poll message, not a refusal.
