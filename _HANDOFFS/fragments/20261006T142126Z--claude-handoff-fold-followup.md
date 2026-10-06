<!--
branch: claude/handoff-fold-followup
head: 1c62a544
created_at: 2026-10-06T14:21:26Z
-->
> **Handoff fold #921 merged (`78c6e949`): four fragments folded to v3.107.0-v3.110.0; two follow-up chips spawned.**
> Receipts `2026-10-06--handoff-fragment-pr914--ZH`, `2026-10-06--handoff-fold-pr921--ZH`.

## Done
- #914 (`9bf8ca27`): fragment for the #906 constant-time jobs token session (that block folded as v3.108.0, now archived).
- #921: first fold collided with a hand-written v3.106.0 on main (cf0bf7f1 / #923); reset to origin/main and re-folded.
  v3.110.0 + v3.109.0 live; v3.105.0-v3.108.0 relocated to `_ARCHIVE/handoffs.md`.

## Open (next session)
1. Chip task_7f5ac139 (running): v3.109.0 cites `abb6aedb`, which lives only on unmerged `claude/model-registry-drift-gate`.
2. Chip task_c9678ac7: stale handoff commands still teach direct CLAUDE.md writes
   (`~/.claude/commands/arcs-handoff.md`, main checkout's `.claude/commands/handoff.md`); add a pre-commit gate.

## Lessons
- `/handoff` can load a stale command copy: check it says "fragment" before following it.
- A fold PR goes stale fast when other sessions merge handoffs; re-fold on fresh main instead of resolving CLAUDE.md conflicts by hand.
