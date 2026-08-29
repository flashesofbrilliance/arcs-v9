# ROM Axis Index — the three tiers, and which one is canon

> **Status:** `AUTHORITATIVE (human ruling, 2026-08-28)` · Resolves
> `_DECISIONS/CANON-COLLISION-rom-vocabulary.md` under **Option A** (declare one authoritative axis,
> subordinate the others). Read this before citing "the ROM primitives" — three different axis-sets
> historically wore the "ROM" label; this index says which is canon and how the others nest.

## The ruling

"ROM" names **three distinct tiers**. They are views of one physics, not competitors. One is canon;
the other two are explicitly subordinate and derived.

| Tier | Name | Count | Authoritative source | Role |
|---|---|---:|---|---|
| **CANON** | **ROM Primitives** | 7 | `.claude/arcs-canon.md` → *ROM Primitives (never violate)* | The constitutional primitives. When someone asks "what are the ROM primitives?", **this is the answer.** |
| derived | ROM Behavioral Laws | 6 | `runtime/specs/ARCS-v9-ROM.md` → *Core axioms* (ROM-1…ROM-6) | Execution/behavioral laws derived from the primitives. A behavioral layer, not a primitive layer. Renamed from "core axioms" to **ROM behavioral laws (derived)** to end the label collision. |
| foundation | Epistemic Foundations | 7 | `_CANON/book-ii/part-ii-rom-axioms.md` → *Core ROM Axioms* (I…VII) | The epistemic axioms the primitives rest on. Foundational, not operative — cite for *why*, not for *what to do*. |

## The 7 canon primitives (from `.claude/arcs-canon.md`)

1 NOTOMATION · 2 HYPERSPHERE CONTEXT MANIFOLD · 3 HYPERSTITION PIPELINE · 4 GOLDEN INCHWORM ·
5 ORTHOGONAL ECHO DETECTOR · 6 KINTSUGI IMMUNE SYSTEM · 7 WRITE-LOCK

(`CLAUDE.md`'s ROM section mirrors these 7 — the earlier 5-item truncation there was doc-rot,
de-rotted 2026-08-27.)

## How they nest (partial map — evidence they are views of one thing)

- Epistemic Axiom II (NOTOMATION) ↔ Primitive 1 (NOTOMATION)
- Epistemic Axiom V (Repair Visibly) ↔ Primitive 6 (KINTSUGI)
- Epistemic Axiom VII (Irreversibility Declared) ↔ Primitive 7 (WRITE-LOCK)
- Epistemic Axiom III (Time Quality First-Class) ↔ `time-quality-attribution-rom.json`
- The 6 behavioral laws (ROM-1…6) do **not** cleanly map onto a primitive — they are the derived
  execution layer, which is exactly why they are subordinate, not canon.

## Numbering authority (unblocks ROM candidates)

Because the canon axis is now declared (7 primitives, `.claude/arcs-canon.md`), new ROM invariants
have a home to be numbered against. The Norse ROM candidates
(`runtime/specs/ROM-CANDIDATES-norse-witness.md`) are proposals **against Primitive 1 (NOTOMATION)**;
their ratification checklist (Loki test + one live receipt each) is unchanged and still governs.

## Verified-as-prose caveats (carried forward, do not propagate as implemented fact)

- **WRITE-LOCK is prose-only** as a mechanism narrative. The oracle pre-commit hook
  (`scripts/git-hooks`, armed 2026-08-28) enforces ADR-number uniqueness — a *concrete* write-lock on
  numbering — but the general "git-is-the-write-lock" framing remains a metaphor beyond that hook.
- No drift-lint yet diffs the primitive lists across `.claude/arcs-canon.md`, `CLAUDE.md`, and
  `part-ii`. Candidate wiring, not built — the nightly canon-propagation cron (armed after this branch
  merges) handles mechanical mirror de-rot but not this specific cross-list diff.
