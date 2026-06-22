# ADR-026 — Outcome-logging UX

> **Status:** DECIDED
> **Date:** 2026-06-22
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** What is the minimum UX surface, schema delta, and adoption mechanism needed to bring `Outcome` row count to MIN_SAMPLE=20 per SAGE-fired/not-fired cohort, unblocking `sage_efficacy.js` and all downstream operator validation?

---

## E — Entity / System

- `Outcome` table (Supabase) — currently 7 columns, 1 row
- `Receipt` table — 184 rows, the source population
- `SageTrace` table — 9 rows, the SAGE-fired cohort
- `sage_efficacy.js` — the validation script; gates at MIN_SAMPLE=20 per cohort
- `/brief/[receiptId]` — the existing post-compass artifact surface (most natural re-entry point)
- `src/app/api/` — API route layer where outcome write endpoint lives

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** `sage_efficacy.js` produces a result — i.e., both cohorts (sage_fired=true and sage_fired=false) each have ≥20 Outcome rows. At that point, re-open ADR-025 Option A (text-derived signal).

---

## Context

The `Outcome` table schema is already correct for the efficacy study [cite:40]:

| Column | Type | Notes |
|---|---|---|
| `id` | text | PK |
| `receiptId` | text | FK → Receipt |
| `what` | text | Free-text: what did the user decide/do? |
| `matched` | boolean | Did the outcome match the compass True North? |
| `regretScore` | integer | User-reported regret (implied 0–10 scale) |
| `learning` | text | Optional: what would you do differently? |
| `loggedAt` | timestamp | Auto-set |

`sage_efficacy.js` joins `Outcome → Receipt → SageTrace` on `receiptId` and splits on `sage_fired` [cite:41]. No schema changes are required — the bottleneck is entirely on the UX side (users never see a prompt to log an outcome).

With 184 Receipts and 1 Outcome (0.5% close-loop rate), the gap is behavioral, not structural. The most likely root cause: there is no post-compass moment that surfaces outcome logging. Users get a result, leave, and have no reason to return unless the product creates one.

The `regretScore` field has no documented scale. This must be defined and enforced in the UI before logging — a freeform integer is useless for averaging.

---

## Options Considered

### Option A — Passive prompt on Brief page
- Add a "How did it go?" section at the bottom of `/brief/[receiptId]`; users who return to their brief see it
- Pros: Zero new surfaces; lowest build cost; non-intrusive
- Cons: Relies on users returning to their brief, which likely mirrors the current 0.5% rate. Won't move the number.

### Option B — Timed email re-engagement
- Send a follow-up email N days after a compass call (e.g., T+7 or T+14): "What happened with [true_north summary]?"
- Pros: Meets users where they are (email); proven pattern; existing Resend + T+7 infrastructure already in place (see ADR-013 / `cron/t7-emails`)
- Cons: Requires threading `receiptId` + `true_north` into the email template; requires a unique logging URL per receipt; higher build surface than Option A

### Option C — Prompt on next compass visit
- When a user opens the compass again, surface a modal or inline prompt: "Last time you asked: [prior true_north]. How did it go?"
- Pros: Catches users in a decision-making mindset; contextually relevant
- Cons: Requires session state / receipt lookup on compass load; more complex; may feel interruptive

---

## Decision

**Chosen:** Option B (timed email re-engagement), with Option A as a low-cost complement

**Rationale:** The existing T+7 email infrastructure (Resend batch, `cron/t7-emails/route.ts`, `compass_receipt_id` already threaded into the waitlist capture) is the shortest path to reaching users outside the app. Option A alone won't move the number because it requires users to return unprompted — the same behavioral gap that produced 0.5%. Option C has the highest build cost and the most UX risk.

Building Option B on the T+7 cron means:
1. A targeted re-engagement email referencing the user's specific True North (not generic)
2. A unique deep-link to `/outcome/[receiptId]` — a lightweight logging surface
3. Option A (Brief page prompt) ships alongside as a zero-friction complement for users who do return organically

**Trade-offs accepted:**
- Email re-engagement requires Resend template work and a new `/outcome/[receiptId]` route
- Outcome logging is still opt-in — some users will never close the loop regardless of prompts
- MIN_SAMPLE=20 may still take weeks to clear if compass traffic is low; this ADR cannot control for that

---

## Y — Conviction

**Polarity:** GREEN
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Option B is overkill — Option A (Brief page prompt) is free and might be enough if users are already visiting their briefs. Counter: there's no evidence users return to briefs; the 0.5% rate suggests they don't. Building Option A alone is the same bet that produced 1 Outcome in 184 tries. Option B's marginal build cost against the T+7 infrastructure is low relative to unblocking the entire operator validation path.

---

## Consequences

**Schema delta required:** None — `Outcome` table is already correct.

**`regretScore` scale must be defined before build:** Recommend 1–5 ("1 = no regret, made the right call; 5 = deep regret, would do the opposite"). Must be enforced as a constrained input in the UI and documented in the API route — a raw integer field with no scale is unanalyzable.

**Build sequence:**
1. Define `regretScore` scale (1–5), document in this ADR and in the API route
2. `/outcome/[receiptId]` — lightweight page: True North recap + 3-field form (matched boolean, regretScore 1–5 slider, optional learning text)
3. `POST /api/outcome` — write Outcome row; idempotent (one outcome per receipt)
4. Option A complement — add "Log outcome" link to `/brief/[receiptId]` pointing to `/outcome/[receiptId]`
5. Extend T+7 email template — thread `receiptId` + `true_north` into existing cron; link to `/outcome/[receiptId]`
6. After MIN_SAMPLE=20 clears — run `sage_efficacy.js`; re-open ADR-025 Option A

**Architecture Decision 1 (soft/hard NCI gate):** Remains deferred. Re-evaluate in the ADR-025 re-open once `sage_efficacy.js` produces a result. No gate implementation until NCI is validated.

**Implementation pointer:** New issue required — `[FEAT] Outcome-logging UX (ADR-026)`. Build sequence steps 1–5 above are the acceptance criteria.

---

## Linked receipts / ADRs

- ADR-025 — SAGE signal validation path (this ADR is created by ADR-025 Option C decision)
- ADR-013 — arcs.care conversion architecture (T+7 email infrastructure source)
- ADR-023 — Observability as superionic goal lattice (downstream beneficiary of Outcome data quality)
