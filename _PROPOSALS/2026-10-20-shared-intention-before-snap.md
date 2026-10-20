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

## Status at a glance (as of 2026-10-20; hardened after a claims-skeptic pass)

Every count below is dated 2026-10-20 unless it says otherwise. Section labels:

| Section | State |
|---|---|
| 1, First intention, D1 trigger, 4b drill-down, surgical spec home | DECIDED by Zach |
| 4k receipt bridge (PR #1698), underwriter rc1 (PR #1695), plumbing proof, status restamp (PR #1697) | BUILT and merged |
| 2, 3, 4, 4c, 4d, 4f, 4i, 4j, 5, 6 | PROPOSED design, not built |
| 4e build order, 4g domino line, live dependency map | PLAN, live; refresh before acting |
| 4h seam ledger | RECORD |
| Risk underwriter design | PROPOSED in PR #1694 (separate) |

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
`scripts/backlog_ripeness.py` (RIPE etc.). REUSE all three.

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

Tactical fields already on the rows (rows carrying the key, out of 327, recounted 2026-10-20 after the ruin fill): blockers and dependencies =
`depends_on` (170) and `unblocks` (160), REUSE via backlog_graph.py; configs = `route` (306) and
`needs` (53), REUSE; risks = `ruin` (71), `door` (32), `gates` (306), REUSE; failure modes =
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

- **Built (read-only, PR #1695 merged 2026-10-20 as 45a93f68, tag risk_underwriter-rc1-2026-10-20; blank ruin prints UNPRICED):** `scripts/risk_underwriter.py` prices rows by the
  PR #1694 table (coins; SPECIALTY rider tier and UNINSURABLE, both shown, never blocked) and runs
  a pre-registered three-point duration table with a critical path per case. WAIT and UNKNOWN rows
  are named, never guessed. First readout at build time: two one-way rows at 4 coins, the rest 0 with `ruin` blank on 266 rows.
  After the 10-row ruin fill (as of 2026-10-20): `ruin` blank on 256; blank two-way rows now read UNPRICED.
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
| 1 | DONE 2026-10-20: PR #1695 merged (45a93f68), rc1 tagged, catalog untouched | none | merged with --merge | 4, 7 |
| 2 | Fill `ruin` bands on the rows in play (5 triage + calibration chain), then the rest in batches (first 10 DONE 2026-10-20, Zach confirmed) | tool on any branch | each band proposed by Claude with a reason, confirmed by Zach, written to the row; `backlog_status_check.py --check` exits 0 | 4, 7 |
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

## 4f. I.D.E.A. as the sprint wrapper (Zach, 2026-10-20)

Zach: the I.D.E.A. macro and loop should be interoperable with this, as a wrapper for a
multi-validated learning loop over a graph of related, globally serialized sprints.

Mapping (REUSE: the I.D.E.A. and Staff of Chiefs agents in `.claude/agents/`, all [CANDIDATE]):

- **Sprint** = one step of the build order (section 4e). Its node and edges come from that table;
  the graph is the loop graph. A sprint closes on its exit check, never on the clock.
- **Wrapper, per sprint, in order:**
  1. `idea-librarian`: prior art for the sprint (runs /prior-art first).
  2. `idea-alchemist`: the sprint's one falsifiable claim, MECHANISM vs METAPHOR. It must match
     the exit column, or the exit is rewritten before work starts.
  3. `idea-detective`: the weak joint and its cheapest falsifier, run before the main work.
  4. `idea-curator`: one orthogonal reframe; recorded, not obeyed.
  5. Work.
  6. Multi-validation, three independent seats: `chief-loki` (break it cheaply),
     `chief-bayesian` (did the evidence move the prior, by how much), and the underwriter re-price
     (did risk go down, by a detector re-run, never by assertion). A sprint passes on all three
     or returns to the queue with the dissent attached.
  7. `chief-conductor`: sequences what survives and names the next ripe sprint from the graph.
- **Learning loop:** each sprint ends with one kintsugi seam line (what broke, who caught it, the
  repair) and one Accountant-readable outcome via `scripts/receipt_outcome_queue.py`. Those feed
  the slow policy update in PR #1694 section 5.
- **Global serialization:** one sprint RUNNING at a time across all sessions and harnesses
  (Claude Code and Hermes). The lock is the backlog row's `RUNNING` claim (`claimed_by`,
  `claimed_at`); git's non-fast-forward rejection on `_QUEUE/induced-backlog.jsonl` is the atomic
  step, the same pattern as oracle numbering. Sprint ids: GAP, `scripts/oracle.py` has namespaces
  adr, handoff, seed, tao only; adding `sprint` is a small change, Zach's call.

**Second pass: hyperstition (Zach, 2026-10-20).** Two passes in a fixed order: I.D.E.A. first, then hyperstition as the second pass that tests and validates what I.D.E.A. let through:

| | I.D.E.A. | Hyperstition (ROM 3) |
|---|---|---|
| Job | de-risk: kill a wrong claim cheaply | make: bring an artifact into being |
| Stages | librarian, alchemist, detective, curator, work, three validators, conductor | ethereal (the vision, stated), Loki test, receipt evaluation, ROM (graduate or compost) |
| Exit | the falsifiable claim survived its cheapest attack | one S-tier, diamond-cut apex artifact that passes its own gates |
| Fails as | analysis paralysis | a beautiful artifact nobody needed |

Guard on "diamond cut": earned fidelity, not maximal (memory `earned-fidelity-not-maximal-diamond-cut`).
The apex is cut only as fine as its evidence supports, and its gates are the repo's own
(page_gate, artifact_wrap_lint, the counterpart gauntlet where it goes outward). Order is fixed:
I.D.E.A. finds what is true; hyperstition makes it real and tests the made thing. A sprint that
fails I.D.E.A. never reaches the second pass. A sprint whose job is pure de-risking (no artifact)
stops after I.D.E.A. and says so. GAP: no row field records the pass reached; proposed
`pass: idea | hyperstition | rom`.

Known limits, stated now:
- The validator seats are the same model family as the worker (memory
  `control-integrity-described-vs-wired`). Loki and Bayesian are pre-scores; the outside check is
  the detector re-run and the outcome, never the seats alone.
- Seven stages per sprint is heavy for a 1 h step. Rule: sprints under 2 h likely run stages 2, 5
  and the underwriter re-price only; the full wrapper is for one-way doors and multi-hour sprints.
- Hermes integration and global rules wait until one sprint has run through the wrapper and its
  receipt shows the wrapper caught something (earned, not decreed).

## 4g. Domino line: the open items in order, each with the moment it falls (2026-10-20)

Zach: line the right dominoes up in the right order, to knock them down at the right time.
Each domino names what tips it (the trigger) and what it tips next. A domino with no trigger is
not in the line. Numbers in brackets are the open-items list from the chat of 2026-10-20.

| # | Domino | Falls when (trigger) | Tips |
|---|---|---|---|
| D0 | Onramp check: is this the right problem? Red team, blue team, inverse, then steelman vs strawman of the premise "timing is the bottleneck, and pricing risk is the first move" | now, before D2; one pass, about 30 min | confirms or swaps the onramp; every later domino inherits its answer |
| D1 | DECIDED (Zach 2026-10-20): the intention test fires by default on the next `/fold` or `scripts/unfold.py` run that adds 10 or more rows, with an override switch: Zach may fire it now on any backlog, skip one trigger, or change the threshold; each use of the switch is logged with his reason, so the default stays honest [14] | default event, or Zach's override | nothing else waits on it; it stops the test from quietly never running |
| D1b | Defensive structural scan (Zach 2026-10-20: weaknesses first, defensive before offensive): for each of the 10 rows with DRAFT cover, list its weak joints and failure modes (detective pass, one line each) | now, before D2; cheap, no fate needed | D2 attacks known weak joints instead of guessing |
| D2 | Steelman the 10 DRAFT covers against the D1b weak joints [2] | now, Zach in chat, one row at a time | D4, D8 |
| D3 | DONE 2026-10-20: PR #1695 merged (45a93f68), tag risk_underwriter-rc1-2026-10-20 [1] | done | D6, D9 |
| D4 | Priced triage: fate the five rows | D2 done for those rows | D7 for the one-way rows |
| D5 | DONE in PR #1698: Accountant scoreboard prints synthetic_excluded [12] | D3 merged (same review rhythm), any session | honest weekly output |
| D6 | Exposure passes down from one-way blockers [6] | D3 merged | correct prices on chains |
| D7 | Offensive pre-mortem (best, base, worst) and recovery spec files for the one-way rows, building on D1b | D4 fate is not drop | SPECIALTY riders on file |
| D8 | Ruin bands for the remaining 256 rows, in batches of about 25 [9] | D2 done (a reviewed cover makes the band honest) | D10, D11; kill rule check: if most land low, stop the line at D7 |
| D9 | Sprint id namespace in `scripts/oracle.py` [3] | D3 merged and Zach says yes | D12 |
| D10 | Shared ledger for pathogen and repair loading [5] | D8 at least half done | D11, PR #1694 section 5 policy update |
| D11 | Reinsurance groups | D8 and D10 | weight lab |
| D12 | Run ONE sprint through the I.D.E.A. wrapper by hand [7, 13] | D9 | measure wrapper cost vs what it caught; decides the light-wrapper rule |
| D13 | Wire the wrapper as a script | D12 shows the wrapper caught something | D14 |
| D14 | Hermes and global config rules [8] | D13 merged and one receipt shows a catch (earned, not decreed) | the whole line runs across harnesses |
| D15 | Duration table calibration [10] | 10 rows on a priced path reach DONE with real hours logged | better critical path |
| D16 | Real outcomes toward n>=30 [4] | each real interview outcome as it lands; no clock, it is an arrival | calibration chain; the timing reading the intention asks for |
| D17 | Weight lab | D11, and the PR #1694 test set frozen first | exploratory only |

Not a domino (a standing limit): the validator seats are the same model family as the worker [11].
It never falls; every sprint states it, and only detector re-runs and outcomes count as outside proof.

Now-ripe set (as of 2026-10-20): D1b, then D2 (D0, D1, D3, D5 done).

**D0 result (run 2026-10-20 by Claude, same model family as the worker: a pre-score, not proof).**
Premise under test: "timing is the bottleneck, and pricing risk is the first move."
Facts used (prod, read-only, 2026-10-20): 271 receipts; provenance real 0, test 189, untagged 82;
3 outcomes scored by the Accountant; external cohort 11 receipts, 0 closed.

- Red team: the bottleneck is outcomes, not risk. With 0 real-tagged receipts, nothing can learn
  timing. Of the rows priced, only 2 are one-way doors; the rest are internal and reversible.
  Building tooling over a 249-row open backlog (327 rows in all, as of 2026-10-20) risks entropy masquerading as motion (WORLD.md).
- Blue team: the underwriter is cheap, read-only, and its first catch was real: the one outbound
  send in the chain priced as SPECIALTY, which matches the intention (do not strike early). The
  plumbing test proved outcomes can close.
- Inverse (how to guarantee the timing intention fails): keep live decisions outside ARCS. That is
  today's state: the handoff's open decisions (the Amy draft, the George reply, the funnel kill
  condition due 2026-10-22, the Vico follow-up) have no receipts.
- Steelman of the alternate onramp: file one receipt per live timing decision this week (sow,
  rest or strike, with a resolve-by date), close each as it lands. Minutes each; it feeds
  `receipt-real-interview-closes` directly and tests the intention on real moments.
- Strawman of the current onramp: pricing a mostly reversible internal backlog before any real
  decision is on record.

Lean (Zach decides): swap the order. Onramp = real receipts on live decisions (D16 moves from a
passive arrival to an active step, now). The underwriter stays as the counterweight on one-way rows
only. D2 onward continue behind it.


**D0 verification (2026-10-20, read-only: Gmail and decision_receipt).** The lean did not survive as stated.
- Amy draft: CONFIRMED open (Gmail draft to amy@recruithaus.com dated 2026-10-18, unsent). No receipt.
- George reply: CONFIRMED open. Bundle sent 2026-10-16, a nudge sent 2026-10-19, no reply seen.
  But a receipt EXISTS: `2026-10-16--scout-wonderful-fde-lead-ex-ante--ZH`.
- Vico follow-up: CONFIRMED open. Email to Joe Schriner 2026-10-14 with a one-page attachment,
  Mixmax reminder 2026-10-16, no reply seen. Receipts EXIST (`2026-10-14--lyndon-followup-close-pr1304--ZH` and others).
- Funnel kill condition: still due 2026-10-22; no receipt found.
- So "the live decisions have no receipts" is confidently false for two of four. The real gap is a
  bridge: ex-ante receipts live in `decision_receipt`, while the Accountant's real cohort reads the
  compass `Receipt` table (0 real-tagged). Outcomes on decision_receipt rows never reach calibration.
- Revised lean (untested): the onramp is the bridge, not new filing. Close the George and Vico
  ex-antes when replies land, and count decision_receipt outcomes in the Accountant as their own
  cohort. Seam banked: the inverse step asserted absence without searching the decision_receipt
  table (memory `false-null-requires-provenance-exhaustion`).

**Wrong-onramp tripwires (pre-registered).** The onramp is mostly a two-way door: everything built so
far is read-only or a proposal, so a wrong onramp costs time, not damage. It is wrong if any fires:
1. D4 priced triage changes no fate and sharpens none (the underwriter added nothing).
2. The mirror sentence and Zach's intention share fewer than 2 of 8 core rows (the backlog is
   pulling somewhere else).
3. No real outcome lands within 30 days (2026-11-19): the calibration chain cannot teach timing,
   so the timing intention needs a different feedback source.
On a fire: stop the line, write a seam line, re-run D0 with the alternate onramp named in its output. Everything else waits on a named trigger.

## 4h. Failure modes banked this session (seam ledger, 2026-10-20)

Format per memory `kintsugi-seam-when-the-test-was-wrong`: seam, detected by, whose error, repair,
heading change. Banked here until the repo-wide ledger (domino D10) exists.

| Seam | Detected by | Whose | Repair | Heading change |
|---|---|---|---|---|
| Told Zach to release a stale claim on receipt-test-real-tag; the row was DONE | live row read during the dependency map | Claude (trusted the 2026-10-18 handoff prose) | step dropped, noted in the live map | verify handoff claims against the live backlog before advising (memory `false-null-requires-provenance-exhaustion`, already banked; not applied) |
| Placed two rows in the horizon grid as examples; Zach read them as priorities | Zach's question | Claude (examples inside a would-be-blind exercise) | said so; marked illustrative in 4b | no example rows inside a blind step |
| Backlog edit rewrote 64 lines (json.dumps re-encoded others) | git diff --stat before commit | Claude | reverted, single-line replace | diff-stat check before any jsonl commit (it caught this one) |
| Picker (AskUserQuestion) returned empty twice | the tool result | harness or client, unclear | switched to wrap_up buttons | prefer button replies with this user |
| Accountant weekly output hides synthetic_excluded | plumbing test | pre-existing tool gap | repaired in PR #1698 (7506fbde) | print every exclusion |
| Built the underwriter before the ship ruling was answered | own review | Claude (read "good safeguard" as a go) | kept on a branch, then merged on Zach's ruling (45a93f68) | a go to build is not a go to ship |
| Hand risk table first said "no overlay applied" only when asked | Zach's question | Claude (did not say what the leans were based on) | priced overlay built | state the basis of every lean in the same message |

Gap: these lines live in a proposal, not a ledger a detector can re-read. D10 is where they move.

## 4i. Evidence rule for the validators: truth axis plus provenance axis (Zach, 2026-10-20)

Truth axis, one state per claim, each earned by its own test:

| State | Earned by |
|---|---|
| Confirmed true | a resolving source shows it; anyone can re-run it |
| Confidently false | the opposite shown, or a falsifier written before the check fired; absence counts only after every place it could live was searched (memory `false-null-requires-provenance-exhaustion`) |
| Circumstantially true, not provable | at least two uncorrelated source families agree, none contradicts, the reason proof cannot exist is stated, and a re-check date is set (memory `defeasible-warrant-freshness-horizon-and-defeater-triggers`) |
| Probable | best explanation; the cheapest test that would move it is named |
| Unknown | stated as unknown, never filled |

Liveness (live or moot) stays a separate axis (memory `claim-exit-lattice-falsification-truth-axis-vs-mootness-liveness-axis`).

Provenance axis (Zach: a truth constructed to look credible, synthesized to make the receiver
believe it is not a false positive). Classified by chain of custody, never by guessed intent:
intent is unknowable from the artifact, and the same signature comes from deliberate fabrication,
from model confabulation, and from self-deception.

| Provenance state | Meaning |
|---|---|
| Witnessed | captured at the moment by the source itself (memory `witness-trigger-attest-in-the-moment`) |
| Reconstructed | written after the fact by someone who was there; labeled as such |
| Relayed | passed through an intermediary; the original speaker is named (ADR-033 ventriloquy guard) |
| Unattested | no chain of custody; carries zero weight however credible it reads (memory `hermes-attestations-carry-zero-evidentiary-weight`) |
| Counterfeit suspected | chain of custody broken AND a counterfeit signature present |

Counterfeit signatures (each a cheap check; two or more together raise the flag):
1. Temporal paradox: the evidence predates its own cause (memory `pathogen-detection-via-temporal-paradox-pre-merge`).
2. Too tidy: a clean reversal or perfect fit with no loose ends (memory `coherence-is-not-correctness-suspect-the-tidy-reversal`).
3. One source wearing many hats: "independent" confirmations trace to one origin.
4. Self-citation loop: the evidence cites the claim, or its own author.
5. Unresolvable reference: an id, sha, URL or quote that does not resolve when checked.
6. Stamped preference: a decision presented as the human's revealed preference that the human
   never stated (memory `counterfeit-system2-fabrication-stamped-as-revealed-preference`).

REUSE before building (Zach, 2026-10-20): honest.arcs.care already runs the deterministic half of
this, client-side, as the front door to `tools/arcs-verb-eval` (route in `src/proxy.ts`). Its five
steps (analysis, assessment, evaluation, synthesis, recapitulation) stamp go or stop on: every
marked fact names a source (signature 5), no new marked fact sneaks in during synthesis (the Op 25
"no new claim" rule), at least one review disagrees (the sycophancy check), and a high-stakes fact
needs two sources from different sites (the uncorrelated-families rule). The page says it plainly:
it cannot tell whether a claim is true. So arcs-verb-eval is the mechanical floor for both axes;
signatures 1, 2, 3 and 6 and the truth states stay judgment, recorded with their evidence.

REUSE from resume-tailor (resume-tailor.arcs.care, `public/resume-tailor.html`; Zach's private
overlay skill `resume-tailor-zach`), same problem shape (nothing written past its evidence):
- Checkability grade, three tiers: documented, self-reported, unverifiable. Maps onto the truth
  axis (confirmed; circumstantial or probable; unknown) and is already field-tested on real sends.
- Record of record: one source outranks the others (LinkedIn export over old resumes, "your own
  say-so"). Here: prod tables and git outrank handoff prose and memory.
- Evidence ledger plus lint: `evidence.jsonl` (one pattern and source per number) checked by
  `scripts/provenance_lint.py --ledger`. Its known blind spot is banked: it misses claims with no
  digit, so a gauntlet runs after it. Same pairing here: lint for numbers, judgment for the rest.
- Stress-test flags become prep: what cannot be defended becomes the pre-mortem list (domino D7).
- Red-team rule: only true hits change a word; edits are subtractive, never puffed. Here: a
  validator's dissent changes the plan only if it survives the evidence rule.
- "Say which stages ran and which skipped": every sprint receipt states the passes it ran.

**Self-deception guard: a hardening floor on every recommendation (Zach, 2026-10-20).**
The system can talk itself into a route. Rule: a lean may be no more confident than the evidence
state of the claims it rests on, and the bar rises with the climb.

1. Every lean lists its load-bearing claims with their truth state (table above).
2. Required floor by stakes: two-way and low ruin, probable claims may carry the lean. Medium
   ruin or a deadline inside the week: every load-bearing claim must be confirmed or
   circumstantial. One-way door or high ruin: every load-bearing claim confirmed, plus a
   pre-mortem on file (domino D7) and the Op 25 cold re-read passed.
3. Below the floor, the lean is rewritten as "untested" and the recommended next move becomes
   the cheapest check that would lift it, never the plan itself.
4. Effort is weighed against the moment: if the check costs more than the plan's worst case on a
   two-way door, act and record the gap (over-hardening is also a failure; memory
   `pessimism-bias-is-a-daemon-gate-not-rigor`).

Caught in this session: D0's "swap the onramp" lean rested on four probable claims (from the
2026-10-18 handoff) and was first stated as a lean anyway. Under this rule it reads "untested;
next move: verify the four decisions live (read-only)".

A counterfeit-suspected claim drops to Unknown on the truth axis, is never scored, and gets a seam
line. Rule for Claude itself: its own unverified output is Reconstructed at best, never Witnessed.
GAP: neither axis is a field on receipts yet; today both squash into `what_unconfirmed`.

## 4j. RC shipping discipline for the eval harness (Zach, 2026-10-20)

Zach: the release-candidate discipline from the monday.com take-home and dj.arcs.care belongs in
the eval harness, as composable, self-sovereign micro-services that run when a current is induced.

REUSE, the two working precedents:
- `ret-rfp-intelligence/scripts/release_check.sh`: golden check, eval run, seeded fuzz (30,000 runs,
  seed 7), report check, freshness, package; under `set -e`, so only a fully green run tags the
  next `rcN-YYYY-MM-DD`, keeps the exact artifact, and writes its sha256. rc46 was the one sent.
- `scripts/phosphor_build.py --release`: a merge does not change what the public sees; the public
  copy (public/dj.html) is written only at a release checkpoint, after the full suite and a
  browser pass (AGENTS.md gotcha 21).

Applied here, each harness piece is one service: `risk_underwriter.py`, `arcs-verb-eval`,
`provenance_lint.py`, `backlog_graph.py`, `backlog_ripeness.py`, the outcome plumbing check.

| Property | Meaning for one service |
|---|---|
| Self-sovereign | stdlib, own `--self-test`, own golden fixtures, reads files or read-only queries, writes nothing it does not own |
| Composable | JSON in, JSON out (`--json`), so one service's output is the next one's input |
| RC-shipped | its own release check: self-test, golden set, a seeded run; only a green run tags `<service>-rcN-date` and records the sha256 of the script |
| Pinned | consumers (the sprint wrapper, the snap list) name the rc they ran; a receipt cites it |
| Public on checkpoint | anything outward-facing updates only at a release checkpoint, never on merge |

"Inducing a current" (my reading, Zach to confirm): an event, not a clock, sets the chain running.
Backlog induction is the first such event: it fires ripeness, graph, underwriter and the intention
step in order, each pinned to its last green rc. GAP: no event runner and no per-service tag scheme
in arcs-v9 yet; the RET script is the template. First candidate to put through it: the underwriter
(PR #1695), since it has a self-test and no consumers yet.

## 4k. Sprint: the receipt bridge (onramp, chosen by Zach 2026-10-20; DONE, PR #1698 merged 7506fbde, receipt 2026-10-20--decision-receipt-bridge-pr1698--ZH)

**Job.** Let outcomes on Zach's real decisions reach the Accountant. Today they cannot: ex-ante
receipts live in `decision_receipt` (1,104 rows on prod at my count late on 2026-10-20, 1,098 earlier the same day; the 854 is the 2026-10-17 universe adapter snapshot), their outcomes in `_STATE/receipt-outcomes.jsonl`
(30 verdict rows on 21 receipts), and the Accountant reads only the compass `Receipt` table
(0 real-tagged).

**Facts the design rests on (read 2026-10-20).**
- Ledger verdicts: held/external 12, held/self 8, dropped/self 5, open/external 4, reeled/external 1.
- The Accountant takes receipts `{receipt_id, cohort, nci_score, horizon, stakes, mode}` and
  outcomes `{matched, regret_score}`; cohorts are fixed in `KNOWN_COHORTS` (founder, external,
  anonymous, test, real, and `decisions`, added in PR #1698); calibration needs 30 closed per cohort (`CALIBRATION_MIN_N`).
- Ledger verdicts are per open line, not per receipt; `decision_receipt` has no NCI and no regret.

**Design (REUSE: `receipt_outcome_queue.py`, `universe_receipts_adapter.py --export`,
`operators/prod_receipt_to_accountant.py` as the adapter pattern, `accountant_weekly.py --ingest`).**
1. Read-only adapter `scripts/decision_receipt_to_accountant.py` (built, PR #1698): joins the export and the ledger,
   emits Accountant-shaped rows in a new cohort `decisions` (one line added to `KNOWN_COHORTS`).
2. Receipt closes when every in-scope open line has a verdict other than `open`. Matched = no line
   `reeled`. Dropped lines are excluded, not counted as held.
3. Only `external` verdicts score. `self` verdicts are carried and reported, never scored (the
   ledger's own rule and effort-policy evidence grade).
4. No NCI on decision receipts, so the decisions cohort cannot be NCI-calibrated. It reports closure
   rate and hit rate by stakes and horizon instead; that is the timing reading the intention asks for
   (did holding or striking at this horizon land). GAP, Zach's call: add a confidence field to new
   decision receipts so a calibration curve becomes possible later.
5. Regret: blank; the Accountant already tolerates a missing regret score (unverified, checked in
   the self-test before relying on it).

**Wrapper (section 4f).** Claim (alchemist): "the bridge reports the externally adjudicated, fully
closed decision receipts exactly, no more and no fewer." Cheapest falsifier (detective): recount
by hand from the ledger and compare. Second pass (hyperstition): the weekly scoreboard shows a
`decisions` line with n, closure and hit rate, and the synthetic and self exclusions printed.

**Exit (checkable).** Self-test with known-bad and known-good fixtures; on today's data the
`decisions` cohort n equals the hand recount; `accountant_weekly.py` prints it; underwriter re-price
of the sprint row recorded. RC-shipped per 4j. Not in this sprint: closing George and Vico (that is
Zach's verdict when replies land), and any Accountant change beyond the one cohort name.

**Risk read.** Two-way door, low ruin: read-only on prod, new script, one tuple entry. Main failure
mode: counting self verdicts as evidence (guarded by rule 3 and a fixture).

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

Step log: 2026-10-20 plumbing proven; finding: accountant_weekly.py does not print synthetic_excluded (5 here), so the exclusion was invisible in the weekly scoreboard (fixed in PR #1698, 7506fbde).

Kintsugi seam: the first draft of this chain (in chat) said to release a stale claim on
receipt-test-real-tag first. That came from the 2026-10-18 handoff; the live row is DONE. The
step is dropped.

## Ask

Next: Zach writes the one sentence, horizon and exclusion line, and marks 3 to 7 core rows, before
seeing either list (test step 1). Building waits for that and for s4 to be scored.
