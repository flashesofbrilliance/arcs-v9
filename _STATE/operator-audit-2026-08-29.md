# Operator Audit Thread — Session State (2026-08-29)

Paste as first message in fresh thread. Self-contained.

## What this is

ARCS v9 operator audit service (FastAPI sidecar + TS translator + 4 Python operators: SAGE/LAB/BAR/KINTSUGI). Path A → Path B evidence review. The operators audit the operators — dogfood design from day one.

## What landed this session

|| Commit / file | What |
||---|---|
|| `operators/audit_service/persistence.py` (653 lines) | compute_csm + fidelity_weight + WEIGHTS + weighted_csm + weighted_csm_by_operator + print_weighted_store. Lint clean. Sound board runs. |
|| `operators/audit_service/coverage_hooks.py` (373 lines) | Approach D: KAIros stub annotation + OP20 seed extraction + CONTRACT one-time check. Verified 36/36. |
|| `operators/audit_service/main.py` | Wired with record_coverage (once-per-receipt caching, thread-safe). Service on :8766 healthy. |
|| `operators/audit_service/play_instrument.py` | Synthetic enrichment + sound board on 9 sample pairs (1 real + 8 synthetic). Exit 0. |
|| `src/lib/audit-translator.ts` | HORIZON_MAP (lines 105-116) + somaticPrompt (386-420) + hci_score derivation. tsc clean. |
|| `docs/operator-audit-experiments.md` | 261-line manifest, 12 experiments E1-E12. |
|| `docs/task4-grounded-recommendations.md` | Full synthesis report (17,638 chars). |
|| `docs/volunteer-segment-briefs.md` | 4 volunteer segment briefs. |
|| `docs/audit-translator-validation.md` | Translator validation protocol + 7 gaps. |

## Production / running state

- FastAPI audit service: `uvicorn main:app` on 127.0.0.1:8766. Health: `{"ok":true,"operators":["SAGE","LAB","BAR","KINTSUGI"],"version":"1.0.0"}`.
- `npx tsc --noEmit` — clean (exit 0).
- `py_compile` on main.py, persistence.py, coverage_hooks.py, service.py — all exit 0.
- `benchmark_pairs.jsonl` — 1 real row (verify-coverage-001 / SAGE) + 0 synthetic. 5/9 rows have adjudication on the synthetic set.
- `audit_traces.jsonl` — lean operational trace.

## Known integrity bugs (persistence.py, NOT yet fixed 2026-08-29)

1. **FM-E3.1 — LlmReference ReadPath**: `SONIC_REFERENCE_KEY`/`LLM_REFERENCE_PROPAGATED` written on WritePath but not propagated to ReadPath. 8/9 pairs show "no" LLM reference. Fix: `_llm_reference_present(pair)` helper + update `print_weighted_store` + propagate on ReadPath.

2. **FM-E3.3 — per-operator subtask maps**: `_alignments` always uses `_SAGE_SUBTASKS` regardless of operator. LAB/BAR/KINTSUGI `llmOutput` fields not aligned against correct subtasks → 0 alignment on all 5 subtasks for non-SAGE pairs. Fix: `_alignments` should dispatch to per-operator subtask map.

Both produce distorted sound: all operators sound like SAGE, almost all pairs look like no LLM reference. User approved repairing both (2026-08-29).

## What's NOT yet done (still open)

- **Persist 9 real pairs** — `benchmark_pairs.jsonl` has 1 real row. The other 8 "pairs" referenced in the task list don't exist on disk yet. Need: ANTHROPIC_API_KEY + compass POSTs per traceId → audit fires → 4 operators → JSONL grows. OR continue synthetic until key available.
- **Persist CSM + fidelity_weight results** — currently computed at runtime only, not stored. Build 3 writes functions, doesn't store results. Storage is Phase 3 (storeCompositeOutcome).
- **`deleg_e5ae564863ac4b7596e97f32c6be1f8e`** (3-agent gauntlet: E1 somatic/HCI, E2 horizon, E3 CSM) — status unknown at session close. Do NOT re-dispatch without checking first.
- **Somatic/HCI collection** — HELD. Field type in place (somatic JSON column, somaticPrompt 6 Q, hci_score derivation). No collection path. Decision: hold.
- **Review cadence + monthly structured review template** — not started. Adjudication field exists on 5/9 synthetic pairs.
- **Translator validation script** — protocol written, waits for DB.

## Skills

- `arcs-operator-table` — `skill_view` returns [SKILL_PRUNED]. File on disk at `~/.hermes/profiles/arcs/skills/arcs-operator-table/SKILL.md` intact (12,541 chars). Read via `read_file` directly.
- `arcs-pre-mortem` — pruned, reload before acting.
- `claude-code` — pruned, reload before acting.

## cuadriver / system permissions

Enabled on macOS (Accessibility, Screen Recording). cua-driver can now do GUI/visual work (screenshots, clicks, typing, scroll, window focus). Not the blocker for "landing the plane on the agentic harness" — that's Build 3 + 4 completion + real receipts flowing. Code + data + process, already accessible via terminal + file tools.

## Memory consolidated this session

- Delegation `deleg_e5ae564863ac4b7596e97f32c6be1f8e` still IN PROGRESS (status unknown).
- persistence.py integrity bugs (FM-E3.1, FM-E3.3) confirmed + user approved repair.
- Coverage hooks FULLY VERIFIED — no remaining work.
- Somatic/HCI: HOLD collection, KEEP field type (approved 2026-08-29).
- arcs-operator-table skill: skill_view pruned, file on disk intact — read via read_file.
- cuadriver/system-permissions enabled — GUI work unlocked, not the harness blocker.
- Build 3 ON DISK, Build 4 runs on 1 pair, integrity bugs distort sound.

## Next session — first move

1. Check `deleg_e5ae564863ac4b7596e97f32c6be1f8e` status (ls delegation cache + tail task logs).
2. If gauntlet returned: read subagent summaries, synthesize E1/E2/E3 verdicts.
3. Repair persistence.py integrity bugs (FM-E3.1 + FM-E3.3) — mechanical fixes, read offset 384-405 for _alignments, offsets 95-270 for WritePath/ReadPath.
4. Re-run play_instrument.py after fix — sound should vary by operator, LLM reference should show YES for enriched pairs.
5. If ANTHROPIC_API_KEY available: drive 9 compass POSTs → real llmOutput → real CSM distribution.
6. If no key: continue synthetic until key available. Handoff stub notes this.

## File status

|| File | Status | Notes |
||------|--------|-------|
|| `operators/audit_service/persistence.py` | ✅ on disk, lint clean | 2 integrity bugs (FM-E3.1, FM-E3.3) |
|| `operators/audit_service/coverage_hooks.py` | ✅ on disk, verified | Approach D, 36/36 |
|| `operators/audit_service/main.py` | ✅ patched, service healthy | record_coverage wired |
|| `operators/audit_service/play_instrument.py` | ✅ on disk, exit 0 | 9-pair sound board |
|| `src/lib/audit-translator.ts` | ✅ modified, tsc clean | HORIZON_MAP + somaticPrompt |
|| `docs/operator-audit-experiments.md` | ✅ on disk | 12 experiments |
|| `docs/task4-grounded-recommendations.md` | ✅ on disk | synthesis report |
|| `docs/audit-translator-validation.md` | ✅ on disk | protocol + gaps |
|| `docs/volunteer-segment-briefs.md` | ✅ on disk | 4 briefs |
|| `operators/audit_service/benchmark_pairs.jsonl` | ⚠️ 1 real row | needs 8 more (real or synthetic) |
|| `operators/audit_service/verify_coverage.py` | ✅ on disk, PASS | end-to-end verification |
|| `operators/audit_service/_verify_hooks.py` | ✅ on disk, PASS | 36/36 assertions |
|| `operators/audit_service/_verify_wiring.py` | ✅ on disk, PASS | functional TestClient |
