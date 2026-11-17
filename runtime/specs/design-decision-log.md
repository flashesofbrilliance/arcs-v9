---
spec: design-decision-log
version: 1
status: PROPOSED
date: 2026-11-13
backlog: seat-binding-design-log
extends: seed 20 hardening item 6 (the append-only pick log), _PROPOSALS/2026-11-13-seed-induced-render-engine.md on claude/seed-induced-render-engine-8ec25e
---

# Design-decision log: one append-only record of every visual pick and who objected

**Why.** Zach, 2026-11-13: "maybe serialize our design decisions over time for wider and more broad perspectives." A pick made in a widget and applied in one session leaves only the winning CSS behind. The unpicked options, the reason and the seat that disagreed are gone, so a later review cannot learn from it.

**What.** One JSONL store, the seed-20 pick log, gains seat verdicts and a rationale. It is not a second store. Each line is one decision on one block. The seed-20 curator reframe holds: each line is a vote on a design-system default, so the log is the dataset that says when a default is ready to promote.

**Why now.** The option board generator is being written now (session distracted-grothendieck). The fields cost nothing to include at the start and are lossy to add later, because old picks cannot be re-annotated with seats that were never asked.

**How.** Before: the generator owner confirms the path and seed-20 items 1 to 3 (manifest, hashed pick string, named changes). During: each design-loop stage in `runtime/specs/design-review-seats.json` appends its seat verdicts to the line for that block. After: the promote stage reads the log (Op 19 tallies, Op 20 clusters, chief-bayesian says when). To read this page: the field table is the contract; the rules under it are what a writer must keep.

## Path

`runtime/design/pick-log.jsonl`, committed, unless the generator owner has already named another path; then that path, and this spec follows it. One store either way.

## One line

| Field | Type | From | Meaning |
|---|---|---|---|
| `at` | ISO 8601 | writer | when the pick was made (check with `date`, never guessed) |
| `board` | sha | seed-20 item 1 | manifest hash; resolves every letter after the widget is gone |
| `page` | path | seed-20 item 6 | the surface the board was for |
| `block` | string | seed-20 item 6 | block id on the page |
| `layer` | atom, molecule, organism, template, page | seed-20 item 6 | atomic layer of the block |
| `shown` | [change id] | seed-20 items 3, 6 | the named token or rule changes offered, e.g. `gap.lg+glass.1x` |
| `chosen` | change id or `prose` | seed-20 item 6 | the pick; `prose` when the reviewer fell back to words |
| `dial` | number | seed-20 item 6 | strength dial, 1 = resting page |
| `decided_by` | string | writer | the human who picked (NOTOMATION: seats advise, a human decides) |
| `rationale` | string | reviewer, verbatim | why, in the reviewer's words; empty is allowed, invented is not |
| `seats` | [{seat, stage, verdict, note}] | design-review-seats.json | `seat` is a binding-map id; `verdict` is PASS, OBJECT or ABSTAIN; `note` quotes the objection |
| `applied` | commit sha or null | apply stage | the commit that applied it through `scripts/page_tune.py --apply` |

## Rules

1. Append only. A correction is a new line with `supersedes` naming the old line's `board` + `block`; nothing is edited or deleted (the decision_receipt precedent).
2. A held objection stays in `seats[]` with verdict OBJECT even when the human picks against it (memory `disagreement-is-load-bearing-no-forced-consensus`).
3. Every `seat` must exist in `runtime/specs/operator-binding-map.json`; `scripts/operator_binding_emit.py --check` already fails on an unknown seat in the stage file, and the log validator (backlog row `seat-binding-design-log`) applies the same rule to lines.
4. Promotion of a default is a backlog row Zach fates, never an automatic edit to tokens.
5. No PII: counterpart names stay out of `rationale` (memory `counterpart-pseudonym-key-public-artifacts`).
