# Claude Code Pickup — ADR-002: Database Split + P4 Deploy

> **Status:** BLOCKED — needs `DATABASE_URL` + `DIRECT_URL` set on Vercel  
> **Generated from:** `_DECISIONS/ADR-002-database-split.md`  
> **Horizon:** QUARTER | **Conviction:** GREEN / HIGH / STABLE

---

## What was decided

SQLite for local dev (zero config), Supabase Postgres for prod. Prisma 7 resolves the driver from `prisma.config.ts`, not `schema.prisma`. The P1012 Prisma 7 breaking change has been fixed (commit `42852d4`).

## Blocker

Supabase credentials not yet set on Vercel. Until these are in place, the Next.js build will fail at the compile step (env validation in `src/lib/env.ts`).

## Unblock checklist

1. Supabase dashboard → Settings → Database → Connection Strings
   - **Pooler URL** (port 6543, Transaction mode) → set as `DATABASE_URL` on Vercel
   - **Direct URL** (port 5432) → set as `DIRECT_URL` on Vercel
2. Supabase dashboard → Settings → API
   - **service_role key** → set as `SUPABASE_SERVICE_ROLE_KEY` on Vercel
3. Vercel dashboard → arcs-v9 project → Environment Variables → add all three (Production + Preview)
4. Locally: `npx prisma db push` against Supabase to sync schema
5. `vercel deploy` or push to `main` to trigger redeploy

## Files to touch

```
prisma.config.ts         — already correct, no changes
prisma/schema.prisma     — already correct (P1012 fix applied)
src/lib/env.ts           — verify DATABASE_URL is in required vars list
```

## Done when

Deploy succeeds on Vercel, `prisma db push` confirms schema synced, `_QUEUE/PENDING.md` ADR-002 row updated to `DONE`.
