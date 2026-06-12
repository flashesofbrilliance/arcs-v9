# ADR-025 — ARCS Go-Live: Provisional Logic for the Public Launch

> **Status:** DRAFT (PROVISIONAL — held in the pressure band, Bayesian-updatable)
> **Date:** 2026-06-12
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Ship `app.arcs.care` publicly now — announced on LinkedIn — with the
anonymous compass open, the brief publicly shareable, and sign-up / advisory as the
lead-capture gate, rather than waiting for a more complete product?

---

## E — Entity / System

- Public surface: `app.arcs.care` (promoted toward primary `arcs.care`)
- Funnel: anonymous compass → public brief → **gated share / history** → advisory waitlist
- Instrumentation: Vercel Analytics (`brief_shared` + brief page-views), `Lead` table
- External: the LinkedIn launch post (the public articulation of the positioning)

---

## W — Window

**Horizon:** WEEK (launch), reviewed at T+30 days
**Revisit trigger:** the 30-day signal read below. Any of: zero brief shares, zero waitlist
signups, or zero advisory inquiries after meaningful traffic → re-open the positioning and the
gate placement.

---

## Context

The launch post stakes a deliberately sharp position: *"You are certain you know. That
certainty is the problem."* ARCS is framed not as another tool that optimizes from your input,
but as one that runs a **hard gate before any output** — is the question correctly framed, is it
biased, does the confidence score have a documented methodology — and kills what fails. The
architecture pitch is concrete: L0–L5 resolution → vector survivability scoring → decision
receipts → Bayesian update loop. "Not vibes. 🧾"

This is a one-way **public** act (the post is out; the brand claim is made), but the underlying
product decisions remain two-way and revisable. The launch-hardening work in this sprint is the
instrumentation that turns the launch from an assertion into a measurable bet:
- per-user receipt isolation + auth-gated sharing (the lead-capture hook),
- prep integration (so results aren't skewed by a hardcoded confidence),
- the advisory waitlist + consult funnel,
- analytics on brief sharing.

---

## Options Considered

### Option A — Launch now, gate sharing/history, capture via waitlist *(chosen)*
- Public compass + public briefs maximize reach from the post; sign-up is the natural
  capture moment when a user wants to *share* or *keep* their work.
- Pro: converts attention into leads without a hard wall in front of the core value.
- Con: depends on shares/briefs being compelling enough to trigger sign-up.

### Option B — Hard login wall before the compass
- Pro: every user is a known lead from turn one.
- Con: kills the anonymous funnel the post is explicitly driving; high drop-off.

### Option C — Delay launch until full product (RBAC, observatory, etc.)
- Pro: more complete first impression.
- Con: forfeits the launch-moment attention; the post is already public.

---

## Decision

**Chosen:** Option A.

**Rationale:** The post is live and the positioning is sharp; the highest-leverage move is to
let attention flow to a working compass and shareable briefs, and to place the only friction
exactly where intent is highest (share / save / advisory). This matches the "earned clarity"
ethos — the user does the work first, then chooses to keep it.

**Trade-offs accepted:** We are betting that briefs are share-worthy and that the gate converts
rather than repels. We accept a thinner first-run product (no observatory, no RBAC beyond the
share gate) in exchange for capturing the launch window.

---

## Y — Conviction

**Polarity:** YELLOW
**Conviction:** MEDIUM
**Stability:** CONTESTED

**Loki test:** The sharpest case against: the "your certainty is the problem" frame is
confrontational; some prospects bounce rather than engage, and the share gate adds friction at
the exact moment of enthusiasm — so the funnel could capture *fewer* leads than a softer,
ungated share with a follow-up nudge. If T+30 shows shares-but-no-signups, the gate is the
suspect, not the positioning.

---

## Consequences

- Unblocks: the launch-hardening PRs (analytics, prep, auth-gating, advisory funnel) become the
  measurement apparatus for this bet.
- Creates: a T+30 review obligation against the signal read.
- Amends: ADR-001 / ADR-016 — history is now per-user gated by default (see ADR-016 amendment).

**30-day signal read (what confirms / refutes):**
- `brief_shared` events > 0 and brief page-views climbing → sharing loop works.
- `Lead` rows (source=waitlist) > 0 → demand for full-service.
- `Lead` rows (source=advisory) ≥ 1 → the advisory motion has a pulse.
- Zero across all three after real traffic → refute; re-open positioning + gate placement.

**Implementation pointer:** this sprint's PRs (prep integration, auth-gated PLG, advisory
funnel, analytics) on branch `claude/launch-hardening` + analytics PR #7.

---

## Linked receipts / ADRs

- ADR-016 — arcs-v9 Auth Model (relates to / amended: history now gated by default)
- ADR-001 — App-level auth gate (relates to)
- ADR-012 / ADR-013 — arcs.care PLG + conversion architecture (sibling funnel logic)
