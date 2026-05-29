# ARCS Session State

**Last updated:** 2026-05-29 (v2.1.0)
**Last commit (arcs-v9):** d3f7272 — handoff v1.9.0
**Last commit (arcs-care):** 136add1 — perf(cron): batch T+7 emails

## Status

- arcs-v9 Vercel: ✅ LIVE
- arcs-care: ✅ LIVE
  - Week 1 conversion builds: ✅ ALL SHIPPED
    - Item 1 (case study): ✅ Built · 🔒 Dark — pending NEXT_PUBLIC_CASE_STUDY_APPROVED
    - Item 2 (email capture): ✅ Live
    - Item 3 (spots badge): ✅ Live
  - Email auth: ✅ DKIM + SPF + DMARC p=quarantine all verified
  - compass_receipt_id: ✅ In Supabase waitlist table
  - Supabase MCP: ✅ Wired (xbbpiryokswwvcrcutge)
  - T+7 cron: ✅ resend.batch.send()

## Requires human action

1. Dan Pascone approval → set NEXT_PUBLIC_CASE_STUDY_APPROVED=true in Vercel Production → close issue #7
2. DMARC tighten: p=quarantine → p=reject once delivery confirmed
3. Preview DATABASE_URL (arcs-v9) — add via Vercel dashboard
4. Define "Lab inquiry" for ADR-013 30-day signal
5. 30-day calendar reminder from case study ship date

## Next session

/arcs-handoff-pickup → flip case study env var → arcs-v9 Panel/Chip components → ADR-006
