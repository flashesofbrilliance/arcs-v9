# Dreaming pass 2 (2026-11-02): the 120-day window

Same scout as pass 1, longer sleep: `python3 scripts/dream_mine.py --days 120 --min-sessions 5
--out _STATE/dream/mine-120.json`. Proposals only; mark each **ACCEPT / REJECT / EDIT**.

**Ruling (Zach, 2026-11-02):** accept C1 to C6. Applied the same day: new `browser-pane-protocol` (C1),
`edit-shared-file-reread-region-first` (C2), `absolute-worktree-paths-and-live-cwd` (C3); corrected
`gh-auto-merge-no-required-checks-merges-now` (C4, auto-merge now disabled); extended
`mcp-oversized-result-envelope-parse-from-disk` (C5) and `long-inline-shell-goes-in-a-script-file` (C6).

- **Window:** 595 arcs-v9 transcripts (they start in late July, so about 100 days of real
  history), 9.7 seconds. 57 tool-error clusters seen in 5+ sessions; 303 correction-shaped
  turns.
- **What the long window changes:** prevalence. Pass 1's A1 (inline quoting breaks) was 9
  sessions in a week; over the window it is **88 sessions, 109 hits**, the single largest
  repeat failure. Pass 1's A4 (file:// tab) is 20 sessions. Both memories already landed.
- **What it does not change:** the correction regex. At 303 hits it is mostly noise (the
  "em-dash" theme is Zach quoting my replies, not asking). Corrections need the regex fix
  from pass 1 before a long window says anything; nothing in section B below rests on it.
- **Prevalence** = distinct sessions (total hits).

## A. New repeat failures (not seen or not ranked in pass 1)

| # | Pattern | Prevalence | Existing memory | Proposal |
|---|---|---|---|---|
| C1 | Browser pane protocol misses: no site open before `navigate` (33), no preview open (21), pinned file tab can't navigate (18), tab closed (14), `read_page` before `find` (13), `scroll` before any screenshot (16), malformed `computer` args (30), pane hidden so `computer`/screenshot time out (37 + 8) | about 120 session-hits across 8 shapes | `preview-file-tab-page-tools-dont-act` (one shape) | **Widen that memory into one browser-pane protocol:** `tabs_context` first; open with `preview_start {url}` or `tabs_create` + `navigate`; `read_page` before `find`/refs; screenshot before coordinate actions; if the pane is hidden use `get_page_text`/`read_page`, not screenshots. |
| C2 | Edit tool: "String to replace not found" (35 sessions, 74), "modified since read" (11), "not read yet" (8) | 54 sessions | `whole-file-overwrite-clobbers-parallel-session-work` (adjacent) | **New feedback memory:** re-Read the exact region before an Edit when the file is shared or regenerated (CLAUDE.md, MEMORY.md, JSONL, built HTML); a "modified since read" is another writer, so re-read and merge, never overwrite. |
| C3 | Wrong working directory: "File does not exist, cwd is ..." (30), `getcwd` on a deleted worktree (8), worktree-isolation hook blocks (5) | 43 sessions | gotcha 14 (run repo tools from your worktree) | **Strengthen gotcha-14 memory:** use absolute worktree paths in tool calls; after any worktree removal, `cd` to a live path before the next command. |
| C4 | `gh pr merge --auto` refused: "Auto merge is not allowed for this repository" | 10 (10) | `gh-auto-merge-no-required-checks-merges-now` says `--auto` merges at once | **Correct that memory (stale or wrong):** auto-merge is disabled on arcs-v9; merge only with `scripts/safe_merge.sh <pr> <head-sha>`. Verified 2026-11-02: `gh api repos/flashesofbrilliance/arcs-v9 --jq .allow_auto_merge` returns `false`. |
| C5 | Parsing tool output as JSON fails (`JSONDecodeError` Expecting value 18, Extra data 6) | 24 sessions | `mcp-oversized-result-envelope-parse-from-disk` (one cause) | **Extend it:** check the output is JSON before `json.loads` (empty stdout, a warning line first, or JSONL read as one document); for JSONL parse line by line. |
| C6 | Python f-string with a backslash in the expression (`SyntaxError`) | 8 (8) | none | **Fold into A1's memory:** inline Python with quotes or escapes goes in a script file; the system Python rejects backslashes inside f-string braces. |

Seen but not proposed: permission-stream aborts (56; harness), user rejections (44; Zach's
call working as designed), Kintsugi and integrity pre-commit blocks (19 + 9; gates working),
SendUserFile JSON (14) and DesignSync auth (7) (harness-side), Vercel pending checks (7).

## B. Recall gaps the long window confirms

| # | Memory that existed | Still hit | Proposal |
|---|---|---|---|
| R1 | `bsd-sed-...` (BSD userland) | `head: illegal line count` 7 sessions | Already amended in pass 1 (A3); no change. |
| R2 | harness rule "never foreground sleep" | 8 sessions | Pass 1 rejected A5; the long window says 8 sessions, still self-correcting. Keep rejected unless Zach wants it. |

## Not done

1. Pass 1's correction-regex fix (count only short turns right after an assistant turn), which
   the long window needs before its 303 corrections mean anything.
2. A weekly schedule. With 10 seconds for 120 days, the scout is cheap enough to run daily; the
   judgment pass is the cost.
