# ADR-035 — Commit-NCI Rubric (ratify the `[NCI:XX]` commit gate)

> **Status:** DECIDED
> **Date:** 2026-07-19
> **Commit:** (set at merge)
> **Y:** GREEN / MEDIUM / REVISIT
> **Supersedes:** the informal, undocumented `[NCI:XX]` convention

## D — The Decision

**Sharp question:** The `[NCI:XX]` commit tag has been used for months with **no documented rubric** —
it lived only as numbers in commit history, and had decayed to the point that recent commits are
effectively all `[NCI:SKIP]`. Meanwhile "NCI" *also* names the product's canonical 5-lens decision score
(`nci_score`, `runtime/specs/dewy-receipt-schema-v1.md`). Do we (a) retire the commit tag, (b) ratify a
real rubric for it, or (c) collapse it into the product score?

**Decision:** **(b) Ratify a real commit-NCI rubric**, defined here as the single source of truth. The
`nci-scoring` skill and the `/nci-commit` + `/drift-check` commands import *this* ADR; they do not carry
their own rubric. Commit-NCI scores **code changes**; the product `nci_score` scores **decisions run
through the compass**. They are deliberately parallel (same five-lens frame) but MUST NOT be conflated —
a commit is not a decision receipt.

## E — Entity / System

- `_DECISIONS/ADR-035-commit-nci-rubric.md` — **this file is the rubric's only source of truth.**
- `.claude/skills/nci-scoring/SKILL.md` — mirrors the rubric; header points back here.
- `.claude/commands/nci-commit.md`, `.claude/commands/drift-check.md` — same.
- Commit messages: `type(scope): imperative [NCI:XX]` or `[NCI:SKIP <reason>]`.

## The rubric — Commit-NCI (0–100)

Five lenses, parallel to the product's clarity/conviction/coherence/consequence/cadence, adapted to a
code change. Score each, then sum:

| Lens | Weight | What earns points |
|---|---|---|
| **Correctness** | 30 | Does what the message claims; build/typecheck/tests implications sound; no obvious breakage or regressions. |
| **Coherence** | 25 | Fits existing architecture + canon — inline styles only, no new deps without asking, WORLD.md/AGENTS.md rules honored; no internal contradiction. |
| **Consequence** | 20 | Downstream effects understood and handled — migrations, cross-repo sync, env/secret impact, RLS, docs updated where load-bearing. |
| **Clarity** | 15 | Atomic and single-purpose; no unrelated edits riding along. |
| **Craft** | 10 | Naming, no debug cruft, comments where load-bearing, commit message quality. |

**Thresholds (carried from the prior convention):**

| Bar | Rule |
|---|---|
| **≥ 50** | Clears the bar to **commit**. |
| **≥ 45** | Floor to **merge to main**. |
| **> 10-pt drop** | vs. the previous *scored* (non-SKIP) commit in a session → flag **drift**. |
| **< 50** | Do NOT commit. Report score, weakest lens, and the 1–2 edits that would clear 50. |

> ⚠️ **Open calibration question (the REVISIT):** the commit bar (≥50) is *higher* than the merge bar
> (≥45), which is inverted from intuition (merge should be the stricter gate). This is carried verbatim
> from the undocumented convention — it may be intentional (per-commit rigor, relaxed batch-merge) or a
> historical typo. **Confirm or correct at the first revisit.** Flagging rather than silently "fixing."

## When `[NCI:SKIP]` is legitimate (not theater)

Scoring a change that encodes **no engineering judgment** is false precision. A commit MAY tag
`[NCI:SKIP <reason>]` when it is purely: docs, handoff, chore, formatting, dependency bump, or a
mechanical rename. This legitimizes the current all-SKIP state for the recent doc/chore-heavy sessions.

**A real score is expected** when the diff changes runtime behavior under `src/`, `prisma/`,
`operators/`, or `runtime/` — anything a user or the pipeline can observe.

## Anti-false-precision clause (ties to `_CANON/trust-contract.md`)

Commit-NCI is a **disciplined gut-check on a five-lens frame, not a measured metric.** Do not tune
digits. If torn between two numbers, pick the **lower** and name the weak lens. The number's job is to
force the five questions, not to be mathematically precise — the same honesty the trust-contract requires
of the product `nci_score`.

## W — Window

QUARTER. Revisit after ~20 *scored* (non-SKIP) commits, or at the first drift flag — whichever comes
first — to calibrate weights and resolve the commit>merge threshold inversion.

## Y — Gate

**GREEN / MEDIUM / REVISIT.** The decision (ratify, single-source, parallel-not-conflated) is solid.
Conviction is MEDIUM because the specific weights and the threshold inversion are inherited, not yet
outcome-validated — hence the explicit revisit trigger.

## Consequences

- The `nci-scoring` skill and commands become buildable against a real definition instead of a placeholder.
- Future sessions have one rubric to cite; command and skill cannot disagree.
- If a future session finds the weights mis-calibrated, it amends **this ADR** — not the skill copy.
