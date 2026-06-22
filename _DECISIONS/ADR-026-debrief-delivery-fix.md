# ADR-026 — Debrief Delivery Fix

> **Status:** DECIDED
> **Date:** 2026-06-22
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** What is the minimum set of delivery repairs needed to route real users to the already-built debrief UX, so that `Outcome` rows accumulate and `sage_efficacy.js` can eventually produce a result?

---

## E — Entity / System

- `src/app/debrief/[receiptId]/page.tsx` — fully built debrief form (matched/what/regretScore/learning); not the problem
- `src/app/api/cron/` — scheduled debrief email trigger; the primary delivery vector
- `Receipt` — 184 rows; only a subset currently eligible for debrief emails
- `PrepSession` — gating object; `outcomeHorizon` field controls `reminderDate`
- Resend — email delivery; 30-day scheduling ceiling
- `Outcome` — 1 row; the metric we are trying to move

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** `sage_efficacy.js` produces a result — both cohorts (sage_fired=true, sage_fired=false) each have ≥20 Outcome rows. At that point, re-open ADR-025 Option A (text-derived signal).

---

## Context

The debrief UX is fully built and correct: `src/app/debrief/[receiptId]/page.tsx` has a complete form (matched boolean, free-text what-happened, 1–5 regret scale, optional learning), a receipt recap card, and a working API route. It is not the bottleneck.

Three delivery bugs are preventing users from reaching it:

**Bug 1 — Prep-gated eligibility (highest impact)**
`reminderDate` on `Receipt` only sets from `parsed.reminder_iso`, which only exists when a `PrepSession` includes `outcomeHorizon`. Compass works without a PrepSession (`prepId` is optional). Result: receipts created without a PrepSession never get a `reminderDate` and are permanently ineligible for the debrief email. With 184 receipts across 2 users, it’s likely most receipts skip prep entirely.

**Bug 2 — Resend 30-day ceiling (silent failure)**
Resend’s scheduling API fails silently for any send date >30 days out. Commit `8ded67f` identified 14 of 74 eligible receipts with `reminderDate` >30 days. These emails were scheduled, appeared to succeed, and were never delivered. No long-horizon scheduler exists.

**Bug 3 — Timezone bug (partially fixed)**
Debrief emails fired at 5am ET (UTC offset error) until commit `8ded67f` this morning corrected the send time to 9am ET. Bug is fixed for future sends; emails sent before this fix were delivered at the wrong time.

**Secondary gap — No in-app fallback**
Debrief is purely email-triggered. A user who misses or ignores the email has no in-app path back to the debrief form unless they happen to find `/debrief/[receiptId]` directly. No surface in `/history` or elsewhere surfaces open (un-debriefed) receipts.

---

## Options Considered

### Option A — Fix Bug 1 only (eligibility extension)
- Set `reminderDate` on all receipts at creation time, defaulting to T+7 when no `outcomeHorizon` is provided
- Pros: Highest-impact single fix; routes all compass calls into the debrief pipeline
- Cons: Doesn’t fix Bug 2 (long-horizon receipts still fail silently) or the in-app gap

### Option B — Fix Bugs 1 + 2 (eligibility + long-horizon scheduler)
- Extend eligibility to all receipts (Option A) + build a fallback for `reminderDate` >30 days (e.g., Vercel cron that re-queues long-horizon sends as they enter the 30-day window)
- Pros: Closes both silent failure modes; correct for any user with a quarter+ horizon
- Cons: Vercel cron work adds build surface; may be over-engineered for current traffic (2 users)

### Option C — Fix Bugs 1 + 2 + add in-app fallback
- All of Option B + a “Open debriefs” surface in `/history` (receipts with no Outcome row)
- Pros: Non-email fallback; catches users who ignore email; most complete fix
- Cons: Highest build surface; in-app nudge UX needs design consideration

---

## Decision

**Chosen:** Option B (eligibility extension + long-horizon scheduler), with Option C in-app fallback as a follow-on once Option B is shipped and measured

**Rationale:** Bug 1 is the highest-impact fix — extending eligibility to all receipts is a small schema/logic change that routes the full receipt population into the debrief pipeline. Bug 2 is a silent failure that will compound as more long-horizon receipts accumulate; fixing it while the fix is scoped is lower cost than triaging it later. The in-app fallback (Option C) is real value but not the binding constraint right now — ship it as a follow-on after delivery is confirmed working.

**Trade-offs accepted:**
- In-app fallback deferred; users who ignore email still have no path back until Option C ships
- Default T+7 `reminderDate` for prep-free receipts is a heuristic, not a user-stated horizon; some users will find it too soon or too late
- Long-horizon scheduler adds cron complexity; over-engineered for 2 users but necessary for correctness at any scale

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Bug 1 alone (Option A) is the 80/20. Build it, ship it, measure whether Outcome rows accumulate, and only build the cron if long-horizon receipts are actually a pattern in the data. Counter: the cron is already identified as a failure mode with 14 known victims in the current dataset. Deferring it means knowingly shipping a silent failure for any user with a quarter+ horizon.

---

## Consequences

**`regretScore` scale is already defined:** the existing debrief form uses 1–5. No schema change needed. Document it in the API route if not already present.

**Build sequence:**
1. **Eligibility extension** — set `reminderDate = now() + 7 days` at receipt creation when no `outcomeHorizon` is provided; backfill existing receipts with no `reminderDate` (or accept they’re permanently ineligible)
2. **Long-horizon scheduler** — Vercel cron (daily or weekly) that queries receipts where `reminderDate` is within the next 30 days and no Outcome exists; queues Resend sends for any not yet sent. Replaces the single-shot schedule-at-creation pattern for long-horizon receipts.
3. **Verify delivery** — after steps 1–2, confirm Outcome rows start accumulating; run `sage_efficacy.js` check as a canary (will still be GATED but “n” should start climbing)
4. **Option C follow-on** — once delivery is confirmed working, add “Open debriefs” to `/history`; receipts with no Outcome row surface a “How did it go?” CTA

**Architecture Decision 1 (soft/hard NCI gate):** Remains deferred. Re-evaluate when `sage_efficacy.js` produces a result.

**Implementation pointer:** New issue required — `[FIX] Debrief delivery pipeline (ADR-026)`. Build sequence steps 1–3 are the acceptance criteria for unblocking `sage_efficacy.js`.

---

## Linked receipts / ADRs

- ADR-025 — SAGE signal validation path (this ADR is created by ADR-025 Option C decision)
- ADR-013 — arcs.care conversion architecture (T+7 email and Resend infrastructure context)
- ADR-023 — Observability as superionic goal lattice (downstream beneficiary of Outcome data quality)
