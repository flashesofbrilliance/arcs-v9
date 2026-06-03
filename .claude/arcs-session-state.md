# ARCS Session State

**Last updated:** 2026-06-03 (v2.3.0)
**Last commit (arcs-v9):** 84d7537 — fix(sync): handoff-pickup fetches arcs-v9 snapshot via GitHub
**Last commit (arcs-care):** 136add1 — perf(cron): batch T+7 emails (unchanged this session)

## Status

- arcs-v9 Vercel: ✅ LIVE — https://app.arcs.care (new permanent domain)
- arcs-v9 Auth: ✅ FULLY OPERATIONAL — magic link working end-to-end
- arcs-v9 DB: ✅ xbbpiryokswwvcrcutge / arcs_app role / 7 tables
- arcs-care: ✅ LIVE (unchanged this session)
  - Item 1 (case study): 🔒 Dark — pending NEXT_PUBLIC_CASE_STUDY_APPROVED
  - Item 2 (email capture): ✅ Live
  - Item 3 (spots badge): ✅ Live

## What landed this session (ADR-016 + infra)

- **ADR-016 Option C SEALED** — anonymous compass + magic link auth chain
  - 401 guards removed from compass + prep routes
  - `PATCH /api/receipts/claim` created (userId from auth() only)
  - localStorage session_id bridge for pre→post auth receipt migration
  - `scripts/smoke.sh` 5/5 passing
  - First authenticated user: zach.harris@gmail.com, 2026-06-03 16:57 UTC
- **PrismaPg SSL fix** — `new Pool({ ssl: { rejectUnauthorized: false } })`
  (entire DB layer was silently broken in prod since day 1)
- **emailVerified + image schema gap** patched live + ADR-022 written
- **app.arcs.care** domain wired (CNAME via Vercel DNS)
- **Vercel CLI** upgraded 53.1.0 → 54.7.1 (Homebrew)
- **State sync layer** — `_STATE/snapshot.json` + enhanced /handoff + /handoff-pickup
  Architect (cloud arcs-decision-receipts) fetches via GitHub raw URL
  Implementor (local arcs-v9) reads local file

## Requires human action (URGENT)

1. **⚠️ Rotate credentials exposed in session transcript:**
   - `***REDACTED-RESEND-KEY-ROTATED-2026-06-03***` — Resend API key → regenerate at resend.com/api-keys
   - `***REDACTED-DB-PASSWORD-ROTATED-2026-06-03***` — arcs_app DB password → reset at Supabase dashboard → update DATABASE_URL in Vercel
2. **Vercel Preview env** — add AUTH_SECRET + AUTH_RESEND_KEY to Preview environment
3. **arcs-care case study** — flip NEXT_PUBLIC_CASE_STUDY_APPROVED=true when Dan Pascone confirms

## Open sprint

No active sprint. Priority order:
1. Credential rotation (⚠️ do first)
2. Panel/Chip design system components (ADR-009)
3. ADR-006 branching strategy (first external user gate now triggered)
4. arcs-care /call route for Lab booking href

## Key infra facts (for next session)

- DB: `xbbpiryokswwvcrcutge` / `arcs_app` role / port 6543 pooler
- Supabase MCP: `.mcp.json` scoped to xbbpiryokswwvcrcutge (project-level, gitignored)
- Vercel project: `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9` / team `zachharris-3439s-projects`
- State snapshot: `_STATE/snapshot.json` in repo + GitHub raw URL for Architect surface

## Next session

/handoff-pickup → credential rotation → Panel/Chip OR ADR-006
