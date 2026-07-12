# Operator 20 Archaeological Excavation — 2026-07-11

> **Mode:** Relic Archaeology / Canon Recovery / Product Primitive Extraction
> **Authority:** God-mode exploration; HUMAN WRITE-LOCK required for every promotion below.
> **Status:** REPORT — nothing in this document mutates canon, receipts, or ROM. All dispositions are recommendations.
> **Method:** Full-corpus census (repo tree, _CANON, _DECISIONS, _PATTERNS, operators, runtime/specs, scripts, src, public, _STATE, _QUEUE), triune pass (NULL/OM/IDEA) per relic family, live verification where possible (git, grep, Supabase CLI link confirmed; direct row-count query unavailable — no psql, no local DATABASE_URL).
> **Key live facts grounding this report:**
> - Receipts recorded at **184** in `_QUEUE/PENDING.md` (reconciled ~2026-06-25, PR #20); not re-verified live this session. `Receipt_pkey` shows 3,678 index scans (active production use); `Outcome_pkey` shows **3** (outcome loop essentially unused).
> - ADR-025a's 30-day go-live review window lands **~2026-07-12 — tomorrow**.
> - ADR-020's 50-receipt trigger has **cleared**; ADR-023's gate is a *measurement* (Gini/Zipf baseline) that has **never been run** despite the count being satisfied.

---

# 1. Archaeological Map

Nine relic families found. Per-family verdict in one line each.

| Family | Contents | Verdict |
|---|---|---|
| **Foundational doctrine** | WORLD.md · Book II Parts I–VI (canonical) · trust-contract v1.1 (live at `/trust`) · ROM primitives (NOTOMATION, Kintsugi, write-lock, Golden Inchworm, Orthogonal Echo) · `_CANON/living/*` | Healthiest family. Already governed. One doc-vs-code enum drift (see Collision #2). |
| **Live product loop** | Compass → Receipt → Brief → (Debrief) · PrepSession · tributaries · Y-gate (`src/lib/ygate.ts`) · DEWY schema v1 (Prisma-wired) | The load-bearing spine. ~184 real receipts. Outcome/recoil half of the loop is built but **nearly unused** (3 index scans on Outcome). |
| **Engagement/pilot artifacts** | 13 live call briefs on `[name].arcs.care` · two-tier ledger (`runtime/recoil/generated/` internal + `public/*.html` external) · `receipt_lookup.py` Detective · recoil-modes v1 · call-brief-hooks v1 (both DRAFT) | **The only family with A-grade revenue-adjacent evidence** (Todd $1,500 proposal, Kelly, LaBella, Fanatics). Its two governing specs are still DRAFT. |
| **Governance protocols** | 31 ADRs + index.json + `_QUEUE` auto-workflow · pathogen taxonomy (10 named, each with a real instance) · dual-bar-raiser · 5D/5W/5C/5R/5H rubric · handoff system (3 overlapping logs) | Strong bones, zero mechanical enforcement (per the 2026-06-23 audit: 0 of 6 SKILL.md rules enforced). The 3-log drift problem is the family's chronic disease. |
| **Operators (Python)** | 34 files / 16.6K LOC (`operators/`) + `operators/core/` foundation layer + RC registry | Claims "production-ready canonical." Reality: zero integration with the compass route, 12/34 files import numpy/scipy against the README's own "stdlib-only" claim, README annotates its own files with "?" (CIS, Yoav Store). Reference implementation, mislabeled. |
| **UI/visual systems** | `src/ui` typed DS (22 atoms, ADR-031) · compass-kit (static reference) · recoil-report ui-kit (13 HTML atoms + `_tokens.css`, 5 shipped instances) · document registry (5 doc types × 10 patterns) · instrument/molecules/organisms | Four parallel atomic-design systems that have never been reconciled under one taxonomy. ADR-031 (extend `src/ui/`) is the decided path; Phase 2 not started. |
| **Observability/analysis** | Observatory page (live) + provenance ledger (P## methods) · `build_observatory.py` · `lattice_sim.py` · Folksonomist (`arcs_core.py`) · scan suite (6 scanners) | Real machinery, correctly gated — but the gate condition (corpus baseline) is now *measurable* and nobody has measured it. |
| **Mythic/experimental language** | Periodic Table v3.0 (53 elements, quark "equations") · Vector Collision Engine v1/v2 · Phase-Change Thesis · YellowPaper (68%→87%, $350B, blockchain receipts) · 12D kinematics D5–D12 | Metaphor density highest here; evidence density lowest. The kinematics adjudication (2026-06-24) is the model precedent: D5–D10 formally ruled numerically noise. Apply that discipline family-wide. |
| **Dead/duplicate branches** | `archive/specs` · unreachable arcs-care PLG code · orphaned Supabase tables (`meeting_cards` etc., no owning app) · static `public/observatory` demo (superseded by real page) · root `SESSION-HANDOFF-2026-05-26.md` · stale `/Users/zharris/arcs` clone | Everything here is already known-dead; the cost is that it still *reads* as alive to a cold session. Needs explicit ARCHIVED markers, not deletion. |

---

# 2. Relic Registry — 25 highest-leverage relics, ranked

Columns: **Ev** = evidence grade (A live-verified / B documented+partially verified / C internal docs only / S speculative) · **Rel** = current relevance 1–5 · **Mass** = cognitive mass 1–5 (higher = heavier) · **Lev** = product leverage 1–5.

| # | Relic | Source / lineage | Atomic kernel (plain language) | Ev | Rel | Mass | Lev | Disposition — reason | Next test |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Call-brief pattern + two-tier ledger | `public/*.html` ×13 · `runtime/specs/call-brief-hooks-v1.md` · `_tokens.css` kit | A shared, password-gated terrain page per counterpart; candid internal ledger never auto-leaks to the external page | **A** | 5 | 2 | 5 | **ROM candidate** — only relic with live revenue conversations attached | Ratify hooks spec DRAFT→ROM (write-lock Q1 below) |
| R02 | Compass→Receipt→Brief loop | `src/app/api/compass/route.ts` + live app, ~184 receipts | Question in → positioned bearing + frozen receipt out; system never decides, only maps | **A** | 5 | 3 | 5 | **ROM (de facto)** — formalize what's already load-bearing | Close the Outcome half (3 scans ≈ unused) |
| R03 | DEWY receipt schema v1 | `runtime/specs/dewy-receipt-schema-v1.{json,md}`, Prisma-wired | One decision = one D/E/W/Y coordinate frozen in time | **A** | 5 | 2 | 4 | **ROM promotion** — front-matter still says REVIEW | Validate all live receipts against the JSON schema; count violations |
| R04 | Y-gate engine | `src/lib/ygate.ts` | Polarity × conviction × stability → navigation state → render fidelity | **A** | 5 | 2 | 4 | **ROM promotion** — after fixing doc/code enum drift (Collision #2) | Query live y_state distribution |
| R05 | Pathogen taxonomy (10 pathogens) | `_PATTERNS/2026-06-23-governance-roadmap.md` | Every drift instance gets a name, a category, and a visible repair seam | **A** | 4 | 2 | 4 | **ROM candidate** — every pathogen has ≥1 real caught instance | Classify next session's findings against it; measure coverage |
| R06 | ADR + _QUEUE lifecycle | `_DECISIONS/` ×31 · `adr-queue.yml` | Decisions are receipts with status, gate, and pickup notes | **A** | 4 | 2 | 4 | **ROM candidate** — needs the closing-ceremony fix (`Closes: ADR-XXX` trailer) to stop PHANTOM_OPEN_ITEMs | 30-min: commit-msg regex hook |
| R07 | `receipt_lookup.py` Detective | `scripts/receipt_lookup.py`, hooks spec §Detective | Before spending call time, query prior history with this person | B | 5 | 1 | 4 | **RAM** — exists, referenced, thin usage history | Run against all 13 briefs; grade advisory quality |
| R08 | Recoil modes v1 (reverse listening + deep recall) | `runtime/specs/recoil-modes-v1.md` (DRAFT) | Read transcripts end-to-start first so outcomes can't rationalize weak moments | B | 4 | 2 | 4 | **RAM** — used on real calls (LaBella), spec unratified | Apply to next 2 transcripts; then court |
| R09 | Tributaries 3-type contract | compass output: meta/challenge/adjacent | Every answer ships with the deeper question, the uncomfortable one, and the reframe | **A** | 4 | 1 | 4 | **ROM candidate** — the contract, not the unbuilt ATG engine | Count tributary click-throughs (nested threads, ADR-030) |
| R10 | PrepSession calibration | `/api/prep`, live | Five fields, two minutes, richer compass context | **A** | 4 | 1 | 3 | **RAM** — live and stable; promote with R02 | Measure prep-vs-no-prep NCI delta |
| R11 | JTBD four-surface map (Calibrate→Orient→Chart→Detect) | `runtime/specs/field-os/jtbd/jtbd-master-map.md` | Four sequential jobs; receipts feed the next cycle's questions | B | 4 | 2 | 4 | **RAM** — governing frame; Calibrate + Detect surfaces unbuilt | Keep as frame; do not cite as shipped |
| R12 | `src/ui` typed DS + ADR-031 | 22 atoms, tokens.ts | One palette, direct imports, no barrel, extend-don't-fork | **A** | 4 | 2 | 4 | **RAM** — decision made, Phase 2 not started | Execute Phase 2 per `_STATE/compass-kit-phase2-handoff.md` |
| R13 | recoil-report ui-kit | `src/ui-kit/recoil-report/` 13 atoms + 5 shipped instances | Snap-together HTML atoms that already produce paid-pilot artifacts | **A** | 4 | 2 | 4 | **RAM** — this is the *actual* working atomic design system for revenue work | Fold `_tokens.css` values into `tokens.ts` (one palette rule) |
| R14 | compass-kit static reference | `public/compass-kit/` | Design source of truth for Phase 2 parity | **A** | 4 | 2 | 3 | **RAM** — retire after Phase 2 parity is reached | Parity checklist in handoff doc |
| R15 | Document registry (5 doc types × 10 patterns) | `src/document/registry.ts` | Every ARCS document is one of 5 types assembled from 10 reader patterns | B | 3 | 2 | 3 | **RAM** — real code, thin consumption | Wire Profile Scan Phase 1 against it (per memory) |
| R16 | Observatory + provenance ledger | `src/app/observatory/page.tsx` (1,174 LOC, live) · `docs/provenance-ledger.md` | Every scored claim cites a reproducible method (P## ids) | **A** | 3 | 3 | 3 | **RAM** — also the promotion instrument for RC-OPS-001 | Load a real drift-findings dataset (roadmap #4c) |
| R17 | Tribune Intelligence Layer | ADR-020 | Anterior/proactive/posterior intelligence wrapped around receipts | C | 3 | 3 | 3 | **RAM — decision due**: 50-receipt trigger cleared at 184; either schedule or formally re-gate | Explicit go/park decision (write-lock Q below) |
| R18 | Lattice ROM + Folksonomist | ADR-023 · `lattice-pressure-rom.json` · `arcs_core.py` · `lattice_sim.py` | Goals precipitate from receipt-graph edge weights; constants are L7-governed, never self-tuned | B | 3 | 4 | 3 | **RAM (gated)** — gate is now measurable and unmeasured | **The 30-min experiment** (see Docket) |
| R19 | RC-OPS-001 Inchworm+Echo | `operators/arcs_inchworm_echo.py`, RC-REGISTRY | 3-pass thread extraction + cross-domain isomorphism detection | B | 2 | 3 | 2 | **RAM (gated, correctly)** — Observatory period not yet served | Keep gate; log findings through Observatory |
| R20 | Operators library (34 files, 16.6K LOC) | `operators/` | Component-level L0–L5 reasoning in Python | C | 2 | 5 | 3 | **IDLE + relabel** — "production-ready canonical" is falsified by its own README ("?" annotations), 12/34 numpy imports vs "stdlib-only," zero integration. Keep code; kill the status claim | Write-lock the README relabel (Q below) |
| R21 | HOLD/REJECT validation gate | SKILL.md Domains 6 + dedicated section | One missing truth → HOLD; one broken truth → REJECT | C | 3 | 2 | 3 | **ETHEREAL** — most elaborately specced rule in the repo, zero code (0 grep hits for `validation_state`/`ARCS-INV-`) | Mark SPECCED-NOT-IMPLEMENTED; smallest revival = input validation on `/api/compass` |
| R22 | 12D kinematic manifold | `operators/arcs_kinematics.py` v1.3 + 2026-06-24 adjudication | D1–D3 are real derivatives; D5–D12 are coherence operators, not measurements | B (D1–D3) / S (D5–D10) | 2 | 4 | 2 | **RAM (D1–D3) / ETHEREAL (D5+)** — the adjudication already ruled D5–D10 numerically noise | None until reformulation (canon-level work) |
| R23 | Periodic Table v3.0 (53 elements) | `operators/docs/PERIODIC-TABLE.md` | A taxonomy poem: quark forces, bond strengths, reaction types | S | 2 | 4 | 2 | **LEGACY** — self-declares "Canonical"; conflicts with the 5-level ProductionGuide and with Brad Frost usage in `src/`; keep annotated as inspiration | Add a non-normative banner (write-lock) |
| R24 | Vector Collision Engine v1/v2 | `runtime/specs/ARCS-Vector-Collision-Engine-*.md` | Paths-over-probabilities: rank paths by constraint survivability | S | 1 | 4 | 2 | **COMPOST** — the lesson already lives as `paths[]` + court verdicts in the live compass output; the spec's geometry claims were never implemented | Extract 1-paragraph lesson into ARCS-v9-ROM.md; move spec to archive/ |
| R25 | External-claims corpus (YellowPaper metrics, Phase-Change Thesis physiology, blockchain receipts) | `_CANON/ARCS-YellowPaper.md`, `ARCS-PHASE-CHANGE-THESIS-001.md` | Marketing-era quantitative claims (68%→87%, $350B, 40–60% ROI, "vagus-safe") | S | 1 | 3 | 1 | **ARCHIVE with do-not-quote annotation** — no reproducible evidence in corpus; real reputational risk if quoted to a client | Annotation PR (write-lock) |

---

# 3. Collision Report

Unsoftened, per instruction.

1. **"L0–L5" means three different things.** (a) `.claude/arcs-canon.md`: pipeline *stages* (parse→decompose→bayesian→triune→emit). (b) `CLAUDE.md`/AGENTS: fractal *abstraction layers* (atomic signal→coherence→…→L7 meta-governance). (c) Periodic Table: atomic-design *hierarchy levels* (quarks→pages). A new contributor cannot tell which is meant in any given sentence. This is ACRONYM_DRIFT at the system's namesake concept.
2. **Y-gate enum: docs contradict live code.** `src/lib/ygate.ts:6` polarity = `SCRATCH|YELLOW|PARADOX|FORK|DELTA|GREEN|LOCKED`. WORLD.md's render table and CLAUDE.md's project map both list **RED** and **DRIFT** as Y *states* (`RED=GRAIN`, free-solo RED). In code, RED is a condition *severity* and drift is a separate `driftState` field. Per standing rule (kinematics precedent): code wins; docs need the fix.
3. **Operators README self-falsifies.** Claims "production-ready, tested, canonical" and "all operators are stdlib-only" while: 12/34 files import numpy/scipy (including LAB, BAR, SAGE, CURATOR — the core four), the README annotates its own inventory with "?" ("CIS (coherence/integrity/signal?)", "Yoav Store (time-aware?)"), and nothing imports any of it from the live app.
4. **The AtomicDesign Production Guide grades phantom files.** It assigns letter grades (A- 84%, A- 85%, B 72%…) to `ARCS-RigorProtocol-S-TIER.md`, `ARCS-ExternalityDetector-S-TIER.md`, `ARCS-MoleculeLibrary-Complete.md`, `ARCS-RemediationHierarchy.md`, `ARCS-DecisionLineage.md` — **none of which exist anywhere in the repo**. Grades with no gradeable object are manufactured evidence and must not be cited.
5. **Four unreconciled "atomic design" systems share one name.** Periodic Table (6 levels/53 elements) · ProductionGuide (5 levels/9 atoms) · operators/README (meta-operators/primitives/systems) · actual Brad Frost usage in `src/ui|molecules|organisms`. ADR-031 governs only the fourth. The first three impose cognitive mass on every reader who tries to map them onto real code.
6. **"NCI" is two unrelated numbers.** The commit-tag counter (`[NCI:212]`, monotone session counter) and the receipt `nci_score` (a 0–100 coherence score). Same three letters, same repo, different quantities. Same shape as the resolved BAR/KKL collision — this one is still open.
7. **Inline-styles rule violated at the app root since first commit** (already documented in the 2026-06-23 audit, re-verified today: `layout.tsx:57-59` uses className + Tailwind utilities; `tailwindcss` in deps). Three files still state the absolute rule. Fix the rule text or the code; the current state trains sessions to distrust stated law.
8. **CI enforces the forbidden thing.** `AGENTS.md`/CLAUDE.md say "npx next build, not tsc --noEmit"; CI's hard type-check gate runs `tsc --noEmit`.
9. **HOLD/REJECT gate: spec-as-settled.** Two full SKILL.md sections describe a validation layer with receipt schema and trigger taxonomy; zero code exists; the compass Court verdict enum (`PASS|TENSION|BLOCK`) is a different three-state enum that invites conflation on a skim.
10. **Gates satisfied but unacknowledged.** ADR-020's trigger (50 receipts) cleared at 184 — status still "not yet started" with no explicit go/park. ADR-023's real gate is a measured Gini/Zipf baseline — count satisfied, measurement never run. ADR-025a's 30-day review is due ~2026-07-12 with no named checklist or reviewer. UNCLOSED_CEREMONY applied to gates: they open loudly and clear silently.
11. **The Outcome loop is a missing dependency for two decided ADRs.** ADR-025b needs MIN_SAMPLE=20/cohort; ADR-026 step 3 is "verify Outcome accumulation." Live evidence: `Outcome_pkey` has 3 index scans. Debrief delivery shipped; accumulation didn't follow.
12. **Duplicate/orphan bookkeeping:** two ADR-025s; no ADR-021; `_CANON/arcs-v9-additional/` still contains 4 docs whose promoted copies live in `_CANON/living/` (the v3.6.0 consolidation moved them but the originals' README remains — verify no double-canon); orphaned Supabase tables with no owning app; the three overlapping narrative logs (backlog #3) remain the single largest drift generator.
13. **Metaphors carrying equation costumes:** quark "equations" (`C = Ψ·σ`, `R = ⟨Ψ₁|Ψ₂⟩`), ARCS Law constants (α=0.5, β=0.3, γ=0.2 — no calibration evidence anywhere), bond strengths (10/10 covalent), D5–D12 "quantum flow." None are validated technical claims; all should read as design language only.

---

# 4. S-Tier Minimum Viable Artifact Sets

## Kit A — Founder monetization / paid-pilot selection ("Pilot Court")

- **JTBD:** "Decide which prospect gets my next block of hours, at what price, before the window closes — and leave a receipt so future-me stops re-litigating it."
- **Atoms:** Question · Entity (counterpart) · Window · Stakes · Evidence (ledger history) · Bet (price+scope) · Stop-loss · Confidence · Decision Receipt.
- **Molecules:** Detective lookup (`receipt_lookup.py`) · Loki pre-mortem (3 falsifiers: why won't this convert/pay/renew) · BAR ruin check (founder time = the ruin asset) · Kairos window check · Outcome Recoil (post-call, recoil-modes v1).
- **Governance gates:** NOTOMATION (system renders terrain, never picks the pilot) · Y-gate conviction stated on GO · every proposal gets a review_date at creation (kills PHANTOM_OPEN_ITEM).
- **10-minute flow:** (1) `receipt_lookup` on counterpart — 1 min. (2) DEWY-frame the pilot question in compass — 3 min. (3) Loki: write 3 falsifiers — 2 min. (4) BAR: price floor + stop-loss + review date — 2 min. (5) Freeze receipt; name the next irreversible step — 2 min.
- **Receipt schema:** DEWY vector + `{offer_price, scope, stop_loss, signal_threshold, review_date, y_state, falsifiers[3]}`.
- **Success metric:** 1 signed paid pilot per 30 days.
- **Stop-loss:** 2 proposals aged >14 days without response → change the *offer*, not the effort.
- **Deliberately excluded:** Observatory, lattice, kinematics, Tribune, any operator Python — nothing enters the kit that a paying founder can't see working in 10 minutes.

## Kit B — Client decision-room / high-stakes action ("Shared Terrain Session")

- **JTBD:** "Help me and my counterpart see the shape of one hard decision in one sitting and leave with an artifact we both trust."
- **Atoms:** Question · Entities (both parties) · Stakes · Horizon · Options (paths) · Evidence · Dissent · Receipt.
- **Molecules:** Pre-call context scan (call-brief pattern) · FATED decomposition (live in Brief) · Assumption challenge (tributary[1]) · Co-signed delta gate ("are both parties bound by this?" — Part VI unanimity-of-being-bound, 2-party minimal form) · Post-call Outcome Recoil.
- **Governance gates:** Two-tier ledger rule as written — internal ledger always writes; **external page is never auto-created** (publishing a relationship is a deliberate human act) · dissent recorded, never averaged away · write-lock on any change to a live external brief.
- **10-minute flow:** (1) Open the counterpart's brief page together — 2 min. (2) Run compass on the shared question — 3 min. (3) Walk paths + court verdict; capture dissent verbatim — 3 min. (4) Co-sign the delta gate or record HOLD; set review date — 2 min.
- **Receipt schema:** DEWY + `{respondent, witnesses[], dissent_record, cosigned: bool, external_page: exists|none, review_date}`.
- **Success metric:** counterpart references the artifact unprompted, or books the next session.
- **Stop-loss:** if a counterpart won't engage with the brief across 2 sessions, stop producing custom briefs for that relationship.
- **Deliberately excluded:** Arbitration sessions, >2-party quorum, blockchain/ordinal anything, live multi-user editing.

## Kit C — Canon promotion / deprecation court ("Relic Court")

- **JTBD:** "Decide whether an artifact becomes load-bearing, stays experimental, or retires — without silent mutation and without a vibe standing in for a gate."
- **Atoms:** Relic ID · Lineage · Claim · Evidence grade · Gate condition (as a measurement) · Disposition · Write-lock question · Receipt.
- **Molecules:** Loki challenge (Operator 17: what falsifies this?) · Collision scan (does the name/claim collide with existing canon — ACRONYM_DRIFT check) · Gate measurement (run the number, don't assert it) · Kintsugi seam (repair visibly, log permanently, discount trust post-repair).
- **Governance gates:** Human write-lock on every ROM promotion (ROM primitive #7) · CANON_COLLISION → escalate, never resolve unilaterally · entry in `operators/RC-REGISTRY.json` (or successor) required before court convenes · promotion requires an attached *measured* gate result.
- **10-minute flow (per relic):** (1) Registry entry + lineage — 2 min. (2) One falsifier — 2 min. (3) Run/cite the gate measurement — 3 min. (4) Disposition + proposed canon diff — 2 min. (5) Freeze receipt with the write-lock question for the human — 1 min.
- **Receipt schema:** RC-REGISTRY shape + `{evidence_grade, gate_measurement: {metric, value, threshold}, disposition, canon_diff_ref, writelock_question}`.
- **Success metric:** zero ROM entries without a measured gate; zero unresolved collisions older than one session.
- **Stop-loss:** if a relic's gate can't be stated as a measurement within 10 minutes → automatic ETHEREAL, no debate.
- **Deliberately excluded:** batch promotions, self-tuned thresholds (NOTOMATION breach per lattice ROM), retroactive lineage edits.

---

# 5. Promotion Court Docket

## Top 5 ROM promotion candidates

| # | Candidate | Proposed canon diff | Human write-lock question | 30-min uncertainty-reducing experiment |
|---|---|---|---|---|
| 1 | **Call-brief two-tier ledger** (R01) | `runtime/specs/call-brief-hooks-v1.md` front-matter DRAFT→ROM; add engagement-protocol pointer in `_CANON/index.md` | "Ratify permanently: hooks may NEVER auto-create or auto-edit an external page — yes/no?" | Run `receipt_lookup.py` against all 13 briefs; grade each advisory usable/not |
| 2 | **Pathogen taxonomy** (R05) | Lift the 10-pathogen catalog from `_PATTERNS/` into a Book II Part V annex (or new `_CANON` doc) | "Closed-world or open? Can a session add pathogen #11 without court?" | Classify every finding in the last 3 handoffs against the taxonomy; report coverage % |
| 3 | **DEWY receipt schema v1** (R03) | `dewy-receipt-schema-v1.md` status REVIEW→ROM | "Freeze the v1 field set (additive-only from here)?" | Script: validate live receipts against the JSON schema; count violations |
| 4 | **Y-gate enum + render map** (R04) | Correct WORLD.md/CLAUDE.md render tables to the code enum (RED→severity, DRIFT→driftState); mark mapping ROM in `ARCS-v9-ROM.md` | "Confirm: code enum is canonical; RED is not a polarity state?" | Pull y_state distribution from prod; sanity-check every state renders |
| 5 | **ADR lifecycle + closing ceremony** (R06) | Add `Closes: ADR-XXX` trailer to the commit convention in AGENTS.md; queue workflow parses it | "Adopt the trailer as *required* (mechanically checked) or advisory?" | Write the commit-msg regex hook; run it against the last 30 commits |

## Top 5 to retain in RAM

1. **Tribune Layer (ADR-020)** — trigger cleared at 184 receipts; needs an explicit go/park decision, not silence.
2. **Compass-kit Phase 2 + ADR-031** — decided, specced, unstarted; the UI convergence path.
3. **Observatory + provenance ledger** — live; it is also the promotion instrument for RC-OPS-001 and the drift-sensor display.
4. **Recoil modes v1 + `receipt_lookup.py`** — the engagement loop's working memory; promote after 2 more real-call uses.
5. **Lattice/Folksonomist machinery (ADR-023)** — correctly gated; becomes promotable the moment the baseline is measured.

## Top 5 to archive or compost

1. **Vector Collision Engine v1/v2** → COMPOST: extract the one-paragraph paths-over-probabilities lesson into `ARCS-v9-ROM.md`; move specs to `archive/`.
2. **AtomicDesign ProductionGuide's phantom-file grades** → COMPOST the grades outright (they cite nonexistent files); keep the 9-atom operational definitions as LEGACY reference.
3. **YellowPaper / Phase-Change Thesis quantitative claims** → ARCHIVE with a do-not-quote-externally banner.
4. **Static `public/observatory/` demo + root `SESSION-HANDOFF-2026-05-26.md`** → ARCHIVED markers (superseded by the real page and the handoff chain).
5. **Periodic Table v3.0** → LEGACY with a non-normative banner ("design language, not spec"); resolves its false "Canonical" self-claim.

## The single highest-information 30-minute experiment

**Run the ADR-023 corpus baseline against the live receipts.** `scripts/arcs_core.py`'s Folksonomist + `lattice_sim.py` exist; the corpus (~184) exceeds every stated count threshold. One run produces the measured Gini/Zipf baseline that simultaneously: (a) converts ADR-023 from "gated on vibes" to "gated on a number," (b) informs the ADR-020 go/park decision, and (c) tests RC-OPS-002's stability condition. Three open gates, one script run.

---

# Decision Receipt

- **Question:** Which excavated kernels form the smallest coherent ARCS v9 atomic system that can win a real paid pilot this quarter?
- **Horizon:** This quarter.
- **Stakes:** High — architecture, product surface, canon integrity.
- **Recommended True North:** Ship **Kit A (Pilot Court)** on the call-brief + Detective-lookup + compass spine — the only relic family with A-grade, revenue-attached evidence — and run the 30-minute corpus baseline to convert three silent gates into numbers. Demote or annotate everything graded C/S so it stops taxing attention.
- **Why this and not the nearest alternative:** The nearest alternative is Compass Kit Phase 2 (UI parity) first. But no prospect has bounced off the current UI; the pilots in motion (Todd, Kelly, LaBella, Fanatics) were won on call-brief artifacts and follow-through, not on `/dashboard` polish. Kit A monetizes what already works; Phase 2 beautifies what already ships.
- **Top risks:** (1) ADR-025a's go-live review lands ~2026-07-12 with no checklist or named reviewer. (2) The three-log drift keeps manufacturing PHANTOM_OPEN_ITEMs faster than sessions clear them (backlog #3 unstarted). (3) The operators library's false "production-ready canonical" label misleads a future session into wiring unvetted numpy code into a decision path.
- **Open uncertainties:** live receipt count (184 recorded ~Jun 25; no local psql/DATABASE_URL to re-verify); Outcome accumulation near-zero (blocks ADR-025b/026); ownership of the orphaned Supabase tables; whether `_CANON/arcs-v9-additional/` still double-hosts docs promoted to `living/`.
- **Human write-lock required:** YES — for all five ROM promotions, the operators README relabel, the Periodic Table/YellowPaper annotations, and the VCE compost. Nothing in this report has been applied.
- **Next 30-minute action:** Run the Folksonomist/Gini-Zipf baseline over the live receipt corpus and write the measured number into ADR-023.

---

*Report generated by Operator 20 excavation session, 2026-07-11, worktree `dreamy-nightingale-6127c8`. Uncommitted pending human review.*

---

# Repair log — 2026-07-11, same session (closing ceremony)

Zach authorized debt paydown ("writing checks we can't cash"). The following Collision
Report items were **repaired the same day**, in this worktree, build-verified
(`npx next build` green, `/` and `/trust` visually verified on the dev server):

| Item | Repair |
|---|---|
| Collision #3 (operators README self-falsifies) | ✅ REPAIRED — status relabeled "Reference implementation, not wired in"; stdlib claim corrected with the 12-file numpy/scipy list; CIS/Yoav "?" rows replaced with descriptions from the files' own headers |
| Collision #4 (phantom-file grades) | ✅ REPAIRED — PROVENANCE NOTICE (Kintsugi seam) prepended to the Production Guide; grades marked unciteable; original text preserved |
| Collision #7 (Tailwind at app root vs. rule) | ✅ REPAIRED, the real fix — Tailwind removed entirely (deps, lockfile, `postcss.config.mjs`, `@import`); `globals.css` rewritten to a minimal preflight-equivalent reset + live keyframes + font tokens only (dead `@theme` palette and `@layer components` block cut — zero consumers, grep-verified); `layout.tsx` body de-classed; rule text in SKILL.md/AGENTS.md/CLAUDE.md rewritten to the now-true form with two explicit carve-outs (next/font classes on `<html>`, single globals.css) |
| Collision #8 (CI runs forbidden `tsc --noEmit`) | ✅ REPAIRED — `type-check` script and CI step removed; build is the sole type gate, matching the documented rule |
| Collision #9 (HOLD/REJECT spec-as-settled) | ✅ REPAIRED — both SKILL.md sections banner-marked `SPECCED, NOT IMPLEMENTED`, with the Court-enum conflation warning inline |
| Audit findings #5/#6/#7 (scanner stdlib, gauntlet interface, 3-vs-5 files) | ✅ REPAIRED — SKILL.md Domain #5 rewritten to declared-exceptions + composition architecture; token budget corrected to 5. SKILL.md bumped to v0.5.0 with changelog |
| Bonus: dead `.fadein` class (undefined anywhere) | ✅ REPAIRED — replaced with a real inline `animation: fade .2s` in `ScenarioStack.tsx` |

**Deliberately NOT repaired (write-lock territory, unchanged):** Collision #1 (L0–L5 triple
meaning — needs a naming ruling), #2 (Y-gate RED/DRIFT in WORLD.md — canon edit, docket Q4),
#6 (NCI name collision — needs a naming ruling), #10–#13 (gate decisions, Outcome loop,
ADR renumbering, metaphor annotations on Periodic Table/YellowPaper — Promotion Court items).
