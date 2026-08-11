# ADR-045 — Model-tier routing by reversibility × value

> **Status:** DECIDED
> **Date:** 2026-08-11
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Should every task run on the top model, or route each to the cheapest capable model by
reversibility × value?

<!-- JTBD: "get this task done at the lowest cost that still meets its consequence" · TOOL-FIT: model tier, not always Opus · EX-ANTE: Opus-on-everything drove weekly usage to 52% mid-week -->

## E — Entity / System

The agent/session model selection; ARCS routing (extends "cook temp for the job"); weekly usage / cost.

## W — Window

**Horizon:** TODAY / ongoing. **Revisit trigger:** when a task-classifier or an automated router is built.

## Context

Opus-on-everything burned weekly usage (52% by mid-week) across a 686k-token marathon session that was ~60%
routine (edits, commits, sweeps, deploys, template drafts). The adjacent canon is "cook temp for the job"
([[cook-temp-for-the-job-deductive]]) — but that routes *temperature*, not *model tier*. No model-tier router
exists. Cost is a global goal ([[cost-efficiency-global-goal]]); context size is the larger co-lever.

## Decision

Route by **reversibility × value**:
- **Routine → Haiku** — deductive, reversible, low-consequence: recognizer/grep sweeps, watcher regex, file
  edits, commits, deploys, form toggles, template-fill drafts, serialization.
- **Structured → Sonnet** — judgment inside guardrails: spec-driven generation, verify-against-source,
  routine review, most emails.
- **Judgment → Opus** — abductive, high-value, or irreversible: curation/CURATOR, ATG/orthogonal-echo, recoil
  synthesis, socratic review, gauntlet/red-team, ARR register-matching, canon/ADR decisions, design direction.

**Co-levers (cost is not model alone):** end long sessions / work in narrow-scoped ones (context size is the
bigger burn); fewer tool calls (screenshots/re-renders cost tokens).

## Guardrails

1. Never downgrade ruin-exposed or irreversible work to save cost; value dominates the routing.
2. When unsure of tier, round up one level.
3. Model selection is currently a human control (`/model`); an automated router is a future build
   (surface-candidate — same classify-and-route shape as the watcher family).
