# Claude Code Pickup — ADR-009: Design System Canonicalization in arcs-v9

> **Status:** READY
> **Generated from:** `_DECISIONS/ADR-009-design-system-canonicalization.md`
> **Horizon:** QUARTER | **Conviction:** HIGH
> **Auto-generated:** 2026-10-06 18:04 UTC

---

## What was decided

**Chosen:** Option A

**Rationale:** arcs-app already solved this problem — the Register pattern maps directly to ARCS's three
UX contexts. Recovering from git history costs hours vs. rebuilding from scratch. Inline styles are the
established constitutional contract. `tokens.ts` bridges the @theme CSS vars to component-level style
objects without violating the no-className rule.

**Trade-offs accepted:** tokens.ts will have some duplication with globals.css @theme until a future
single-source-of-truth ADR. Accepted at QUARTER horizon — duplication is visible and localized.

## Implementation pointer

Recover from arcs-app git log — find pre-stub-revert commit for Badge.

## Full ADR

See `_DECISIONS/ADR-009-design-system-canonicalization.md` for complete context, options considered, and rationale.

## Done when

`_QUEUE/PENDING.md` ADR-009 row updated to `DONE` + commit.
