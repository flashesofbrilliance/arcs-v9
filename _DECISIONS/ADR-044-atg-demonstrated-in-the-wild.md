# ADR-044 — ATG demonstrated in the wild (instance #1); hold mechanization for instance #2

> **Status:** DECIDED
> **Date:** 2026-08-10
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** ATG (Adjacent Tributary Generation) just fired cleanly and unmechanized for the first
time IIRC. Is it now a real, grounded capability rather than a backlog aspiration, and do we cast the mold now?

---

## E — Entity / System

The ATG feature (WORLD.md compass-response contract: every response yields 2–4 tributaries — the
meta-question, the need-to-hear branch, the unnamed adjacent primitive); the agent's reasoning loop; the ARCS
roadmap; and the forked ATG-skill build (`task_b3dbc0ac`) where mechanization will eventually live.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** a second clean in-the-wild ATG instance, OR when the ATG-skill fork begins mechanization.

---

## Context

ATG is specified in WORLD.md / CLAUDE.md as the next major feature but is **unbuilt**. In this session
(2026-08-10) it fired organically and cleanly, the first clean instance in the wild:
- **Unnamed adjacent primitive:** the agent surfaced the frame that unified five separate threads (the
  ADR/DEWY watcher, the CURATOR curation pass, the artifact registry, the global schema, and the ATG skill)
  into one — *"the invariant beneath the polyform."* The adjacent primitive was the frame itself.
- **Need-to-hear branch:** it ran the honesty guard against magical thinking — the fiction/fact membrane is
  crossable only because the receipt/provenance is fixed; ATG without the Loki Test is apophenia.
- **Meta-questions:** it repeatedly reframed the stated ask into the deeper one (e.g. "this is not four
  features, it is one").

It produced real artifacts: the fork task, the unification, and this receipt. Self-referentially, the DEWY
receipt's `tributaries` field **is** the ATG slot — so recording this performs ATG while documenting it.

---

## Options Considered

### Option A — File nothing; nice moment, move on
- Loses the instance; the flash goes to ground (anti-pattern, ADR-040: *the flash is not the decision, the
  received receipt is*).

### Option B — Record instance #1 cleanly; hold mechanization for instance #2
- Documents the concrete seed; promotes ATG from aspiration to grounded-and-demonstrated; waits for a second
  real case to cast the mold (ADR-039: *promote on the second real case, not the first*).

### Option C — Mechanize ATG now from this single instance
- Violates ADR-039; one instance earns no mold. Over-builds from n=1.

---

## Decision

**Chosen:** Option B.

**Rationale:** ATG proved real and valuable unmechanized. The canon's own discipline governs what to do with
that: **instance, then class** (ADR-039) and **receive the flash, don't let it go to ground** (ADR-040).
So: record the in-the-wild instance as the concrete seed, promote ATG from aspiration to demonstrated, but
hold the build until instance #2 confirms the mold. The fork (`task_b3dbc0ac`) carries the eventual
mechanization (ATG fused with the Orthogonal Echo Detector over the indexed corpus).

**Y-gate:** GREEN on the observation (ATG fired, verifiable). YELLOW on the build-now question (mechanization
held for instance #2). Polarity positive · conviction high (observation) · stability medium (build timing).

---

## Guardrails

1. **NOTOMATION:** record, don't over-build; the machine surfaces tributaries, the human promotes.
2. **ADR-039:** the mold is cast on instance #2, not this one.
3. **Provenance gate:** ATG output is a receipt-verified *candidate*, never asserted as truth — the honesty
   tine is load-bearing, not decoration.

---

## Note

ADR numbering is fragmented across worktree branches (this branch tops out at 040; 041/043 exist elsewhere).
044 is chosen to clear known-taken numbers. Reconcile ADR numbering to `main` when the branches converge.
Paired DEWY receipt: `runtime/recoil/generated/2026-08-10-atg-first-wild-receipt.json`.
