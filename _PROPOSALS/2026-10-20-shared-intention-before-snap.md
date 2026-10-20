---
title: Shared intention before the snap (design only)
date: 2026-10-20
status: PROPOSED, definition chosen (B with C mirror, Zach 2026-10-20); not built
scope: the first step after a backlog is induced, before backlog_graph.py ranks anything
freeze: s4 amendment 6 holds; this file edits no tool description and no code
---

# Shared intention before the snap

Zach, 2026-10-20, verbatim: "the first thing I want to happen after a backlog is induced and this
mechanically begins is meditating on a single shared intention, I am not sure what that is precisely
but I think it will help to visualize what we're manifesting."

Labels used below: **REUSE** names existing code or spec that does the job today. **GAP** names
something that does not exist yet. Nothing here is built.

## 1. What the intention is (three candidate definitions, pick one)

All three share this shape: **one sentence, one owner, one horizon, one exclusion line.**
They differ in what the sentence is about.

| | A. Outcome intention | B. Felt intention | C. Pull intention |
|---|---|---|---|
| Sentence names | a state of the world at the horizon ("By 2026-11-01, one paying user has run a receipt end to end.") | how Zach wants the work to feel and what it protects ("Close loops before opening new ones; nothing outward ships unverified.") | the thing the backlog is already leaning toward, named back to Zach ("Most load-bearing rows point at the outcome loop; make it close.") |
| Owner | Zach states it | Zach states it | system proposes, Zach accepts, edits or rejects |
| Horizon | one of the receipt horizons: `today`, `this-week`, `this-quarter`, `1-3y` (REUSE: decision_receipt CHECK constraint) | same | same |
| Excludes | one line of what it is NOT for (rows that do not serve it stay visible but go to the rim) | same | same |
| Strength | checkable at the horizon | closest to "meditating"; survives not knowing the form | grounded in rows, cheapest to start |
| Risk | forces a precise form Zach said he does not know yet | hard to score fit against | the backlog sets its own goal: NOTOMATION risk if accepted without edit |

**My lean (advisory, not a decision): B stated by Zach, with C shown beside it as a mirror.**
That matches "not sure what that is precisely": Zach names the felt direction, the system shows
what the rows are actually pulling toward, and the gap between the two is itself the first reading.
It is the om gap of Op 25 (confidence vs conviction) applied to a backlog instead of a claim set.

Rules that hold for any choice:
- One intention per induced backlog. A second one supersedes, never stacks.
- The system never writes the sentence alone (ROM 1, NOTOMATION). C only proposes.
- The intention is a frame, not a gate: no row is hidden or closed for misfit.

## 2. Where it comes from

1. **Stillness first.** After induction, nothing ranks. This is Op 25 component 2 (stillness
   window), fired by a new trigger: "backlog induced". REUSE: the spec
   `runtime/specs/operator-25-shavasana-v0.md` and its mechanical half `scripts/shavasana_handoff.py`.
   GAP: the trigger list there names pre-send, pre-merge, pre-handoff, pre-write-lock, drift,
   post-gauntlet; "post-induction" is not on it.
2. **Mirror (C draft).** The system reads the load-bearing rows (most downstream descendants and
   wave 0, both already computed by `scripts/backlog_graph.py`, REUSE) and drafts one sentence
   naming the common pull. GAP: no code drafts it; v0 could be a human reading the top 8 rows.
3. **Kairos check.** REUSE: `operators/arcs_operator_kairos.py` `TimeMode`. If Zach is in
   SANCTUARY or DRIFT, the step waits; it only asks in KAIROS (a sentence of intention is a
   depth act, not a throughput act). GAP: nothing passes a human time mode into the backlog path.
4. **Zach states or edits** the sentence, owner, horizon and exclusion. REUSE as precedent: the
   compass `true_north` field (`src/app/api/compass/route.ts`: "one actionable sentence", no
   hedges, no em-dashes) and the handoff "Goal / true north" block in CLAUDE.md. Same discipline,
   one level up: true_north is per decision, the intention is per backlog.
5. **Record.** GAP: no home. Smallest option: one JSON line per intention in a new
   `_STATE/intentions.jsonl` (sentence, owner, horizon, excludes, mirror_sentence, stated_at).
   Not a schema change, not a new table.

## 3. How it changes ranking

Today `backlog_graph.py` orders by wave, then `rank`, then `order`, then `priority`, then id, and
labels tool fit (HAVE / PARTIAL / NOT-RESOLVED / NONE from `route.tool`). Urgency comes from
`backlog_ripeness.py` (RIPE etc.). REUSE all three.

Proposed: keep the three terms and **rename the old fit to tool-fit**, then add **alignment**:

- **urgency** = ripeness (REUSE, unchanged)
- **priority** = dependency wave and downstream count (REUSE, unchanged)
- **tool-fit** = the HAVE/PARTIAL label (REUSE, unchanged)
- **alignment** = how directly finishing this row moves the intention. Three levels, not a float:
  **core** (finishing it is the intention, or a direct step), **feeder** (unblocks a core row in
  the graph), **rim** (neither).

Feeder is mechanical: any row with a core row among its descendants (REUSE: the descendants walk
already in `build`). Core is judgment. v0: Zach marks core rows by hand (expect 3 to 7). GAP: no
field for it; candidate is an `intention_core: true` on the row, or a list of ids in the intention
record (preferred: the rows stay untouched).

Ordering rule, proposed: within the ready-now set, sort by alignment (core, feeder, rim) first,
then the existing key. Waves still bind: alignment never lets a row jump its own dependencies.
Kinematic atoms are named as a later option only: `FirstDerivative` and `SecondDerivative` in
`operators/core/atoms.py` could read whether core rows are closing faster week over week (is the
field converging). REUSE exists; wiring is a GAP and is not needed for the test below. I did not
verify which periodic-table numbers those classes carry; treat "Op 1-3, 7" as unconfirmed here.

## 4. How it is shown (sketch only)

The intention sits at the center. Rows sit on three rings by alignment. Angle groups rows by
dependency chain, so a chain reads as a spoke from rim toward center. Size is downstream count.
Ripe rows are drawn solid; unripe rows as outlines (text stays full opacity, per WORLD.md).

```
                 rim  ·  ·  ·  ·  ·  ·  ·  ·
              feeder    o     o       o
                 core      ●   ●   ●
                       [ the one sentence ]
                 core      ●       ●
              feeder    o      o
                 rim  ·  ·  ·  ·  ·  ·  ·
```

Beside it, two lines: Zach's sentence and the mirror sentence, with the count of core rows that
the mirror also picked. Large disagreement is the useful reading, not a fault. REUSE: `--dot`
output of `backlog_graph.py` already emits the graph; the ring layout is a GAP (no new dependency;
plain SVG or the existing DOT path).

## 4b. Altitude drill-down (Zach, 2026-10-20)

The intention is shown at four horizons side by side (today, this week, this quarter, 12 months;
12 months records as `1-3y`, the nearest receipt horizon). Each horizon drills down by altitude:

| Altitude | Unit | What it holds |
|---|---|---|
| Exec | epoch | the intention at that horizon |
| Strategic | milestone | the outcome that shows the intention landed |
| Operational | sprint | the bounded run of work toward the milestone |
| Tactical | issue | one backlog row with its blockers, dependencies, configs, risks and failure modes (Zach) |
| Surgical | spec | the decomposition of that issue into steps (Zach) |

Tactical fields already on the rows (counts out of 324, 2026-10-20): blockers and dependencies =
`depends_on` (167) and `unblocks` (157), REUSE via backlog_graph.py; configs = `route` (303) and
`needs` (53), REUSE; risks = `ruin` (58), `door` (29), `gates` (303), REUSE; failure modes =
`abort` (10) and `rollback` (10), REUSE but thin. GAP: no field names failure modes directly,
and most rows lack abort and rollback.

Surgical has no home on the row: only 2 rows carry `next_action`. Decided (Zach, 2026-10-20): one linked spec
file per issue, referenced from the row. Proposed shape, not built: `runtime/specs/issues/<row-id>.md`,
and a `spec` key on the row holding that path. backlog_status_check.py does not restrict row keys
(checked 2026-10-20), so the key needs no gate change. GAP: a check that each `spec` path resolves
(the archive-move gate pattern would cover renames).

Short horizons skip high altitudes (a day has no milestone). Row placement in the grid is never
a ranking; examples in the 2026-10-20 sketch were illustrative only and are not core picks.

## 4c. Many paths to one waypoint, and the om among them (Zach, 2026-10-20)

Zach: there are endless paths to the safe waypoint; consider them all, then adjust the gear,
training and mindset each one needs, from the most dangerous to the safest. And treat the session's
chatter as signal: constructive or destructive interference, converging on a shared om instead of
dissonance or an endless echo, with standing disagreement recorded so it cannot deadlock, ending
in one prime torque move.

How it fits this design:

1. **Waypoint** = the intention at a horizon (section 1). Paths are routes through the backlog
   graph that reach the core rows. REUSE: dependency waves and descendants in backlog_graph.py
   enumerate routes; the `ex-ante-paired-paths-template` row already wants paired paths with cost
   if wrong and a falsifier per path. GAP: "all paths" is unbounded, so v0 shows a bounded set
   (say safest, fastest, and the one Zach would pick by feel) and says what was not enumerated.
2. **Danger per path** = the sum of its rows' risk fields (`ruin`, `door`, `gates`, `abort`,
   `rollback`; section 4b), priced by the risk underwriter (PR #1694, PROPOSED). REUSE: compass
   L2 path survivability as the frame.
3. **Gear, training, mindset** = what must be true before a path is walkable. Gear = tools
   (tool-fit, HAVE or PARTIAL). Training = skills or past receipts that show it was done before.
   Mindset = the human's time mode (Kairos) and the Op 25 somatic read. GAP: no per-path readiness
   readout exists; v0 is a three-line checklist per path.
4. **Chatter as interference.** Echo is already detected: Op 25 sycophancy check (agreement with no
   dissent). Its known flaw: it counts keywords, so it misses dissent in other words. Om is already
   defined: confidence vs conviction gap (Op 25 spec). REUSE as math only: `WaveDiffusion` and
   `PhaseCancel` in `operators/core/atoms.py` smooth and notch a number series. GAP: no series
   exists; the cheapest one is each core row's confidence per turn or per day.
5. **Agree to disagree** = recorded unruled collision, the pattern already used for FATED and KKL
   in `runtime/specs/legend.jsonl`. A disagreement on record stops blocking; it does not vanish.
6. **Prime torque move** = the single next move that the most considered parties push the same
   way, after recorded disagreements are set aside. It is a proposal Zach releases, never an
   automatic vote (NOTOMATION). GAP: multi-party conviction readings do not exist; v0 parties are
   Zach, the mirror sentence, and the risk underwriter's price.

The test in section 5 is unchanged; path views are shown after it, so they cannot steer the picks.

## 5. Pre-registered test (judged by Zach)

**Question:** does an intention-aligned snap list help Zach pick what to do next better than
today's list?

**Setup, fixed before anyone looks at results:**
1. Zach writes one intention (whichever definition he picks) and marks its core rows, before
   seeing either list.
2. Produce two top-8 ready-now lists from the same backlog file and date: **L0** =
   `backlog_graph.py` as is; **L1** = same set reordered by alignment then the existing key.
3. Show them blind as X and Y, order randomized by a coin flip recorded in advance.
4. Zach answers one question per list: "If you could only do three of these this week, which
   three?" and then "Which list would you rather work from?"

**Pass:** Zach prefers L1 AND at least 2 of his 3 picks from the preferred list are core or feeder
rows. **Fail:** he prefers L0, or prefers L1 but his picks are mostly rim (the intention is
decoration). **Null:** the two lists share 7 or more of 8 rows; the intention adds nothing at this
backlog's size, and we say so.

**Limits stated now:** one judge, one run, same person wrote the intention: this is a usefulness
check, not evidence of general value. A second run a week later on the same intention is the
cheapest repeat.

## 6. Reuse and gap ledger

| Piece | Status |
|---|---|
| Urgency (`backlog_ripeness.py`) | REUSE |
| Priority by wave and descendants (`backlog_graph.py build`) | REUSE |
| Tool fit (`resolve_tool`, tool-catalog.json) | REUSE, renamed tool-fit |
| One-sentence discipline (compass `true_north`, handoff Goal block) | REUSE as precedent |
| Stillness window and om gap (Op 25 spec, `shavasana_handoff.py`) | REUSE spec; post-induction trigger is a GAP |
| Time mode (`arcs_operator_kairos.py`) | REUSE; wiring a GAP |
| Kinematic convergence (`operators/core/atoms.py`) | REUSE later; not needed for v0 |
| Intention record (`_STATE/intentions.jsonl`) | GAP |
| Alignment term and core marks | GAP |
| Mirror sentence drafting | GAP (v0 can be manual) |
| Ring view | GAP |

## Decision

Zach, 2026-10-20: B (felt intention, stated by Zach) with C (mirror drafted from the backlog) shown beside it.

## Ask

Next: Zach writes the one sentence, horizon and exclusion line, and marks 3 to 7 core rows, before
seeing either list (test step 1). Building waits for that and for s4 to be scored.
