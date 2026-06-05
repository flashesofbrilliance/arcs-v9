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

## Linked receipts / ADRs

- ADR-017 / ADR-019 — Receipt core schema, sealed ReceiptObject (relates to / respects)
- ADR-020 — Tribune Intelligence Layer (relates to; lattice is the deferred cross-session layer)
- `runtime/specs/lattice-pressure-rom.json` — companion ROM (governing authority)
- `runtime/specs/time-quality-attribution-rom.json` — Drift Sentinel + W-decay (depends on)

---

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
