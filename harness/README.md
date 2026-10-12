# ARCS Agentic Harness — not yet built

> **Status:** placeholder only. No harness code exists yet. This file exists so the directory
> boundary is fixed before the first harness commit lands, per the 2026-10-06 canon-structure
> decision (`CLAUDE.md` → Handoff v3.22.0, `MEMORY.md` v3.12.0).

## What goes here

The composition layer that consumes `operators/` — ARCS operators as first-class capabilities,
orchestration/delegation by JTBD, RAG + model routing, polymorphic surface composition,
sealed-environment + external-dependency integration, russian-doll/ziggeraut self-contained
artifacts, JIT compile from any entry point, decentralized-interoperable ID-based refs,
multi-tenant isolation.

## What does NOT go here

Atomic decision-reasoning components (LAB/BAR/SAGE/CURATOR/KAIROS/CONTRACT/OPERATOR20/KINTSUGI,
primitives, pipeline, systems, storage) — those stay in `operators/`. This directory is a
*consumer* of `operators/`, not an extension of its atomic-design taxonomy.

## Dependency contract

See `operators/README.md` → "Composition Boundary — Agentic Harness" for the public surface
this layer may depend on (currently TODO-filled, pending the harness's first real JTBD).
Harness code must not reach past the entry points declared there once they're filled in.

## Next steps (not started)

- Pick the harness's actual file shape (thin layer on `arcs_pipeline_v1.py` /
  `arcs_runtime_service.py`, or a new file family — worker runtime, sealed-env builder,
  ziggeraut/russian-doll renderer, UA/player schema, ticket outputs).
- Fill the three TODOs in `operators/README.md`'s Composition Boundary section once the
  harness's real dependencies on `operators/` are known.
