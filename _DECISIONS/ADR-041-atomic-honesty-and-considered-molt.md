# ADR-041 — Atomic Honesty + the Considered Molt (keeping the architecture true)

> **Status:** RC — PROPOSED
> **Date:** 2026-08-01
> **Commit:** (set at merge)
> **Y:** GREEN / HIGH / STABLE (principle) · YELLOW on enforcement
> **Relates to:** ADR-040 (the amp's gain-staging + custody rods, lifted here), ADR-039
> (instance→class), the "honest gauges keep tildes" ROM invariant, `/impeccable` (molt behavior),
> the casting metaphor, `_PATTERNS/2026-07-10-quiet-signals.md` (leads-not-verdicts), the
> enforcement-parity ledger (ADR-034).

## D — The Decision

Two disciplines, one charter — **keep the architecture true**: honest about *certainty*, and clean of
*dead scaffolding*.

### 1 · Atomic GAAP/non-GAAP belief reconciliation (honest about certainty)

Every belief/number carries two possible values, audited at the **atomic (per-belief) level**:
- **GAAP** — custody-traced, audit-defensible, reconcilable (the receipts).
- **non-GAAP** — assessed / adjusted / abductive (confidence estimates, quiet-signal *leads*, tilde
  numbers). Often the *more informative* view — pro-forma is not the enemy.

The standard (the SEC rule, applied to beliefs):
1. **Label the non-GAAP** — the tilde. ("Honest gauges keep tildes at any resolution" — the existing
   ROM invariant; this promotes it to an enforced standard.)
2. **Reconcile it to its nearest GAAP measure** — the chain of custody (ADR-040). No custody, no
   number.
3. **Never give non-GAAP more prominence than GAAP** — gain-staging (ADR-040). The assessed view is
   never broadcast louder than the audited one.

**The failure mode this prevents:** *unlabeled* non-GAAP presented *as* GAAP — an assessed number
wearing an audited number's clothes, confidence in fact's costume. That single substitution is what
quietly rots an architecture; the tilde is the whole safeguard.

### 2 · The considered molt (clean of dead scaffolding)

Scaffolding — scratch pads, exploratory reasoning, the metaphors and intermediate artifacts that got
us here — is **formwork**: throwaway lumber that shapes the pour and then comes off. It was never part
of the structure. After a build, **molt** it (per `/impeccable`, and per [[cut-not-add-provable-architecture]]).

Two rules make the molt safe and right-sized:
- **Timing — strip only after the concrete sets.** Pull the formwork while the pour is still curing
  (the ideas still settling) and the structure collapses. The molt is a *consolidation* step, not a
  live one. Corollary: do not molt an ADR/skill/spec that is still actively accreting this session;
  flag it, molt at handoff.
- **Considered, not generic (the sake polish).** Strip the *right* outer layers to reach *this*
  grain's core — chosen per-artifact, right-sized (the 25th-polish essence), never a uniform
  mass-polish that over-strips some things and under-strips others.

**The molt is operationalized by RECAPITULATE (the 5-verb terminal, ADR-040), run in deep KAIROS
mode.** Recapitulate is not a chronos summary; it is the high-coherence-depth pass (`TimeMode.KAIROS`)
that executes the molt as **scan → audit → distill**: *scan* the whole field at depth, *audit*
GAAP/non-GAAP (custody-backed vs assessed-formwork), *distill* to the load-bearing grain (the sake
polish). This is why the molt is a consolidation step, not a live one — it requires kairos depth, and
kairos depth requires the concrete to have set.

## E — Entity

Governs every durable artifact (ADRs, skills, specs, canon, memory). The reconciliation clause is
checked at write-time (does this number have a tilde or a custody trace?); the molt clause runs at
consolidation / handoff (strip cured formwork). Owner: the author at write-time (honesty), the
consolidator at dawn (molt).

## W — Window

Honesty clause: now, always. Molt clause: at each consolidation boundary. **Immediate application:**
ADR-040 accreted exploratory formwork across this session's edits — it is a candidate for a considered
molt-pass *once its concrete sets* (the Kairos-circuit ideas stop moving), not before.

## Y — Y-Gate: GREEN / HIGH / STABLE (principle) · YELLOW (enforcement)

GREEN as principle — it formalizes an existing invariant (tildes) and an existing practice
(`/impeccable`'s molt), both already load-bearing. **YELLOW on enforcement:** like most prose rules
in this corpus (the 2026-06-23 audit found zero of six enforced), the tilde/custody standard is
currently convention, not tripwire. Promotion to GREEN-enforced requires a write-time check
(unlabeled-assessed-number gate) wired into the enforcement-parity ledger (ADR-034). **Honest edge:**
the molt itself can be over-eager — stripping formwork that was still load-bearing (premature
optimization's twin). The timing rule (strip only after set) is the guard; when unsure whether the
concrete has cured, leave the lumber.
