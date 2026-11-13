---
title: Seed 19, atomic composer, through the I.D.E.A. loop
date: 2026-11-13
seed: seed-atomic-composer (oracle seed 19)
verdict: BROKEN as pitched (the public-good claim fails a falsifier today); the narrower value claim is HELD, untested
backlog: seed-atomic-composer
proposal: _PROPOSALS/2026-11-13-atomic-composer.md (session distracted-grothendieck; not on main when this was written; cited, not edited)
---

# Seed 19: the atomic composer

## Why
Zach (2026-11-13) wants to compose pages by dragging kit parts into place instead of describing changes in prose or
editing JSON, and called the composer a possible public good: a tool that could work on any design system with a
token file and an atomic component inventory. Before anyone builds it, the seed has to survive the I.D.E.A. loop
(ADR-058): sharpen it, ground it, find the weak joint, attack it, reframe it.

## What was tested
The seed as pitched: drop kit atoms, molecules, organisms and templates (`src/ui-kit/README.md:15`) into the regions
of a page; export a JSON spec that `scripts/tabbed_brief_build.py` builds (schema
`src/ui-kit/tabbed-brief/brief.schema.json`); the same tool works on any design system.

## Verdict: BROKEN as pitched

The public-good claim fails today, on a falsifier whose pass/fail rule was written before it ran.

- **Rule (Detective, fixed before the run):** PASS if the builder reads at least one inventory file and picks its
  renderer from data; FAIL if it reads none and the block-type dispatch is hardcoded.
- **Result:** registry reads 0; 8 literal type branches in `r_blocks` (`scripts/tabbed_brief_build.py:265-289`) plus
  3 expanded first (proof, beliefs, hats), giving the schema's 11 types; one kit path hardcoded
  (`scripts/tabbed_brief_build.py:18`); the token file must start with `/* ARCS Recoil Report`
  (`:108`); the ARCS FIELD OS wordmark is written into the header (`:455`). FAIL.
- **Confirming run (this session, under 1 minute):** the Gravity brief builds clean (77,099 bytes). The same brief
  with one added key naming a different kit is refused: `✖ $: unknown key 'kit'`. The schema has no field naming a
  kit, token file, brand or wordmark, and sets `additionalProperties: false` at the top level
  (`brief.schema.json:7`). No data file can point a brief at another design system; only code can.

The "drop atoms, molecules, organisms and templates" part is metaphor, not mechanism:

- The schema has no free regions. Blocks go into fixed slots (`overview.sections[].blocks`, `tabs[].units[].blocks`,
  `overview.coldread.block`) from a closed list of 11 types.
- Atoms are tokens and cannot be dropped. Templates are page shells, one per page, also not droppable. Only
  `tabbed-brief` of the 15 templates in `src/ui-kit/templates.json` is built from data; the rest are hand pages
  enrolled by a marker.
- `src/ui-kit/kit-manifest.json` lists 88 parts and none has a structured atomic-level field. The level appears only
  in subtitle prose ("Atom 38") and in the group name "Molecules". A palette "grouped by layer", as the composer
  proposal describes in During step 2, would need that field added first.

## What survives (HELD, not tested)
The Alchemist's sharpened claim is narrower and still open:

> An editor writes ordered block arrays into the brief schema's fixed slots, choosing from its 11 block types; the
> existing builder validates and renders. On 3 real tabbed-brief pages, Zach reaches a chosen arrangement in at most
> half his option-board time, and 3 of 3 exports build with no hand edits. Any hand edit, or a fallback to the option
> board on 2 of the 3 pages, kills it.

This is a block-sequence editor for one template, not a general page composer. It cannot be tested yet: option-board
time has never been measured, and the repo has only 2 real brief JSONs (`_ARTIFACTS/tabbed-brief/gravity.json`,
`_ARTIFACTS/gauntlets/2026-11-11-kyle-libra-gravity/brief.json`), not 3.

## Held objections (quoted, not reconciled)

- **Loki (the bet):** "the value claim aims at a step that is not where the time goes." Evidence: of 65 commits to
  `gravity.json`, 48 are copy and about 5% are design plus style. Kill line: "Kill the seed if, on 3 real briefs,
  the arrangement step is under 20% of Zach's total time on each page." Caveat from this session: commit subjects
  measure edits, not minutes; the time share is still unmeasured.
- **Loki:** "Most dropped atoms have nothing to compile to ... At that point the composer is the option board with
  dragging."
- **Curator (reframe, below):** the canvas is the wrong thing to build first; the contract is the public good. This
  sits alongside, not against, the proposal's Before/During plan, which builds the canvas first.
- **Librarian (duplicate risk):** the composer proposal in session distracted-grothendieck covers the same seed and
  the same prior art; "align with that session before writing a second spec." This file is a verdict, not a second
  spec.
- **Alchemist:** "Words and data still have to be filled in for each block, so the time saving may come only from
  layout."

## The orthogonal reframe (Curator)
**The public good is the contract, not the canvas.** The thing other design systems could reuse is a schema plus a
kit binding: which token file, which block types, which renderer per type. Drag-and-drop is one client of that
contract; the option board is another, so it does not need replacing. This makes portability testable before any
UI exists: write one brief against an outside kit's token file and count how many failures come from the schema, the
builder and the tokens. Today the count is decided before the run, because the kit path is code (above), so the
first step of that test is a binding field in the schema, which is a build and outside this seed's scope.

## Prior art (Librarian)
| Part | Fate | Where |
|---|---|---|
| Closed block list, validate then render | REUSE | `brief.schema.json:412-761`, `tabbed_brief_build.py:122` |
| Atomic hierarchy written down | REUSE | `src/ui-kit/README.md:15`, ADR-083 |
| Rank parts by fit for a data file or job | REUSE | `scripts/kit_pull.py` (score) |
| One standard page per block | REUSE | `scripts/kit_specimen.py` |
| Write-back from a live page | EXTEND | `scripts/page_tune.py` takes replace and add patch ops only; no move or reorder op |
| In-page editor surface | EXTEND | `src/ui-kit/token-tuner.js` (`?edit`, RFC 6902 patch); edits text and tokens, not block order |
| Option board (3 variants per block, tagged by layer) | EXISTS, not on main | `scripts/option_board.py` in worktree distracted-grothendieck-72ab37 |
| Reorder or insert op on the patch path | NEW | none |
| Structured layer field per manifest part | NEW | none |
| De-coupling the builder from ARCS tokens and wordmark | NEW | none found |

## Re-plant conditions (what would revive each half)
1. **Value claim:** measure, on the next 3 real briefs, the share of page time spent on arrangement. Pre-register
   it: under 20% composts the composer and the option board stays the method; 20% or more makes the sharpened claim
   above testable, and the cheapest build is a reorder op on the `page_tune.py` patch path, not a canvas.
2. **Public-good claim:** one outside token file plus one outside inventory builds a page through a binding field in
   the schema, with zero ARCS imports (Loki: `tabbed_brief_build.py:24-26` imports `precall_brief_build`,
   `page_tune` and `proof_emit`). Until then the composer is an ARCS tool, not a public good.

## Kill condition
Composted if the arrangement-time measurement in re-plant condition 1 comes back under 20% on 3 real briefs, or if
no outside kit has been bound by 2027-02-13.

## How to read this
The verdict and its evidence are at the top. Everything below "What survives" is either open (HELD) or a condition
for re-planting. Nothing here was built; the only test run was read-only and its files sit in the session scratchpad.
