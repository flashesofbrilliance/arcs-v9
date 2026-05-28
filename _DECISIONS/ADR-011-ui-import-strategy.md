# ADR-011 — UI Component Import Strategy: Direct vs. Barrel

> **Status:** DECIDED
> **Date:** 2026-05-27
> **Commit:** (set at merge)

---

## D — The Decision

Should arcs-v9's src/ui/ component library use a barrel file (index.ts) for
re-exporting all components, or should consumers import from individual component
files directly?

---

## E — Entity / System

- `src/ui/` — all current and future component files (Badge, Button, Card, Panel, Chip, Spinner)
- All arcs-v9 app pages that import UI components
- `next.config.js` — would require `optimizePackageImports` if barrel is added
- Next.js/Turbopack build pipeline — directly affected by re-export resolution cost

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** Component count reaches 8+, OR a page import block exceeds
5 individual @/ui/* lines, OR Turbopack adds native barrel tree-shaking support.

---

## Context

At 4 components (Badge, Button, Card, tokens), a barrel file offers no meaningful
ergonomic advantage — `@/ui/Badge` is already a single import. The ergonomic
case for barrels ("one import instead of many") only becomes real at 8+ components.

Research confirms: barrel files in Next.js src/ code break tree-shaking.
`optimizePackageImports` in next.config.js mitigates this for packages but not
local paths. Turbopack's tree-shaking behavior with local barrels is not yet
guaranteed. The cost of adding a barrel now is real (build risk); the benefit is
zero (import ergonomics unchanged at current scale).

*Research summary:*
- Barrel imports force bundler to crawl all re-exported modules — documented Next.js issue
- `optimizePackageImports` does not apply to local `src/` paths
- Anti-barrel guidance from Vite, webpack, and library authors is consistent
- Revisit threshold is ~8 components OR a next.config.js-level mitigation is confirmed

---

## Options Considered

### Option A — No barrel; direct imports only (status quo)
- Each consumer imports from `@/ui/Badge`, `@/ui/Button`, etc. directly
- Pros: zero tree-shaking risk; zero build overhead; already works; ADR-009 compliant
- Cons: import lines grow linearly with component count; no single-line convenience

### Option B — Add index.ts barrel now
- Single `src/ui/index.ts` re-exports all components
- Pros: cleaner import sites once count grows
- Cons: breaks tree-shaking without next.config.js mitigation; adds build risk for
  zero ergonomic benefit at current scale (4 components)

### Option C — Add barrel + optimizePackageImports when count reaches threshold
- Defer barrel until 8+ components; add alongside next.config.js optimization config
- Pros: gets ergonomic benefit when it matters; mitigates tree-shaking risk
- Cons: requires remembering to add next.config.js change alongside the barrel

---

## Decision

**Chosen:** Option A — no barrel, direct imports only.

**Rationale:** Four components. Zero ergonomic problem. Real tree-shaking risk.
The case for a barrel does not exist yet. Direct imports (`@/ui/Badge`) are already
idiomatic and readable. Revisit trigger in W is explicit — when we hit it, switch to
Option C (barrel + config mitigation together as one PR).

**Trade-offs accepted:** Import lines will grow linearly. This is visible and
localized — not a hidden cost.

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** REVISIT

**Loki test:** Turbopack in Next.js 16 may already handle barrel tree-shaking
natively, making the tree-shaking risk moot. If Turbopack handles it, we're
paying a small ergonomic cost (multiple import lines) for zero safety benefit.
Worth checking release notes before the revisit trigger fires.

---

## Consequences

- No `src/ui/index.ts` created; direct imports remain the convention
- When adding a new component, import from its own file: `@/ui/ComponentName`
- Revisit when count hits 8: add barrel + `optimizePackageImports` in one PR
- If Turbopack confirms native barrel tree-shaking: Option B becomes safe, revisit earlier

**Implementation pointer:** No code change required. This ADR locks the convention.
