# ADR-029 — Onboarding profile upload (store-only, skippable)

**Status:** DECIDED (implementation), scoped per Zach's direct call
**Date:** 2026-06-25
**Author:** delegated subordinate (Claude Code)

## D — The Decision

Add a `/onboarding` step where a logged-in user can upload their LinkedIn profile PDF
and/or full data-export ZIP. Two scope questions were routed to Zach rather than guessed:

1. **Store-only vs. wired into a live generation pipeline** → **store-only**. Files land
   in Vercel Blob; `ProfileUpload` records the pointers. No parser/LLM pipeline runs on
   upload — that pipeline (LinkedIn input → populated `ProfileScanResponse`) is still
   unscoped per ADR-028.
2. **Required vs. skippable** → **skippable, nudge later**. The step never blocks reaching
   `/dashboard`; a user who skips (or hasn't been asked yet) sees a small dismissible
   banner there instead.

## E — Entity / System

- `prisma/schema.prisma` — new `ProfileUpload` model (`userId` unique, `pdfUrl`,
  `exportUrl`, `skipped`, `uploadedAt`), migration `20260625010000_add_profile_upload`,
  applied live via `supabase db query` (per the established CLI-not-MCP pattern for this
  project — MCP is wrong-org for `xbbpiryokswwvcrcutge`)
- `src/app/api/onboarding/upload/route.ts` — `GET` (status check), `POST` (upload via
  `@vercel/blob`'s `put()`), `PATCH` (skip)
- `src/app/onboarding/page.tsx` — the upload/skip UI
- `src/app/dashboard/page.tsx` — nudge banner, shown when `GET /api/onboarding/upload`
  returns `seen: false` (i.e. the user has neither uploaded nor explicitly skipped)
- New dependency: `@vercel/blob` — confirmed with Zach before adding (repo policy: no new
  deps without asking). Native Vercel integration, no separate provisioning needed.

## W — Window / Why now

Companion to ADR-028's deferred generation pipeline and this session's `/scan` staging
work — the upload step is the other missing half of "land the plane on the profile scan."
Scoping it store-only keeps it shippable now without waiting on the pipeline spec; scoping
it skippable keeps the <30s onboarding promise honest even for a user without files handy.

## Y — Y-gate

GREEN/HIGH/STABLE for the implementation as scoped — additive, no auth-flow changes (the
nudge lives dashboard-side, not in a NextAuth redirect callback, to avoid touching the
already-validated magic-link flow), build-verified clean, migration confirmed live.

## Consequences

- No automatic redirect to `/onboarding` after sign-in yet — a user only sees it via the
  dashboard nudge banner or a direct link. If a forced first-run redirect is wanted later,
  that's a NextAuth callback change, deliberately not bundled into this ADR.
- The uploaded files sit unused until the generation pipeline (ADR-028's deferred item) is
  built. Acceptable per the "store-only" scope call — better to capture the files now than
  to wait on the pipeline to ask for them twice.
