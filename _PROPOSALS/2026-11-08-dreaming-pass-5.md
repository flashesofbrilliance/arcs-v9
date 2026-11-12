# Dreaming pass 5 (nightly, 2026-11-08)

Proposals only. Nothing here is applied; Zach rules each row.

## Header

- Worktree: /tmp/dream-2026-11-08 at origin/main b66b5bce.
- Quiet-night check: 28 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 51 transcripts, 26 error clusters (>= 2 sessions), 15 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1338 docs, 132 dead cites, 108 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 44 orphans, 8 cited, 1 unregistered, 0 awaiting a fate.
- Slice: dropped everything named in `_PROPOSALS/*-dreaming-*.md` (passes 1 to 3) and in open draft PR #2061 (pass 4, 2026-11-07). The RESIDUE file was already cited by pass 4, so it is not re-used here.
- Clusters with no prior proposal and >= 2 sessions were judged inline (under 40 items, no scouts).

## Proposals

| id | pattern | prevalence | existing memory | proposal | file it would edit | risk |
|----|---------|-----------|-----------------|----------|--------------------|------|
| F1 | Harness refuses a command on macOS bash 3.2.57 ("this shell is too old to run it reliably": backticks, arrays, nested `$(...)`, long text not in single quotes), exit 126 | 5 sessions; 3 of them on 2026-11-08 alone (22d2d282 19:49Z, 7def9610 19:59Z, 5fb153f6 20:33Z) | `long-inline-shell-goes-in-a-script-file.md` (accepted pass 1 A1, last edited 2026-11-02) covers nested quotes and heredocs but never names the bash 3.2 refusal or its trigger shapes. Recall gap, not a new memory. | Add one paragraph plus trigger words to the description: "bash 3.2 refusal (exit 126): no backticks, no arrays, one plain command per `$(...)`, commit messages in single quotes; else script file." | ~/.claude/projects/-Users-zharris-arcs-v9/memory/long-inline-shell-goes-in-a-script-file.md | Low: one memory edit; MEMORY.md index line unchanged |
| F2 | Closes pass 4 E5's open question | n/a | Verified this pass: the A1 memory exists and is indexed at memory/MEMORY.md:53 ("Long/nested-quote shell -> script file"). | Rule E5 as "accepted and filed; recall gap". F1 is the sharpened hook E5 asked for. | _PROPOSALS/2026-11-07-dreaming-pass-4.md (ruling note only) | None |
| F3 | Script edit anchors on a substring that is not there: `str.index` raises `ValueError: substring not found` mid-edit of HTML or JS | 2 sessions (5adfa139 2026-11-04, twice; 22d2d282 2026-11-08) | `edit-jsonl-and-html-surgically.md` says anchor on unique ids but has no "check the anchor count first" step | Add a line: "Before an edit, print `text.count(anchor)` and stop unless it is exactly 1; never `index()` blind." | ~/.claude/projects/-Users-zharris-arcs-v9/memory/edit-jsonl-and-html-surgically.md | Low |
| F4 | Orphanage false positive: a branch with an open PR is reported as an "unregistered cited orphan" | 1: `scripts/engagement_progress.py` on claude/myally-progress (commit e800aca1, 2026-11-08 15:06 -0500), PR #2066 open; cited by memory/myally-progress-log-is-claudes-job.md:11 | none | (a) No `--intake` and no fate: the fix is to merge or close #2066. (b) Tighten `orphanage.py --check` to mark branches with an open PR as IN-FLIGHT, not orphan (gotcha 15). (c) The memory cites a tool not yet on main; once the PR is ruled, add "(lands with #2066)" or drop the line. | scripts/orphanage.py; memory/myally-progress-log-is-claudes-job.md | Low; (b) needs a `gh` call or a cached PR list, so it fails open offline |
| F5 | Write hook blocks a write outside the session's isolated worktree | 2 sessions (126fc091 2026-11-01, twice; 5adfa139 2026-11-05) | `absolute-worktree-paths-and-live-cwd.md` exists; did not fire. Recall gap. | Sharpen that memory's description with the hook's exact phrase "running in an isolated git worktree" so it matches on the error. Unverified whether the hook text changed since the memory was written. | ~/.claude/projects/-Users-zharris-arcs-v9/memory/absolute-worktree-paths-and-live-cwd.md | Low |

KINTSUGI rows each would have prevented: F1 to F5 are transcript-only; none maps to a Project KINTSUGI row (G1 to G42, per pass 4's read). F4 sits in pass 4's E3 class (orphaned tools: G41, G42) but adds no new row.

## Not proposed

- Corpus: 132 dead cites and 108 stale verifications, versus 131 and 107 in pass 4. Classes already ruled in pass 3 (D1 to D4). The one new item of each was not isolated (no saved per-item list from pass 4). Unverified.
- "This tab shows a local file" (4 sessions, latest 2026-10-30) and "No commits between main and ..." on `gh pr create` (2 sessions, latest 2026-11-01): outside the 2-day window and last seen before pass 4; left for a long-sleep pass.
- 15 corrections: none newer than pass 4 points at a repo behavior (job-pipeline and client-scope remarks); dropped.

## False-positive shapes to drop from the scan

- `orphanage.py --check`: branches with an open PR (see F4b).
- `dream_mine.py`: generic "Exit code <n>" and tool-rejection clusters (user pressed Stop) carry no pattern; already noted in earlier passes.
