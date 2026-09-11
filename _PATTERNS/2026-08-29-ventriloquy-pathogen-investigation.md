# Ventriloquy — attribution-drift contamination in the recoil pipeline

> **Status:** INVESTIGATION RECEIPT — drafted 2026-08-29 (Zach named the pathogen live:
> "this feels like a contamination pathogen for recoil we should investigate").
> Proposed member of the ADR-033 Serialization Pathogen Family. **NOT admitted** —
> admission requires Zach's ratification per the family's gate; this file is the case.

## The pathogen

**Ventriloquy:** language authored by one speaker migrates to another across
serialization hops. Dominant strain: Zach's own conceptual framing re-attributed to a
counterpart ("importing your language into the counterpart's mouth").

**Family-axiom fit (ADR-033, "one coordinate silently dropped at write"):** the
**speaker coordinate** is dropped at compression (digests store ideas + resonance,
strip attribution), then **reinferred at resynthesis** by plausibility. Stored
resonance reads as shared authorship, so warm counterparts are maximally plausible
false hosts. Infection likelihood correlates with counterpart warmth.

## Census (4 confirmed + 1 adjacent, as of 2026-08-29)

1. **Jeben/Spock fusion** (corrected 2026-08-23, memory
   `jeben-spock-line-attribution-corrected`): "disturbance in the force" = ZACH's
   Feb 13 annotation, fused onto Jeben's Apr 21 Spock/probability-chart line.
   Caught by corpus re-listen. **Substrate-independent: human recall did this** —
   compression + reinference is the mechanism, not any one synthesizer.
2. **Yuri 5-altitude framing** (2026-08-05, guardrail in
   `project_yuri_kleban_google`): the 5-altitude/lossiness/receipt framing is
   Zach's, nearly serialized as Yuri's. Caught at authoring.
3. **Yuri consent/data-ethics stance** (2026-08-09): fabricated stance attributed
   to Yuri across receipt/codex/profile. **Passed BOTH the impeccable detector and
   the register gauntlet** — caught only by counterpart-vantage premortem.
   Existing detectors check register/render, not provenance.
4. **Yuri bookmark/cold-start** (2026-08-29, this session): Zach's Aug 28 email
   language ("composable meeting… think bookmark… without needing to rebuffer")
   drifted into "Yuri's own stated vision" in conversation AND into the witness
   stub before Zach caught it live. Penetrates canon surfaces, not just
   counterpart pages. Corrected upstream (stub amended same session).
5. *(adjacent)* Ayesha SSOT `runtime/recoil/generated/2026-07-17-ayesha-khan-toronto.json`
   carries a `MISATTRIBUTED_FIT` riskFlag (LOW) — fit-misattribution flavor,
   already being flagged ad hoc without a class.

## Why recoil is the preferred host (the autoimmune payload)

- **Transcript asymmetry:** Zach does the conceptual framing; counterparts affirm
  briefly. Compression preserves the idea + the resonance, strips the tag.
- **Scoring contamination:** recoil grades ex-ante bets against "what they said."
  If their ledger side carries Zach's language, the loop scores Zach's echo —
  **the belief-updater becomes a mirror.** Structural sycophancy wearing the
  costume of falsifiability.
- **Echo-detector poisoning:** Zach's returning language counted as convergent
  orthogonal echo — RC-OPS-001's adversarial-FP weakness, self-inflicted from
  inside the corpus.
- **Counterpart-facing blast radius:** fabricated interiority shown to the one
  person who knows what they actually said.

## Existing immune responses (all prose/judgment — instances 2–4 happened anyway)

`fact-check-final-pass-vs-transcript` · `verify-flags-against-full-source` (ADR-061)
· `counterpart-vantage-premortem` · per-counterpart guardrail notes ·
`read-full-source-before-confident-opinions` (2026-08-30, jog-vs-rewind). None are
mechanism-first; ADR-033 requires a mechanism.

## Proposed mitigation (mechanism-first): the speaker-provenance lambda

Granola transcripts are already speaker-tagged (`Me:` / `Them:` / named). So the
check is mechanically scorable, same shape as `scripts/artifact_wrap_lint.py`:

- **Input:** an SSOT or counterpart artifact + its source transcript(s) (+ optionally
  Zach's sent emails/annotations for the distinctive-phrase scan).
- **Rule:** every quote or stance attributed to the counterpart must fuzzy-match a
  `Them:` turn. Match against a `Me:` turn → **CONTAMINATED**. No match anywhere →
  **UNSOURCED** (either paraphrase-label it or strike it).
- **Extension (strain 2):** n-grams distinctive to Zach's authored corpus appearing
  inside counterpart-attributed spans → flag for human review.
- **Wiring:** forge / recoil-ship pre-send gauntlet (blocking), the
  sixty-second-read settle beat (operator-lambda, envelope contract), and a
  retro-sweep mode over `runtime/recoil/generated/*.json`.
- **Bidirectional rule applies:** a CONTAMINATED finding is never just deleted —
  it emits an upstream correction against the SSOT/memory that carried it
  (this session's "upstream implications of ground truth" rule; every gate a
  detector, ADR-051/052).

## Proposed ADR-033 registry row (for Zach's ratification — not applied)

| Pathogen | Coordinate dropped | Decay mode | Receipts | Mitigation | Enforcement |
|---|---|---|---|---|---|
| Ventriloquy | **speaker/attribution** | provenance stripped at compression, reinferred at resynthesis biased toward warm hosts; scoring loop degrades to self-echo | Jeben/Spock 8-23 · Yuri framing 8-05 · Yuri consent-stance 8-09 (passed 2 detectors) · Yuri bookmark 8-29 (reached witness stub) · Ayesha `MISATTRIBUTED_FIT` | speaker-provenance lambda (Them-turn match; CONTAMINATED/UNSOURCED verdicts); quote-attribution requires source-read-this-session | pre-send gauntlet (blocking) + sixty-second-read settle beat + retro-sweep |

## Open

- [ ] Zach ratifies (or rejects) family admission; if ratified, the ADR-033 edit
  cites this receipt (canon edit through normal governance, oracle untouched —
  no new number needed for a registry row).
- [ ] Build the lambda (`scripts/attribution_provenance_lint.py` or an operator) —
  natural home: the running sixty-second-read mint session (task_ce99d3fd), whose
  settle beat already owns quote verification; or a follow-up chip.
- [ ] Retro-sweep `runtime/recoil/generated/*.json` against available transcripts;
  census update with hit-rate (the family's own hit-rate metric).
