---
title: Eightfold coverage map, what the repo already embodies per factor
date: 2026-10-21
status: AUDIT (read-only); every piece below was confirmed to exist as a file on origin/main at 2364a79e. Whether a piece *embodies* a factor is my reading, not a tested fact.
source_table: _PROPOSALS/2026-10-21-doors-of-perception-first-touch.md (eightfold DAG table; that file is on the arc-positioning-perspective-3bdb4b worktree, not yet on main)
---

# Eightfold coverage map

## Method and limits

- Factors are the eight in the proposal's table, with its ARCS embodiment column as the test.
- Pieces came from: `operators/OPERATOR-REGISTRY.json` (28 operators; status is the registry's own READY / PARTIAL / UNBUILT / BLOCKED), `operators/docs/PERIODIC-TABLE.md`, `runtime/specs/surface-catalog.json` (290 rows, 81 hosts), `runtime/specs/tool-catalog.json` (362 entries), ROM primitives in `CLAUDE.md`, and `_DECISIONS/`.
- A piece is listed only if I opened or listed its file. Registry status is shown, because an UNBUILT operator embodies nothing yet.
- Not found: Zach's own eightfold canon. `grep -ril "eightfold|noble path"` over `_CANON`, `_SEEDS`, `_DECISIONS`, `_PROPOSALS` returns nothing (matches the proposal's own "Open" note). So the mapping is a new reading, not a restatement.
- I did not read every ADR body. ADR placement rests on titles plus spot greps, flagged "title-only" where so.

## Table: factor to pieces

| # | Factor | Pieces (path) | Count |
|---|---|---|---|
| 1 | Right view (sure isn't the same as shown) | **ROM:** NOTOMATION, KINTSUGI, Loki Test step of HYPERSTITION PIPELINE (`CLAUDE.md`). **Operators:** #17 Detective READY (`operators/arcs_operators_lab.py`), #23 Loki PARTIAL (`operators/arcs_trace_loki.py`), #18 Immune PARTIAL (`operators/arcs_constitutional_court.py`), #12 BayesianUpdater PARTIAL (`operators/arcs_operators_lab.py`). **ADRs:** `_DECISIONS/ADR-079-refusal-to-overclaim-is-the-product.md`, `ADR-062-ouroboros-recursive-self-falsification.md`, `ADR-061-verify-flags-against-full-source.md`, `ADR-033-serialization-pathogen-family.md`, `ADR-044-temporal-provenance-gate.md`, `ADR-064-external-corroboration-milestone-gate.md`. **Tools:** `.claude/agents/claims-skeptic.md`, `.claude/agents/chief-loki.md`, `scripts/receipt_timing_gate.py`. **Surface:** `honest.arcs.care` (`public/honest.html`, "Check It Before You Say It"). | 14 |
| 2 | Right intention (supply structure for pre-work) | **Product:** compass pipeline and prep form (`src/app/api/compass/route.ts`, `src/app/api/prep/route.ts`, `src/app/dashboard/page.tsx`). **ROM:** HYPERSPHERE CONTEXT MANIFOLD, GOLDEN INCHWORM (`CLAUDE.md`). **ADRs:** `ADR-018-helpful-input-model.md` (DRAFT, held), `ADR-058-CALIBRATE-IDEA-Construction.md`, `ADR-086-two-pass-backlog-induction.md`. **Tools:** `.claude/commands/precall-brief.md`, `.claude/skills/recoil-prep/SKILL.md`, `scripts/recoil_brief.py`. **Surface:** `app.arcs.care` (`src/app/page.tsx`). | 10 |
| 3 | Right speech (resonance and codex, facts invariant) | **Surfaces (codex family):** `public/robin-codex.html`, `public/scott-codex.html`, `public/kam-codex.html`, `public/yuri-codex.html`. **Canon:** `_CANON/living/ARCS-Codex-v8.5.md`. **ADRs:** `ADR-084-reliance-not-trust-public-surfaces.md`, `ADR-044-temporal-provenance-gate.md`, `ADR-060-hypercube-gauntlet-arc-weld.md` (greps "rhetorical"). **Tools:** `.claude/workflows/counterpart-gauntlet.js`, `.claude/skills/forge/`, `.claude/skills/teardown-page-factory/`. **Canon:** `_CANON/book-ii/part-v-the-accumulation-protocol.md` (greps "rhetorical"). | 8, but no *operator* and no "how I read you" instrument; see thin factors |
| 4 | Right action (pull, not push; same strength used as the door works) | **ROM:** WRITE-LOCK (one-way doors declared), GOLDEN INCHWORM non-blocking (`CLAUDE.md`). **Operators:** #13 TemporalSequencer BLOCKED (`operators/core/operators.py`), #6 PhaseLock UNBUILT. **ADRs:** `ADR-085-main-write-lock-and-hot-file-leases.md`, `ADR-075-metabolic-router-mechanical-judgment-split.md`, `ADR-081-kairos-detector-attractor-basin-condenser.md`. **Gates in practice:** `scripts/safe_merge.sh` (AGENTS.md gotcha 17), `AGENTS.md` gotcha 22 (one owner per branch). | 6, only 1 ROM primitive and no READY operator |
| 5 | Right livelihood (workforce thesis: identity follows the role; Zach's gloss 2026-10-21: lean into strengths, do not larp what you are not; and an opportunity-cost stop loss, interrupting the pattern of applying into a void and taking shots you cannot take or track) | **Job-fit and honest-self surfaces, per Zach:** `jobs.arcs.care` (`src/app/jobs/page.tsx`, `src/app/jobs/JobsBoard.tsx`, admin-gated), its scan, profile and lane routes (`src/app/jobs/scan/`, `src/app/jobs/profile/`, `src/app/jobs/lane/`, `src/app/jobs/champions/`), LinkedIn personal-data read (`public/arcs-field-scan.html` at `arcs-field-scan.arcs.care`, `scripts/linkedin_cut.py`, `scripts/linkedin_render.py`), `resume-tailor.arcs.care` (`public/resume-tailor.html`, honest resumes), `honest.arcs.care` (`public/honest.html`, also in factor 1), `scripts/jobs_prose_gate.py`; titled for the opportunity-cost idea: `mercury.arcs.care` (`public/mercury.html`, "Opportunity-Cost Engine", title-only read). **ADRs, adjacent:** `ADR-054-free-to-hold-metered-to-fire-pricing.md`, `ADR-076-mcp-led-growth-attribution-wedge.md`, `ADR-069-first-closed-client-receipt-precedent.md` (title-only). | 9 on the individual side; 0 on the enterprise/workforce side |
| 6 | Right effort (read the grain before you push) | **Operators:** #1 Fd, #2 Sd, #4 Wd, #5 Pc, #7 De READY (`operators/core/atoms.py`), #3 Td READY (`operators/arcs_kinematics.py`). **Tools:** `scripts/outcome_funnel.py`, `.claude/commands/catalog.md` (reuse before building), `.claude/commands/prior-art.md` (`scripts/prior_art.py`). **ADRs:** `ADR-077-prime-invariant-reverse-jtbd-magnetize-the-tool.md`, `ADR-073-model-routing-adr-audit-default.md`, `ADR-039-deploy-cost-guardrail-ignored-build-step.md`. **ROM:** ORTHOGONAL ECHO DETECTOR (`operators/arcs_inchworm_echo.py`, `operators/arcs_echo_embedding.py`). | 13 |
| 7 | Right mindfulness (atlas, ziggurat, HUD; rise then descend) | **Operators:** #25 Shavasana UNBUILT as an operator, but the mechanical half exists as `scripts/shavasana_handoff.py`; #22 Conductor READY (`operators/receipt_evaluator.py`). **Tools:** `scripts/essay_atlas.py`, `scripts/hud_signal_audit.py`, `.claude/commands/witness.md`, `.claude/commands/loops.md` (`scripts/open_loops.py`), `scripts/echo_ridgeline_feed.py`. **Surfaces:** `public/prl-status-atlas.html` (atlas), `public/blog-nftt-loop-hud.html` (HUD), `status.arcs.care` (`public/status.html`), `monolith.arcs.care` (`public/monolith.html`), `surfaces.arcs.care` (`runtime/warroom/surfaces.html`). **ADRs:** `ADR-046-witness-trigger-live-capture.md`, `ADR-068-verb-altitude-gate-matrix.md`, `ADR-023-observability-goal-lattice.md`, `ADR-027-observatory-substrate-seed.md`. **Specs:** `_PROPOSALS/2026-10-15-hud-widget-lockups-spec.md`, `_PROPOSALS/2026-10-19-hud-audit-ruling-sheet.md` (only place "ziggurat" appears in repo markdown I searched). | 17 |
| 8 | Right concentration (oars, flow, spiral) | **Operators:** #14 CoherenceScorer PARTIAL (`operators/arcs_primitives.py`), #19 Accountant READY (`operators/arcs_accountant.py`), #21 Librarian READY (`operators/arcs_store.py`), #20 Folksonomy READY (`operators/arcs_operator20.py`). **Loop closure:** `scripts/receipt_outcome_queue.py`, `scripts/receipt_outcome_resolver.py`, `scripts/accountant_weekly.py`, `scripts/decision_receipt_to_accountant.py`, `scripts/receipt_coverage.py`. **ADRs:** `ADR-051-drift-receipt-gate.md`, `ADR-052-inchworm-drift-auditor.md`, `ADR-080-instance-to-class-self-promotion-build-loop.md`, `ADR-071-mobius-one-surface-triune-invariant-gravity-well.md`. **Tool/product:** receipt history in `src/app/api/history/route.ts`. | 14 |

Groupings from the proposal, by piece count: wisdom (1, 2) = 24, conduct (3, 4, 5) = 22, practice (6, 7, 8) = 44. Mass sits in practice; conduct is the light group.

## Thin factors (fewer than 2 pieces that actually fit)

1. **Right livelihood (5): individual side covered, enterprise side empty.** Zach's correction: the jobs board, scan, LinkedIn read, resume-tailor and honest surfaces already point at it (play to real strengths, never pose as something you are not). What is missing is the workforce half: nothing implements "the identity follows the role" for a team or an L&D buyer (cheapest test 3 not yet run). Also note these surfaces read as Zach's own job search; whether a visitor meets them as a livelihood tool is untested.
2. **Right action (4): 1 real primitive.** WRITE-LOCK plus repo gates (`safe_merge.sh`, one-owner-per-branch) cover *when not to act*. Nothing covers the *pull, not push* idea (matching effort to how the thing works). The only operators near it are #13 BLOCKED and #6 UNBUILT.
3. **Right speech (3): no instrument.** The codex surfaces and the gauntlet are *outputs and checks*. No operator or tool computes a register read or backs the proposed "how I read you" toggle; nothing under `operators/` or `scripts/` matches `resonance|rhetor|register`. The phrase "adaptive rhetorical resonance" lives in memory notes, not a file I could cite.

Borderline: factor 7's "ziggurat" is named only in two HUD proposals, so the metaphor is specced but unbuilt; atlas, HUD and Shavasana-mechanical are real.

## Orphans (pieces that fit no factor)

These exist and I could not honestly place them on the eight. Orphan does not mean wrong; the path may simply not cover plumbing.

- **Infrastructure and plumbing ADRs:** `ADR-001` auth gate, `ADR-002` database split, `ADR-005` env injection, `ADR-006` Supabase branching, `ADR-007` Prisma migrations, `ADR-008` RLS, `ADR-016` auth model, `ADR-032` zero-trust, `ADR-048` secrets rotation, `ADR-014`/`ADR-039` CI and deploy cost.
- **Design-system and ops ADRs:** `ADR-009`, `ADR-011`, `ADR-031`, `ADR-083` (UI kit), `ADR-087` (animation timeline), `ADR-057` (sequence oracle), `ADR-089` (JTBD graph schema).
- **Operator atoms with no path role yet:** #8 Ra, #9 Ha, #10 Ns, #11 Ci, #15 Ec (all UNBUILT), #4 Wd READY but used for diffusion, not a factor.
- **Operators with no factor:** #27 Taxonomist, #28 Auditor (UNBUILT), #24 DevilsAdvocate (UNBUILT; arguably factor 1 once built), #26 SuperAdmin PARTIAL.
- **Business-vertical stacks in the periodic table:** L5 pages #301 to #306 (Career GPS, Trading System, Marketing OS, Last Time, Research Engine, Team Resonance). Only Team Resonance (#306) loosely touches factor 5, and it is a doc entry with no binding found.
- **Surfaces:** the ~60 per-counterpart pages (`yuri-*`, `scott-*`, `julia*`, etc.) are factor 3 instances in aggregate; I mapped the codex family and left the rest as a bulk class, not individually.
- **Product/distribution:** `germinate.arcs.care`, `rosetta-shell.arcs.care`, `resume-tailor.arcs.care` (public packages and tools).

## What this says

1. The map is lopsided: practice factors (6 to 8) have 44 pieces, conduct (3 to 5) only 22. Building to the eight means building toward 5, 4, 3.
2. Factors 1 and 8 are strongest in *enforcement* (gates, receipts, Accountant); factors 6 and 7 in *instruments* (kinematics atoms, atlas, HUD).
3. The UNBUILT operators (10 of 28) cluster in the places the path needs: DevilsAdvocate and Shavasana (factors 1, 7), Ci/Ns/Ra/Ha (right speech's resonance, if it computes anything).
4. Because the eightfold is a new reading, treat the mapping as a hypothesis. A sharper test: for each factor, pick the single piece a visitor would meet on first touch. Today that is a real piece only for 1 (`honest.arcs.care`), 2 (compass), and 7 (`status.arcs.care`).

## Not checked

- Contents of most ADR bodies (title-level placement).
- Whether the codex pages implement "facts invariant, delivery in their register"; I mapped them by name and the ADR-060 grep only.
- Operator status is the registry's claim as of its last generation, not re-probed (`operator_registry_emit.py --probe` not run).


## Addendum (Zach, 2026-10-21): livelihood is a stop loss

Right livelihood here means opportunity-cost stop loss: break the habit of applying into a void, and do not fire shots that cannot be taken or tracked. Open question this raises, not answered by the audit: which of the pieces above actually *stops* a shot (a gate that refuses an application) versus only *scores or tracks* it. I did not read the jobs code to tell.

## Addendum 2 (Zach, 2026-10-21): telemetry for the average person

Show progress and trajectory as numbers even when they are rough ("even if inaccurate"), in a form an ordinary user can read. Fits factors 7 and 8 (see the whole terrain; every pull moves you forward). What exists today is built for Zach, not a first-time visitor: `scripts/outcome_funnel.py`, `scripts/accountant_weekly.py`, `scripts/receipt_coverage.py`, `status.arcs.care` (`public/status.html`). Tension to resolve before building: the repo's refusal-to-overclaim stance (`_DECISIONS/ADR-079-refusal-to-overclaim-is-the-product.md`) means a rough number must be labelled as rough ("first read, will sharpen", as the proposal already says), not hidden.

## Addendum 3 (Zach, 2026-10-21): livelihood as a portable, owned belief graph

Second half of right livelihood: a belief graph with receipts behind each decision, decoupled from any employer, owned by the person and built on their own zone of genius ("neural net worth" is Zach's phrase). The aim is heirloom grade: Zach's example is a son compounding on a parent's judgment and learning from the bad decisions, not only the good ones. This makes the failures part of the asset, which is the Kintsugi primitive applied to a life.

Pieces that point at it, by file or title (none confirmed to do the portable-ownership part):
- Receipts as the evidence layer: `operators/arcs_receipt_core.py`, `operators/receipt_evaluator.py`, `_DECISIONS/ADR-017-receipt-core-schema.md`, the `decision_receipt` ledger (append-only, AGENTS.md).
- Memory and retrieval: `operators/arcs_store.py` (#21 Librarian, READY), `runtime/memory-export/`.
- Ownership and portability, title-only: `_DECISIONS/ADR-072-engine-sovereignty-gradient.md`, `_DECISIONS/ADR-037-stateless-anonymous-share.md`, `_DECISIONS/ADR-050-federated-family-airgap.md`, `_DECISIONS/ADR-038-recoil-bookmark-primitive.md`.
- Outcome truth: `scripts/receipt_outcome_queue.py`, `scripts/receipt_outcome_resolver.py` (a decision only teaches once its result is recorded).

Gaps I can see without reading deeper: no file I found exports one person's receipts as a graph they hold outside the hosted database; nothing marks a receipt as "bad decision, lesson attached" for a reader other than the author; no heir or inheritance concept appears in the ADR titles. Whether the term reads as slop is a copy question, not a coverage one.
