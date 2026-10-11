<!--
session: claude-handoff-config-main-checkout
branch: claude/handoff-config-main-checkout
head: 2a3adb7b
created_at: 2026-10-11T01:09:18Z
-->
### Shavasana — handoff pause, 2026-10-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-config-main-checkout), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 9 / dissent 1 (ratio 4.5) → THIN: high agreement, little dissent.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

Attachment release: kept all claims; downgraded "resolution rule" to experiment-only (no Claude Code doc found stating it). Somatic: not asked. Disposition: release (THIN dissent noted).

> Found and fixed the class "worktree sessions run stale Claude config from the main checkout": verified by experiment that project skills, commands, agents and settings.json hooks all load from /Users/zharris/arcs-v9 (CLAUDE_PROJECT_DIR points there), salvaged that checkout's dirty work, moved it to origin/main, and added a session-start tripwire.

## Goal
Every worktree session runs the Claude config (skills, commands, agents, hooks) that is on origin/main.

## Changed
- #1156 merged (`374d409c`): session-start drift check for skills and commands in the main checkout, plus an AGENTS.md gotcha 14 note. Receipt `2026-10-10--project-skills-drift-tripwire-pr1156--ZH`.
- #1162 merged (`28d96741`): the check also watches agents. Receipt `2026-10-10--skills-drift-agents-pr1162--ZH`.
- Main checkout dirty work (13 files) committed as `b5c41786` on branch claude/falsifiable-position-criteria-inltlk-local-salvage; main checkout moved to detached origin/main.

## State
- Main checkout clean and detached at origin/main; the drift check is silent.
- Hooks probe: a tagged Bash hook fired only from the main checkout's settings.json; both probes reverted.
- Salvage branch holds unported work (handoff/memory edits, memory_index_sync.py, epic-migration-plan.md).

## Decisions
- Keep the main checkout detached at origin/main (main is checked out in another worktree), and warn rather than auto-move it, since moving can strand uncommitted work.

## Open
1. Triage the salvage branch: chip task_e553e591 "Triage salvaged main-checkout dirty work".
2. The main checkout falls behind whenever main advances; re-detach when the warning fires.

## Next action
Start chip task_e553e591 to classify and port the salvaged work.

## Cold-start
- /handoff-pickup; then `git -C /Users/zharris/arcs-v9 status` and `scripts/project_skills_drift.sh .` from your worktree.
- Memory `claude-config-resolves-from-main-checkout`.
