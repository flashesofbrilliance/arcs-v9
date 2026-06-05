# ARCS Session State

**Last updated:** 2026-06-05 (v2.5.0)
**Environment:** Claude Code on the web (cloud)
**Branch:** `claude/observability-milestone-mapping-345ho` — ⚠️ NOT merged to main
**Last commit (arcs-v9):** bbeb8a8 — feat(observatory): hide=strip-to-subject; regen deployed data clean
**Last commit (arcs-care):** 136add1 — perf(cron): batch T+7 emails (unchanged this session)

## ⚠️ Cloud snapshot sync gap

The cloud setup script fetches `_STATE/snapshot.json` from the **main** branch. This session
wrote it on a feature branch — the next cloud session won't see it until merge. A local
`/handoff-pickup` reads the working-tree file and is fine. **To close: merge this branch to main.**

## Status

- arcs-v9 Vercel: ✅ LIVE — https://app.arcs.care (unchanged this session)
- arcs-v9 Auth: ✅ magic link end-to-end (unchanged)
- arcs-v9 DB: ✅ xbbpiryokswwvcrcutge / arcs_app / 7 tables (unchanged — no migration this session)
- arcs-care: ✅ LIVE (unchanged)
  - Item 1 (case study): 🔒 Dark — pending NEXT_PUBLIC_CASE_STUDY_APPROVED
  - Items 2 + 3 (email capture, spots badge): ✅ Live

## What landed this session (ADR-023 + Observatory)

- **ADR-023 DECIDED** — Observability as a Superionic Goal Lattice. Inferred weighted folksonomy
  DAG over receipts; observe edge-weight tightening not node-state; three governed counter-forces
  (edge-decay/contrarian/Drift-Sentinel) hold the superionic band. FMEA + Conductor-loop arch.
  Build GATED at 100+ receipts (L6). `9f669fa`, `48b1e6f`.
- **lattice-pressure-rom.json** — ROM v0.1.0, L7-governed pressure constants, self-tuning FORBIDDEN.
- **lattice_sim.py** — structural load-test harness. `7bc512c`.
- **5-agent adversarial pass** — corrected 4 over-claims (recorded in ADR Loki + ROM `_adversarial_grounding`).
- **Observatory wired** — repo-agnostic `build_observatory.py`; `--attribution hide` = strip-to-subject;
  `data.jsx` regenerated clean for Deloitte demo; turbopack.root + absolute asset paths. `27ee318`→`bbeb8a8`.

## Open sprint

```
1. Merge claude/observability-milestone-mapping-345ho → main   (closes cloud snapshot sync gap)
2. Panel/Chip design system components (ADR-009)               READY
3. ADR-006 branching strategy (first-external-user gate)       READY
4. arcs-care: flip NEXT_PUBLIC_CASE_STUDY_APPROVED (if Dan confirmed)
```

## Key infra facts (for next session)

- DB: `xbbpiryokswwvcrcutge` / `arcs_app` role / port 6543 pooler
- Vercel project: `prj_aKmLj1UvT2oaDSH4KIAqEPaULqx9` / team `zachharris-3439s-projects`
- State snapshot: `_STATE/snapshot.json` — cloud setup script reads it from **main** raw URL
- `/arcs-handoff` is local-only; in cloud use the `/handoff` skill

## Next session

/handoff-pickup → confirm branch merge state → merge to main OR Panel/Chip (ADR-009) OR ADR-006
