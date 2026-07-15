# arcs.care Landing Page Optimization — Platinum Master Package

**Version:** 1.0.0 · **Date:** 2026-07-10 · **Author:** Claude (Fable 5) with Zach Harris
**Scope:** arcs.care `/` landing page + first-run Question Compass funnel (`/dashboard`)
**Evidence basis:** live page fetch (verified identical to repo `main`), full code audit, Granola meeting corpus, first external user session (Vic, 2026-07-09/10), GitHub issue scan. **No Vercel Analytics numbers were available to this session** — every claim below is labeled Fact-backed / Inference / Hypothesis accordingly.

---

## 1. Executive North Star

- **Core problem (1 sentence):** The page has the right architecture — anonymous-first, a real receipt as proof — but it's flying blind (zero click instrumentation), the subhead is a wordy mixed metaphor, and the first real user got a degraded answer because nothing invites the prior analysis he'd already done.
- **Recommended move (1 sentence):** Instrument every CTA, tighten copy in place, add the missing share card, and make the "add context / prior work" path legible — no redesign.
- **Top 3 reasons:**
  1. You cannot rank any future landing change without CTA event data; instrumentation is the prerequisite for everything else. (Fact-backed: 0 `track()` calls on `/` or `/dashboard`.)
  2. The only real-user session on record (Vic) praised the design and framing but hit two concrete failures: an affordance that reads as disabled text, and an answer that assumed zero prior analysis. Both are S-sized fixes. (Fact-backed.)
  3. The page already converts on architecture — no signup wall, live product proof — so copy/affordance precision is the highest-leverage remaining surface. (Inference.)
- **Top 3 risks:**
  1. n=1 user feedback over-steers copy — mitigated by shipping the smallest version and measuring for 2 weeks.
  2. Prompt change (exclusion criteria) could shift answer quality for users who state no prior work — mitigated by making the block conditional on user-stated prior work.
  3. Silent regression risk: this repo serves 4 domains from one deployment; deploy only from the main checkout (known worktree gotcha).
- **Smallest viable high-leverage change set:** the 10 quick wins in §2, all S complexity, no new dependencies, no structural change.

---

## 2. Prioritized Quick-Wins Table

| # | Priority | Change | Why it matters | Evidence source | Complexity | Confidence | Expected impact | Owner |
|---|----------|--------|----------------|-----------------|------------|------------|-----------------|-------|
| 1 | P0 | `track()` on every landing + compass CTA | Unblocks all future decisions; currently blind | Code audit (0 events on funnel); Zach in-thread | S | High | Enables measurement (indirect) | Eng |
| 2 | P0 | "Add context" affordance fix (`CompassForm.tsx:78–84`) | First real user read it as disabled text and never found it | Vic session (fact) + code (40% opacity dimmed mono) | S | High | Higher prep uptake → sharper answers | Eng |
| 3 | P0 | Prior-work capture: placeholder invite + exclusion-criteria prompt block | ARCS assumed Vic did no analysis; violates "lived experience outranks system inference" | Vic session (fact); prompt audit (no such block) | S | High | Better answers for prepared users | Eng |
| 4 | P1 | Subheadline rewrite | Current copy is 3 sentences with a mixed metaphor ("line of sight to the horizon line") | Live copy (fact); quality judgment (inference) | S | Medium | Clarity at first read | Copy |
| 5 | P1 | Root `opengraph-image.tsx` | Shares of arcs.care render bare text — every share is a lost trust impression | Code audit (fact: none exists) | S | High | Better share CTR (hypothesis) | Eng |
| 6 | P1 | Metadata retitle ("ARCS Field OS" → visitor-facing) | Internal codename as browser-tab/search title | Code audit (fact) | S | High | Search/social clarity | Copy |
| 7 | P2 | Wire dead `onCalibrate` as quiet secondary CTA | Prop exists, never rendered; calibrated sessions produce sharper terrain | Code audit (fact: dead prop) | S | Medium | More calibrated sessions (hypothesis) | Eng |
| 8 | P2 | Trust line under primary CTA ("Free · no account needed…") | Anonymous-first is a real differentiator the page never states | Code audit (fact: no auth wall, unstated) | S | Medium | Lower CTA hesitation (hypothesis) | Copy |
| 9 | P2 | Mañana footer copy tighten + instrument | Only revenue CTA on the page; currently a vague question | Live copy (fact); Zach confirmed keep-Mañana | S | Medium | Inquiry click-through (hypothesis) | Copy |
| 10 | P3 | Compass event taxonomy (`compass_submitted` etc.) | Zach requested verbatim; completes funnel visibility | Zach in-thread (fact) | S | High | Full-funnel measurement | Eng |

---

## 3. Landing Page Diagnosis

**What is working** (leave untouched):
- **Split-screen hero: pitch left, live receipt right.** Real product output as the trust signal — doctrine-perfect (earned fidelity, not decoration). Vic: "Excellent design… really really like the framing." *Fact-backed (user quote). Confidence: high.*
- **Anonymous-first funnel.** No signup wall anywhere; receipts claimable after later login (ADR-016). Rare and genuinely low-friction. *Fact-backed (code). Confidence: high.*
- **H1 "What are you really trying to decide?"** Doubles as the product's own L0 question. Do not touch. *Fact-backed (it survived a real user's first contact with praise). Confidence: high.*
- **"How it works" 4-step section.** Honest, unhyped, right register. *Confidence: medium.*
- Mobile: container queries + auto-fit grid, no JS breakpoints. Structurally sound. *Fact-backed. Confidence: high.*

**What is confusing:**
- Subheadline mixes metaphors and buries the mechanism. "Clear line of sight to the horizon line" — a line of sight *to a line*. *Fact-backed (live copy) → inference (it costs comprehension). Confidence: medium.*
- Post-CTA, the "Add context" affordance renders at 40% opacity dimmed mono text until a decision is typed, then brightens only to `text.dimmed`. Vic (mobile): "that looks like disabled text." *Fact-backed. Confidence: high.*

**What is likely suppressing conversion:**
- Nothing states the offer costs nothing and needs no account — the single strongest objection-remover is implicit. *Inference. Confidence: medium.*
- Bare-text link previews (no OG image) on every share. *Fact-backed gap → hypothesis on impact.*
- First-answer quality for prepared users: no intake of prior analysis → generic-feeling first bearing → weaker word of mouth. Vic's session is the proof case. *Fact-backed (n=1). Confidence: medium (n=1).*

**What should be removed:** Nothing structural. The page is already ≤7 sections and ≤3 CTAs. (Deletion review done; the discipline is holding.)

**What should be rewritten:** Subheadline (§4 has exact copy), page `<title>`/description, Mañana footer message, compass Decision placeholder.

**What should be re-ordered:** Nothing. Section order (hero+proof → how it works → footer offer) is correct.

---

## 4. Brutally Efficient Design Spec

- **Page objective:** Get a visitor with a live decision to open the compass and submit a real question with enough context to earn a sharp bearing.
- **Audience segments** (from Granola, trust-ordered): (1) operators/founders with a live high-stakes fork, discretionary spend; (2) career-pivot individuals; (3) referred-in evaluators (like Vic) kicking the tires.
- **Primary JTBD:** "I'm too deep in the variables to see the answer — show me the terrain and give me one direction I can defend."
- **Messaging hierarchy:** 1) the question (H1, unchanged) → 2) the mechanism + payoff (subhead) → 3) proof (featured receipt) → 4) how it works → 5) the team offer (footer).

**Replacement copy (exact):**

| Slot | Current | Replacement | Rationale |
|------|---------|-------------|-----------|
| Subhead | "Critical decisions are too important to tackle alone. When you're too close to the problem a fresh perspective helps. ARCS gives you a clear line of sight to the horizon line and orients you in the right direction." | "It's hard to see the simple answer when you're deep in the variables. ARCS stress-tests the decision you're carrying and hands back one clear direction — with the reasoning, the tradeoffs, and what to watch next." | First sentence is Vic's own words, near-verbatim — voice of customer. Mechanism + payoff, one metaphor, two sentences. |
| Trust line (new, under CTA) | — | "Free · no account needed · first bearing in about a minute" | States the objection-removers the code already delivers. |
| Secondary CTA (new, quiet) | — (dead `onCalibrate` prop) | "Calibrate first →" (ghost, sm) | Activates the existing prep path without competing with the bindu. |
| `<title>` | "ARCS Field OS" | "ARCS — Navigate to clarity" | Visitor-facing; keeps the primary tagline. |
| Meta description | "Navigate to clarity. Make the decision visible." | "Bring ARCS the decision you're carrying. It stress-tests your framing and hands back one clear direction — reasoning, tradeoffs, and what to watch." | Mechanism-first for search/share surfaces. |
| Footer offer | "Interested in ARCS powered sprints by Mañana?" | "ARCS-powered decision sprints for teams — run by Mañana." | Statement of offer, not a question; Mañana kept per Zach. |
| Compass placeholder | "Type the decision, not the stress around it. The real fork, not the symptom." | "Type the decision, not the stress around it — and include what you've already analyzed or ruled out." | Zero-schema prior-work capture (Vic fix). |
| Context affordance | "Add context — stakes, confidence & what you already know" | "Add what you already know — it sharpens the bearing →" | Leads with payoff; pairs with the contrast fix. |

**Visual/interaction rules:**
- Inline styles + `@/ui/tokens` only (repo law). Palette unchanged: `#020408` bg · `#00F0FF` cyan · `#FFD700` gold · `#00FF9D` green.
- Context affordance states: resting (no decision typed) = `text.dimmed` at 0.5 opacity; armed (decision typed) = `signal.cyan` at full opacity. The state change **is** the animation — no pulse needed (pulse deferred; decoration vs. precision conflict).
- One bindu per screen holds: "Get True North" stays the only primary action on `/dashboard`; "Open the compass" the only primary on `/`.
- Accessibility floor: armed/resting states must differ by more than opacity (color shift included); all buttons remain real `<button>` elements.
- **Do-less rules:** no new sections; no testimonials until a second consenting case exists (Dan Pascone gate, ADR-015, still unresolved); no animation work; no chat UI (deferred hypothesis, §5 non-goals); max 3 CTAs per screen.

**Change classes:** Quick wins, no structure: #1–4, 6, 8–10. Quick wins, low structure: #5 (new file), #7 (new element). Medium-lift (specced, deferred): prep prior-work field + migration; clarification gate; context expand-in-place. Deferred ideas: chat UI, pulse animation, testimonial section, full redesign.

---

## 5. PRD

- **Problem statement:** The landing→compass funnel is unmeasured, understates its own strengths (free, anonymous, real proof), and produces degraded first answers for prepared users because it never invites prior analysis.
- **User goals:** Understand what ARCS does in one read; get a first bearing fast; have prior work respected rather than re-derived.
- **Business goals:** More compass sessions per visit; more brief views; measurable funnel; inquiry clicks on the Mañana offer.
- **Non-goals (explicit):** Full redesign; chat-style compass UI (Vic's preference — recorded, declined for now: structured MVP is deliberate); testimonials (blocked on ADR-015 consent); pricing/paywall surfaces; SOC-2/enterprise messaging.
- **Success metrics** (all post-instrumentation; no baselines exist today): landing→compass-open rate; compass-open→submit rate; context-affordance open rate; % of submissions containing prior-work signal; brief CTA CTR; footer inquiry clicks.
- **Events/telemetry needed:** see §8 taxonomy.
- **Functional requirements:** FR1 all funnel CTAs emit `track()` events. FR2 context affordance has visually distinct resting/armed states. FR3 compass system prompt honors user-stated prior work as exclusion criteria and never re-proposes ruled-out options. FR4 root OG image renders brand card at 1200×630. FR5 metadata is visitor-facing. FR6 secondary calibrate CTA routes to `/prep?q=`.
- **Non-functional:** No new npm dependencies; inline styles only; no schema/migration in Phase 1; page stays a single server-rendered pass (no new client fetches); no regression to the 13 subdomain rewrites.
- **Dependencies:** Vercel Analytics dashboard access (human) for baselines; deploy from main checkout only.
- **Risks/assumptions:** n=1 feedback; prompt-change answer drift (mitigate: conditional block); assumption that Vercel Analytics custom events are enabled on the project plan (verify in Phase 0).
- **Open questions:** Does the Hobby/Pro plan cap custom events? What is the current weekly visitor count (unknown — dashboard)? Dan Pascone case-study consent (ADR-015)?

---

## 6. Implementation Plan

| Phase | Scope | Deliverables | Owner | Deps | Cx | Conf |
|-------|-------|--------------|-------|------|----|------|
| **0 — Evidence** | Verify custom events fire in prod; pull dashboard baseline (visitors, top pages, devices, referrers — human step); optional: receipt/user counts via `supabase` CLI | Baseline note appended to this doc | Zach + Eng | Dashboard access | S | High |
| **1 — Quick wins** | All 10 items in §2 | Code in repo, this doc, preview verification | Eng | none | S | High |
| **2 — Structural** | Prep "already ruled out" field (+ PrepSession migration + EXCLUSION CRITERIA prompt block); context expand-in-place accordion on `/dashboard`; clarification gate design ADR | Migration + ADR + code | Eng | Phase 1 data | M | Medium |
| **3 — Experiment** | Copy A/B via 2-week windows (not split tests at this traffic); clarification gate build (L0 semantic check: high-stakes + no prior-work signal → 1–2 clarifying questions before bearing, maps to Calibrate/HOLD in canon) | Gate + eval | Eng | Phase 2 | L | Medium |

- **Branch strategy:** feature worktree → PR → merge to main → deploy **from main checkout only** (worktree deploy silently drops subdomain rewrites — documented regression).
- **Ticket breakdown (GitHub Issues):** one issue per §2 row for Phase 1 is overkill — ship as one PR titled `feat(landing): instrumentation + copy + first-run fixes`; open 3 issues for Phase 2 (prep field, accordion, clarification-gate ADR).
- **Review loop:** preview deployment → Vercel toolbar comments → resolve threads → promote. Each merged change gets a DEWY receipt via the normal commit format.

---

## 7. Self-Contained File Brief (hand to any coding agent)

- **Purpose:** Apply all Phase 1 quick wins. This is a **component patch set**, not a replacement page.
- **Files:**
  1. `src/organisms/Home.tsx` — subhead swap (§4 exact copy); trust line under CTA (mono, `text.dimmed`, 0.75rem); ghost `size="sm"` "Calibrate first →" button beside primary, `onClick={onCalibrate}`; `track()` on: primary CTA (`landing_cta_compass`), brief buttons (`landing_cta_brief`), tributary chips (`landing_tributary_click`, `{type}`).
  2. `src/app/layout.tsx` — title/description/OG/twitter strings per §4.
  3. `src/app/opengraph-image.tsx` — **new**; static 1200×630 `ImageResponse`, no DB: bg `#020408`, cyan left rail (4px), "ARCS" wordmark row, H1 "What are you really trying to decide?", tagline "Navigate to clarity." Copy the styling idiom from `src/app/brief/[receiptId]/opengraph-image.tsx` but with `runtime = "edge"` acceptable → use `nodejs` to match sibling.
  4. `src/ui/StickyFooter.tsx` — no code change needed except `track('footer_inquiry_click')` in the CTA onClick; message string changes at the call site in `layout.tsx`.
  5. `src/organisms/CompassForm.tsx` — placeholder swap; affordance copy swap; armed/resting color states (`signal.cyan` when `question.trim()`); `track('compass_context_opened')`, `track('compass_submitted')`, `track('compass_example_clicked')`.
  6. `src/app/api/compass/route.ts` — add a `PRIOR WORK` rule to the SYSTEM prompt (after the RULES intro): treat user-stated analysis/ruled-out options as exclusion criteria; never re-propose ruled-out options; if HIGH stakes and no prior work stated, surface that as an explicit assumption in `fated.assumptions`, not a silent default.
- **Inputs required:** none beyond repo access. **No new deps** — `track` is already installed via `@vercel/analytics`.
- **Acceptance criteria:** `npx next build` clean; `/` shows new subhead + trust line + calibrate CTA; `/dashboard` affordance turns cyan when a decision is typed; events visible in network tab (`/_vercel/insights/event`) on click; `/opengraph-image` returns a PNG; no visual regression in the receipt card.
- **Definition of better (plain English):** A first-time visitor can tell within one read what ARCS does and that trying it costs nothing; a prepared user can tell ARCS what they already know and the answer respects it; and every one of those moments now emits a signal we can count.

---

## 8. Analytics Plan

- **Vercel Analytics answers immediately (dashboard, human pull):** pageviews, visitors, top pages, referrers, device/browser mix, country. **It cannot answer alone:** CTA click-through, funnel progression, scroll depth, per-session behavior, anything before today (no retroactive events).
- **Event taxonomy (minimal, final):**
  `landing_cta_compass` · `landing_cta_calibrate` · `landing_cta_brief` · `landing_tributary_click {type}` · `footer_inquiry_click` · `compass_context_opened` · `compass_submitted {hasContext}` · `compass_example_clicked`
  (8 events. Waitlist/sign-in clicks deliberately excluded from Phase 1 — AuthControl is app-wide chrome; add in Phase 2 with a `location` prop if the data is missed.)
- **2-week learning plan:** Week 1 — collect; no changes. Week 2 — compute landing→compass-open, open→submit, context-open rates; read referrer mix against Granola's segment hypothesis.
- **Decision rule:** If compass-open rate ≥ baseline intuition (set the number after Week 1) → keep and move to Phase 2. If submit rate drops vs. open rate after the prompt change → inspect receipts for answer drift, revert the prompt block alone. Copy changes revert independently of instrumentation (never revert instrumentation).

---

## 9. Decision Receipt

- **Question:** How do we raise clarity, trust, and conversion on arcs.care without a redesign?
- **Horizon:** THIS_WEEK (ship) / THIS_QUARTER (learn).
- **Stakes:** MEDIUM — public surface, low blast radius, fully reversible (TWO_WAY door).
- **Options considered:** (A) full redesign — rejected, no evidence supports it; (B) instrument-and-tighten (chosen); (C) do nothing until analytics exist — rejected, instrumentation IS the change; (D) chat-style compass rebuild (Vic) — deferred hypothesis.
- **Recommended move:** B — the 10-item quick-win set, then measure for 2 weeks.
- **Why:** Zero-instrumentation is the binding constraint; the only real-user evidence points at S-sized fixes; doctrine (less-is-more, deletion before addition) rules out speculative structure.
- **What would change my mind:** Two weeks of data showing healthy CTA click-through but poor submit completion (→ the problem is the compass form, escalate Phase 2 accordion + gate); or a second user independently requesting conversational flow (→ re-open option D as a real experiment).

---

## 10. Missing Evidence / Next Retrieval Steps

| Missing | Why it matters | Retrieval step |
|---------|----------------|----------------|
| Vercel Analytics baselines (visitors, referrers, devices, trends) | All impact claims above are hypotheses without it | Zach: dashboard → arcs-v9 project → Analytics; screenshot into repo or paste into Phase 0 note |
| Custom-events plan support | `track()` events may be capped/disabled on current plan | Verify one event arrives in dashboard after deploy |
| Receipt/user/waitlist counts | Sizes the funnel; candidate trust-signal number | `supabase` CLI (MCP is wrong org — known gotcha) |
| Dan Pascone case-study consent (ADR-015) | Unlocks the only shippable social proof | Zach: confirm with Dan |
| Second+ user sessions | Everything Vic-derived is n=1 | Send arcs.care to 3–5 more people post-ship; watch the new events |

---

*Doctrine conflicts surfaced (none silently overridden): testimonials conflict with warmth-through-precision until consent exists → deferred. Pulse animation conflicts with no-decoration → replaced with state-contrast. Chat UI conflicts with structured-MVP decision → recorded as hypothesis, not built. Clarification gate is doctrine-mandated (lived experience outranks system inference) and is the flagship Phase 2/3 item.*
