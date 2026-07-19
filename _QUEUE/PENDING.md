# Implementation Queue

> Auto-maintained by `.github/workflows/adr-queue.yml`
> Read by `/arcs-handoff-pickup` at session start
> Status: READY | BLOCKED | IN_PROGRESS | DONE

| ADR | Title | Pointer | Status | Horizon | Conviction |
|-----|-------|---------|--------|---------|------------|
| 001 | Auth gate: app-level (not RLS) | `src/app/api/` — audit userId filter on all routes | DONE — `25e76e8` | YEAR | HIGH |
| 002 | DB: SQLite dev / Supabase prod | `prisma/schema.prisma` + Vercel env (DATABASE_URL) | DONE — closed, P4 trigger fired | QUARTER | HIGH |
| 003 | arcs.care: COCD as first-class UX primitive | `~/arcs-care-local/components/hero.tsx` + `loop-diagram.tsx` | DONE — shipped (arcs-care `0240f18`) | QUARTER | HIGH |
| 004 | mcp.arcs.care DNS fix | Vercel dashboard → perplexity-mcp → add domain `mcp.arcs.care` | DONE — live, 308 redirect confirmed | TODAY | HIGH |
| 005 | Vercel Supabase env injection | Vercel → Integrations → Supabase | DONE — execution diverged (manual `vercel env add`, not integration); rotation risk tracked in ADR-005 amendment | TODAY | HIGH |
| 006 | Supabase Branching for preview DBs | Gate: first external user OR first schema PR | READY — gate condition ("first schema PR") has fired multiple times since (e.g. ADR-026's migration); branching itself not yet set up | QUARTER | MEDIUM |
| 007 | Prisma migration strategy | `npx prisma db push` → baseline → switch build cmd | DONE — bootstrap complete (amended 2026-05-28) | QUARTER | HIGH |
| 008 | RLS policy design | `scripts/rls-policies.sql` | DONE — deny-all policies applied to 9 tables (note: `SageTrace` added later, RLS currently disabled on it per live advisory — needs a follow-up policy) | YEAR | HIGH |
| 009 | Design system canonicalization | `src/ui/tokens.ts`, `Badge.tsx`, `Button.tsx`, `Card.tsx` | IN_PROGRESS — Tokens/Badge/Button/Card shipped; Panel + Chip not started | QUARTER | MEDIUM (revisit, not STABLE) |
| 010 | `arcs_dewy` naming collision fix | Python package vs. flat-file shadowing | DONE | QUARTER | HIGH |
| 011 | UI import strategy (no barrel) | `@/ui/Badge` not `@/ui` | DONE — convention in force; revisit trigger is ≥8 components (currently 4) | QUARTER | MEDIUM |
| 012 | arcs-care PLG Phase 1 (model swap + Lab card) | `app/api/compass/route.ts`, `app/compass/page.tsx` (arcs-care) | DONE — `a54e5dd` | QUARTER | MEDIUM |
| 013 | arcs.care conversion architecture (Kintsugi sequence) | case study + email capture + spots badge | DONE — all 3 Week 1 items shipped (`8746ece`, `a5dcffc`/`3ffe6b1`); case study dark behind `NEXT_PUBLIC_CASE_STUDY_APPROVED` pending Dan Pascone confirmation | QUARTER | MEDIUM |
| 014 | arcs-care CI/CD governance (NOTOMATION circuit breakers) | `.github/workflows/*.yml`, `scripts/smoke.sh` | DONE | YEAR | HIGH |
| 015 | Case study content gate | gates ADR-013 item 1 | BLOCKED — waiting on Dan Pascone confirmation (human action, not a build task) | QUARTER | MEDIUM |
| 016 | arcs-v9 auth model (anonymous compass) | `src/app/api/compass/route.ts` | DONE — fully sealed | YEAR | HIGH |
| 017 | Receipt core schema (canonical field set) | `prisma/schema.prisma`, Supabase direct (arcs.care) | DECIDED | QUARTER | HIGH |
| 018 | `/helpful` raw-context input model | arcs-care `/helpful` | DRAFT — HELD pending Architect packet from Perplexity Space session | QUARTER | — |
| 019 | `ReceiptObject` as canonical Python runtime type | `operators/arcs_receipt_core.py` | DECIDED | QUARTER | HIGH |
| 020 | Tribune Intelligence Layer (Anterior/Proactive/Posterior) | wraps existing Receipt flow, no ReceiptObject mutation | **READY — decided, 50-receipt trigger cleared (184 receipts live), not yet started** | QUARTER | — |
| 022 | `User.emailVerified`/`image` Postgres column debt | migration needed (SQLite-only `d732dad` never ported) | DONE — confirmed live via Supabase MCP `list_tables`: both columns exist on `public.User` | QUARTER | — |
| 023 | Observability as superionic goal lattice | `runtime/specs/lattice-pressure-rom.json`, `scripts/lattice_sim.py` | GATED — blocked until 100+ receipts give a measurable real-corpus Zipf baseline (184 receipts exist; gate is on baseline measurement, not just count — not yet run) | QUARTER | HIGH |
| 024 | Resume / arcs-care architecture gates | — | DECIDED | — | — |
| 025a | ARCS go-live: provisional public launch logic | `app.arcs.care` anonymous compass + public brief | DRAFT — PROVISIONAL, 30-day signal review window (launched 2026-06-12, review ~2026-07-12) | WEEK | — |
| 025b | SAGE signal validation path | `operators/arcs_api.py`, `scripts/sage_efficacy.js` | DECIDED — gated on Outcome data reaching MIN_SAMPLE=20/cohort; unblocked by ADR-026 | QUARTER | — |
| 026 | Debrief delivery fix (eligibility + long-horizon cron) | `src/app/api/compass/route.ts`, `src/app/api/cron/debrief/route.ts` | DONE — steps 1–2 merged `a2bc4e4`; step 3 (verify Outcome accumulation) and step 4 (in-app `/history` fallback) still open | QUARTER | HIGH |

**Known queue issues (not yet fixed, flagging rather than silently resolving):**
- Two ADRs are both filed as "025" (`ADR-025-arcs-go-live-provisional-logic.md` and `ADR-025-sage-signal-validation-path.md`) — disambiguated above as 025a/025b. Renumbering one would require updating cross-references; not done here.
- No `ADR-021` exists — numbering gap, unexplained. Not necessarily a problem, just noting it for whoever investigates next.
- **Verify (surfaced 2026-07-19 from archive scan):** the NCI<40 / UNDEFINED-W-field **HOLD gate** (original Issue #4 "Compass → DEWY flow" scope) is not visibly branched in `src/app/api/compass/route.ts` — the prompt names the 40–60 uncertainty band but there's no explicit HOLD/REJECT branch. May be intentionally deferred under the anonymous-first model (ADR-016) or handled downstream in `ygate.ts`. Confirm whether still wanted before treating as debt; not a prod blocker (app is live at 184 receipts without it).

---

## Non-ADR backlog (real gaps, no ADR filed yet)

These don't have a number in the table above because no ADR exists for them — confirmed against the actual codebase (`AGENTS.md`'s backlog table is stale on the first item below):

- **Receipt save prompt (soft-auth nudge UI)** — `AGENTS.md` lists this as P1; confirmed via grep, genuinely not built (no `ReceiptSavePrompt` component anywhere in `src/`). Biggest open PLG gap, no dependency, no gate. *(Note: `AGENTS.md` also lists "Outcome handler — PATCH /api/receipts/[id]" as P1/not-built — that one is wrong, it's built and live at `src/app/api/receipts/[receiptId]/outcome/route.ts`.)*
- **Calibrate-surface malformed-question HOLD gate** (Book II Part V §5.7) — the compass route has an inline L0 activation-filter heuristic, but no dedicated reject/HOLD path for the Calibrate surface as the canon specifies. This is a doctrine gap, not just a missing feature: running L0–L5 on a malformed question without holding it first can produce a confident-looking output on a broken input.

---

## Open backlog from the token-efficiency audit session (2026-07-19)

> Branch `claude/token-efficiency-audit-ip3l3x` (not yet merged). Full detail in the `_PATTERNS/2026-07-19-*`
> docs. The in-repo fixes are done + pushed; what remains is out-of-band (other environments) or follow-on.

**Out-of-band — need an environment this cloud session can't reach** (see `_PATTERNS/2026-07-19-out-of-band-actions.md`):
- 🔴 **Sentinel rebuild (fix #3) + security guardrail** — recreate from the `arcs-decision-receipts` env
  (ownership rule): zero MCP connectors, Haiku model, push on. **AND make it report-only** — drop `Write`/
  `Edit`, never let it `Edit` `CLAUDE.md`; see the lethal-trifecta write-up in
  `_PATTERNS/2026-07-19-threat-assessment.md` §HIGH.
- 🔴 **`SageTrace` RLS** — enable + deny-all policy via the Supabase **CLI** (project invisible to the MCP,
  wrong org).
- 🟡 Connector hygiene (claude.ai settings), Vercel preview `DATABASE_URL`, `DATABASE_URL` rotation reminder,
  Resend MCP key rotation, DMARC `p=reject` — all itemized in the out-of-band checklist.
- 🟡 **Dan Pascone case-study gate** (ADR-015) — human decision, still open.

**In-repo follow-ups (started this session, safe to continue):**
- **B2 depth:** source the `nci_by_lens.cadence` lens from `time-quality-attribution-rom.json` (currently
  Claude-estimated), and decide the **HOLD gate at NCI < 40** — which overlaps the existing "Calibrate-surface
  malformed-question HOLD gate" item above. See `_PATTERNS/2026-07-19-tech-debt-batch.md` B2.
- **Merge** `claude/token-efficiency-audit-ip3l3x` → main (closes the cloud-snapshot staleness the lean
  CLAUDE.md/MEMORY.md changes depend on).

---

*Last updated: 2026-07-19 (token-efficiency audit session); prior auto-gen 2026-07-01 22:41 UTC*
