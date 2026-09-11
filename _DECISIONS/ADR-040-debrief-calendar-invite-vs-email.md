# ADR-040 — Debrief Close-the-Loop: Calendar Invite vs. Email Only

> **Status:** DRAFT
> **Date:** 2026-06-21
> **Commit:** (set at merge)
> **Note:** Drafted 2026-06-21 as "ADR-026" but never tracked; renumbered to ADR-040 on 2026-08-01 to resolve a collision with the tracked ADR-026 (Debrief Delivery Fix). Still DRAFT — Decision section pending Zach's call.
>
> **Code-verified state (2026-08-01):** the close-the-loop JTBD is **already shipped as Option C, Stage 1** — the loop closes today without any calendar mechanism. Built & hardened: the in-app debrief surface (`src/app/debrief/[receiptId]/page.tsx` + `src/app/api/receipts/[receiptId]/outcome/route.ts` writing `Outcome`, status→LOGGED, driftState LANDED/DRIFTING), the `DebriefCard` prompt, compass-time scheduled Resend send (`api/compass/route.ts:509–582`, loud logging, opt-in gating), and the long-horizon cron sweep for the >30-day Resend ceiling (`api/cron/debrief/route.ts`). **Not built:** `.ics` attachment (Option A's calendar half) and Google Calendar API / OAuth (Option B) — no `googleapis` dep, no Google provider, `Account` token columns unused. So this ADR's live question narrows to: *is a calendar mechanism worth adding on top of the shipped email+in-app loop?* — lower urgency than the original 0.4%-completion framing implied, since the loop is no longer email-only-and-broken.

---

## D — The Decision

**Sharp question:** Should the debrief (close-the-loop) touchpoint move from email-only to a real Google Calendar event, given email-only is producing a ~0.4% completion rate?

---

## E — Entity / System

- `src/app/api/compass/route.ts` — debrief email send logic (§2, the block this ADR concerns)
- `src/lib/auth.ts` — Auth.js v5 config; currently Resend magic-link only, no OAuth provider
- `prisma/schema.prisma` — `Account` model already has unused `access_token`/`refresh_token`/`expires_at` fields
- Resend (existing email infra) vs. Google Calendar API (new dependency + new OAuth surface)
- Google Cloud Console — manual, human-only setup step (OAuth consent screen, Calendar API enablement, CLIENT_ID/CLIENT_SECRET) — cannot be automated by an agent

---

## W — Window

**Horizon:** QUARTER
**Revisit trigger:** Real with-Google-Calendar-connected user count crosses a threshold worth re-evaluating ROI, OR Apple/Outlook calendar parity becomes a stated requirement.

---

## Context

This session's audit of the 248-receipt production corpus found a confirmed bug: Resend's `scheduledAt` has a hard 30-day maximum, and the existing `.catch(() => {})` silently swallowed every failure beyond that window — at least 14 of 74 eligible receipts hit this with zero visibility (commit `eff3d65`, this session). That bug is now fixed (logged loudly, not solved structurally) — the underlying question of *how to actually close the loop* remains.

The completion rate (1 logged Outcome across 248 receipts, now 177 after dedup) is also explainable by mundane causes — the debrief feature was rolled out recently, the receipts are largely the account owner's own dev-testing traffic, and there's been no real attempt yet to act on a debrief reminder. So the data does **not** prove email is ineffective; it proves nothing has been tested at all yet. This ADR is being drafted on a hypothesis (calendar invites get native reminders, lower chance of inbox burial) — not on confirmed evidence of email failing where a calendar invite would succeed.

A real Calendar API integration also happens to structurally fix the 30-day Resend ceiling for free: creating a calendar event is a synchronous API call at receipt-creation time, and the event's *start date* can be arbitrarily far in the future — there is no Google Calendar equivalent of Resend's "schedule a send 30 days out" limit, because nothing is being delayed; the event simply exists now with a future start time.

---

## Options Considered

### Option A — Email only, fix what's already broken
- Keep `.ics` attachment as the calendar affordance (no event creation, just an "add to calendar" file the email recipient can click)
- No new OAuth provider, no new dependency, no manual Google Cloud setup
- Works identically for every calendar provider (Google, Apple, Outlook) since `.ics` is a universal standard
- Con: still requires a manual click to add to calendar — same friction class as clicking a debrief link directly. Doesn't structurally improve completion rate, just adds a second affordance.

### Option B — Real Google Calendar API push
- Add Google as a second Auth.js OAuth provider, requesting `calendar.events` scope
- Existing magic-link users need a new "connect Google Calendar" linking flow — they did not consent to this scope at sign-in
- Requires token refresh logic (access tokens expire ~1hr; debrief events fire days/weeks/months later)
- Requires a manual, human-only setup step: Google Cloud Console project, OAuth consent screen, Calendar API enablement, CLIENT_ID/CLIENT_SECRET generation
- No Outlook/Apple Calendar parity without separate, provider-specific integrations
- Pro: genuinely no click required — the event exists on the user's calendar with a native reminder, no email-open or link-click dependency at all
- Pro: structurally fixes the 30-day Resend ceiling as a side effect

### Option C — Both, staged
- Ship Option A now (cheap, immediate, zero new dependencies, fixes the universal-compatibility gap)
- Ship Option B later, gated on real signal that Option A's completion rate is still poor *despite* real usage (not dev-testing noise)
- Avoids spending OAuth/token-refresh engineering effort before there's evidence it's the actual bottleneck

---

## Decision

**Chosen:** _(left blank — DRAFT, pending your call)_

**Rationale:** _(pending)_

**Trade-offs accepted:** _(pending)_

---

## Y — Conviction

**Polarity:** SCRATCH
**Conviction:** LOW
**Stability:** SHIFTING

**Loki test:** The entire premise — "calendar invites close the loop better than email" — is unvalidated. The 0.4% completion rate has a much simpler explanation (dev-testing traffic, feature rolled out recently, account owner hasn't tried debriefing himself yet) than "email is the wrong channel." Building real Calendar API integration (OAuth provider, token refresh, account-linking UX) before testing whether the existing email flow works at all on real usage is solving a problem that hasn't been confirmed to exist. Option C's staging explicitly addresses this — ship the cheap fix, gather real signal, then decide if B is justified.

---

## Consequences

- If Option C: no engineering work blocks on this ADR being fully decided — `.ics` attachment can ship now under the existing email infra, no new accounts/scopes needed
- If Option B (now or later): unblocks on the human-only Google Cloud Console setup step first — cannot be started by an agent
- Either way, this ADR should be revisited once there are ≥20 *real* debrief opportunities (not dev-testing duplicates) to look at actual completion rate before/after any change

**Implementation pointer:** none yet — DRAFT status, no code changes implied until Decision is filled in

---

## Linked receipts / ADRs

- ADR-026 — Debrief Delivery Fix (the loud-logging fix for the 30-day Resend ceiling; this ADR is the follow-on strategic question of *how* to close the loop)
- This session's commit `eff3d65` — fixed the silent 30-day Resend scheduling failure that prompted this ADR
- ADR-016 — arcs-v9 auth model (Resend magic-link only; Option B would extend this, not replace it)
