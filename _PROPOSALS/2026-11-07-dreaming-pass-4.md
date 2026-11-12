# Dreaming pass 4: KINTSUGI repeat classes plus the 2-day scan (2026-11-07)

PROPOSALS ONLY. Nothing here is applied. Zach rules each row ACCEPT, AMEND or REJECT.

## Header

- Commands (run 2026-11-07 ~01:20 EST in worktree /tmp/dream-2026-11-07 off origin/main 49a2a63f):
  - `python3 scripts/dream_mine.py --days 2 --min-sessions 2`: 71 transcripts, 36 error clusters (>= 2 sessions), 51 corrections
  - `python3 scripts/dream_mine.py --corpus --stale-days 45`: 1335 docs, 131 dead cites, 107 verifications older than 45d, 0 near-duplicate memory pairs
  - `python3 scripts/orphanage.py --check`: 41 orphans, 7 cited, 0 unregistered, 0 awaiting a fate
- Extra residue: ~/Downloads/gauntlet-2026-11-06/RESIDUE-for-dream-2026-11-06.md (first dreaming pass to cite it), cross-checked against the claude.ai Project ledger claude/KINTSUGI.md (rows G1 to G42, read this session).
- Note: the residue file numbers two rows G36 and G37; the ledger renumbered them G39 and G40 (collision fix, see G39). This file uses ledger numbers.
- Slice: dropped everything ruled in passes 1 to 3 (A1 to A7, B1 to B5, C1 to C6, R1, R2, D1 to D4). No open claude/dream-* PR exists (`gh pr list --search "dreaming pass" --state open` returned none).
- Ranking: by how many past KINTSUGI rows the change would have prevented (counted from the ledger's Break and Guard cells).

## Proposals

| id | Pattern | KINTSUGI rows it would have prevented | Existing guard | Proposal | File it would edit | Risk |
|---|---|---|---|---|---|---|
| E1 | Partial search reported as absence ("not built", "not on disk", "none", "cleared") | 9: G1, G10, G18, G24a, G28a, G30, G33, G34, G42 | CLAUDE.md:93 says run `/prior-art` before planning (planning only, not absence claims); AGENTS.md:140 covers Hermes state.db only; ROOTSTRAP v2 FACT-CHECK "Absence" line lives in the Project, not the repo | Add one hard rule next to CLAUDE.md:93: "Before any claim that something is missing, unbuilt or clean: search file CONTENTS by concept words across arcs-v9 (working tree plus `git log --all -S`), arcs-decision-receipts and RET, with stderr visible and one sanity probe that must hit; then name every place searched. Not wired and not built are different claims." Optional mechanical form (unverified feasibility): `prior_art.py --absence <concept>` that runs that sweep and prints the scope line. | CLAUDE.md (rule); scripts/prior_art.py (optional flag) | Slower answers on trivial lookups; mitigated by scoping the rule to absence claims only |
| E2 | Assumed tool or file contract (path limits, connector type, pathspec syntax, file shape, schema field, docstring) | 7: G11, G24b, G29c, G29d, G30 (pathspec), G39, G40; plus G42's misdescription of orphanage.py | None in repo (grep for "tool contract", "before the first call" in CLAUDE.md and .claude/rules: 0 hits) | New rule file `.claude/rules/precall-contract.md`, three lines: (1) before the first call of a tool new to the session, read its description for path, scope and source limits; (2) print a data file's top-level shape and read its schema before writing an edit or count against it; (3) when a doc names a limit, test the risky call path on one item before building around it. | .claude/rules/precall-contract.md (new) | Rule-file sprawl; could fold into an existing rules file instead if Zach prefers |
| E3 | Built or improvised while an existing tool already did the job; tools built without a trigger go orphan | 4: G33, G34, G41, G42 (residue adds orphaned tools: dream, surface_watch.py, prospect-scout) | `.claude/skills/tool-forge/SKILL.md` forge steps 1 to 8 end at Commit; grep for schedul, cron, trigger, wire, orphan in that file: 0 hits. orphanage.py reports 41 orphans, 7 cited | Add tool-forge step 9: "Wire it. Name the trigger that will run it (scheduled task, hook, skill, slash command or another tool's call) and land that wiring in the same PR, or register it with `scripts/orphanage.py --intake` and a fate. A tool with no trigger is not done." | .claude/skills/tool-forge/SKILL.md | Overhead for genuine one-shot tools; the intake path covers those |
| E4 | A term from Zach's notes applied to the wrong scope (audit-fee credit mapped to the nearest step) | 1: G35 | None (grep for "credit" plus "audit fee" across the repo: 0 hits; MEMORY.md has no credit line) | New memory line: "Audit-fee credit applies only to the later full build, never to the light-audit ladder steps; any change that touches price is shown with its arithmetic before it is proposed." | MEMORY.md, or the matching feedback memory under ~/.claude (location unverified) | Low; pricing terms may change per deal, so scope the line to the current ladder |
| E5 | Recall gap: pass 1's A1 class (heredoc / `bash -c` quoting, `eval: unexpected EOF`) still fired in 2 new sessions after 11-03 (8baff32b, 2c88ef63) | 0 KINTSUGI rows (transcript-only) | Pass 1 proposed a feedback memory; whether it was accepted and filed is unverified (no heredoc line in repo MEMORY.md; ~/.claude memory not readable from this pass) | If A1 was accepted, sharpen its hook to the trigger words (multi-line, heredoc, quotes inside `bash -c`); if it was never filed, re-surface A1 for a ruling. | ~/.claude memory (unverified path) | Low |

## Not proposed (already guarded)

- Skipped boot (G21, G22, G23, G37, G38: 5 rows): mechanized by BOOT.md and R-013 in the Project; no repo change needed. Watch for a sixth repeat as the test of R-013.
- Connector-first before asking Zach (G9, G31): already in ROOTSTRAP v2 Chronos. Repo-side copy would duplicate it.

## Corpus notes (for Zach to triage, not proposals)

- MEMORY.md at the repo root is 36,768 bytes; scripts/memory_index_sync.py sets BUDGET = 24,576. Unverified whether that budget applies to this file or only to the harness memory index under ~/.claude. Check before any trim.
- 131 dead cites and 107 stale verifications remain; pass 3 (D1 to D4) already ruled the classes. No new class found in this window; the per-item diff against pass 3 was not computed.

## False-positive shapes to drop from the scan

- "The user doesn't want to proceed with this tool use" (12 hits, 11 sessions): a user rejection, not a tool failure. dream_mine.py should exclude it.
- "Tool permission request failed: AbortError: Tool permission stream closed" (3 sessions, all 11-06): harness transport, not actionable here.
- `--days 2` still pulls clusters whose first examples date to July and October (window filters by transcript, not by event timestamp). Consider filtering examples by ts.
