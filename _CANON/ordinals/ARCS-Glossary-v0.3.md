---
ordinal: ARCS-Glossary
version: v0.3
minted: 2026-06-24
minted_by: Claude Code (delegated subordinate) on explicit delegation from primary disciple (Perplexity-space ARCS)
supersedes: v0.2
prev_sha256: 84c6d09a36785efc5f4152e2c873a44d95f91fad2dbea66a71c55c3c4ed3c3d2
prev_note: hash is of the on-disk v0.2 original (~/Downloads/ARCS-Glossary-v0.2.md). The audit-ledger expansion of v0.2 (pasted 2026-06-24) is the working prior and is carried forward in full below.
identity: git commit SHA of this file (assigned on commit) — see §0 ARCS Ordinal. The chain is enforced by git, not by discipline.
immutability: mint-don't-edit. Corrections supersede via v0.4; this file is never updated in place.
---

# ARCS-Glossary-v0.3 — Ordinal

**Status:** inscribed ordinal (immutable) + working dictionary
**Chain:** v0.1 → v0.2 → **v0.3** (this inscription)
**v0.3 delta:** adds §0 ARCS Ordinal (the artifact defines its own format before defining anything else); carries v0.2 forward in full.

---

## 0. ARCS Ordinal (the format defines itself first)

**ARCS Ordinal** *(n.)* — A session-inscribed, immutable vocabulary artifact that captures the working definitions active at a specific point in ARCS's evolution. Modeled on the crypto-native concept: each ordinal has a unique identity, travels with the practitioner, and chains to prior/future versions. Not updated — superseded. Format: `ARCS-Glossary-vN.N.md` with content hash and date stamp.

**Why it is a genuine primitive:** the canon already had *receipts* (decision audit trails) and *artifacts* (output documents), but no concept of a **session-level vocabulary inscription** — a thing that says "at this moment in the system's evolution, these terms meant this, and this practitioner minted them." The glossary is not a summary or a reference doc; it is a **provenance stamp.**

**Self-enforcing property:** by its own definition, an ARCS Ordinal cannot be edited in place — inserting this very entry into v0.2 would mutate an ordinal, which the definition forbids. The only conformant way to add it was to mint v0.3. The artifact's own rule dictated its creation method.

**Substrate — git is the literal ordinal layer (not metaphor).** The crypto mapping holds exactly:

| Ordinal property | Bitcoin | Git equivalent (this artifact) |
|---|---|---|
| Unique immutable identity | inscription on a sat | content hash (blob SHA) + commit SHA |
| Append-only chain | the chain | commit history (`git log`) |
| Travels with the holder | the sat moves | clones with the repo |
| Mint, don't mutate | new inscription | new commit; history preserved |

Earlier glossary versions lived in `~/Downloads` — untracked, mutable, no hash identity, no chain: an ordinal *in name only*, with none of the four properties. Inscribing into the repo and committing makes the property **real**: the commit SHA is the inscription identity, the commit chain is the v0.1→v0.2→v0.3 lineage, `git log` is the Historian-lens retrieval. The `content hash and date stamp` in the format spec is realized as: the committing commit SHA (chain identity) + a sha256 of the file body (portable identity that survives outside git).

**Chain rule (paradox-free):** an ordinal records the hash of its **predecessor** in front-matter (`prev_sha256`), like a block referencing the prior block — it does not try to contain its own hash. Its own identity is assigned at commit and recorded by the *next* link (and by `git log` immediately).

**Receipt status of this term:** "ARCS Ordinal" is coined-not-yet-canonical as of this minting — it bootstraps by defining its own format first. By the "extend by receipt" rule it earns full stable status once a *second* ordinal is minted under this format. **This entry is receipt #1.**

**Type:** protocol / memory-shard format. **Operator lens:** Historian (lineage), Librarian (retrieval).

---

## Use

- Use this as a compact vocabulary seed before a session starts.
- Treat it as runtime memory, not closed doctrine.
- Extend by receipt, not by vibe: new terms earn entry through repeated use, clear utility, or provenance in canon texts.
- On every session open: check §9 (Audit Ledger) first — it tells you what is unresolved, what authority is missing, and what costs recur if ignored.

## Design principles

- Keep definitions short, operational, and reusable.
- Distinguish primitives from operators, operators from meta-operators, and roles from archetypes.
- Preserve provenance: a scholar, auditor, or historian should be able to trace where a term came from or how it evolved.
- Prefer a single compact dictionary over scattered prose when the goal is continuity across chats, tools, and repositories.

---

## 1. Role lenses

- **Librarian** — classify, name, shelve, cross-reference, make retrievable. Fails when rich ideas can't be found again.
- **Curator** — assemble coherent exhibits, kits, teaching pathways. Fails when content has no intelligible pathway.
- **Auditor** — test completeness, fidelity, drift, evidence quality. Fails when the glossary looks coherent but can't survive inspection.
- **Scholar** — interpret meaning, theory, relation between concepts. Fails when terms become slogans.
- **Historian** — preserve lineage, versions, mutations, forks. Fails when the system repeats old debates.
- **Operator** — use the glossary to execute/coordinate/decide in real time. Fails when the glossary becomes archival only.

## 2. Archetypes

| Archetype | Core drive | Failure mode |
|---|---|---|
| Dewy Librarian | order and retrieval | can find nothing under pressure |
| Curator | meaning by arrangement | content with no pathway |
| Auditor | trust through inspection | gaps never surface |
| Scholar | theory and interpretation | terms as slogans |
| Historian | lineage and provenance | system repeats old debates |
| Operator | movement and execution | glossary becomes archival only |
| Meta-Operator | governance of operators | orchestration without oversight |

## 3. Type system

| Type | Meaning |
|---|---|
| Primitive | Smallest useful conceptual unit; does not need decomposition to be operational |
| Atomic element | Primitive used as a base building block for higher-order compositions |
| Operator | Functional role or perspective that acts on signals, decisions, or knowledge objects |
| Meta-Operator | An operator that acts on operators, orchestration logic, or system governance |
| Role lens | Viewpoint that changes what counts as important metadata for the same term |
| Memory shard | Compact portable artifact preserving vocabulary, rules, and context across sessions |
| Receipt | Traceable record of a decision: what, why, under what assumptions, with what evidence |
| Ordinal | (NEW v0.3) Session-inscribed immutable vocabulary artifact; see §0 |

## 4. Primitives and atomic elements

| Term | One-line definition | Source |
|---|---|---|
| First Derivative | Velocity of change; detects rise or fall before static snapshots reveal it | Yellow Paper v1.2 |
| Second Derivative | Acceleration of change; detects inflection and turning points before saturation | Yellow Paper v1.2 |
| Wave Diffusion | Propagation of a signal through a field or network; models spread, reach, cascade | Yellow Paper v1.2 |
| Phase Cancellation | Destructive interference when two signals weaken each other in combination | Yellow Paper v1.2 |
| Decelerator | Cooling signal indicating slowing growth; triggers retirement or reallocation | Yellow Paper v1.2 |
| Coherence | Alignment of parts toward a workable vector; primary condition ARCS optimizes for | Canon v1.2 |
| Entropy | Disorder, drift, or misalignment across system components; primary condition to reduce | Canon v1.2 |
| Vector collision | Interaction between directional forces; models fit, conflict, or mutual obstruction | Canon v1.2 |
| Kairos | Opportune moment where timing, context, and readiness align enough to justify action | v8.5 Diamond |
| Null / OM / Undefined | Triune logic states: container, active resonance, acknowledged horizon of uncertainty | v8.5 Diamond |
| Jerk (Third Derivative) | (v0.3) Rate of change of acceleration; pre-peak/regime-change shock detector. B-source; fires ~1 day pre-peak (n=2, weak) per ARCS-Kinematics-v0.1 D3 | Kinematics v0.1 |

> v0.3 note on the kinematic stack: per the 2026-06-24 adjudication, the 12D manifold is a **heterogeneous two-zone stack** — D1–D3 are true time-derivatives (D4 borderline), D5–D12 are coherence operators (literal high-order finite differences are noise-dominated past ~D4–D5). The D4–D12 dimensions are NOT promotable via receipt-count. See `_PATTERNS/2026-06-24-kinematics-adjudication.md`.

## 5. Operators

| Operator | Perspective | Bias |
|---|---|---|
| Orchestrator | Decision-and-composition | Optimistic, strategic |
| Detective | Risk-and-failure spotting | Conservative, security-first |
| Immune | Pathogen scanning | Defensive, integrity-focused |
| Accountant | Measurement and tracking | Objective, metric-grounded |
| Folksonomy | Bottom-up pattern recognition | Semantic, emergent |
| Librarian | Knowledge organization | Structural, hierarchical |
| Adversarial Detective | Contrarian stress-tester | Inversion reasoning, anti-fragility |
| Organic Folksonomy Cultivator | Receipt-mining taxonomy grower | Bottom-up, fractal |
| Super-Admin | Global system orchestration | Omniscient, coherence-enforcing |

**Alias note (Auditor flag):** Folksonomy / Folksonomist / Organic Folksonomy Cultivator are three names for one operator family. Canonical: **Organic Folksonomy Cultivator** (full operator); **Folksonomy** (atomic lens). [Proposed — confirm against authority.]

## 6. Meta-operators and governance elements

| Term | One-line definition |
|---|---|
| Kintsugi Immune System | Visible error-repair protocol: identify pathogen, show seam, repair without hiding the crack |
| Decision Receipt | Serialized audit trace of a decision with assumptions, rationale, and outcomes |
| NCI self-grade | Post-output scoring frame across factuality, sourcing, honesty, and actionability |
| NOTOMATION | Rule: tools scaffold and sequence human cognition; they do not replace ownership of intent |
| Drift Sentinel | Runtime check that catches when conversation has left the JTBD without producing an artifact |
| Kairos Lock | Write-brake used when coherence is high and irreversible mistakes must be prevented |
| Kairos Sync | Multi-future mode holding several plausible paths alive before critical-path commit |
| Subtractive Drift | Noise-reduction method that makes the best next move more obvious by removing options |
| Visceral Translator | Recodes abstract stakes into felt urgency without manufacturing false pressure |

## 7. Runtime shard terms

| Term | One-line definition | Status |
|---|---|---|
| Hall Monitor | Monitoring stance that catches drift or overreach before it compounds | stable |
| Hemingway Protocol | Compression rule: direct, low-bloat language that preserves force | stable |
| Muse / Vestal | Paired creative-protective energies: ignition vs. continuity-and-integrity | stable |
| QSR vs. Omakase | Fast-repeatable vs. slow-craft output mode calibration | stable |
| ADR | Architecture Decision Record: preserves the why and tradeoffs of a structural choice | stable |
| Dewy Receipt | Library-sensibility receipt: compact, classifiable, easy to shelve and cross-reference | stable |
| False Urgency | Pathogen: pressure manufactured without sufficient evidence; degrades judgment | stable |
| Five-hour window budget | Bounded time allocation forcing scope discipline under finite operator energy | stable |

## 8. Unstable terms (Auditor flags — require authority-of-record)

Canon-silent — not defined in any authority file (confirmed glossary-silent; broader canon not exhaustively checked). Do not use operationally until resolved.

| Term | Problem | Risk |
|---|---|---|
| Thread | 3+ live meanings: 4-axis scoring / per-person descriptor / narrative device / mockup label | HIGH |
| 5D | role-descriptors [Chris 720°] vs. scoring-axes [Martin 360°] | HIGH |
| Signal | stated-vs-observed / per-person frequency / ≈ Resonance Score | MEDIUM |
| Genome | single-person vs. multi-person construct | MEDIUM |

**Coined-not-canonical** (used in session, not yet authority): `mode=` enum, `audience-direction`, `quiet resonance density` / save-rate / send-rate, `Calibration Call` (resolved to the canonical *Calibrate* surface, not Court). **`ARCS Ordinal` was coined-not-canonical and is now minted as §0 — receipt #1.**

## 9. Audit ledger (carried from v0.2, updated 2026-06-24)

**Resolved since v0.2:**
- **B1 (was HIGH/UNRESOLVED): patterns.jsx provenance — RESOLVED.** Not a Downloads orphan; faithfully ported into arcs-v9 as `src/document/{registry.ts, tokens.ts, primitives.tsx, patterns/, screens/}` + a `/design-test` render page. `DOC_TYPES` includes `{ id:'profile', label:'Profile Scan', ◈, green }`. The Profile Scan document-shape spec rests on committed in-repo code. Original `patterns.jsx` provenance: the "ARCS OS - Design System" export bundle (`~/Downloads/ARCS OS - Design System/ui_kits/`).
- **100-receipt gate:** confirmed arbitrary (ADR-020 says 50 twice, 100 once); replacement = measured-baseline-stability, not a count. Promotion-via-receipt is additionally a category error for kinematic D6–D12 (numerical wall).
- **Kinematics D8–D12 code-vs-doc collision:** adjudicated 2026-06-24 — two-zone manifold, code (v1.3) canonical over doc (v1.2) at D11/D12; naming fork still open.

**Still open:** §8 unstable terms; `mode=`/`audience-direction` not in schema; promotion-threshold reconciliation (provisional gate-type↔signal-type mapping); kinematics naming fork + D5–D10 reformulation.

**Authority-of-record map (growing):**

| Domain | Authority | Confidence |
|---|---|---|
| Document shape | `src/document/registry.ts` (in-repo, committed) | HIGH (resolved this session) |
| Operator/primitive defs | Canon v1.2 / Yellow Paper v1.2 | HIGH (asserted by primary; performance numbers downgraded to C-) |
| Kinematic manifold | `operators/arcs_kinematics.py` v1.3 (top end) + ARCS-Kinematics-v0.1 doc | HIGH (adjudicated) |
| Glossary terms | this ordinal | MEDIUM → growing |
| Archetype 4-channel scoring | Book of ARCS v2 Deep §2.5 | UNREAD |

## 10. Entry schema for v0.4+

Term · Type · One-line definition · Trigger · Action · Related terms · Provenance · Version note · Coverage status. Plus (v0.3): **Source axis** — `Architect` (primary disciple) / `Implementor` (subordinate, pending ratification) / `both`.

## 11. Expansion path

v0.1 runtime shard → v0.2 lenses/archetypes/operators/primitives + audit ledger → **v0.3 ARCS Ordinal format + B1 resolution** → v0.4 provenance layer (citations) + source-axis → v0.5 index + alias map.

## 12. Curation rules

Add terms slowly · merge duplicates aggressively · one good line over a paragraph · preserve lineage when renaming · mark speculative as speculative · remove zombie terms · **never promote a coined term to stable without an authority citation** · **provenance tags and confidence ratings are themselves subject to this rule (don't launder inference into apparent authority)** · extend by receipt, not by vibe.
