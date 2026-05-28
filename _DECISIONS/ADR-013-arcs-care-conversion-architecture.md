# ADR-013 — arcs.care Conversion Architecture: Build Sequence for Founding-10 Acquisition

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** (set at merge)

---

## D — The Decision

What is the correct build sequence for closing arcs.care's founding-10 client
conversion gap — given that the page serves warm-traffic referrals (not cold PLG),
the email infrastructure is live, and the hero redesign is a third-order move?

---

## E — Entity / System

- `arcs-care-local/components/compass-widget.tsx` — result panel; email capture added here
- `arcs-care-local/components/lab-offer.tsx` — case study receipt excerpt added above CTA
- `arcs-care-local/components/hero.tsx` — spots badge elevated in prominence
- `arcs-care-local/app/api/waitlist/route.ts` — reused for compass-result captures (`source: 'compass-result'`)
- `arcs-care-local/app/globals.css` — minor style additions only
- Supabase `waitlist` table — captures compass emails; T+0 + T+7 cron sequence fires automatically
- Resend (`RESEND_API_KEY`) — already configured; no new env vars needed
- **NOT in scope this ADR:** hero two-column redesign, soft auth, Stripe

**Blast radius:** arcs.care only. No arcs-v9 or Supabase schema changes required.

---

## W — Window

**Horizon:** THIS_QUARTER
**Revisit trigger:** 1 Lab inquiry within 30 days of case study going live.
If this fires → hero redesign is next.
If it does not fire → reassess whether the page is the conversion surface at all (Option C promoted).

---

## Context

The dual-bar-raiser + ATG + ultrareview gauntlet run on 2026-05-28 produced three
findings that shape this decision:

1. **Distribution model is undefined at NCI 85.** arcs.care is not a cold-traffic PLG
   funnel — it is a handshake artifact for Zach's warm referral network. The page's
   job is credibility/legitimacy, not conversion. The DM is the conversion surface.

2. **Compass gives value away free.** This is not a bug — it is the trust instrument.
   For a $300 service, trust IS the product. But the result panel has no forward pull:
   compass → result → cold Lab ask. No nurture step.

3. **No named social proof.** "Battle-tested in live founder workshops" is generic.
   A specific human, decision, and outcome above the Lab CTA would do more than
   any layout change.

**Email infrastructure is live:** Resend configured, `/api/waitlist` operational,
T+0 receipt fires on signup, T+7 cron runs daily. Compass capture reuses this
with `source: 'compass-result'` — no new route required.

**CANON_COLLISION resolved:** Email capture on compass result would conflict with
existing "No email required · 60 seconds · one clear output" microcopy. Resolved
by framing as optional follow-up: *"Want Zach to send a note on this? One message,
no list."* This preserves the compass instrument's identity and sidesteps the
future soft-auth collision (parallel identity layers).

---

## Options Considered

### Option A — Case study + email capture + spots prominence (chosen)
- Ship three targeted changes in sequence; reuse existing infra; no hero rebuild
- Pros: closes nurture gap; adds named social proof; preserves compass instrument identity;
  no new dependencies; falsifiable within the founding-10 window
- Cons: doesn't fix the distribution model if warm traffic volume is too low to signal

### Option B — Hero redesign first (the wireframe)
- Two-column split, compass at fold, fog atmosphere, distinctive display font
- Pros: correct aesthetic direction; stronger instrument register than current poster layout
- Cons: layout change does not close the nurture gap; doesn't add social proof;
  signals nothing if traffic volume is too low; high LOE for uncertain PLG return
- Deferred: correct as the third move, not the first

### Option C — Do nothing to the page; optimize direct outreach instead
- Write outreach DM templates for Zach's warm network; treat page as static credibility artifact
- Pros: matches actual distribution model; zero build cost; highest leverage if the page
  is not the conversion surface
- Rejected because: Zach's direct outreach is already running and has not produced
  the founding 10. The case study adds credibility *to that outreach* — it's a link
  Zach sends in DMs, not a standalone conversion surface. Option A and Option C
  are complementary, not competing.
- **If the 30-day signal does not fire:** Option C is promoted to primary strategy.
  This must not be treated as a strawman — it is the correct fallback.

---

## Decision

**Chosen:** Option A — sequenced, targeted, in order below.

**Build sequence:**

```
Week 1 — The gold seams (in order)
  1. Case study receipt excerpt       lab-offer.tsx, above Lab CTA
     One real anonymized founder: decision, true north, outcome.
     Written in ARCS receipt register — not a testimonial box.
     Gate: case study content must exist before build starts.

  2. Optional email capture           compass-widget.tsx, below result panel
     "Want Zach to send a note on this? One message, no list."
     Optional field. Reuses /api/waitlist with source: 'compass-result'.
     T+0 receipt fires automatically. T+7 cron follows.
     Microcopy updated: remove "No email required" from submit state;
     retain it on the form state (pre-result).

  3. Spots badge prominence           hero.tsx, immediately below headline
     Move "6 of 10 founding spots remaining" from microcopy
     to a live badge with pulsing dot — above the CTA buttons.

Week 2 — Verify signal
  Observe: did any Lab inquiry arrive within 30 days of case study going live?
  If yes → hero redesign (Option B) is next sprint.
  If no  → Option C promoted; evaluate direct outreach systematically.

Week 3+ — Hero redesign (Option B)
  Only if signal fires. Not before.
```

**Rationale:** The three changes close specific gaps (nurture, social proof, scarcity
legibility) without touching the hero. They are independently deployable and
individually falsifiable. The email infrastructure is already live — the build
cost is low. The falsifiability threshold is conservative: one Lab inquiry in
30 days is achievable even at low traffic volume.

**Trade-offs accepted:**
- Case study content must exist before build starts — this is a content dependency,
  not a code dependency. If no founding client outcome is shareable, item 1 slips.
- Optional email capture changes the compass result panel's UX — mitigated by
  framing as follow-up from Zach, not a newsletter gate.
- Hero redesign is deferred — the wireframe direction is correct but the data
  to justify it doesn't exist yet.

---

## Y — Conviction

**Polarity:** YELLOW
**Conviction:** MEDIUM
**Stability:** REVISIT

**Rationale for YELLOW/MEDIUM:** Two unknowns remain at lock time:
(1) case study content — does a founding client outcome exist that can be shared?
(2) traffic volume — warm referrals may be insufficient to trigger the 30-day signal
even if the changes are correct. GREEN/HIGH would require these resolved.

**Loki test:** arcs.care's traffic volume is low enough that the 30-day signal
window produces noise, not signal — even a perfectly executed build yields 0 Lab
inquiries because 3 warm visitors used the compass. Counter: the signal threshold
is a Lab *inquiry* (a DM or email to Zach), not a booked Lab — this is observable
at near-zero traffic. If Zach gets 3 compass users and sends 3 personal follow-up
notes (via T+0 receipt capture) and none respond, the signal is clear: Option C.

---

## Consequences

1. **Before Week 1 build starts:** Confirm case study content exists. If no founding
   client outcome is available to share, item 1 cannot ship — skip to items 2 and 3.

2. **Microcopy audit:** Update compass-widget.tsx — "No email required" retained on
   form state (pre-submit); removed from result state (post-submit, where capture lives).

3. **Soft auth dependency note:** The `source: 'compass-result'` waitlist entries
   are informal identity (email + compass context). When soft auth lands (future ADR),
   these must be reconcilable — recommend tagging with `compass_receipt_id` for
   future linkage. Not required for this build; flagged for the auth ADR.

4. **If 30-day signal does not fire:** Option C is the correct next move. Write three
   outreach DM templates for Zach's warm network. The page becomes a static
   credibility artifact, not a conversion surface.

5. **If 30-day signal fires:** Hero redesign sprint opens. Wireframe from 2026-05-28
   (arcs-care-local/wireframe-hybrid.html) is the starting point — instrument aesthetic,
   two-column, compass at fold.

---

## Linked ADRs

- ADR-012 — PLG Phase 1 (upstream; this ADR is the implementation sequence for ADR-012)
- ADR-001 — Auth gate strategy (downstream dependency when soft auth lands)
