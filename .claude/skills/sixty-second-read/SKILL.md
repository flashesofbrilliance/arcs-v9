---
name: sixty-second-read
description: Produce a counterpart "60-Second Read" — a bite-size four-beat artifact (bet -> outcome -> spark -> move) with the scoring collapsed behind a closed-by-default toggle. Plain english surface, no em-dashes, no ARCS jargon. The read is the SEED; every longer form (NFTT post, atlas entry) is a condition-gated resynthesis serialized against it via the Yoav Protocol. Use after a call whose loop you want to close in a form the counterpart can actually consume, or when forge needs the bite-size tier of a counterpart family. Composable: forge may call this as a stage.
---

# sixty-second-read — the seed tier of a counterpart family

Golden reference: the hand-built Yuri artifact (claude.ai `17a1923c-09a8-4653-b5e0-6ab6bf78f28b`,
source-verified 2026-08-30 against the Jul 15 LinkedIn DM + Jul 23 Granola transcript). Canon
trail: last entry of `_STATE/witness/2026-08-29.jsonl` (germination-chain thesis, Yoav nod,
bidirectional rule, attribution correction, Louisville lineage edge). Engine:
`scripts/sixty_second_read.py` (stdlib, zero LLM). Contract: `scripts/sixty-read.schema.json`.

## The one idea: the read is the seed

Artifact tiers (60s read -> post -> atlas) are not separate documents. They are **altitudes of
one serialized object**. The read commits first; every longer form is a **resynthesis that
compounds on the committed read**, globally serialized against the SSOT through the Yoav
Protocol (`operators/arcs_yoav_store.py`: FutureVector = the dormant seed's possible longer
forms; CommitEntry = a sprouted resynthesis with provenance; the serializability check = the
anti-drift gate). Drift between tiers becomes structurally impossible, not editorially policed.
Same invariant, third domain: Louisville omakase said it first ("every later course is this
one, unfolded"); the sixty-second-read says it for the call read; the NFTT sprouting stage
says it for the publication chain.

**Bidirectional rule.** The chain forward-propagates artifacts and back-propagates truth.
Correction has one legal entry point: upstream, in the SSOT — never patch a leaf. A
resynthesis that FAILS to serialize is never discarded: `commit` writes an upstream
resolution receipt next to the seed and exits 3 (conflict-quarantine; every gate a detector,
ADR-051/052). Fix the SSOT, then re-commit.

## The four beats (exactly four, locked)

| Beat | What it is | Renders as |
|---|---|---|
| **bet** | The read filed BEFORE (who they are / what they want / what you want) | three cyan cards, the pre-brief snack shape |
| **outcome** | What actually happened, scored against the bet, incl. the honest miss (`miss: true`, amber) | three green cards |
| **spark** | The ignition moment where recognition fired. Distinct beat, never folded into outcome. Canon: the sparkplug (chan-suh SSOT sparkplug entry + ADR-053) — a small, precisely timed spark converting the counterpart's OWN stored potential to kinetic; the energy was theirs the whole time (NOTOMATION signature). Evidence-anchored: a verbatim quote. | violet ignition panel |
| **move** | ONE move, never a menu (gate enforces) | amber panel + math-on-pull |

Math (the scoring table) lives behind a `<details>` closed by default — "don't show me the
math, tell me what to say/do" (Yuri, Aug 28, the feedback that locked this design).

## Division of labor (gotcha 11: teleport to terminal)

**Agent judgment — you, before the seed exists:** cold inference (author the bet from pre-call
sources only), spark detection (find the ignition line in the transcript), synthesis prose
(card heads/bodies, hero, move copy). Everything else is mechanical and runs in the engine:

```bash
python3 scripts/sixty_second_read.py validate <seed.json>          # structure
python3 scripts/sixty_second_read.py gate     <seed.json>          # temporal + provenance + plain-english + single-ask
python3 scripts/sixty_second_read.py settle   <seed.json> --pipe-evaluator \
    --source transcript=<granola.txt> --source dm=<dm.txt>         # score the bet; KINTSUGI gate; speaker-provenance lambda
python3 scripts/sixty_second_read.py render   <seed.json> <out.html>         # refuses on open gate findings
python3 scripts/artifact_wrap_lint.py <out.html>                   # wrap-regression class gate
python3 scripts/sixty_second_read.py commit   <seed.json> --tier read        # Yoav serialization (banking the seed)
python3 scripts/sixty_second_read.py ripeness <seed.json> --context <ctx.json>   # germination range-check
python3 scripts/sixty_second_read.py commit   <seed.json> --tier post --context <ctx.json>  # SPROUT (gated + ledgered)
```

## The speaker-provenance lambda (ventriloquy paternity test)

Ventriloquy is the sixth coordinate (SPEAKER) of the ADR-033 Serialization Pathogen
Family (ratified 2026-08-29; case: `_PATTERNS/2026-08-29-ventriloquy-pathogen-investigation.md`):
one voice's words re-read as another's — the speaker tag dropped at compression,
reinferred at resynthesis toward warm hosts. The payload is autoimmune: recoil scores its
own echo. `scripts/attribution_provenance_lint.py` is the mechanism-first gate, wired into
the settle beat: every counterpart-attributed quote must fuzzy-match a `Them:` turn (or
counterpart-authored text like a DM). Match against a `Me:` turn = CONTAMINATED; no match
= UNSOURCED (paraphrase-label or strike). A failed check is never just discarded: it
writes an upstream resolution receipt against the artifact that carried it — fix the
SSOT/memory upstream, never the leaf, then re-run. Standalone form for any SSOT/page:

```bash
python3 scripts/attribution_provenance_lint.py --artifact <ssot.json|page.html> \
    --source transcript=<granola.txt> [--source dm=<dm.txt>]
```

## Germination: universal axes, earned ranges, the conditions ledger

Do not invent bespoke trigger prose. Conditions = fixed universal axes with per-seed
RANGES: **moisture** (attention/bandwidth) · **temperature** (Kairos/timing) · **oxygen**
(live demand: an open question the seed answers) · **light** regime (exposure — some seeds
REQUIRE dark = internal-first, some require light = public) · **medium**
(substrate/provenance density) · **stratification** (required dormancy;
`requires_gauntlet` = serotiny, opens only under adversarial fire). Ripeness is a
mechanical range-check of the context vector against the seed's ranges. Ranges are
EARNED from settled outcomes, never decreed — new seeds carry
`ranges_provenance: provisional` until outcomes calibrate them.

Every sprout decision LOGS: `commit --tier post|atlas` appends a `sprouted`/`refused`
event to `_SEEDS/ledger.jsonl` carrying the `conditions_present` snapshot plus which
axes matched/missed — a refusal without a receipt violates every-gate-a-detector
(ADR-051/052). On a committed sprout, `seed_state` moves dormant -> sprouted in the seed
file. Tests set `SIXTY_LEDGER=<scratch path>`; never write synthetic events to the real
ledger.

## Run order

1. **Gather.** Read the war-room SSOT (`runtime/recoil/generated/<date>-<name>.json`) and the
   raw sources (transcript, DM thread). Quotes attributed to real people must trace to a
   source actually read this session; record when/how in `provenance.sources[].verified`
   (the gate blocks an empty `verified`). Memory digests are jogs, not rewinds.
2. **Author the seed** to `_ARTIFACTS/sixty/<seed_id>.60s.json` per the schema. Author the bet
   beat from pre-call evidence only (the ex-ante receipt in the SSOT); never retro-fit it.
   Fill `future_vector` with the dormant longer forms and their germination conditions.
3. **validate -> gate.** Fix findings in the SEED (never in the render). The gate is an
   honesty refusal: `render` produces no output while findings are open.
4. **settle --pipe-evaluator --source ref=path...** FATED maps onto the beats
   (facts=outcome, assumptions=bet, tradeoffs=miss, emotions=spark, direction=move).
   Somatic/axiom signals are NEVER fabricated; a KINTSUGI `warn` on those is honest, a
   `halt` blocks. The --source mappings arm the speaker-provenance lambda (below):
   CONTAMINATED or UNSOURCED halts settle and writes the resolution receipt.
5. **render + wrap-lint + sweep.** Screenshot-sweep 375 / ~790 / desktop before calling any
   render done (the ~790px band is where the wrap class bites).
6. **commit --tier read.** Seed enters the Yoav log (`<seed>.yoav.jsonl`), `seed_state:
   dormant`. Exit 3 = quarantined: read the `.resolution.json`, resolve upstream, re-commit.
7. **Ship gate (human).** Nothing counterpart-facing sends without Zach's explicit go. The
   internal/external air-gap holds: war-room scores never appear on the surface.

## Register + design system (do not relitigate)

Dark cockpit, IBM Plex Mono/Sans, per the golden reference. ONE `--measure` px token,
auto-fit minmax grids, `text-wrap: balance/pretty`, no per-role ch caps, no em-dashes
anywhere (see `_PATTERNS/arcs-artifact-css-base.css`). Accents: cyan=bet, green=truth,
amber=miss+move, violet=spark. Plain english on the surface: the engine's jargon gate is a
floor, not the bar — read the copy as the counterpart before shipping.

## Attribution guardrails

- The cold-start / bookmark / "without needing to rebuffer" composable-meeting vision is
  ZACH'S OWN line (his Aug 28 email to Yuri), not Yuri's. Never import Zach's language into a
  counterpart's mouth (same class as the Jeben/Spock correction).
- In Granola transcripts "Me" = Zach, "Them" = the counterpart.
- Quote rule: their words verbatim, filler-cleaned, never paraphrased; not-in-quotes text is
  labeled as Zach's read.

## Designed next stage (NOT built): the NFTT sprouting fork

Second-order, deliberately out of scope here: a sprouting stage
`(seed, SSOT, conditions) -> post` that forks `nftt-story-factory` to consume this seed
schema. It must RUN ON YoavStore (or its contract) as the artifact-tier commit log, not
merely cite it (witness 2026-08-29 implementation directive): germination conditions gate
the sprout (resolved? counterpart-safe? kairos window open?), the post is a CommitEntry
whose provenance points at the seed commit, and a post that fails to serialize emits the
upstream resolution receipt. `seed_state` moves dormant -> sprouted on the first such commit.
If an ADR gets minted for the germination-chain thesis, allocate the number via
`python3 scripts/oracle.py next adr` — never infer.

Queued design addenda (ratified 2026-08-29 in the parent canon session, carried in the
witness entries; NOT built): **Kairos-first ripeness** — the temperature axis should
inherit from a `Kairos.window()` half of `operators/arcs_operator_kairos.py`, with mode
reading as an input axis; **expression-strategy layer** — mechanism/strategy/axes/ranges
with deciduous-vs-evergreen urgency semantics (a deciduous seed's bloom window expires;
Yuri is deciduous, Sep 14 is the bloom window).

## Proven instances

- `_ARTIFACTS/sixty/2026-07-23-kleban.60s.json` -> `yuri-60s-read.html` — the conformance
  test: 6/6 golden-reference card bodies match (spark is the additive fourth beat). The
  lambda's first true positive (card-1 DM quote tail) was resolved BIDIRECTIONALLY: seed
  corrected upstream here, golden republished with the strict DM verbatim by the parent
  session, both re-conformed 2026-08-29.
- `_ARTIFACTS/sixty/2026-07-22-elsamadisi.60s.json` -> `ahmed-60s-read.html` — first cold
  dogfood (internal only; ahmed-ext is the only shareable surface; nothing sends without Zach).
