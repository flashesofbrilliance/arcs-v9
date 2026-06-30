# ADR-027 — Observatory as a render surface over the git/receipt/ordinal substrate

**Status:** SEED / DRAFT — Implementor-drafted (Claude Code), routed UP for primary-disciple ruling. NOT decided. Do not treat as canonical.
**Date:** 2026-06-24
**Author:** delegated subordinate, from the 2026-06-24 session synthesis.

## Decision (proposed, for ruling)

The Observatory stops being a replay-UI-over-a-database and becomes a **render surface over one indelible substrate**: git (the content-addressed, append-only, block-by-block-traversable chain) carrying receipts + ordinals + ADRs as block types, instrumented with OpenTelemetry, with the kinematic manifold as the trajectory math and ADR-023's lattice as the structure rendered.

## Substrate map (each WORLD.md Observatory verb → a substrate primitive)

| Observatory verb (WORLD.md) | Substrate operation |
|---|---|
| scrub backward to any Receipt | walk the commit chain (`git log` / `git cat-file`) |
| overlay two sessions | diff two ordinal/receipt chains |
| annotate inflection points | annotate commits/receipts (OTel events) |
| conviction gradient peak/collapse | kinematic D1–D3 over the receipt signal-vs-time |
| every decision recorded / replayable | the append-only chain IS the recording |
| cold-start replay | the ordinal reload-incantation ("load #001, board reconstructs") |

## Why now / grounding

Not new philosophy — it unifies things already in canon: the ordinal substrate (#001), git-as-inscription-layer, the receipt model, ADR-023 (observability lattice = weighted folksonomy DAG over receipts), and the recovered interactive `/observatory` route (PR #21) as the render shell.

## Hard constraints (carried from tonight's rulings — do not relax)

- **Kinematics two-zone:** only D1–D3 are reliably computable over a real signal; D5+ are operators, not finite differences (numerical wall). The Observatory ships D1–D3 trajectories now; operator-zone views are gated on the D5–D10 reformulation. Don't render D4+ "texture" as if measured.
- **OTel-over-git-commits is net-new instrumentation** — spans don't emit from commits for free; that's a real build, not config.
- **NOTOMATION:** the Observatory *renders* the chain; it does not adjudicate it. Replay ≠ re-decision.

## Open questions for the primary to rule

1. Is the Observatory's data model literally git (commits as blocks), or git + a derived index? (Performance vs. fidelity.)
2. Does it read receipts from the DB (current Receipt model) or from inscribed ordinals/commits, or both?
3. OTel backend: which drain (Vercel Observability / self-hosted)?
4. Relationship to the existing static `/observatory/index.html` demo + the interactive `src/app/observatory/page.tsx` — extend, or rebuild against this substrate?

## Y-gate

DRAFT / HELD — architecture decision, primary-lane. Seed only; not graded until ruled.
