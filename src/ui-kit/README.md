<!-- ARCS ui-kit — atomic design SSOT for self-contained HTML surfaces. -->
# ARCS ui-kit — the visual SSOT pages snap into

This is the visual twin of the anti-slop eval suite (`scripts/slop_lint.py` + `slop_eval.py` +
`provenance_lint.py` + `_PATTERNS/slop-free-rubric.md`). The eval suite gates the *words*; this kit
gates the *look*. Both are single-source, opt-in, ratcheted gates.

**The problem it solves:** every self-contained page used to re-author its own CSS/tokens, so they
diverged and repeatedly failed `scripts/token_source_gate.py`. A census (2026-09-26) of 225 surfaces
found only 42 inherit the tokens (27 inline, 15 link) while 135 re-author the 4-signal palette (74
verbatim under canonical names, 27 under foreign names like `--nc`/`--vc`/`--acc`/`--bc`). Section
labels alone appear under 6 different class names; chips under 5. There was no atomic SSOT for pages
to *snap into*. This kit is that SSOT.

## The atomic hierarchy

```
atoms      → recoil-report/_tokens.css  (color · type · space · radius · glow)
             the ONE palette. Signal hexes #00F0FF #00FF9D #FFD700 #FF4D6D live here and NOWHERE else.
molecules  → recoil-report/27..33, 37 (@dsCard group=Molecules): 27-section-label · 28-chip (pill/badge) · 29-tile (stat/prob) · 30-button · 31-callout · 32-evidence-ref · 33-led · 37-fidelity-grain (sharp/degraded/grain/moire)
organisms  → recoil-report/NN-*.html (the 14 numbered @dsCard primitives):
             01 header · 02 hyperstition-arc · 03 entity-card · 04 signal-delta-table ·
             05 kairos-node · 06 beat-stepper · 07 probability-bar · 08 receipt-table ·
             09 stop-loss-footer · 10 pipeline-tracker · 11 champion-map · 12 role-thesis ·
             13 90day-build · 14 earned-fidelity-twin · 15 case-world
             16 instrument-panel · 17 altitude-ladder · 18 contact-sheet · 19 gate-ladder · 20 transport
                          21 big-button-grid · 22 pad-grid · 23 step-sequencer · 24 segmented-control · 25 resolution-ladder · 26 beat-check
             (16 to 20 are the Instrument Lab group, added 2026-10-15; 21 to 26 were promoted from _ARTIFACTS/phosphor.html on 2026-10-16.
              They use the DESIGN.md conformance tokens, and scripts/kit_primitive_sync.py --check keeps each @prim block identical to the page.)
templates  → a composition of organisms a page declares once and snaps into (see templates.json)
```

Each organism is a `@dsCard` file: line 1 is `<!-- @dsCard group=... name=... -->`, it `<link>`s
`_tokens.css`, and its `<style>` block owns the component classes. `index.html` assembles all of them.

## Templates map 1:1 onto a slop --mode (the organizing spine)

A page declares its template ONCE, and that declaration drives BOTH the visual composition AND the
anti-slop eval thresholds. Visual template and eval mode can never silently drift apart. Registry:
`src/ui-kit/templates.json`. Many templates may share one mode (mode drives thresholds, template
drives composition).

| template | slop `--mode` | kind | canonical example |
|---|---|---|---|
| `recoil-report` | `operate` | instrument dashboard | `src/ui-kit/recoil-report/index.html` |
| `scan-hud` | `operate` | instrument dashboard | `_ARTIFACTS/profile-scan-hud.html` |
| `candidate-brief` | `persuade` | persuasion surface | `public/success-academy.html`, `public/squad.html` |
| `nftt-essay` | `essay` | editorial longform | `public/blog-nftt-the-loop-closes.html` |
| `resume-print` | `resume` | print / paper | `public/vico-resume.html` |
| `instrument-lab` | `operate` | instrument explainer | `_ARTIFACTS/raw-capture.html` |
| `tool-getting-started` | `read` | tool explainer, one swatch per tool | `public/good-rfp-engine.html` |
| `counterpart-onepager` | `persuade` | counterpart proposal one-pager, built from a data file | `_ARTIFACTS/brooks-audit-onepager.html` |

Modes are defined in `scripts/slop_lint.py` `MODE_SPEC` (specificity floors; burstiness is
mode-independent). `essay`/`reflective`/`longform` carry the low 0.10 floor for evidence-dense prose;
`persuade`/`read` = 0.50; `operate`/`resume`/`default` = 0.60.

## How a page enrolls

Add two marker comments near the top of the page:

```html
<!-- @arcs-template: candidate-brief -->
<!-- @arcs-mode: persuade -->            <!-- optional; if present must match the template's mode -->
```

Then (a) inherit the palette and (b) assemble from the kit primitives:

- **Tokens:** inline `recoil-report/_tokens.css` VERBATIM (keep its sentinel line
  `/* ARCS Recoil Report — Design Tokens */`) for a self-contained page, or `<link>` it for a kit
  file. Never rename the tokens. A page may add its own NON-signal tokens in a second `:root{}`
  block (spacing scale, an extra neutral) as long as it never re-declares the 4 signal hexes.
- **Components:** use the template's signature selectors from `templates.json`. If the page needs a
  shape the kit lacks, add ONE new `@dsCard` primitive file to `recoil-report/` (so it can round-trip
  to the DS via `/design-sync`), then use it. Do NOT hand-roll a bespoke redesign.

## The two gates

- **`scripts/token_source_gate.py`** (already on main): a page painting an ARCS signal hex in a
  custom property must inherit `_tokens.css`. Blocks the re-authored-palette class.
- **`scripts/component_source_gate.py`** (this change): the visual twin. For an ENROLLED page it
  requires the template to be registered, tokens inherited, `@arcs-mode` (if present) to match the
  template, and at least `min_signatures` of the template's signature selectors present (proof of
  kit assembly, not bespoke CSS). Un-enrolled pages PASS (`not enrolled`) so it rolls out
  surface-by-surface. `--pair` ratchets: an already-enrolled+failing HEAD warns, never blocks.
  Self-test: `python3 scripts/component_source_gate.py --self-test`.

## The Impeccable DESIGN detector & the ARCS brand profile

The Impeccable detector (`~/.claude/skills/impeccable/scripts/impeccable detect`) reads its design
system from `DESIGN.md` (Inter + JetBrains Mono). The recoil-report kit is a deliberately separate
visual world (Geist / Instrument / Bricolage per `_tokens.css`), so a kit-inheriting page trips
`design-system-*` findings that are BRAND, not slop.

**The real, verified exemption mechanism (do not trust the old `rule: null` gotcha — it is stale).**
Empirically (controlled A/B/C/D/E test, 2026-09-26): a detector finding has no `rule` key; the rule id
lives under `antipattern` and the matched value under `ignoreValue`. The engine maps a config
`ignoreValues` entry's `rule` onto the finding's `antipattern`, `value:"*"` is a wildcard, and `files`
is an enforced glob. Removing the exemptions surfaced 12 findings on a kit page; the real config
produced 0. So **rule-keyed `ignoreValues` DO work.** Add them with the detector's own CLI (JSON-safe):

```
impeccable ignores add-value design-system-color "*" --file "<glob>" --reason "..."
```

or `ignores add-file "<glob>"` to waive ALL rules for a file (whole-file separate world).

**The ARCS brand profile = which antipatterns are brand-deliberate (exempt) vs which stay live:**

- EXEMPT (recoil-report kit grammar): `design-system-font`, `design-system-font-size`,
  `design-system-color`, `design-system-radius`, `dark-glow` (status-LED / earned-fidelity bloom),
  `all-caps-body` + `wide-tracking` (mono tracked-caps label voice), `border-accent-on-rounded`
  (signal-color card border), `side-tab` (the 4px thread rail / entity strip).
- STAY LIVE (real debt + generic AI tells): `tiny-text`, `undersized-ui-text`, `low-contrast`,
  `cramped-padding`, `skipped-heading`, plus generic slop tells (glassmorphism, radial halo, unrelated
  glyph/badge rows) which are simply not in the exempt list.

Proof it is load-bearing on the PoC (`_ARTIFACTS/profile-scan-hud.html`): 120 findings with no
profile → 76 with the profile (only the debt classes remain; all 44 brand-class findings suppressed).

## Known open decision (do NOT resolve unilaterally — cross-session)

`_tokens.css` names Geist/Instrument/Bricolage; `DESIGN.md` + the DS adherence linter permit only
Inter + JetBrains Mono. Enrolling a page onto `_tokens.css` therefore trips `design-system-font`
(handled by the brand profile above) and shifts sans rendering to a system fallback. The reconciliation
(`/design-sync` one component at a time) is backlog item `tokens-css-vs-ds-font-stack-drift` and is not
this change's to decide.

## Specimen pages (2026-10-28)

Every building block gets one standard page: head, live stage, states, anatomy, usage, data, access, relations,
gates, in that order. Write a spec in `src/ui-kit/specimens/<name>.json`, then run
`python3 scripts/kit_specimen.py --all`. The page lands in `recoil-report/` as `NN-<slug>.html`, enrolled in the
`kit-specimen` template, so `component_source_gate` refuses a page that drops a section and
`kit_specimen.py --check` (pre-commit) refuses a hand edit. First specimen: `36-change.html`.

## Pull: parts flock to the pages and jobs they fit (2026-10-31)

`scripts/kit_pull.py` makes the boids rules countable. Cohesion is job fit (the data shapes a part renders, and
the backlog rows that name it). Alignment is shared tokens and gates (links `_tokens.css`, ships a `@prim` block a
generator can pull, paints no raw signal hex). Separation is near-duplicate shapes (a rule copied into another part).

- `python3 scripts/kit_pull.py manifest` writes `kit-manifest.json` (generated, never hand-edited): every kit part,
  the grammar chips, the `src/ui` React parts, and the cards of the local claude.ai/design export when it exists.
  `--check` (pre-commit, on kit or `src/ui` changes) fails when a part's own fields drift from its file.
- `python3 scripts/kit_pull.py score <data.json>` ranks parts for a page's data file by pull. It proposes; it never edits.
- `python3 scripts/kit_pull.py harvest` writes `kit-harvest.json`: rule shapes, flocks of rules that travel together,
  and textures repeated across at least two page families outside the kit. A one-off earns no mold; promote on the
  second real case. Part 37 was the first promotion (the audit report and the good-case pages share the grain).

Parts 38 (wordmark) and 39 (theme toggle) were promoted on 2026-11-04 from the Brooks one-pager and storyboard, each on its
second real case (public/honest.html; the myally pages). The shapes with one case so far are listed as candidates in
`_ARTIFACTS/counterpart-onepager/README.md`.

## Page pattern: the client hub (parts 43 to 51, 2026-11-09)

Promoted from the My Ally Step 1 tab Zach approved on 2026-11-09 (`public/myally-hub.html`, PR 2094): "clean above the
fold, organized below the fold". Each part is a specimen (`src/ui-kit/specimens/<slug>.json` built by `kit_specimen.py`)
whose `@prim` block a page inlines verbatim. Tokens come from `_tokens.css`; light mode is the 39 remap, which every
specimen carries.

**Order, top to bottom:**

1. **Wordmark row** with **51 Display preferences** at its right: the theme switch and the "Aa" reading options side by
   side; the panel opens under the Aa button.
2. **44 Status strip** (`.is-top`, 0.85rem), directly under the wordmark row and above the header, on every tab. It is
   engagement-wide status, not one tab's content: `Not started.` plus `Up next` before any progress, then day segments,
   `Day N · X of Y hours done`, what is ready for review and the comments count.
3. **Header strip**: meta (prepared for, from, status) with the **43 Action menu** at its right, then the tabs.
4. **47 Now note**: one sentence that leads with the reader's next action; dismissible, remembered per note text.
5. **48 Summary disclosure** ("The whole plan"): closed, a title and one exec line; open, **45 Fact tiles** and a quiet note.
6. **45 Fact tiles** where facts stand alone (label outside the box, subgrid rows).
7. **46 Day list** ("Your week"): Before, Day 1 to n, After, one sentence each.
8. **See every item**: a disclosure holding the full-width grid plus the **49 Pinned details card** (bottom-right from
   961px, in flow below that). **50 Term definition** marks terms of art anywhere in the copy.

**Rules:**

- **Rhythm:** one 28px gap between blocks (`margin:0` on the children); tight inside a group, generous between groups.
- **Say it once, less text:** drop a tile or sentence the next block repeats; no pill that does not change a decision.
- **Labels:** one word (Agreement, Details, Discuss), or `format, for purpose` in menus (PDF, for print · Word, for
  counsel · Google Doc, for comments). Label left, action icon right; the call to action is the solid last item.
- **Tabs collapse where they stop fitting, not at a phone breakpoint.** Measure the tab bar's natural width and set the
  hamburger breakpoint above it (the hub's five tabs need about 754px, so it collapses at 900px and narrower). Reason:
  tablets in portrait (768 to 834px) and narrow second-screen windows must get the hamburger, never a clipped tab.
- **The action menu stays in the header above 560px** and moves into the hamburger panel, under the tabs, only at 560px
  and below (`kitActionGroup` in 43).
- **Status honesty:** never an empty 0% bar; a Details toggle only when something is behind it.
- **Reading-options check on every change:** every block uses rem or em and the kit font tokens so 51 reaches it; check
  at 375 and 1280, light and dark, at the largest text size with roomy spacing and the easy-read font, for clipping,
  overlap, overflow and 44px targets; screen-reader pass (heading order, native disclosures, labelled regions, focus
  returned on close, decorative icons `aria-hidden`).

29 Tile and 39 Theme toggle stay unchanged for their consumers; 45 and 51 are their siblings for this pattern.
