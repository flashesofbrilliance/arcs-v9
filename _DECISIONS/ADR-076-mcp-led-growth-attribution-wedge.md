# ADR-076 — MCP-Led Growth: the attribution wedge (MCP is the free land, the API is the paid expand)

> **Status:** DRAFT (adopted as directional GTM thesis; the build is gated on a demand signal, see Y)
> **Date:** 2026-09-07
> **Author:** Claude (with Zach)
> **Stakeholders:** ARCS distribution / arcs-skills marketplace / compass + receipt substrate / OSS family
>
> **Provenance note:** Flagged by Zach on 2026-09-04 while reviewing Dealroom's "four ways to work
> with us" + `/mcp/` ("MCP-led growth could be huge for ARCS"). Corroborated by a delegated research
> crawl the same day (`_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md`, section E)
> and banked as memory `arcs-mcp-led-growth-gtm`.
>
> **Numbering note (collision resolved 2026-09-07):** originally allocated and drafted as **ADR-075**
> off the oracle (`oracle.py next adr` → 75). A parallel session concurrently minted a *different*
> **ADR-075 — The Metabolic Router**, which merged to `main` first as **DECIDED**. Per the oracle-first
> doctrine and the ADR-072 precedent, the ratified/merged canon ADR keeps the number and this unmerged
> DRAFT renumbered via the oracle to **ADR-076** (`_SEEDS/_oracle.json` committed at 76). This is a
> mechanical numbering collision (two sessions raced the same free number), not a canon-content
> collision. This ADR records the *direction*; it does not authorize a build beyond the Y validation step.

---

## D — The Decision

**Sharp question:** As agents (Claude, Cursor, Perplexity, etc.) become the surface where people ask
questions, how does ARCS get distributed — and what is the wedge that a general model cannot copy?

**Decision:** Adopt **MCP-led growth** as a primary distribution motion, in a **land / expand** shape:

- **MCP is the free LAND layer** riding on the authed core: "bring ARCS into your AI tools, free with
  your account, just sign in, no setup." Activation friction near zero.
- **The API is the paid EXPAND**: higher limits, hosted MCP for teams, real-time sync, custom rate
  limits.
- **The wedge is attribution, not features.** Every ARCS answer through the connector is a **live,
  cited receipt — not the model guessing.** This is already ARCS's constitutional promise
  (NOTOMATION, earned fidelity, refusal to overclaim), so the MCP pitch requires *no new claim*: it
  is the receipt substrate exposed as a tool. The reference model (Dealroom) proves attribution *is*
  the MCP value prop; ARCS starts with the substrate Dealroom had to build.
- **Tools are read-only and verb+entity-namespaced** (`analyze_receipt`, `search_decisions`,
  `compare_founders`, `entity_lineage`): safety-by-construction ("every tool reads, nothing changes")
  is part of the sell.
- **Public content surfaces double as MCP on-ramps**: a "Connect an agent →" affordance on each ARCS
  report/receipt/blog surface so the marketing artifact and the connector are one funnel. Onboarding
  is itself productized (a prompt pack + example JTBD prompts + a coming-soon one-click skill recipe).

---

## E — Entity / System

- `flashesofbrilliance/arcs-skills` (the Claude Code marketplace) and the OSS public-good family —
  the existing distribution rails this rides on ([[oss-family-distribution-registry]]).
- The compass + **Receipt / DEWY substrate** (`prisma/schema.prisma`, `src/app/api/compass/route.ts`)
  — the freehold whose attribution IS the wedge ([[engine-sovereignty-gradient]], ADR-072).
- A future **ARCS MCP server** (not yet built) exposing read-only receipt/decision tools.
- Public content surfaces (`good.arcs.care`, `/blog/nftt/*`, per-engagement report pages) — the
  on-ramps.
- Evidence base: `_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md` (Dealroom model).

---

## W — Window

**Horizon:** QUARTERS to YEARS. This is a distribution doctrine, not a sprint. It is a **two-way door
at the direction level** (adopting the thesis costs nothing and is reversible) but the *build* of a
hosted MCP server is a larger commitment that should follow a demand signal, not precede it.

**Revisit / advance triggers:** (1) inbound asking to query ARCS from an agent; (2) the arcs-skills
marketplace showing pull for a data/connector tool; (3) a first read-only MCP tool over the public
receipt/blog corpus shipped as a cheap probe and used. Any one of these graduates this from DRAFT.

---

## Y — Conviction

**Y-state: YELLOW (directional, not validated).** The *fit* is high-conviction: ARCS already has the
attribution substrate, already ships per-client Claude Code surfaces, already runs an OSS/MCP-tool
family — so the pieces rhyme. What is **not** yet proven is *demand*: no one has yet asked to query
ARCS from an agent, and building a hosted MCP server before that signal is the failure mode this ADR
explicitly guards against ([[explore-value-before-declining-not-reflexive-restraint]] balanced against
[[cheap-tripwire-before-expensive-jtbd]]).

**Falsifier:** if a cheap read-only probe (one MCP tool over the already-public corpus) ships and
draws no usage across a fair window, the thesis is weakened and this stays DRAFT or is retired. The
honest boundary: this is a bet on where distribution is going, stated as a bet, not a validated plan.

---

## Consequences

- **Opens:** a distribution path that does not depend on ARCS owning the end-user surface; the receipt
  substrate becomes a product others pull, not only a page people visit.
- **Commits (softly):** future public surfaces should be built agent-consumable (a machine-readable /
  "connect an agent" affordance), the way Dealroom ships an "agent endpoint" on every chart. Cheap to
  honor now, expensive to retrofit later.
- **Guards against:** building the hosted MCP server as speculative infra. The probe-before-platform
  ordering is the load-bearing constraint.
- **Does not change:** the receipt/DEWY schema (freehold; one-way door, untouched here), NOTOMATION,
  or the real-data-only rule — MCP answers are receipts, never fabricated.

---

## Linked

- Memory: `arcs-mcp-led-growth-gtm`, `dealroom-talent-report-grammar`
- Evidence: `_ARTIFACTS/research/2026-09-04-dealroom-talent-report-grammar.md`
- ADRs: ADR-072 (engine-sovereignty — the substrate is the freehold), ADR-054 (free to hold, metered
  to fire — the land/expand echo), the PLG-onramp-as-mindset-filter thesis, the OSS-family distribution
  registry.
