# Operator Audit — Experiment Manifest (gauntlet input)

> Source: alchemist germination, 2026-08-27.
> 12 experiments. Each runs a 5-lens gauntlet: SAGE, LAB, BAR, KINTSUGI, Skeptic reviewer.

## Gauntlet lenses

- **SAGE** — coherence/NCI: does hypothesis hold under coherence scrutiny? weakest link?
- **LAB** — adversarial/threat: loki challenge? advisor consensus (PROCEED/PAUSE/PIVOT/ABORT)? bayesian posterior after falsification?
- **BAR** — ruin/risk: ruin scenario if wrong? asymmetry? baseline floor? kelly fraction of proceeding as-designed?
- **KINTSUGI** — pathogen/repair: what's wrong as-designed? faulty assumption, missing data, ambiguous mapping, unvalidated weight? what's the repair before trustworthy? post-repair NCI?
- **Skeptic reviewer** (persona) — what kills it? minimum bar? red flag?

## Verdict scale (per agent)

- **READY** — can run as designed
- **REPAIR** — specific fix needed before it can run
- **SHELVE** — shelve until decision/infra resolves

---

## E1 — S1×C-bmk: somatic/HCI fidelity under benchmark scrutiny

**Hypothesis:** If we add somatic self-report collection (6-question intake from `somaticPrompt` → DB column / JSONL field → translator wire so `somatic.source = "user_self_report"`) and a single 0–100 HCI self-report question at intake (same path → `hci.source = "user_self_report"`), then the benchmark's somatic and HCI layers will carry discriminatory signal for real receipts, because both layers currently receive the same default/proxy reading regardless of content.

**Current state:** `somaticPrompt` exists in `audit-translator.ts` (6 questions, 0–1 intake scoring, skip-for-defaults). Nothing collects the scores — no DB column, no intake UX, no wire from form→translator→somatic.source. HCI is always proxy (`hci_score = Math.round(coherence_pct ?? 50)`, `hci_source = "proxy"`). DB has no somatic/HCI columns. `benchmark_pairs.jsonl` has 9 rows, all `somatic: default / hci: proxy / axioms: llm_derived`.

**Status:** OPEN — no collection path yet.

**Tooling:** `audit-translator.ts` (somaticPrompt, translateCompassReceipt reads somatic/hci — currently always default/proxy), `prisma/schema.prisma` (Receipt model — needs somatic/HCI columns or JSONL fields), `persistence.py` (store_benchmark_fragment writes fidelity markers), `service.py` (run_sage/lab/bar/kintsugi consume somatic/hci from primitives), `benchmark_pairs.jsonl` (live pairs — can add somatic/HCI self-report fields to test locally first), `review_pairs.py` (can display fidelity markers).

**Tune the gauntlet for E1:**
- Does the translator wire the collected scores (or does collection happen and source stays default)?
- Does somatic/HCI self-report actually correlate with operator output differences (or is it still noise after collection)?
- DB schema constraint: columns vs JSONL fields vs PrepSession fields?
- HCI self-report as single 0–100 question — is that enough, or does BAR's irreversibility×HCI interaction need more?
- Somatic 6-question intake — UX cost vs signal gained?
- Negative result is still real: if collected and still no discriminatory signal, that's a finding (the layers may not be discriminatory by design).

---

## E2 — S2×C-min: horizon mapping under minimal framing

**Hypothesis:** If we add a mapping layer from DB `horizon` enum (`TODAY|WEEK|QUARTER|YEAR|YEARS`) to translator's expected enum (`TODAY|THIS_WEEK|THIS_MONTH|THIS_QUARTER|ONE_TO_THREE_YEARS|LONGER`), then every receipt with non-`TODAY` horizon gets correct `signalProxy`, because currently the translator reads the DB `horizon` value without mapping and expects a different enum.

**Current state:** `prisma/schema.prisma` has `horizon String?` — values `TODAY|WEEK|QUARTER|YEAR|YEARS`. `audit-translator.ts` reads `horizon` from the receipt (currently without mapping — reads DB enum directly, expects translator enum). `docs/audit-translator-validation.md` — C-5 gap identified, DB→translator mapping called out as required. Mismatch is a correctness risk, not just fidelity.

**Tooling:** `audit-translator.ts` (translateCompassReceipt reads horizon — currently without mapping), `prisma/schema.prisma` (horizon field, values documented), `docs/audit-translator-validation.md` (C-5 gap, DB→translator mapping required).

**Tune the gauntlet for E2:**
- Mapping location: translator (reads DB enum, maps to translator enum) vs persistence (stores mapped value) — translator cleaner.
- Exact mapping for ambiguous cases: `YEAR` → `ONE_TO_THREE_YEARS` or `LONGER`? `YEARS` → `LONGER` or `ONE_TO_THREE_YEARS`?
- Does `TODAY` map to `TODAY` cleanly (or does a special-case handler break it)?
- Does the translator read horizon from the raw receipt or from a mapped field?
- Is the mapping a lookup dict, a function, or a case statement?
- What's the falsification: mapping applied but translator still reads raw DB enum (mapping not wired into read path).

---

## E3 — S4×C-pb: CSM operationalization under Path B framing

**Hypothesis:** If we implement CSM computation per-pair (formula in `docs/CSM-spec.md`) and store CSM on each benchmark pair, then the benchmark can begin making Path B decisions (CSM ≥ 0.65 on sustained sample → operator output agrees with LLM enough to consider replacing/augmenting LLM compositon).

**Current state:** `docs/CSM-spec.md` — full formula (alignment×0.40 + delta×0.30 + (1−coherence_loss)×0.20 + (1−severity)×0.10), threshold 0.65, per-operator subtask maps, coherence loss per operator, severity computation, fidelity adjustment (separate from CSM), aggregate weighting, 5 open questions. `benchmark_pairs.jsonl` has real pairs with primitives + llmOutput + auditResult (enough to compute CSM on SAGE/LAB/BAR/KINTSUGI for t2/t3/t4). CSM formula specced but no code computes it.

**Tooling:** `docs/CSM-spec.md` (formula, subtask maps, coherence loss, severity, fidelity, aggregate weighting, open questions), `persistence.py` (loadBenchmarkPairs reads pairs — CSM can operate on loaded pairs), `service.py` (has runners — could host CSM or separate module), `benchmark_pairs.jsonl` (real pairs — enough for baseline CSM), `review_pairs.py` (could display CSM per-pair).

**Tune the gauntlet for E3:**
- Per-operator subtask map correctness: does SAGE alignment use the right dimensions from llmOutput + auditResult?
- `coherence_loss` formula per operator: SAGE = `1 − (operator.coherence_law_score / max(llm.coherence_pct, 1))`; LAB = `1 − (posterior_confidence / (nci_score/100))`; BAR = `1 − (1 − abs(floor_nci − nci_score/100))`; KINTSUGI = `1 − (nci_score / llm.nci_score)`.
- `severity` normalization: stakes × irreversibility — is the stakes_weight mapping (LOW 0.3 / MEDIUM 0.6 / HIGH 1.0 / EXISTENTIAL 1.0) right?
- 5 open questions: somatic/HCI exclusion from alignment? normalized_distance function? categorical partial credit? CSM computation location?
- Unweighted CSM first (baseline), then weighted once fidelity weights validated.
- Who computes CSM — store-side function vs CLI reviewer?

---

## E4 — S5×C-bmk: who-was-right persistence under benchmark scrutiny

**Hypothesis:** If we add an outcome adjudication field to the benchmark store (when reviewing a pair, record who was right — LLM or operator — and why, plus unresolved flag), then the benchmark can accumulate "who was right" data over time, which validates the fidelity weights (do high-fidelity pairs get adjudicated correctly more often than low-fidelity pairs?).

**Current state:** Review protocol exists (5 questions in `audit-benchmark-plan.md`, Q5 = "who was right?"). CLI reviewer (review_pairs.py) can display pairs. Store is JSONL (can add a field, or separate adjudication file). No adjudication field exists yet. No human review cadence scheduled (no reminder, no "time to review" flag).

**Tooling:** `persistence.py` (store_benchmark_fragment can add adjudication field; loadBenchmarkPairs can read it), `benchmark_pairs.jsonl` (real pairs — can add adjudication field), `review_pairs.py` (can display adjudication field, can prompt for adjudication), `audit-benchmark-plan.md` (review protocol, 5 questions), `docs/CSM-spec.md` (fidelity weighting needs who-was-right data to validate).

**Tune the gauntlet for E4:**
- Inline field on each pair vs separate adjudication file linked by traceId/operator — which is cleaner?
- Human-only adjudication vs partial automation (if CSM high + LLM/operator agree → mark "aligned" without full adjudication)?
- Adjudication reasoning quality — "LLM seemed right" vs specific reason. Minimum bar for useful data.
- Selection bias: if only high-fidelity pairs get adjudicated, data is biased.
- Review cadence scheduling gap: no reminder, no "time to review" flag — adjudication needs a cadence to accumulate.
- Does who-was-right need to be on the pair (for correlation with fidelity markers) or can it be a separate file?

---

## E5 — S6×C-loc: fidelity weighting under local-only framing

**Hypothesis:** If we implement fidelity weighting (per-pair weight from somatic/hci/axioms source, weighted aggregate) using provisional weights from `docs/CSM-spec.md` (somatic: user_self_report=1.0/default=0.3, hci: user_self_report=1.0/proxy=0.4, axioms: llm_derived=0.6/default=0.3), then the benchmark can compute weighted CSM aggregates on pairs already in `benchmark_pairs.jsonl` — even without somatic/HCI self-report data (all pairs low weight, but machinery works and validates when real fidelity data arrives).

**Current state:** `docs/CSM-spec.md` — fidelity adjustment section (explicit: NOT in CSM, separate weighting layer; provisional weights). `benchmark_pairs.jsonl` has 9 rows, all `somatic: default / hci: proxy / axioms: llm_derived` → weight = 0.3×0.4×0.6 = 0.072 per pair (low, but machinery works). No DB needed. `review_pairs.py` could display fidelity weights + weighted aggregates.

**Tooling:** `docs/CSM-spec.md` (fidelity adjustment, provisional weights, validation path), `persistence.py` (loadBenchmarkPairs reads pairs — fidelity weighting operates on loaded pairs), `benchmark_pairs.jsonl` (real pairs with fidelity markers — enough to compute weights), `review_pairs.py` (could display fidelity weights + weighted aggregates).

**Tune the gauntlet for E5:**
- Is fidelity weight multiplicative (somatic × hci × axioms) or additive? `docs/CSM-spec.md` says multiplicative.
- Are provisional weights right? somatic default 0.3 / user_self_report 1.0; hci proxy 0.4 / user_self_report 1.0; axioms llm_derived 0.6 / default 0.3. These are guesses — validation against who-was-right needed.
- Weighted aggregate: weighted mean CSM for SAGE across all pairs? Or per-decision-class?
- Is the weighting machinery useful even with all-low weights? (Yes — unblocks weighted evidence, but weights untrustworthy until validated.)
- Does weighted CSM replace unweighted CSM, or supplement it? (Supplement — unweighted CSM is the baseline, weighted CSM adjusts for fidelity.)

---

## E6 — S14×C-prod: post-compass composition under product framing

**Hypothesis:** If we define the smallest concrete post-compass hook (receipt-created event/webhook, one subscribable consumer) and start with one anticipatory briefing use case (receipt confirmation email or follow-up notice enriched with Y-gate-driven guidance: YELLOW → "bearing provisional; re-run after horizon closes"; RED → "conviction blockers; see court verdicts"; FORK → "two paths surfaced — review before committing"), then the product gains a post-compass composition layer without building the full Hermes workflow composition of operators (FM-10 structural gap).

**Current state:** Compass route returns receipt + Y-gate state + fire-and-forget runAudit + receipt confirmation email (T₀) + scheduled debrief email (T+7). No receipt-created event/webhook yet. Existing email infrastructure (Resend, receiptEmail, debriefEmail) is the hook point. FM-10 flags "No Hermes workflow composition of operators" as structural gap.

**Tooling:** `src/app/api/compass/route.ts` (creates receipt + returns it + fire-and-forget runAudit + emails), `src/app/emails/receiptEmail.ts` (receipt confirmation email — can be enriched with Y-gate guidance), `src/app/emails/debriefEmail.ts` (scheduled debrief — T+7), Y-gate state on receipt (route computes it).

**Tune the gauntlet for E6:**
- Is the hook subscribable (second consumer added later without rebuilding first) or hardcoded to one consumer?
- Y-gate guidance content: what does the user actually need to know for each Y-gate state? (YELLOW, RED, FORK, SCRATCH, DELTA, PARADOX, DRIFT, GREEN.)
- Anticipatory briefing timing: receipt confirmation (T₀) is immediate; is that the right moment, or should it be a follow-up notice (e.g. T+1 day, or horizon-close time)?
- Is the receipt-created event a webhook (HTTP POST to a URL) or an in-process event (callback in route.ts)? Webhook is subscribable; in-process is simpler.
- Does this overlap with the T+7 debrief email (which already exists)? Anticipatory briefing is sooner + Y-gate-driven; debrief is T+7 + outcome-oriented. Different purposes.
- FM-10 structural gap — this partially addresses it (smallest concrete hook exists) but full operator composition remains a gap.

---

## E7 — S12×C-opint: op20/op21 entanglement under operator-integrity framing

**Hypothesis:** If op20 and op21 are correctly characterized as "two sides of the same coin" (per user correction — architect session was wrong to call them unrelated), then D3 ("prod_receipt_to_op20_seed.py and audit service are unrelated pipelines") may still hold (different pipelines), but the framing of op20/op21 as independent operators may be wrong — they may share a contract, a phase derivation, or a kinematic lens that the audit service treats as if they were independent.

**Current state:** `prod_receipt_to_op20_seed.py` targets op20's seed contract (surface→phase). Audit service targets SAGE/LAB/BAR/KINTSUGI independently (no op20/op21 in the audit pipeline). `arcs_operator20.py` and `arcs_operator21.py` both exist (operator library, 16.6K LOC). User says op20/op21 entangled — two sides of same coin. Architect session said unrelated (wrong). Re-examination underway, not completed.

**Tune the gauntlet for E7:**
- What does "two sides of the same coin" mean concretely? Shared contract? Shared phase derivation? Shared kinematic output? Complementary (one forward, one backward)?
- Does the audit service's independence from op20/op21 (D3) hold if they're entangled? (D3 is about prod_receipt_to_op20_seed.py vs audit service — that's still a different pipeline from the audit sidecar. But if op20/op21 are entangled, are they both candidates for the audit pipeline?)
- Is op20 or op21 in scope for the operator audit pipeline (SAGE/LAB/BAR/KINTSUGI), or are they a separate layer?
- Does the entanglement affect Phase A (audit layer) or Phase B (compositor) decisions?

---

## E8 — S13×C-opint: phase derivation (surface→phase vs horizon→phase) under operator-integrity framing

**Hypothesis:** If surface→phase (op20 adapter, `prod_receipt_to_op20_seed.py`) and horizon→phase (translator, `audit-translator.ts`) are the same concept with different names, then the translator's phase derivation and the op20 adapter's phase derivation should converge — and currently they may diverge (different inputs, different mappings, different outputs). If they're genuinely different concepts, they should be explicitly documented as different (not silently assumed to be the same).

**Current state:** `prod_receipt_to_op20_seed.py` uses surface→phase (maps receipt surface state to op20 phase). `audit-translator.ts` uses horizon→phase (maps horizon enum to phase — TODAY/THIS_WEEK/etc. → phase_1/phase_2/etc.). User flagged they may be related, not different. Not yet resolved. `docs/audit-translator-validation.md` — horizon mapping gap (C-5) noted but phase derivation convergence not examined.

**Status:** OPEN — two phase derivations on disk, relationship unconfirmed.

**Tune the gauntlet for E8:**
- What does surface→phase produce? (op20 phase from receipt surface state.)
- What does horizon→phase produce? (translator phase from horizon enum.)
- Are the phase outputs comparable? (Both produce phase_1/phase_2/etc.? Or different phase systems?)
- Does the translator's phaseId match the op20 adapter's phase for the same receipt?
- Is horizon a surface attribute (part of the W-field in DEWY) or a separate dimension?
- If they're the same concept: why does one use surface and the other use horizon? (Surface is the receipt's state; horizon is the time window. Both could drive phase — but are they the same driver?)
- If they're different concepts: what's the conceptual boundary? (Surface = where you are; horizon = how long you have. Different inputs, possibly same phase output, or different phase systems.)

---

## E9 — S3×C-bmk: geometry detail only in rawResponse under benchmark scrutiny

**Hypothesis:** If `geometry.macros_on/off` (which macros the LLM considered and rejected) is only available inside `rawResponse` (not stored as separate DB columns or JSONL fields), then older receipts without `rawResponse` lose macro geometry detail, and `macro_tags` (which macros were on) partially compensates but doesn't capture which were considered and rejected — reducing the axiom derivation's fidelity for those receipts.

**Current state:** `rawResponse` is a JSON field on the Receipt (per Prisma schema). `geometry.macros_on/off` lives inside `rawResponse`.macros. `meta.macro_tags` is a separate field (which macros were on). Older receipts without `rawResponse` lose geometry detail. `docs/audit-translator-validation.md` — C-1 and C-7 gaps noted.

**Tune the gauntlet for E9:**
- Does `rawResponse` always get stored? (If not, geometry detail is lost for some receipts.)
- Does `macro_tags` compensate for missing geometry? (It captures which macros were on, but not which were considered and rejected.)
- Is the geometry detail (which macros considered + rejected) material to axiom derivation? (If the axioms are derived from macro presence, not macro consideration+rejection, then the detail may not matter.)
- Is this a correctness issue or a fidelity issue? (Data availability — older receipts have less information.)
- Is the fix: always store rawResponse, or add JSONL fields for macros_on/off, or accept the gap for older receipts?

---

## E10 — S15×C-vol: skills under volunteer-facing framing

**Hypothesis:** If we evaluate the 3 proposed skills (outcome-loop, kairos-detection, observatory-replay) under volunteer-facing framing, we can identify which skill has the clearest volunteer path — i.e., which one a volunteer can pick up, read the existing skills (arcs-operator-table, arcs-reading-sequence), and run an operator on their own decision as a learning exercise.

**Current state:** 3 skills proposed by task 3 swarm: `arcs-outcome-loop` (trigger: receipt off Y-gate GREEN or user claims outcome), `arcs-kairos-detection` (trigger: receipt with timing dimension), `arcs-observatory-replay` (trigger: replay a prior decision). Existing skills: `arcs-operator-table` (12,879 chars, comprehensive operator library), `arcs-reading-sequence` (substrate-first reading protocol). No "developing for ARCS" guide, no volunteer onboarding doc.

**Tune the gauntlet for E10:**
- Which skill's trigger is most accessible to a volunteer? (Outcome-loop needs a receipt that went GREEN or an outcome claim — accessible. Kairos-detection needs a receipt with timing dimension — accessible. Observatory-replay needs a prior decision to replay — accessible but requires existing data.)
- Which skill's structure is most self-contained? (Outcome-loop: SKILL.md + outcome-grade-card.md template. Kairos-detection: SKILL.md + kairos-axis-catalog.md. Observatory-replay: SKILL.md + observatory-status.md.)
- Which skill has the clearest "run an operator on your own decision" path? (Outcome-loop and kairos-detection are consumption-side; observatory-replay is analysis-side.)
- Does the volunteer need the audit service (port 8766) to run these skills? (No — these are product-side skills, separate from the audit pipeline.)
- Does the volunteer need the Prisma DB? (Outcome-loop writes Outcome records — yes, needs DB. Kairos-detection reads receipt timing — yes, needs DB. Observatory-replay reads prior receipts — yes, needs DB.)
- Which skill is most volunteer-ready given DB availability? (All need DB. Outcome-loop is the most concrete — it writes a record and produces a card.)

---

## E11 — S16×C-prod: configs under product framing

**Hypothesis:** If we evaluate the 2 proposed configs (nightly outcome sweep cron, ARCS_MODEL env-var convention) under product framing, we can identify which config has the clearest product path and which earns its keep first.

**Current state:** 2 configs proposed by task 3 swarm: nightly outcome sweep cron (scan for GREEN Y-gate receipts with no Outcome record within N days; emit prompt to invite outcome capture; OUTCOME_SWEEP_DAYS default 30, OUTCOME_SWEEP_MAX default 20), ARCS_MODEL env-var convention (single env var threading model choice through ADR-audit harness + compass route; fallback chain ARCS_MODEL → ANTHROPIC_MODEL → hardcoded default; per-surface override).

**Tune the gauntlet for E11:**
- Nightly outcome sweep: what's the cron mechanism? (Hermes cronjob? Uvicorn background task? External scheduler?) Needs a cron mechanism to exist.
- ARCS_MODEL: what surfaces need the override? (Compass route hardcodes claude-sonnet-4-6. ADR-audit harness has --model wired but inert for CIS path. Audit CLI --model → env var.)
- Which config is more product-facing? (Outcome sweep affects the user (outcome capture prompt). ARCS_MODEL affects model routing — more infra-facing.)
- Which config earns its keep first? (Outcome sweep makes outcome capture a habit — product-facing, high-yield. ARCS_MODEL makes model-routing ADRs falsifiable — infra-facing, important but less visible.)
- Does the outcome sweep need the Outcome model to exist? (Yes — writes Outcome records. Outcome model exists in Prisma schema per CLAUDE.md §31.)

---

## E12 — S17×C-opint: operator-audit skill under operator-integrity framing

**Hypothesis:** If the audit service + TS layer + benchmark cadence is a real subsystem with its own coordinate space (service shape, contract surface, persistence model, benchmark cadence, known gaps), then a light `arcs-operator-audit` skill may be worth creating — so an agent working on the audit layer has the coordinate space without re-discovering it each time. Alternatively, a summary folded into `arcs-operator-table` under "integration seam points" may be enough.

**Current state:** Audit service running on :8766 (health + 4 endpoints + batch, KINTSUGI fixed). TS layer built (audit-client.ts Promise.all, audit-translator.ts, audit-client-helpers.ts, types.ts). Compass route calls runAudit (fire-and-forget, AUDIT_SERVICE_URL-gated, D4 advisory persistence-only). Persistence (JSONL, read APIs, sampling toggle). Benchmark cadence (Phase 0-5, CSM specced, 7 plan gaps). 7 known gaps (C-1 through C-7). Swarm results (tasks 3, 6, 7, 8, 9 all complete). Decision locks (D1-D5 + A1-A4 + 7 user confirmations).

**Tune the gauntlet for E12:**
- Is the skill worth creating (agents will regularly touch the audit layer) or fold into operator-table (rarely touched)?
- What's the coordinate space? (Service shape: port 8766, health + 4 endpoints + batch. Contract: TS ↔ Python, fidelity markers. Persistence: JSONL, read APIs, sampling toggle. Benchmark cadence: Phase 0-5, CSM 0.65, review cadence gaps. Known gaps: C-1 through C-7. Decision locks: D1-D5, A1-A4, 7 confirmations.)
- Is the skill maintainable? (The audit layer is changing — new items added to backlog, CSM operationalized, fidelity weights validated. A skill that goes stale quickly is worse than no skill.)
- Does `arcs-operator-table` already have an "integration seam points" section? (If yes, folding in is cleaner. If no, a separate skill is cleaner.)
- Is the skill a live document (updated as the layer evolves) or a snapshot (captured at a point in time)? Live document is more maintainable but more work.

---

## Dispatch note

6 high-signal experiments (E1-E6) run the full 5-lens gauntlet. E7-E12 are lower-signal — surface as one-line results inline with the main dispatch, not separate agents.

**6 gauntlet agents (parallel):**
- Agent 1: E1 (somatic/HCI fidelity)
- Agent 2: E2 (horizon mapping)
- Agent 3: E3 (CSM operationalization)
- Agent 4: E4 (who-was-right persistence)
- Agent 5: E5 (fidelity weighting)
- Agent 6: E6 (post-compass composition)

Each agent reads this manifest + the files it needs (no writes — read-only gauntlet). Returns per-lens test + result + verdict (READY/REPAIR/SHELVE) + synthesis.

**E7-E12 surface inline** — included in the manifest so the main synthesis can reference them, but not dispatched as separate agents.

**Serialization:** all 6 parallel (independent experiments, no shared writes). No cross-agent dependencies. Review/alignment conversations (E7, E8, E14) are surfaced by the agents as explicit calls, not dispatched separately.
