# JTBD graph s4: labelled query set (DRAFT, partly labelled)

Status: DRAFT. Not valid as a gate until Zach fills every `label` cell and the file is committed;
the commit sha that contains the filled labels is the one the s4 run and the /catalog baseline cite.
Rules come from `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md` (s4 section). Nothing here
changes them.

## How to fill it (about 20 minutes)
1. Keep, edit or replace rows 1 to 5. They are verbatim asks from your own recent sessions
   (2026-10-17 to 2026-10-19), picked because they do not name a tool. At least 5 rows must stay real asks.
2. Write rows 6 to 20: jobs you actually have, in your own words. Do not copy a catalog `jtbd` line
   (that leaks the answer to /catalog).
3. For each row put ONE tool id in `label`, using the schema form, for example `tool:script:oracle.py`,
   `tool:command:loops`, `tool:skill:cruft-sweep`, `tool:op:21`. If no existing tool does the job, write
   `none` (both systems are then scored correct only if they say no tool fits).
4. Do not run /catalog or the graph on these before committing. Labels written after seeing either
   system's answer void the gate.

No labels are suggested here on purpose: a label proposed by an agent that has read the catalog is
the contamination the pre-registration guards against.

| # | Source | Job statement | label | tuned |
|---|---|---|---|---|
| 1 | real ask | check if the scheduled ones are hung | sweep (housekeeping night moves chore) |  |
| 2 | real ask | check them for half-written state | /fold or a cold molt; check head / tail / ephemeral memory shards, cross-referenced against the oracle and GitHub as source of truth | 1688 |
| 3 | real ask | molt the handoff fragments now | handoff_fold.py molt (Claude reading of Zach's reply; unconfirmed) | 1688 |
| 4 | real ask | I closed a bunch of stuff - check again? | /loops covers the open-loop part only (Claude reading; unconfirmed) |  |
| 5 | real ask | measure landing drag on the last three handoffs (tokens to first useful action, re-derivation count) | /fold or a cold molt; measured as velocity of OM amplification across turns (shorter is better); no meter exists | 1688 |
| 6 | Zach | pre-flight checklist of surfaces, drift, tech-debt, design-debt, blockers, P0 triage | inchworm audit, reconcile and mend (ouroboros forcing function) |  |
| 7 | Zach | non-obvious insights / counter-intuitive signals - how to make sense of them | inlier / outlier detection; FUN / LAB / COURT / KKL lenses for cognitive distortions; posterior / anterior reasoning |  |
| 8 | Zach | arcs primitives and atomic elements snap together upon induced current | librarian / folksonomist / conductor / orchestrator / alchemist / curator / scholar / sage / loki assemble in planning mode |  |
| 9 | Zach | contour of shape of problem emerges and jobs to be done magnetically attract to the loadbearing edges of the problem space; tools snap to jobs as more current is induced; backlog prioritizes on electromagnetic principles and creates a dynamo effect | same quorum as row 8; backlog prioritization becomes greek-chorus constructive interference and productive discord |  |
| 10 | Zach | vector collision engine v2 and orthogonal echo detector start firing to look out for rare earth arcs periodic elements and we ensure that our conditions are dialed in | lattice density and load-bearing properties: net-new adjacent / orthogonal cuts that add to brilliance, coherence, clarity and conviction, not diminish it |  |
| 11 | Zach | reverse look up index, catalog, state, memory, handoff files to date and piece together well inferred hypotheses with source quality grading and explainable provenance | quorum: Op 19 Accountant, 20 Folksonomy, 21 Librarian, 25 (Sage; unbuilt) plus auditor and scholar; cross-reference DEWY receipts, Apex Spine and ADRs as a card-catalog sweep; add Op 17 Detective, 16 Orchestrator, 12 Bayesian, 18 Immune, 14 Coherence where beneficial |  |
| 12 | Zach | sweep for seed candidates and night moves and check if any memories conflict or need to be updated | /night-moves is right; a collector basin for seed, ADR, DEWY and wisdom receipts we may have overlooked; it does not take a global write-lock |  |
| 13 | Zach | audit priors and see if any net-new data requires changes in belief or adaptive time signature detection | a belief log updated by the Golden Inchworm forcing function, as on status.arcs.care/beliefs |  |
| 14 | Zach | run a forensic recoil report on the thread and map out the full kinematic manifold between null, om and infinite | a recoil report for a conversation, a composable meeting, or a disposable thread; or a map of the kinematic manifold at the choice moments of an I/O arc |  |
| 15 | Zach rewrite of 1 | sweep the housekeeping night-moves chore, including whether scheduled runs are hung |  |  |
| 16 | Zach rewrite of 2 | check head / tail / ephemeral memory shards and cross-reference the oracle and GitHub source of truth |  | 1688 |
| 17 | Zach rewrite of 3 | compare cold molt against handoff pickup for efficacy and cold retrieval, evidence only (receipts or it didn't happen) |  |  |
| 18 | Zach rewrite of 4 | cross-reference surfaces.arcs.care, status.arcs.care, status.arcs.care/beliefs, arcs.care/reading-room and the docs reconciliation sync state to see which loops are open, what is drifting and where tech debt is arising |  |  |
| 19 | Zach | | | |
| 20 | Zach | | | |

## Disclosure: labels 1 to 14 were written after seeing /catalog's answers (2026-10-20)
Zach's labels for rows 1 to 14 came while judging a /catalog baseline run (fresh agent, catalog only,
one shot) on rows 1 to 14, so /catalog's answers were seen first. The pre-registration requires labels before
either system runs. These rows therefore cannot score /catalog against the graph as pre-registered; they are
kept as realistic queries. Before s4 scores, Zach decides one of: a fresh set labelled blind, pooled blind
judging (both systems' answers shuffled, judged without knowing the source), or an amendment that accepts
this set with the disclosure. Rows 15 to 18 are Zach's rewrites and have not been run by either system.

Baseline marks (Zach; provisional ones are Claude's readings, unconfirmed): 1 wrong, 2 wrong, 3 right
(provisional), 4 close (provisional), 5 right (none is honest), 6 close, 7 wrong, 8 wrong, 9 close,
10 wrong, 11 close, 12 right, 13 wrong (assumptions.py is a premises ledger; scripts/belief_log_emit.py, which builds the beliefs log, exists in the catalog and was passed over), 14 close (provisional: /thread-recoil covers a conversation, not meetings or the manifold). Tally of 14: 3 right, 5 close, 6 wrong.

Several labels are an assembly of operators, not one tool (rows 8, 9, 11). A top-1 tool test cannot score
an assembly; whether s4 is judged on assembling the right set is Zach's call and needs an amendment.

## Tuned rows (amendment 6)
Rows 2, 3 and 5 are marked `tuned: 1688`. PR 1688 rewrote the `/fold` and `scripts/handoff_fold.py`
descriptions after row 2's symptom showed up here. Row 2 is the half-written-state query the amendment names.
Rows 3 and 5 are marked too, to be safe: row 3 (molt) targets handoff_fold.py, whose description changed,
and row 5 (landing drag) matches the words "cuts landing drag" that 1688 added. s4 reports an untuned-subset
score alongside the all-20 score. Any row Zach adds later that paraphrases half-written state is marked the same way.

## Scoring (fixed, for whoever runs it)
- Baseline first: the /catalog procedure at the start sha, a fresh session with only that command and
  `runtime/specs/tool-catalog.json`, one shot per row, same model tier as the s4 run. Map its one
  recommended tool to a schema id; top-1 correct if it equals `label`.
- Early read (2026-10-19 proposal, does not change any threshold): if the baseline scores 18 or more
  of 20, s4 cannot win by a margin worth its upkeep, so s4 and s5 stop and only s3's integrity gates
  are kept. That stop is a choice Zach makes on the number, not an automatic kill.
