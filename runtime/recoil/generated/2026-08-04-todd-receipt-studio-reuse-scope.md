# PRL — Signed Phase Receipt (reuse the louisville Receipt Studio)
_2026-08-04 · scope for applying the existing interactive receipt system to the PRL engagement._

## What already exists (reuse target)
The louisville.arcs.care Receipt Studio is a **persisted, signable receipt system**, not a mockup:
- **Model:** `SessionReceipt` (prisma/schema.prisma) — author, bet, assumptions, falsifier (required),
  killScale, atRisk, **scoreBackDate** (required, future), status (OPEN→SCORED/KILLED/SCALED), outcome,
  variance, lesson, **parentId/seedsSessionId** (lineage → each receipt seeds the next), sealedAt.
- **API:** `src/app/api/louisville/receipts/route.ts` — POST create + GET session-scoped, zod-validated,
  body/row caps, IP throttle, field allowlist.
- **DB:** `src/lib/db-louisville.ts` — least-privilege `louisville_app` role, RLS-pinned to
  jeben/louisvillebrands, fail-closed.
- **UI:** the Receipt Studio in `public/louisville.html`.

## Why it fits (near 1:1 with the receipt-calibrated pricing)
This IS the recoil ex-ante/ex-post receipt + the receipt-calibrated pricing loop, already built:
sign the expected (bet + falsifier + assumptions + atRisk), revisit on scoreBackDate, bank the field
truth (outcome + variance + lesson), and seed the next receipt (parentId/seedsSessionId = "iterative
logic carries"). Both parties as `author` = the co-sign.

## PRL-1.2 receipt (field mapping)
- author: **TODD + ZACH** (both seal).
- bet: "Phase 1.2 delivers [delivery + enrichment + 4-hr metric + baseline] at $4,500, base ~20h, Monday kickoff."
- assumptions: CRM stamps first-touch · baseline pulls clean · ZoomInfo/Mailgun access in hand.
- falsifier: "wrong if actual effort lands outside 12–30h, or the metric cannot be built from existing data."
- atRisk / killScale: the $4,500 cap · the sandbox/kill-switch triggers.
- scoreBackDate: the **1.2 wrap date** (~2 weeks out) — the revisit reminder.
- at wrap: status OPEN→SCORED · outcome + variance (expected vs actual) + lesson (banked field truth).
- seedsSessionId: the 1.2 receipt seeds the **1.3 receipt** → calibrates the 1.3 price/scope.

## What reuse takes (honest scope)
1. **Parameterize tenant + authors** — API hardcodes TENANT=jeben, BRAND=louisvillebrands, authors
   JUSTIN|JEBEN|ZACH. Add tenant `prl`/`prlresins` + authors `TODD|ZACH`.
2. **DB role + RLS** — add a `prl_app` least-privilege role pinned to the PRL tenant (or generalize the
   policy). Touches the production DB → careful, migration + RLS test.
3. **UI port** — lift the Receipt Studio onto a PRL surface (`prl.arcs.care/receipt` route or a section).
   Note the todd-call routing-saga risk on that host; a section on an existing served page may be safer.
4. **Reminder gap** — `scoreBackDate` is STORED but nothing FIRES on it. A real 1.2-wrap reminder needs
   a cron/email wire-up (scheduled-tasks capability). Data model is ready; the trigger is not.

## Discipline
This is **Zach's engagement tooling**, not PRL-facing scope. It is genuinely valuable (it operationalizes
the receipt-calibrated pricing + banks field truth for the flight-ops loop), but it is a real build
touching prod DB/RLS. **Do not let it delay Send 1 / 1.1 go-live.** Recommend: scope it as its own small
piece, build after (or alongside, if bandwidth) the go-live push. It also generalizes: a parameterized
receipt tenant = a reusable engagement-flightops component (the signed receipt that feeds the pricing loop).
