# Tao of ARCS — Implementation Plan v1 (static artifacts → product)

> **Status:** PLAN. Deferred this week (budget reserved for the Todd/PRL project). This doc is the
> pickup. Nothing here is started.
> **Spec = the shipped artifacts.** Implementation is a *port*, not a redesign. The static HTML and
> the generators already encode the exact look, behavior, and data contract.

## What already exists (all committed, branch `claude/decision-geometry-logo-81fb56`)

- **SSOT:** `runtime/tao/proverbs.json` — 241 proverbs, atomic contract `{id, aspect, verb, source, text, movement, minted}`.
- **Generators (the microservices):** `scripts/gen_tao_views.py`, `gen_tao_corpus.py`, `gen_tao_alchemist.py` — each renders the SSOT into one surface; re-runnable as the corpus compounds.
- **Artifacts (deployed, private Claude Artifacts):** Amplifier grid `5e505614`, Views `93f9a41c`, Corpus `170b3ed3`, Alchemist `2e97f776`. Plus hand-built `_ARTIFACTS/arcs-tao.html`, `-cards.html`.
- **Governance:** `DESIGN.md` + `.impeccable/design.json` (the grammar), `tao-mint` skill, ADR-039/040/041, the SSOT schema in ADR-041.
- **Seed:** [[tao-as-object-level-taxonomy-of-problem-space]] — the product-bridge hypothesis.

## Target

Move the Tao from static artifacts into arcs-v9 **product surfaces** (inline-styles design system, no
new deps), with the **live Alchemist enricher** as the one real backend piece (the static stub made
real).

## Phases (prioritized, budget-aware)

### Phase 1 — Static → in-app routes (cheap, mechanical)
- Port the three generator outputs to Next.js routes: `/tao` (browsable corpus), `/tao/views`
  (Hokusai grid), `/tao/alchemist` (drag-drop). Read `proverbs.json` server-side; render via
  inline-styles React components reusing `src/ui/tokens.ts` (the tokens already match DESIGN.md).
- The generators' HTML/CSS is the exact target; translation to components is mechanical.
- **Effort: M. No new deps. No LLM cost.** Highest-certainty, lowest-risk.

### Phase 2 — The live Alchemist (the one real backend, and the point)
- `POST /api/alchemist` — body `{aId, bId}` → look up both proverbs → Anthropic SDK call → mint the
  **transmuted proverb** the static chamber deferred (`~ pending`). Return `{reaction, transmuted}`.
- Wire the drag-drop chamber to call it; the stub becomes the live synthesis.
- Grounds ADR-040's Alchemist (the offstage enricher, now an on-demand API). NOTOMATION holds: it
  *proposes* the transmuted proverb; a human ratifies before it enters the SSOT.
- Optional persistence: append accepted transmutations to `proverbs.json` with custody
  `source: "alchemist:<aId>+<bId>"`.
- **Effort: S–M. Uses existing `ANTHROPIC_API_KEY`. Cost = 1 cheap LLM call per combine, on-demand.**

### Phase 3 — Compounding + the taxonomy bridge (the north star)
- `tao-mint` **hook** on new `_DECISIONS/ADR-*.md` — auto-mint the grid on ADR creation (the
  oral-history compounds without a manual step).
- **Taxonomy API** (the seed): tag an artifact/problem by which D/R/W/C/H×verb cells it occupies →
  return the cell's proverbs as the applicable lenses. This is the Tao-as-product bridge
  ([[tao-as-object-level-taxonomy-of-problem-space]]). Keep it an open folksonomy: an artifact that
  fits no cell nominates a net-new aspect, it is not forced.
- **Effort: M. Defer until Phase 1–2 land and the taxonomy seed is validated on real artifacts.**

## Budget guidance (this week)

- **DEFER everything above.** Todd/PRL gets the week's budget (Zapier lead delivery, blocked on the
  Tidio plan — see the Todd master handoff).
- The artifacts + SSOT are the durable spec; nothing decays by waiting.
- When resumed: Phase 1 is the cheap mechanical port; **Phase 2 (live Alchemist) is the high-value
  backend**; Phase 3 is the product bridge.

## Open decisions (resolve at implementation, not now)

1. **SSOT: JSON vs Prisma model.** Recommend: stay JSON until Phase 2 persistence needs querying;
   promote to a `Proverb` model only if the Alchemist writes back at volume.
2. **Public vs gated.** The Tao is public-safe brand; likely public at `tao.arcs.care` or `/tao`
   (verify no client names ever leak from the SSOT — the mint discipline already forbids it).
3. **Where components live.** New `src/tao/` (organisms) vs extend `src/document/`. Recommend a
   dedicated `src/tao/` since it is a distinct surface family.
