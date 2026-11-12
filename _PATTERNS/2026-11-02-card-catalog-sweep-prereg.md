# Card-catalog sweep: pre-registration (2026-11-02)

Row: `card-catalog-sweep-quorum` (s4 query row 11, `_PATTERNS/2026-10-19-jtbd-s4-labelled-queries.md`).
Written and committed BEFORE any change to `operators/arcs_librarian.py`. The queries, the pass rules and the
fail rules below are fixed; results are reported against them as they come out, failures included.

## What the sweep is

One query to the Librarian (Operator 21) returns hits from DEWY receipts, ADRs and the Apex Spine
(`_CANON/apex-spine-mobius-induction-circuit.md`) side by side, each with a graded source and a provenance line.
The other quorum members named in row 11 (Op 25 Sage, an auditor, a scholar) are not built; the output must say so.

## What a passing answer contains (per query)

A. Class coverage: every class the query lists under "expects" appears among the returned items.
B. Graded source: every item carries `source.tier` from `runtime/specs/source-trust.json` (a tier string, never empty).
C. Provenance per claim: every item carries `path`, `why_load_bearing` (the query terms that hit and the in-degree),
   and `freshness.verified` (a date or an explicit null). An item with no `path` is a fail.
D. Backing honesty: an item with no M0 backing is listed under `what_unconfirmed` and never under `what_confirmed`.
E. Gaps named: the result has a `gaps` list that names Op 25 Sage, the auditor and the scholar as unbuilt, with the
   registry status quoted from `operators/OPERATOR-REGISTRY.json` where one exists. A result that lists any of the
   three as consulted is a fail.

## Test queries

| # | Query | Expects |
|---|---|---|
| Q1 | `apex spine induction circuit witness ADR DEWY wisdom Tao` | apex-spine item within the top 3; at least one ADR |
| Q2 | `triad none may null potential well one non-orientable surface` | apex-spine item; ADR-071 |
| Q3 | `honesty air-gaps spine being its own gate` | apex-spine item; at least one ADR |
| Q4 | `decision receipt unconfirmed lines for a shipped merge` | at least one receipt class (personal-receipt, store-receipt or operator-receipt) and at least one ADR; apex-spine not required |
| Q5 (negative control) | `zebra quartz metronome tuning fork` | no apex-spine item, no item with p_load_bearing above 0.3 |

Q5 passes only if the sweep stays quiet on a query nothing in the corpus answers. Criteria B to E apply to every
query, Q5 included (an empty result passes B to D vacuously and must still carry `gaps`).

## What counts as a fail

* Any expectation in the table unmet (a missing class, apex-spine outside the top 3 on Q1, an apex-spine hit on Q5).
* Any of criteria B to E broken on any returned item.
* A claim of coverage for Op 25 Sage, the auditor or the scholar.
* Reporting a fail as a pass, or dropping a query after seeing its result.

Known risks stated in advance: the query tokenizer is ASCII-only, so a query written with "Möbius" loses the word;
the queries above avoid the diacritic on purpose and that is a limit of the tokenizer, not a pass. The personal-tier
receipts are generated and gitignored (`_STATE/job-search/universe`), so Q4 can fail on a checkout where they are
absent; a Q4 fail there is reported with that cause, not hidden. The unit tests use a synthetic corpus and do not
depend on those files.
