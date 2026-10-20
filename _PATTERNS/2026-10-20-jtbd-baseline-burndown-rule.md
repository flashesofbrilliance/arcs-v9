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

## Amendment 1 (2026-10-20, written before counting): stricter COMPOST rule
The first rule found 0 candidates because prose mentions count as use. Zach asked for a stricter one.
- A tier C orphan tool (not a periodic-table op, not a surface) is a COMPOST candidate when its name
  token appears in no tracked code or config file other than its own: extensions .py .sh .ts .tsx .js
  .mjs .cjs .json .jsonl .yml .yaml .toml, plus `.claude/settings.json`, excluding the generated
  catalogs listed above, the baseline, and anything under `_STATE/`, `_ARCHIVE/` or `_ARTIFACTS/`.
- Markdown never counts, under this rule, as use. Commands and skills are .md files people invoke by hand, so they
  are listed in their own group, kept apart from the scripts.
- Output: a list for Zach with each candidate's last commit date. Nothing is deleted or moved.

## Erratum (2026-10-20)
The message of commit 30d36669 (merged in PR 1730) says "614 to 609". The true count is 613 to 608,
as the PR body and the receipt say. Merged history is not rewritten; this line is the correction.

## Amendment 2 (2026-10-20, after the first run of amendment 1 returned 0)
That run returned 0 because `runtime/specs/fixtures/jtbd-graph/root/` holds frozen copies of the generated
catalogs, which name every tool. Those copies are the excluded files under another path, so they are
excluded too. Nothing else changed.
