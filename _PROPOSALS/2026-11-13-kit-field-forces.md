---
title: Kit field forces, cold-rendering wireframes from the job's shape
date: 2026-11-13
status: proposal (etude 1 run, nothing built)
builds_on: scripts/kit_pull.py score, scripts/kit_periodic_table.py, seed 20 induced render engine (PR 2226), seed 19 atomic composer verdict
---

# Kit field forces

**Why.** Zach (2026-11-13): when a job arrives, induce a full-fidelity wireframe from the design system's parts, the way
the option pickers render three choices per block, and keep playing until the push and pull of parts is a standard
pattern, "like how gravity applies".

**What.** Treat the kit as a field. A job (an interaction goal plus the task beneath it) has a shape; every part feels a
pull toward it. Cold rendering means filling a template's slots with the strongest pulls, then rendering three variants
only where the field is ambiguous.

**Why now.** The pull score already exists (`kit_pull.py score`), the periodic table now records attraction and new cuts,
and seed 20 is building the three-variant renderer. Joining them is cheap now and expensive after each grows its own
vocabulary.

**How.** Before: etude 1 (below). During: add the missing forces, one per change, each with a check. After: every
cold render writes its picks to the catalyst ledger, so the field learns from use. To read this page: forces first,
then the etude that exposed them, then the build order.

## The forces

| Force | Today | Source |
|---|---|---|
| Shape fit | 0.55 of pull | `kit_pull.py score`: data-shape tags the part renders vs the job needs |
| Mass (reuse) | 0.20 | pages that use the part (log scale) |
| Alignment | 0.15 | token use, pullable, no raw signal hex; minus 0.1 for a near twin |
| Job affinity | 0.10 | the backlog row names the part |
| **Verb fit** | missing | the interaction goal (decide, compare, read, act) vs what the part is for |
| **Bond** | missing | layer slots: an organism sits in a template slot, a molecule in an organism |
| **Medium** | missing | the audience preset's tokens; a part that does not read them does not bend with them |
| **Repulsion** | partial | exact twins (moire) and parts the job already holds |

Equilibrium is the pick: the variant a person chooses. A forked part that wins on a second page is an attraction event
and gets promoted (a phase shift in the ledger).

## Etude 1: "decide what to merge next across sessions" (2026-11-13)

Data: the 13 open PRs, as `rank, pr, state, sha, at` rows plus `depends_on` and a verdict. Needs found: evidence,
fidelity, graph, note, percent, scalar, sequence, state, timeline.

Three greedy bundles covered every need:
- **A, pull-greedy:** 29 tile, 15 case-world, 28 chip, 31 callout, 17 altitude-ladder, 55 sound-bite, 34 manifold.
- **B, widest-first:** 34 manifold, 29 tile, 57 ledger-row, 26 beat-check, 31 callout.
- **C, graph-first:** 34 manifold, 12 role-thesis, 35 backlog-graph, 29 tile, 15 case-world.

What it exposed:
1. **Shape fit alone picks nonsense.** 55 sound-bite won "timeline", 15 case-world won "fidelity", 17 altitude-ladder won
   "sequence". The tags match; the jobs do not. That is the missing verb-fit force.
2. **Pull favours small molecules.** No organism covers the merge job, so the render is always a bundle. Bundling
   (set cover over needs) is a first-class step, not an afterthought.
3. **Judgment corrected each bundle** for the rendered etudes (ledger queue, dependency field, decide cards). Each
   correction is a labelled data point for the verb-fit force.

**Pick (Zach, 2026-11-13):** "both but maybe cards first". C stacked over A: the decide cards (61 option, 59 claim
check) above, the ledger queue (31 callout, 29 tile, 57 ledger row, 28 chip) below. B (dependency field) was not
picked. Read as a force: for a decide goal, the option organism sits above the fold and evidence molecules settle
under it, the same order as memory `clean-above-fold-organized-below-fold`. First labelled example for verb fit:
goal `decide` pulls 61 to the top slot.

## A second finding: the medium leaks (MyAlly)

`public/myally-hub.html:108` switches easy-read by overriding `--font-body`, a token name only that page uses. Kit 51
(built from that page) overrides the kit names `--ds-font-sans` and `--ds-font-display`, which every kit part reads. A
kit part placed into MyAlly ignores the reader's font choice. Audience presets must only override kit token names, and
a check should fail a page that overrides a name the kit never declares.

## Build order (each small, each with its check)

1. `layer` as a manifest field (move it from the periodic table into `kit_pull.py`); fix the failing
   `kit_pull.py --self-test` first (parts 38, 46, 50, 53, 64 have no data shape).
2. Verb fit: a `verbs` field per part (from specimen `job` lines), scored against the job's goal; etude 1's corrections
   are the first test set.
3. Bundling: `kit_pull.py score --bundle` returns ranked set covers, not single parts.
4. Field view: `kit_periodic_table.py --field <job.json>` tints tiles by pull and flags boundary slots (top two pulls
   within 0.05), which go to the seed 20 renderer for A, B, C.
5. Medium: audience presets as data plus the token-name check; fix MyAlly's switch.
6. Picks to the ledger: each chosen variant is an event; a fork's second win is attraction.
