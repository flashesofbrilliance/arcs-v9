# JTBD baseline follow-ups: COMPOST list, health-probe use cases, orphan-job grooming (2026-10-20)

Rule: `_PATTERNS/2026-10-20-jtbd-baseline-burndown-rule.md` amendments 1 and 2. Nothing here is deleted or moved.
Each list needs Zach's ruling.

## 1. COMPOST candidates (25)
Orphan scripts and operators that no code or config file calls, and that no hook, AGENTS.md, rule,
command or skill names. Last commit date first. Fates: compost (move to `scripts/_archive/` through
`archive_move_gate.py`), keep and give it a job (a backlog row's route.tool), or keep as a manual tool.

| Last commit | Path |
|---|---|
| 2026-06-16 | `operators/arcs_diagnostic.py` |
| 2026-06-16 | `operators/seed_test_receipts.py` |
| 2026-07-08 | `operators/waveform_optimizer.py` |
| 2026-09-07 | `scripts/forge_finalize.sh` |
| 2026-09-07 | `scripts/nftt_dropcap_lint.py` |
| 2026-09-10 | `scripts/second_pass_ledger.py` |
| 2026-09-24 | `scripts/baseline-prod-migrations.sh` |
| 2026-10-04 | `scripts/blog_provenance.py` |
| 2026-10-04 | `scripts/gravity_well_fork_scan.py` |
| 2026-10-04 | `scripts/linkedin_render.py` |
| 2026-10-04 | `scripts/snapshot_prune_ui_artifacts.py` |
| 2026-10-05 | `scripts/forge_finalize_one.sh` |
| 2026-10-05 | `scripts/trust_name_leak.py` |
| 2026-10-06 | `scripts/bank_event.py` |
| 2026-10-06 | `scripts/risk_sweep_cron.sh` |
| 2026-10-07 | `scripts/artifact_reuse_catalog.py` |
| 2026-10-15 | `scripts/coherence_sweep.py` |
| 2026-10-17 | `scripts/doc_classify.py` |
| 2026-10-17 | `scripts/era_b21.py` |
| 2026-10-18 | `scripts/decision_geometry_ret.py` |
| 2026-10-18 | `scripts/ledger_score.py` |
| 2026-10-18 | `scripts/phosphor_playlog_summary.py` |
| 2026-10-18 | `scripts/provenance_bench_dataset.py` |
| 2026-10-18 | `scripts/recall_coherence_ledger.py` |
| 2026-10-18 | `scripts/tao_print_export.py` |

## 2. Not compost: in use, but the graph cannot see it (13)
The amended rule flagged these, but a hook, AGENTS.md, a rule or a command runs or documents them.
The graph calls them orphans because the adapter draws no edge for a pre-commit hook calling a
script. That is a gap in the adapter, so none of these is compost. Backlog row
`jtbd-graph-hook-invocation-edges` takes the fix.

| Last commit | Path | Named by |
|---|---|---|
| 2026-07-21 | `scripts/score_me.py` | .claude/rules/operators-and-workers.md  |
| 2026-08-28 | `scripts/canon_propagation_nightly.sh` | .claude/commands/canon-review.md  |
| 2026-09-23 | `scripts/html_div_balance_lint.py` | scripts/git-hooks/pre-commit  |
| 2026-09-23 | `scripts/tooltip_link_lint.py` | scripts/git-hooks/pre-commit  |
| 2026-09-24 | `scripts/gutter_consistency_lint.py` | scripts/git-hooks/pre-commit  |
| 2026-09-28 | `scripts/migration_rls_lint.py` | scripts/git-hooks/pre-commit  |
| 2026-10-04 | `scripts/case_world_sync.py` | scripts/git-hooks/pre-commit  |
| 2026-10-04 | `scripts/export_apollo.py` | .claude/rules/operators-and-workers.md  |
| 2026-10-06 | `scripts/case_evidence_lint.py` | scripts/git-hooks/pre-commit  |
| 2026-10-06 | `scripts/resume_ats_render.py` | scripts/git-hooks/pre-commit  |
| 2026-10-17 | `scripts/analytics_coverage_gate.py` | scripts/git-hooks/pre-commit  |
| 2026-10-18 | `scripts/archive_move_gate.py` | AGENTS.md scripts/git-hooks/pre-commit  |
| 2026-10-20 | `scripts/sync_worktree.sh` | AGENTS.md  |

## 3. Health-probe use cases for the 3 held runtime deps (Zach to flag)
The github edge left the baseline in 51ddf069, when ship_docs.sh began merging through safe_merge.sh.
The gate wants a code line that calls the dep and names it outside a string literal. No line like
that exists today. These options would each be real probes:

| Held edge | Option |
|---|---|
| `dep:env:DATABASE_URL <- outcome_funnel.py` | A `/api/health?deep=1` step that opens a connection from `process.env.DATABASE_URL` (the shallow probe already runs `SELECT 1` through Prisma) |
| `dep:env:DATABASE_URL <- universe_jtbd_adapter.py` | Probably a false edge: the adapter reads `DATABASE_URL` only inside its own self-test fixture text. Fix the edge, not the probe |
| `dep:service:vercel <- deploy-prod.sh` | deploy-prod.sh already curls `api.vercel.com` for domains; a named `vercel_health()` that does it would count, or a Vercel step in the deep health route |

## 4. Orphan jobs (163) to groom
114 are OPEN or READY rows, 8 are HOLDING/RUNNING/BLOCKED, and 41 are terminal or mined. For each one:
name the tool that does it (append it to route.tool), compost the row, or mark the row as human-only
work. Backlog row `jtbd-orphan-jobs-groom` takes this on, starting with the OPEN and READY rows.
