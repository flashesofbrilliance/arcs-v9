<!--
session: arcs-config-harness-integration
branch: claude/arcs-config-harness-integration-b14b89
head: 1a149911
created_at: 2026-10-09T20:08:56Z
-->
## Goal
Decide whether Every's compound-engineering plugin belongs in the ARCS harness; take only what it adds.

## Changed
- #1123 merged (cab0c99b): `/prior-art <job>` (`scripts/prior_art.py`, `.claude/commands/prior-art.md`) ranks memory, `_PATTERNS/`, ADRs and the tool catalog (idf-weighted keywords, stdlib, read-only) before planning; CLAUDE.md token-saving rules now ask for it. Receipt `2026-10-09--prior-art-preplan-lookup-pr1123--ZH`.
- #1131 open: npm `overrides` forces `mysql2@3.23.1` (prisma 7.10.0 pins 3.15.3), clearing Dependabot #23 (high) and #26 (medium). Local `prisma validate`, `prisma generate`, `npm run build` pass.
- Dependabot #22 (deepmerge-ts via @prisma/config) and #32 (braces, dev-only, no patch) dismissed as not_used, with reasons on each alert.

## State
- Compound-engineering plugin NOT installed: it duplicates agent-protocols, /code-review, /simplify, memory and handoff, and `/lfg` would bypass receipts, NCI commit format and page gates. Only its retrieval idea was borrowed.
- #1131 CI was green except `smoke` still pending at handoff time; Zach authorized merging when green.

## Decisions
- Borrow the compound-engineering idea (read past lessons before planning), not the plugin.
- Clear the mysql2 alerts with an override; dismiss deepmerge-ts and braces as unreachable instead of jumping to Prisma 8 RC.

## Open
1. Merge #1131 with `--merge` once `smoke` passes, then log a receipt covering the merge and the #22/#32 dismissals (not yet logged).
2. Remove the mysql2 override and revisit Dependabot #22 when Prisma 8 ships GA.
3. `/prior-art` does not index AGENTS.md; keyword matching misses some lessons (e.g. merge rules).

## Next action
Merge #1131 when CI is green and log its receipt.

## Cold-start
- `gh pr checks 1131`; `gh api 'repos/flashesofbrilliance/arcs-v9/dependabot/alerts?state=open'`
- `python3 scripts/prior_art.py "<job>"`
