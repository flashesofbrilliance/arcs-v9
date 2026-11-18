---
title: Pre-registration, gate shadow eval (did the wrong answer reveal itself)
date: 2026-11-17
status: PRE-REGISTERED (rules fixed before the first count)
tool: scripts/gate_shadow_eval.py
---

# Pre-registration: gate shadow eval

**Question (Zach, 2026-11-17).** When a gate is wrong, does history show it? Only in the shadow, the ma: count a verdict as wrong only when later events exposed it. Everything else stays unrevealed and is never guessed into a class.

**Trigger.** Two gate errors surfaced on 2026-11-17: the kit ledger check blocked a correct merge (PR 2248, fixed by PR 2346), and the integrity gate flagged a night-moves digest that correctly labeled its cites as branch-only.

## Observation unit

A commit reachable from `origin/main`. Read-only: git history only, no network, never blocks anything (shadow).

## Rules (fixed now)

**Bypass event.** A commit whose message records a gate override: `--no-verify`, `INTEGRITY_GATE_BLOCK=0`, `--allow-hold`, or `bypass` next to a gate name. The gate is attributed from the message: an override env var names its gate; otherwise a `scripts/<name>.py` mentioned in the message, or one of the known phrases ("kit ledger", "integrity gate"). No attribution means gate `unknown`.

**Revealed false positive (the gate blocked; it was wrong).** A bypass event where all of these hold:
1. the bypassed commit is on main (it landed);
2. it was not reverted (no later main commit says "This reverts commit <sha>");
3. the attributed gate's script was changed by a later main commit (the gate itself was corrected).

A bypass that meets 1 and 2 but not 3 is `bypass-held`: the gate was overridden and nothing has corrected it yet. It is counted, not classified.

**Revealed false negative (the gate passed; it was wrong).** A main commit that a later main commit reverts ("This reverts commit <sha>"), when the reverted commit carries no bypass. Something that every gate let through was undone.

**Unrevealed.** Every other commit. Reported as a count, never as "correct".

## Predictions (before the first run)

- At least 1 revealed false positive: the kit ledger check (a30eb252 bypass, kit_periodic_table.py changed later by 5db6ae8e).
- The integrity gate bypass (4b08bc94) is `bypass-held`: its gate is not fixed yet.
- Reverts on main are rare (merge-commit-only repo): predicted 0 to 5 revealed false negatives.

## What this cannot see

- Inliers: a wrong pass that was never reverted. The eval says nothing about them; the unrevealed count is their upper bound.
- A false positive that someone fixed by editing the record instead of bypassing the gate.

## Result, v1 (as registered, 2026-11-17, origin/main 39b5c405, 7,299 commits)

bypass-held 65 · revealed-fp 30 · revealed-fn 1 · unrevealed 7,203. Predictions: kit ledger revealed FP (held), integrity bypass held (held), 0 to 5 revealed FN (held, 1).

Reading four sampled messages showed the eval making the errors it was built to catch:

| Eval error | Example | Kind |
|---|---|---|
| Negation read as a bypass | `3b76ad9e` "fixed the surface, never --no-verify" | FP |
| A gate documenting its own override read as bypassing it | `dc97fff3`, the commit that wired `INTEGRITY_GATE_BLOCK=0` | FP |
| A gate blamed because it is named elsewhere in the message | phrase anywhere in the body | misattribution |
| "The gate script changed later" is too loose: a busy script reveals every old bypass | `integrity_gate.py`, 8 later edits | FP |
| Conventional `revert(scope):` commits name no sha and are invisible | `b0db00b7`, `701e5127`, `38321d62`, `3ffa9421`, `c6ed1746` | FN |

## Amendments (v2, 2026-11-17, after the v1 count; v1 numbers above stand)

- A1: an override token preceded on its line by never / without / not / no / instead of does not count.
- A2: a commit that edits a gate's own script, or the pre-commit hook that wires every gate, documents it; it is not a bypass of it.
- A3: a gate is attributed only from the line that carries the override.
- A4: revealed FP needs a later `fix`-typed commit to the gate's script within 30 days.
- A5: a `revert(...)` / `Revert "..."` subject with no "This reverts commit" sha is counted as revert-unlinked (not attributed to a gate).

## Result, v2

bypass-held 58 · revealed-fp 28 · revealed-fn 1 · revert-unlinked 5 · unrevealed 7,207. Same three predictions hold. Live test: the integrity gate fix in the same PR (a `fix(...)` commit to `scripts/integrity_gate.py`) should flip the `4b08bc94` bypass from bypass-held to revealed-fp when the eval reads the branch.

## Amendment A6 (v3, 2026-11-17, after the live test)

The live test flipped the two predicted bypasses (`94ac0182`, `4b08bc94`) but also two older integrity bypasses. A manual replay (the fixed gate run on each bypassed record) split them:

| Bypass | Fixed gate on the bypassed record | Revealed by this fix? |
|---|---|---|
| `94ac0182` night-moves 11-16 digest | WARN (passes) | yes |
| `4b08bc94` same digest via a merge | WARN (same record) | yes |
| `8d456294` `_SEEDS` ledger cites | still FAIL | no, A4 over-claimed |
| `1218fc33` files already on main, a moved file | different cause | no, A4 over-claimed |

A6: a later fix to a gate is a lead, not proof. An A4 match is reported as `fix-followed`; `revealed-fp` needs a replay of the fixed gate on what was bypassed. No replay engine exists yet (backlog row `gate-shadow-eval-replay`), so v3 reports zero machine-revealed FPs and the two replayed by hand above.
