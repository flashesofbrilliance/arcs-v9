# ADR-023 — Observability as a Superionic Goal Lattice

> **Status:** DECIDED
> **Date:** 2026-06-05
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should the observability layer model goal structure as an inferred,
weighted folksonomy lattice (a DAG over receipts) held in a "superionic" phase band by
governed counter-forces — rather than as a declared top-down milestone hierarchy?

**Chosen: yes.** Observability over goals is a *phase-controlled reinforcement lattice*,
not a milestone checklist against a declared tree.

---

## E — Entity / System

- The **Observatory** (WORLD.md — not yet built): the surface that renders this.
- The cross-receipt layer *above* the Tribune (ADR-020), which annotates single receipts
  and explicitly deferred cross-session structure to "100+ receipts (L6 territory)."
- The **Folksonomist** operator (`scripts/arcs_core.py:708–1014`, `folksonomist_cluster()`)
  — the existing bottom-up emergent-tagging engine; the edge-growth mechanism.
- Receipt **lineage** (`prisma/schema.prisma:145`, single-parent `parentId`) — preserved
  unchanged; the lattice is a separate overlay, not a Receipt modification.
- The **Drift Sentinel** (`runtime/specs/time-quality-attribution-rom.json`) — the phase
  monitor.
- The `challenge` tributary (ATG[1]) — the contrarian-pressure source.

---

## W — Window

**Horizon:** YEAR
**Revisit trigger:** Gate at 100+ real receipts (same L6 gate as ADR-020); or first
time the Observatory is actually built; or if the Receipt lifecycle model changes.

This ADR records the **model and the decision**. Implementation is gated, not done here.

---

## Context

This began as a thinking session (branch `claude/observability-milestone-mapping-345ho`):
*does mapping milestones onto coordinate/subordinate/superordinate goals make sense from
an observability perspective?* It converged through four moves:

1. **Lattice over tree.** A strict goal hierarchy is a *tree* (one parent per node). Goals
   don't behave that way — one subordinate milestone often serves multiple superordinate
   goals — so the correct structure is a **DAG** (directed, acyclic, multi-parent).
2. **Folksonomy over taxonomy.** Matches the ARCS core bias (the Folksonomist operator):
   bottom-up emergent structure over rigid top-down classification. The hierarchy is
   *inferred from the receipt trail*, never declared up front.
3. **Observation moves from nodes to edges.** In a taxonomy you observe node-state ("did
   milestone X hit its declared state?"). In a folksonomy lattice you observe **edge-weight
   over time** — which goal connections are *tightening*. The superordinate goal is
   whichever attractor the high-weight edges point at; it precipitates out of the lattice
   rather than being imposed on it.
4. **The failure mode and its counter-force.** Reinforcement lattices calcify via
   preferential attachment ("rich get richer") — a folksonomy without a counter-force
   silently becomes the rigid taxonomy it was meant to escape.

### The superionic target (governing image)

The desired state is **superionic**: crystalline structure that refracts light cleanly
(renders sharp) yet stays fluid-dynamic under sufficient pressure (re-arrangeable on new
evidence). Real superionic ice fixes an oxygen sublattice while protons flow through it —
structure *and* flow at once. Mapped onto the L0–L7 stack, "superionic" is not one global
state but a **gradient**: L0–L1 (atomic signal, coherence) is the fluid proton layer
(edges form/dissolve fast); L5–L6 (global coherence, ecosystem) is the crystalline frame
where weight solidifies.

### The three counter-forces (flying buttresses, not patches)

They are one phase-control loop, each carrying thrust at a different level — external
load-bearing members, like flying buttresses, that let the structure stay tall, thin, and
luminous instead of collapsing into a squat, dark, solid mass (the taxonomy):

- **Edge decay** keeps the proton layer fluid — without it everything freezes solid.
  Reuses the W-field decay curve already in the Time ROM. Guards **L2** (path survivability).
- **Contrarian pressure** (the `challenge` tributary) is the "sufficient pressure" —
  superionic is a high-energy phase that relaxes to ordinary ice at rest. Guards **L4**
  (cross-domain).
- **Drift Sentinel** reads the phase (gas / superionic / solid). Guards **L5** (global
  coherence). Calcification itself is an **L3** cascade; the three forces bracket it.

### Governing authority

`runtime/specs/lattice-pressure-rom.json` (this ADR's companion, created with it) pins the
pressure constants. They are **L7 meta-governance constants, not system-tunable** — if the
system could set its own decay rate it could overrule revealed preference by choosing how
fast it forgets, a NOTOMATION breach.

### Adversarial grounding (deep research, 2026-06-05)

The model was pressure-tested against Wolfram's "Games Between Programs: The Ruliology of
Competition" (2026), NKS 6.7 finite automata, and the CA regular-language-complexity
literature (Wolfram 1984; Nordahl 1989). A 5-agent adversarial pass corrected four
over-claims; the surviving (corrected) claims are recorded in the Loki test below. Primary
Wolfram pages were 403-gated in the research environment; quotes are stable search-index
reconstructions, not byte-verified — confirm against the live source before treating any
quotation as verbatim.

---

## Options Considered

### Option A — Declared milestone hierarchy (taxonomy / tree)
- User declares the superordinate goal; milestones hang beneath it.
- Pros: simple, legible, conventional observability (node-state checks).
- Cons: NOTOMATION violation (freezes a still-forming preference); cannot represent a
  multi-parent milestone; structurally blind to lateral (coordinate-goal) conflict.

### Option B — Flat receipt event log (no goal structure)
- Observe receipts as a stream of discrete events.
- Pros: zero modeling commitment.
- Cons: structurally blind to lateral coherence — two coordinate goals can both be GREEN
  while pulling against each other (a Y-gate FORK/PARADOX), invisible in a flat log.

### Option C — Superionic folksonomy lattice *(chosen)*
- A DAG of weighted goal edges, inferred bottom-up by the Folksonomist, held in a
  superionic phase band by edge decay + contrarian pressure + Drift Sentinel.
- Pros: roll-up confidence over lineage without instrumenting the parent; sees lateral
  conflict; makes drift computable; matches the ARCS folksonomy bias and the WORLD.md
  superionic target.
- Cons: more machinery; the calcification risk is real and must be actively countered;
  L6 territory (gated).

---

## Decision

**Chosen:** Option C.

**Rationale:** It is the only option that observes *edges* (the tightening connections),
which is where the value lives — roll-up, lateral-conflict detection, and computable drift.
It is the direct consequence of two things already in the codebase: the Folksonomist
operator and the receipt lineage edge. A and B are both structurally blind to coordinate-goal
conflict; A additionally freezes preference.

**Trade-offs accepted:** We take on the calcification risk and the obligation to govern the
pressure constants at L7. We accept that this is L6 work and defer implementation behind the
100+-receipt gate.

### Proposed architecture (documented; implementation gated)

- Receipts stay as-is. The single-parent `parentId` lineage tree is **preserved**; the
  lattice is a **separate weighted-edge overlay** — mirrors ADR-020's "annotate, don't
  modify the sealed ReceiptObject (ADR-019)" discipline.
- A future `goal_edges` table — `(from_receipt, to_receipt, weight, last_reinforced)`,
  many-to-many (the DAG), weight reinforced on co-occurrence, decayed by age via the
  Time ROM's W-field decay curve. **Sketch only — out of scope for this ADR; a future
  schema ADR builds it.**
- Reuse, do not reinvent: Folksonomist = edge-growth operator; Drift Sentinel = phase
  monitor; `challenge` tributary = pressure source.

---

## Y — Conviction

**Polarity:** GREEN (on the model and direction)
**Conviction:** MEDIUM (on mechanism grounding — see Loki)
**Stability:** STABLE on direction; SHIFTING on mechanism (`goal_edges` shape is a sketch)

**Loki test — the strongest cases against, with what survived an actual adversarial pass:**

1. *"You're inventing an L6 engine before a single cross-receipt pattern exists."* —
   Defense: this ADR records the model only; build is gated at 100+ receipts, same as
   ADR-020.
2. *"Irreducibility proves the tree can't be declared."* — **Rejected as stated.** A static
   weighted DAG is reducible by construction (topo-sort + DP); irreducibility only bites in
   the cyclic/self-reinforcing regime, and it concerns cheap *prediction*, not whether
   structure can be *declared*. "Inferred-not-declared" stands on NOTOMATION + folksonomy
   bias, NOT on a computational-necessity claim.
3. *"The lattice calcifies by theorem (monotone complexity growth)."* — **Rejected.**
   Wolfram's CA result is "*usually* non-decreasing," never monotone; and rising
   regular-language complexity is *enrichment*, not calcification (calcification is the
   LOW-complexity Class-1/2 pole). Backing for "positive-feedback systems lose flexibility
   without perturbation" is **preferential-attachment / loss-of-plasticity** literature, not
   the CA-complexity result. The buttresses are load-bearing by dynamics, not by theorem.
4. *"The DAG is computationally required because nesting is non-regular."* — **Rejected.**
   Real goal hierarchies are bounded-depth, and bounded nesting *is* regular. The DAG is
   well-motivated by scaling / persistence / shared structure — not a Chomsky-hierarchy
   impossibility.
5. *"Emergent goals have no describable rationale, so none is owed."* — **Over-licensed.**
   The honest form is per-case: attempt reduction, report "found none / not yet checked."
   Confabulating a clean why is the NOTOMATION breach to avoid; asserting irreducibility by
   default is the opposite failure.

---

## Consequences

- Unblocks the Observatory's data model (the thing it renders is the lattice, not a log).
- Relates to ADR-020: Tribune = per-receipt annotation; the lattice = cross-receipt
  structure. The lattice feeds the Tribune's deferred cross-session phase.
- Creates a future schema ADR for the `goal_edges` overlay table.
- Creates `runtime/specs/lattice-pressure-rom.json` as governing authority for the pressure
  band (committed with this ADR).

**Implementation pointer:** `runtime/specs/lattice-pressure-rom.json` (constants);
future `goal_edges` schema ADR (build); gated at 100+ receipts.

---

## Structural Integrity (pre-PR load analysis)

The counter-forces are structural members carrying thrust, so promotion is gated on a
structural load analysis, not a vibe check. **The thrust** has two sources: reinforcement
inflow (co-occurring receipts pumping edge weight) and preferential attachment (the
rich-get-richer lateral force concentrating weight on one hub). **Failure** = leaving the
SUPERIONIC band: SOLID collapse (compression) or GAS blowout (tension).

### FMEA — failure modes to mind

| # | Mode | Mechanism | Buttress that fails | Trigger | Detection |
|---|------|-----------|---------------------|---------|-----------|
| F1 | SOLID collapse (calcification) | Preferential attachment freezes lattice to rigid taxonomy | decay too slow (λ) / cap too high (g) | R ≫ λ | Gini→1, attractors→1 |
| F2 | GAS blowout (churn) | Over-correction; nothing solidifies, no attractor | decay too fast / contrarian too hot | λ or c too aggressive | complexity unbounded, 0 stable attractors |
| F3 | Oscillation (resonance) | Decay↔reinforcement loop never settles | undamped loop, gain too high | c near decay timescale | high phase variance, no rest state |
| F4 | Premature lock (cold calcification) | Early edge locks before flow can challenge it | contrarian can't fire (no alternatives) | N below minimum | **NOTOMATION breach — must HOLD, not infer** |
| F5 | Sensor blindness | Phase proxy diverges from true minimal-DFA complexity | the gauge (not a buttress) | any | proxy-vs-ground-truth validation only |
| F6 | Governance drift (foundation) | L7 constants mis-set or self-tuned; envelope shifts | all three at once | single point of failure | audit only |

F4 and F5 are load-bearing-critical: F4 *is* the NOTOMATION breach the model exists to
prevent; F5 makes every other reading a lie. (Deep research flagged F5 — minimal-DFA size
is the true measure and is heavy; any cheap proxy can diverge, and complexity direction is
counterintuitive.)

### Load-bearing calculations (capacity inequalities the test must verify)

1. **Decay capacity (vs F1):** net edge accumulation = `R·gain − λ·weight`; stable only if
   `λ` clears weight faster than `R` drives it past the cap. Margin = `λ_required / λ_set`.
2. **Contrarian capacity (vs F1/F4):** `t_cap(R)` (time for a contingent winner to cross g)
   must exceed `t_challenge(c)` (time to first challenge). The buttress must arrive *before*
   the collapse, not after.
3. **Cap headroom (vs false-positive F2):** real goal/topic co-occurrence is **Zipfian**, so
   `g` must sit *above* the corpus baseline skew: `g > Gini_baseline(corpus)`. That baseline
   is a **measured** quantity — the reason synthetic data cannot finalize the constants.

### The threshold = the stable envelope

Not a single number: the region of `(λ, c, g)` where phase stays SUPERIONIC across load
`(R, burstiness, skew)`. The boundary is the failure surface; proposed constants must sit
inside it with margin. Deliverable: envelope is non-empty, per-mode failure load, margin at
the operating point.

### Pre-PR gate (what a synthetic load test may and may not certify)

A synthetic run (`scripts/lattice_sim.py`, follow-on commit) may certify: (1) machinery runs
and each buttress has its predicted directional effect; (2) a non-empty stable envelope
exists on parametrized synthetic load; (3) F1–F6 are reproducible and detected. It may **NOT**
certify the production constant values — those need the real Zipf baseline (calc #3).

**PR GATE (DECIDED): PR is BLOCKED until the real-corpus Zipf baseline can be measured
(100+ receipts, the L6 gate).** Synthetic thresholds are not sufficient to promote — signing
off on assumed loads instead of measured ones is the structural sin this gate exists to
prevent. The harness demonstrates the structure *can* bear load and characterizes the failure
surface; it does not set the operating point.

---

## Forward architecture — the Conductor loop (gated, recorded not built)

The Observatory runs the lattice as a **progressively tightening loop**, not a one-shot.
The image is a golden orb-weaver: each pass lays silk (reinforces co-occurrence edges),
prunes (decay), challenges (contrarian), and tightens a **reticulated lattice of abductive
inference** toward its best-explanation attractor.

- **Conductor + ballet of operators.** A single orchestrator steps the operators in a fixed
  choreography each tick: `folksonomist (grow edges) → reinforce → decay → contrarian
  injection → calcification guard → Drift Sentinel (phase read)`. Operators are choreographed,
  not ad hoc.
- **Abductive precisification.** Lattice edges are abductive inferences (inference to the best
  explanation): co-occurrence → inferred goal connection → the high-weight attractor is the
  current best explanation of the decision pattern. The systematic-vs-contingent discriminator
  (LP-CONTRA-01) is an *abductive-quality test* — the systematic winner is the explanation that
  survives orthogonal challenge. This ties directly to Wolfram's "pocket of reducibility" win.
- **Anterior / proactive / posterior phases** (lattice-scale Tribune, ADR-020): **anterior** =
  forward-simulate under load to predict calcification *before* it happens (this is the load
  test); **proactive** = the live during-loop, silent below threshold; **posterior** = replay a
  finished trajectory + recoil analysis (where did a YELLOW get overridden, where did an edge
  calcify). The harness (`scripts/lattice_sim.py`) runs anterior + posterior modes.
- **The watcher / cron deployment.** In production the loop is a scheduled watcher. Precedent in
  this repo: `.github/workflows/adr-queue.yml` (GitHub Action trigger); arcs-care's cron-route
  pattern is the alternative. **Gated (L6) — not built until the 100+-receipt corpus exists and
  the PR gate clears.** An `analytics/` home for the watcher does not yet exist; create it with
  the production loop, not before.

This subsection is a recorded decision about *shape*, not a build authorization. The PR gate
above (real-corpus calibration) still governs.

---

## ⚠️ Amendment — 2026-07-13: First real-corpus baseline measured (gate now has a number)

The revisit gate above ("100+ receipts") cleared on count some time ago without anyone
running the measurement the gate actually requires. Measured today, per the dual-audit
composite action (`_PATTERNS/2026-07-13-dual-audit-reconciliation.md` §6).

**Method (reproducible):**
- Corpus: all **233 production receipts** (project `xbbpiryokswwvcrcutge`), ordered by
  `createdAt`, pulled read-only via
  `SELECT json_agg(COALESCE("macroTags",'[]') ORDER BY "createdAt") FROM "Receipt"`.
- Lattice: `macroTags` co-occurrence — each receipt's unordered tag pairs increment edge
  weight by 1. No decay applied (decay is a lattice-dynamics parameter in
  `lattice-pressure-rom.json`, not a corpus property; the baseline is the raw distribution).
- Metrics: byte-identical formulas to `scripts/lattice_sim.py` — `gini()` over edge
  weights, node strengths, `eff_attractors` (Hill number), phase thresholds
  (HOLD < 50 · SOLID ≥ 0.78 · GAS < 0.30 or unstable · else SUPERIONIC). "Stable" adapted
  from the sim's 12-tick argmax persistence to: argmax node unchanged across the trailing
  3 checkpoints.
- Transcription cross-validated: script tag totals match SQL
  `json_array_elements_text` GROUP BY exactly, all 9 tags.

**Results (cumulative checkpoints):**

| N | Gini | top_share | eff. attractors | vocab | edges | Zipf slope | argmax |
|---|---|---|---|---|---|---|---|
| 50 | 0.456 | 0.203 | 7.36 | 9 | 26 | −1.09 | KAIROS |
| 100 | 0.523 | 0.222 | 7.15 | 9 | 29 | −1.10 | BAR |
| 150 | 0.560 | 0.214 | 7.32 | 9 | 33 | −1.02 | BAR |
| 200 | 0.557 | 0.213 | 7.24 | 9 | 33 | −1.06 | KAIROS |
| **233** | **0.577** | **0.227** | **7.06** | **9** | **33** | **−1.14** | **KAIROS** |

**Reading:**
- **Gini_baseline(233) = 0.577** — mid-band, far from SOLID. But it is still drifting
  upward (max |Δg| = 0.020 over the trailing 3 checkpoints) and the top attractor
  **flipped BAR → KAIROS** inside the last 60 receipts. Under the sim's strict rule
  (unstable ⇒ GAS), the corpus reads **GAS: the baseline has NOT yet stabilized.**
  The gate stays open — but now for a measured reason, not an arbitrary count.
- **Proposed stabilization criterion** (needs L7/write-lock ratification, per the
  self-tuning prohibition): promote when trailing |Δgini| < 0.01 per 25-receipt
  checkpoint for 3 consecutive checkpoints AND the argmax attractor persists across
  them. At the current pace that is plausibly reachable within ~50–100 more receipts.
- **Honest caveats:** (1) `macroTags` is a **closed 9-term system vocabulary**
  (KAIROS 155 · BAR 141 · ONE_WAY 118 · KKL 97 · LAB 55 · TWO_WAY 43 · CHRONOS 38 ·
  NOTOMATION 30 · FATED 7), not open emergent tagging — the lattice's open-folksonomy
  assumption is not exercised by this corpus; true emergent structure awaits the
  Folksonomist over free text (RC-OPS-002 territory). (2) Zipf slope ≈ −1.0 to −1.14 is
  strikingly Zipf-like but fitted over only 9 ranks — suggestive, not evidential.
  (3) Edge space is nearly saturated (33 of 36 possible pairs), so any future tightening
  must appear in *weights* (Gini), not new edges — which is exactly what the model
  predicts for a maturing lattice.

---

## Linked receipts / ADRs

- ADR-017 / ADR-019 — Receipt core schema, sealed ReceiptObject (relates to / respects)
- ADR-020 — Tribune Intelligence Layer (relates to; lattice is the deferred cross-session layer)
- `runtime/specs/lattice-pressure-rom.json` — companion ROM (governing authority)
- `runtime/specs/time-quality-attribution-rom.json` — Drift Sentinel + W-decay (depends on)

---

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
