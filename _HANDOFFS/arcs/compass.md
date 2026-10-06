# Arc: compass (reconstructed 2026-10-06)

> The compass began (v0.3 to v1.9, May to June) as a 5-lens Claude call on the old arcs-care site with a Lab offer
> card, moved into arcs-v9 as the L0-L5 pipeline that writes a DEWY receipt plus a Y gate, and spent July to
> September adding lens scoring, anonymous share, Tribune and the outcome loop. On 2026-09-24 a validation question
> found a six-week silent prod P0 (schema drift broke signed-in create and every brief read). From 2026-10-04 the
> arc turned to privacy and cost: anonymous-row leaks, owner-only briefs with hashed share tokens, an IDOR series
> on parent/prep/session ids, calm model-error codes, receipts that no longer spend tokens to view, and a shared
> "Ahmed order" layout for receipt and brief. The keel gap that never moved: almost nobody closes an outcome.

## Goal
A person stuck at a decision asks one question and gets a bearing (True North, reasons, open questions, Y gate)
saved as a receipt they own, can share deliberately, and later close with an outcome, at earned fidelity, with
no data visible to anyone but the owner and no model spend that the user did not ask for.

## What changed
- v0.3 to v1.9 (May to June): compass to DEWY flow spec (`runtime/flows/question-compass-to-dewy.md`); arcs-care
  P5 Phase 1 shipped the 5-lens compass and the conviction-gated Lab card (ADR-012). That site is now dormant.
- v3.8 to v3.11 (July): 5-lens `nci_by_lens`/`nci_grade`, output sanitizer, anon-share; "Sign in to keep"
  persist fix PR #121; the live auth loop was later proven.
- v3.54 (2026-09-06): ADR-020 Tribune, `POST/GET /api/tribune`, owner-only panel on `/receipt/[id]`.
- v3.65 (2026-09-24): SAGE pre-screen re-activated (#487, #488); prod P0 schema drift found and fixed.
- v3.68.1 (2026-09-27): #586 `scripts/outcome_funnel.py` (external: 10 receipts, 0 closed) and `/fears` cards that
  open into the dashboard with `?q=&horizon=`.
- v3.79.1 (2026-10-04): field landing (`Landing.tsx`, `Scope.tsx`); privacy hotfix #737 (`?? null` userId matched
  every anonymous row).
- v3.87 (2026-10-05): #808 owner-only briefs, `BriefShare` revocable SHA-256 tokens in the URL fragment.
- v3.89: preview magic-link fixed (cause: `ADMIN_EMAILS` Production-only); `/api/auth/session` stops returning the
  session token and full User row; `scripts/null_userid_gate.py` on pre-commit.
- v3.92 to v3.95: showcase-review privacy bugs closed; #848 `metadataBase` so OG images resolve.
- v3.94: IDOR series. #813 parent lookup scoped to caller, #836 `src/lib/session-owner.ts`, #847 anonymous
  claim route retired (48 legacy unowned rows stay unowned).
- v3.98: prod `_prisma_migrations` matches all 22 local migrations by sha256.
- v3.101 to v3.102 (2026-10-06): #888 receipt views read with `?generate=0`, no model call; #885/#890 receipt and
  brief share `src/organisms/AhmedOrder.tsx` and `src/lib/vocabulary.ts`.
- Model errors: #878-era `f4a3c1be` calm codes, provider bodies server-side; #901 skip recovery poll on mapped
  errors; #910 one shared code list; #902 outage alert throttle; #928 no-poll unit test.
- #882 `src/lib/claude-models.ts` single model registry; `deep` role moved to Sonnet 5.5 after the COURT eval.
- #887 smoke test + UX audit (Y-gate verdict under True North, AA contrast, 16px inputs), repo ESLint 174 errors
  to 0; #918 True North is the page h1. Handoff v3.115.0 (`c0d8ac7b`) records it.
- Receipts: `2026-10-06--qualify-abb6aedb-pr936--ZH` and earlier rows in `decision_receipt` (Supabase).

## State
- origin/main at `89264922` (2026-10-06). All PRs named above are MERGED (checked with `gh pr view`).
- Outcome route `src/app/api/receipts/[receiptId]/outcome/route.ts` requires a session and owner match.
- `/api/account/reminders` verifies a signed link (`src/lib/reminderLink.ts`), not a bare uid.
- Models: `fast` Haiku 4.5 (QUICKMOVE/PLAN), `deep` Sonnet 5.5 (COURT, brief), `guide` still Opus 4.5,
  `max` Opus 4.7; `package.json` pins `@anthropic-ai/sdk ^0.128.0`.
- Outcome capture: about 2/247 closed overall, 0 external closed (last measured 2026-09-27, unverified now).
- Live `/brief/[id]` against the real API and the signed-in share-token round trip: not exercised (unverified).

## Decisions
- Briefs and receipts are owner-only; sharing is a revocable hashed token carried in the URL fragment, never path.
- A `null` session userId must 401 before any `where` (gate: `scripts/null_userid_gate.py`).
- Client-supplied ids (parent, prep, session) are never proof of possession; scope every lookup to the caller.
- Viewing never spends tokens; generation is an explicit user action.
- Model ids live only in `claude-models.ts` (`model_id_gate.py` blocks hardcoded ids).
- Provider error bodies stay server-side; the client sees calm codes from one shared list.
- The human supplies `matched`/`regretScore`; a receipt never closes itself.
- Local prod-server smoke needs `AUTH_TRUST_HOST=true` or `/api/auth/session` 500s.

## Open
1. Outcome-capture keel: re-run `python3 scripts/outcome_funnel.py --sql`; backlog `outcome-capture-rate-keel-gap`.
2. Exercise signed-in share flow (copy link, private window, revoke) and live `/brief/[id]`.
3. `guide` role still on Opus 4.5: decide whether to move it (and run the eval like COURT).
4. Compass answers for open questions (chip task_160443dd; proposal `d3217e4f`): status unverified.
5. Zach: provider abstraction (`compass-model-agnostic-provider-abstraction` in backlog).

## Next action
Run `python3 scripts/outcome_funnel.py --sql` against prod and record the closed-outcome count in the
`outcome-capture-rate-keel-gap` backlog row.

## Cold-start
- Files: `src/app/api/compass/route.ts`, `src/lib/ygate.ts`, `src/lib/session-owner.ts`,
  `src/organisms/AhmedOrder.tsx`, `src/lib/vocabulary.ts`, `src/lib/claude-models.ts`,
  `src/app/api/brief/[receiptId]/route.ts`, `scripts/outcome_funnel.py`, `scripts/null_userid_gate.py`.
- Commands: `npm run build`, `git log origin/main --oneline | grep -i compass`, `gh pr view <n>`.
- Backlog: `_QUEUE/induced-backlog.jsonl` (outcome-capture, compass-mobile-timeout, provider abstraction).
- Memory: `null-userid-matches-anonymous-rows`, `publish-review-is-an-audit-of-the-product`,
  `prod-schema-drift-migrate-deploy-not-db-push`, `client-fetch-failure-is-not-persistence-failure`.
