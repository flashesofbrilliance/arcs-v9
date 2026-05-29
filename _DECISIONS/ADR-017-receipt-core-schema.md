# ADR-017 — receipt-core Canonical Schema

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** (set at merge)

## D — The Decision

**Sharp question:** What is the canonical field set for a compass receipt, and where does it
live so that arcs.care (Supabase direct) and arcs-v9 (Prisma) cannot drift from it?

## E — Entity / System

- `runtime/specs/dewy-receipt-schema-v1.json` — existing JSON Schema (Kairos Locked) in arcs-v9; enforcement document for canonical field naming
- `prisma/schema.prisma` — `Receipt` model (arcs-v9); superset of receipt-core
- Supabase `compass_receipts` table — does NOT yet exist (needed for Phase 2 arcs.care)
- `app/api/compass/route.ts` in arcs-care — currently returns 9 fields; not persisted
- `.github/workflows/ci.yml` (arcs-care) — CI enforcement point; schema validation step to be added before any receipt-touching deploy

## W — Window

**Horizon:** PERMANENT — this schema is a write-lock surface (irreversible downstream contracts)
**Revisit trigger:** L6/L7 engine requires new fields not in v1 schema. At that point, create
`dewy-receipt-schema-v2.json` (never mutate v1 in place).

## Context

The dependency map surfaced a critical ordering error: receipt-core was listed as a Phase 3
dependency, but it is a Phase 2 prerequisite. If `compass_receipts` is built on arcs.care
without locking the canonical field set first, two schemas diverge and a painful migration follows.

**Current schema state:**
- `dewy-receipt-schema-v1.json` exists and is Kairos Locked (arcs-v9)
- arcs.care compass API returns: `true_north`, `why`, `nci`, `mode`, `tributaries`, `risk_reading`,
  `timing_reading`, `somatic_reading`, `drift_reading` (9 fields, not persisted)
- arcs-v9 Prisma `Receipt` model has: DEWY fields + Y-gate + kinematic + lineage (~25 fields)

**The gap:** arcs.care returns 9 fields; arcs-v9 stores ~25. These are not the same schema.
receipt-core must define the minimum canonical set that both surfaces agree on, before any
Supabase table is created.

## Options Considered

### Option A — arcs.care adopts arcs-v9's full Prisma schema
- Supabase table mirrors every field in `prisma/schema.prisma`
- Pros: Single source of truth. Full DEWY decomposition in both places.
- Cons: arcs.care compass generates 9 fields; 16 fields would be NULL or default.
  Prisma schema has Auth.js relations (User, Session) that arcs.care doesn't need.
  Over-engineering for a funnel surface.

### Option B — Define a `receipt-core` minimum field set (chosen direction)
- Lock the minimum canonical fields both surfaces MUST have
- arcs-v9 Prisma schema is a superset (adds DEWY decomposition, Y-gate, lineage, Auth.js)
- arcs.care Supabase table is the minimum set + `source: 'arcs-care'` discriminator
- Both surfaces write to Supabase; arcs-v9 also writes through Prisma
- Pros: Each surface owns its superset. Core fields are shared and schema-validated.
- Cons: Two write paths. Schema sync requires discipline.

### Option C — arcs-v9 writes to Supabase directly (no Prisma for receipt storage)
- Drop Prisma for receipts; use Supabase client everywhere
- Pros: Single storage layer. arcs.care and arcs-v9 share the same table.
- Cons: Loses Prisma type safety. Major architectural change. ADR-007 + ADR-008 assumption violated.
  Do not choose this.

## Decision

**Chosen:** Option B — define a `receipt-core` minimum field set; arcs-v9 Prisma schema and arcs.care Supabase table are both supersets.

**Minimum receipt-core fields (candidate):**

```typescript
interface ReceiptCore {
  id: string                    // uuid
  created_at: string            // ISO 8601
  source: 'arcs-care' | 'arcs-v9'
  question: string              // raw input question (D field)
  true_north: string            // L5 compass bearing
  nci: number                   // 0-100
  mode: 'QUICKMOVE' | 'PLAN' | 'COURT'
  y_polarity: string            // GREEN | YELLOW | SCRATCH | PARADOX | RED | LOCKED
  user_id: string | null        // null = anonymous
  session_id: string            // anonymous session identifier
}
```

**arcs.care superset adds:** `risk_reading`, `timing_reading`, `somatic_reading`, `drift_reading`
**arcs-v9 superset adds:** full DEWY decomposition, `tributaries`, Y-gate kinematic fields, lineage

**Trade-offs accepted:** Two write paths (Prisma + Supabase direct) must stay in sync. Enforcement mechanism: `runtime/specs/dewy-receipt-schema-v1.json` is the source of truth; CI validation step in `.github/workflows/ci.yml` (arcs-care) validates any receipt-touching deploy against it. Any field present on both surfaces must use canonical naming from the JSON Schema — no silent aliasing.

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** "Option B means two schemas that can drift despite the 'canonical' core, because
there's no enforcement mechanism preventing arcs.care from adding a field that arcs-v9 also
adds with a different name." Counter: lock the core in `runtime/specs/dewy-receipt-schema-v1.json`
and add a CI check that validates both surfaces against it. Any field in both must use canonical naming.

## Consequences

- This ADR must be DECIDED before any Supabase migration for `compass_receipts` is written
- Once decided: Supabase migration for `compass_receipts` is an Implementer task (ADR-018)
- `runtime/specs/dewy-receipt-schema-v1.json` is the enforcement document — run a validation
  step against it in CI before any receipt-touching deploy

**Implementation pointer:** `runtime/specs/dewy-receipt-schema-v1.json` (already exists),
`supabase/migrations/YYYYMMDD_compass_receipts.sql` (to write after this ADR locks)
