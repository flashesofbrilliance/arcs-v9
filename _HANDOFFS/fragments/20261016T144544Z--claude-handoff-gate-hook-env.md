<!--
session: claude-handoff-gate-hook-env
branch: claude/handoff-gate-hook-env
head: b51bfa44
created_at: 2026-10-16T14:45:44Z
-->
> Molted the integrity-gate fragment into v3.137.0, then fixed the gate's foreign-sha lookup reading the wrong repo inside the pre-commit hook.

## Goal
Keep CLAUDE.md citations verifiable by the integrity gate with zero WARN, in the hook as well as by hand.

## Changed
- #1406 merged (`b6246512`): molt of the integrity-gate fragment into handoff v3.137.0. Receipt `2026-10-16--handoff-molt-v3.137.0-pr1406--ZH`.
- #1408 merged (`b51bfa44`) after both checks passed: the foreign-sha lookup in scripts/integrity_gate.py drops GIT_* env vars, because the hook's GIT_DIR overrode `git -C` and read arcs-v9. Receipt `2026-10-16--integrity-gate-hook-git-env-pr1408--ZH`.

## State
- ret-rfp-intelligence 175afe2 verifies as foreign OK with no env, with GIT_DIR, and with GIT_DIR plus GIT_INDEX_FILE; a typo sha on a named-repo line still WARNs.

## Decisions
- Strip GIT_* for the one sibling-repo subprocess only, so the rest of the gate keeps the hook's index view.

## Open
1. Add the gate's foreign-sha cases (found, typo, unnamed hex, repo not cloned, GIT_DIR set) to a test file; still run by hand.

## Next action
Add a self-test for the integrity gate's foreign-sha lookup, including the GIT_DIR case.

## Cold-start
- `GIT_DIR=$(git rev-parse --git-dir) python3 scripts/integrity_gate.py CLAUDE.md` should show 175afe2 as foreign OK.

### Lessons
- A tool that shells out to another repo from a git hook must clear GIT_DIR and GIT_INDEX_FILE, or `git -C` is silently ignored.

### Notes: Shavasana

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-gate-hook-env), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 1 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 2 / dissent 1 (ratio 1.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag3.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Attachment release: kept all claims; both merges, their checks and receipts were read back this session. Somatic: not asked. Disposition: release.
