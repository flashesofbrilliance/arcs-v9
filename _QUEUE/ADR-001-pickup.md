# Claude Code Pickup — ADR-001: Auth Gate Strategy

> **Status:** READY  
> **Generated from:** `_DECISIONS/ADR-001-auth-gate-strategy.md`  
> **Horizon:** YEAR | **Conviction:** GREEN / HIGH / STABLE

---

## What was decided

App-level auth gating only. No Supabase RLS. Every API route must filter by `session.user.id` — there is no DB-layer backstop if a route forgets.

## Acceptance criteria

All `/api/` routes pass this audit:
- [ ] `GET /api/history` — returns only receipts where `userId = session.user.id`
- [ ] `GET /api/brief/[receiptId]` — receipt ownership verified before generation
- [ ] `GET /api/guide/[receiptId]` — same
- [ ] `POST /api/compass` — receipt created with `userId` set
- [ ] `POST /api/prep` — PrepSession created with correct association
- [ ] `PATCH /api/receipts/[id]` — (not yet built) will need ownership check

## Files to touch

```
src/app/api/history/route.ts
src/app/api/brief/[receiptId]/route.ts
src/app/api/guide/[receiptId]/route.ts
src/app/api/compass/route.ts
src/app/api/prep/route.ts
```

## Implementation note

Audit pattern: for each route, verify `where: { userId: session.user.id }` or equivalent guard exists. If a route is missing it, add it. Do not change behavior — just enforce the filter.

## Done when

`_QUEUE/PENDING.md` ADR-001 row updated to `DONE` + commit `audit(auth): userId filter audit complete [NCI:SECURITY]`
