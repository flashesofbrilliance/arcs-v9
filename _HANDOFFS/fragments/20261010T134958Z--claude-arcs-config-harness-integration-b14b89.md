<!--
session: arcs-config-harness-integration-c
branch: claude/arcs-config-harness-integration-b14b89
head: 3740d026
created_at: 2026-10-10T13:49:58Z
-->
## Changed
- #1137 merged (77b04de5): 2026-10-09 night-moves digest late update (added to, not overwritten) + backlog row `remove-mysql2-override-on-prisma-release`. Receipt `2026-10-09--night-moves-late-update-pr1137--ZH`.
- #1138 merged (3defe76b): held-exceptions check. `runtime/specs/held-exceptions.json` registers every npm override and Dependabot ignore with a reason and a `lift_when`; `scripts/held_exceptions.py check` (pre-commit + CI gates step) fails on an unregistered hold or stale entry; `watch` reports LIFT/HOLD from the newest STABLE npm version. Seeded: mysql2 override (#1131), eslint major ignore (#556). Receipt `2026-10-09--held-exceptions-check-pr1138--ZH`.
- Local scheduled task `arcs-prisma-release-watch` renamed "Held dependency exceptions watch" (Mondays ~9:14): runs `held_exceptions.py watch` against origin/main via `git archive` into a temp dir; report-only.

## State
- watch today: both holds HOLD (prisma 7.10.0 pins mysql2 3.15.3; eslint-plugin-react 7.37.5 peer stops at ^9.7). Prisma `latest` dist-tag is 8.0.0-rc.22, which is why watch reads the newest stable instead.
- Python side: all four Python projects use `>=` floors only, no pins or overrides; nothing to register.
- The new pre-commit hook is NOT active locally yet: `core.hooksPath` = `/Users/zharris/arcs-v9/scripts/git-hooks` (main checkout's copy), which runs whatever branch the main checkout is parked on. CI enforces the same check meanwhile.
- First manual run of the reworded task (session local_bfa28a5d) was waiting, likely on a tool-approval prompt (git, tar, python3), at handoff time; the earlier stuck run (local_c65a4a97) was stopped.

## Decisions
- Chose the held-exceptions registry + watch over a CI "canary removal" job (try dropping each hold, PR if green); the canary stays a possible later upgrade.
- Watch reads origin/main via git archive, never the main checkout working tree.

## Open
1. Zach: approve the tool prompts in the "Held dependency exceptions watch" run so Monday runs unattended.
2. Move the main checkout onto current main (or otherwise refresh `scripts/git-hooks`) so the held-exceptions pre-commit hook goes live locally.
3. Optional: the scheduled task runs on Opus; a cheaper model would do for one shell command.
4. Optional later: CI canary job that tries removing each hold and opens a PR when the build stays green.

## Next action
Approve the watch run's tool prompts; then nothing pending from this session.

## Cold-start
- `python3 scripts/held_exceptions.py check` / `watch`
- `runtime/specs/held-exceptions.json`; add an entry whenever adding an override or Dependabot ignore.
