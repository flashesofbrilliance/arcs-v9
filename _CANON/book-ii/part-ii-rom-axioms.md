---
title: "Part II — Core ROM Axioms: The L0–L7 Genome"
series: "ARCS Field OS — Book II: The Decision Manifold"
version: "0.1.0-DRAFT"
status: "CANONICAL"
audit: "Upstream ARCS audit — CONDITIONAL CLEAR. Three items patched 2026-05-26 before commit."
created: "2026-05-26"
governing_physics: "WORLD.md"
governing_spec: "arcs-field-os/specs/orient-prd.md v0.1.0"
memory_anchor: "MEMORY.md v4.0 — ROM Principles + ROM Axioms (verbatim)"
depends_on:
  - "_CANON/book-ii/part-i-firehose-to-compass.md"
---

# Part II — Core ROM Axioms: The L0–L7 Genome

> **Tier: EPISTEMIC FOUNDATIONS** (not the operative canon). Per the ROM-vocabulary ruling
> (2026-08-28, Option A — see `runtime/specs/ROM-AXIS-INDEX.md`), the CANON axis is the **7 ROM
> Primitives** in `.claude/arcs-canon.md`. The seven axioms (I–VII) below are the *epistemic
> foundations* the primitives rest on — cite them for **why**, not for **what to do**. Three map
> cleanly onto primitives (II↔NOTOMATION, V↔KINTSUGI, VII↔WRITE-LOCK).

---

## What ROM Means

Read-only memory is not called that because it is old. It is called that because it cannot be changed at runtime. It is the part of the system that was decided before the session began — the part that does not negotiate.

ARCS has a ROM layer. It is not a list of best practices or a set of recommended principles. It is the set of constraints that, if violated, break the instrument rather than merely degrading it. A compass that tells you what direction to walk is not a slightly inferior compass — it is not a compass at all. The distinction between the ROM and the rest of the system is exactly that sharp.

Seven axioms. The architecture is their consequence.

---

## I. Decisions Are Bets, Not Facts

The system does not return answers. It returns bearings.

The distinction matters more than it sounds. An answer implies a fact that was waiting to be found. A bearing implies a direction that was earned from incomplete information — the best orientation available given what the terrain shows right now.

When the compass returns an NCI score of 57, that number is not a disappointment to be improved before acting. It is the accurate reading. A YELLOW conviction gradient is not a problem to solve before a decision can be made — it is the honest state of the manifold. Operating from a bearing you didn't earn is not more confident; it is more dangerous.

This is the foundational axiom because it determines what every output means. If you enter expecting answers, a 57 feels like failure. If you enter understanding bets, a 57 tells you exactly how to size your move.

**Receipt:** `MEMORY.md v4.0` — *"Decisions are bets, not facts. Always choose under uncertainty to make bets visible and learnable."*

---

## II. The System May Not Decide for You

This follows directly from Axiom I, and it is worth making explicit because every instinct in software design pushes against it.

If a decision is a bet, only the person placing the bet can place it. The system can compute the terrain, surface the ruin risk, name the strongest counter-argument, and freeze the coordinate in a receipt. It cannot move the conviction needle. That movement is yours — it happens in the world, through action and reflection, not inside a pipeline.

The name for this constraint is **NOTOMATION**. Tools may only externalize/scaffold/sequence human cognition. Never compress or overrule revealed preference. When you tell the compass that the job offer feels wrong despite the GREEN NCI, the system records UNDEFINED on the Y-field, not GREEN. Your lived experience outranks the inference.

The practical consequence: every ARCS output is framed as terrain observation, not instruction. *True North: Accept the offer.* Not: *You should accept the offer.* A bearing, not a command. The word choice is not stylistic. It is constitutional.

**Receipt:** `arcs-canon.md` — ROM Primitive 1. `MEMORY.md v4.0` — *"No commands, only offers. No authority, only earned pattern-recognition. The user's lived experience always outranks the system's inference."*

---

## III. Time Quality Is a First-Class Variable

Two operators ask the compass the identical question — whether to hire a specific candidate. One asks in week two of their role. The other asks in month fourteen. The question is the same. The decision is not.

The difference is not just information — it is *time quality*. The depth of context, the strength of the adjacent signals, the operator's ability to assess fit, the cost of being wrong. These degrade or improve predictably as a function of where the operator sits in their own tenure, the stage of the process, and the urgency of the window.

ARCS treats this as a variable in the NCI computation, not a footnote. The cadence lens — one of the five NCI lenses — scores whether the decision is being made at the right moment in its natural lifecycle. A technically well-formed question asked two weeks too early gets a lower cadence score, a fidelity warning, and a HOLD recommendation if the degradation is severe enough.

This is not a subtle point. The most common failure mode in high-stakes decisions is not bad analysis — it is analysis conducted at the wrong moment in the decision's lifecycle. The system is designed to name that.

**Receipt:** `runtime/specs/time-quality-attribution-rom.json` — W-field inference rules; cadence NCI lens scoring; HOLD conditions when window quality falls below threshold.

---

## IV. Structure Is Earned Before It Is Named

Every named concept in this system arrived the same way: as a pattern that kept appearing in concrete sessions before it was given a name. DEWY was not designed as an acronym — it emerged from repeated observations that the same four variables kept determining whether a compass run was useful. The Golden Inchworm — the rule that every abstraction must be preceded by a worked example — is itself its own first example.

The pipeline encodes this axiom structurally. L0 fires on the raw input before any abstraction is applied. L1 decomposes before scoring. L3 scores the network before generating a True North. You cannot call something a FORK until you have named the two paths. You cannot issue a True North until you have earned the NCI. Each layer inherits from the layer below it — and the inheritance is not optional.

The Hyperstition Pipeline states this at the level of ideas: Ethereal → Loki Test → Receipt Evaluation → ROM. A concept begins as a suggestion. It earns a receipt when it survives an adversarial pass. It reaches ROM status when it has been referenced by downstream artifacts without producing failures. Nothing starts at ROM. Everything arrives there.

**Receipt:** `arcs-canon.md` — ROM Primitive 3 (Hyperstition Pipeline), ROM Primitive 4 (Golden Inchworm).

---

## V. Repair Visibly

When the system detects it has been building on a false premise, it does not correct silently and continue.

If L0 sharpens a 3,000-word context dump into a 280-character question, the compression ratio is logged in the receipt and the sharpened question is surfaced for operator confirmation before L1 fires. If the W-field is inferred rather than provided, the receipt logs it under `inferred_fields`. If two valid parse paths collide, the receipt logs it under `collision_fields`. The seams are visible.

This is **Kintsugi** — the Japanese art of repairing broken ceramics with gold rather than invisible adhesive. The repair is not hidden because hiding it would compromise the integrity of the whole. A receipt that silently absorbed a false premise is a receipt that cannot be trusted as a coordinate. The terrain it describes may not be the terrain you navigated.

The corollary: HOLD is not a failure state. REJECT is not a failure state. They are the visible announcement that the system found a seam before it became load-bearing. A Brief that was never issued because the NCI was 32 protected the operator from a false coordinate. The system did its job.

**Receipt:** `arcs-canon.md` — ROM Primitive 6 (Kintsugi Immune System). `arcs-field-os/specs/orient-prd.md` §3 L0 — OM behavior (compression logged, confirmation required). `runtime/specs/dewy-receipt-schema-v1.json` — `inferred_fields`, `collision_fields`, `validation_state`.

---

## VI. History Is a Teacher, Not a Jailer

Receipts accumulate. They form a trajectory — a record of where you were on the manifold at specific moments in time, with the conviction gradient and the ruin analysis and the True North all frozen together.

That trajectory does not constrain the present session. A YELLOW receipt from three months ago is not evidence against a GREEN receipt today. It is context that makes the GREEN receipt more interpretable — you can see the path from uncertainty to clarity, the specific turn where the Y-gate shifted, the receipt where the Loki counter stopped landing. The movement is itself information.

The `parent_receipt_id` field in the schema encodes this axiom structurally. Every compass run can be linked to its predecessor. The delta between sessions — NCI rising or falling, conviction gradient shifting, True North rotating — is as meaningful as any single session in isolation.

The constraint runs in one direction only: past receipts cannot veto present moves. The operator who saw a FORK six months ago and chose Path A is not bound to the logic of that receipt. New terrain changes the coordinate. The Receipt is a historical marker, not a constraint on navigation.

**Receipt:** `MEMORY.md v4.0` — *"History is a teacher, not a jailer; past receipts shape probabilities without veto power over present moves."* `runtime/specs/dewy-receipt-schema-v1.json` — `parent_receipt_id`, `version` (session lineage field).

---

## VII. Irreversibility Is Declared, Not Assumed

The system has no mechanism for detecting one-way doors on your behalf.

Some decisions can be unwound. Others cannot. The difference is consequential — not because irreversible decisions are necessarily worse, but because they require a different navigation posture. Once you are past the point of reversal, the ruin risk calculus changes. Options that existed before the commitment no longer exist. The terrain behind you closes.

**Write-Lock** is the rule that says: before you step through a one-way door, you name it as such. The declaration is made explicitly — in the PrepSession, in the receipt, in the artifact. You do not discover irreversibility after the fact. You commit to the topology before you cross it.

At the artifact level, the Kairos Lock is this axiom applied to documents and specs. When `arcs-field-os/specs/orient-prd.md` reached constitutional status — when it became the governing authority for downstream artifacts — it was Write-Locked. Any breaking change now requires a version bump, a new file, and a PR. The lock does not prevent change; it requires that change be declared as such.

The subtlety worth naming: a Write-Lock is not reluctance. It is precision. Knowing exactly which doors are one-way is the precondition for moving through them confidently.

**Receipt:** `arcs-canon.md` — ROM Primitive 7 (Write-Lock), Kairos Lock section. `arcs-field-os/specs/orient-prd.md` — v0.1.0 Kairos Lock declaration (§0).

---

## The Genome and the Organism

The L0–L7 stack is not arbitrary architecture. It is the structural consequence of the seven axioms above.

| Layer | Name | Governing axiom |
|---|---|---|
| L0 | Atomic signal | I — Start from the smallest honest unit; do not compress before you know what you have |
| L1 | Coherence | IV — Earn the abstraction; confirm question coherence before building the DEWY vector on top of it |
| L2 | Path survivability | III — Time quality is a variable; paths have survival windows that must be scored, not assumed |
| L3 | Cascade | II — NOTOMATION; the cascade surfaces the terrain, it does not select the path |
| L4 | Cross-domain | IV — earn the structure before naming it; each architectural layer inherits only from proven lower layers |
| L5 | Global coherence | V — Kintsugi; freeze the full state visibly; the receipt is the sealed seam |
| L6 | Ecosystem | VI — History as teacher; cross-session pattern recognition requires a dense receipt substrate *(not yet built)* |
| L7 | Meta-governance | VII — Write-Lock; the layer that enforces constitutional constraints across the full stack *(not yet built)* |

The current implementation runs L0–L5. L6 and L7 exist in the architecture because the axioms require them — not because they were designed first. The genome always precedes the organism.

> **ROM CANDIDATE [RC-II-001]:** The L6/L7 layer behavior described here is architecturally specified but not yet implemented. The claim that "cross-session pattern recognition requires a dense receipt substrate" is directionally receipted by the trajectory analysis design in `WORLD.md` (Observatory) but has not been formally implemented or validated. Promote to ROM when Observatory session trajectory analysis is live and tested.

---

## What This Part Established

Seven axioms. Each one the necessary consequence of the one before it. Together, they generate the architecture.

The reader who finishes here and asks *"could these rules be different?"* is asking the right question. The answer is: some of them could, at the cost of breaking the instrument in a specific way. NOTOMATION could be relaxed — but then the system is a recommendation engine, not a compass. The Write-Lock could be optional — but then Kairos Locks cannot be trusted as constitutional anchors. The axioms are the minimum set that preserves what the system is.

Part III goes where the axioms lead when stakes are highest: the Constitutional Court, and what happens when a decision requires more than a bearing.

---

## Confirmed Gaps in This Draft

| ID | Claim | Status | Upgrade path |
|---|---|---|---|
| RC-II-001 | L6 cross-session pattern recognition behavior | ROM CANDIDATE | Promote when Observatory trajectory analysis is live |
| RC-II-002 | L7 meta-governance constitutional enforcement behavior | ROM CANDIDATE | Promote when L7 is specified and implemented |
| RC-II-003 | "Most common failure mode is analysis at the wrong moment" (Axiom III) | ROM CANDIDATE — EMPIRICAL | Promote when Observatory session frequency data confirms cadence errors as the predominant failure mode. Cannot be confirmed by logical analysis alone — requires comparative frequency across error types. |

All other claims anchored to committed receipts listed inline.

---

*End of Part II — v0.1.0 CANONICAL. Upstream audit: CONDITIONAL CLEAR (2026-05-26). Three patches applied before commit: NOTOMATION definition made verbatim from arcs-canon.md ROM Primitive 1; genome table L4 row scoped to what Axiom IV established; RC-II-003 classified as EMPIRICAL with Observatory upgrade path.*
