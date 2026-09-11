# CANON COLLISION — ADR-033 assigned to two distinct decisions

> **Status:** `RESOLVED — Option A (human ruling, 2026-08-28)` · **Raised:** 2026-08-28 during a
> branch-reconcile (forensic-recoil thread rebased onto main).
>
> **RULING (Zach, 2026-08-28):** Option A. ADR-033 stays with the earlier ratified **Serialization
> Pathogen Family**. The model-routing decision was renumbered to oracle-issued **ADR-073**
> (`ADR-073-model-routing-adr-audit-default.md`); `_DECISIONS/index.json` updated; a renumber note
> added to the ADR-073 header. (A first pass used 071, but a parallel session had taken 071/072 —
> Möbius invariant and engine-sovereignty — so this moved to 073; the branch was rebased onto that
> live main state on 2026-08-29.) `oracle.py audit adr` → 0 collisions after the move. The
> `enforcement-parity-ledger-adr-033` memory refers to the *Pathogen Family* framing and remains
> correct.

## The finding
`_DECISIONS/` now contains **two different DECIDED ADRs both numbered 033**:

| file | title | status | landed |
|---|---|---|---|
| `ADR-033-serialization-pathogen-family.md` | The Serialization Pathogen Family (tuple axiom + membership registry) | DECIDED (2026-07-18), ratified | commit `1694a907` |
| `ADR-033-model-routing-adr-audit-default.md` | Route ADR-audit harness default to laguna-xs-2.1:free | DECIDED | commit `38fc95be` (2026-08-27) |

The second was introduced by `feat(adr-audit): wire model-routing into the ADR audit harness`; the
follow-up `chore(state): bump ADR stat 64→65 for ADR-033 landing` counted it as a new file. But it is
a **duplicate number, not a new id** — the distinct-ADR-id set is unchanged at 64 (ids 001–069 minus
the gaps 021/041/042/043/047); the file count is 65 only because 033 is doubled.

## Why it matters
Every reference to "ADR-033" is now ambiguous. The global `MEMORY.md` note
`enforcement-parity-ledger-adr-033` already pointed at ADR-033 for a *third* framing — so the number
is overloaded across at least the repo (×2) and memory. This is the same class as the ROM-vocabulary
collision (`CANON-COLLISION-rom-vocabulary.md`): a label pointing at more than one thing.

## Options for the ruling (pick one; do not auto-apply)
- **A.** Keep 033 = Serialization Pathogen Family (the earlier, ratified one); renumber the
  model-routing ADR to the next free slot (e.g. ADR-070) + fix its references.
- **B.** The model-routing decision is small/operational — demote it to a `_PATTERNS/` note or fold it
  into an existing audit-harness ADR, freeing 033.
- **C.** If one supersedes/retires the other in intent, mark the retired one SUPERSEDED explicitly and
  keep the number, rather than leaving two live DECIDED files.

## Reconcile note (this thread)
The forensic-recoil baseline (`_ARTIFACTS/forensic-recoil-2026-08-27/CANON_INDEX-baseline.md`) lists ADR
*ids*, so it remains accurate at 64. No baseline edit needed — the drift is a duplicate *file*, captured here.
