# ADR-070 — ARCS is two surfaces: the Receipt (deductive record) and the Induction (abductive instrument-forging)

> **Status:** DECIDED
> **Date:** 2026-08-28
> **Commit:** (set at merge)
> **Numbering note:** FIRST ADR minted THROUGH `scripts/oracle.py next adr` (counter 69→70, `_SEEDS/_oracle.json` committed with this file). ADR-069 and earlier were minted off-oracle against the index tail — this one is the discipline dogfooding itself, in the same session that built the oracle pre-commit gate.
> **Lineage:** Witness stub `_STATE/witness/2026-08-28.jsonl` (Zach, verbatim, 11:51 EDT). Names the surface that ADR-053 (Tao of ARCS), the Folksonomist (`scripts/arcs_core.py`), and the WORLD.md Myst/Guide register were all circling. Tao proverb: `_CANON/tao-proverbs.jsonl` tao-254.

---

## D — The Decision

**Sharp question:** Deductive tooling assumes you can already name what you want. But the highest-value ARCS moments are the opposite — a vague target you cannot yet put in words, fluid exploration, wanting the right thing to float across your desk. What is the surface that serves *that*, and how does it relate to the receipt?

**Decision:** ARCS is **two complementary surfaces**, and this is canon:

- **The Receipt surface** — *deductive, backward-looking.* Attests and records coherence that already happened: a DEWY state vector frozen at a decision, a witnessed flash, a closed ex-ante→ex-post loop. It answers "what did we decide, and was it earned?"
- **The Induction surface** — *abductive, forward-looking.* Engages exactly where deductive logic fails: the pre-verbal, exploratory, meandering search. It (1) **recognizes the shape of the job-to-be-done — often before the human consciously does**, (2) **keeps the human honest** by checking the inferred shape against ground truth (repo, live data), and (3) **forges the purpose-built instrument** that fits that exact job. It answers "what is this work actually asking for, and what tool would fit it?"

The receipt looks backward and records. The induction surface looks forward, recognizes the pattern, and builds the instrument. **The meandering is not waste to optimize away — it is the generative medium**, and ARCS's job is to let the right thing arrive and name it.

## E — Entity / System

The Folksonomist (bottom-up emergent clustering, `scripts/arcs_core.py`) is the induction surface's engine. NOTOMATION is its constitutional floor (scaffold cognition, never replace it). The Receipt models (`Receipt`, DEWY, witness ledger) are the other surface. This ADR names the pair; it does not add code. Every purpose-built instrument this session minted by pattern-recognition (canon-propagation sentinel, gravity-well fork detector, oracle pre-commit gate, prod→op20 adapter, night-moves digest) is an induction-surface output — evidence of the pattern, not the pattern itself.

## W — Window

YEARS / constitutional. This is a naming of existing architecture, not a dated tactic. It reframes the product thesis (ARCS is not a decision *logger*; the logger is one of two surfaces) and should govern how new surfaces are classified: does this attest the past (receipt) or forge for a pre-verbal future (induction)?

## Y — Gate

**GREEN.** Named live by the user as "the whole point of ARCS," corroborated in-session by ~7 instrument-mints that each recognized a job-pattern and forged the fit tool, and consistent with prior canon (ADR-053 Tao, the Folksonomist, WORLD.md). Conviction high; it names structure already present rather than proposing new machinery.

**Falsifier:** If, across the next epoch, ARCS's genuinely-valued outputs are all reducible to *records of already-articulated decisions* (pure receipts) and none are *instruments forged for a target the user could not yet name*, then the "induction surface" is decoration and ARCS is just a decision logger. The claim survives only while ARCS keeps producing fit-for-pre-verbal-job instruments the user did not ask for by name.

## Tao (apex spine)

> **When the student is ready, the master appears. When the job to be done is ready, the right tool for the job appears.** *(tao-254)*
