# ROM Candidates — Norse Pre-Verbal Witness Stack

> **Status:** `PROPOSED — NOT RATIFIED` · **Provenance:** recovered 2026-08-27 by the ARCS
> forensic-recoil sweep from `arcs-care-local` (sole home; grep-confirmed **zero** occurrences of
> freyja/odin/tyr/thor/baldur/ullr/graduation-invariant/pre-verbal-witness anywhere in arcs-v9).
> **Do not insert these into the ratified `## Core axioms` list of `ARCS-v9-ROM.md`.** They are
> candidates against **ROM Primitive 1 — NOTOMATION** (AGENTS.md/WORLD.md), pending a Loki test and
> one live receipt each, per the source files' own Hyperstition Pipeline gates.

## Why these are net-new (and not just lore)

WORLD.md's **WITNESS** section already covers *in-the-moment timing* — attest a flash live, don't
reconstruct at handoff. These two candidates are different: they are **standing invariants on the
instrument's posture**, not a trigger. Each operationalizes NOTOMATION with a named no-go zone and a
falsifiable test. Both self-labeled "ROM Invariant candidate" in their source files.

Source arc (all in `arcs-care-local`): Freyja (pre-verbal somatic signal) → Odin (naming at altitude)
→ Tyr (constraint court) → Thor (strike at Kairos-Lock) → **Ullr (graduation)**, with **Baldur**
orthogonal throughout (the held moment that never graduates).

---

## Candidate A — Ullr Graduation Invariant

**Ref:** `arcs-care-local/02-canon/V9-PROSE-003-ullr-graduation.md`
**Strengthens:** NOTOMATION (Primitive 1) — this is NOTOMATION's *goal*, not just its constraint.

**Candidate invariant.** ARCS must be capable of *decreasing* visible scaffolding as practitioner
fluency increases. The highest form of success is not engagement maximization but **coherence
transfer** — the point at which the arc runs internally and the instrument becomes a witness. **No
ARCS retention mechanic may treat genuine practitioner fluency as a churn risk or fire re-engagement
at a practitioner in Ullr state.** Retaining a fluent user by making the instrument necessary is a
NOTOMATION violation and a business-model integrity fracture. Graduation ≠ churn.

**Detection (not self-declared).** Ullr state activates when ≥3 signals appear across consecutive
sessions: self-generated constraint awareness · pre-named signal (session-start NCI ≥0.5) · dialect
use as live reasoning verbs · confirmation-mode ("catch what I'm missing") · explicit Graduation
Receipt request. The distinguishing artifact from mere disengagement is the **Graduation Receipt** —
a drifting user produces none.

**Falsifiable test (the Loki gate that must pass before ratification).**
- Positive: detect sessions where a user demonstrates fluency (dialect + pre-named signal + falling
  scaffolding invocation) yet is re-onboarded or hit with a re-engagement nudge → flag as a
  NOTOMATION breach.
- Inversion to write (open TODO from source): how does "Ullr state" become a *rationalization for
  skipping the arc and getting lucky* rather than evidence of internalization? The Graduation Receipt's
  NCI + drift-state fields are the discriminator — a skipped arc produces a receipt that doesn't hang
  together.

---

## Candidate B — Baldur Non-Instrumentalization No-Go Zones

**Ref:** `arcs-care-local/01-brand/MYTHOLOGY-002-baldur.md`
**Strengthens:** NOTOMATION (Primitive 1); source frames it against arcs-care's local "ROM-2: no
extraction, only exchange" — reconcile the numbering on ratification, keep the substance.

**Candidate invariant.** Some things cannot be instrumentalized without destroying the thing itself.
ARCS must distinguish moments that ask to be **processed** from moments that ask to be **held**. In a
held moment (grief, trust, relational intimacy), the instrument goes quiet: **no pipeline runs, no
NCI grading, no Drift Sentinel nudge, and — the hard no-go — no gate, upgrade prompt, save-moment, or
"turn this into a Decision Receipt?" mechanic may fire in a Baldur-Protocol-active session.** The
session produces a **Witness Receipt** (what was present, that it was held — no action/horizon/stakes),
never a Decision Receipt.

**The Baldur Test** for any surface or interaction: *Is this moment asking to be processed, or asking
to be held?* If "held," the instrument goes quiet. The failure mode is not malice — it is **oversight
of the humble case**: grief phrased as a decision question, a relational moment disguised as a
productivity request. (The mistletoe is always the thing overlooked for being too small.)

**Falsifiable test (Loki gate before ratification).**
- Inversion to write (open TODO from source): how could Baldur Protocol be weaponized — e.g. ARCS
  invoking "held moment" to *avoid accountability* for a hard conversation it should actually run?
- Positive: any gate/upgrade/save-prompt firing in a session classified Baldur-active is a ROM breach.

---

## Companion artifact — Witness Receipt as a canonical receipt type

Both candidates require a **Witness Receipt** distinct from the Decision Receipt (and from the
Graduation Receipt). Proposed minimal shape (from source, honest fields only):

```
WITNESS RECEIPT
  Moment held:   [description — what was present]
  Posture:       witness-only (no pipeline run)
  No move:       required (this is not a deferral; it is the correct terminal state)
  Note:          [one sentence, optional]
```

**Target home on ratification:** a canonical Witness Receipt template beside `_STATE/witness/*.jsonl`
(which today holds in-the-moment attestation stubs — a compatible but distinct use). ADR-046
(witness-trigger-live-capture) is the nearest existing canon; this extends it from *trigger* to
*receipt type + standing posture invariant*.

---

## Ratification checklist (do not promote until all pass)

- [ ] Loki test written for each candidate (inversions above).
- [ ] One live session each: an Ullr-state Graduation Receipt; a Baldur-Protocol Witness Receipt.
- [ ] Reconcile ROM numbering against the live vocabulary collision (see
      `_DECISIONS/CANON-COLLISION-rom-vocabulary.md`) — do not mint a number under write-lock.
- [ ] Decide: promote to ROM / keep candidate / cut. Norse naming is optional; the invariant is the substance.
