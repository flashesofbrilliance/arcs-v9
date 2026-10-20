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

## 4d. Risk counterweight: underwriter, pre-mortem, reinsurance (Zach, 2026-10-20)

The snap list gets a counterweight that prices risk before a fate is picked.

- **Built (read-only, PR #1695, unmerged):** `scripts/risk_underwriter.py` prices rows by the
  PR #1694 table (coins; SPECIALTY rider tier and UNINSURABLE, both shown, never blocked) and runs
  a pre-registered three-point duration table with a critical path per case. WAIT and UNKNOWN rows
  are named, never guessed. First readout: the two one-way rows price at 4 coins (no write-lock,
  DRAFT cover); every other row prices 0 because `ruin` is blank on 266 rows (exposure unpriced).
- **Glass box:** both tables live at the top of the script; every price shows inputs, missing
  cover and flags; changes only by Zach's ruling with a version stamp.
- **Weight lab (GAP):** restate the price as weighted dimensions (exposure, door, missing cover,
  draft cover, duration spread, loading) and recompute live, writing nothing, as `src/app/jobs/JobsBoard.tsx`
  does. Exploratory only: the frozen table is what the PR #1694 test scores, so sliding weights on
  rows with known outcomes must never change it.
- **Pre-mortem and disaster recovery (Zach):** failure modes = `abort`; recovery = `rollback` plus
  the surgical spec file per issue. A cover is a strawman while marked DRAFT unreviewed (already
  flagged), steelmanned once someone other than its author attacked it and it held. The
  `scenario-runner` agent writes the best, base and worst pre-mortem for one row. GAP: no field
  records "steelmanned by whom".
- **Reinsurance (second order, GAP):** rows that share a failure source (a common upstream blocker,
  the same unreviewed rollback text, one detector's false positives) are correlated; pricing them
  one by one undercounts. v1 groups rows by shared source and prices the group's worst case once.

## 4e. Build order with nested dependencies (hardened 2026-10-20)

Serial by default. Each step names what it needs (entry), what proves it done (exit), and what
it unblocks. "Needs" is a hard edge; a step never starts before its entry holds.

| # | Step | Needs | Exit (checkable) | Unblocks |
|---|---|---|---|---|
| 1 | Ship ruling on PR #1695 (s4 freeze) | none | Zach rules: merged with --merge and catalog untouched, or held | nothing hard; the tool runs from its branch |
| 2 | Fill `ruin` bands on the rows in play (5 triage + calibration chain), then the rest in batches | tool on any branch | each band proposed by Claude with a reason, confirmed by Zach, written to the row; `backlog_status_check.py --check` exits 0 | 4, 7 |
| 3 | Steelman pass on the 10 DRAFT `abort`/`rollback` texts | none | each text reviewed by Zach: kept, edited or struck; DRAFT marker removed only on his word | 4, 5, 7 |
| 4 | Priced triage: re-run the underwriter, Zach fates the five rows | 2 (those rows), 3 (those rows) | five fates recorded on the triage row | 5 |
| 5 | Pre-mortem the one-way rows (scenario-runner, best/base/worst + recovery plan) into their surgical spec files | 3, 4 (fate is not "drop") | one spec file per one-way row at `runtime/specs/issues/<row-id>.md`, `spec` key on the row | SPECIALTY riders |
| 6 | Arrival-rate model for WAIT rows on the calibration chain | none (reads prod counts read-only) | best/base/worst date to n>=30 from the measured close rate, rate and window stated | timing reading for the intention |
| 7 | Reinsurance: group rows by shared failure source, price each group once | 2, 3 (it groups on those fields) | group table with members and group worst case; self-test | weighted dimensions |
| 8 | Weight lab, exploratory only, never edits the frozen table | 7, and the PR #1694 test set frozen first | live sliders, writes nothing; frozen table unchanged (diff check) | none |

Nested edges inside step 2: a row's band waits on its blockers' bands when the blocker is a
one-way door (exposure inherits downstream). Inside step 4: a row whose upstream is unfated is
fated "hold" by default unless Zach says otherwise.

Kill rule: if step 2 shows most rows are low, the price spread is too thin to matter; stop at 4
and say so, before building 7 and 8.

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

### First intention (stated by Zach, 2026-10-20)

Root: mono no aware. Time is precious and passing; learn to tell the right moment to sow, rest or
strike from the wrong moment to act, before hindsight shows it.

| Horizon | Line (drafted by Claude, confirmed by Zach as right) |
|---|---|
| today | Notice the moment before acting on it |
| this-week | Close one loop at its ripe time |
| this-quarter | Learn my timing from receipts |
| 1-3y (shown as 12 months) | ARCS tells sow, rest, strike apart |

Exclusion, Zach verbatim: "intention is not for summary judgment" or momentum for the sake of it
but reserved for thoughtful action that's deliberate, with meditative consideration for the value
of not acting at all or holding off on implementing a plan until it feels more right or will be
better received in the spirit in which its intended.

Consequence for ranking: "wait" is a valid outcome. A row can be core and still be shown as
"hold", so the snap list must be able to say "nothing yet" for a horizon (GAP: today's
ready-now list always fills).

Core picks: pending, by this process (Zach asked for a more scientific one, 2026-10-20):

1. Horizon fit, mechanical from `cost_prior` (unsized rows: Zach decides).
2. Alignment 0/1/2 per horizon line, scored by Zach from row text and size only, blind to
   ripeness, waves and downstream counts (those are L0's inputs).
3. Hold test from the exclusion: "would acting now be momentum for its own sake?" yes = HOLD.
4. Core = alignment 2 and fits; fewer than 3 fills from 1s; more than 7 breaks ties by forced
   pairs; none = "nothing yet" for that horizon.
5. Sealed cross-check: Claude scores alignment first and commits only a SHA-256 of the scores;
   agreement (kappa 0.6 or more) means the lines are legible.
6. Structure reveal, AFTER picks are recorded (Zach, 2026-10-20: one row may block another; solve
   first-order things first; or build or adjust a tool for the job shape). Show dependency edges
   among the shortlist, outside blockers, and tool fit. Zach may then promote a blocker to core
   as "first-order" or add a "tool gap" row. Pre-reveal and post-reveal picks are both recorded;
   the blind test runs on pre-reveal picks, and a second arm (L2) on post-reveal picks shows what
   the structure added.

Reveal data, computed 2026-10-20 by backlog_graph.py --json, withheld from Zach until step 6:
edges inside the shortlist 14 > 15 > 2 and 18 > 9; outside blockers on 1, 2, 9, 10, 12, 14, 17;
tool NOT-RESOLVED on 7, 11, 15, 16, PARTIAL on 12, NONE (human work) on 13. "HAVE" means the
named tool resolves, not that it fits the job.

### Live dependency map for the compounding chain (refreshed 2026-10-20 from backlog_graph.py --json)

Zach chose to start with the smallest, highest-leverage, compounding steps, picked after the
structure reveal (so these are post-reveal picks; the blind test moves to the next induced
backlog). The map is updated as each step lands; the date above changes with it.

```
backlog-fate-triage-2026-10-18        READY    needs human   tool HAVE      no deps
receipt-randomized-plumbing-closes    DONE     proven 2026-10-20 (5 synthetic closes, seed 20261020)
  receipt-test-real-tag               DONE
receipt-real-interview-closes         HOLDING  now unblocked tool NOT-RESOLVED
  receipt-randomized-plumbing-closes  DONE
accountant-real-cohort-calibration    HOLDING  waiting       tool HAVE
  accountant-calibration-curve        HOLDING  waiting
    accountant-external-cohort-nonzero HOLDING waiting
      agent-receipts-audit-first-conversion HOLDING RIPE  tool NOT-RESOLVED (one-way external send, Zach)
      notomation-receipt-save-nudge   DONE
  receipt-real-interview-closes       (above)
handoff-open-items-closes-when        OPEN     needs human   tool HAVE      no deps
```

Step log: 2026-10-20 plumbing proven; finding: accountant_weekly.py does not print synthetic_excluded (5 here), so the exclusion is invisible in the weekly scoreboard.

Kintsugi seam: the first draft of this chain (in chat) said to release a stale claim on
receipt-test-real-tag first. That came from the 2026-10-18 handoff; the live row is DONE. The
step is dropped.

## Ask

Next: Zach writes the one sentence, horizon and exclusion line, and marks 3 to 7 core rows, before
seeing either list (test step 1). Building waits for that and for s4 to be scored.
