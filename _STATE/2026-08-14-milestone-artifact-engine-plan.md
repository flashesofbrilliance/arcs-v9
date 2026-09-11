# Milestone-artifact engine — 4-layer plan

**Status:** PLAN · 2026-08-14 · Layer 1 built (`5ca190b`), Layers 2–4 designed-not-built
**Origin:** the fortnight wins-map (`_ARTIFACTS/milestones/2026-08-13-fortnight.*`) proved a rendered,
visual milestone map is genuinely useful ("useful seeing it like this"). This generalizes it.

> Core insight: a **visual** is a faster rehydration + motivation surface than prose. Freeze the layout,
> vary only the data — so even a headless (cron) render can't reintroduce a layout bug. There is no
> layout to break, only data to fill.

## Layer 1 — the engine ✅ BUILT
- `_ARTIFACTS/milestones/_template.html` — frozen, pre-verified atomic layout (carries the 2026-08-14
  tag/heading wrap fix). Renders entirely from one JSON blob `window.MILESTONE_DATA`.
- `scripts/milestone_render.py` — inject `data.json` → dated `html` (stdlib; replaces ALL markers).
- First instance: `2026-08-13-fortnight.{json,html}` (render-verified in browser).
- **Data schema** (the "parameterized syntax"): `{period, span, head_sha, title, subtitle, lede,
  stats[{n,l,c}], trace[[day,count]], trace_caption, clusters[{title,accent,tag,sub,span?,items[{weight,html}]}],
  through{fronts[{t,b,c}], punch_html}}`. Accents: green|cyan|gold|violet|red.

## Layer 2 — the visual grammar (the `/impeccable` idea) — TODO
Author `_ARTIFACTS/milestones/GRAMMAR.md` via `/impeccable` (+ the `dataviz` skill for the trace chart).
A design-system sidecar formalizing what the template implies:
- **Atom catalog:** stat tile · activity bar · cluster card · major/minor marker · tag chip · through-line front.
- **Semantic-accent map:** green=revenue/shipped · cyan=product/canon · gold=governance · red=ruin/security ·
  violet=compounding/meta. (Accent encodes *win-type*, not decoration.)
- **Weight system:** major (gold dot, brighter) vs minor (dim square). Encodes significance, not order.
- **The `MILESTONE_DATA` schema** as the formal parameterized language every producer emits.
- Precedent: the existing DESIGN.md brand-grammar sidecar (also via `/impeccable`).
Lock this BEFORE building more producers, so they share one language.

## Layer 3 — a second artifact TYPE: state-of-ARCS (orientation / reheat) — TODO
Distinct from the wins-map: **momentum** (what shipped over a period) vs **orientation** (where things
stand NOW). Same engine + grammar, different data shape — clusters become **Active tracks · Open flags ·
Live surfaces · Forked sessions · Recent decisions**, fed from `snapshot.json` + latest handoff + `_SEEDS`.
- **Purpose:** a rehydration surface for a chunked handoff — the visual reheats context faster than prose
  ([[arcs-assumes-stateful-human-memory-needs-rewarming]], [[design-for-arriving-cognitive-state]]).
- **Trigger discipline:** at the handoff/chunk boundary or `/handoff-pickup` — NOT per ADR/DEWY (20 ADRs
  in 2 weeks = noise). A per-ADR render is over-firing.
- Producer: a `state_gather` step (or fold into `/handoff`) emits state-shaped `MILESTONE_DATA`.

## Layer 4 — the weekly night worker (draft-for-review) — TODO
Decided cadence: **weekly**; autonomy: **draft-for-review** (NOTOMATION — narrative judgment stays human).
- A scheduled agent (schedule skill / scheduled-tasks): gather the week (git + `/night-moves` logs) →
  synthesize themed major/minor clusters (judgment) → emit `MILESTONE_DATA` → `milestone_render.py` →
  commit dated instance to `_ARTIFACTS/milestones/` → publish a **private** draft artifact → ping for review.
- **Headless caveat = why Layer 1 matters:** a cron agent can't visually spot-check; the frozen template
  means only data changes, so there's nothing new to break. Do NOT let the worker hand-edit layout.

## Sequence note
Build order is flexible, but Layer 2 (grammar) ideally precedes Layers 3–4 so producers share the language.
Each layer is independently shippable on the Layer-1 engine that already exists.
