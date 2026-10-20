# JTBD s4 raw assemblies (amendment 7, rows 1 to 18)

Inputs to the blind pool. Do not show these files to the judge.

- `queries-rows-1-18.json`: the job statements, copied from `_PATTERNS/2026-10-19-jtbd-s4-labelled-queries.md` (last changed at c30de5f9). Labels were not copied.
- `graph-raw.json`: `Librarian.jtbd()` at run sha `bd3e49ea` (s4 start sha `43f1291a`). Deterministic, so it can be re-run.
- `catalog-raw.json`: the `/catalog` baseline, one shot per row, run by a fresh subagent that read only the command file and the catalog. The catalog and the command file are unchanged since `43f1291a`.
- `source-mapping.json`: which system offered each item. Rows 19 and 20 were blank at the run, so s4 runs on rows 1 to 18 (rule 1).

Pooling, sealing and judging belong to another session (rule 3). This session has not seen a pool.
