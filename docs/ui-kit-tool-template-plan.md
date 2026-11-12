# ui-kit as the master template set for good.arcs.care tools: plan

Status: APPROVED A–E by Zach, 2026-10-30. Steps beyond 2 still go one PR at a time.
Grug rule: plan small, ship small. One page per PR.

## 1. Inventory (what exists today)

Templates in `src/ui-kit/templates.json` (origin/main): recoil-report, scan-hud, candidate-brief,
nftt-essay, resume-print, instrument-lab, recoil-player, kit-specimen. A ninth, `tool-getting-started`
(mode `read`, signatures `.g-chip .eyebrow .rules .stats .panel`, min 3, one `--tool-accent`), exists
only on `claude/good-rfp-engine` (PR flashesofbrilliance/arcs-v9#1876).

| Page | File | Job it does | Enrolled? | Fits | Funnel stage |
|---|---|---|---|---|---|
| honest | `public/honest.html` (108 KB, has video) | check a claim before you say it | no | `tool-getting-started` for the install half; the long explainer and video stay page-specific | graduate |
| resume-tailor | `public/resume-tailor.html` | tailor a resume honestly | no | `tool-getting-started` (its output samples link to `resume-print` pages) | graduate |
| germinate | `public/germinate.html` | grow a durable seed into a tool | no | `tool-getting-started` | seed |
| rosetta-shell | `public/rosetta-shell.html` | lossless shell translation | no | `tool-getting-started` (germinate and rosetta-shell are near clones, so they enroll together) | seed |
| instruments | `public/good-instruments.html` | catalog of the field instruments | no | not a tool page. Needs a small `tool-index` template (cards that link out); it wears no swatch | hub |
| rfp-engine | `public/good-rfp-engine.html` (PR branch) | answer an RFP from a known corpus | yes, the reference | `tool-getting-started` | graduate |

Facts to check before enrolling: none of the five live pages carries an `@arcs-template` marker or the
kit signature classes yet. Each uses `--cyan` most (12 to 25 uses), then green or gold, so today the
pages use cyan as decoration, which DESIGN.md's Semantic Color Rule forbids.

## 2. Funnel stages map to templates, not to new pages

- **seed**: an idea with a working core. Template: `tool-getting-started` with the `not-proven` list
  as the main content and no stats.
- **graduate**: a tool with dated measurements and a copy-ready install. Same template, with stats
  and the rules panel filled in.
- **instrument**: a graduate that is used live and reports state. Moves to `instrument-lab` (or
  `recoil-player` for replay). This is the only stage change that changes the template.

A tool moves to the next stage by filling in sections, so no page gets rebuilt.

## 3. Reuse or fork: the rule

Start from inventory. For a new or existing tool:

1. **Find its JTBD row.** Every tool page cites one `job:backlog:<id>` (or `job:memory:`) node from
   `scripts/universe_jtbd_adapter.py` output. No row: write the row first and build no page.
2. **List the tools already serving that job.** These are the `tool:*` nodes with a serves or
   design-dep edge to that job (`runtime/specs/tool-catalog.json` plus the graph). If one exists,
   **extend it** (a mode, flag or section) and do not ship a new tool.
3. **Reuse the template** when the page does what `tool-getting-started` already does: say what the
   tool is, how to install it, what it proved and what it has not proved. Different content,
   different swatch, same slots. That covers all six pages above.
4. **Fork a new template only when the problem shape differs**, meaning the page needs a section
   type the template does not have *and* at least two pages need it. One page with a special
   section keeps that section page-local next to the kit primitives. Examples: a live readout is
   `instrument-lab`, and a catalog of tools is `tool-index`.
5. A fork gets an entry in `templates.json` (mode, signatures, canonical example) in the same PR as
   its first page, so the gate never sees an unregistered template.

## 4. Swatches checked against DESIGN.md

The signal hues are taken: cyan 184°, green 157°, gold 51°, orange 30°, red 349°, violet 255° and
magenta 292°. A `--tool-accent` should sit at least about 15° of hue away from all of them, stay
at the muted chroma of the rfp swatch, and be used only on structure (rules, borders, eyebrow ticks).

| Tool | Swatch | Hue | Verdict |
|---|---|---|---|
| rfp-engine | `#00748e` (shipped on PR) | about 191° | **Conflict**: it reads as dark cyan (bearing). Proposal: move it to steel `#3d6a9e` (about 212°) |
| honest | proposed `#6f8f3a` (moss) | about 82° | clear of gold and green |
| resume-tailor | proposed `#9a5b7a` (mulberry) | about 330° | 19° from red. Check it beside the red chips |
| germinate | proposed `#3f8a5e` (fern) | about 145° | **too close to green (157°)**. Use `#5f8a3f` (about 95°) instead, and keep honest at 82° only if the two never appear side by side |
| rosetta-shell | proposed `#4f5fa0` (slate indigo) | about 229° | clear of violet and cyan |
| instruments | none | n/a | hub pages wear no tool swatch |

Each swatch needs a contrast check before it ships: as a border it needs 3:1 against #0d1117 (WCAG
1.4.11). It is never used as text, so text contrast does not apply.

## 5. Order of work (each step is one PR and waits for Zach's go)

1. Land #1876 (`tool-getting-started` plus rfp-engine), with the rfp swatch fixed or kept as Zach decides.
2. Enroll resume-tailor (the smallest graduate). Set its swatch and move its cyan used as decoration to neutral.
3. Enroll germinate and rosetta-shell together (near clones) as seeds.
4. Enroll the install half of honest. The video and long explainer stay page-local.
5. Add `tool-index` and enroll instruments.
6. Add a JTBD row citation to each page (`data-jtbd="<id>"`) so the reuse rule can be checked.

## 6. Go-aheads needed from Zach

- A. Use the stage model in section 2 (seed and graduate share one template, instrument switches)?
- B. Adopt the reuse/fork rule in section 3?
- C. Change the rfp-engine swatch from `#00748e` to `#3d6a9e` because the old one reads as cyan?
- D. Approve the proposed swatches (or pick others)?
- E. Start step 2 (resume-tailor enrollment)?
