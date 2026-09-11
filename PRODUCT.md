# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

ARCS is deliberately **dual-audience**; both are first-class, durable users, not one real user plus marketing.

1. **Decision-makers under pressure.** An individual (or small team) who is stuck, pressurized, or standing at a fork with a high-consequence decision that will not wait. They arrive in fog and need to see the *shape* of the decision — what they are actually deciding, who else is in it, the time window, and how solid their conviction is. They are not looking to be told what to do.

2. **Evaluators of the maker's craft.** Prospective employers, consulting clients, and boards assessing whether the person behind ARCS builds production-grade systems solo, with discipline and honesty. A large share of surfaces (the live build-status page, per-engagement call briefs, recoil reports, external counterpart twins) exist primarily for this reader. Their job is to decide whether to hire, engage, or fund.

The same product truth serves both, but individual surfaces usually optimize for one reader; which one is a per-surface decision, recorded in that surface's brief, not here.

## Product Purpose

ARCS is a **decision-intelligence platform** that produces clarity about the *shape* of a decision, not an answer. A user brings a question; ARCS runs it through a pipeline (L0–L5) and returns a bearing — a sharpened question (D), the entities in play (E), the time window (W), and a conviction gate (Y) — plus a small number of tributaries (the deeper question, the uncomfortable constraint, the cross-domain reframe). Output is a **Receipt**: a decision's state vector frozen in time, which can be revisited, and whose history becomes the user's personal cartography.

Success is currently measured on four fronts at once, all live:
- **Land a role** — prove production-grade solo craft to prospective employers.
- **Land consulting / Mañana** — convert evaluators into paid engagements (consultancy, B2B sprints, scoped builds).
- **Grow compass usage** — grow the B2C Question Compass as a product-led onramp.
- **Advance the product** — ship the platform toward its roadmap (ATG, Kairos detection, Observatory/replay, L6–L7).

## Positioning

The mechanism a neighboring product could not truthfully copy: ARCS **scaffolds and sequences a person's own cognition without ever deciding for them or overruling their revealed preference** (NOTOMATION). It renders decisions at *earned fidelity* — the output is only as sharp as the evidence deserves and never lies about how certain it is. It treats a zero-margin ("free-solo") decision topology as a design bug to be re-shaped toward survivable failure, not a personality trait to optimize around. The free compass additionally functions as a psychographic filter (self-selecting for growth-mindset, positive-sum thinkers) rather than a generic top-of-funnel.

## Operating Context

- Primary product surfaces: `/` (entry), `/dashboard` (main compass UI), `/compass` (magic-link login), `/brief/[receiptId]` (cartography brief). Core pipeline is `POST /api/compass` → Receipt.
- Evaluator surfaces are frequently standalone HTML pages served at per-engagement subdomains (e.g. `status.arcs.care`, `<name>.arcs.care` call briefs), some password-gated (gate = the person's first name), some deliberately ungated.
- Live in production at `app.arcs.care` (and `arcs.care`, `www.arcs.care`, `resume.arcs.care`), all served by this repo's deployment.
- Reading register for evaluator surfaces is often non-technical or tech-weary; artifacts must be legible without ARCS insider vocabulary.

## Capabilities and Constraints

- **Built:** compass pipeline (L0–L5) → DEWY receipt + Y-gate; prep session; cartography brief; guide; history; magic-link auth; anonymous-receipt claim on sign-in.
- **Not yet built / on roadmap:** ATG tributary expansion, Kairos timing detection, Observatory/replay as an interactive product surface, L6–L7 governance engine, outcome-loop closure, billing gate.
- **Terminology** is canonical and load-bearing: DEWY (D/E/W/Y state vector), Y-gate states (GREEN/YELLOW/RED/FORK/SCRATCH/DELTA/PARADOX/DRIFT), Receipt, Brief, Compass, tributaries, NCI, confidence vs conviction (confidence = belief is true; conviction = how stable that confidence is; NCI = coherence of the whole decision, decision-level only, never per-belief).
- **Technical:** Next.js 16 · Prisma 7 (SQLite dev / Supabase prod) · Auth.js v5 · Anthropic SDK. Inline styles only in components (no Tailwind, no utility classes); sole stylesheet is `globals.css`. No new dependencies without asking. JSON arrays stored as TEXT.

## Brand Commitments

- **Name:** ARCS. Taglines: *Navigate to clarity. Survive the pressure. Find the flow.* / *Render through the fog.*
- **Voice:** calm, precise, serious play; instruments in skilled hands, not SaaS onboarding. Copy does not explain what the reader already understands and never implies the system decides for them (reinforces user agency).
- **Plain language, no em-dashes** in deliverables: short, uncomplicated sentences; translate jargon; audience is often non-technical.
- **Dark-cockpit design system binds product surfaces** (app, dashboard, briefs, status): the canonical ARCS visual world (dark palette `#020408`/`#0d1117`, JetBrains Mono + Inter, 2.5D isometric decision-observatory register, earned-fidelity render scale) governs. Full physics spec in `WORLD.md`; tokens are canonical in `colors_and_type.css` / the design-system bundle. (Impeccable `document` can record it as DESIGN.md later; this file does not.)
- **Per-engagement canon families may carry their own locked visual world** (confirmed 2026-07-25): e.g. the Louisville omakase family at `public/omakase/` runs its canon-locked house grammar (case `#0B0B0C` / dial `#E8E4DA` / gold `#C9A227` / vermillion `#E34F1C`, Helvetica voice + SF Mono serialization, "color is never ornament"). Each such world is recorded per surface and is binding within its family; it does not leak into product surfaces.
- **No em-dashes, anywhere, without exception** (reaffirmed 2026-07-25): the plain-language rule wins even over authored canon voice. Counterpart-facing canon artifacts are swept the same as business deliverables; prefer commas, colons, periods, or the house interpunct.

## Evidence on Hand

- **Real repository history** is the proof substrate: commit counts, day-count, milestones, and deploy state are measured directly from the public repo and must always resolve to real commits/deployments.
- Real client engagements exist as source material (e.g. Todd Hotes / PRL Resins chatbot, Ahmed Elsamadisi / Polyform reconnect, and other per-name briefs) with transcripts and SSOT JSON in `runtime/recoil/generated/`.
- **Non-negotiable — real data only:** never fabricate numbers, quotes, testimonials, benchmarks, metrics, customers, pricing, or deployment claims. Every headline claim must trace to a real source, and unproven claims are stated as absent rather than invented. A final fact-check pass against the source transcript is required before shipping any counterpart-facing artifact.

## Product Principles

1. **NOTOMATION.** Scaffold and sequence cognition; never compress, replace, or overrule the user's revealed preference. The user decides; ARCS shows the terrain.
2. **Earned fidelity.** Render only as sharply as the evidence deserves. Never overclaim certainty; a coarse answer honestly labeled beats a confident fabrication.
3. **Real data or nothing.** Every claim is falsifiable and sourced. Fabrication is the one unrecoverable failure.
4. **Dual-audience discipline.** Product truth is shared, but each surface serves one reader; keep an air-gap so evaluator-facing artifacts never leak another party's private material or internal scoring.
5. **Instrument, not dashboard.** Calm, precise, legible under pressure. Cut what does not earn its place; concentrate rigor on the materially significant decision logic.

## Known design failure modes (check on every design pass, handoff, or pickup)

**The measure/wrap regression class** (recurred 3x on 2026-08-23 alone: wing page column, stat strip, PRESENT deck; fixes in arcs-v9 PRs #159/#162/#165). The defect never looks the same twice but has one root: layout constraints written as selector-local literals, so every new region or port re-derives its own edges and breakpoints. Binding rules for all surfaces:

1. **Reading measures are `:root` tokens** (e.g. `--measure: 660px`), inherited by every text role in a column. Never per-selector literals, and never `ch` caps on mixed font sizes (`ch` recomputes per font size, so roles get misaligned right edges and caps silently move at breakpoints).
2. **Content grids use `repeat(auto-fit, minmax(<longest-real-value>px, 1fr))`**, never fixed columns plus a single mobile breakpoint: that pattern clips at every width between the tested presets. (Deliberate `1fr auto 1fr` center-pinning grids for chrome are the sanctioned exception.)
3. **Responsive verification sweeps four widths**: desktop, ~790px, tablet, mobile. The regression lives at the intermediate widths presets skip.
4. `text-wrap: balance` on headings, `text-wrap: pretty` on reading text, `white-space: nowrap` on chips/counts/values that must never break mid-token; mono stat values step down a size on phones rather than wrapping.
5. **Ported CSS re-audits against these rules at port time**: the deck recurrence happened because chan-era CSS predating rule 1 was imported wholesale.

## Accessibility & Inclusion

Plain-language requirement (above) is partly an accessibility commitment: surfaces must be legible to non-technical, tech-weary readers without insider vocabulary.

**WCAG 2.1 AA is the target for product surfaces** (confirmed 2026-07-25). Experience/canon artifacts meet AA where feasible (contrast, visible focus, reduced-motion support, keyboard paths) without flattening their committed aesthetic; deliberate sub-AA moments in an experience artifact are recorded as intentional exceptions, not defects.
