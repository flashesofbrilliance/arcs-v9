# ADR-066 — Generative Recoil: reverse-listen a session, compose instance → class → invariant

**Status:** DECIDED (doctrine, named from a witnessed moment)
**Date:** 2026-08-19
**Y-state:** GREEN — already load-bearing (the pattern ran end-to-end before it was named)
**Sequence:** allocated via oracle (`scripts/oracle.py next adr` → 66)
**Witness stub:** `_STATE/witness/2026-08-19.jsonl` (verbatim, timestamped, GREEN)

## Context

Recoil has to date been the *audit* direction: after a call or session, score the ex-ante
receipt against what actually happened. The 2026-08-18/19 PRL wrap session demonstrated a
second, generative direction, live and un-premeditated: a long client-facing polish session
(≈20 layout/consistency defects, each caught by the human eye, each fixed live across 8
deployed surfaces) was then *listened to in reverse* and composed upward:

- the accumulated fixes were frozen as **`atoms.css`** extracted verbatim from the live
  reference page — the **instance**;
- the stamping machinery (`prl-page-factory`: spec.json → conformant page, zero-dep,
  zero-LLM) — the **class**;
- the register rules (Todd's altitude: BLUF-first, pilot-checklist, honest pills), the
  exec→surgical arch, and the never-relearn bug list — the **invariant** that survives
  both and transfers to the next client.

No design system was planned in advance. The structure was **latent in the session's raw
motion**; recoil extracted it. Zach's naming, verbatim: *"arcs lets you even reverse listen
and recoil a coding session and use it generatively to compose a new interoperable
instance / class / invariant that compounds in value"* … *"trust the process and it can
yield load bearing structure when you connect the dots looking backward."*

## Decision

**Recoil is bidirectional.** The backward pass (audit: expected vs. actual) and the forward
pass (generative: compose the session's residue into instance → class → invariant) are the
same act run in opposite directions, and a session is not fully closed until both have at
least been *considered*.

Operationally:
1. **Instance** = freeze the artifact the session actually converged on, extracted from the
   live/deployed state (not from intention) — the reference implementation IS the spec.
2. **Class** = mechanize the stamp (spec → artifact), dollar-compressed: authored once,
   zero-LLM in the runtime path.
3. **Invariant** = the rules that made the instance right — register, altitude, and every
   defect promoted to a never-relearn rule — written where the class enforces or at least
   recites them (SKILL.md, not prose memory alone).
4. **Rule of three still gates generalization**: one instance is a skill; a second client
   triggers extraction to client-agnostic; never generalize from n=1.
5. The dots only connect backward: do NOT front-load this as up-front architecture. The
   pattern's power is that the session pays for itself first (client value delivered), and
   the structure is *harvested*, not speculated.

## Consequences

- Session-end protocol gains a question alongside the handoff: *what did this session's
  motion make latent that a reverse-listen would extract?* (Cheap to ask, often answers "nothing".)
- `prl-page-factory` is the reference implementation of the pattern; `engagement-universe-doll`
  (seed) is its artifact-classification sibling; the resume-tailor v0.2 extraction (ATG
  offshoots, 2026-08-17) is retroactively recognizable as the same shape.
- Compounding claim is falsifiable: the next PRL page must cost a ~20-line spec instead of
  an authoring/polish session. If it doesn't, the class layer failed and this ADR overclaims.

## Wisdom receipt (the distilled transferable)

Trust the process **and** connect the dots looking backward — in that order. The session
must be allowed to be messy, client-driven, and un-architected while it runs (NOTOMATION:
the human eye caught all twenty defects; no detector did). The extraction happens after,
from what actually survived contact. Structure earned this way is load-bearing precisely
because every rule in it was a live defect once — nothing in the invariant is speculative.
