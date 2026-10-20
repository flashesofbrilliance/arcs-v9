# JTBD graph pre-registration, amendment 5 (2026-10-19; number 4 is PR 1666)

Amends the s3 section of `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`. No threshold changes: every
rule stays zero-tolerance. Written by the s3 child (row `jtbd-graph-s3-gates`).

## What was seen first (disclosure)
The original names the six rules but does not define them. Before writing the definitions below, s3 counted
the s2 graph (origin/main 4beca333, 1022 atoms, 620 edges) with a plain any-edge degree test: orphan tools 374
of 646, orphan jobs 153 of 322, blockers with a resolve_by 0 of 5 (no backlog row carries the field), cycles 0,
dead path or evidence references 0. The definitions were then tightened twice (stricter, not looser), the second
time after the claims-skeptic round 1 found 14 evasion classes, so the counts rose: orphan tools 399 then 442,
orphan jobs 163, unprobed runtime-dep edges 2 targets then 4 edges. Round 2 (11 more classes) changed no count on main. No definition was chosen to lower a count.

## Definitions
- **Live edge**: known type, legal kind pair, from != to, both endpoints are atoms, non-empty evidence whose every
  item matches a format allowed for that type AND resolves (file:line and import: open in the repo; backlog: and
  route.tool: name a real backlog row; commit: and receipt: cannot be resolved offline and never attach).
  `blocks` edges never attach (being blocked is not use), and nothing attaches through a dep atom. Since skeptic
  round 2 the edge's `match` text must also sit on its first evidence item and name one of its endpoints (key,
  path or file name), so a real but unrelated line or row does not attach.
- **ORPHAN-TOOL**: a tool whose connected component over live serves/needs/design-dep/runtime-dep edges between
  non-dep atoms holds no job.
- **ORPHAN-JOB**: a job whose component (same edges) holds no tool.
- **BLOCKER-NO-RESOLVE-BY**: a blocker atom whose `resolve_by` (copied from its backlog row) is not a real YYYY-MM-DD
  date from today to today + 366 days. A far sentinel (9999-12-31) is not a date, and a lapsed date is not a plan:
  a blocker whose date passes turns the gate red until it gets a new one.
- **DEP-CYCLE**: a strongly connected component of size > 1 over needs + runtime-dep + design-dep together (mixed
  types, inferred edges included), or a self-loop of those types.
- **DEAD-FILE-REF**: an atom `path`, a file-valued source catalog line, a `file:line` or `import:` evidence item, or a
  probe entry that does not resolve inside the repo to a file (missing file, a directory, line past end, absolute or
  escaping path), or a memory path when no memory directory is present to check it (fail closed).
- **RUNTIME-DEP-NO-PROBE**: one finding per runtime-dep edge whose target has no entry in
  `runtime/specs/jtbd-graph-probes.json` whose file:line resolves, is code (.ts .tsx .js .mjs .cjs .py .sh), carries
  the needle outside a comment (comment and docstring state carried across lines), calls or awaits something
  outside string literals, and names the dep outside string literals (an env var as a whole word; a service by one
  of its declared words, `github` not a bare `gh`). Not closable by a line check: a probe line inside dead code
  (`if (false) ...`). Each probe entry is human-reviewed in the PR that adds it.
- SOURCE-DUP (schema checker): within a namespace, a repeated key; within a kind, a repeated cited line of a
  one-unit-per-line catalog; for prose catalogs a repeated (normalised file, line, service needle). KEY-LOOKUP (`--root`): the exact source form of the
  key is on the cited line (JSON `"name"` in a row of the namespace's own `"kind"` for tool-catalog tools, a backticked table cell or
  `process.env.` read for env vars, host plus same-row path for surfaces, the declared
  needle for services).

## Baseline (needs Zach's approval)
`runtime/specs/jtbd-graph-gate-baseline.json` holds the 614 ids that violate on main (442 + 163 + 5 + 4) so the
gate can be wired green. It is a ratchet: a held id passes, a new id fails, a held id that stops violating fails
as STALE-BASELINE, and any id not in the file's first version on main's first-parent history fails as BASELINE-GREW, so a growth
committed with the hook bypassed still fails on every later --check. A branch's own first version does not
count (it can be amended away, which happened once in this sprint: 399 then 442 held, disclosed above). Before
the file reaches main there is no reference and --check says so; if git cannot answer, the check fails closed. Growing it needs a new
dated amendment. If Zach rejects the baseline, the gate ships report-only or the s3 row returns to OPEN.
