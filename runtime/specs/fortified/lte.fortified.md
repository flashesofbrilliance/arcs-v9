---
spec_id: ARCS-LTE-SPEC (Lossless Translation Engine)
version: 2.0.0-fortified
original_path: /Users/zharris/Downloads/ARCS_Lossless_Translation_Engine_Spec.md
original_sha256_prefix: ceac766aa79e3071
original_file_date: 2026-04-05
original_lines: 964
fortified: 2026-11-12 by Claude Opus 5.5 from ledger runtime/specs/fortified/ledgers/lte.json
status: DRAFT for Zach's review
filing_status: OPEN QUESTION (see Corrected, row 1). Do not label this document "patent-pending".
disclosure_caution: this page adds no technical detail beyond the original and operators/arcs_lte.py, operators/arcs_hc.py.
---

# Lossless Translation Engine: fortified spec

## Cold read

- **Why this spec exists:** ARCS needs a stage that rewrites one message for a reader at a different level of abstraction without dropping the points that must survive.
- **What it is now:** a check of the April 2026 spec against the code in `operators/arcs_lte.py` and `operators/arcs_hc.py`, with every claim marked as holds, corrected, hypothesis, or gap.
- **Why now:** the pressure test (54 claims) found 13 false and 24 internally contradicted claims, including a wrong scoring formula, five different pass marks for one metric, and a "Patent-Pending" label with no filing on record.
- **How to use it:** before building, read Corrected and Gaps; during the build, treat every item under Hypotheses as untested and gate nothing on it; after the build, return here and promote a hypothesis only with the test named beside it.
- **How to read this page:** "holds" means checked today with the evidence shown; anything without evidence is under Hypotheses. Spec line numbers refer to the original file.

## Verdict

Nobody can build the spec as written. Its maths contradicts itself, its main gate has five thresholds, and it cites calibration that does not exist. A builder can still trust three things: the stage order (intake, altitude, codex lookup, style rewrite, recheck, channel state), the seven-archetype registry, and the intent of the invariant gate. All three exist in `operators/arcs_lte.py` as a stdlib-only prototype. The prototype is not wired into any route, never blocks a dropped invariant, and halts on ordinary business sentences before translating them. Build from the code plus this page, not from the original.

## What holds

| Statement | Evidence |
|---|---|
| The pipeline order exists in code: HC pre-scan, intake, altitude, codex, rewrite, recheck, channel state. | `operators/arcs_lte.py:3-4` docstring; `translate()` at `operators/arcs_lte.py:925-1010` calls the stages in that order. |
| The HC pre-scan fires before intake and gates on a sender score below 0.65. | `operators/arcs_hc.py:9-10`, `:42`; halt path at `operators/arcs_lte.py:935-970`. The original spec never defines this stage (see Corrected). |
| Altitude weights 0.45 / 0.40 / 0.15 summing to 1, scaled to 0-5 and rounded. | `operators/arcs_lte.py:450`. The original's own code sample (line 684-686) agrees; its prose formula does not. |
| Seven built-in archetypes, INSTITUTIONALIST through CAVEMAN. | `ARCHETYPE_REGISTRY` at `operators/arcs_lte.py:185`, entries through line 272. |
| The intent of the invariant gate: keep the signal at its source altitude rather than ship one that drops an invariant. | Original line 859-860 (Rule 1). Kept as a requirement; the code does not yet meet it (Corrected rows 6-8). |
| The Yellow Paper section cites resolve, to v1.2 only. | `_CANON/arcs-v9-additional/ARCS-YellowPaper-v1-2.md:453` is "2.1 Audience as Wavefunction". `_CANON/ARCS-YellowPaper.md` numbers sections differently. |
| The original's own "What I Don't Know" note is honest. | Original line 958: the IPS threshold is theoretical, coefficients need real data, kairos detection is approximate. This page moves that note to the top. |
| `list[complex]` in a Pydantic model needs Pydantic 2.9 or later. | https://pydantic.dev/articles/pydantic-v2-9-release. The repo code uses dataclasses with floats, so this only matters if the Pydantic schema is built. |

## Corrected

| # | Original (line) | Correction | Evidence |
|---|---|---|---|
| 1 | "Patent-Pending" (4) | Filing status is an open question in the repo's own filing chain. No application number or date is recorded. "Patent-pending" has legal weight: it says an application exists. If none exists, the label is a misstatement. Keeping, dropping or replacing it is Zach's call with counsel. **I disagree with the ledger's FALSE verdict:** the repo shows the status is unverified, not that no filing exists. | `_QUEUE/induced-backlog.jsonl:120` row `filing-prior-filings`, state READY, gate "Yes/no with number and date, or 'none'", never answered. `filing-file` (line 130) is HOLDING. `_STATE/earliest-public-disclosure-ledger-2026-10-15.md` question 6 asks the same thing. |
| 2 | "Every ARCS output that reaches a human is routed through the LTE" (15) | Intended, not wired. No route or app code imports it. | `grep -rn arcs_lte src/` returns one hit, a comment in `src/lib/claude-models.ts:20`. Only `operators/arcs_cis.py` imports the module. |
| 3 | "Altitude = ... + (1 - γ) · UI" (175) | Forced fix: the third weight is 0.15, not 0.85. With 0.85 the weights sum to 1.70 and scores saturate at the top level. | `operators/arcs_lte.py:450`; original line 684-686. |
| 4 | "weights empirically validated on ARCS corpus" (177) | Uncalibrated initial values. No dataset, fit or notebook exists. | Original line 958 says calibration data is missing; no labelled altitude set found under `tests/` or `operators/tests/`. |
| 5 | "IPS ≥ 0.95" (52, 860) | One metric has five pass marks: 0.95 (52, 860), 0.90 (55, 792, 833, 906), 0.85 (913), and a per-mode split (930). The 0% invariant-loss rows (287-294) imply 1.0. The single gate is undecided; see Gaps. | The lines cited. |
| 6 | "roll back last style transfer op and retry" (407) | The code does not roll back. It appends the missing invariants verbatim under "Key points preserved", then rescores. Because the rescore looks for those same words, the gate passes by construction. | `operators/arcs_lte.py:765-769`. Run today: a two-sentence input to L0 returned IPS 1.0 with the second sentence pasted in brackets. |
| 7 | IPS as set intersection of semantic invariants (790) | The code scores an invariant as kept when 40% of its words of three or more letters appear in the output. A paraphrase scores as lost; a polarity flip scores as kept. | `operators/arcs_lte.py:689-722`. Run today: invariant "the plan will fail" against output "the plan will succeed" scored IPS 1.0. |
| 8 | Test 5 expects a block with "INVARIANT_DROPPED" (921) | No such error, block path or typed invariant exists. The Test 5 input ("The deal has a 90-day expiry.") never reaches recheck: the HC gate halts it at a sender score of 0.38. | `grep INVARIANT_DROPPED operators/arcs_lte.py` returns 0 hits; `_extract_invariants_stub` at line 295 returns plain strings; run today without an LLM client. |
| 9 | Rule 6: negative valence is an invariant (874) | Not implemented. | `grep -n "valence\|sentiment" operators/arcs_lte.py` returns 0 hits; see row 7. |
| 10 | "Every output MUST carry a visible seam" (862) | The code returns an empty seam when IPS, resonance and sender score all pass. | `operators/arcs_lte.py:744`. |
| 11 | Every translation logs a receipt (67) | A receipt object is built in memory and never stored. It does not use the repo's `decision_receipt` form. | `TranslationReceipt` built in `run_recomp`; no database write or endpoint in the module. |
| 12 | Drift fires when the gradient exceeds 1.5 (623) | Can never fire. Abstraction scores lie in [0,1], so `np.gradient` cannot exceed 1.0. The 1.5 belongs to the 0-5 level scale. A correct threshold is undefined; the derivative detector is also not built. | Checked in Python today: max absolute gradient of a [0,1] signal is 1.0. `grep gradient operators/arcs_lte.py` returns 0 hits. |
| 13 | Rule 4: the channel state warm-starts the detector (869) | The detector uses channel state only to damp urgency. It never reads the stored altitude. | `operators/arcs_lte.py:446-447`, `:836`. |
| 14 | Compression table agrees with code (287-294) | It does not. The code adds cells (4,0), (5,1), (3,1), (2,0), (1,0), omits the lateral 2:1 row, and falls back to `abs(delta) * 1.5` for any cell not listed. | `MAX_COMPRESSION` at `operators/arcs_lte.py:58-70`; fallback at line 463. |
| 15 | L5 "None (expand only)" (188) | Contradicted by the L5 to L0 and L5 to L2 rows at 289-290 and by Tests 2 and 3. Limits belong to a (source, target) pair, not a level. | The lines cited. |
| 16 | Stage and module count (6, 76) | The spec says 7 stages and 4 modules and draws 6 boxes. The code reaches 7 only by adding the HC pre-scan, which the spec never defines. | Original lines 76-118; `operators/arcs_lte.py:3-4`. |
| 17 | Rule 3 geodesic routing (866) | No routing function exists. The rule also conflicts with the one-step L5 to L0 and L4 to L1 rows and with Test 3. | `grep route_geodesic operators/arcs_lte.py` returns 0 hits; original lines 289-290, 903-906. |
| 18 | "persuasion" mode (379, 930) | The code's mode list is inform, persuade, brief, instruct, receipt. Use those names. | `operators/arcs_lte.py:55`. |
| 19 | Archetype energy names (266, 274, 565) | Three spellings across JSON, table and code. Use the code's names until one enum is chosen. | `operators/arcs_lte.py:194-272`. |
| 20 | Rule 5: pending queue then delivery (872) | A queue that sends on a timing signal breaks the spec's own NOTOMATION constraint (line 66) and the repo's confirm-before-send rule. Delivery stays a human action; a queue may only hold. | Original lines 66, 855, 872. |
| 21 | `BANDWAGON_AMPLIFY` as a style op (349) | Conflicts with the spec's own statement that the propaganda taxonomy is for defence only (354) and with Rule 6. Remove it or keep it out of build scope until Zach decides (Gaps). | The lines cited. |
| 22 | Source "L0-L5" labels (180) | L0-L5 already names the compass stack in this repo. Audience altitude needs a different label. Bands in the table also do not match the rounding rule. | Root `CLAUDE.md` L0-L7 stack; `operators/arcs_lte.py:450-451`. |
| 23 | `operators/README.md:51` calls LTE "Long-term expectation" | Wrong name for this file. Fix belongs in a separate change (this task edits no other file). | `operators/README.md:51`. |

## Hypotheses, not facts

Each item is untested. None may gate a build or appear in copy as a result.

| Hypothesis | What would verify or kill it |
|---|---|
| "Altitude mismatch causes 80% of communication failures" (17). No primary source found; nothing measures altitude mismatch as a category. | A cited study that measures it, or drop the number. |
| The altitude score classifies text correctly 85% of the time (P3). | A labelled set of 100 or more signals with a per-level confusion table. None exists. |
| Resonance R ≥ 0.80 predicts a message landing. R is not computable from the spec: the message state is never defined, and the 0.60-0.80 band has no action. The code's R is word overlap minus forbidden-word hits. | Define the representation, then test R against recorded reader reactions. Until then call it an overlap score. |
| Phase delta δ < 0.15. Phase of a text is undefined; the code's value is a friction ratio times π. | A definition of phase for text, or drop δ as a gate. |
| Compression fidelity CF. The entropy of a "semantic payload" has no estimator. CF is undefined when the input is all invariants and negative for expansion. | An estimator plus a test. Until then CF is undefined. |
| Multi-step compression keeps more invariants than one step (M5). The metric tensor is never specified. | An A/B on a fixed sample set, stepwise against direct, scored by a non-keyword IPS. |
| Wave, diffusion, Boltzmann and projection maths (M1, M4, T3.3-T3.5). The original calls this "formalism-by-analogy" (958). The quantities are undefined, so none is computable. | Treat as metaphor. Any one becomes a requirement only when a concrete measurable proxy is written and tested. |
| The decelerator stops retry loops. It needs three points and the cap is three passes, so it can fire only on the last one. | Not needed: an iteration cap already stops the loop. |
| Round-trip IPS ≥ 0.90 (or 0.85). Never run; with keyword IPS a pass through L0 likely loses words by design. | Run the round trip on a fixed sample set and report the number before keeping either threshold. |
| Per-archetype forbidden words and value anchors (273-281). Author-written, no source. | Reaction data per archetype. |
| Latency targets, P50 under 500 ms (725-730). No benchmark; an LLM call alone may exceed it. | Measure the stdlib path and the LLM path separately. |
| Original self-grade and "Ready for implementation" (5, 956). Score stripped. | An outside review, not a self-assessment. |
| "Grounded in ... field transcripts" (952). No transcript is cited by id; the White Paper has no altitude content. | List the transcript ids, or drop the claim. |
| Seven ROM-LTE candidates (926-934). ROM is a seven-primitive constitutional set; promotion is earned through a gate. | Keep as candidate ADRs; promote one only with its passing test. |

Grounds: ledger runtime/specs/fortified/ledgers/lte.json (claims marked UNVERIFIABLE and UNSOURCED-SELF-GRADE); the code these hypotheses would test lives in operators/arcs_lte.py; no test file for it exists (`ls operators/tests | grep -i lte` returns nothing). Each row above is unconfirmed until that test exists.

## Gaps and open questions

Build gaps:

1. **No wiring.** Nothing in `src/` calls the LTE. Per the repo rule that a built asset must join the recurring run, wiring it needs its own backlog row, or the module stays a prototype.
2. **No tests.** No test file covers `operators/arcs_lte.py`. Tests 1-5 in the original have never run.
3. **HC gate over-fires.** With no LLM client, two plain sentences ("The deal has a 90-day expiry.", and a revenue-and-board-meeting pair) scored sender confidence 0.38 and 0.71; the first halted. The gate needs a sample set before it can block anything.
4. **IPS cannot fail.** The recovery pass makes the gate circular (Corrected row 6). Until IPS is scored without the pasted text, every IPS number from this module is meaningless.
5. **Hard versus soft invariants.** The spec wants 0% invariant loss and an IPS below 1.0 at once. It needs a split: hard invariants block at 1.0; soft ones count toward a score.
6. **Receipts.** In-memory only. Decide whether translations write to `decision_receipt` or to a separate ledger.
7. **Undeclared dependencies.** spaCy, FAISS or ChromaDB, FastAPI, NumPy and SciPy (line 507 on) are named; none is declared, and the repo rule is no new dependencies without asking.

Decisions only Zach can make:

1. **Filing label.** Answer `filing-prior-filings` (number and date, or none). With counsel, decide what this document and the White Paper may say about patent status.
2. **Disclosure.** Whether this spec and its fortified copy stay private until counsel advises (backlog `filing-public-surface-decision`).
3. **One IPS gate.** Which threshold, per mode, and whether it is 1.0 for hard invariants.
4. **Bandwagon op.** Remove it, or allow it only with real cited adoption data and a visible seam.
5. **Real people as audiences.** The original names real people as target audiences (lines 44, 848, 885). Keep named mappings in private files, use placeholders in specs.
6. **Altitude label.** Rename audience levels so they do not collide with the compass L0-L5 stack.
7. **Scope cut.** Whether the wave and signal-processing layer (T3, M1-M8) stays in scope at all, or is filed as background.

## Kintsugi seam

1. **It claimed evidence it did not have.** "Empirically validated" weights, "Ready for Claude Code Implementation", a 94/100 self-grade, and "Patent-Pending" all read as settled facts. None had a record behind it. The honest note at line 958 contradicted all of them and sat at the bottom.
2. **It dressed heuristics as physics.** Wavefunctions, phase, entropy and geodesics give the look of measurement. None of those quantities is defined for text, and the code replaced each one with word counting under the same name. Readers could not tell which numbers were computed and which were decoration.
3. **The gate it called non-negotiable was never a gate.** The spec says an invariant drop blocks output. The code pastes the dropped words back in and passes itself, and no route runs the code. The break was invisible because the receipt reported IPS 1.0.
