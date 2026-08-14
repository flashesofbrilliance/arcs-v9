# ADR-056 — The ARCS tie-in connector: per-tool `<tool>.arcs.care` = the umbrella head

**Status:** Accepted · 2026-08-13

## Context
The open repos (Tier-A/B, ADR-055) are brand-neutral standalone public goods. germinate's
`docs/adjacencies.md` scoped an `arcs` umbrella as a thin aggregator with "a head mini-app on
labs.arcs.care." `forge.arcs.care` already exists as a live, ungated arcs.care page that explains a
tool and ties it into ARCS — i.e. the reference implementation of a **connector**. Missing: the
decision to make this the family pattern.

## Decision
Every microservice / public good in the family gets an **ARCS tie-in connector**: a hosted, ungated
`<tool>.arcs.care` page that explains the tool and ties the open repo to the ARCS ecosystem.

- The connector is the **socket made into a hosted surface** — the **fourth face** of the ADR-053 seam:
  *public method / private rosetta · dormant seed / animating spark · free-to-hold / metered-to-fire ·*
  **open repo / arcs.care connector**.
- The **fleet of connectors *is* the `arcs` umbrella head** (aggregator, not monolith).
- **Rendered from SSOT, not hand-built:** the same "one invariant shape, many surfaces" machinery
  forge already proves (counterpart-forge / omakase). Each `_SEEDS/index.jsonl` row gets a
  `connector: <tool>.arcs.care` field; pages generate from the seed.

## Consequences
- **Hard air-gap:** a connector is PUBLIC — it carries the open tool's story + the tie-in, **never** the
  `_SEEDS` registry, rosetta, or ripeness priors. Same discipline as recoil external artifacts; enforced
  by a connector air-gap tripwire (mirrors ADR-051 family-tripwire).
- **Build forks to the umbrella/omakase session** — not hand-cranked. `forge.arcs.care` is the template.
- Ties the open bank (ADR-055) to the private spark (ADR-053) through one public surface per tool.

## Lineage
[[arcs-tie-in-connector-per-public-good]] · ADR-053 · ADR-055 · [[counterpart-forge-pipeline]] ·
[[plan-generalize-omakase-site]] · germinate `docs/adjacencies.md` §"The arcs umbrella".
