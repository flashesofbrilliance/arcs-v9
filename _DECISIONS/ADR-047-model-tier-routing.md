# ADR-047 — Model-Tier Routing by Reversibility × Value

> **Status:** DECIDED
> **Date:** 2026-08-11
> **Commit:** (set at merge)

> Numbering note: the seeding task referenced this as "ADR-045", but ADR-045 (night-moves) and
> ADR-046 (witness) were already taken. Filed as ADR-047, next free number.

---

## D — The Decision

**Sharp question:** How should ARCS pick which Claude tier (Haiku/Sonnet/Opus) carries a task, cheaply and without ever trading survivability for cost?

---

## E — Entity / System

`scripts/model_tier_router.py` — a stdlib heuristic classifier. Consumed by a human (and, later,
by the conductor's-map staff layer) as a *recommendation*. Touches no route, no model call, no state.

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** the cue lexicons miss a class of task often enough that recommendations feel wrong; or the router gets wired into an automated dispatch layer (would change the NOTOMATION posture and demand a stricter guardrail proof).

---

## Context

The conductor's-map principle (AGENTS.md) says: push each job to the cheapest layer that can do
it well. Prepaid-reflexes ([[prepaid-reflexes-tier-descent]]) says the expensive model paves a
groove once and the cheap model rolls it reflexively. But cost-descent has a ruin edge: downgrading
an irreversible or ruin-exposed task to a cheap tier to save money is exactly the
[[cost-leaks-ruin-vector-no-silent-toggle-regression]] failure inverted — cheapness winning over
survivability. The WORLD.md BAR/free-solo frame is explicit: a single mistake on a zero-margin
task must be treated as a design bug, not optimized into.

The watcher family (`surface_watch.py`, `adr_dewy_watch.py`) already established the shape: a
stdlib, zero-dep, cue-lexicon classifier that emits candidates for a human and never acts. Reuse it.

---

## Options Considered

### Option A — Heuristic cue-lexicon classifier (chosen)
- Compiled regex lexicons per dimension (routine / structured / abductive) + a ruin lexicon that only pushes UP.
- Pros: zero cost, zero deps, NOTOMATION-clean, same shape as the watchers, auditable rationale.
- Cons: lexicons are hand-tuned; will miss novel phrasings until extended.

### Option B — Ask a cheap model to classify the task
- Pros: more robust to phrasing.
- Cons: costs a model call per routing decision (routing the router), a Loki loop; violates the cheap/stdlib goal.

### Option C — No router; human picks the tier every time
- Pros: simplest.
- Cons: no scaffold, no audit trail, no default; the exact "scaffold cognition" gap NOTOMATION exists to fill.

---

## Decision

**Chosen:** Option A.

**Rationale:** Matches the watcher pattern the repo already trusts, costs nothing, and keeps the
human in the loop. The router *recommends*; it never switches a model. Three guardrails encode the
ruin edge directly:
1. **Ruin floor** — any ruin/irreversible cue (delete, drop table, migration, deploy, prod, payment, auth, secret, publish, send…) floors the recommendation at OPUS and flags `needs_human_confirm`. It is never downgraded, whatever else the task looks like.
2. **Ambiguity rounds up** — no cue match → SONNET (safe middle), never the HAIKU floor.
3. **Ties break toward the more capable tier.**

**Trade-offs accepted:** Lexicon maintenance; occasional over-escalation (a routine task with a
ruin-adjacent word gets OPUS + a confirm prompt). Over-escalation is the safe failure direction.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Strongest case against — a hand-tuned lexicon is brittle and will misroute
unfamiliar phrasing, giving false confidence. Mitigation: it only ever *recommends*, the guardrail
fails toward OPUS (safe direction), and `--self-test` pins the guardrail invariant so a regression
that lets a ruin-exposed task downgrade fails CI-style.

---

## Consequences

- New `scripts/model_tier_router.py` (stdlib, `--self-test`, `--stdin`, `--json`, `--sessions`).
- Recommendations logged to `_INBOX/tier-recommendations.jsonl` on session sweeps (audit trail, dedup by hash).
- Unblocks: wiring tier recommendations into the staff/conductor layer later (out of scope here).
- New decision it creates: if/when this is ever wired into automated dispatch, the guardrail needs a stronger proof than a self-test (that would flip the NOTOMATION posture).

**Implementation pointer:** `scripts/model_tier_router.py`

---

## Linked receipts / ADRs

- [[prepaid-reflexes-tier-descent]] — the cost-descent principle this routes for
- [[cost-leaks-ruin-vector-no-silent-toggle-regression]] — the ruin edge the guardrail defends
- ADR-034 — enforcement-parity (recommend-don't-enforce lineage)
- `scripts/surface_watch.py`, `scripts/adr_dewy_watch.py` — the pattern reused
