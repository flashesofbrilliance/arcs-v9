<!--
session: arcs-config-harness-integration-g
branch: claude/arcs-config-harness-integration-b14b89
head: 093bbd3f
created_at: 2026-10-11T01:13:53Z
-->
> Added the 2026-10-10 evening to the existing night-moves digest, using the restored dependency sweep for the open-PR section.

## Shavasana
- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/handoff-night-moves-1010), receipts in digest: 0.
- **Inhale** (what came in): 0 falsification rows today, 4 dissent markers, 1 unconfirmed markers in the day's records.
- **Breath balance**: mirror (inhale, no exhale).
- **Sycophancy check**: agreement 11 / dissent 5 (ratio 1.83) → OK: dissent present.
- **Cold re-read (canary on the draft frag7.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._
- Exhale reads 0 because its scope is this handoff branch; the session merged #1167.
- Attachment release: narrowed "skipped two runs in a row" to today's two digest runs (the 10-09 pulse was not checked). Somatic: not asked. Disposition: release.

## Goal
Keep the day's ledger whole: add to an existing digest, never overwrite another run's record.

## Changed
- #1167 merged (`cce0a774`): `_STATE/night-moves/2026-10-10.md` evening update (#1151 to #1163: main-checkout salvage and drift warning, backlog state gate, atlas spec v0.3, sweep and auditor restored). Receipt `2026-10-10--night-moves-evening-update-pr1167--ZH`.

## State
- `scripts/dependency_sweep.py` ran on main at 21:06: 1 open PR (#730), parallel-safe, no blocking roots.
- The integrity gate refused the first commit because the digest cited a salvage-branch commit not on origin/main; the digest now names it by branch.
- Counterpart pulse and model drift check were not run (pulse skipped; no ANTHROPIC_API_KEY in shell).

## Decisions
- Name unmerged work by branch, not by SHA, in records that must pass the integrity gate.

## Open
1. Zach: approve the tool prompts in the "Held dependency exceptions watch" run.
2. Zach: confirm the better-sqlite3 bump (#557) was an approved dependency change (risk register).
3. Sort the salvaged uncommitted files on `claude/falsifiable-position-criteria-inltlk-local-salvage` against today's main; do not delete that branch first.

## Next action
Run the counterpart pulse fresh in a new session (skipped in both of today's digest runs).

## Cold-start
- Digest: `_STATE/night-moves/2026-10-10.md`
- `python3 scripts/dependency_sweep.py`; `scripts/night_moves_gather.sh 2026-10-10`
