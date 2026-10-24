<!--
session: claude-handoff-provenance-bench
branch: claude/handoff-provenance-bench
head: eb749100
created_at: 2026-10-20T18:17:20Z
-->
> Ran the pre-registered provenance-retrieval benchmark once, published every result including the failures, and merged the one change that passed (the Librarian lineage index).

## Goal / true north
Find out, with a pre-registered test, which faster provenance-retrieval layers beat the current per-pair matcher without adding wrong-source answers, and adopt only what passes.

## What changed
- #1629 merged with --merge (`3d144a22`): raw results of the single run (all but H8) and `_PATTERNS/2026-10-18-provenance-retrieval-results.md`. Receipt 2026-10-18--provenance-bench-results-pr1629--ZH.
- #1745 merged with --merge (`517ae98a`): the H8 run, `h8.json`, a one-line `load_librarian` fix, report addendum. Receipt 2026-10-20--provenance-bench-h8-pr1745--ZH.
- #1588 merged with --merge (`d39c9ec2`): Operator 21 Librarian posting-list lineage index. Receipt 2026-10-20--librarian-lineage-index-pr1588--ZH.

## Current state
- Source of every number below: `scripts/provenance_bench_score.py` over the published verdict files; registration in `_PATTERNS/2026-10-18-provenance-retrieval-prereg.md`.
- Results: H1 PASS (4,697x), H2 PASS, H3 FAIL on the 85% kill line (S 85.0%), H4 PASS, H5 KILL (37 false negatives in 600), H6 PASS, H7 PASS, H8 PASS (lineage 80.5% of time, 0 mismatches, 5.15 s to 1.55 s, exponent 1.183 vs bar 1.2), H9 PASS. Primary safety: 0 confident-wrong in 800.
- Shingle index and Bloom prefilter are NOT adopted. Hash verification and speaker attribution unchanged are supported.
- An independent claims-skeptic agent (same model family) re-scored the raw outputs and matched the frozen scorer; its script is not archived.

## Decisions made
- Zach: merge on Vercel-only checks; merge 1588 only after H8 passed.
- Run H8 only once the machine was quiet; it took four waits and one fresh worktree. Not run under load 15 or higher.

## Open decisions (waiting on Zach)
1. Zach: the tower's decision queue (HUD rulings A1, compass anti-distillation A2, ADR-085 A3, stale backlog fates A4, and the one-way doors) in `_PROPOSALS/2026-10-19-tower-decision-queue.md` on the tower's branch.

## Open (other)
1. Commit the skeptic's re-score script so the check can be rerun (currently scratch only).
2. universe-atlas-tokens row still OPEN; the canon atlas HTML stays uncommitted (token_source_gate).

## Next action
Zach rules on the tower queue; this thread has nothing blocking.

## Cold-start recipe
Read `_PATTERNS/2026-10-18-provenance-retrieval-results.md`, then `python3 scripts/provenance_bench_score.py --results tests/fixtures/provenance-bench/results/run-2026-10-18`.

### Notes: Shavasana
- Mechanical half: exhale shows 0 commits because it counts this fresh branch; the three merges above are in git on main. Sycophancy OK (dissent 2).
- Attachment release: the H8 exponent pass (1.183 vs 1.2) is a single run on a machine at load 2.7 with swap near full; downgraded to "passed, thin margin". Somatic: not asked. Disposition: release.
