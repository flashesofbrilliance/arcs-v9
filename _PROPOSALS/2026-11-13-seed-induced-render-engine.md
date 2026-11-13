---
seed: seed-induced-render-engine
oracle_n: 20
status: seed (candidate)
verdict: HARDENED
date: 2026-11-13
backlog: seed-induced-render-engine
---

# Seed 20: the induced render engine (I.D.E.A. loop, 2026-11-13)

**Why.** On 2026-11-13 Zach picked a glass treatment for each block of the Gravity page from a widget that rendered three options per block. The picks came back as one line: "Header C, Stats B, Week One C, Folds A, Evidence rows B. Glass strength 1x." He wants this for all visual work and called it a possible public good, meaning it should work with any design system. This page banks it as a seed and records what the I.D.E.A. loop did to it.

**What.** For a visual change, the engine renders each block as about three variants (A, B, C) from the page's real copy and real design tokens, and tags each block with its atomic layer. The reviewer clicks a pick per block and sets a strength dial. The picks come back as one line, and a builder applies them. The method is memory `visual-work-three-rendered-options-per-block`. The first implementation, the option board generator (not yet on any branch), is being built in session distracted-grothendieck and is not on any branch yet. This seed does not touch it.

**Why now.** The generator is being written right now. The hardening below is cheap to build in from the start and expensive to add later, because the pick log only becomes readable if the variants are built a certain way from day one.

**How.** Before: backlog row `seed-induced-render-engine`, prior-art run, seed 20 from the oracle. During: five seats in order, plus one falsifier run here. After: the verdict, the held objections, and what germination needs. To read the page: the verdict and the hardening list are what to act on, and the seat notes are the evidence.

## Verdict: HARDENED

It survived the cheapest falsifier, but only just. Loki wounded it and did not break it. It is not GERMINATE: the evidence is one use and one stated preference, and no test has compared it against prose feedback. It germinates only once the hardening below exists and the pre-registered test has run.

## The claim (idea-alchemist)

For a multi-block visual change, about three renders per block from real copy and tokens, with click-to-pick and a one-line pick string, get the reviewer to an accepted build in fewer review rounds and fewer reviewer minutes than one render plus prose feedback. A second builder applying only the pick string also gets an accepted build.

- **Mechanisms:** recognition beats recall; a fixed vocabulary (block, letter, dial) removes the step of translating prose into a design; real tokens keep every option buildable.
- **Metaphors (do not build on them):** "induced", "engine", "public good", and "glass strength" as a universal dial (it is one effect's parameter).
- **Pass bar, fixed before testing:** at least 6 changes, arms alternating. The median must be at least 1 round fewer, with at least 30% fewer reviewer minutes. The reviewer can fall back to prose on no more than a third of blocks, and a second builder's build must be accepted in at least 5 of 6 changes.
- **Scope:** ARCS tokens, with Zach as reviewer. "Any design system" is a separate test on a design system that is not ARCS.
- **Prior:** 0.6, a judgment based on one stated preference. Self-report bias from a single reviewer is the main confound.

## Prior art (idea-librarian)

Mostly a composition of tools that already exist. Only the variant generator is new.

| Part | Status | Where |
|---|---|---|
| Variant induction (A/B/C from tokens) | NEW | only hand-made show_widget practice |
| Real tokens | EXISTS | `src/ui-kit/token-tuner.js:36`, `src/ui-kit/README.md:18` |
| Atomic layer tag | PARTIAL | kit parts are tagged (`src/ui-kit/README.md:20-21`); page blocks are not |
| Pick and dial UI | PARTIAL | the tuner has sliders, not a per-block picker; the dial can follow ADR-087's state = f(recipe, t), with 1x as the resting page |
| One-line return | PARTIAL | the tuner exports Copy CSS and Copy JSON, not a pick string |
| Builder apply | EXISTS | `scripts/page_tune.py --apply`, `scripts/token_tuner_inline.py --apply-text` |
| Portability | NEW | the tuner hardcodes ARCS token names |

The librarian's ruling: each pick should be emitted as a tuner export so that `page_tune.py --apply` works unchanged. Do not build a second apply path. Every rendered option must pass the earned-fidelity floor (`artifact_wrap_lint.py`, `page_gate.py`, a sweep from 360 to 1440). Outside prior art, from general knowledge and not checked: Figma Variants, Storybook Controls with Chromatic, Framer and Webflow variant states, bandit A/B testing (which picks by traffic, not by a reviewer), and Brad Frost's Atomic Design.

## Weak joint and falsifier (idea-detective), run here

**Weak joint:** the baseline. The board can only save visual-choice rounds. If visual changes already land in about one round, there is no room for the claim to show anything.

**Pre-registered before counting:**
- **Data:** origin/main, last 60 days, no merges, files under `public/`, `_ARTIFACTS/` and `src/ui-kit/`.
- **What counts as visual rework:** `style`, `design` or `polish` commits, plus `fix` commits whose subject names a visual term.
- **A change:** a chain of such commits on the same file, each within 7 days of the last. Its rounds are the chain plus the introducing commit.
- **Kill:** fewer than 6 changes with at least 2 rework commits, or a median below 2.0 rounds.

**Result (2026-11-13):**
- 119 visual-rework commits across 73 unique changes.
- 29 changes had at least 2 rework commits, against the kill floor of 6. **Survives.**
- The median is 2.0 rounds, against the kill line of below 2.0. **Survives, on the line.**
- Distribution: 44 changes at 2 rounds, 13 at 3, 5 at 4, 4 at 5, and one each at 6, 7, 8, 10, 12, 14 and 19. The long tail is myally-hub (19 and 10), cia-brief (14), myally-proposal (12), success-academy (8) and gravity-brief (7).

**Reading:** the effect has room to show only in the tail. For the median change, saving one round means accepting on the first pass. The test should be aimed at multi-block pages with long histories, not at the median. Two caveats: the class includes `fix` commits that are defect fixes rather than choices between options, and chains that share commits across files are only partly deduplicated. Both make the tail look heavier than it is.

**Ruled out of scope:** copy rework. On gravity it dominates (48 copy commits against 4 visual ones), and the board does not claim to fix copy.

## Cheapest attack (chief-loki): WOUNDS

The one-line pick string loses information. In the only real use (commit `3f79881e` on branch `claude/tabbed-brief-lockup`, not yet on main), the builder wrote "Header C, Stats B, Week One C, Folds A, Evidence rows B" into a CSS comment and described only the picked variants. The unpicked options appear neither at that commit nor on main, so the letters point to renders that are gone. The same session rendered the options and applied the picks, so the string has never been tested on its own. That use also needed "one fix round". As stated, the second-builder half of the claim cannot be tested.

## Orthogonal reframe (idea-curator)

Treat it as a calibration tool for the design system, not as a review tool. Each variant is a named change to one token or one rule, for example "Stats B = gap.lg plus glass 1x". Then every pick is a vote on whether a default is right. If the same change keeps winning for a layer across pages, that default is ready to promote. If picks scatter, it is a real per-context choice and should stay open. This follows NOTOMATION: the revealed preference proposes the change and a human approves it. It changes what to build first: a generator that can only emit named token or rule changes, plus an append-only pick log. The picker UI can stay rough.

## Hardening the verdict depends on

1. **Persist the board.** Before the widget is shown, write a manifest to a committed path: block id, atomic layer, and for each letter the token diff or CSS-snippet hash, plus a content hash. (Loki)
2. **Address the string.** The pick string carries the manifest hash, for example `board:<sha> Header C, Stats B...`, so a letter can still be resolved after the widget is gone. (Loki)
3. **Variants are named changes.** Each option is a token or rule change, not free-form markup, so the pick log reads as votes on defaults. (Curator)
4. **One apply path.** Each pick is emitted as a token-tuner export, and `page_tune.py --apply` applies it. (Librarian)
5. **Gate every option.** No option is shown at SHARP fidelity unless it passes wrap-lint and page_gate. (Librarian)
6. **Pick log.** Append-only (block, layer, change ids shown, chosen, dial, page). This is the dataset that makes it a public good. (Curator)

Items 1 to 4 belong to the `the option board generator` owner. They go to session distracted-grothendieck as suggestions; this session does not edit that branch.

## Held objections (not resolved)

- **Loki:** until the board is persisted, the second-builder arm cannot be tested, and the claim stays half-unfalsifiable.
- **Detective:** the median sits exactly on the kill line. With one reviewer reporting on himself (joint d), the test has no cheap retrospective control.
- **Alchemist:** "public good for any design system" stays a METAPHOR until a token adapter runs on one design system that is not ARCS.
- **Not run:** who chooses the axis of variation (the reviewer only sees the builder's frame); whether picks that are each good on their own still make a coherent page together; and the cost of rendering about three times as much per block.

## Germination conditions

- **Soil:** the option board generator exists with hardening items 1 to 3, and there is one non-ARCS token set.
- **Trigger:** the next multi-block visual change to a long-history page (myally-hub, cia-brief, gravity-brief).
- **Test:** six changes with alternating arms, against the pass bar above. Run the second-builder arm in a fresh session that gets only the string and the manifest path.
- **Kill:** the pass bar fails, or the seed has not germinated by 2027-02-13.
