# ADR-014 — CI/CD Governance — NOTOMATION Circuit Breaker Model

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** 5f8529d (feat: NOTOMATION circuit breakers)

## D — The Decision

**Sharp question:** What is the correct automation authority ceiling for arcs-care CI/CD,
and how do we enforce NOTOMATION (ROM Primitive #1) without preventing automated
build-failure repair?

## E — Entity / System

- `.github/workflows/ci.yml` — lint + build gate
- `.github/workflows/vercel-ai-fix.yml` — Claude Code auto-repair
- `.github/workflows/promote.yml` — prod promote gate
- `scripts/smoke.sh` — post-deploy validation

## W — Window

**Horizon:** PERMANENT (ROM Primitive #1 is constitutional)
**Revisit trigger:** If the team expands to 3+ engineers and the human-approve-to-promote
loop becomes a measurable velocity bottleneck (>2 deploys/day blocked on human availability).

## Context

arcs-care had no CI/CD pipeline. Adding automated build repair (vercel-ai-fix.yml) created
a NOTOMATION violation risk: automation could promote to production without revealed human
preference. The fix required a governance model that allows automation to repair while
preserving human authority over the prod surface.

## Options Considered

### Option A — Taxonomy/Tier Model
- Assign automation tiers (safe / supervised / human-only) per action type
- Pros: familiar, easy to document
- Cons: tiers are static; new actions require re-classification; brittle at boundaries

### Option B — Circuit Breaker Model (chosen)
- Named trip signals (SIGNAL_PROMOTE_GATE, SIGNAL_SURFACE_BREACH, etc.)
- Each signal has a defined trip condition and a fixed human-required response
- Automation authority ceiling = preview; prod promote = workflow_dispatch only
- Pros: self-documenting; each signal is independently auditable; maps directly to NOTOMATION
- Cons: signal proliferation risk if poorly scoped

## Decision

**Chosen:** Option B — Circuit Breaker Model

**Rationale:** NOTOMATION is not a tier — it's a topology. The question isn't "what level of
automation is safe?" but "at what boundary does automation stop and human agency begin?" The
circuit breaker model names the exact boundary conditions, making each one independently
auditable. `workflow_dispatch` is the only primitive that requires revealed human preference —
using it as the prod-promote gate directly encodes ROM Primitive #1 into the pipeline topology.

**Trade-offs accepted:** Every prod deploy requires a human to run `gh workflow run promote.yml`.
No continuous deployment. This is intentional — arcs.care is a decision intelligence product;
its deploy process should model the same human-agency primitives it teaches.

**Named signals in force:**

| Signal | Trip condition | Required human action |
|--------|---------------|----------------------|
| SIGNAL_PROMOTE_GATE | Any prod promote attempt | Must be workflow_dispatch with deployment_id + reason |
| SIGNAL_SURFACE_BREACH | Fix touches >3 files OR >50 lines OR auth/compass routes | Human code review before promote |
| SIGNAL_SCHEMA_DRIFT | Valid compass payload returns missing fields | Halt; diagnose API contract |
| SIGNAL_ENV_DRIFT | Smoke fails post-promote | Do not auto-rollback; human diagnoses env delta |
| SIGNAL_FIX_LOOP | Auto-fix applied same failure >2x | Circuit open; escalate to human |

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** "This slows shipping velocity — every prod deploy requires a human action even
for a 1-line fix." Counter: the slowdown is the point. The human-approve step is not overhead;
it is the product's epistemic integrity check. A decision intelligence tool that auto-ships
to prod without human sign-off violates its own first principle.

## Consequences

- Prod can never be updated without a human running `promote.yml`
- Claude Code auto-repair is bounded to preview surface
- Decision Receipts (GitHub Issues) are posted for every auto-fix attempt
- Smoke tests gate both preview validation and post-promote verification

**Implementation pointer:** `.github/workflows/promote.yml`, `scripts/smoke.sh`
ADR-014 is the governance record for the entire `.github/workflows/` topology in arcs-care.
