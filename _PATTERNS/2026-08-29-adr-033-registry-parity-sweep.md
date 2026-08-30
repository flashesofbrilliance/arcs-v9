# ADR-033 registry parity sweep — post-Jul-19 instruments turned on the family itself

> **Status:** SWEEP RECEIPT — 2026-08-29. Zach's directive: "sweep using any/all newly invented
> skills since we last wrote to this ADR" (last write `1694a907`, 2026-07-19). Two arms:
> (1) every post-Jul-19 mechanical detector run live; (2) claims-skeptic agent over the ADR's
> own registry, described-vs-wired, file:line-cited. Companion:
> `_PATTERNS/2026-08-29-ventriloquy-pathogen-investigation.md`.

## Arm 1 — live detector readings (2026-08-29)

| Detector | Reading |
|---|---|
| `oracle.py audit adr` | clean — 68 numbers, next-free 74; gaps [21, 41–43, 47] = scar tissue |
| `lattice_drift_check` | **LIVE DRIFT** — lattice claims 63 ADRs vs repo 68; epoch 50d stale |
| `seedbank_drift_check` | OK (30 seeds / 61 receipts) |
| `branch_hygiene_check` | 13 worktree→branch smells; collision-critical invariant HOLDS |
| `canon_propagation_check` | OK (0 drifted pairs) |
| `artifact_wrap_lint` | clean on new; legacy grandfathered |
| `echo_detector_dogfood` | banked verdict stands: NOT seaworthy (adv-FP 1.0) |
| `gravity_well_fork_scan` | needs input artifact; not a corpus-sweep mode |

## Arm 2 — skeptic parity verdicts (registered members)

| Member | Verdict | Key evidence |
|---|---|---|
| Chronos-sequencer | **WIRED** | `receipt_lookup.py:81-86` skip + `RecoilReport.tsx:294` authority order |
| Inductive-overfit | **WIRED** | validityBounds + regime ladder live in code and ledgers |
| Open-loop decay | **WIRED, Loki condition FAILING** | mechanism runs (82 open obligations / 48 reports) but **0 explicit closures ever recorded**; revisit trigger (100-mark) approaching |
| Epistemic-sequencer | **EXISTS-BUT-UNWIRED** | no `"warrant"` field anywhere in `runtime/recoil/generated/*.json`, 41 days after "future: warrant field" was written |
| Etymology-sequencer | **PARTIALLY WIRED POST-HOC** | glossary exists; no rename-tombstone mechanism; `canon_propagation_check.py` + pre-commit oracle guard mechanized the escalation discipline but are unnamed in the ADR |

## Arm 2 — inverse sweep (post-Jul-19 detectors vs the registry)

| Detector | Family status | Coordinate |
|---|---|---|
| oracle numbering | **UNREGISTERED — PASSES ALL FOUR ADMISSION CRITERIA** (distinct coordinate, distinct mechanism, in-repo receipts 033/067, wired enforcement = pre-commit hook) | dictionary |
| lattice / seedbank / canon-propagation | registered classes, but **enforcement column doesn't name them** | time |
| echo false-positive | UNREGISTERED-CANDIDATE | warrant |
| ventriloquy | UNREGISTERED-CANDIDATE — would be a **sixth tuple coordinate** (speaker); no-detector claim **VERIFIED** (exhaustive grep: nothing mechanically checks who said a quoted line) | speaker |
| branch-hygiene | weak fit; admission gate would likely demote to a note | (scope, marginal) |
| wrap-lint, gravity-well | **correctly outside the axiom** — not every detector joins the family | — |

## Stale claims found in the ADR itself

1. **HIGH — line 26 is FALSE:** "the lingering ADR-032 duplicate remains the standing example"
   — resolved by forensic remap `08330a84` (032→049); only one ADR-032 exists today. And the
   ADR later became a collision victim itself (033 dup → ADR-073, resolved `380b8e70`) with no
   self-note — the family's registry doc caught its own founding pathogen and doesn't say so.
2. "Future: warrant field" — still prose after 41 days; an open loop the sweep itself doesn't track.
3. Revisit trigger approaching: 82 open obligations, 0 closures — the Loki condition (obligations
   actually close) is currently failing.

## Proposed amendment package (Zach's ratification — nothing applied)

- **A1 (correctness, HIGH):** fix line 26; add the kintsugi self-note (033 was itself duplicated
  and resolved via CANON-COLLISION → ADR-073 — show the seam).
- **A2 (admission):** admit **oracle-numbering** (dictionary coordinate) — the one candidate the
  skeptic scores as passing every gate criterion already.
- **A3 (bookkeeping):** name the post-Jul-19 detectors in the enforcement columns of the rows
  they already police (lattice/seedbank → chronos; canon-propagation → etymology).
- **A4 (judgment):** admit **ventriloquy** as the sixth coordinate (speaker) — census + mechanism
  in the companion receipt; detector not yet built (queued for the sixty-second-read settle beat).
- **A5 (judgment):** admit **echo false-positive** under warrant, or fold into epistemic-sequencer.
- **A6 (discipline):** log the failing Loki condition on open-loop decay; decide whether the
  0-closures fact triggers the revisit clause early.

## Open

- [ ] Zach ratifies any/all of A1–A6; the ADR edit follows ratification (canon governance, no
  new oracle number needed for amendments to an existing ADR).
- [ ] Lattice drift `--regenerate` (countables only; judgment layer human-owned) — offered, unactioned.

## Interim ventriloquy retro-sweep (2026-08-29, n=2 counterparts — the family's first hit-rate datum)

Scrappy prototype (`scratchpad/retro-sweep/sweep.py`, superseded by the mint session's lambda):
quoted spans + named verbatim fields from 9 kleban SSOTs + elsamadisi SSOT, classified against
the Me:/Them: pools of the Jul 23 (Yuri) and Jul 22 (Ahmed) Granola transcripts.

**Headline: ZERO `ME`/`NEAR-ME` hits.** No counterpart-attributed span matches only Zach's turns —
the classic strain (Zach's call-words in the counterpart's mouth) is ABSENT from the shipped SSOT
layer for both counterparts. Ahmed fully clean (3/3 THEM). Yuri: 27/43 THEM or NEAR-THEM.

**16 UNSOURCED, triaged by hand:**
- ~12 false positives: URLs/CSS caught by the quote regex, authored headlines/copy in
  verbatim-named fields, one span self-labeled "illustrative only" (correct disclosure).
- 1 **cross-channel pointer, content verified true**: `kleban.json meta.provenance.load_bearing_quote`
  ("I have nothing to sell/ask…") is verbatim from the Jul 15 LinkedIn DM (verified against the
  pasted thread 2026-08-30), invisible to a call-transcript pool. Lesson for the lambda:
  UNSOURCED means "not in THIS source," never "fabricated" — per-counterpart pools must span ALL
  sources (transcripts + emails + pasted DMs) or the verdict itself commits the jog-vs-rewind error.
- 1 real adjacent-strain finding: `kleban-receipt.json reverse_listening.beats[3].quote` renders
  "I automated it with data science, no AI, in 2020" in a QUOTE field; transcript actual is "this
  was data using data science there's no AI in 2020" — **paraphrase-as-verbatim** (compressed,
  meaning-faithful, but quote-labeled). Plus one scene-summary line living in a quote field
  (beats[5]) — field-misuse, not misattribution.

**Refinement for the ADR row:** the recorded infections all lived in MEMORY, CONVERSATION, and
draft artifacts — the shipped SSOT layer largely held. The pathogen concentrates UPSTREAM of the
ledger (digest + authoring time), which confirms the enforcement placement: pre-send gauntlet +
settle beat (authoring), with the retro-sweep as census, not as the primary gate.
