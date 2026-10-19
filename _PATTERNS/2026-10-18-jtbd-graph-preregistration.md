# JTBD graph: pre-registered gates for sprints 1 to 4 (2026-10-18)

Status: fixed. Written by the Sprint 0 child (row `jtbd-graph-s0-schema`, ADR-089) and committed
before any sprint counts a node, an edge or a query result. Changing a threshold below after a
count has been seen needs a new dated amendment file that says what was seen first; editing this
file in place after s1 starts is a gate failure.

Disclosure: before writing this file, Sprint 0 read the size and key uniqueness of each source
catalog to design the ID scheme (tool-catalog 327 tools, backlog 303 rows, registry 28 operators,
surface-catalog 282 rows, package.json 34 deps, memory 334 files, _PATTERNS 70 files). None of
the thresholds below depends on those numbers: s1 is exact reconciliation, s2 to s4 are ratios
over outputs that do not exist yet.

## s1 nodes (`jtbd-graph-s1-nodes`)
- Per source, emitted atom count == the source's own count of natural keys, exactly. No
  tolerance. Sources and keys are the namespaces in `runtime/specs/jtbd-graph-schema.json`.
  The 6 known tool duplicates are counted once by key; any dedupe is listed by key in the PR.
- Every atom carries `source.catalog`, `source.key`, `source.line`; a sample of 20 atoms drawn
  by `random.Random(20261018)` over the sorted id list must each resolve to that line.
- `scripts/jtbd_graph_schema_check.py` reports 0 findings on the emitted graph.
- A SOURCE-DUP (duplicate natural key in one source) fails s1 until fixed at source.
- Mined jobs (memory, _PATTERNS) are emitted only for files that state a job; the rule for
  "states a job" is written in the s1 PR before the miner runs, and Zach's labelling pass on a
  sample of 30 (same seed) must agree with the miner on at least 24 of 30 (80%), else the
  mined-job namespaces ship empty and s1 ships backlog jobs only.

## s2 edges (`jtbd-graph-s2-edges`)
- Mechanical share: edges with `inferred=false` / all edges >= 0.90.
- Every edge passes the checker (evidence format matches its type, legal kind pair).
- Counter-agent sample: 20 edges drawn by `random.Random(20261018)` over the sorted
  (from, type, to) list, stratified so inferred edges are drawn in proportion. All 20 must be
  confirmed against the cited evidence. One unconfirmed edge fails the gate; the fix is to the
  rule that produced it, then a fresh 20 with seed 20261019.
- Cycle detector runs; any cycle in `needs` or `runtime-dep` is listed, not silently dropped.

## s3 gates (`jtbd-graph-s3-gates`)
- Six rules (orphan tool, orphan job, blocker without resolve_by, dependency cycle, dead file
  reference, runtime-dep without a health probe), each proven fail-on-bad and pass-on-good with
  a committed fixture pair (AGENTS.md gotcha 15). A rule without both proofs does not ship.
- `--check` green on main at merge; a seeded orphan tool in a scratch commit turns it red.

## s4 retrieval (`jtbd-graph-s4-retrieval`)
- Query set: 20 job statements, written and labelled with the one correct tool id each BEFORE
  either system is run, by Zach (or, if he delegates, by a labeller who has not seen either
  system's output). At least 5 of the 20 come from real asks in session transcripts, not from
  catalog jtbd lines (guards against the catalog-text leak). The file is committed and its
  commit sha recorded before the first run.
- jtbd(job) top-1 correct >= 16 of 20 (80%).
- Baseline, today's /catalog: the `.claude/commands/catalog.md` procedure as committed at the
  s4 start sha, run by a fresh session given only that command and `runtime/specs/tool-catalog.json`,
  one shot per query, same model tier as the s4 run, its single recommended tool scored top-1
  against the same labels. No retries, no follow-up questions answered.
- Win condition: jtbd top-1 count > /catalog top-1 count (strictly more, out of 20) AND >= 16.
  A tie or a loss kills s4: stop, report both scores, do not wire /prior-art or /catalog to it.
- Output budget: each jtbd(job) answer under 1,000 tokens (counted as len(text)/4); a breach is
  a fail for that query.

## Kill condition for s0 itself
Jobs must get stable ids from backlog rows, memory and _PATTERNS. Answer and sample are in
ADR-089, not here, so this file carries no counts that the answer could have tuned.
