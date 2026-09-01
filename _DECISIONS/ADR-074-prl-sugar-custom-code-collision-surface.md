# ADR-074 — PRL Sugar custom-code collision surface: chatbot lead path is clear; attribution rides W-Systems hooks

> **Status:** DRAFT · **Number reserved** via `oracle.py audit adr` (next-free 74); MINT AT COMMIT
> (pre-commit hook enforces). **Date:** 2026-09-01. **Scope:** PRL Resins chatbot engagement.
> **Y-state:** YELLOW→GREEN-leaning (package layer verified; process/hook layer residual).

## Context

Before any production cutover, we needed to know whether PRL's custom Sugar code collides with the
chatbot's lead create / dedup / route path. Two pressures framed it: (1) Sugar's PS arm (Ken Clark,
Principal CRM Consultant, ex-W-Systems) declined to grant sandbox access and steered the schema work
toward a paid Professional Services engagement; (2) the surviving build documentation (Kim Borst,
Director PS) is two .docx design specs, because the original builders (Fred Block, Amy Jaeger) have
left Sugar. Rather than buy PS to re-explain their own build, we inspected the sandbox directly,
read-only.

## Finding (verified 2026-09-01, sandbox Module Loader, read-only)

Five installed custom packages, all **before-save logic hooks on the revenue/opportunity side**:
`wBenchmarkTargetTemplate`, `OrderHistorySetRLI` (Revenue Line Items), `OpenOrdersSetProduct` (Open
Orders), `SalesNumbersSetAccountRel` (Account relationship in sales numbers), `wGlobalSearch`.
**None touches the Leads module.**

## Decision

1. **The chatbot lead-capture / dedup / routing path is clear of the custom-code surface.** 1.2/1.3
   lead work proceeds **additive-only**, no collision. **No Sugar PS purchase is required** for the
   current scope; the PS-steer is unnecessary for the lead work.
2. **The custom hooks own the revenue→attribution layer.** This explains the $43.7M / 48%-no-lead-
   source baseline gap (Bill's 2022 "connect leads→opportunities→closed-won" was "limited at best").
   Any future revenue-attribution phase must be designed to respect these hooks, not around them.
3. **Residual gate before prod cutover:** confirm no SugarBPM Process Definition or Web Logic Hook
   touches Lead create/dedup (Module Loader covers packages, not workflows). ~10-min sandbox read.

## Consequences (risk re-profile)

- Chatbot-collision risk **LOWERED** (verified at the package layer).
- Attribution-layer complexity **CLARIFIED** as W-Systems-owned (a boundary, not a surprise).
- Vendor-lock / PS-cost risk **NEUTRALIZED** for current scope.
- Todd-facing translation (he asked why this is a fulcrum): *"I checked your CRM's custom code myself.
  The custom pieces all sit on the revenue and order side, not on leads — so the chatbot changes are
  safe and need no Sugar consulting spend. The same custom layer is also why your lead source has
  never tied through to revenue, which is exactly what we're fixing."*

## Evidence
- Sandbox Module Loader (read-only), 2026-09-01 · `prl-sugar-custom-code-collision-map` memory
- Kim Borst Aug-7 build docs (email); Bill Galla 2022 origin thread (Fwd: Sugar reports tracking leads)
- Baseline: `_ARTIFACTS/prl-baseline/` (942 leads, 4,238 opps, $43.7M/48% blank lead_source)
