# Compass Atomic Design Spec — v1

**Status: SPEC — not yet wired to live data**
**Date:** 2026-05-29
**Source:** Architect packet (Kairos Recall — canon-derived, nothing invented)
**ADR reference:** ADR-020 (Tribune Layer), ADR-016 (auth gate), ADR-017 (receipt schema)

---

## Gate Status

| Atom | Gate | Status |
|---|---|---|
| 1–4 (Question / Horizon / Stakes / CTA) | None — UI only, no auth needed | UNBLOCKED |
| 5–6 (True North card + Why bullets) | Needs `POST /api/question-compass` | UNBLOCKED |
| 7–8 (Depth trigger + Mode badge) | Same as 5–6 | UNBLOCKED |
| 9 (Drift Sentinel) | Needs session model + JTBD anchor — Phase 3 | BLOCKED |
| 10 (Receipt persistence indicator) | Gate 1: auth verified E2E; Gate 2: receipt in prod | BLOCKED |
| 11 (NCI display) | RICH/DEEP mode, needs compass orchestrator | BLOCKED |

---

## ATOM 1 — Question Input Field

**Design Spec**
- Single large text box, white/clean surface
- Placeholder: *"What are you really trying to decide right now?"*
- Max 2–3 sentences; character soft cap at ~280 (enforce at UX layer, not hard block)
- No label above — the placeholder IS the label
- Font: body, `--text-base` to `--text-lg`, generous line-height

**Product Requirements**
- Required field — no submission without it
- Free text only; no dropdowns, no predefined categories
- On submit, text feeds `classify_context` microservice — user never sees this routing
- Must log raw text to Decision Receipt with `decision_receipt_id` at time of submission

**Implementation Considerations**
- `POST /api/question-compass` receives: `{ user_id, question, horizon, stakes, verbosity? }`
- Input sanitized before passing to context classifier
- Do NOT parse or classify client-side — all ARCS geometry runs server-side

---

## ATOM 2 — Horizon Chip Row

**Design Spec**
- 4 single-select chips in a horizontal row
- Labels: `Today` / `This week` / `This quarter` / `1–3 years`
- Single-select only; selected chip fills with primary accent color
- No label required — chips are self-describing
- Chips collapse to 2-column grid on mobile

**Product Requirements**
- Required; default = none selected (force explicit choice)
- Maps internally to `altitude` inference: Today/This week → L2–L3 (tactical); This quarter → L1–L2 (operational); 1–3 years → L0–L1 (strategic/Constitutional Court)
- This mapping is **never shown to the user**

**Implementation Considerations**
- Enum: `horizon: 'today' | 'week' | 'quarter' | 'years'`
- Horizon + Stakes together feed `select_mode` to determine QUICKMOVE / PLAN / COURT
- Store raw value in receipt; do not store inferred altitude in user-facing schema

---

## ATOM 3 — Stakes Chip Row

**Design Spec**
- 3 single-select chips: `Low` / `Medium` / `High`
- Optional sublabels (shown below chip, smaller text): *annoying if wrong* / *costly but fixable* / *hard to undo*
- Same single-select behavior as Horizon chips
- `High` chip: subtle warm/warning tint on selection — not alarming, just distinct

**Product Requirements**
- Required; no default
- `High` stakes + `1–3 years` horizon = auto-escalate to COURT mode internally; Constitutional Court runs silently
- `High` alone triggers BAR Ruin check under the hood
- Stakes feeds `irreversibility_score` (0–1 float) in internal receipt

**Implementation Considerations**
- Enum: `stakes: 'low' | 'medium' | 'high'`
- BAR tier auto-assigned: Low → Baseline; Medium → Asymmetric; High → Ruin check required
- `irreversibility_score` is computed server-side, not exposed in UI

---

## ATOM 4 — Primary CTA Button

**Design Spec**
- Label: **"Get my next move"**
- Full-width on mobile; constrained (240–300px) centered on desktop
- Solid primary accent color — no gradients (gradient buttons = AI slop anti-pattern)
- Disabled state: muted, not hidden, until all 3 fields populated

**Product Requirements**
- Triggers `POST /api/question-compass`
- On click: button enters loading state (spinner, label changes to *"Thinking…"*)
- Loading duration: 1.5–4s typical (Claude call); show skeleton result card during wait, not blank screen
- On error: inline error below button, not toast

**Implementation Considerations**
- Loading state must disable re-submission (prevent duplicate receipts)
- Response streams if possible — show True North sentence first, then Why bullets, to reduce perceived latency
- Error message: *"Something went wrong — your question is saved. Try again."* (preserve input state)

---

## ATOM 5 — True North Output Card

**Design Spec**
- Appears below the input form after submit; does not replace the form
- Bold single sentence at `--text-lg` to `--text-xl`
- Clear visual separation from input (subtle card lift / surface-offset background)
- No header label ("Your answer:", "True North:", etc.) — the sentence IS the answer
- Decision mode badge (small chip): `QUICK MOVE` / `PLAN` / `COURT` — muted, top-right of card

**Product Requirements**
- Always present; never suppressed even in SIMPLE mode
- True North sentence must be **identical** across SIMPLE / RICH / DEEP — deeper modes add context, never reverse the sentence
- Must include `decision_receipt_id` (not shown to user — stored in DOM/session for downstream calls)
- If COURT mode: add subtle amber indicator that Constitutional guardrails were applied (no detail unless user expands)

**Implementation Considerations**
- Response schema: `{ true_north: string, why: string[], mode: string, clarity_mode: string, decision_receipt_id: string, show_full_reasoning_available: boolean }`
- True North sentence: max 25 words
- Stream True North first, then append Why bullets as they resolve

---

## ATOM 6 — Why Bullets (3-Bullet Block)

**Design Spec**
- Max 3 bullets, always exactly 3 in SIMPLE mode
- Bullet structure (canonical, never vary):
  - Bullet 1: Identity/values point (if High stakes) or practical constraint (if Low/Med)
  - Bullet 2: Practical constraint (time/energy/money)
  - Bullet 3: Upside/optionality point
- `--text-base`, regular weight, left-aligned
- Subtle bullet marker — dash or minimal circle, not icon-in-colored-circle (AI slop)

**Product Requirements**
- Bullets derived from LAB + FATED internally — never expose macro names to user
- In SIMPLE mode: bullets are compressed summaries, no sub-points
- In RICH mode: bullets may expand to 1–2 sentences each
- DEEP mode: bullets replaced by full reasoning graph (different component)

**Implementation Considerations**
- Server must guarantee exactly 3 bullets in SIMPLE; 3 expanded bullets in RICH
- Bullet content tagged internally with source macro (FATED/BAR/LAB) for receipt audit trail
- Never surface macro tags in UI

---

## ATOM 7 — "See Full Reasoning" CTA / Depth Trigger

**Design Spec**
- Small text link below Why bullets: *"See how I got here →"*
- Not a button — text link with subtle arrow, `--text-sm`, `--color-text-muted`
- On click: expands inline (no navigation); accordion pattern
- Only visible if `show_full_reasoning_available: true` in response

**Product Requirements**
- Consent-gated entry to RICH / DEEP mode — never auto-expanded
- First expansion → RICH (adds context narrative + 1 visual if applicable)
- Second CTA inside RICH → *"Show me everything"* → DEEP (full Court/LAB/advisor output)
- DEEP mode requires explicit second click — never inferred

**Implementation Considerations**
- Expansion calls `POST /api/question-compass/deepen` with `{ decision_receipt_id, depth: 'rich' | 'deep' }`
- Receipt is updated with `clarity_mode` field on each deepening call
- DEEP mode should be rate-limited or gated (Phase 4 / Stripe billing candidate)

---

## ATOM 8 — Decision Mode Badge

**Design Spec**
- 3 states: `QUICK MOVE` / `PLAN` / `COURT`
- Small chip, `--text-xs`, upper-case tracked
- Color: neutral/muted by default; COURT gets subtle amber tint
- Positioned: top-right of True North card

**Product Requirements**
- Auto-assigned server-side from `select_mode` logic:
  - Low stakes + short horizon → QUICK MOVE
  - Medium stakes or medium horizon → PLAN
  - High stakes or high irreversibility → COURT
- Never user-selectable on input — always output
- COURT badge: tooltip on hover: *"Constitutional guardrails were applied to this answer"*

**Implementation Considerations**
- Enum: `mode: 'quickmove' | 'plan' | 'court'`
- COURT mode: `court_invoked: true` in Tribune table (ADR-020) when Tribune Layer is live
- Badge must persist if user deepens to RICH/DEEP — mode doesn't change with depth

---

## ATOM 9 — Drift Sentinel Nudge

**BLOCKED — Phase 3+ (requires session model)**

**Design Spec**
- Inline, non-modal banner within the session UI
- Single sentence + 2 action buttons: `"Stay exploring"` / `"Land the plane"`
- Warm/amber background tint — noticeable but not alarming
- Dismissible; disappears if user takes either action

**Product Requirements**
- Fires after 3+ consecutive low-semantic-overlap interactions without producing an artifact
- Message template: *"We've drifted from [JTBD anchor] with [X] left in this session. Stay exploring or land the plane?"*
- "Land the plane" generates a single time-bounded prompt → one concrete artifact (receipt, spec, checklist)
- Drift state stored in session: `ONTRACK` / `USEFULTANGENT` / `DERAILMENT`

**Implementation Considerations**
- Requires JTBD anchor field in session init (`POST /api/session/init` — v9 backlog item)
- Drift computed server-side via semantic embedding comparison against JTBD anchor
- Do NOT ship until session model is instrumented (Phase 3+)

---

## ATOM 10 — Decision Receipt Persistence Indicator

**BLOCKED — Gate: auth verified E2E + receipt persisting in prod**

**Design Spec**
- Small, quiet indicator below the True North card
- Icon + text: `✓ Saved to your receipts` (appears ~1s after successful save)
- `--text-xs`, `--color-text-muted`; no emphasis — confirmation, not celebration
- Links to `/receipts` page on arcs.care (Phase 2 dependency)

**Product Requirements**
- Only visible if user is authenticated (email captured)
- Pre-auth: replaced with *"Sign in to save this →"* soft nudge (no force)
- Receipt ID must be generated even pre-auth (anonymous receipt for re-engagement)
- On anonymous receipt: store in localStorage until auth completes, then migrate to Supabase

**Implementation Considerations**
- `compass_receipts` table (arcs-care Supabase direct, per Phase 2 architecture)
- Anonymous receipt: `user_id: null`, `session_token: [ephemeral]`
- Auth migration: on email capture, update `user_id` on all receipts with matching `session_token`

---

## ATOM 11 — NCI Score Display (RICH / DEEP only)

**BLOCKED — Gate: compass orchestrator built**

**Design Spec**
- Numeric score + label: `87 / 100 — HIGH COHERENCE` or `NCI: OM`
- Only visible in RICH or DEEP mode — never in SIMPLE
- `--text-sm`, monospaced font for the number
- Positioned within the expanded reasoning section, not the main card

**Product Requirements**
- NCI grades: `< 50` = LOW (flag), `50–74` = MEDIUM, `75–89` = HIGH, `90–100` = OM (gold state), `UNDEFINED` = system declined to score
- NCI components: Factual Accuracy / Source Quality / Intellectual Honesty / Actionability
- `UNDEFINED` state shown when evidence is insufficient — never fake a score

**Implementation Considerations**
- NCI computed as part of the synthesis step in the Compass orchestrator
- Store all 4 sub-scores in receipt JSONB, surface aggregate only in UI
- `UNDEFINED` is a first-class Triune Logic state — must be returned as a valid value, not null

---

## Canonical Cross-Atom Rules — WRITE-LOCKED

These govern all atoms above and cannot be overridden at the component level:

- **True North is always identical across depth modes** — no quiet reversals
- **Complexity is consent-gated** — RICH and DEEP only via explicit user action
- **No macros/labels exposed in SIMPLE mode** — BAR, LAB, FATED, KKL are internal only
- **Constitutional Court runs silently** in SIMPLE; visible in DEEP only
- **NOTOMATION**: no atom silently edits external state — every write is human-confirmed
- **Minimum 12px text floor** on all atoms; body at 16px; buttons at 14px
- **No gradient buttons** — solid accent color only (gradient = AI slop anti-pattern)
- **Bullet markers**: dash or minimal circle only — no icon-in-colored-circle
