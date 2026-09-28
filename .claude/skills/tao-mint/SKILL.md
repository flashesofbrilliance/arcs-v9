---
name: tao-mint
description: Mint net-new Tao of ARCS proverbs from a source (an ADR, a session recapitulation, a decision) via the deep-kairos recapitulate pass, per the ADR-041 5x5 grid (D/R/W/C/H x Analyze/Assess/Evaluate/Synthesize/Recapitulate). Appends load-bearing proverbs (never padded) to the compounding Tao SSOT, which the front-of-house Tao and all visual-engineering artifacts render from. Use to compound the oral history from each decision, and to feed the brand's visual pipeline.
---

# /tao-mint — compound the oral history, one decision at a time

> **Governed by:** ADR-041 (recapitulate = deep-kairos scan/audit/distill; the 5x5 proverb grid;
> the anti-padding rule). Renders through: DESIGN.md ("Render Through the Fog"). Feeds:
> `_ARTIFACTS/arcs-tao.html` (front of house) and Phase-2/3 visual engineering.

## What it does

Turns a **source** (usually a filed ADR, but also a session recapitulation or a single decision)
into up to **25 net-new proverbs** and appends the load-bearing ones to the **Tao canon**
(`_CANON/tao-proverbs.jsonl`, oracle-numbered, append-only; the single source of truth since the
Option A ruling of 2026-09-27, `_DECISIONS/CANON-COLLISION-tao-two-books.md`). The rendered book
`runtime/tao/proverbs.json` is a DERIVED projection: never edit it by hand, regenerate it. The Tao stops being hand-curated and starts *compounding*: every
decision the house makes grows the oral tradition, and the same SSOT is the source material for
visual artifacts (each proverb -> a silkscreen card via the DESIGN.md grammar).

## The grid (ADR-041)

Five aspects (kimonos) x five verbs = 25 cells:

- **D** Decision (the sharp DEWY-D question; the floating receipt type)
- **R** Risk / Ruin (gauntlet: BAR / LAB / COURT / KKL / Funhouse)
- **W** Window (bearing + the safe/dangerous entry conditions, not just why-now)
- **C** Clarity (Clarity / Confidence / Coherence / Cohesion / Conviction)
- **H** Horizon (time / capital / opportunity cost / leverage / reward)
- x verbs: **Analyze -> Assess -> Evaluate -> Synthesize -> Recapitulate**

## Procedure

1. **Deep-kairos recapitulate the source** (ADR-041): scan it at depth, audit GAAP/non-GAAP, distill.
2. **Fill only the cells the source genuinely populates.** A proverb is earned when it states a
   load-bearing truth the source actually carries. **Tilde the empty cells** (`~`). A grid that comes
   back full is the tell of padding.
3. **Net-new only.** Dedup against the SSOT: a proverb that restates an existing one is *sediment,
   not signal* (the water rule). Only genuinely new drops are minted. If a mint run yields nothing
   new, that is an honest zero, not a failure.
4. **Custody on every proverb** (ADR-081/041): each carries `{aspect, verb, source, minted}`. No
   custody, no mint.
5. **Voice:** serif-register, carried-in-the-mouth, plain language, NO em-dashes (DESIGN.md
   Three-Voice + PRODUCT.md). A proverb is a truth shaped to be passed down, not a clever line.
6. **Number through the oracle, write canon, regenerate.** Per proverb: `python3 scripts/oracle.py next tao`
   gives the id (`tao-NNN`, never inferred); append one line to `_CANON/tao-proverbs.jsonl` with the
   canon fields plus `grid_id` (the grid cell id, e.g. `adr041-C-recapitulate`) and a `grid` object
   carrying the custody `{seq, aspect, verb, source, minted, text, movement, gloss}`; then run
   `python3 scripts/tao_project.py` and commit canon + `runtime/tao/proverbs.json` + `_SEEDS/_oracle.json`
   together (pre-commit runs `tao_project.py --check`). A proverb that cites a blog post carries the
   post slug in `source` or `associations` so `scripts/tao_coverage_check.py` can see it.

## Anti-goals (the honesty floor)

- **Never pad to 25.** The number is the grid, not a quota. A manufactured proverb is a non-GAAP
  line in GAAP's clothes (ADR-041). Fewer earned beats more filled.
- **Never mint a duplicate.** Restatement is sediment. Dedup first.
- **Never keep a proverb for being quotable.** Load-bearing or cut (the considered molt).
- **Never cross voices** (no mono proverb, no em-dash).

## Canon entry shape (`_CANON/tao-proverbs.jsonl`, one JSON object per line)

```jsonc
{
  "id": "tao-259",                       // from `python3 scripts/oracle.py next tao`; never inferred
  "type": "proverb", "tenant": "user0",
  "aspect": "C", "aspect_name": "Clarity", "verb": "recapitulate",
  "source_adr": "ADR-041",               // custody: where it was distilled from (ADR, seed, post slug)
  "text": "Keep the load-bearing grain; a line kept for being quotable is sediment, not signal.",
  "minted": "YYYY-MM-DD",
  "provenance": "one line: who asked, what closed on it, session or witness ref",
  "associations": [{"rel": "generated-from", "ref": "ADR-041"}],
  "grid_id": "adr041-C-recapitulate",    // the rendered id; a row is projected iff it carries grid_id
  "grid": {"seq": 243, "aspect": "C", "verb": "recapitulate", "source": "ADR-041",
           "minted": "YYYY-MM-DD", "text": "…cased form as rendered…",
           "movement": "VI · The Echo", "gloss": null}   // seq = next reading-order slot
}
```

The projection `runtime/tao/proverbs.json` is rebuilt by `scripts/tao_project.py` (self-test:
`--self-test` proves zero rows lost and the three renderers byte-identical).

## Forms

- **Command (this skill):** `/tao-mint <source>` mints from one source now.
- **Job/hook (optional, later):** a hook on new `_DECISIONS/ADR-*.md` files that runs this at file
  creation, so every filed ADR compounds the Tao automatically. Not wired yet (stubbed, `~`).

## Feeds visual engineering (the point)

The SSOT is the bridge past written/oral tradition into visual artifacts: each proverb is a card, a
poster, a motion beat, rendered through DESIGN.md ("Render Through the Fog"). Written -> oral ->
visual, one compounding source.
