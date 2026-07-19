# /nci-commit

> Score the staged diff against Commit-NCI (ADR-035), then commit with the `[NCI:XX]` tag — or
> `[NCI:SKIP <reason>]` for a mechanical/docs change. One step instead of remembering to tag.
> Billing tier: SUBSCRIPTION (interactive).

> **Rubric source of truth:** `_DECISIONS/ADR-035-commit-nci-rubric.md`. Do not inline a different
> rubric here — cite the ADR / the `nci-scoring` skill so command and skill never disagree.

## Steps

1. **Get the change:** `git diff --cached`. If nothing is staged, stop and say so (don't score an empty diff).
2. **Classify:** is this a pure docs/handoff/chore/formatting/dependency/mechanical change (no runtime
   behavior under `src/`, `prisma/`, `operators/`, `runtime/`)?
   - **Yes** → this is `[NCI:SKIP <reason>]`. Skip scoring; go to step 5 with the SKIP tag.
   - **No** → score it (step 3).
3. **Score** with the `nci-scoring` skill (five lenses, mirror of ADR-035). Produce the score table.
4. **Gate:**
   - `< 50` → **do NOT commit.** Report the score, the weakest lens, and the 1–2 concrete edits that would
     clear 50. Stop.
   - `≥ 50` → proceed.
   - Compute the drift delta vs the previous scored commit; if `> 10-pt drop`, warn before committing.
5. **Commit:**
   ```
   git commit -m "type(scope): imperative [NCI:XX]

   <body if load-bearing>

   Co-Authored-By: Claude <model> <noreply@anthropic.com>"
   ```
   Use `[NCI:SKIP <reason>]` for the mechanical path. Never invent a score to clear the bar — that defeats
   the gate (ADR-035 anti-false-precision clause).

## Output

The score table (or SKIP rationale), the drift line, then the commit SHA. Do not push unless asked.
