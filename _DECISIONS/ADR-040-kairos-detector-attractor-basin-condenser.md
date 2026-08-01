# ADR-040 — Kairos Detector / Attractor-Basin Condenser (the signal-condensation primitive)

> **Status:** RC — PROPOSED (blueprint; design before machinery)
> **Date:** 2026-08-01
> **Commit:** (set at merge)
> **Y:** YELLOW / MODERATE / SHIFTING
> **Relates to:** `operators/arcs_operator_kairos.py` (existing timing operator — unwired),
> `_PATTERNS/2026-07-10-quiet-signals.md` (the abductive QS method), Golden Inchworm (WORLD.md:
> Red Thread → Golden Thread → Needle), Orthogonal Echo Detector (ROM primitive #5),
> `runtime/specs/conductor-notation-v1.md`, the Alchemist (ROM spec + meta-audit v2.2), `forge-kit`
> intake, and the ICP-state / Kairos memory (catching the caught-breath window).

## D — The Decision

**Sharp question:** The corpus continuously throws off *weak, scattered* evidence — quiet signals
(what the lattice says by what it doesn't), red/golden threads, cross-domain echoes, and timing
windows — but nothing **condenses** them into a form an operator can act on. The Alchemist (the
overnight enricher) needs cooking-ready input; today the threads stay diffuse and the timing windows
go uncaught. That uncaught window *is* the Kairos problem this session kept naming: the caught-breath
moment passes because nothing detected the gap aligning. **How do we condense weak scattered signal
into a candidate substrate the Alchemist/Conductor/operators can cook with — WITHOUT manufacturing
patterns (abductive overfit)?**

**Decision (proposed):** A **Kairos Detector / Attractor-Basin Condenser** — a *propose-only*
operator that:

1. **Ingests four weak-signal streams:**
   - **Quiet signals** — `_PATTERNS/…quiet-signals` method (abductive; each already names its verify step).
   - **Red→Golden thread** — Golden Inchworm 3-pass (Red Thread → Golden Thread → Needle), non-blocking.
   - **Non-obvious patterns** — Orthogonal Echo (cross-domain kinematic isomorphisms).
   - **Timing windows** — the existing KAIROS operator (`TimeMode`/`TimeGate`/horizon).
2. **Runs attractor-basin dynamics on the manifold.** A basin is a region toward which trajectories
   converge. A *forming* basin = scattered signals condensing to a point = simultaneously a
   **candidate golden thread** and a **kairos window opening** (the gap aligning). Basin formation is
   the "get cooking" trigger.
   - **Discharge model (the Tesla coil):** the basin does not fire on convergence alone — it
     *accumulates conversion potential* and **discharges at the peak**, when voltage (basin depth /
     multi-stream convergence) is maximal **AND** the gap aligns (the kairos window / counterpart
     receptivity). Voltage without gap-alignment is stored potential (hold, do not fire); firing
     early is a short. The discharge is the *flash of brilliance* — and it is a **give/take bridge**:
     the recipe is given at one pole, crosses the arc, and is confirmed received at the other.
3. **Emits a condensed, verification-tagged candidate substrate** — golden-thread candidates +
   timing windows + flagged patterns — handed to the **Alchemist** (enrich → propose canon), the
   **Conductor** (orchestrate the operators/advisors), and the operator cast (LAB · BAR · SAGE ·
   CURATOR · KAIROS · CONTRACT · KINTSUGI).
4. **Never commits.** The basin condenses *candidates*; ratification is human, at dawn, on the record
   (the meta-audit COURT two-way door). This is NOTOMATION: it scaffolds/sequences, never decides.

## The matched pair — Condenser (in) + Blower (out) = the decision amplifier

The detector above is the **condenser** (signal IN: capture the whisper, condense the scattered
streams, converge to a cooking-ready substrate). It has a matched complement, the **blower /
speaker** (signal OUT: project the cooked substrate back as the tuned delivery — front-of-house, the
discharge, the receipt returned). Together they make ARCS a **decision amplifier**: weak
decision-signal in → clear bearing out. (The blower is also the forge **bellows** — the air that
gets the fire hot enough to cast; same primitive, both jobs.) The give/take bridge spans the pair:
the condenser *takes the give* (their reference/recipe), the blower *returns the take* (the projected
receipt).

**Gain-staging discipline (the honest edge on the output side):** output fidelity must never exceed
input fidelity. Overdriving the blower is clipping — distortion that reads as louder/more-certain but
is *manufactured*. The speaker cannot broadcast SHARP when the condenser only heard GRAIN (WORLD.md
render scale as a gain rule). Amplify signal, never past the evidence. This is the same control rod
as the condenser's over-pull guard, applied to projection: the map never lies about how certain it
is, and neither does the amp.

## E — Entity

A new operator, `arcs_kairos_detector.py`, composing the existing KAIROS operator + the QS method +
the Echo detector + the Inchworm. Consumers: the Alchemist and Conductor. It feeds `forge-kit`'s
intake with detected windows ("this counterpart's basin is forming — reach now"). It does not
replace any operator; it condenses their inputs into one cooking-ready substrate.

## W — Window

Gated, not now. Depends on: the operators being wired at all (currently canon-in-code, zero
production callers — the meta-audit's standing gap) and the Observatory period / 100-receipt gate
that unblocks the operator library generally. This ADR is the *blueprint*; machinery waits behind
that gate. Design captured now so the shape is ready when the gate opens.

## Y — Y-Gate: YELLOW / MODERATE / SHIFTING

Deliberately **not** GREEN. The mechanism is beautiful and the risk is exactly the one this whole
session circled:

**The honest edge — an attractor basin that pulls too eagerly IS the pattern-fabrication engine.**
Condensing "quiet signals + non-obvious patterns" is precisely where abductive overfit lives: the
basin will *find* a golden thread whether or not one is there, because a synthesizer (human or
operator) manufactures resonance past a certain density. Uncontrolled, this is the runaway fission /
echo-fabrication we spent the night guarding against. The control rods, mechanized:

1. **Propose-only.** Emits candidates, never commitments. Ratify at dawn, by a human, on the record.
2. **Every candidate names its disconfirmation step** (extends the QS method — a signal without a
   verify step is not emitted).
3. **Multi-stream convergence required** — a candidate is surfaced ONLY when **≥ 2 independent
   signal streams form the same basin** ("three axes brace one point make a structure; one axis
   makes a story"). Single-stream basins are *logged, not surfaced* — this is the primary
   over-pull guard.
4. **Basin decay / cool-down** — a candidate that does not re-converge across runs decays out
   ("what still rings in the morning is a bond; what went quiet was the spark fading").

With those four rods it is a reactor; without them it is the bomb. The YELLOW gate stays YELLOW
until the multi-stream + disconfirmation guards are proven to suppress fabricated candidates on a
known-signal test set — that proof is the promotion criterion to GREEN.
