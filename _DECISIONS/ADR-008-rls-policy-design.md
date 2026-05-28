---
id: ADR-008
title: RLS Policy Design — Deny-All for Non-Superuser Roles
status: ACCEPTED
date: 2026-05-27
deciders: [Zach Harris]
nci: 88
gate: GREEN
---

## Context

Supabase project `owdiiyvphyifukygvxhg` has 9 tables with Row Level Security disabled. Before first external user, policies must be in place so accidental anon-key exposure or future supabase-js usage doesn't expose raw data.

**Architectural constraint:** Auth.js v5 manages sessions in the database (not via Supabase Auth). Prisma connects as the `postgres` superuser role via `DATABASE_URL` (pooler, port 6543). Postgres superusers bypass RLS unconditionally. Therefore:

1. `auth.uid()` is always `NULL` for Prisma-originated queries — row-level user policies would silently return 0 rows.
2. App-level user scoping (ADR-001) is the correct isolation mechanism for Prisma queries.
3. RLS protects a different attack surface: anon-key access, PostgREST, or any non-superuser connection.

## Decision

Enable RLS on all 9 tables with explicit DENY ALL policies for `anon` and `authenticated` roles. No permissive policies are written. Prisma (superuser) is unaffected.

Tables: `User`, `Account`, `Session`, `VerificationToken`, `Receipt`, `Brief`, `PrepGuide`, `PrepSession`, `Outcome`.

**Applied via:** `scripts/rls-policies.sql` — paste into Supabase SQL Editor.

## Why not `auth.uid()` row policies?

Three options were considered:

| Option | Verdict |
|--------|---------|
| `auth.uid()` policies (standard Supabase RLS) | ❌ Requires Supabase Auth JWT. Auth.js v5 uses DB-backed sessions, not Supabase Auth — `auth.uid()` always NULL for Prisma queries. Would silently break all queries. |
| Custom JWT passing (`SET LOCAL request.jwt.claims`) per Prisma connection | ❌ Requires middleware wrapper around every Prisma call, significant complexity, no clear benefit given ADR-001 already enforces user scoping at route layer. |
| Deny-all for non-superuser roles (this ADR) | ✅ Correct scope for the attack surface. Prisma unaffected. Clean. |

## Future path to row-level user policies

If Supabase Auth is adopted (replacing Auth.js v5), migrate to:
```sql
CREATE POLICY "users_own_receipts"
  ON "Receipt" FOR ALL TO authenticated
  USING (auth.uid()::text = "userId");
```
This ADR should be superseded at that point.

## Consequences

- RLS enabled on all 9 tables — anon access denied by default
- Prisma queries are unaffected (superuser bypass)
- No `auth.uid()` policies; user isolation remains at app layer (ADR-001)
- Direct Supabase dashboard SQL (as postgres) still works
- supabase-js anon client gets 0 rows on all tables
