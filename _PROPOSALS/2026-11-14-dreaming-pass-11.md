# Dreaming pass 11 (nightly, 2026-11-14)

Proposals only. Nothing here is applied; Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Worktree: /tmp/dream-2026-11-14 at origin/main d91a7a06. Ran 2026-11-14 01:18 EST.
- Quiet-night check: 133 commits across all refs in the last 26h; 0 files changed under ~/Downloads/gauntlet-2026-11-06/ in 26h.
- `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 77 transcripts, 42 error clusters (>= 2 sessions), 53 corrections.
- `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1396 docs, 140 dead cites, 115 verifications older than 45d, 0 near-duplicate memory pairs.
- `python3 scripts/orphanage.py --check`: 52 orphans, 7 cited, 0 unregistered, 0 awaiting a fate.
- Slice: dropped everything in `_PROPOSALS/*-dreaming-*.md` on main (passes 1 to 9) and in open draft PR #2221 (pass 10, branch claude/dream-2026-11-13, L1 and L2). RESIDUE-for-dream-2026-11-06.md already cited by passes 4 to 8; not re-used.
- KINTSUGI ranking: Project claude/KINTSUGI.md searched (RAG, not a full read) for file:// preview tabs and rev-parse: 0 matching rows. Ranking is by evidence strength. Unverified against a full KINTSUGI read.
- Under 40 items after the slice: judged inline, no scouts.

## Proposals

| id | pattern | prevalence | existing guard | proposal | file it would edit | risk |
|----|---------|-----------|----------------|----------|--------------------|------|
| N1 | Browser-pane navigation to a `file://` URL, then page tools fail with "This tab shows a local file, not a web page". Recall gap: the memory from pass 1 A4 exists and still did not fire. | Error in 11 sessions since 2026-11-01 (22d2d282, 22f19e57, 97844597, 170d5a0e, 6055c769, 3c272f38, d99e228e, 831afdde, cb345c9d, d94edfec, 5adfa139; 775b12bd excluded as the dream scan echoing itself). Direct `navigate` to `file:///private/tmp/...scratchpad/...html` seen in 97844597 2026-11-14 03:59Z, 6055c769 2026-11-13 02:01Z and 17:35Z, 3c272f38 2026-11-06 04:46Z. Newest error 22d2d282 2026-11-14 04:57Z. Read this pass. | Memory `preview-file-tab-page-tools-dont-act.md` (accepted pass 1, 2026-11-02). No browser hook: `.claude/settings.json` has PreToolUse only on Edit, Write, MultiEdit. | Mechanize the memory: add a PreToolUse hook with matcher `mcp__Claude_Browser__(navigate\|browser_batch)` that denies any `url` starting `file://` (including inside batch actions) with the message: "file:// tabs block page tools. Serve the folder: `python3 -m http.server <port>` from its directory, then navigate to http://127.0.0.1:<port>/<file>, or Read the file. See memory preview-file-tab-page-tools-dont-act." New script `.claude/hooks/browser-file-url-guard.py`. | .claude/settings.json; new .claude/hooks/browser-file-url-guard.py | Low to medium: blocks a screenshot-only look at a file tab, which does render. The matcher name is from transcripts (`mcp__Claude_Browser__*`); confirm it matches in the desktop app before relying on it. Hook payload shape for MCP tools unverified. |
| N2 | `git rev-parse --short A B` with two revisions dies `fatal: Needed a single revision` (exit 128), and in a compound command it hides the earlier output behind a failure. Root cause of the pass 9 / pass 10 watch item, now traced. | 2 sessions: 4c093fb0 2026-11-12 21:08Z (`git -C /Users/zharris/arcs-v9 rev-parse --short HEAD origin/main` at the end of a receipt-gathering command), 5adfa139 2026-11-08 20:53Z (`git rev-parse --short HEAD origin/claude/louisville-give-get` to confirm a push). Reproduced this pass on git 2.52.0: `git rev-parse --short HEAD origin/main` exits 128; `git rev-parse HEAD origin/main` and one `--short` per rev both work. | None found: no memory on rev-parse; `cruise-control-bash-guard.py` exists in .claude/hooks but is not wired in settings.json. | New feedback memory `git-rev-parse-short-takes-one-rev`: "`--short` implies `--verify`, which takes exactly one rev. To compare two heads use `git rev-parse HEAD origin/x \| cut -c1-8` or one `rev-parse --short` per rev." Add a one-line pointer in the git gotchas section of MEMORY.md. | memory/git-rev-parse-short-takes-one-rev.md (new); MEMORY.md index line | Low: memory text only. MEMORY.md must stay under its 24,576-byte budget; size not checked this pass. |

## Evidence updates to proposals still open (not new proposals)

- Pass 5 F1 (bash 3.2.57 harness refusal, exit 126): now 51 hits in 31 sessions (pass 10: 40 in 23). Still the strongest unruled item.
- Pass 6 `JSONDecodeError: Expecting value`: 4 sessions, flat.
- Pass 5 F5 (write hook blocks writes into another worktree): 3 sessions, flat.
- Pass 10 L1 (`safe_merge: REFUSE: PR <n> is not OPEN`): 2 sessions, flat. Pass 10 is still an open draft (#2221).
- Corpus: 140 dead cites (+1 on pass 10), 115 stale verifications (flat). Orphans 52 (+7), 0 awaiting a fate. Not isolated.

## Not proposed (watch)

- `eval: line <n>: syntax error: unexpected end of file` (4 sessions, 5 hits): newest example 2026-10-28; unbalanced quotes in long inline shell. Covered by memory `long-inline-shell-goes-in-a-script-file` (pass 1 A1); no hit in the window.
- `Exit code: Node.js v<n>` (4 sessions, 19 hits): mixed causes (eval syntax, Playwright timeout, playwright package missing in a worktree scratchpad). No single fix.
- `No module named 'PIL'` (2 sessions: 2ff15ba6 2026-11-12, 5ce819e6 2026-10-15): the Mac's system python3 has no Pillow. Could become a memory if it repeats; unverified whether Pillow is meant to be installed.
- `SyntaxError: EOL while scanning string literal` (2 sessions, newest 2026-10-22): multiline replace strings in inline python. Same family as A1.
- Corrections: 2 since 2026-11-12, both one session (22d2d282). No second session.

## False-positive shapes to drop from the scan

- User tool rejections (13 sessions): consent, not an error. Eighth pass in a row; exclude "The user doesn't want to proceed" in dream_mine.py.
- The dream scan's own transcript (775b12bd) matching error strings it printed. Exclude tool results from commands that run dream_mine.py.
- `Exit code: SKILL.md`, `[resize_window] Viewport emulation cleared`, `head: illegal line count`: repeats.
