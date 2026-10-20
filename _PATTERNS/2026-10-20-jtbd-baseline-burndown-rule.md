# JTBD gate baseline burn-down: pre-registered rule (2026-10-20)

Written and committed before any held id was counted or ranked. Applies to
`runtime/specs/jtbd-graph-gate-baseline.json` (614 held ids on 2026-10-19). Triage entries
(`runtime/specs/jtbd-graph-triage.json`) are out of scope.

## Ranking (value first)
- Tools, tier A: the tool is named (exact token, see F1) in the text of a backlog row whose state is
  OPEN, READY, HOLDING, RUNNING or BLOCKED. Tier B: named only in DONE, COMPOSTED or SUPERSEDED rows.
  Tier C: named by no row. (An orphan tool cannot be returned by `jtbd(job)`, which walks job edges,
  so "returned by jtbd or /catalog" reduces to "a live job names it".)
- Jobs: tier A = rows OPEN or READY; tier B = HOLDING, RUNNING, BLOCKED; tier C = terminal states and mined jobs.
- Blockers: ordered by the latest YYYY-MM-DD in the row's status_note.

## Fix rules (mechanical only)
- F1 route.tool: append a tool to a row's route.tool only when the row's own jtbd, gates, trigger or
  status_note names it by an exact token (full path, script or operator basename, `/command`, or the
  command/skill name as a whole word) in a sentence that does not state it as an analogy, history or a
  replacement (the edges module ROW_NOT_USED list), and the row is not in a terminal state. Each append
  is read once by eye; any doubt, no append.
- F2 resolve_by: the row's own review_by when it is a valid date in the gate horizon; otherwise the date
  the row went BLOCKED (from status_note) plus 14 days, recorded as a recheck date, not a promise.
  No trigger states a calendar date, so no date is invented beyond that recheck.
- F3 probes: an entry in `runtime/specs/jtbd-graph-probes.json` only for an existing code line that
  exercises the dep (calls it) and passes the gate's probe check. No new code written to satisfy the
  gate; a presence check (`if (!process.env.X)`) is not a probe.
- Any held id not fixed by F1 to F3 stays held.

## COMPOST candidates (listed for Zach, nothing deleted)
Tier C tools whose name token appears in no other tracked file outside generated catalogs
(`runtime/specs/tool-catalog.json`, `runtime/specs/tool-catalog.md`, `operators/OPERATOR-REGISTRY.json`, `runtime/specs/surface-catalog.json`,
the baseline itself) and in no row.

## Done means
`python3 scripts/universe_jtbd_adapter.py --check` PASS; each fixed id removed from the baseline;
before and after counts per rule in the PR.
