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
- **Inversion (written 2026-08-28).** *The failure mode: "Ullr state" becomes a badge a user (or ARCS
  on their behalf) claims to justify skipping the arc and calling a lucky outcome "internalized
  fluency." A confident user who got a good result once demands the scaffolding drop; ARCS complies and
  mislabels recklessness as graduation. The discriminator is the Graduation Receipt itself: genuine
  fluency produces a receipt whose NCI, pre-named signal, and drift-state fields cohere across
  consecutive sessions; a skipped-arc lucky-hit produces either no receipt or one that does not hang
  together (no pre-named signal, drift-state absent, single-session). The invariant therefore requires
  the ≥3-signals-across-consecutive-sessions detector — self-declaration alone can never trigger Ullr
  state. If a user could talk ARCS into Ullr state without the corroborating receipt trail, the
  invariant is falsified and must be cut.*

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
- **Inversion (written 2026-08-28).** *The failure mode: Baldur Protocol is invoked as an
  accountability escape hatch — ARCS (or a user) classifies a session "held / witness-only" precisely
  to avoid running a hard decision the moment actually demands (a real fork with stakes and a closing
  window, reframed as "this just needs to be held"). Silence becomes a way to dodge the Court, not
  honor the humble case. The discriminator is directionality: the Baldur case is a moment that
  *presents as a decision but asks to be held* (grief phrased as a decision question); the weaponized
  case is a moment that *presents as held but is a decision with a live window* (a hard conversation
  with real reversibility cost, relabeled to skip it). The safeguard: Baldur classification must be
  falsifiable against stakes+window — a held-moment claim over a decision with a closing one-way door
  and non-trivial stakes is a mis-classification, and the Drift/Court layer must still surface the
  window even while the pipeline stays quiet. If Baldur can suppress a genuine COURT-grade fork, the
  invariant is being abused and must be re-scoped.*
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

- [x] **Loki test written for each candidate** (inversions above, written 2026-08-28).
- [ ] One live session each: an Ullr-state Graduation Receipt; a Baldur-Protocol Witness Receipt.
      *(Cannot be fabricated — requires a real fluency trail / a real held moment. This is the only
      remaining hard gate.)*
- [x] **ROM numbering reconciled.** The ROM-vocabulary collision is RESOLVED (Option A, 2026-08-28):
      the canon axis is the 7 ROM Primitives (`.claude/arcs-canon.md`), and these candidates are
      proposals against **Primitive 1 — NOTOMATION**. See `runtime/specs/ROM-AXIS-INDEX.md`. No new
      primitive number is minted until the live-receipt gate passes.
- [ ] Decide: promote to ROM / keep candidate / cut. Norse naming is optional; the invariant is the substance.
