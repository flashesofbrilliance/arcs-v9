---
name: nci-scoring
description: Score a code change/commit/diff against the ARCS Commit-NCI rubric (ADR-033) and its thresholds. Use when the user asks to "score this," "what's the NCI," rate a diff/commit/PR before committing or merging, or references NCI, drift, or the >=50/>=45 thresholds. Scores CODE CHANGES, not compass decisions (that is the product nci_score, a different thing).
---

# NCI Scoring (Commit-NCI)

Makes the ARCS **Commit-NCI** gate portable: any surface — chat, Cowork, Claude Code — scores a code
change the same way, so numbers stay comparable to `[NCI:XX]` history and the drift sentinel.

> **Source of truth:** `_DECISIONS/ADR-033-commit-nci-rubric.md`. The rubric below is a MIRROR of that
> ADR. If they ever disagree, the ADR wins — update this file from it, never the reverse.

> **Do not confuse with the product `nci_score`.** Commit-NCI scores a *code change*. The product's
> Network Coherence Index (5 lenses in `runtime/specs/dewy-receipt-schema-v1.md`) scores a *decision run
> through the compass*. Same five-lens spirit, different subject. If the user wants a decision scored, this
> is the wrong skill.

## When to use

The user wants a change scored: "score this diff," "what's the NCI on this," "is this mergeable," before a
commit or merge, or any mention of NCI / drift / the thresholds. If no change is in front of you, get it
first (`git diff --cached` when staged, else ask for the diff).

## The rubric (mirror of ADR-033 — 0–100)

| Lens | Weight | What earns points |
|---|---|---|
| Correctness | 30 | Does what the message claims; build/typecheck/tests sound; no obvious breakage. |
| Coherence | 25 | Fits architecture + canon (inline styles only, no new deps, WORLD/AGENTS rules); no contradiction. |
| Consequence | 20 | Downstream handled — migrations, cross-repo sync, env/secrets, RLS, load-bearing docs. |
| Clarity | 15 | Atomic, single-purpose; no unrelated edits riding along. |
| Craft | 10 | Naming, no debug cruft, comments where load-bearing, commit-message quality. |

**Thresholds:** ≥50 commit · ≥45 merge-to-main · >10-pt drop vs previous scored commit in a session =
drift · <50 → do not commit, report weakest lens + the 1–2 edits to clear 50.

**`[NCI:SKIP <reason>]` is legitimate** for pure docs/handoff/chore/formatting/dependency/mechanical
commits — scoring those is false precision. A real score is expected when the diff changes runtime
behavior under `src/`, `prisma/`, `operators/`, or `runtime/`.

**Anti-false-precision:** this is a gut-check on a five-lens frame, not a measured metric. Don't tune
digits; if torn, pick the lower number and name the weak lens.

## How to score

1. Read the change (diff/commit/PR); get it first if not provided.
2. Score each lens with a one-line justification.
3. Sum to an integer 0–100.
4. If you have the prior scored commit, compute the session delta for the drift check.
5. Output the format below. If the diff is pure docs/chore, recommend `[NCI:SKIP <reason>]` instead of a score.

## Output format

```
NCI: XX/100  — [✅ commit-ready | ⚠️ merge-only | 🔴 below bar | ⏭️ SKIP-eligible: <reason>]

| Lens        | Score | Note |
|-------------|-------|------|
| Correctness | xx/30 | ...  |
| Coherence   | xx/25 | ...  |
| Consequence | xx/20 | ...  |
| Clarity     | xx/15 | ...  |
| Craft       | xx/10 | ...  |

Drift: <none | ⚠️ dropped N pts from previous scored commit>
Verdict: <commit / hold — with the 1–2 fixes to clear 50 if below>
```

When invoked inside Claude Code with staged changes, offer to hand off to `/nci-commit` to score-and-commit
in one step rather than duplicating commit logic here.
