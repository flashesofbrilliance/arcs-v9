# 02 SOW scaffold: My Ally LD (INTERNAL DRAFT, 2026-10-08)

**Handling.** Internal working draft for Zach. Not a proposal, not priced, not for the counterpart. Built from the Oct 8 intro call (a Granola transcript exists; paraphrased here, no verbatim quotes, treat as INTERNAL), the repo, and the external sources cited below. Nothing in this file has been run through Question Compass or any ARCS surface. The NDA, codebase and build spec have **not** arrived (Gmail search for the three names returned nothing on 2026-10-08), so every item that depends on them is graded accordingly. Where law, privacy, IP or contracts are touched the text says counsel should confirm; no legal conclusion is stated.

## 0. Relationship charter (pre-frame)

**Overarching premise (Zach, 2026-10-08): shared documentation is not shared understanding.** The goal of the engagement is to narrow that gap, so that how Chelsea builds in Lovable and with Claude stays aligned with the reality of the financial projections and the business plan. Evidence status: the premise is Zach's design hypothesis, GRAIN. In the call, the cost model was built separately by Chelsea and Morgan and the AI layer is unbuilt, so the model and the build can drift (T). Zach also described the general two-silo risk, business plan and tech roadmap co-created apart (T, a general remark, not a finding about them). Three instruments carry the premise through the scaffold: (1) **teach-back**: each founder explains the plan, the unit economics and the state of the build in their own words at discovery and again at Phase 1 graduation; the gap is the count of points where explanations differ from each other or from the documents (asm-037); (2) **plan-to-build tether** (F.8): each financial-projection driver is traced to the code or config that sets it; (3) **double-entry reconciliation** (F.5): every plan claim maps to a roadmap item and the reverse.

The charter frames the whole scaffold. It sits **beside** the legal agreement and does not replace it. Anything in it that could read as binding (commitments, exits, handoff duties) is for counsel to confirm before it is shown to anyone. Gate names are **checkpoint**, **graduation** and **soft landing**: framing chosen so a small team reads them as support rather than a trap (see the grades below: that wording preference is our judgment, not a finding). Each phase has exactly three gates, one measurable test each, set in advance and registered before the work starts. One-page template: `05-charter-template.md`.

Per phase the block carries: **Goal** (their words, to be replaced with the founders' own wording at discovery; the lines here are paraphrase); **Deliverables**; **Checkpoint** (a test that says reality mirrors the plan); **Graduation** (what it looks like if it worked and they can run it alone); **Soft landing** (the handoff pack if it did not work, so they lose nothing); **Commitments** (mutual, same kind on each side).

### The four phases (re-cut 2026-10-08 on Zach's sketch; tracks A, F, B are now delivery modes, not phases)

| Phase | Name | Core work | Horizon tag | Delivery mode (Zach's progressive shape, T, his view) |
|---|---|---|---|---|
| 0 | Audit and light discovery | Code, spec, cost model, data-flow map, journey and role map; one session per founder | Now | Advisory-level, Zach alone |
| 1 | Shareback, alignment, co-design of the roadmap | Findings and dependency map; roadmap from priorities, constraints and timing; build-versus-hire receipt and premortem on the fork | Now | Fractional product and technical advisory |
| 2 | Foundational hardening, syncing and alignment of plans | Environment, vendor-agnostic layer, controls, counsel-gated policies, business plan reconciled to the roadmap; the AI build (B.3) when the roadmap places it | Next | Embedded, fixed-term (front-loaded technologist), tapering to fractional |
| 3 | Product strategy, scenario planning, premortem, post-mortem | Strategy and scenarios on real data; premortem on the next big bets; look-back: what we tried to do, what we did, did the outcome match the goal | Later | Light strategic advisory |

Departures from the sketch, for Zach to accept or reject: (1) the premortem on the build-versus-hire fork runs in Phase 1, before spend, because a premortem is only worth its name ex-ante; Phase 3 runs a second one on the next bets. (2) The look-back is a short scoring at the close of every phase (ex-ante charter receipt against reality, ADR-068 close-loop via `.claude/skills/recoil-close/SKILL.md`), with the full post-mortem in Phase 3; waiting for Phase 3 loses what phases 0 to 2 could teach. (3) The AI build (B.3) has no home in the four-phase sketch; default is the tail of Phase 2, gated by the Phase 1 fork receipt and the Phase 2 graduation, so it can move.

### Phase 0: audit and light discovery (worked block, EXAMPLE placeholders)

| Part | Draft content |
|---|---|
| Goal (paraphrase) | Find out what is true about the product, the data and the plans today, before anyone decides anything. |
| Deliverables | Audit findings (code, spec, cost model, data-flow map, journey and role map: P0.A1 to P0.A5); four ex-ante receipts, one per founder (P0.D1 to P0.D4); first counsel question list (L.1). |
| Checkpoint | Test: by [EXAMPLE: date], every spec requirement is tagged built, partial or absent, and no data-flow hop is left unmarked. Set before the audit starts; a miss is said out loud and re-scoped, nobody is blamed. |
| Graduation | Test: [EXAMPLE: all four] founders have filed an ex-ante receipt in the fixed form before seeing each other's. |
| Soft landing | Test: if we stop after Phase 0, the findings pack opens from client-owned storage with no ARCS account (H.2) by [EXAMPLE: date]. They lose nothing. |
| Commitments, us | Share audit findings by [EXAMPLE: date]; keep materials inside the NDA; say early if an estimate moves. |
| Commitments, them | Provide materials by [EXAMPLE: date]; name one decision owner; say early if plans or funding timing move. |

### Phase 1: shareback, alignment, co-design (worked block, EXAMPLE placeholders)

| Part | Draft content |
|---|---|
| Goal (paraphrase) | Agree one time-sequenced roadmap and one decision on how to build, with priorities, constraints and timing on the table. |
| Deliverables | Shareback memo; dependency map; now/next/later roadmap (P1.R1, F.1, F.7); one decision receipt on the build-versus-hire fork and the premortem list (P1.W1); cost baseline filled where sourced. |
| Checkpoint | Test: at shareback, [EXAMPLE: every] node on the dependency map has a named owner and an upstream. |
| Graduation | Test: at workshop close each founder restates, [EXAMPLE: in writing, unprompted], the fork decision, its owner, its reversal condition, and the top premortem failure with its leading indicator. |
| Soft landing | Test: if we stop after Phase 1, the pack (memo, map, roadmap, receipts, premortem, counsel list, cost baseline) opens from client-owned storage with no ARCS account by [EXAMPLE: date]. |
| Commitments, us | Share the shareback memo [EXAMPLE: days] before the session; run the workshop on invented sample decisions until the NDA and Zach's yes allow real material. |
| Commitments, them | Bring priorities, constraints (hours, budget, funding date) and the decision owner; say early if any of them move. |

Same-kind pairs in both: inputs on dated terms; one accountable person; early notice of change.

### Phases 2 and 3 (structure set, content TBD at the Phase 1 workshop)

Each gets the same six-part block, three gates, one measurable test per gate, filed ex-ante. Candidate tests, unmeasured and UNVERIFIED as fit. **Phase 2:** checkpoint = the business plan to roadmap reconciliation (F.5) has no orphan on either side; graduation = Chelsea runs a release, a rollback and a key rotation unaided (B.7); soft landing = runbooks, accounts inventory and decision log in client-owned storage. **Phase 3:** checkpoint = each scenario has a trigger and a pre-agreed response; graduation = the founders run a premortem on the next big decision without us and file it ex-ante; soft landing = the retrospective pack and playbook. Items for Phase 3 are in section 7b.

### Evidence grades for the behavioral claims behind the charter

Relayed from the Docs Reconciliation session's check of 2026-10-08; I did not re-fetch these sources. Claim no more than the grade.

| Claim | Grade | Source (as relayed) | Use in the charter |
|---|---|---|---|
| Minimum targets that trigger a change of course, less threatening negative outcomes, and judging the decision process rather than the outcome were among the most effective ways to reduce escalation of commitment | SUPPORTED, lab setting only; not a study of consulting engagements | Simonson and Staw 1992, Journal of Applied Psychology 77(4):419-426, https://www.gwern.net/doc/psychology/cognitive-bias/sunk-cost/1992-simonson.pdf | Checkpoint = minimum target; soft landing = threat reduction; shareback and workshop = process accountability |
| People demand commitment devices and these can change behavior | SUPPORTED for individuals; transfer to a B2B engagement UNVERIFIED | Bryan, Karlan and Nelson 2010, Annual Review of Economics 2:671-698, https://ideas.repec.org/a/anr/reveco/v2y2010p671-698.html | Why dated, pre-registered gates may help; not shown for a company |
| Stating the worst case makes a small team feel safer committing | CONTESTED; design hypothesis, NOT an established finding. Loss aversion is overstated in places (Gal and Rucker 2018, https://imo.unisg.ch/wp-content/uploads/2020/12/01_jcpy.1156.pdf) yet holds under specific conditions with moderators (Mrkva, Johnson, Gaechter and Herrmann 2020) | as cited | Do not rely on it; soft landing is framed as support, not as a persuasion lever |
| Disclosing to someone raises liking, and people disclose more to those they like; so naming our constraints first may invite theirs | PARTLY SUPPORTED; interpersonal, not business; plausible, not shown | Collins and Miller 1994, https://pubmed.ncbi.nlm.nih.gov/7809308/ | We state our constraints first; no claim it works |
| A four-person team can carry three gates per phase; "kill switch" wording would spook them | UNSUPPORTED, our own judgment | none; stage-gate processes are widely used and Cooper himself calls them time-consuming when heavy (secondary sources only), which supports few, light gates | Cap at three gates per phase, one test each; ask at discovery which wording they prefer |
| A relationship charter improves partnership outcomes | NO EVIDENCE FOUND | none | Treated as a hypothesis with a pre-registered test: asm-028, registered before counting |

## How to read the grades

Evidence codes: **T** = call transcript (internal; paraphrased). **R** = repo asset (path). **X** = external source (URL, fetched 2026-10-08). **U** = unconfirmed.

Fidelity (WORLD.md render scale, never more certainty than the evidence earns):
- **SHARP**: the need is stated on the call or in a primary source AND the way to deliver it is backed by a repo asset or a check we ran.
- **DEGRADED**: one kind of evidence, or a reasoned inference whose inputs we have not seen.
- **GRAIN**: Zach's judgment, a pattern from elsewhere, or anything that waits on materials not received. Shown, but not to be relied on.

Owner: Z = Zach, C = Chelsea, Co = founders as a group, L = counsel (founders' side), TBD = unassigned (flagged). Cost driver: **T** time, **V** vendor/subscription, **K** model tokens, **L** legal/counsel, **O** other. Assumption hooks point at `03-assumptions-draft.jsonl` (asm-015 to asm-030, draft numbering).

## 1. Shape of the engagement

Three directions Chelsea asked to see (advisory, fractional, hands-on build) and the build-versus-hire fork she wants decided. Zach's stated recommendation (T, his view, not a verified fact) is a front-loaded technologist so Chelsea can run the build, then progressive fractional support. Mapped:

| Direction | What it is here | Track | Zach's sequence |
|---|---|---|---|
| Hands-on build | Embedded, fixed-term retainer; configures the environment, builds the load-bearing pieces | B | first, front-loaded |
| Fractional | Product and technical advisory and management; owns sequencing and decisions | F | second, tapering |
| Advisory | Light strategic: sprint planning, review, acceptance testing | A | third, steady state |

Fork options to put in front of the founders at the workshop (names are working labels): **Fork-1** build side by side with a developer; **Fork-2** hire a developer, Chelsea advises; **Fork-3** front-load then taper (Zach's shape). A fourth shape Zach judged less efficient on total cost of ownership (a "vibe coding tutor") is kept as a rejected alternative, GRAIN: the judgment is his, and no cost data supports it yet. The workshop must test it, not assume it.

**Premise correction to carry into the workshop:** Chelsea described herself as a marketing professional who does most of the building. So "who advises whom" is itself a variable: the SOW should not assume a developer is the senior party (T, DEGRADED).

## 2. Phase 0 (audit and light discovery) and Phase 1 (shareback, alignment, co-design)

Order matters: in Phase 0 audit and discovery run in parallel (A items need materials; D items need only the founders); Phase 1 shareback needs both, and the workshop needs shareback. Spend on hardening and build (Phase 2) is released only by the Phase 1 fork receipt: that is the one-way-door discipline (ADR-068 mandatory ex-ante print). Phase 0 spend is the audit and discovery only, with a cap that stays TBD until the cost baseline has inputs.

| ID | Step | Inputs | Output artifact | Acceptance test | Reusable assets | Owner | Cost | Grade (evidence) | Loki attack and disposition |
|---|---|---|---|---|---|---|---|---|---|
| P0.A1 | Codebase review | Repo (not received) | Findings list keyed to file and line | Each finding cites a path; a spec-to-code trace marks every spec requirement built, partial or absent | `.claude/skills/sbom-payload-scan/SKILL.md` (run before installing dependencies from a repo we did not write) | Z | T | GRAIN (T: they will send it; U: not received) | Unowned input: if the repo never arrives the step cannot run. Disposition: Phase 0 exit allows D and W with unverified inputs flagged. asm-022 |
| P0.A2 | Build spec review (20 to 30 pages) | Build spec (not received) | Requirement trace, ambiguity list, candidate "always, sometimes, never" statements for counsel | Every requirement tagged; every always/never candidate has an owner on the counsel list; factual claims are verified in P0.A6, not here | `scripts/assumptions.py` for open questions | Z | T | GRAIN (T) | Vague scope: "review" has no end. Disposition: done when the trace table has no untagged row. asm-022, asm-023 |
| P0.A3 | Token-cost model review | The founders' light/typical/heavy model | Recomputed cost per persona; sensitivity table; gap to the founders' number | Reproduces their figure within a tolerance agreed in advance, or the gap is explained line by line; price inputs carry a source and fetch date | `04-cost-baseline-template.md`; `scripts/token_kaizen.py` as a model of projected-vs-actual | Z with C | T, K | DEGRADED (T: model exists, built by Chelsea and Morgan; U: not seen) | Hidden cost: long uploaded documents drive input tokens; vault size is the swing. Disposition: persona table adds a document-size column. asm-019 |
| P0.A4 | Vendor and data-flow map | Codebase, spec, vendor terms | Table: hop, data class, vendor, retention, agreement status, evidence | Every hop traced to a code path or marked unknown; no hop marked "covered" without a cited agreement | X below (L.4); projection factory idea for the external view | Z, then L | T | DEGRADED (T: stack named by Chelsea; X: vendor docs) | A risk with no mitigation: if a hop is unknown at shareback it becomes a counsel question, never a guess. asm-015 |
| P0.A5 | Journey and role map reverse-engineered from the existing front end | Running app (test accounts, synthetic data only), build spec | User segments (parent, child, practitioner such as an OT, others found), journeys per spoke (vault, A-team directory, strengths questionnaire, opportunities, checklist and dashboard), role and permission matrix as-built vs needed, draft user stories | Every screen maps to a journey and a role; every access rule is stated or marked missing; founders confirm or correct the draft at discovery | `07-probability-bar` and `08-receipt-table` for presentation; `scripts/assumptions.py` for open questions | Z with C | T | GRAIN (T: front end works; U: whether stories, journeys or access rules already exist) | Falsifier: if the spec already holds journeys and role rules, this step shrinks to a reconciliation. asm-033 |
| P0.A6 | Adversarial claim audit of the build spec (and any plan document): confidence of tone is not evidence | Build spec (not received); codebase; primary sources for outside facts | Claims register: id, claim, type (fact about their own code, fact about the outside world such as law, vendor terms, prices and versions, forecast, design intent), evidence, verdict (verified, contradicted, unverifiable); an unchallenged-plans list (plans with no rejected alternative, stated risk or falsifier); a steelman pass listing what holds up | Every factual claim has a verdict and a citation to a code path or primary source; none is marked verified on a document's say-so; a second reader re-verifies a sample agreed in advance and the verdicts match; contradicted and unverifiable are kept apart | `claims-skeptic` agent type (adversarial verifier of factual claims against live sources); `scripts/provenance_lint.py` (facts), `scripts/slop_lint.py` (style); manual citation checks, never trust a subagent's citation unchecked | Z | T, K | GRAIN (T: Chelsea said she used Lovable's AI and Claude's AI to build; U: how the spec was drafted, who challenged it) | Framing risk: it can read as an accusation. Disposition: the same register standard is applied to our own documents, this scaffold included, and provenance is asked neutrally at discovery. Gate: running their spec through an AI verifier is a vendor hop; after the NDA and their consent only (question 12). Pessimism guard: the steelman pass hunts good evidence as hard as bad. asm-040, asm-041 |
| P0.D1 | Discovery: Leah (founder) | Founder session | Ex-ante receipt in the fixed form (question, horizon, stakes, mode, confirmed, unconfirmed) filed before shareback | Receipt complete; filed before the founder sees any other founder's receipt | `.claude/skills/recoil-new/SKILL.md` (local SSOT), fixed form in AGENTS.md "Receipts" | Z | T | DEGRADED (T: Zach offered a round with all four) | Hidden cost: Leah was not on the call, so her view of build-versus-hire is unknown, and she holds the budget decision (T, inference). asm-020 |
| P0.D2 | Discovery: Morgan | Founder session | Same | Same | Same | Z | T | DEGRADED | Morgan co-built the cost model (T); role otherwise unknown. Disposition: ask. |
| P0.D3 | Discovery: Kelly | Founder session | Same | Same | Same | Z | T | DEGRADED | Kelly named empathy-without-health-advice as the hard problem and wrote the business plan (T); her receipt anchors A.3 and F.5. |
| P0.D4 | Discovery: Chelsea | Founder session | Same, plus neutral provenance questions on the spec: how it was drafted (by hand, AI-assisted), who reviewed it, which plans were challenged or rejected, and when each section was written relative to the code | Same | Same | Z | T | DEGRADED | She is both the builder and the party deciding who advises her (see premise correction). Provenance is asked as a process question, never as a charge. |

**Phase 0 exit (stop-loss).** If materials have not arrived by the first review date, run discovery only and mark every audit output UNVERIFIED. If the founders cannot name a decision owner at D1, Phase 1 is postponed (a decision with no owner is not a decision).

### Phase 1 steps

| ID | Step | Inputs | Output artifact | Acceptance test | Reusable assets | Owner | Cost | Grade (evidence) | Loki attack and disposition |
|---|---|---|---|---|---|---|---|---|---|
| P1.S1 | Shareback: findings and dependency map | P0.A1 to P0.A5, P0.D1 to P0.D4 | Findings memo; dependency map (sequential vs parallel; critical path; counsel-gated nodes) | Every node has an owner and an upstream; the map reconciles to the business plan's dates (the funding plan expects a start of next year, T) | Night-moves digest section 6 (dependency map) as the form; `10-pipeline-stage-tracker.html`; `scripts/reconcile_epoch.py` | Z | T | DEGRADED | Unowned dependency: counsel's answer times are outside anyone's control here. Disposition: map shows counsel nodes as gates with an external clock. asm-016, asm-025 |
| P1.R1 | Roadmap co-design: a now/next/later roadmap built with the founders from their priorities, constraints and timing | Shareback; the founders' stated priorities, hours, budget and funding date; counsel gates from the map | A time-sequenced roadmap across the five spokes (produces the F.1 backlog and the F.7 spoke order); the order criterion in writing | Each item has an owner, an upstream, a counsel gate and a phase; the founders sign off the order criterion; the first release is one thin path | `10-pipeline-stage-tracker.html`, `13-90day-build.html` retitled; `.claude/skills/fold/SKILL.md` for splitting dense work | Z with Co | T | GRAIN (T: Kelly mentioned an informal priority and beta-test idea; the sequence itself is unseen) | Falsifier: a dated, dependency-ordered sequence already exists (asm-034). Unowned input: priorities and constraints must come from the founders, not us. |
| P1.W1 | Decision receipt workshop and premortem on the build-versus-hire fork | Shareback; four receipts; invented sample decisions for the demo | One decision receipt on the fork; premortem list (failure story, leading indicator, mitigation, owner) | Receipt in the fixed form; each founder contributes a failure story; each failure story has a leading indicator and an owner; the rejected-alternative test of Fork-3 is run | Question Compass (`src/app/dashboard/page.tsx`, `src/app/api/compass/route.ts`) with INVENTED decisions only; LAB/BAR/Loki as method (`operators/`); `counterpart-gauntlet` to pre-test the deck | Z facilitates, Co decide | T | DEGRADED (T: offered on the call; R: compass exists) | Gate: no prospect material in the compass until NDA and Zach's yes (src/app/privacy terms govern stored receipts); fallback is a local SSOT file. asm-027 |

**Phase 1 exit (stop-loss).** Spend on Phase 2 hardening and any build is released only by the fork receipt. If the founders will not decide, stop at the soft landing pack: the pack is the product.

## 3. Track A: Advisory (light strategic support)

| ID | Item and deliverable | Acceptance test | Depends on | Owner | Cost | Assump | Grade (evidence) | Loki |
|---|---|---|---|---|---|---|---|---|
| A.1 | Sprint planning cadence: backlog groomed, sprint goal set | Each sprint has a written goal, a done-test per item, and a stated capacity | F.1 | Z with C | T | asm-025 | DEGRADED (T) | Vague scope until capacity is known. Capacity of four people with other jobs is U. |
| A.2 | Sprint review and decision receipts for one-way doors as they arise (vendor, retention period, pricing) | Each one-way-door decision has a receipt before commit (write-lock) | P1.W1 | Z with Co | T | asm-016, asm-017 | SHARP (T: fork named; R: WRITE-LOCK primitive, AGENTS.md receipts) | Risk: receipts logged after the fact lose their value; keep them ex-ante. |
| A.3 | Acceptance testing: scripted boundary set for "empathetic, no health advice" plus functional checks | A scored set agreed with counsel; pass threshold written before building; reruns on every model change | L.1, B.3 | Z, L, Kelly | T, L | asm-024 | DEGRADED (T: requirement stated by Kelly; U: no spec of the boundary) | Falsifier: if counsel cannot define the boundary precisely, the test is a judgment call; then the deliverable is a counsel-signed rubric, not a pass rate. |

## 4. Track F: Fractional product and technical advisory and management

| ID | Item and deliverable | Acceptance test | Depends on | Owner | Cost | Assump | Grade (evidence) | Loki |
|---|---|---|---|---|---|---|---|---|
| F.1 | Backlog built from the build spec, sequenced by dependency (what is always, sometimes, never, settled with counsel first) | Every item has an upstream and an owner; counsel-gated items are marked | P1.S1 | Z with C | T | asm-022, asm-023 | DEGRADED (T: Zach's method; U: spec unseen) | Unowned dependency: counsel timing. Shown on the map as an external clock. |
| F.2 | Architecture decisions recorded: vendor-agnostic model layer, role-based access for parents, children, practitioners, extensibility | One ADR per decision; each names the one-way doors | P0.A4 | Z | T | asm-017 | DEGRADED (T: Zach's recommendation) | Gold-plating risk for a four-person pre-launch company; cap at what the first cohort needs. |
| F.3 | Model vendor decision support: criteria, evidence, switch-cost, receipt | A receipt with the data-handling terms attached and counsel's input; swap test passes | L.2, L.4, B.2 | Z, Co | T, L | asm-016, asm-017 | DEGRADED (T: Anthropic vs OpenAI open, BAA a concern; X: Anthropic doc) | The receipt must record that the data-handling terms, not model quality, drive the one-way door. |
| F.4 | Unit economics and token caps: per-user caps, spend alerts, price-point scenarios (light, typical, heavy; long-term user counts from their model) | Cost per persona with a source and fetch date per price input; cap enforced in code and tested | P0.A3, B.6 | Z with C | T, K | asm-019 | DEGRADED (T: model exists) | Hidden cost: web-search calls and file processing are not tokens; add to the model. |
| F.5 | Business plan to tech roadmap reconciliation, stated versus revealed, kept like double-entry: every plan claim maps to a roadmap item and the reverse | A reconciliation table with no orphan on either side; reviewed at each shareback | P1.S1 | Z with Kelly | T | asm-025 | DEGRADED (T) | Falsifier: if the plan has no claim a roadmap item could contradict, the plan is too vague to reconcile. |
| F.6 | Accessibility requirements: which standard and level, who verifies | A named standard and level confirmed with counsel; a check run on each release | L.1 | Z, L | T | none yet | GRAIN (T: Zach raised it; U: which standard applies) | Hidden cost: remediation after build. Disposition: decide the standard before B.5. |
| F.7 | Spoke sequencing: a time-sequenced roadmap across the five spokes, with a stated order criterion (risk of data handled, value to the first cohort, dependency, legal gate) | Each spoke has a start window, an upstream and a counsel gate; the first release is one thin path, not five | P0.A5, P1.S1 | Z with Co | T | asm-034 | GRAIN (T: five services described by Chelsea; informal priority and beta-test idea mentioned by Kelly; the missing sequence is Zach's reading, not stated by them) | Candidate criterion, untested: lower-data-risk spokes first, vault plus Alice behind the counsel gates. The founders may reasonably want the AI first; the workshop decides, not us. |
| F.8 | Plan-to-build tether: a trace from each financial-projection driver (users per persona, sessions, tokens per call, model choice, vault document size, caps, price points) to the code or config that sets it and to the person who can change it | Every driver has a code location or is marked unset; a driver change made on a test branch is caught by the review checklist and triggers a cost-model update by its owner | P1.S1, P0.A3 | Z with C | T | asm-038 | GRAIN (T: cost model built separately from the build; U: how the code sets those drivers) | Falsifier: if the drivers live in one config file the founders already review, the tether is a checklist line, not a deliverable. Risk: vibe-coded changes (a model swap, more context stuffed in) move the cost silently. |

## 5. Track B: Hands-on build (front-loaded)

| ID | Item and deliverable | Acceptance test | Depends on | Owner | Cost | Assump | Grade (evidence) | Loki |
|---|---|---|---|---|---|---|---|---|
| B.1 | Environment ready for Chelsea to run the build: repo, branches, environments, secrets handling, CI, test data (synthetic only) | Chelsea ships one backlog item end to end with Zach reviewing only; blocking interventions counted | P0.A1 | Z | T | asm-021 | DEGRADED (T: Zach's stated plan; U: current state of their setup) | Falsifier in asm-021. Risk: real children's records in test data; synthetic only, stated in the acceptance test. |
| B.2 | Model-agnostic wrapper plus model version pin and freeze window (the spec already names a freeze window) | A fixed set of synthetic prompts through two vendors; only wrapper config changes; pin enforced | F.2 | Z or hire | T | asm-017 | DEGRADED (T: Zach's view; T: spec has a freeze window) | Claim "agnostic" is falsifiable by the swap test; until run it is a design intention. |
| B.3 | AI integration for Alice (not started): retrieval over the vault, voice and boundary layer, provider calls via B.2 | Passes the A.3 set at the agreed threshold; no vault content leaves the allowed path in A4's map | P1.W1, P1.R1, A.3, B.2, B.4, F.8 | C with Z | T, K | asm-024 | GRAIN (T: unstarted; U: spec details) | The largest unknown in the engagement; do not estimate until A2 has read the voice spec. Zach's hunch (asm-039): integration before product planning and discovery prework is premature. Counter-consideration: the funding story may need a visible Alice; a bounded spike on synthetic data (section 11) buys real token numbers for the cost model without committing to integration. |
| B.4 | Redaction design: deterministic pass for structured identifiers plus a parent-review step; a measured recall figure on a synthetic IEP set | Recall reported by identifier type; the review step is mandatory in the UI; counsel signs off the residual risk | L.3 | Z with C | T | asm-018 | DEGRADED (T: Chelsea's requirement that redaction not depend on the AI; Zach prefers deterministic scripts; R: none) | Loki: deterministic rules miss names and context in prose, so "deterministic" alone cannot meet Chelsea's requirement. Review step added. Needs a synthetic-IEP generator (gap 4 in file 01). |
| B.5 | Role-based access: parents, children, practitioners | Role matrix reviewed by counsel; tests show each role sees only its data | F.2, L.6 | Z or hire | T | none yet | DEGRADED (T) | Child accounts are a counsel gate (L.6). |
| B.6 | Audit log and spend caps | Log entries exist for vault reads and model calls; a cap trips in a test | B.2 | Z or hire | T | asm-023 | DEGRADED (T: audit log in the spec; U: not built) | asm-023 says the spec lists intentions, not controls; check before promising. |
| B.7 | Handover: Chelsea runs a release, a rollback and a key rotation unaided | Dry run with Zach silent; checklist signed | H.1 | C | T | asm-021 | DEGRADED | |

## 6. Legal, privacy and security table stakes

Counsel should confirm every row. Zach is not giving legal advice; the SOW must say so. Rows are things to schedule, not conclusions.

| ID | Item | Acceptance test | Evidence and notes | Grade | Loki |
|---|---|---|---|---|---|
| L.1 | One consolidated, ranked counsel question list (the consultant and Leah's outside counsel already hold a long one) | Ranked; each question tagged blocks-build, blocks-launch, or later; answers dated | T: two lawyers consulted, long list exists | DEGRADED | Unowned until named. Owner: Leah or her counsel (TBD). |
| L.2 | Applicability determination: which regimes apply to which data class (HIPAA, COPPA, state laws, others counsel names) | A written answer per data class | X: HHS developer guidance says a consumer-populated app is not a business associate, a developer working on behalf of a covered entity is; depends on facts (https://www.wsgrdataadvisor.com/2016/06/hhs-issues-hipaa-guidance-for-mobile-health-apps/, secondary summary of HHS OCR guidance). Zach cited HIPAA, COPPA and a BAA on the call; applicability is for counsel. | DEGRADED | Do not repeat any liability figure; Zach's recollection of one on the call is unverified and is not in this file. |
| L.3 | Data minimization and retention policy for children's information | A retention period per data class, decided and enforced in code | X: the amended FTC COPPA Rule took effect June 23, 2025 with a compliance date of April 22, 2026 and a limit on retaining children's personal information (https://www.dwt.com/blogs/privacy--security-law-blog/2025/05/coppa-rule-ftc-amended-childrens-privacy, summary of the Federal Register notice). Whether the product is covered is for counsel. | DEGRADED | |
| L.4 | Vendor agreements per hop of the A4 map | Each hop shows agreement status with evidence | X (primary): Anthropic documents HIPAA-ready API access with a standard BAA enabled in the Console, feature eligibility limits (beta features generally not covered, Claude Code not covered), and ZDR as a separate arrangement (https://platform.claude.com/docs/en/manage-claude/api-and-data-retention). X (primary): Lovable's terms prohibit submitting HIPAA-protected health information or other sensitive categories through its services, with a carve-out only where a separate written agreement exists (https://lovable.dev/terms). X: Supabase's HIPAA page was fetched but did not state plan eligibility; secondary sources say a HIPAA add-on exists for higher plans, **unconfirmed** (https://supabase.com/docs/guides/security/hipaa-compliance). OpenAI's terms were not fetched: U. | DEGRADED | The Lovable finding matters: the build tool's terms may bear on how IEP-like data is handled during development and testing. Counsel confirms which services actually touch data (A4). |
| L.5 | Audit trail and model-freeze evidence | Controls exist and are exercised (see B.6, asm-023) | T: written into the spec; R: none | GRAIN | |
| L.6 | Parent and child consent flows, terms, privacy policy | Counsel-approved text live before any external user | T: child data acknowledged; U | GRAIN | Today only the four founders use it; the first external user is the trigger. |
| L.7 | Security basics: MFA, least privilege, secrets, backups, dependency scanning | A checklist run once and on each release | R: `.claude/skills/sbom-payload-scan/SKILL.md`; U for their current state | DEGRADED | Pen test timing TBD, not estimated. |
| L.8 | Breach and incident response SOP | A tabletop run once; contacts and decision owners named | R: pattern in `.claude/commands/rca.md`; U | GRAIN | |
| L.9 | Our engagement terms: NDA, IP assignment for work product, liability and no-legal-advice language, data handling for their materials | Reviewed by counsel on both sides | T: NDA to be sent by them | GRAIN | Whose paper and which entity pays: open question 1. |

## 7. SOP and handover

| ID | Item | Acceptance test | Grade |
|---|---|---|---|
| H.1 | Runbooks: deploy, rollback, key rotation, vendor outage | Chelsea executes each from the page alone | DEGRADED |
| H.2 | Decision log exported to client-owned storage (receipts, ADRs, premortem) | Client can open it without any ARCS account | DEGRADED (R: receipt form; the export format is TBD) |
| H.3 | Accounts and subscriptions inventory with a named owner each | Every recurring charge has an owner and a renewal date | GRAIN (U: which vendors sit on a card today) |
| H.4 | Enablement sessions, recorded only with consent | Consent logged first | GRAIN (see recording question) |
| H.5 | Exit criteria per track and stop-loss per phase | Written before the track starts | SHARP (R: `09-stop-loss-footer.html`, ADR-068) |

## 7b. Phase 3 items: product strategy, scenario planning, premortem, post-mortem

| ID | Item | Acceptance test | Evidence and assets | Grade |
|---|---|---|---|---|
| P3.1 | Product strategy on real data: what to double down on, drop or rent (build versus rent, owned IP versus platform), using beta results | A written strategy with the rejected options and why; each claim cites beta data or is marked a bet (section 11) | T: Zach raised owned IP and build-versus-rent on the call; no beta data exists yet | GRAIN |
| P3.2 | Scenario planning: a small set of futures (funding, regulation, vendor change, adoption), each with a trigger and a pre-agreed response | Each scenario has an observable trigger and an owner | R: `operators/arcs_operators_bar.py` (ruin framing) as method; no scenario asset in the repo | GRAIN |
| P3.3 | Premortem on the next big bets | Filed ex-ante; each failure story has a leading indicator, mitigation and owner | Same method as P1.W1; asm-035 | GRAIN |
| P3.4 | Post-mortem: for every phase and bet, what we tried to do, what we did, and whether the outcome matched the goal | Every ex-ante charter receipt and bet card is scored aligned, diverged or unresolved, with the reason; confidence vs outcome recorded (asm-032) | R: `.claude/skills/recoil-close/SKILL.md` scoring pattern, ADR-068 close-loop; a short version runs at each phase close (asm-036) | DEGRADED |

## 8. Cost-baseline hook

Every item above carries a cost driver code (T, V, K, L, O). `04-cost-baseline-template.md` turns the codes into fixed, variable and hidden lines under best, base and worst. No price, rate or term exists yet. The rates Zach floated on the call were a negotiating signal, not a quote, and are deliberately not recorded here.

## 9. Loki log (what was cut or demoted)

- **Cut:** any statement that HIPAA, COPPA or a BAA applies or is required. Replaced by the L.2 determination.
- **Cut:** the liability figure Zach recalled on the call. Unverified; excluded.
- **Cut:** nonprofit infrastructure pricing; the company is for-profit (T), so it is out of scope.
- **Demoted to GRAIN:** the "vibe coding tutor" cost judgment, B.3 estimate, F.6 standard, L.5, L.6, L.8, L.9, H.3, H.4.
- **Changed:** "deterministic redaction" became "deterministic pass plus mandatory parent review" after the Loki test (B.4).
- **Added:** premise correction (Chelsea is the builder, not a developer), Lovable terms issue (L.4).
- **Added (addendum 2026-10-08, relayed from another session, not typed by the user):** section 0 charter wrapper, evidence grades, `05-charter-template.md`, assumptions asm-028 to asm-030. Gate count capped at three per phase.
- **Not run:** premortem on this scaffold itself with a second reader; the `counterpart-gauntlet` workflow was not run (multi-agent cost; Zach's call).
- **Falsifier for the scaffold as a whole:** if the codebase shows the AI layer is further along than the founders described, B.3 and the cost model change first.

## 10. Open questions for Zach

1. Whose entity pays and signs, and on whose paper (founders' NDA, or ours)?
2. Which vendors are on a card today (needed for H.3 and the cost baseline)?
3. Is cost visibility an engagement outcome (dashboards, alerts) or only a finding?
4. Disclose the recording: on the call you said you record only after an NDA and explicit consent, yet a transcript exists. Tell them, and decide whether the transcript is kept, before it feeds anything counterpart-facing.
5. NDA status: not received as of 2026-10-08; codebase and build spec also not received.
6. "By manana" in your framing is unclear and is not read as a duration. What did you mean?
7. May the Phase 1 workshop use Question Compass on their real material after the NDA, or do you want a local SSOT only?
8. Charter: which gate wording do the founders prefer (checkpoint, graduation, soft landing, or other)? Counsel should confirm anything in the charter that could read as binding before it is shown.
9. Learning loops (section 11): who states the confidence forecasts before each bet, and what is the founders' runway, so the sum of bet caps can be checked against it? (Runway is also a finance intake field.)

## 11. Validated learning loops: every bet is a falsifiable forecast with a cap

Purpose: avoid opportunity-cost ruin and learning on your own dime. A bet is anything we do not yet know will work (a plan item, a vendor, a timeline). Each bet gets the same five questions **before** work starts, filed ex-ante (write-locked) in the decision log. The cheapest test that could kill the bet runs first (cheap tripwire before expensive work).

**The five questions (bet card: `06-bet-card-template.md`):**
1. **Confidence:** how confident are you that you can complete this in this timeframe with this budget? Stated by the owner as a forecast **before** the work, not by us; blank until elicited. No number is supplied in this draft.
2. **Timebox and cap:** the time and cash ceiling for the bet. Both `TBD` until the cost baseline has inputs. Rule: a failed bet must not be ruinous, so the sum of the caps of bets that can fail together stays below runway (runway comes from the founders; BAR logic, `operators/arcs_operators_bar.py`).
3. **Pass criterion:** one measurable test, set in advance.
4. **Fail criterion:** one measurable test that is not simply "not pass" (a middle band is named, which triggers re-scope, not stop).
5. **Ramifications, both outcomes, named for both sides:** lost time, velocity, focus, frustration, cash, trust, and option value (what we can no longer do because we spent here). Who bears each. A fail that falls on the client's own dime needs their prior yes.

**Why this protects the engagement.** The Simonson and Staw grades in section 0 apply: minimum targets that trigger a change of course and judging the process rather than the outcome were among the most effective ways to reduce escalation of commitment, lab setting only. Honest limit: calibration cannot be shown in one engagement. The Accountant (Op 19, `operators/arcs_accountant.py`) reports calibration only at 30 or more closed positions per cohort and otherwise says `sufficiency=insufficient`; we will record confidence and outcome per bet and say so, without claiming more (asm-032).

| Bet | Linked | Cheapest falsifier, run first | Pass | Fail (and middle band) | Ramification if it fails, and who bears it |
|---|---|---|---|---|---|
| Materials fit a single review pass | P0.A1, A2; asm-022 | Skim the codebase and spec against a timebox before committing the full audit | Spec-to-code trace table has no untagged row inside the box | Untagged rows remain: re-scope the audit, name what is deferred | Time and focus on us; a late shareback delays the founders' decision (client velocity) |
| The cost model survives recomputation | P0.A3; asm-019 | Recompute one persona from the spec's call pattern and a dated price page | Gap inside the tolerance agreed in advance | Gap outside it: model rebuilt before any pricing talk | Cash planning error falls on the founders; trust cost on us if we sized from a wrong model |
| Vendor swap is cheap | B.2; asm-017 | Swap test through the wrapper with a fixed prompt set | Only wrapper config changes | More changes: the decision is a harder one-way door and goes back to the workshop | Rework time on the builder; a locked-in vendor is option value lost |
| Redaction meets Chelsea's requirement | B.4; asm-018 | Recall test on a synthetic IEP set by identifier type | Recall acceptable to counsel with the review step | Misses on names stay high: review step becomes the control, UI burden on parents | Frustration for parents and Chelsea; legal exposure is for counsel to size |
| Chelsea can run the build after front-loading | B.1, B.7; asm-021 | One backlog item shipped with Zach reviewing only | Few blocking interventions (threshold set ex-ante) | Many interventions: switch toward Fork-2 or extend Phase 1 | Frustration and velocity loss for Chelsea; cost overrun on the retainer, shared by both |
| Empathy without health advice is scorable | A.3; asm-024 | Counsel marks a small boundary set before any build | Counsel can state the boundary precisely | Counsel cannot: deliverable becomes a counsel-signed rubric, not a pass rate | Build rework on the AI layer; focus drain on Kelly and counsel |
| Pilot by start of next year | asm-025 | Size the backlog in weeks against Chelsea's hours and ours | Critical path fits the window | It does not: cut scope or move the date at the checkpoint, decided ex-ante | Missed funding story, founder morale; our reputation |
| Counsel answers arrive in time | L.1, L.2; asm-016 | Ask counsel for dates for the blocks-build questions in the first week | Dates committed | No dates: counsel nodes are drawn as an external clock and work behind them is not started | Idle time on whoever waits; spend ahead of an answer is the risk we refuse |
| Fork-3 is the lowest total cost of ownership | P1.W1; asm-031 | Cost Fork-1, Fork-2 and Fork-3 side by side with the same case definitions | Fork-3 lowest in the base case | Not lowest: recommend the cheaper fork, say so plainly | Credibility on us; wrong pick costs the founders cash and months |
| A bounded Alice spike on synthetic data teaches more about cost and voice than it costs | B.3, F.8; asm-039 | Run one persona's synthetic session through the model behind the B.2 wrapper inside a timebox | Real token counts per call recorded in the cost model; voice notes captured | Cap hit with no usable numbers: stop, no integration work follows | Time on the builder; risk that a demo is mistaken for a commitment to integrate; no child data used |

**Ruin tests for the whole engagement (checked at each checkpoint):** (a) could any single failed bet end the project, by cash, runway, or a founder walking away? (b) is any bet's cost landing on the client without their prior yes? (c) is the loss we are about to take larger than the lesson it buys? If yes to (a) or (b), or no to (c), stop and re-scope before spending (soft landing).
10. Phases: accept the three departures from your four-phase sketch (premortem on the fork in Phase 1 plus one in Phase 3; a look-back at every phase close; the AI build placed at the tail of Phase 2 by default)?
11. Spike: may a time-boxed Alice spike on synthetic data run in Phase 1, to give the cost model real token numbers, while full integration stays gated to Phase 2?
12. Spec verification: after the NDA, do you want their build spec run through an AI claim-verifier (a vendor hop), or checked by hand only? Either way, ask how it was drafted and challenged, neutrally, at discovery.
