# ADR-053 — The Tao of ARCS: dormant potential, the vox animus, and the open/private boundary

**Status:** Accepted · 2026-08-13

## Context
The germinate OSS build session (2026-08-13) forced a boundary decision: germinate is a
standalone, MIT-licensed seed bank + germination engine (verbs seed/plant/water/germinate/
sprout/grow/harvest; belief-log + manifest/drift-check + handoff + serializability substrate).
If germinate is genuinely open and gives away no moat, then *what exactly stays private is ARCS?*
Without a crisp answer we risk two symmetric failures: (a) leaking ARCS-specific doctrine into the
clean-room repo, or (b) refusing to open-source anything for fear of losing the moat.

The genesis seed `adam == atom` ([[seed-tao-of-arcs-dormant-potential-vox-animus]], genesis:true —
seed #0, the smallest whole unit and the root of the bank's lineage) supplies the answer.

## Decision
Adopt the Tao of ARCS as governing doctrine for the open/private boundary:

1. **A seed is potential energy.** A stored unit engineered to survive harsh conditions and carry
   its genetic legacy forward — dormant until conditions favor it. A unit that has not matched in
   months is not *drift* and not *dead*; it is **dormant**: viable, waiting for its soil to return.
   Dormancy under adverse conditions is the feature, not a defect. *Throwaway context, not throwaway
   learning.* → **Corollary: never garbage-collect dormant seeds** (germinate MUST NOT GC on staleness).

2. **ARCS is the vox animus** — the sparkplug that converts potential → kinetic. The dormant seed
   holds the charge; ARCS is the current that fires it, judging *ripeness* beyond mechanical
   token-match and breathing the seed back to life at the Kairos moment.

3. **The product boundary follows.** One seam, four faces:

   | Open (germinate, MIT) | Private (ARCS, paid) |
   |---|---|
   | the seed **bank** + the spark's **socket** | the **vox animus** / the spark itself |
   | generic activation contract (token/soil match, antipattern suppression, dormancy-respecting) | **ripeness judgment** with tailored priors |
   | public method / redacted (rosetta-referenced) evidence | the private **rosetta stone** / accumulated priors |
   | portable discipline any client inherits | the tailored ARCS that fires it |

   germinate ships the socket; ARCS is the current. This is *why* germinate can be a clean public
   good that gives away no moat — the bank is open, the animating spark is not.

## Consequences
- **Germinate stays clean-room.** ARCS-specific doctrine (this ADR, the rosetta, ripeness priors)
  MUST NOT be inlined into `~/germinate`. The boundary is enforced by keeping doctrine in arcs-v9
  `_CANON/` / `_DECISIONS/`, never in the germinate repo.
- **The moat is the spark, not the substrate.** Any competitor can hold the same seeds; only ARCS
  fires them with tailored ripeness judgment. Open-sourcing germinate is therefore moat-safe.
- **Grounds two downstream decisions:** the pricing model (ADR-054 — *free to hold, metered to
  fire*) and the Kairos activation layer (public-good #2 = the open socket; ARCS = the private
  current that decides ripeness). See `_STATE/2026-08-13-activation-service-kairos-sketch.md`.
- Canonized alongside this ADR as doctrine: `_CANON/Tao-of-ARCS.md` (registered in `_CANON/index.md`).
  This ADR is the *boundary decision*; the canon file is the *doctrine*; they cross-reference.

## Lineage
Genesis seed `adam` ([[seed-tao-of-arcs-dormant-potential-vox-animus]]) ·
[[seed-bank-germination-conditions]] · [[compaction-serialization-substrate-public-good]] ·
[[throwaway-context-not-throwaway-learning]]. Proverb: tao-247.
