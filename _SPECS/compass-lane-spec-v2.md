---
title: Compass Lane · domain-agnostic spec v2 (Search Compass is instance 1)
status: DRAFT for Zach's review · 2026-09-05
supersedes: _SPECS/search-compass-plg-spec-v1.md (kept; v1's onramps and phases are now the job-search binding of this spec)
grounded in: ADR-068 (verb x altitude print schedule) · ADR-070 (two surfaces: receipt + induction) · the Tao coordinate system (D/R/W/C/H x five verbs) · runtime/specs/target-role-scan.json · runtime/specs/forge-triggers.json
---

# Compass Lane

> One loop, many problem shapes. A stream of candidates, sized against a declared target, decided by a human, worked through a five-stage lane, and closed against what actually happened.

Search Compass (jobs.arcs.care) is the first instance. Nothing in this document names a job, a posting, or a resume except in the binding section, and the code follows the same rule: the engine reads a **lane file**; the lane file is the only place the domain lives.

## 1. The isomorphism

Every problem shape this covers has the same skeleton:

| Invariant | Job search | Sales | 0→1 build | Ops |
|---|---|---|---|---|
| **Subject** (who is deciding, with a record) | candidate + resume record | seller + case history | founder + prior builds | team + runbooks |
| **Target** (what a good candidate looks like, as weights) | role rubric | ideal customer profile | bet criteria | SLA + severity policy |
| **Stream** (candidates arriving from sources) | postings | leads | ideas / tickets | incidents / requests |
| **Sizing** (score each candidate against the target, evidenced) | composite + band | fit + qualification | scope score | triage |
| **Decision** (the human swipes) | right / left + why | pursue / pass | greenlight / park | accept / defer |
| **Run** (work fired by a decision, tiered and metered) | forge: cut, page | proposal, pilot | build sprint | fix |
| **Counterpart** (a human on the other side; unlocks the full tier) | recruiter / hiring manager reply | buyer engagement | user / customer | requester |
| **Outcome** (what happened, scored against the ex-ante receipt) | screen, offer, reject | won / lost | shipped / killed, retro | resolved, postmortem |

The five lane stages are the five verbs of the print schedule. Labels differ per domain; the rule that each stage prints an artifact through a gate to a fate does not.

## 2. Core objects (domain-free)

```
Tenant       owner of everything below
Subject      {record: structured fields + evidence grades + flags, intake: url | document | export}
Target       {archetypes[], quads[] (differentiators with proof + dim loading), filter{in[],out[]},
              dims[{key,label,weight,anchor0,anchor3}], gates[], bands, cutoff, tiers}   ← today: target-role-scan.json
Source       {type, adapter, config, poll_window, last_run, last_error}
IngestRequest{sources[], from, to, status, counts}
Candidate    {id, source, url, title, org, place, first_seen, seen_count, hint?}       ← today: JobOpportunity
Score        {candidate, target_version, dims, gates, composite, band, tier, read, evidence{quad: [quotes]},
              meta{...domain fields...}, scored_at}
Decision     {candidate, direction, why?, note?, at}                                     ← today: JobSwipe
Run          {candidate, tier: light|full, status ∈ lane.run_statuses, artifacts[], cost, notes}  ← today: ForgeRun
Counterpart  {candidate, kind, replied_at}                                               ← gate for full tier
Correction   {candidate|target, learned, pattern, avoid, logic[{step,confidence}], links[]}  ← Wayfinder's record
Outcome      {candidate, stage_reached, result, at, vs_receipt: {predicted, actual, delta}}
Ledger       {run, est, actual, credits}
Lane         {domain, stages[5]{label, verb, print, gate, fates[], sla?}, run_statuses[], decision_vocab, why_tags[]}
```
Domain-specific fields live in `Score.meta` and in the lane file (for example ATS class, hiring manager, apply path are job-search meta). The engine never reads them by name; the lane's `meta_schema` tells the surfaces how to render them.

## 3. The lane file

`runtime/specs/lanes/<domain>.json`. The engine loads one per tenant surface. It carries:

- `stages`: five, in verb order. Each has a label, the verb, what it prints, its gate, its fates, and an optional SLA. A Candidate's `stage` is one of these labels; the kanban is a rendering of stages.
- `run_statuses`: the vocabulary for a Run (today: queued, gathering, grading, rendering, built, live).
- `triggers`: the what-fires-when table (today: forge-triggers.json), keyed on decision direction, tier, and current status.
- `decision_vocab` and `why_tags`: what a swipe is called and the reasons offered on a no.
- `sources`: which adapter types the lane accepts.
- `meta_schema`: the domain fields on Score and how to label them.
- `lenses`: which D/R/W/C/H aspect each rubric dimension loads on, so the Tao proverbs can be pointed at a candidate without a second taxonomy.

The first lane file ships with this spec: `runtime/specs/lanes/job-search.json`.

## 4. Pipelines (domain-free)

- **Ingest.** IngestRequest → each enabled Source's adapter → Candidate records, deduped by id. Adapters are the only code that knows a source's shape.
- **Size.** Candidate + Target → Score. Reads the candidate's own text before scoring; quotes it per differentiator; unknown stays unknown. Re-sizes on target version change.
- **Decide.** A Decision applies the lane's trigger table; the engine creates or withdraws a Run. Pure function, asserted by the trigger eval.
- **Run.** Light tier from a decision; full tier only with a Counterpart. Stages print artifacts per the lane; hosting or sending is a separate human-approved fate.
- **Close.** Outcome recorded against the Score and any Correction; Ledger actual against estimate. This is the recapitulate stage and it is mandatory, not optional.

## 5. Surfaces (domain-free, lane-labeled)

Board (stream, sized, decided), Candidate Scan (subject overlaid on target for one candidate), Subject Scan, Target Scan with a calibration editor, Sources, Lane view (the five stages as columns with SLA color), Run page (public, air-gapped), Counterpart tier. Every label on every surface comes from the lane file. Mobile first for the decision surface.

## 6. Onramps (domain-free)

The six from v1, restated without the domain:

| # | Bring | Get in 60 s | Gated |
|---|---|---|---|
| O0 | one candidate URL | a Candidate Scan against a generic Subject, labeled generic | nothing |
| O1 | the stream (an email forward, a connection, a CSV) | a seeded board, sizing running | sign-in |
| O2 | the Subject's record | Subject Scan, Target seeded from the lane's archetype library, everything re-sized | sign-in |
| O3 | sources | more streams, a source list with last-run, IngestRequest as a real action | sign-in |
| O4 | a decision | a Run, stage by stage; free to hold, metered to fire | credits |
| O5 | a Counterpart reply | the full tier and the close | a recorded reply |

Graceful degradation is a lane-level guarantee: no record scores against generic and says so; no text stays unsized with a reason; unknown is a valid value everywhere; a cap or spend limit holds Runs in order and drops nothing.

## 7. Safety and honesty (invariant, never per lane)

Never fabricate a candidate, a score, a figure, or a person. Unknown beats guessed. Self-reported figures carry their grade. The Subject's record never appears on a public Run page. Sizing vocabulary never leaves the instrument. Only sources the subject legitimately receives or public JSON; no login scraping. Every Run's cost is estimated before and metered after.

## 8. Evals (invariant, run per lane)

- Trigger eval: every live Candidate's Run state matches the lane's trigger table; synthetic candidates driven through the decision route at every tier.
- Sizing eval: re-sizing with the same target version is idempotent; a target version bump re-sizes everything.
- Close eval: every Outcome has a Score to compare against; Ledger actuals within tolerance of estimates.
- Lane eval: the lane file validates against the schema; five stages, verbs in order, every stage prints and gates.

## 9. Binding: Search Compass (instance 1)

Subject = candidate with the resume record and profile scan. Target = target-role-scan.json. Sources = LinkedIn alert email, Ashby/Greenhouse/Lever boards (JobFlow's detect and fetch scripts, ported), manual. Score.meta = ATS class, company type, comp band, hiring manager kind and text, apply path, next step. Run = the counterpart-application-forge light tier; full tier on a recruiter or hiring-manager reply. Stages = Research, Qualify, Apply and screen, Interview loop, Outcome and correction. Why-tags = the navigator's drainers and anti-signals. v1's phases P1 to P5 stand, with one change: P1 now ships the lane file and the Lane view alongside the ingest request.

## 10. What makes it isomorphic in code, not just on paper

1. The engine imports the lane file; no route, page, or pipeline step contains a domain noun. Today's `jobs` routes are renamed under `lanes/<domain>` when the second lane lands, not before.
2. Prisma tables are the invariant objects; domain fields go in `meta` (TEXT JSON per repo rule) with the lane's `meta_schema` as the contract.
3. Adapters are the only domain code, one file per source type, all emitting Candidate.
4. Trigger rules, tiers, why-tags, stage labels, and lenses are data.
5. The evals run per lane from the same scripts.

## 11. Prior art in ~ (Sep 2025 to Jun 2026) and what each contributes

Swept 2026-09-05. Twenty-one sibling projects; the ones with transferable ideas, each mapped to a v2 object or rule. "Adopt" means it changes this spec now; "port" means code worth moving; "keep out" means seen and declined.

| Project (last commit) | What it has | Disposition |
|---|---|---|
| **jobflow-pwa/back-project** (Oct 2025, 14 docs, "JobFlow/Satori CTS") | Haystack v2 **guardrails**: core axes ≥ 60% of weight, supplementary ≤ 20%, weak or missing evidence contributes 0 and never flips a gate. **Bounded EWMA learning** of weights from outcomes (α≈0.03, clamped, renormalized), a stated-vs-learned divergence metric, and the rule that learned changes apply only on consent and are reversible. **Kairos prompt catalog**: prompts only on consistent evidence, 1 to 3 choices, urgency Now / Soon / Later, scope "just this role / this segment for 2 weeks / keep". **Stretch rubric**: Realistic, Healthy Stretch, Long Shot, Unrealistic. **Frame storming** (elicit, detect distortions, reframe, validate, commit) before discovery. **Seven demons** bias detection (ego, hubris, greed, fear, comparison, perfectionism, identity) with user-set intensity. **Onboarding** in 60 to 90 s, ≤ 5 prompts, auto-fill defaults on timeout, reduced-motion respected. | **Adopt** guardrails, bounded consentful learning, the kairos prompt rules, the stretch rubric, and the onboarding contract as invariant rules (§7a below). Frame storming becomes the Target onramp's first step. Demons: adopt as *decision-pattern flags* on the Subject, never as diagnoses. |
| **jobflow-pwa** (Oct 2025) | Greenhouse / Lever / Ashby detection and fetch scripts; 38 VC portfolio boards; capability model; five-column kanban; honesty labels + barriers (regulated credential, deep engineering prereq, talent bench, stale > 90 d); triage timer + hotkeys; CSV import. | **Port** the three ATS scripts and both data files into the Source adapters. **Adopt** stale-over-90-days as a gate and the capability model as the surface-unlock rule. |
| **arcs_cfa / arcs-career-fit** (Nov 2025 → Jun 2026, 13 commits) | Pydantic models: ProfileVector, JobContext, **HiringArchetype** (the inferred selection function on the other side), ConsonanceResult, **Objection {type, description, prevalence, mitigation}** ranked INSURMOUNTABLE / SIGNIFICANT / MINOR, **PathwayRecommendation** (nearest-neighbor discovery by adjusting levers: title, company tier, segment, geo/mode). `job_swipe.py`: a swipe calibration game (CHAD / CULT / KAREN / COPE company archetypes) that trains the user's own definitions before recommending. `company_momentum.py`: first and second derivative of hiring volume. `application_interference.py`: **phase cancellation**, competitor clusters where simultaneous applications interfere. `primitives.py`: **jerk-based pre-peak warning** (still climbing, but the third derivative turned). Full LinkedIn export parsing. Team-bias detection with an explicit ethics frame and confidence intervals. | **Adopt** Objection with mitigation as the shape of `Score.gates` and `Score.evidence` (an objection is a gate with a way through). **Adopt** HiringArchetype as the Counterpart's inferred model. **Adopt** the swipe calibration game as onramp O4's first five swipes. **Adopt** momentum and interference as Candidate-level `hint` fields the sizing step may read. Pathway recommendation becomes the Correction's "nearest neighbor" suggestion. Keep the ethics frame verbatim for any bias feature. |
| **arcs_harmony_career_engine** (Dec 2025) | Deterministic abductive matcher: hard gates (geo allowlist, comp, anti-goals), axes skills / transfer / energy / growth with explicit weights, **confidence = share of axes with sufficient data**, missing signal = neutral never punitive, CSV taxonomies editable without code, receipts CSV with a **decision reward table** (accept 2.0, offer 1.5, interview 1.0, applied 0.5, withdraw −0.5, rejected −1.0) feeding a bounded EMA learner, JSON contracts for DecisionVector and FiveWhys, optional local embeddings off by default. | **Adopt** confidence-as-completeness on every Score, the reward table as the Outcome→learning bridge, and the DecisionVector contract as the wire shape of a Decision. Keep embeddings off by default for the same reason it gave: explainable and reversible first. |
| **wayfinder-frontend** (Nov 2025, 39 commits, Magic Patterns export) | 60+ components, pages Chronicle, Wave / Wavelength, ProfileFlow, QuickStart, DiagnosticSummary, BackendPanel; PDF + LinkedIn ZIP ingest; correlation-id error toasts; "inchworm" accordion (one section open). | **Adopt** the page set as surface names: Chronicle = the Outcome ledger, Wavelength = the Subject's energy profile, QuickStart = O0. Correlation ids on every pipeline write. Code stays out (Tailwind). |
| **arcs-navigator** (Nov 2025) | Receipt with energizers / drainers / signals / anti-signals / archetypes, daily Pulse Check, numbered atomic patterns with a glossary, intuitive-insight line. | **Adopt** drainers + anti-signals as the why-tag vocabulary, the pulse check as the free daily habit, the insight line as `Decision.note`. |
| **career-compass-discovery / -pwa, career-wavelength** (Nov 2025) | Harmony index with **discovery tiers**: prime fit ≥ 80, adjacent ≥ 65 with pattern overlap, **counterintuitive ≥ 50 and orthogonal** with high transferability; domain adjacency matrix; 8-question energy assessment; anti-pattern detection; receipts to LocalStorage or a one-endpoint server with a JSONL audit trail. | **Adopt** the third tier: the board should surface orthogonal candidates separately, not bury them under the cutoff. |
| **job-search-optimizer-v2** (Sep 2025, 50 commits) | JSON schemas jobs.v1, feedback.v1 (CloudEvents-shaped), lens.v1, model.v1; brand-aware builds (brands/<slug>) and env promotion; a "validated learning" prompt. | **Adopt** versioned schemas for Candidate and Decision events, and the brand slot as the tenant theme hook. |
| **job-tracker-pro** (Sep 2025, 47 commits) | Four-env promotion pipeline with provenance hashes and rollback. | Keep out; arcs-v9 has its own deploy doctrine. |
| tribes-and-vibes, Waypoint, wayfinder-v41 (electron/tauri), arcs_chatbot, omma.yaah | Shells and packaging experiments. | Keep out. |

### 7a. Rules adopted from prior art (now invariant)

1. **Weight guardrails.** Core dimensions carry ≥ 60% of a Target's weight; supplementary ones ≤ 20% combined; a dimension with weak or missing evidence contributes 0 and can never flip a gate. (Today's rubric: role-shape + AI-native + strength-leverage = 13 of 24 weight points, 54%. Below the guardrail; flagged for the next calibration.)
2. **Confidence is completeness.** Every Score carries confidence = share of dimensions with sufficient evidence. Missing is neutral, never punitive.
3. **Learning is bounded and consented.** Weights update only from recorded Outcomes, via a clamped EMA with the reward table, and only when the user taps adopt; every update is scoped (this candidate / this segment for a window / everything) and reversible. Stated vs learned divergence is shown, not silently applied.
4. **Prompts only at kairos moments.** Evidence first, 1 to 3 choices, an urgency (Now ≤ 72 h, Soon ≤ 14 d, Later), never a gate flip.
5. **Objections carry mitigations.** A gate is an Objection {type, prevalence, mitigation}; the honesty label (Realistic, Healthy Stretch, Long Shot, Unrealistic) is derived from gates and confidence, and the mitigation is what the Run prints against.
6. **Orthogonal is a tier.** Candidates below the cutoff but orthogonal with high transferability surface as a separate list.
7. **Interference is a hint.** Simultaneous Runs inside one competitor cluster are flagged before firing, never blocked.
8. **Onboarding contract.** ≤ 5 prompts, 60 to 90 s, safe defaults on timeout, reduced-motion means no timer.

## 12. Decisions for Zach

1. Confirm the invariant names (Subject, Target, Candidate, Decision, Run, Counterpart, Correction, Outcome, Lane). They replace the job nouns in code at the second-lane milestone.
2. Second lane to prove isomorphism: sales (leads → ICP → proposal → close) or build (ideas → bet criteria → sprint → retro)? Recommendation: build, because ARCS's own backlog is the stream and the outcomes are already in git.
3. Whether Correction (the five-field record) is required on every close or only on rejections and pivots.
