# Dreaming pass 14 (2026-11-17)

Nightly pass on the Mac, worktree /tmp/dream-2026-11-17 at origin/main c8ff8df5. Proposals only; nothing applied.

## Scans
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 54 transcripts, 26 error clusters, 18 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1421 docs, 140 dead cites, 119 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 47 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- Follow-up: a read-only script matched each error result to the tool call behind it, over transcripts modified in the last 14 days.

## Slice
Dropped as already ruled or proposed (passes 1 to 13; passes 10 to 13 closed on Zach's ruling 2026-11-16, picks merged in PR 2319):
bash 3.2 too-old shell (pass 5 F1), `safe_merge` not OPEN (pass 10 L1, not picked), CONFLICTING (pass 12 Q1, not picked), kit-input refusal (pass 13 T2), gates=FAILURE from an expired hold (pass 13 T1), `file://` tab (pass 11 N1), `Needed a single revision` (pass 11 N2), port in use (pass 9 I3), pre-commit seam message and `substring not found` (passes 5 to 9), isolated-worktree Write hook (pass 5), `send_message` without `session_id` (pass 13 watch item; still the same 2 sessions).
Dropped as noise: `ls: scripts/keyline_check.mjs` and `scripts/jobs_board_mcp.py` (both exist on main; the sessions ran in older checkouts), `Request timed out` (3 sessions, no common tool), tool-use rejections (user choice), interrupted calls.
Residue file `/Users/zharris/Downloads/gauntlet-2026-11-06/RESIDUE-for-dream-2026-11-06.md`: already cited by passes 4 to 13; unchanged since 2026-11-06. Not reused.

## Proposals

| id | pattern | prevalence | existing memory | proposal |
|----|---------|------------|-----------------|----------|
| U1 | Claude in Chrome calls reuse a remembered `tabId`, or open with `tabs_create_mcp`/`navigate` before the tab group exists: "Tab <id> is not in Claude's tab group for this session" and "No tab available". | 14-day window: tab-group error in 6 sessions (22d2d282 2026-11-09 `navigate` tabId 1651232968; 47f0c895 2026-11-16 `tabs_close_mcp`; 66a03f8a 2026-10-12; 97faa012 2026-10-12; 431161e0 2026-09-17; 436464bc 2026-09-30); "No tab available" from `browser_batch` in 4 sessions (a70280ce 2026-11-16, first action `tabs_create_mcp`; 47f0c895 2026-11-16; 08574dcd 2026-11-03; 10adaf9a 2026-09-14). 2-day scan: 3 + 3 sessions, latest 5f23c669 2026-11-17 04:56Z. | `memory/browser-pane-protocol.md` rule 1 ("tabs_context first; reuse a live tab id, never a remembered one") covers the built-in pane only; its description and the MEMORY.md hook name only the pane. Recall gap, not a new memory. | Edit `~/.claude/projects/-Users-zharris-arcs-v9/memory/browser-pane-protocol.md`: widen the description to "built-in browser pane and Claude in Chrome"; add rule 5: "Claude in Chrome: first call `tabs_context_mcp` with `createIfEmpty: true`; take tab ids only from that result, never from a handoff or an earlier session; a tab-group error means call it again, not retry the id." In MEMORY.md line 182 change the hook text `(tabs_context, open, read_page, screenshot, act)` to `(tabs_context / tabs_context_mcp first, open, read_page, screenshot, act)`: +25 bytes. |
| U2 | Ad-hoc Python over `GET /api/jobs` output treats the body as a list of rows; it is an object, so the loop dies with `TypeError: unhashable type: 'dict'` or `string indices must be integers`. | 3 sessions in 2 days on the jobs data: 5f23c669 2026-11-16 17:05Z (`jobs_wt.sh api GET /api/jobs`, printed keys `rows, settings, spec, caller`), 47f0c895 2026-11-16 22:14Z (`jobs.json`), a70280ce 2026-11-16 19:13Z (`board.json`, `for r in rows: r['jobid']`). Same class of error, different JSON, in 6055c769 2026-11-11 and 5492f2a4 2026-11-16 (Substack archive API). | None found: `job-search-swipe-board.md` names the API path, not its response shape. | Add one line under the API sentence in `~/.claude/projects/-Users-zharris-arcs-v9/memory/job-search-swipe-board.md`: "`GET /api/jobs` returns `{rows, settings, spec, caller}` (`src/app/api/jobs/route.ts` lines 31 to 36); loop over `d['rows']`. For any unfamiliar JSON, print `type(d)` and its keys before indexing." No MEMORY.md change. |

Risk, U1: MEMORY.md is 24,564 bytes, 12 under its 24,576 budget; +25 bytes goes over, so cut at least 13 bytes elsewhere on line 182 in the same edit (for example drop " (Frustration Gate)", 19 bytes, leaving 24,570).
Risk, U2: the shape is true at c8ff8df5; if the route changes, the memory line goes stale. It cites the file and lines so a corpus pass can catch drift.

Unverified: whether either pattern caused rows in KINTSUGI.md. That ledger lives in the claude.ai project, not in this repo, so the ranking by prevented KINTSUGI rows was not computed. Ordered by session count instead.

## Watch, not proposed
- Built-in rm safety check ("stops removals that can delete far more than intended"): 6eea3885 2026-11-12, 22d2d282 2026-11-15, 5f23c669 2026-11-16 and older. The scan does not show the `rm` part of each command, so the shared cause is unverified.
- Corpus: 140 dead cites (flat since pass 10), 119 stale verifications (pass 13: 116). Orphans 47 (pass 12: 49), 0 awaiting a fate.

## False-positive shapes to drop from the scan
- `ls: scripts/<name>: No such file or directory` when the file exists on origin/main (a stale checkout, not a missing tool).
