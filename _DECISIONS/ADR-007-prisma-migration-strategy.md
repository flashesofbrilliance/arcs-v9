# ADR-007 — Prisma Migration Strategy: db push vs migrate deploy

> **Status:** DECIDED — BOOTSTRAP COMPLETE (see Amendment below)
> **Date:** 2026-05-27  
> **Amended:** 2026-05-28
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Which Prisma migration strategy should arcs-v9 use for the Supabase production database — `db push` (stateless), `migrate deploy` (tracked), or MCP-direct SQL — and when does each apply?

---

## E — Entity / System

- `prisma/schema.prisma` — DDL source of truth
- Supabase ARCS database (`owdiiyvphyifukygvxhg`)
- Vercel build step (`vercel.json` or `package.json` build command)
- `prisma/migrations/0_init/migration.sql` — baseline migration, committed 2026-05-28

---

## W — Window

**Horizon:** QUARTER  
**Revisit trigger:** First post-launch schema change (any ALTER TABLE or new model after a real user exists in production). At that point `migrate deploy` becomes mandatory.

---

## Context

The Supabase database contains stale tables from older ARCS versions but zero rows in all tables. The v9 Prisma schema has never been pushed to production. Three migration tools are available: `prisma db push` (fast, no migration files, no history), `prisma migrate deploy` (tracked, CI/CD-safe, requires migration history), and Supabase MCP `apply_migration` (emergency DDL bypass). Prisma docs explicitly warn against mixing `db push` and `migrate deploy` — once you choose one path, you must continue it, or baseline the migration history.

*Research summary:* Prisma recommends `db push` for early prototyping and `migrate deploy` for production CI/CD. The transition requires generating a baseline migration with `prisma migrate diff` before the first tracked change.

---

## Options Considered

### Option A — prisma db push (now, then baseline before first post-launch change)
- Fastest path to unblock P4 deploy
- No migration history created; schema applied as current state
- Must be followed by baselining before any post-launch schema change

### Option B — prisma migrate deploy (immediately, generate baseline first)
- Migration history from day one
- Requires `prisma migrate dev` locally first to generate `0_init.sql`
- Adds ~30 min overhead before first deploy; no meaningful benefit while zero users

### Option C — Supabase MCP apply_migration (bypass Prisma entirely)
- Direct DDL via MCP; useful for emergency fixes or initial bootstrap
- No Prisma migration tracking; creates permanent divergence if used for schema management

---

## Decision

**Chosen:** Option A now; Option B from first post-launch schema change forward.

**Rationale:** Zero users, zero migration history, stale tables that need replacing. `db push` is the right bootstrapping tool. The transition to `migrate deploy` requires one baselining step — run `prisma migrate diff` after the `db push` bootstrap to generate `migrations/0_init.sql`, establishing a clean history baseline before any real user touches the schema.

Option C reserved for emergency hotfixes only (production data corruption, out-of-band DDL needed before a deploy can run).

**Trade-offs accepted:** `db push` creates no migration history. If we forget to baseline before the first post-launch schema change, we must run `prisma migrate resolve --applied` to mark the drift as resolved — a recoverable but annoying situation.

---

## Y — Conviction

**Polarity:** GREEN  
**Conviction:** HIGH  
**Stability:** STABLE

**Loki test:** `db push` completes successfully but produces a schema that diverges from what `migrate deploy` would generate (e.g., different constraint names, index ordering). When we later run `prisma migrate dev` to generate the baseline, the diff is noisy and hard to reason about. Mitigation: immediately after `db push`, run:
```bash
npx prisma migrate diff \
  --from-schema-datasource prisma/schema.prisma \
  --to-schema-datamodel prisma/schema.prisma \
  --script > prisma/migrations/0_init.sql
```
This generates the baseline migration file. Mark it applied: `npx prisma migrate resolve --applied 0_init`. Now `migrate deploy` has clean history from bootstrap.

---

## Consequences

**Step 1 (DONE — 2026-05-28):** Schema bootstrapped. Actual path deviated from Option A:
- `prisma db push` failed — direct Supabase connection auth failing from local machine (ENOTFOUND on pooler; P1000 on direct host). Root cause unresolved.
- Fallback: schema applied via **Supabase MCP `apply_migration`** (Option C was used for bootstrap, not ongoing management).
- All stale tables dropped (all empty). All 9 v9 DEWY schema tables created clean.
- `prisma/migrations/0_init/migration.sql` generated via `prisma migrate diff --from-empty --to-schema` and committed.
- `_prisma_migrations` table created; `0_init` registered as applied via Supabase MCP `execute_sql`.

**Step 2 (DONE — 2026-05-28):** Baseline complete. `migrate deploy` will not re-run `0_init`.

**Step 3 (before first post-launch schema change):** Switch Vercel build command to:
```
prisma migrate deploy && next build
```
Gate: this switch is **required before merging any PR that contains a schema change after a real user has created a receipt in production**.

Option C (MCP apply_migration) usage rule: only for production emergencies where a schema fix is needed faster than a deploy cycle. Always follow with a matching Prisma migration file committed to the repo.

**Implementation pointer:** `package.json` build script + `vercel.json` buildCommand

---

## Linked receipts / ADRs

- ADR-005 — Vercel Supabase env injection (prerequisite; DATABASE_URL must exist)
- ADR-006 — Supabase Branching (changes how migrate deploy runs per branch)
- ADR-002 — Database split (this ADR implements the prod migration path from ADR-002)
