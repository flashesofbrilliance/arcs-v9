---
name: ARCS Canon — Core Primitives & Epistemic Status
description: Key ARCS concepts, validated vs UNDEFINED claims, ROM axioms, pipeline spec
type: project
originSessionId: 23619576-afec-4e5b-8da4-0a0324edd5c7
---
**ARCS = Abductive Reasoning & Coherence System** — decision intelligence OS. v9 is the active implementation (`github.com/flashesofbrilliance/arcs-v9`). v8.5 Field OS specs live in `arcs-field-os` and `arcs-canon` repos as canon reference.

**Core primitive**: Decision receipt = a falsifiable prediction logged BEFORE the outcome. Everything else is downstream.

## L0–L5 Pipeline (current arcs-v9 implementation)

Labels per `arcs-v9/SKILL.md` + `orient-prd.md` v0.1.0 (Kairos Locked):

- L0: Activation filter / Question Sharpener
- L1: Loki adversarial (DEWY decomposition per spec; Loki in impl)
- L2: Bayesian validation (Y-gate scoring per spec; Bayes in impl)
- L3: Kintsugi Immune / NCI scoring
- L4: NCI meta-review / True North generation (LAB + BAR macros per spec)
- L5: Synthesis / Receipt generation + Brief render
- L6–L7: Not yet built (architecture specified, not implemented)

**Spec vs impl delta:** Documented in `runtime/flows/question-compass-to-dewy.md` (Issue #4). Two CRITICAL gaps: NCI <40 HOLD gate absent, W-field HOLD gate absent.

## ROM Axioms (L0–L7 genome — from _CANON/book-ii/part-ii-rom-axioms.md)

Seven axioms that cannot be violated without breaking the instrument:
1. Decisions are bets, not facts
2. NOTOMATION — system may not decide for the operator
3. Time quality is a first-class variable
4. Structure is earned before it is named (Golden Inchworm / Hyperstition Pipeline)
5. Repair visibly (Kintsugi)
6. History is a teacher, not a jailer
7. Irreversibility is declared, not assumed (Write-Lock / Kairos Lock)

**NOTOMATION verbatim (ROM Primitive 1):** *"Tools may only externalize/scaffold/sequence human cognition. Never compress or overrule revealed preference."*

## Decision modes
QUICKMOVE (low stakes, today) | PLAN (reversible) | COURT (high stakes, one-way door)

## Court convening conditions (from _CANON/book-ii/part-iii-constitutional-court.md)
1. Irreversibility in window
2. Asymmetric downside
3. Avoidance signal
4. HEAD/HEART/WALLET tension

**LOCKED state:** Post-Court resolved. Foundation the next decision builds from. System shifts to execution mode — no more counterfactual branches.

## Triune Logic (v8.5)
- OM: Validated, n≥5, confidence ≥80%, methodology documented
- NULL: Failed validation or NEVER rule triggered
- UNDEFINED: Insufficient data — label explicitly, never treat as OM

## Key UNDEFINED claims (Gauntlet audit, April 8 2026 — do not treat as validated)
- 87% prediction accuracy — internal test, sample size REDACTED
- Kairos windows average 4–6 hours — single illustrative example generalized
- Energy sustainability 78% vs 32% — hypothesis only
- Network effect λ = 0.000012 — curve-fit, no actual data
- 2.3M cognitive synthesizers in US — no source
- Coherence equation C = A-(S-S_min)²+W — variables not operationally defined

## Book II Canon (_CANON/book-ii/ — arcs-v9 main)

**ALL PARTS CANONICAL as of 2026-05-27.**

| Part | Title | Status |
|---|---|---|
| Part I | From Firehose to Compass | ✅ CANONICAL |
| Part II | Core ROM Axioms | ✅ CANONICAL |
| Part III | Constitutional Court & Agency | ✅ CANONICAL |
| Part IV | (stale draft deleted) | ✅ CANONICAL — CONDITIONAL CLEAR applied |
| Part V | The Accumulation Protocol | ✅ CANONICAL v1.0.0 |
| Part VI | The Shared Court | ✅ CANONICAL v1.0.0 |
