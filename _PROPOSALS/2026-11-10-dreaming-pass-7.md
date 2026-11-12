# Dreaming pass 7 (nightly, 2026-11-10)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-10 at origin/main c00e6530.
- Quiet-night check: 171 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 33 transcripts, 10 error clusters (>= 2 sessions), 11 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1360 docs, 137 dead cites, 111 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 41 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- `python3 scripts/memory_index_sync.py --check`: "INDEX OVER BUDGET 24611B > 24576B".
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` on main (passes 1 to 3) and in open draft PRs #2061 (pass 4), #2071 (pass 5), #2085 (pass 6). RESIDUE-for-dream-2026-11-06.md is already cited by pass 4; not re-used.
- KINTSUGI: claude.ai Project claude/BOOT.md section 6 lists G44 to G46 (2026-11-08) as pending append to KINTSUGI.md (PBI-25). Read via project search this pass; KINTSUGI.md itself not re-read. None of the rows below maps to a G row, so ranking is by evidence strength, not rows prevented.
- Under 40 items: judged inline, no scouts.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| I1 | Project memory index is over its load budget and growing; the warning fires every session and nothing acts on it. | MEMORY.md is 24,611 bytes / 24,341 chars (measured this pass; mtime 2026-11-09 14:43). Pass 6 recorded 23,952 bytes on 11-09. Budget 24,576 (scripts/memory_index_sync.py:24), harness load cap measured at 25,000 chars (same line). Headroom to the cap: ~659 chars, about one day of growth at the 11-09 rate. | `~/.claude/hooks/global-session-start.sh` lines 31 to 36 print "INDEX OVER BUDGET" at session start; memory_index_sync --check reports it. Warning only. Same shape as Project mining F2: written or warned guards did not hold, mechanical ones did. | Schedule one `/consolidate-memory` session before the next memory write (human-owned curation, so a ruling, not an auto-fix). Optionally make `memory_index_sync.py --append` refuse to append while over budget, so the cap is enforced where lines are added. | ~/.claude/projects/-Users-zharris-arcs-v9/memory/MEMORY.md (curation); scripts/memory_index_sync.py (optional refusal) | Over the 25,000-char cap the harness truncates the index from the bottom: newest hooks silently stop loading, which reads later as "memory existed and did not fire". Consolidation can drop a hook Zach relies on; review the diff. |
| I2 | Branch created with `git worktree add -b <name> <path> origin/main` tracks origin/main, so a bare `git push` fails ("upstream branch of your current branch does not match the name"). | 2 sessions: b61d5bd3 (2026-11-09 14:13Z), 7757e3eb (2026-11-09 02:55Z), exit 128. Reproduced in this pass's own setup: step 1 printed "branch 'claude/dream-2026-11-10' set up to track 'origin/main' by rebasing". Repo config: branch.autoSetupMerge=true, push.default=simple, push.autoSetupRemote=true (read this pass). | Memory `feedback_commit_to_main_via_worktree` and `safe-multiworktree-git-primitives` both use `git push origin HEAD:<branch>`, which works; neither names the bare-push trap. | Set `git config branch.autoSetupMerge simple` in /Users/zharris/arcs-v9 (git 2.52.0 supports it): new branches only track a remote branch of the same name, so push.autoSetupRemote then does the right thing. Also add `--no-track` to step 1 of the nightly dreaming routine prompt. | /Users/zharris/arcs-v9/.git/config (local, untracked); the dreaming routine's stored prompt | Low. Changes `git pull` default for new branches only (no upstream until first push). Today's behavior is safe because push.default=simple refuses; under push.default=upstream the same setup would push to main. |
| I3 | `.claude/launch.json` carries stale preview configs and ports pinned in argv, so preview_start hits "Port configured is already in use ... hardcoded port that ignores the PORT environment variable". | 2 sessions: 7c701962 (2026-11-09 22:41Z), 7757e3eb (2026-11-08 20:05Z). File (tracked, 61 lines, last touched 93b35eeb): 6 configs; 5 pin a port in runtimeArgs (`--port 3001`, `--port 3002`, `http.server 8765/5055/5056`); 4 point at worktrees that no longer exist (frosty-kepler-b69f51, zealous-golick-89e6e6, priceless-brattain-208033, vigorous-tu-599264: `isdir` false this pass). | None found (grep for "hardcoded port", "port.*in use", "preview_list" across memory, .claude/rules, CLAUDE.md: 0 hits). | Delete the 4 dead-worktree configs. In the 2 static `public/` configs, read the port from the environment: `bash -c 'python3 -m http.server "${PORT:-5055}" --directory public'`. Unverified: which config each failing session launched (scan excerpt does not name it). | .claude/launch.json | Low. Another session may be mid-use of a deleted config name; those worktrees are gone, so the configs already fail. |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): now 18 hits in 10 sessions in the 2-day window (pass 6: 7 sessions). Latest d08ea1f5 2026-11-09 18:35Z. Strongest unruled item across passes 4 to 7.
- Pass 5 F3 (`ValueError: substring not found` on script edit anchors): now 4 hits in 3 sessions (adds 6055c769 2026-11-09 16:14Z).
- Pass 5 F5 (write hook blocks writes into another worktree): new hit 22d2d282 2026-11-09 14:36Z (target in worktree contract-review-pass).
- Pass 5 F4b (orphanage flags open-PR branches): unregistered count fell from 3 to 0 because PRs #2066 and #2070 merged 2026-11-09 (gh, this pass). Confirms the false positive was transient; the scan fix still stands.

## Not proposed (watch list, 1 session each)

- 5adfa139 2026-11-09: "Stop numbers" and "this part doesn't make 100% sense to me: ... a stop number per decision". Internal jargon in counterpart copy; covered by pass 1 B5 (register) if ruled. Re-check if a second session repeats it.
- 5adfa139 2026-11-09 16:42Z: Zach cannot view .docx locally and asked to rely on Claude's confidence in its formatting. Candidate guard: render a .docx to PDF or PNG and look at it before asserting formatting. One session; unverified whether a render was done.
- 22d2d282 2026-11-09: sales-tax applicability for a CT service provider. A tax question, not a repo behavior; out of scope for a dreaming pass.
- Remaining corrections (6): client-scope and tone judgments, no repo behavior.
- Corpus: 137 dead cites (pass 6: 139) and 111 stale verifications (pass 6: 108). Classes ruled in pass 3 (D1 to D4); new items not isolated. Unverified.

## False-positive shapes to drop from the scan

- User tool rejections (10 sessions): consent, not an error. Already noted in passes 4 to 6; the scan still clusters them. Exclude "The user doesn't want to proceed" in dream_mine.py.
- `[resize_window] Viewport emulation cleared`: informational (repeat of pass 6).
- `head: illegal line count -- 0` inside the "book the seam" cluster: repeat of pass 6.
