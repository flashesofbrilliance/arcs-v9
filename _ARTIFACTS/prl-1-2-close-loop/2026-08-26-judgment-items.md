# Small open bugs — analysis + recommendation (judgment stays Zach's) — 2026-08-26

## 1. Lyro races the flow on returning visitors

**Symptom:** on a returning visitor, Lyro can engage before the lead-capture flow fires, so the
visitor free-texts with the AI and capture never runs. Root cause is architectural: Tidio runs
Flows -> Lyro -> Human sequentially, and the capture flow's trigger is first-visit-scoped, so a
returning visitor has no flow to run and falls straight to Lyro.

**Options:**
- A. **Accept for the pilot** (recommended). Volume is low, Lyro's task/handoff still captures
  contact info on the paths that matter, and every real fix costs flow redesign (returning-visitor
  trigger + dedup against re-greeting annoyance) during a phase that is closing. Log it as a known
  limitation on the status page; revisit in 1.5 (the Lyro phase) where this is natural scope.
- B. Scope now: add a returning-visitor trigger variant of the capture flow with a suppress-if-
  captured condition. Est. 2-4h including test passes, plus re-running Layer 0 per the rule that
  any flow change re-runs the suite.

**Recommendation: A.** 1.5 owns Lyro behavior; fixing it twice is waste.

## 2. "Read more here" links in Lyro answers

**Decision per backlog:** convert only the /contact/ source to a manual Q&A (so the answer gives
the actual contact path inline instead of a bare link), park the rest for 1.3 when the knowledge
layer is rebuilt against the ground-truth catalog anyway. This is a Tidio-UI task (human at
keyboard or Chrome session with Zach present); staged as a 1.3 line item, not done this session.

## 3. Vercel analytics audit on older static PRL pages — CLOSED

Verified 2026-08-26: all 8 PRL surfaces in `public/` (todd-call, prl-chatbot, and the six
prl-status-* pages) carry the insights snippet. No gaps. Nothing to do.
