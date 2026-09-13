# ARCS v9 Operator Audit — Consolidated Session Memory (2026-08-29)

> Pickup document for a fresh session. Read this first; the detailed handoff is in `_handoff.json` and `_STATE/operator-audit-2026-08-29.md`.

## Session identity

- **What:** Operator audit service — FastAPI sidecar running 4 Python operators (SAGE/LAB/BAR/KINTSUGI) against compass receipts. The operators audit the operators.
- **Where:** `operators/audit_service/` (Python) + `src/lib/` (TS translator/client)
- **Why:** Path A → Path B evidence review. Dogfood the operator library against itself.
- **Branch:** `feat/resume-pwa-theming`
- **Date:** 2026-08-28 → 2026-08-29

## What landed this session

### Build 3 — CSM instrumentation (persistence.py, 653 lines)

All on disk, lint clean (`py_compile` exit 0), sound board runs:

| Function | Purpose |
|---|---|
| `compute_csm(pair)` | Unweighted CSM: alignment×0.40 + delta×0.30 + (1−coherence_loss)×0.20 + (1−severity)×0.10 → [0,1], threshold 0.65 |
| `fidelity_weight(pair)` | Per-pair weight from somatic/hci/axioms fidelity markers |
| `WEIGHTS` | Dict[str, float] — SAGE=1.0, LAB=1.15, BAR=0.95, KINTSUGI=1.05 (provisional, unvalidated) |
| `weighted_csm(pairs)` | Weighted aggregate across all pairs |
| `weighted_csm_by_operator(pairs)` | Per-operator weighted CSM |
| `print_weighted_store()` | Sound board — prints per-pair table + per-operator summary + weighted aggregates + who-was-right + horizon mapping |

### Approach D coverage hooks (coverage_hooks.py, 373 lines)

Verified 36/36 assertions (`_verify_hooks.py` exit 0). Wired into `main.py` with once-per-receipt caching (thread-safe, keyed traceId+sessionVersion).

| Hook | What it does |
|---|---|
| KAIros stub annotation | Tier 1 — annotates without running |
| OP20 seed extraction | Tier 1 — extracts seed from receipt |
| CONTRACT one-time check | Tier 1 — runs once, records `legacy_contract_passes = False` for all 4 operators (honest finding: they implement Phase 4 legacy contract, not Phase 6) |

### Coverage verification (all PASS)

- `_verify_hooks.py` — 36/36 assertions, exit 0
- `verify_coverage.py` — end-to-end, exit 0 PASS
- `_verify_wiring.py` — functional TestClient, operator_coverage lands once, exit 0 PASS

### play_instrument.py — 9-pair sound board

Exit 0. 1 real pair (verify-coverage-001/SAGE from benchmark_pairs.jsonl) + 8 synthetic (calibration data). Synthetic enrichment happens at runtime — JSONL not mutated.

**Sound on 9 pairs:**
- SAGE: 3 pairs, mean CSM 0.464 (low — subtasks have non-trivial deltas)
- LAB: 2 pairs, mean CSM 0.785
- BAR: 2 pairs, mean CSM 0.906
- KINTSUGI: 2 pairs, mean CSM 0.787
- Overall weighted CSM: 0.705
- Fidelity weight: 0.072 on every pair (somatic=default + hci=proxy + axioms=llm_derived all push low)
- 5/9 pairs have adjudication (t2/LAB operator, t3/BAR llm, t5/SAGE split unresolved, t7/BAR operator, t8/KINTSUGI undecided unresolved)

### TS layer — clean

- `audit-translator.ts` — HORIZON_MAP (lines 105-116), somaticPrompt (386-420), hci_score derivation, horizonToPhaseId
- `tsc --noEmit` — exit 0, zero errors/warnings

### Audit service — running

- `127.0.0.1:8766` — `{"ok":true,"operators":["SAGE","LAB","BAR","KINTSUGI"],"version":"1.0.0"}`

## Integrity bug status (persistence.py)

### FM-E3.3 — DISPROVEN (2026-08-29)

**Earlier hypothesis:** `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator. Non-SAGE operators get 0 alignment on all 5 subtasks.

**Ground truth check:** Verified false. `_alignments` dispatches correctly:
- SAGE pair → 5 SAGE subtasks (nci_score, coherence_pct, signal_classification, axiom_alignment, court)
- LAB pair → 5 LAB subtasks (loki_threat, bayesian_posterior, advisor_consensus, hidden_assumptions, worst_case)
- Different keys → different maps. The dispatch at lines 390-397 is correct.

**Status:** Removed from bug list. No fix needed.

### FM-E3.1 — ROOT CAUSE REFRAMED (2026-08-29)

**Earlier hypothesis:** LlmReference ReadPath not propagated (SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED written on WritePath but not propagated to ReadPath). 8/9 pairs show "no" LLM reference.

**Ground truth check:** The 8/9 "no" count reflects empty `llmOutput={}` on disk — the store was never populated with real compass output. No separate ReadPath propagation bug confirmed. (Constants SONIC_REFERENCE_KEY/LLM_REFERENCE_PROPAGATED not found anywhere in repo — grep exit 1 across operators/, src/lib/, src/app/.)

**Status:** Root cause is missing data, not a ReadPath bug. Fix direction changed from "propagate on ReadPath" to "drive real compass POSTs (needs ANTHROPIC_API_KEY) to populate llmOutput, then re-check."

## What's confirmed clean

- `npx tsc --noEmit` — exit 0, zero errors/warnings
- `py_compile` on main.py, persistence.py, coverage_hooks.py, service.py — all exit 0
- Audit service health: 127.0.0.1:8766, ok:true
- Coverage hooks: 36/36 + PASS + PASS
- Functional TestClient: operator_coverage lands on stored pair exactly once
- `_alignments` dispatches correctly to per-operator subtask maps (FM-E3.3 disproven)

## What's NOT yet done

### Immediate (next session first move)

1. **Check `deleg_e5ae564863ac4b7596e97f32c6be1f8e` status** — 3-agent gauntlet (E1 somatic/HCI, E2 horizon, E3 CSM). IN PROGRESS UNKNOWN at session close. Do NOT re-dispatch without checking first.

2. **Drive real compass POSTs** — needs ANTHROPIC_API_KEY (already in `.env.local` line 1). 9 POSTs to `/api/compass` for each traceId → fills `llmOutput` on benchmark_pairs.jsonl → instrument plays on real data. The key is set; the flow just hasn't been exercised.

3. **If FM-E3.1 still shows "no" after real llmOutput populated** — then investigate ReadPath propagation. But ground truth says the store is empty, not that ReadPath is broken.

### Pending (user decisions needed)

- **Per-invocation caps for factory wave 1** — proposed `--max-turns 15`, `--max-budget-usd` in $0.50–$2/experiment range. NOT confirmed.
- **E7–E12 handling** — (a) second factory wave of 6 bounded invocations, or (b) orchestrator produces one-line summaries from manifest directly. NOT confirmed.

### Backlog (not blocked)

- JTBD-A: Kernel legibility — verify freshness after E7/E8 + op20/op21 entanglement correction
- JTBD-B: Surface composition declarations — each surface declares what kernel pieces it composes + voltage/current
- JTBD-C: Seam contracts — shared-state exchange points named + guarded (gap: DB seam guards not yet designed)
- JTBD-D: De/composability — can re-compose surface by swapping kernel piece? `ARCS_MODEL` env-var convention is a proposal, not wired
- JTBD-E: Self-sovereignty boundary — harness enforces vs surface declares
- JTBD-F: RAG as kernel-discovery + state-integrity layer — what does RAG index? GIGI substrate seam point at `compass/route.ts` [TBD P3], root-level open question
- `harness/README.md` — create on first harness commit
- `operators/README.md` TODO block — enumerate harness-facing operator modules, contract-stable vs internal, multi-tenant isolation audit

## Delegation status

### Active (check first)

| ID | Status | Tasks |
|---|---|---|
| `deleg_e5ae564863ac4b7596e97f32c6be1f8e` | IN_PROGRESS_UNKNOWN | E1 somatic/HCI, E2 horizon mapping, E3 CSM operationalization |

### Completed

| ID | Status | Notes |
|---|---|---|
| `deleg_ea9dfba2` | RETURNED | E7-E11 gauntlet, 6 agents, 5-lens test (~17:37:35 2026-08-28) |
| `deleg_ec01cca3` | COMPLETED_TRUNCATED | 5 tasks (compute_csm, adjudications, HORIZON_MAP, fidelity_weight, play), delivery truncated |
| `deleg_78da8064` | RETURNED_PARTIAL | Instrument-build batch, 2 timed out resolved via direct writes |
| `deleg_e19fff61` | COMPLETED_ALL_429 | 6-agent E1-E6 gauntlet, all hit 429 + exhausted budget |

## Files on disk

### operators/audit_service/

| File | Lines | Status |
|---|---|---|
| `persistence.py` | 653 | ON DISK, lint clean, 2 integrity items (E3.3 disproven, E3.1 reframed) |
| `coverage_hooks.py` | 373 | ON DISK, verified 36/36 |
| `main.py` | — | Patched, service healthy, record_coverage wired |
| `service.py` | — | Unchanged, lint clean |
| `play_instrument.py` | — | 9-pair sound board, exit 0 |
| `verify_coverage.py` | 195 | PASS exit 0 |
| `_verify_hooks.py` | 146 | 36/36, PASS exit 0 |
| `_verify_wiring.py` | 146 | PASS exit 0 |
| `benchmark_pairs.jsonl` | — | 1 real row (verify-coverage-001/SAGE) + 0 synthetic on disk |
| `audit_traces.jsonl` | — | Lean operational trace |

### src/lib/

| File | Status |
|---|---|
| `audit-translator.ts` | HORIZON_MAP + somaticPrompt + hci_score + horizonToPhaseId, tsc clean |
| `audit-client.ts` | runAudit() Promise.all parallel, D4 advisory persistence-only |
| `types.ts` | ReceiptJSON + AuditRequestShape |

### Docs

| File | Status |
|---|---|
| `docs/operator-audit-experiments.md` | 12 experiments E1-E12 |
| `docs/task4-grounded-recommendations.md` | Synthesis report COMPLETE |
| `docs/audit-translator-validation.md` | Protocol + 7 gaps |
| `docs/volunteer-segment-briefs.md` | 4 briefs |
| `docs/operator-audit-thread-state.md` | State + build backlog |

## Decisions (carried forward)

| Decision | Status |
|---|---|
| Somatic/HCI | HOLD collection, KEEP field type (somatic JSON column + somaticPrompt 6Q + hci_score derivation). User approved 2026-08-29. |
| Coverage approach | Approach D (hybrid): 4 benchmarked Tier 2, 3 Tier 1 (KAIros stub, OP20 seed, CONTRACT one-time), 1 deferred (CURATOR). |
| Contract finding | All 4 operators fail Phase 6 (missing name property). Honest Tier 1 finding, not coverage win. |
| Batch endpoint | Convenience, not merged |
| Advisory | Persist, don't inject (D4) |
| op20/op21 | Entangled — two sides of the same coin, not unrelated |
| Phase derivation | Confirm, don't reconcile. translator horizonToPhaseId and op20 adapt() are different concepts sharing a name. |
| Signal proxy | Treat 12-element proxy as seam, not real data. Semantically empty. |
| operators/ vs harness/ | operators/ = atomic catalog only. harness/ gets own root dir at repo root. Contract-shaped synthesis, not total separation. |

## Auth blocker (factory)

Claude Code v2.1.247 at `/Users/zharris/.local/bin/claude` — OAuth session expired. `claude auth status` reports `loggedIn=true` but `claude -p` fails mid-call with "OAuth session expired and could not be refreshed." Until user refreshes via `claude auth login --sso`, no `claude -p --output-format json` measurement can run (the per-invocation cost capture primitive the factory needs).

## Next session first move (priority order)

1. Check `deleg_e5ae564863ac4b7596e97f32c6be1f8e` status
2. If returned: synthesize E1/E2/E3 verdicts
3. Drive 9 compass POSTs for real llmOutput (ANTHROPIC_API_KEY already in `.env.local`)
4. Re-run play_instrument.py on real data
5. If FM-E3.1 still shows "no" after real llmOutput populated: investigate ReadPath propagation
6. Resolve pending user decisions (per-invocation caps + E7-E12 handling) before firing factory wave 1
7. Refresh Claude Code auth if factory is the active pickup

## Key files for pickup

- `/Users/zharris/arcs-v9/_handoff.json` — full land_the_plane handoff console (33,162 bytes). Load via `load_handoff("land_the_plane")` in a fresh Hermes instance.
- `/Users/zharris/arcs-v9/_STATE/operator-audit-2026-08-29.md` — narrative handoff (94 lines)
- `/Users/zharris/arcs-v9/_STATE/handoff-2026-08-29.md` — session handoff narrative (98 lines)
- `/Users/zharris/arcs-v9/operators/audit_service/persistence.py` — 653 lines, ground truth for CSM instrumentation
- `/Users/zharris/arcs-v9/operators/audit_service/play_instrument.py` — sound board script
- `/Users/zharris/arcs-v9/operators/README.md` — composition boundary section (TODO-form)
- `/Users/zharris/arcs-v9/docs/operator-audit-thread-state.md` — state + backlog
