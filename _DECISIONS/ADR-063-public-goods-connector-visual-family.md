# ADR-063 — The public-goods connector fleet is its own locked visual family

- **Status:** Accepted
- **Date:** 2026-08-16
- **Allocated:** `scripts/oracle.py next adr` → 63 (never hand-guessed; see ADR-057)
- **Relates to:** ADR-056 (per-tool `<tool>.arcs.care` connector), ADR-053 (open/private seam),
  ADR-055 (seedbank two-tier). WORLD.md render scale. PRODUCT.md "per-engagement canon families
  may carry their own locked visual world."

## Context

The ADR-056 connector fleet (`good.arcs.care` + per-tool pages, rendered by
`scripts/connector_render.py` from `_SEEDS/`) needed visual diversity across a growing set of
public goods so the family does not read as one flat cyan wall. Per-surface colorways were added
(CLI = violet, web = amber) alongside the canonical cyan/green.

The canonical ARCS accent palette is **cyan `#00F0FF` / green `#00FF9D` / gold `#FFD700` /
red `#FF4D6D`** only. Violet and amber are **not** canon tokens. Left unrecorded, they would read as
design-system drift.

## Decision

The public-goods connector fleet is declared **its own locked visual family**, the same mechanism
that legitimizes the Louisville omakase world (PRODUCT.md). The family is bound by:

- **Neutrals: canonical ARCS tokens, no deviation.** `--bg#020408 · surface#0d1117 · elev#131a24 ·
  border#1e293b · fg1#e2e8f0 · fg2#94a3b8 · fg3#64748b`. (This realigned the fleet off the
  slightly-bespoke ramp inherited from the hand-built `resume-tailor.html` reference.)
- **Type: canonical** — Inter + JetBrains Mono; the WORLD.md earned-fidelity register.
- **Accents: an extended palette, grouped by tool KIND** (the one sanctioned departure):
  - `skill` → canon **cyan → green** (also the shipped `resume-tailor` page; anchors the family)
  - `cli` → **violet `#A78BFA` → indigo `#6D8BFF`**
  - `web` → **amber `#FFC24D` → orange `#FF8A3D`**
- **Boundary:** this extended palette is scoped to `*.arcs.care` connector surfaces and
  `good.arcs.care` ONLY. It does **not** leak into product surfaces (app/dashboard/brief/status),
  which remain strict cyan/green/gold/red per WORLD.md.

The palette lives as `THEMES` in `scripts/connector_render.py`; group is a per-tool field in
`_SEEDS/connectors.json`. Changing a group's hue is a one-line edit, re-rendered from SSOT.

## Consequences

- Visual diversity across the fleet is now sanctioned and mechanized, not drift.
- `resume-tailor.html` (hand-built, already shipped) still carries the slightly-bespoke neutral ramp;
  a later pass should realign it to the canon neutrals above. Tracked, non-blocking.
- Any new public good picks a group and inherits its family accent automatically. A hue outside
  {cyan/green, violet, amber} on a connector requires amending this ADR.
