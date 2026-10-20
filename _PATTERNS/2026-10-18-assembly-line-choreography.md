# Assembly line: fan, ripple, procreate (design v0, 2026-10-18)

Status: PROPOSAL, first script built. Zach ruled on the three open questions 2026-10-18 (see Decisions).

## Decisions (Zach, 2026-10-18)

1. Fresh parent per wave, reading only the compacted arc block.
2. Children may open PRs unattended. Merges stay with Zach.
3. The `filing-*` hub stays outside the line as a human track (triage forces it to R4).

## Built so far

the line-triage script (this branch, not yet merged) (stdlib, read-only, `--self-test` 10 cases, fails a one-way door sent to R1, passes clean fixtures). First run, wave 0: R1=3, R3=2, R-1=1. Over all 218 active rows: R-1=79, R1=20, R2=2, R3=27, R4=90. So the R-1 lever covers 79 rows, not the 151 NOT-RESOLVED figure (that count included human-gated rows).

Finding: the tier cue on the graph is binary (2 or 4), so R2 is rare (2 rows) and `adr-085-acceptance-redecide` lands in R-1 although it is a decision. Either rows need a `door`/type field for ADR rulings, or triage should treat `*-redecide` and `*-ruling` ids as R3. Left as is; Zach's call.

Prior art read: ADR-086 (two-pass backlog induction, DRAFT), ADR-075 (mechanical vs judgment split), ADR-085 (write-lock, hot-file leases), ADR-068 (print, gate, fate), memory `puppet-master-fanout-worktree-isolated-jtbd`, `/fold`, `scripts/backlog_graph.py`, `scripts/handoff_fold.py`, `runtime/specs/backlog-status.json`.

## Ground truth as of 2026-10-18 (from `backlog_graph.py`, read-only)

- 295 rows: OPEN 157, HOLDING 44, READY 16, DONE 45. 50 rows carry `depends_on`. 0 cycles, 2 dead dependencies, 7 `unblocks` mismatches.
- Wave 0 startable now: 6 rows. Two are decisions (`adr-085-acceptance-redecide`, `rc-ops-001-graduation-ruling`), one needs a first conversion (`agent-receipts-audit-first-conversion`), three are mechanical and have a resolved tool.
- Biggest unblockers (16 downstream) are all `filing-*` rows: counsel, prior filings, who-saw-it. These are human and legal gated. An agent cannot clear them.
- Mechanization gap: 151 of 232 active rows name a tool that does not resolve (NOT-RESOLVED). That gap is what stops a row from being handed to an agent.

Two readings follow. The line must not spend agents on the filing hub; it should surface it once as a single decision card for Zach. And the cheapest unblock for the whole backlog is resolving `route.tool`, not writing more rows.

## The line, six stations

Each station prints an artifact, through a gate, to a fate (ADR-068). A station with no print is not a station.

| # | Station | Who runs it | Print | Gate | Fate |
|---|---|---|---|---|---|
| 0 | **Scan** | script, no model | wave plan JSON from `backlog_graph.py --json`, live sessions, `neighbor_scan.py` hits | acyclic; live sessions under 4 | `planned` or `held` |
| 1 | **Triage** | script first, one reviewer for residue | each ready node gets a resolution level R0 to R4 (below) | level follows the rules table, not a vibe | routed to a station or to Zach |
| 2 | **Fan** | parent session (puppet master) | one child brief per R1 or R2 node, from a fixed template | brief names owned files; no two briefs share a write file | child session started or refused |
| 3 | **Work** | child session | PR + return contract (below) | its own gates; peer reviewer on its diff; never self-merges | PR open, or child returns `blocked` |
| 4 | **Ripple** | parent, on each return | vet for scope-bleed, flip row states, broadcast to citers, write the receipt | diff touches only owned files; `neighbor_scan` broadcast list named | rows flipped, or child sent back |
| 5 | **Procreate** | parent | new rows from cracks, plus one hyperstition pass per checkpoint (ADR-086 pass 2) | every new row cites existing evidence; unknown stays unknown | rows enter `OPEN`, `origin: line` |
| 6 | **Compact** | `handoff_fold.py` | one arc block, not N chat summaries | refuses bookends | next wave's brief is the block |

## Resolution ladder (the "right level and fidelity")

The spawn decision is a function of fields already on the row. It is computed, then reviewed.

| Level | Meaning | Spawns | Model tier | Trigger fields |
|---|---|---|---|---|
| **R0 tick** | a script does it; no agent | nothing | none | route.tool HAVE and the job is a command (`backlog_status_check`, `operator_registry_emit`, `surface_catalog_emit`) |
| **R1 mechanical child** | rule-statable edit, set-diff, regenerate | one session | cheapest | route.tool HAVE, door `two-way`, tier cue 2 or below |
| **R2 build child** | real code or content, needs a reviewer | one session + one peer reviewer | mid | route.tool PARTIAL or HAVE, door `two-way`, tier cue 3 |
| **R3 decision** | ADR, ruling, graduation, anything one-way | no child; parent drafts a decision card for Zach; WRITE-LOCK declared before commit | top | `door: one-way`, or row type is an ADR or ruling, or tier cue 4 |
| **R4 human gate** | counsel, outreach, publishing, merges, money | nothing | none | `consent`, `ruin`, or `state: BLOCKED`; shown, never routed |
| **R-1 resolve-route** | the row names no resolvable tool | one cheap child whose only job is to fill `route.tool` | cheapest | route.tool NOT-RESOLVED. Output is a one-field PR. Re-triage after merge |

R-1 is the lever on the 151-row gap. It turns a row from un-spawnable into spawnable at the price of one tiny child, and its result is mechanically checkable (the tool path exists or it does not).

## Parent and child relationships

Three structural properties, taken from the puppet-master model; no new coordination machinery.

1. **One parent, flat children.** The parent is an arc session, one per backlog hub. Children are leaves. Depth cap 2: a child may propose rows, never start a session. Width cap 4 live sessions (memory `session-budget-discipline-cap-parallel-molt-long`).
2. **Rows are cheap, sessions are not.** Procreation emits rows, not sessions. A row becomes a session only at the next Triage, and only if the cap has room. This is the brake on exponential spawn.
3. **Disjoint write scope, single owner per shared file.** Hot files (backlog JSONL, CLAUDE.md, oracle) follow ADR-085 leases and append-only rules; children never edit the backlog directly. They return a row delta in the return contract and the parent applies all deltas in one commit (the parent is the only writer to `_QUEUE/`).

### Child brief template (fixed; this is the prompt handoff)

```
TITLE: imperative verb phrase
AS-OF: facts verified today, with dates (never "recall")
ROW: id, jtbd, gates, door, abort, rollback (copied from the row)
OWNS: exact files this session may write. Everything else is read-only
SSOT: paths to read; point, never inline
DONE LOOKS LIKE: one observable check (a command and its expected output)
LEVEL: R1 or R2, and the tier this session runs at
RETURN CONTRACT: below
DO NOT: merge; edit _QUEUE/; start sessions; touch another lane's OWNS
```

### Return contract (what a child hands back, so the ripple is mechanical)

```
status: done | blocked | partial
pr: url
touched: [paths]            # the parent diffs this against OWNS
evidence: [receipt ids, command + output]
row_deltas: [{id, state, status_note}]
new_rows: [{jtbd, depends_on, evidence}]     # evidence must exist; no evidence, no row
unblocks_observed: [row ids]
```

## Ripple (what happens after a child lands)

1. Parent checks `touched` against `OWNS`. A bleed sends the PR back, it does not fix it.
2. `neighbor_scan.py` on the changed files; the parent updates citers or posts to the owning session and names the broadcast list in the receipt (AGENTS.md gotcha 19).
3. Row states flip in one commit; `backlog_status_check.py --check` must pass.
4. `backlog_graph.py` re-run. Rows whose last dependency cleared move HOLDING to READY. That diff is the next wave's work list.
5. One receipt per merge, as the repo already requires.

## Procreate (how new rows are born without spin)

- A child or the hyperstition pass may emit a row only with citable, existing evidence (ADR-086). No evidence is recorded `unknown`, no row.
- New rows get `depends_on` at birth, so the graph stays computable. Prose triggers become `gate_event`.
- Cap: one hyperstition pass per checkpoint. Checkpoint = a wave closing, or a calendar week.
- Dedup before birth: the row's jtbd is run through `/prior-art` and `/catalog`; a near-match becomes a `depends_on` or a note on the existing row, not a sibling.

## Where it stays human (NOTOMATION)

R3 and R4 never auto-resolve. The line's job there is to make the human decision cheap: one card per decision with the question, the options, the evidence, the abort, and the rollback. Merges stay with Zach (AGENTS.md gotcha 17; consent stays human). The `filing-*` hub becomes a single card, not sixteen rows of nagging.

## Pilot (smallest real run, no new code except the brief generator)

Wave 0 today, three lanes, one parent:

| Lane | Rows | Level | Why |
|---|---|---|---|
| A | `asm-003-cold-molt-decided`, `doc-gate-false-positive-cleanup`, `accountant-weekly-first-unattended` | R1 | tool HAVE, tier cue 2 |
| B | pick 5 NOT-RESOLVED rows with the most downstream; fill `route.tool` | R-1 | proves the lever on the 151-row gap |
| C | none (parent only) | R3 | draft decision cards for `adr-085-acceptance-redecide` and `rc-ops-001-graduation-ruling`, plus one filing-hub card |

Pre-registered success check (before counting): after the wave, the READY count rises or the NOT-RESOLVED count falls by at least 5, every child's `touched` stayed inside `OWNS`, and no row was born without evidence. If lane B moves NOT-RESOLVED by fewer than 5, the R-1 level is cut and the gap is a human-sized job.

## What to build, smallest first

1. the line-triage script (this branch, not yet merged) (stdlib, read-only): reads `backlog_graph.py --json`, prints level R-1 to R4 per ready node with the rule that fired. Gate: fail on a fixture where a one-way door gets R1; pass on a clean fixture.
2. the line-brief script (this branch, not yet merged): renders the child brief from a row id, refuses a brief whose OWNS overlaps another brief in the same wave.
3. Return-contract validator for the ripple step.
4. A `/line` skill that sequences stations 0 to 6 and calls `/fold`, `start_session`, and `handoff_fold.py` rather than reimplementing them.

Build order is 1, then pilot lane B by hand, then 2. Do not build 3 and 4 before the pilot reports.

## Unconfirmed

- ADR-086 is DRAFT; this design borrows its pass-2 rule but does not depend on it being accepted.
- The tier cue on the graph is a heuristic, not a verified difficulty. R-levels are proposals until the Accountant has n >= 30 closed outcomes per level; today it has none for this line.
- I did not check whether `/fold` or `handoff_fold.py` already enforce an OWNS overlap check; stage 2's gate may duplicate a gate that exists.

## Open questions for Zach

1. Does the parent run as one long arc session, or as a fresh parent per wave that reads only the compacted arc block? (Recommendation: fresh per wave, to stay under the molt threshold.)
2. May children open PRs without a human present, with merge staying yours? (Recommendation: yes, matches the puppet-master proof.)
3. Is the `filing-*` hub in scope for the line at all, or does it stay outside as a standing human track?

## Kirigami loop: cut, fold, molt, land (added 2026-10-18)

Reading of the ask (unconfirmed): a "spike" is a dense burst of threads in one session; "landing" it is the next session booting from the handoff. Drag is everything the lander pays to re-derive.

Kirigami lesson: a flat sheet takes a 3D shape without tearing because the cuts were placed before the load, at the lines where stress would concentrate. The cut pattern sets the shape, not the material. Folds are reversible; cuts are not, so they are declared up front.

| Step | Existing tool | Kirigami role | Change proposed |
|---|---|---|---|
| **Cut** | child `OWNS` + return contract | pre-declared cut lines, made before the burst | cut lines are written into the wave brief, not discovered at handoff |
| **Fold** | `/fold` | residue clustered along the cuts into composed sessions | fold only along declared cuts; an uncut thread stays a backlog row |
| **Molt** | `handoff_fold.py molt` | shed the old skin, keep one arc block | the block carries row deltas and the next triage, not narrative |
| **Land** | fresh parent per wave | boots from the block alone | first action is the line-triage script (this branch, not yet merged) on the new graph, no re-reading |

Loop closure: where a lander re-read a file, corrected the block, or asked what happened, that is stress. The next wave places a cut there.

Drag metric (pre-registered before counting): tokens from session start to the first tool call that advances the block's stated next action, plus count of re-derivations (reads of files the block already summarised). Baseline: the last three handoffs, not yet measured. Kill condition: if drag is not down 30 percent against that baseline after two waves, the loop is cut and the old molt stays.

### Drag baseline, measured 2026-10-18

Cohort: sessions whose first message was `/handoff-pickup` (5 distinct of the 400 most recent transcripts). Measure: new tokens (input + cache-creation + output, summed per assistant message) from session start to the first Edit, Write, commit, push or PR call. Boot = the first message's tokens.

| Session | Boot | Net to first action | Tool calls before | Files read |
|---|---|---|---|---|
| lab-assessment-wrapper | 98k | 171k | 12 | 1 |
| mystifying-tesla | 96k | 258k | 5 | 0 |
| sweet-hopper | 104k | 296k | 46 | 0 |
| ahmed-communication | 61k | 559k | 59 | 6 |
| induced-backlog-arcs-care | 96k | 368k | 16 | 1 |

Median net drag 296k (range 171k to 559k). Caveats: cache-creation grows with tool output, so this is a proxy for spend, not a bill; "first edit" counts as useful action even when the edit was the pickup's own bookkeeping; n=5, not a calibrated baseline. The 30 percent kill condition therefore reads: median under about 207k.

Observation: boot alone is about 100k before any work, a fixed floor the loop cannot cut. Drag above the floor is 70k to 500k and tracks tool calls (5 to 60), not file reads. The cut lines should target calls, not reading.

### Pilot lane B result (2026-10-18, inline, no child sessions)

Resolved `route.tool` on 5 rows by hand (the 2 receipt-closing rows and 3 phosphor rows; prior prose kept in `route.prior_tool`). NOT-RESOLVED fell from 151 to 146, meeting the pre-registered threshold of 5.

What it taught, and changed:
- A resolving path alone made those rows triage as R1, which was wrong: they are builds or human-supplied work. R1 now requires the author-declared row field `mechanical: true`; a resolving path alone gives R2. No existing row carries the marker yet, so wave 0 has no R1 rows until someone marks one (R2=3, R3=3 today).
- A brief's OWNS defaulted to the tool files (the build and check scripts), not the files the work edits. Rows may now declare `route.owns`; the three phosphor rows do. Tool files then move to read-only SSOT.
- The overlap gate did its job: all the phosphor rows edit the same source files, so only one can be in a wave.
- Cost note: the same 5 edits as child sessions would have cost about 100k boot + 170k drag each. Resolving routes is inline work; spawn children for builds.
- Weak spot: "NOT-RESOLVED falls" measures that a path exists, not that it is the right tool. I chose the paths by reading each row; nobody else has checked them.

### Pilot child 1 result (2026-10-20, catalog-fixes-after-s4, PR 1747 merged)

- **Drag to first edit:** 15k net tokens and 3 tool calls (baseline median 296k, 5 to 60 calls). n=1 on a small, bounded task, so this is not a verdict on the 30 percent kill condition.
- **What actually cost the time:** three pre-commit gate blocks the brief did not mention. Adding a catalog surface cascaded into the jtbd-graph gate (22 findings: the agents surface was unknown to the adapter, plus two line scripts with no job edge). The child stopped and asked each time, bypassed nothing, and stayed inside its scope. Total runs were four child turns and about six parent decisions.
- **Change made:** `line_brief.py` now parses the pre-commit hook and lists, in each brief, the gates that may fire for the paths in OWNS, with the command to run before committing. Static and approximate: the hook decides, the brief only warns. Fixtures cover pathspec globs, continuation lines, diff filter and label, and a real-hook case for the exact gate that blocked this child.
- **Deferred:** the agents surface in the catalog, until the jtbd adapter learns the agent namespace (separate row, Zach).
- **Verdict so far:** pre-rendered briefs removed orientation cost; unlisted commit gates became the new cost. Two comparable rows are needed before judging the kill condition.
