# ADR-015 — arcs.care Week 1 Build Gate: Case Study Content Dependency

> **Status:** DECIDED
> **Date:** 2026-05-28
> **Commit:** (set at merge)

---

## D — The Decision

**Sharp question:** Does the absence of a shareable founding-client outcome block
all three Week 1 builds from ADR-013, or do items 2 (email capture) and 3
(spots badge) proceed independently while item 1 (case study excerpt) waits
for content to exist?

---

## E — Entity / System

- `arcs-care-local/components/lab-offer.tsx` — case study receipt excerpt (item 1, content-gated)
- `arcs-care-local/components/compass-widget.tsx` — email capture on result panel (item 2)
- `arcs-care-local/components/hero.tsx` — spots badge elevation (item 3)
- `arcs-care-local/app/api/waitlist/route.ts` — reused for compass-result email capture
- Supabase `waitlist` table — `source: 'compass-result'` tagging
- **Content dependency:** one real or anonymized founding-client outcome (not a code artifact)

**Blast radius:** arcs.care only. No schema changes. No arcs-v9 impact.

---

## W — Window

**Horizon:** THIS_WEEK
**Revisit trigger:** Founding client outcome confirmed available OR confirmed unavailable.
One of those two resolves this stub immediately.

---

## Context

ADR-013 (locked 2026-05-28, commit 4932cdd) specifies the Week 1 build sequence:

```
1. Case study receipt excerpt       — gate: content must exist before build starts
2. Email capture on compass result  — reuses /api/waitlist, source: 'compass-result'
3. Spots badge elevation in hero    — 2-hour CSS/JSX change, no dependency
```

Item 1 has a hard content dependency: a founding client decision, outcome, and
permission to share (even anonymized). Items 2 and 3 have no content dependency.

The open question: is item 1's dependency a reason to wait on 2 and 3, or do
2 and 3 ship independently while item 1 is content-blocked?

The answer changes the build sequence and what ships first.

---

## Options Considered

### Option A — Items 2 and 3 proceed independently; item 1 waits
- Build email capture + spots badge now; case study ships when content exists
- Pros: no artificial sequencing; items 2/3 are independently valuable; email
  captures start accumulating before case study exists; spots badge is trivial
- Cons: page launches partial (no social proof anchor); email capture fires T+0
  receipt before the case study context exists that would make Lab offer legible

### Option B — All three items wait until case study content is confirmed
- Block the entire Week 1 build until item 1 is ready
- Pros: page launches coherent — all three gold seams visible together
- Cons: email capture delay costs real capture opportunities; spots badge is
  held for no reason; artificial coupling of independent items

### Option C — Items 3 then 2; item 1 blocked; explicit content timeline set
- Ship spots badge immediately (2h, no risk); email capture next (1 day);
  set an explicit deadline for case study content (7 days?) before declaring
  it will be replaced with a placeholder
- Pros: cleanest sequencing; forces content timeline decision explicitly
- Cons: adds a placeholder decision that itself needs a deadline

---

## Decision

**Chosen:** Option A — items 2 (email capture) and 3 (spots badge) proceed immediately; item 1 (case study) waits for content.
**Rationale:** Items 2 and 3 have no dependency on item 1 and deliver independent value. Email capture starts accumulating real signals the moment it ships. Spots badge is a 2-hour CSS/JSX change with no risk. Blocking them on a content dependency that may take days or weeks is artificial sequencing that costs real capture opportunities at zero benefit.
**Trade-offs accepted:** The Lab offer section will launch without a case study anchor for some period. Users who opt into email capture before the case study ships will receive a T+0 note without social proof context — acceptable because the T+0 note is compass-bearing-scoped, not Lab-offer-scoped. Content deadline: 14 days from 2026-05-28. If case study content is not confirmed by 2026-06-11, item 1 ships with a placeholder quote and no attribution, to be swapped when content arrives.

---

## Y — Conviction

**Polarity:** YELLOW
**Conviction:** HIGH
**Stability:** STABLE

**Loki test:** Shipping email capture before the case study means users who opt in during the gap receive a T+0 email with no social proof context from the Lab offer section — reducing the email's downstream conversion effectiveness if it references the Lab. Counter: the T+0 email is keyed to the compass bearing, not the Lab offer. Lab conversion happens on return visit or via direct follow-up, not from the T+0 email alone. The risk is real but manageable.

---

## Consequences

- Item 3 (spots badge) ships first — 2026-05-28, same session, 2h
- Item 2 (email capture on compass result) ships next — 2026-05-28 or 2026-05-29
- Item 1 (case study excerpt) ships when content is confirmed, hard deadline 2026-06-11
- If no content by 2026-06-11: ship with placeholder quote, swap on content arrival
- `NEXT_PUBLIC_CASE_STUDY_APPROVED` env var remains `false` (Vercel production) until content confirmed + approved

**Implementation pointer:** ADR-013 § Week 1 build sequence · `lab-offer.tsx` · `compass-widget.tsx` · `hero.tsx`

---

## Linked ADRs

- ADR-013 — Kintsugi build sequence (upstream; this stub resolves ADR-013's content dependency)
- ADR-012 — PLG Phase 1 (upstream context)
