---
title: Atomic composer (design, not built)
date: 2026-11-13
status: PROPOSED; nothing built beyond the option board
artifact: https://claude.ai/artifact/MtSwj38Jw5YpLsk8Ebow2q (private)
rendered: _PROPOSALS/rendered/2026-11-13-atomic-composer.html
owner: Zach Harris
backlog: option-board-generator (this PR); seeds seed-atomic-composer and seed-induced-render-engine (side sessions)
prior_art: scripts/option_board.py (this PR), src/ui-kit/token-tuner.js and scripts/page_tune.py (PR 2115, 2132, 2136), scripts/tabbed_brief_build.py, src/ui-kit/tabbed-brief/brief.schema.json, src/ui-kit/templates.json, src/ui-kit/kit-manifest.json; memory visual-work-three-rendered-options-per-block
---

# Atomic composer

## Why
You judge pages by looking at them. Today a page changes through prose ("make the stats quieter") or by hand edits
to a JSON data file. Both lose detail, and both take a full round trip before you see the result.

## What
A page where you drag kit parts (atoms, molecules, organisms, templates) into the named regions of a template and
see the page render as you go. Its output is the same JSON data file `scripts/tabbed_brief_build.py` already
builds, so nothing downstream changes. Each part you drop can open an option board (three rendered variants) to
pick its treatment.

## Why now
On 2026-11-13 you picked glass treatments for five Gravity blocks from a three-option widget and asked for that
method on all visual work, "unless I can drag and drop" by atomic layer. The option board shipped in this PR
covers the first half. The composer is the second half. Nothing external forces a date.

## How
- **Before (done, this PR):** `scripts/option_board.py` and the kit template `src/ui-kit/option-board/`. Any
  session can render a block-by-block review as a page, an Artifact, or an inline widget (`--fragment`).
- **During (proposed, about 2 days of build):**
  1. Regions come from the template. For the tabbed brief they are the masthead, the overview tiles, the overview
     sections and each tab's units, as `brief.schema.json` defines them.
  2. The palette comes from `kit-manifest.json` grouped by layer. A region accepts only the block types the schema
     allows there (`p`, `table`, `cards`, `ledger`, `plan`, `coldread` and the rest), so you cannot build a page
     the builder would refuse.
  3. Slots only: parts snap into an ordered list per region. No free positioning, so the output is always valid data.
  4. Export writes the JSON file; the builder's existing `--apply` path takes the diff, the same path the token
     tuner uses.
- **After:** first use on the next counterpart brief. Kill rule, written now: if after three real pages you still
  reach for hand-edited JSON or prose first, the composer stops and the option board stays the method.

## How to read this
The ranked tool table below answers "which visual tool for which job". The composer design above is the only
new build proposed.

## Best visual tool for each job (ranked)

| Rank | Tool | Use it when | Cost | How the result gets back to source |
|---|---|---|---|---|
| 1 | Option board, inline widget (`option_board.py --fragment` into show_widget) | Choosing between treatments of a few blocks while we talk | Lowest: one render, no file, no publish | You click Send; the picks arrive as your next message |
| 2 | Live editor (token tuner, `?tune&edit` on a `--tune` build) | Nudging spacing, widths, breakpoints or wording on a page that has a builder | Low: exact write-back with `--apply`, but only pages with a builder | Copy JSON or Copy CSS, then the page's builder `--apply` |
| 3 | Option board as an Artifact or page | The same choice, made later, on a phone, or by someone else | Low: one publish | Copy my picks, pasted back to the session |
| 4 | Plain HTML preview (browser pane plus `page_gate.py`) | Checking a built page renders at every width before it ships | Lowest, but it checks; it does not choose | Not a design tool; it gates |
| 5 | Atomic composer (proposed) | Building a new page from kit parts, or reordering a whole page | About 2 days to build, then low | Exports the builder's JSON |
| 6 | Claude Design (Design Artifact type, a canvas of artboards) | Exploring a new visual direction with no kit part yet | Medium: canvas work sits outside kit tokens until ported | By hand; a new look becomes a kit part first |
| 7 | Figma | A designer outside this repo needs to edit, or brand assets live there | Highest: a separate tool and file, plus an auth step | By hand, or the Figma MCP reads variables and frames |

### Pick by job
- **Which of these looks?** Option board, inline first; Artifact when it must outlive the chat.
- **This page, slightly different:** live editor.
- **A new page from parts:** the composer once built; until then, the builder's JSON plus an option board per block.
- **A look the kit does not have yet:** Claude Design, then promote the winner to a kit part.
- **Is it ready to ship?** Plain HTML preview and `page_gate.py`.

## Next pass: one-shot prompt and three ways to build it (added 2026-11-13, from your comment)

Run this after PR 2225, 2226 and 2227 merge and the composer-dogfood session logs its first round. Seed 19 found the "any design system" pitch broken and held a narrower claim; seed 20 hardened the option board. The prompt aims at the narrow claim.

```text
Run the hyperstition pass (ethereal, Loki test, receipt evaluation, ROM) on the tabbed-brief block-sequence composer. Do not start until PR 2225, PR 2226 and PR 2227 are merged and the composer-dogfood session has logged its first round of edits on the Louisville draft; if any is missing, stop and say which.

Read first, nothing else to orient: _PROPOSALS/2026-11-13-seed-atomic-composer-idea-loop.md (seed 19, BROKEN as pitched, narrow claim HELD), _PROPOSALS/2026-11-13-seed-induced-render-engine.md (seed 20, HARDENED), _PROPOSALS/2026-11-13-atomic-composer.md, src/ui-kit/option-board/README.md, src/ui-kit/tabbed-brief/README.md and brief.schema.json, src/ui-kit/kit-manifest.json, and the composer-dogfood round-1 log. The design system is the repo kit (src/ui-kit/recoil-report/_tokens.css) plus the glass layer in src/ui-kit/option-board/board.css, taken from the ARCS OS Design System artifact.

The claim under test is seed 19's HELD claim only: a block-sequence editor for the tabbed brief takes half the option-board time per page, with 3 of 3 clean exports the builder accepts unchanged. Do not reopen the "any design system" claim.

Produce one document, _PROPOSALS/<date>-composer-spec.md, with these sections:
1. Product spec: the cold-read header (why, what, why now, how before/during/after with dates, how to read), users and the one job, scope and non-goals, and the kill rule, with its baseline measured from the dogfood log.
2. Design requirements: the regions and the block types each region accepts, taken from the schema; layer tags; keyboard reorder plus drag; empty, error and refused-drop states; the light and dark themes and reading options from kit 51; how the export appears.
3. Implementation plan: step -> verify: check for each step; files touched; reuse first (option_board.py, tabbed_brief_build.py --apply, page_tune.py); no new dependencies; gates (self-test, artifact_wrap_lint.py, page_gate.py --matrix full, the design detector at 0 new findings).
Then render the three construction options below as one option board (scripts/option_board.py), each a real mockup on the Gravity brief's copy, and stop for my pick. Build only the option I pick. Each section ends with a Loki line: the cheapest attack and whether it held. Close with a receipt-evaluation line (graduate, hold or compost) and a backlog row.
```

**Three construction options** (the prompt renders these as one option board for your pick):

- **A. Dashboard widget.** The composer runs inline in chat. One row per page region lists its blocks, with up, down and a part picker that shows three rendered treatments. Send posts one block-sequence line, and the session writes the brief's JSON. Cost: About half a day. Cheapest, but it lives in the chat, and you see lists and thumbnails, not the whole page.
- **B. Component explorer (recommended).** A page or Artifact: a palette of kit parts grouped by layer, each with three rendered treatments to pick from, and the page's regions as ordered slots you fill by drag or keyboard. The page checks the schema as you drop, and Copy JSON exports what the builder reads. Cost: About 2 days. It tests seed 19's held claim directly and reuses the option board.
- **C. WYSIWYG styling.** Extends the live editor on the built brief: insert, move and restyle blocks in place, with a treatment dial per block. It writes back through the builder's apply step. Cost: About 3 days. Highest fidelity, but it changes the shared token-tuner script (825 lines), so it carries the most risk of breaking pages that already use it.

## Open questions
1. Should the composer run as an Artifact (shareable, no local server) or as a `tune_serve.py` page (writes
   straight to the repo)? The default proposed is a local page, since export has to reach the builder.
2. Two side sessions are testing both ideas as public goods through the idea loop. Their verdicts may change step 5
   of the ranking.
