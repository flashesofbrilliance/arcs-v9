# JTBD graph pre-registration, amendment 7 (2026-10-20)

Amends `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`, s4 section. Decided by Zach in session
2026-10-20: judge s4 by pooled blind judging, scoring whether each system assembles the right set of
tools or operators. Amendment 6 (tuned rows, description freeze) still applies.

## What was seen first (why the rule changes)
1. Zach could not name the right tool for most of his own jobs from memory, so labels written in
   advance were not possible.
2. A `/catalog` baseline was run on s4 rows 1 to 14 (fresh agent, catalog only, one shot) and Zach
   marked its answers: 3 right, 5 close, 6 wrong. His labels for rows 1 to 14 were written after
   seeing those answers (disclosed in `_PATTERNS/2026-10-19-jtbd-s4-labelled-queries.md`).
3. For rows 8, 9 and 11 Zach's answer was a quorum of operators, not one tool. A top-1 test cannot
   score that.
No graph answer to any s4 query has been seen by anyone.

## Rule
1. **Query set.** Rows 1 to 20 of the labelled-query file. Rows 19 and 20 must be written by Zach
   before the first run; if still blank at the run, s4 runs on rows 1 to 18. Zach's labels in that
   file are reference only and are not used to score.
2. **What each system returns.** An assembly: an ordered list of 1 to 5 items, each a schema id
   (tool, operator, agent or skill) from the catalog or graph.
   - Graph: the s4 retrieval, as built, under the 1,000-token answer budget.
   - Baseline: `/catalog` exactly as committed at the s4 start sha (amendment 6 rule 1), one shot.
     By design it names one tool, so its assembly has one item. This is not padded: the graph must
     beat the tool that exists today, as it exists.
3. **Pool and blind.** For each query, the union of both assemblies' items is shuffled with
   `random.Random(20261020 + row)` and shown to Zach with no system label, no order from either
   system, and no hint of which items came from where. The pool is prepared by a session other than
   the one that built s4 and is committed (as a sealed file with the source mapping kept separately)
   before Zach judges.
4. **Judging.** Zach marks every pooled item for its query: **essential** (the job fails without
   it), **useful** (helps, not required) or **wrong**. He may also name an essential piece neither
   system offered; that is recorded and counts as a miss for both.
5. **Per-query pass.** A system passes a query when its assembly contains at least one essential
   item AND wrong items are no more than half of its items (rounded down).
6. **Gate.** Graph passes at least 80% of the queries run (16 of 20, or 15 of 18) AND passes
   strictly more queries than `/catalog`. A tie or a loss kills s4 retrieval as before.
7. **Reported alongside, not gating.** Essential recall per system (essential items found / all
   essential items judged for that query, averaged); the untuned-subset scores (amendment 6); the
   count of essential pieces neither system offered.
8. **Order.** No graph answer is shown to Zach or anyone before the pool is sealed. Thresholds above
   are fixed by this file; changing any after the pool is sealed needs a new amendment saying what
   was seen.

## Known weakness, stated now
Assemblies favour the graph: a five-item list has more chances to contain an essential item than
`/catalog`'s one. Rule 5's wrong-items cap and the essential-recall report are the counterweights; a
reader should check that the graph's passes are not carried by long lists of mostly-useful items.
