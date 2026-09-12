# ADR-062 — The ouroboros: a falsifier is only honest if it turns on itself

**Status:** Accepted · 2026-08-16
**Allocated by:** the oracle (`oracle next adr` → 62), per ADR-057.
**Witnessed:** `_STATE/witness/2026-08-16.jsonl` — *"The discipline caught its own author on its first day. That's the whole thesis working on itself."*

## Context
ARCS's whole claim is to be an **honest resonance engine, not propaganda** — and the thing that keeps it
honest is the falsifier ([[arcs-purpose-honest-resonance-engine-not-propaganda]]). But a falsifier that
only points *outward* — at counterparts, at other people's ADRs, at external artifacts — is indistinguishable
from a flattering machine that has learned to look rigorous. Two independent events on the tape make the same
point:
- **F6** (the Hypercube Gauntlet self-audit): the tell that a GREEN ADR was actually YELLOW was that *it
  applied its falsification bar to everything except itself.* Self-exemption was the whole defect.
- **F32** (this session): ADR-061 (verify flags vs the full source) was validated within hours by catching
  **its own author** — I forked a parallel wrong-schema falsification-ledger believing none existed; a
  source-check falsified my own claim; the episode was logged as a falsification in the very ledger it
  concerned.

The snake ate its own tail, and that is exactly when the discipline proved real.

## Decision
**Recursive self-application is the honesty test of any falsifier, audit, gauntlet, or control** — not an
optional nicety. A falsifier earns the right to judge external subjects only once it demonstrably bites its
own hand:
1. **No self-exemption.** Any rule, gauntlet, or ADR that carves out an "except when I do it" clause is
   flagged by that fact alone (generalizes F6/F7's author-invokable-exemption tell). The auditor flags
   regardless of who authored the thing.
2. **Turn the instrument on its own outputs.** Run the gauntlet on its own ADR; run the provenance checker
   on the artifact the checker produced; re-verify the fix a verifier prescribed. The subject of a pass
   must periodically be the pass itself.
3. **Log the self-catch as a first-class falsification.** When the discipline catches its own author or
   design, that is the highest-information row on the tape — keep it (F6, F32), do not quietly fix and move
   on. The falsifier's own error rate must be visible.
4. **The propaganda test.** If a resonance/audit surface has never falsified one of its own designs, treat
   its external verdicts as unproven — a falsifier that has never turned on itself is propaganda wearing a
   lab coat.

## Consequences
- **NOTOMATION holds recursively:** the machine surfaces and pressure-tests, the operator adjudicates — and
  that includes pressure-testing the machine and the operator. The gauntlet is not exempt from the gauntlet.
- **Anti-survivorship, kept:** self-catches are the welds most worth keeping; the falsification ledger's
  spine is the record of the discipline biting itself (F6, F32, and forward).
- **A cheap standing check:** for any new control/ADR/gauntlet, ask "what would it look like for this to
  catch *me*, and has it?" A "not yet" is a YELLOW, not a GREEN.
- **Bounds the recursion:** self-application is a health check, not an infinite regress — one honest
  self-catch that changed an output is the bar, not turtles all the way down.

## Lineage
[[arcs-purpose-honest-resonance-engine-not-propaganda]] · [[control-integrity-described-vs-wired]] ·
[[verify-flags-against-full-source]] · ADR-061 · ADR-052 (float-not-drift boundary) ·
F6 + F32 in `_STATE/falsification-ledger.jsonl` · WORLD.md → THE WITNESS.
