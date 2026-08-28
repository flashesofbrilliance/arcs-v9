# Composite Signal Match (CSM) — Formula Specification

> **Status:** SPECCED — Phase 3 prep. Read alongside `audit-benchmark-plan.md` and
> `operators/audit_service/persistence.py` (`loadBenchmarkPairs`).

## Purpose

CSM is the single metric that answers: **how well does the operator pipeline's
output match the LLM's output on this receipt?**

It's the gate for the Path A → Path B decision. When CSM ≥ 0.65 on a sustained
sample, the operator pipeline is producing signal that agrees with the LLM enough
to consider replacing or augmenting the LLM's compositon with operator output
(Path B). Below 0.65, the disagreement is too large to trust the operator as a
compositor — it remains an audit layer only (Path A).

CSM is NOT a claim that the LLM is right and the operator is wrong, or vice versa.
It's a measure of *agreement*, not truth. The benchmark review (human) is what
determines who was right when they disagree.

## Inputs

CSM is computed per (traceId, operator) pair from the benchmark pair store. Four
inputs feed the formula:

### 1. alignment — how much the operator's output agrees with the LLM's output
on the dimensions that matter for this operator.

Per-operator alignment is computed from subtask-specific comparisons (see the
operator comparison map below). Each operator has its own set of comparable
subtasks, scored 0–1 per subtask, then averaged into a single alignment score.

### 2. delta — the magnitude of disagreement, normalized.

Delta captures how far apart the LLM and operator outputs are on the comparable
dimensions, regardless of direction. High delta = large disagreement. Computed
as 1 − normalized_distance(llm_output, operator_output) on the comparable
dimensions, so delta ∈ [0, 1] and higher = more agreement.

### 3. coherence_loss — how much the operator's output degrades the decision's
internal coherence relative to the LLM's compositon.

This is the operator-side analog of the LLM's `coherence_pct`. If the operator
pipeline produces a signal that's internally less coherent than what the LLM
composed, that's a cost to replacing the LLM with the operator. Computed from the
operator's own coherence metrics (e.g. SAGE's `coherence_law_score`, NCI grade)
relative to the LLM's `coherence_pct`.

### 4. severity — how consequential the disagreement is, weighted by the
decision's stakes and irreversibility.

Not all disagreements matter equally. A disagreement on a LOW-stakes, TWO_WAY
decision is lower severity than the same disagreement on a HIGH-stakes, ONE_WAY
decision. Severity is computed from the primitives' `stakes` and
`irreversibility` fields (which come from the compass intake, not the LLM).

## Formula

```
CSM = f(alignment, delta, coherence_loss, severity) ∈ [0, 1]

where:

  alignment   ∈ [0, 1]   — per-operator subtask agreement, averaged
  delta       ∈ [0, 1]   — 1 − normalized_distance (higher = more agreement)
  coherence_loss ∈ [0, 1] — operator coherence relative to LLM coherence
  severity    ∈ [0, 1]   — stakes × irreversibility, normalized

CSM = (alignment × 0.40) + (delta × 0.30) + ((1 − coherence_loss) × 0.20) + ((1 − severity) × 0.10)
```

### Weight rationale

- **alignment (0.40)** — the primary signal. If the operator agrees with the LLM
  on the dimensions that matter, that's the strongest case for Path B.
- **delta (0.30)** — the magnitude of agreement. Two outputs can agree on the
  comparable dimensions but still be far apart in raw value; delta captures that.
- **coherence_loss (0.20)** — the cost of swapping the LLM's compositon for the
  operator's. If the operator degrades coherence, that's a real cost even if it
  agrees on the dimensions being compared.
- **severity (0.10)** — the stakes adjustment. Lower stakes → lower bar for
  agreement to matter (because the cost of being wrong is lower). Higher stakes →
  the agreement needs to be more consequential to count.

The 0.10 severity weight is intentionally low — severity is a modifier, not a
driver. The benchmark is measuring agreement, not stakes-adjusted correctness.

## Threshold

**CSM ≥ 0.65** → the operator pipeline's output agrees with the LLM's output
enough to consider Path B (replacing or augmenting LLM compositon with operator
output) on this kind of decision.

**CSM < 0.65** → the disagreement is too large. The operator remains an audit
layer (Path A) for this decision class.

The 0.65 threshold is from the benchmark plan. It's a directional threshold, not
a bright line — the review cadence (weekly/monthly/quarterly) is where the
sample-level CSM trend gets evaluated, not individual pairs.

## Per-operator comparison map

Each operator has its own set of comparable subtasks. Alignment and delta are
computed per subtask, then averaged into the operator's alignment and delta.

### SAGE vs LLM

| Subtask | LLM source | Operator source | Comparison |
|---|---|---|---|
| NCI score | `llmOutput.nci_score` | `output.nci_score` | normalized difference |
| PCI score | (proxy from coherence_pct) | `output.pci_score` | normalized difference |
| HCI score | (proxy from coherence_pct) | `output.hci_score` | normalized difference |
| Signal classification | (derived from coherence + nci + macro_tags) | `output.signal_classification` | categorical match |
| Axiom compliance | `deriveAxiomsFromLlm` (llm_derived) | `output.axioms.*` | per-axiom match, averaged |
| Verdict | (from court verdicts / macro_tags) | `output.verdict` | categorical match |
| Somatic witness | (always default — no real data) | `output.somatic.witness_score` | excluded from alignment (no real signal) |

Note: somatic is excluded from SAGE alignment because it's always default —
including it would add noise, not signal.

### LAB vs LLM

| Subtask | LLM source | Operator source | Comparison |
|---|---|---|---|
| Loki challenge quality | `reasoning.advisors.loki_challenge` + `loki_counter` | `output.loki.challenge_statement` + `threat_score` | semantic similarity + threat_score correlation |
| Advisor consensus | `reasoning.advisors.consensus` | advisor board stances (PROCEED/PAUSE/PIVOT/ABORT counts) | stance distribution similarity |
| Bayesian posterior | `reasoning.advisors.bayesian_risk_pct` | `output.bayesian.posterior_confidence` | normalized difference |
| Recommendation | (derived from consensus / risk) | `output.lab_recommendation` | categorical match |
| Threat level | (derived from risk geometry) | `output.lab_threat_level` | categorical match |

### BAR vs LLM

| Subtask | LLM source | Operator source | Comparison |
|---|---|---|---|
| Court verdict | `reasoning.court` verdicts | `output.bar_verdict` | categorical match (PERMIT/CONDITIONAL/BLOCK → STRONG/TENSION/RUIN_RISK) |
| Baseline floor NCI | (implied by LLM coherence + stakes) | `output.baseline.floor_nci` | normalized difference |
| Asymmetry ratio | (implied by LLM risk geometry) | `output.asymmetry.asymmetry_ratio` | normalized difference |
| Ruin detection | `reasoning.court` BLOCK triggers | `output.ruin.ruin_detected` | categorical match |
| Bet quality | (derived from asymmetry + reversibility) | `output.asymmetry.bet_quality` | categorical match |
| Kelly fraction | (derived from asymmetry) | `output.asymmetry.kelly_fraction` | normalized difference |

### KINTSUGI vs LLM

| Subtask | LLM source | Operator source | Comparison |
|---|---|---|---|
| Pathogen presence | (LLM's coherence/nci — low NCI may indicate pathogens) | `output.pathogens` (count) | count correlation |
| Repair need | (LLM's NCI grade — SATOSHI_VALID vs lower) | `output.repaired` | categorical match |
| Trust discount | (LLM's irreversibility + NCI delta) | `output.kintsugi_trust_discount` | normalized difference |
| NCI post-repair | (LLM's nci_score) | `output.nci_score` (post-repair) | normalized difference |
| Version compliance | (LLM's phase_id + axioms) | `output.golden_seams` (axiom/phase flags) | categorical match on flagged items |

Note: KINTSUGI compares the LLM's output to the operator's diagnosis of what's
wrong with it. The comparison is "did the operator find the same problems the
LLM's output pattern implies?" — not "did the operator produce the same output."

## Coherence loss computation

Coherence loss is operator-specific:

- **SAGE coherence loss** = `1 − (operator.coherence_law_score / max(llm.coherence_pct, 1))`
  - If the operator's coherence law score is higher than the LLM's coherence_pct,
    coherence_loss → 0 (no loss, possible gain).
  - If the operator's coherence is lower, coherence_loss reflects the gap.

- **LAB coherence loss** = `1 − (operator.posterior_confidence / llm.nci_score/100)`
  - LAB's posterior confidence relative to the LLM's NCI-derived confidence.
  - If LAB is more confident (posteriors ≥ NCI/100), coherence_loss → 0.

- **BAR coherence loss** = `1 − (1 − abs(operator.baseline.floor_nci − llm.nci_score/100))`
  - BAR's baseline floor NCI relative to the LLM's NCI. If the floor is close to
    the LLM's NCI, low loss. If the floor is much lower, high loss.

- **KINTSUGI coherence loss** = `1 − (operator.nci_score / llm.nci_score)`
  - Post-repair NCI relative to LLM NCI. If repair raises NCI, coherence_loss
    → negative (clamped to 0 — a gain, not a loss).

## Severity computation

```
severity = normalize(stakes_weight × irreversibility)

where:
  stakes_weight = { LOW: 0.3, MEDIUM: 0.6, HIGH: 1.0, EXISTENTIAL: 1.0 }
  irreversibility = primitives.irreversibility ∈ [0, 1]  (from intake)
  normalize(x) = clamp(x, 0, 1)  (already in range; stakes_weight × irreversibility ≤ 1)
```

Example:
- HIGH stakes, irreversibility 0.7 → severity = 0.7
- LOW stakes, irreversibility 0.3 → severity = 0.09
- MEDIUM stakes, irreversibility 0.5 → severity = 0.30

## Fidelity adjustment (NOT in CSM — separate weighting)

CSM is computed on the raw pair. The fidelity markers (`somatic: default`,
`hci: proxy`, `axioms: llm_derived`) are NOT baked into CSM — they're a
separate weighting layer applied at the aggregate level (see below).

Rationale: CSM measures agreement between what the LLM produced and what the
operator produced *given the inputs it received*. If the inputs are low-fidelity
(always default somatic, proxy HCI, llm_derived axioms), the agreement is still
real agreement on those inputs — it's just agreement on low-fidelity inputs. The
fidelity weighting tells you how much to trust the CSM number, not whether the
agreement happened.

## Aggregate weighting (separate from CSM)

When aggregating CSM across multiple pairs to make a Path B decision, weight each
pair's CSM by its fidelity:

```
weighted_CSM = sum(CSM_i × fidelity_weight_i) / sum(fidelity_weight_i)

where:
  fidelity_weight_i = somatic_weight × hci_weight × axioms_weight

  somatic_weight:  user_self_report=1.0, default=0.3
  hci_weight:       user_self_report=1.0, proxy=0.4
  axioms_weight:    llm_derived=0.6, default=0.3
```

This is the "fidelity weighting not yet operationalized" gap from the benchmark
plan. The weights are provisional — they need to be validated against the review
cadence's "who was right" data before they're treated as reliable.

## Open questions

1. **Should somatic be excluded from alignment for all operators, or only SAGE?**
   Somatic is always default for every operator (no DB column), so for any
   operator that consumes somatic, the somatic subtask is always noise. Excluding
   it from alignment for all operators is cleaner than per-operator special-casing.

2. **Should HCI be excluded from alignment when HCI source is proxy?**
   HCI is always proxy (no user self-report in DB). BAR compares HCI vs PCI, but
   both are derived from the same coherence_pct → the comparison may not be
   meaningful. Excluding HCI from alignment when HCI source is proxy would
   remove a noisy subtask. Same logic as somatic.

3. **What's the right normalized_distance function for continuous values?**
   Currently assumed to be `1 − abs(a − b) / max_range`. For NCI (0-100), that's
   `1 − abs(a − b) / 100`. For ratios (asymmetry_ratio, kelly_fraction), the
   range is different. Need to specify per-subtask.

4. **How to compare categorical values that have natural ordering (e.g. verdicts)?**
   PERMIT/CONDITIONAL/BLOCK and STRONG/TENSION/RUIN_RISK have natural ordering.
   Exact match gives 1/0, but partial credit for adjacent categories may be more
   informative. Not specified yet.

5. **Who computes CSM — the review tool, or a store-side function?**
   For Phase 1-2 (JSONL store, small sample), computing CSM in the review tool
   or a validation script is fine. For Phase 3+ (larger sample, aggregate stats),
   a store-side function (`compute_csm(pair) → float`) that's queryable is better.
   The formula should be defined once (this doc) and implemented wherever it's
   needed.

## Summary

| Component | Status |
|---|---|
| CSM formula | Specced (alignment × 0.40 + delta × 0.30 + (1−coherence_loss) × 0.20 + (1−severity) × 0.10) |
| Threshold | 0.65 (from benchmark plan) |
| Per-operator subtask maps | Specced for SAGE/LAB/BAR/KINTSUGI |
| Coherence loss per operator | Specced |
| Severity computation | Specced (stakes × irreversibility) |
| Fidelity adjustment | Explicit: NOT in CSM, separate weighting layer |
| Aggregate weighting | Specced (provisional weights, need validation) |
| Open questions | 5 (somatic/HCI exclusion, distance function, categorical partial credit, CSM computation location, per-operator somatic exclusion) |

**Bottom line:** CSM is specced well enough for Phase 3 implementation. The open
questions are refinements, not blockers for implementing the formula. The biggest
unresolved decision is whether to exclude somatic and proxy-HCI from alignment
when their source is default/proxy — that affects which subtasks count toward the
operator's agreement score.
