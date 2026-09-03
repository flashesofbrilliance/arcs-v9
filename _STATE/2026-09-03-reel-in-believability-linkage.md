# Reel-in sweep → believability-ledger linkage (findings receipt)

**Date:** 2026-09-03 · **Session:** kind-lamport-dd294a · **Feeds:** believability-ledger
external-resolver calibration (`believability_ledger.py` @867d7fd0, branch
`claude/determined-herschel-e59b29` — NOT yet on main).

## What this closes

A prior sweep separated genuine "float→reel-in" events (a staked claim caught/corrected before
it became durable error) from keyword noise, across the corpus and git history. This receipt
records feeding the git-grounded subset into the believability ledger **honestly** — i.e. without
violating the ledger's external-adjudication invariant (git is the judge; Claude does not grade
Claude's own corpus).

## Method

`scripts/corrections_link.py` recovers the claim→correction sha-link the ledger leaves unscored:
for each correction commit it blames the lines the correction REMOVED against the parent tree,
finds the introducing commit(s), and — when an introducer carries a numeric `[NCI:NN]` tag —
emits a candidate reel-in link. High-precision by design; candidates are emitted for **human
ratification**, never auto-scored (judgment stays human-owned).

## Findings

- **19 candidate links** at strength ≥ 0.30. After excluding **NCI>100** (accumulator convention,
  uninterpretable as a probability — the ledger's own rule) and deduping cross-branch sha twins:
  **3 logical reveal events / 4 staked claims** are scorable (all low-ruin: a logo, a name, a
  timestamp).
- The ledger's own `GitRevertResolver` **missed the logomark reversal** because it was a *manual*
  `revert(ui):` with no `This reverts commit <sha>` trailer. Blame-linking recovered it — this is
  the concrete value of the companion.

## Re-score (ledger formulas, ratified subset: logomark p=0.96/0.95 + witness-ts p=0.53)

| | resolved | reel-ins | base-rate hold | Brier (w) | skill vs base | seaworthy |
|---|---|---|---|---|---|---|
| Before | 188 | 0 | 1.0000 | 0.033 | −0.033 | ❌ |
| After  | 188 | 4 | 0.9787 | 0.052 | −0.031 | ✅ (mechanical only) |

## Honest verdict — the ✅ is an artifact; do NOT ship `seaworthy: true`

1. The "4 reel-ins" are **2 logical claims** (logomark add + swap), **double-counted by
   cross-branch sha twins** both present in `git log --all`. Deduped → 2 → under the ≥3 gate →
   **non-seaworthy**. The flag rides on branch duplication of one design reversal.
2. The ratified **witness confabulated-ts** claim (the cleanest genuine miss) **did not match the
   ledger's resolved 188** — its sha isn't in the scored set (branch-locality gap). The
   highest-integrity reel-in did not even land.
3. All recovered reel-ins are **low-ruin copy/design** reversals, not high-consequence decision
   failures.

**Real signal that IS legitimate:** the archaeology dropped base-rate below 1.0 (first non-degenerate
reel-in signal) and showed stated confidence carried **negative** information on the recovered set —
the reeled claims were the *highest-confidence* ones (0.96/0.95). But the corpus remains
**data-floor-limited**: exhaustive linking yields only ~2 low-ruin staked reel-ins. The seaworthy
path is the **receipt→outcome loop with external adjudication** (ledger levers 2/3), not more git
mining.

## Artifacts

- `scripts/corrections_link.py` — reusable, stdlib, read-only (this commit).
- `/tmp/corr-links.jsonl` — candidate links (regenerate: `python3 scripts/corrections_link.py --json ...`).
- `/tmp/ledger-ratified.json` — re-scored ledger, flagged artifactual (not committed; ephemeral).

## Co-merge debt

`corrections_link.py` complements `believability_ledger.py`, which is on branch
`claude/determined-herschel-e59b29` (@867d7fd0), **not on main**. These must land on main
**together** or the companion is orphaned. Do not merge this alone to main without the ledger.
