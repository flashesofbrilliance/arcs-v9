# ADR-009 — Design System Canonicalization in arcs-v9

> **Status:** DECIDED
> **Date:** 2026-05-27
> **Commit:** (set at merge)

---

## D — The Decision

Should ARCS have a canonical inline-style component library in arcs-v9, recovering the Register-pattern
Badge/Button/Card from arcs-app git history and extending from arcs-v9's design tokens — rather than
relying on per-page ad-hoc inline styles or shadcn stubs?

---

## E — Entity / System

- `arcs-v9/src/ui/` — new directory (does not yet exist); will house canonical component set
- `arcs-v9/src/ui/tokens.ts` — design token bridge (color, font, radius, spacing constants)
- `arcs-app/src/ui/` — stale repo; source of recovery for pre-stub-revert Badge/Button/Card
- All existing arcs-v9 pages (compass, dashboard, brief, history, prep) that use ad-hoc inline styles

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** Component count exceeds 12, or inline-style composition becomes a measurable
maintenance burden (e.g., spacing/color values diverge across 3+ pages).

---

## Context

arcs-v9 currently has no shared component library. Every page re-solves spacing, color refs, and layout
primitives via ad-hoc inline style objects. The design token palette lives in WORLD.md and CLAUDE.md
as a comment block — not in code.

arcs-app had a working implementation — Badge with three Register variants (cockpit/governance/light),
Button, Card — all using inline styles and a design token import (`color`, `font`, `radius`, `border`).
That implementation was regressed to shadcn stubs in a recent commit and now exists only in arcs-app's
git history.

arcs-v9 loads Tailwind via `@import "tailwindcss"` in globals.css for `@theme` token CSS vars — but
no page or component uses `className` utility application. The constitutional rule (CLAUDE.md, AGENTS.md,
WORLD.md) is explicit: **inline styles only — no CSS files, no Tailwind, no className.**

The job: a developer building a new ARCS screen should reach for `<Badge>`, `<Button>`, `<Panel>` without
re-solving color, spacing, or Register decisions.

*Research summary:*
- Monorepo-style shared library wins at scale; migrate one component type at a time
- Audit current usage before building — prevents over-engineering
- TypeScript-typed variants catch misuse at build time
- LOE to recover + port a minimal viable set: ~2–3 focused days

---

## Options Considered

### Option A — Recover arcs-app components, port to arcs-v9 as `src/ui/`
- Recover Badge/Button/Card from arcs-app git history (pre-stub-revert commit)
- Place in arcs-v9 at `src/ui/` with a `tokens.ts` file exporting color, font, radius, spacing constants
- Extend with Panel, Chip, Spinner as second batch
- Pros: recovers proven work; Register pattern is already solved; inline styles match constitutional contract
- Cons: tokens.ts has some duplication with globals.css @theme until a future ADR resolves single source

### Option B — Build fresh using shadcn/Tailwind `className` pattern
- Use shadcn CLI; apply Tailwind utility classes
- Pros: less hand-rolling; shadcn ecosystem
- Cons: violates constitutional inline-styles rule; shadcn stubs already proven inadequate in arcs-app

### Option C — No shared library; continue per-page ad-hoc inline styles
- Zero migration cost
- Cons: Register pattern never enforced; design drift guaranteed; every new screen re-solves same decisions

---

## Decision

**Chosen:** Option A

**Rationale:** arcs-app already solved this problem — the Register pattern maps directly to ARCS's three
UX contexts. Recovering from git history costs hours vs. rebuilding from scratch. Inline styles are the
established constitutional contract. `tokens.ts` bridges the @theme CSS vars to component-level style
objects without violating the no-className rule.

**Trade-offs accepted:** tokens.ts will have some duplication with globals.css @theme until a future
single-source-of-truth ADR. Accepted at QUARTER horizon — duplication is visible and localized.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Inline styles don't compose well at scale — 500-line style objects accumulate fast.
A typed variant system (cva/class-variance-authority) with Tailwind would be more maintainable if
arcs-v9 grows to 20+ screens. This is a real tension. But the constitutional rule is locked, the
current screen count is small, and the horizon is QUARTER — revisit trigger is explicit above.

---

## Consequences

- New `src/ui/` directory in arcs-v9 with Badge (first), then Button, Card, Panel, Chip, Spinner
- `src/ui/tokens.ts` as the single source for component-level style constants
- Existing pages optionally adopt components — no forced migration in this sprint
- LOE to unblock: ~2–3 days (recover 6 components, author tokens.ts, smoke-test on 1 page)

**Implementation pointer:** Recover from arcs-app git log — find pre-stub-revert commit for Badge.
Start there: Badge is the canonical Register-pattern example.

**Failure path:** If the arcs-app pre-stub-revert commit is unreachable (squashed, force-pushed, or
history pruned), reconstruct Badge/Button/Card from first principles using WORLD.md token spec
(render scale table + Y-gate color system) as the source of truth for Register variants.
