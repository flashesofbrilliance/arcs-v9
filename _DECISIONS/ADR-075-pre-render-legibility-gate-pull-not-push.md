# ADR-075 — Pre-render legibility gate: every counterpart surface opens verdict-first, depth is pulled, and a cold-reader eval can stop it

> **Status:** DRAFT · **Number reserved** via `oracle.py audit adr` (next-free 75); MINT AT COMMIT
> (pre-commit hook enforces). **Date:** 2026-09-03. **Scope:** all counterpart-facing surfaces
> (recoil / codex / receipt / prep / atlas / NFTT), the forge, the PREP renderer, counterpart-gauntlet.
> **Y-state:** GREEN on the mechanism (three independent counterparts, verbatim); YELLOW on the
> gate thresholds (calibrated on a three-page set, not yet on a corpus).

---

## D — The Decision

**Sharp question:** Should legibility for a cold reader be a wired, blocking gate on every rendered
counterpart surface, with a fixed verdict-first grammar and a mechanical plus judgment eval, rather
than a per-counterpart memory?

**Decision: yes.** A counterpart surface ships only if it passes `scripts/cold_reader_gate.py`
(mechanical) and the cold-reader facet of `counterpart-gauntlet` (judgment). The grammar is fixed:
verdict (one line) → three reasons to care → three questions with short answers → tasks → evidence
behind a disclosure, one figure per opened step → full record linked last. Depth belongs to the
reader. Consume-time must be a small fraction of build-time and is stamped on the page.

---

## E — Entity / System

The forge (`scripts/forge_counterpart.py`), the PREP data object and renderer (saul.arcs.care
pattern), `scripts/atlas_render.py`, the NFTT story engine, `counterpart-gauntlet`, the
pre-publish gate chain (`leak_check.sh`, em-dash check, `artifact_wrap_lint.py`). Every counterpart
who receives a page. The author, whose blindspot the gate exists to compensate.

---

## W — Window

**Horizon:** YEARS (a constitutional rendering rule). **Revisit trigger:** the acceptance test fails
(a counterpart who preferred the verdict-first version cannot act on it in two minutes), or the
corpus test (`_STATE/2026-09-03-gone-in-30s-report.md`) returns H0 once the throttled transcripts are
re-read, or the gate begins failing pages that counterparts demonstrably consumed with ease (over-fit).

---

## Context

Three counterparts, three surfaces, one verdict, in their own words:

- Jeben, 2026-04-21, about Harry Wilson: "you are not a person that walks around ready to receive this
  type of information, even though I think it's pretty critical for you." And: "give him the mirror."
- Robin, 2026-08: listen carefully and give them what they asked to see.
- Ahmed, 2026-07-28: "hard to follow." 2026-09-02: "still so lost in your offering and the page."
  2026-09-03: "your delivery mechanisms are just not great ... nobody wants depth front. You want
  depth once you know how to scan it because you built it." He ran a live A/B: a ChatGPT
  verdict-first brief against saul.arcs.care, and preferred the former even though ours contained
  every element he praised. He could not find them.

The rule was already known. Five Fathoms (April) encoded depth-controlled-by-the-subject. Zach's own
line that day, filed YELLOW: "how deep can you go in 30 seconds?" The Ahmed pages were then built
push-first three times. Root cause (witnessed 2026-09-03, GREEN): the lesson was banked as an instance
under each counterpart's name and never as a class with a gate. A who-only index cannot return "you
have seen this twice." Prose cannot stop a page; a gate can (memory: lesson-banked-when-it-can-stop-you).

Pre-registered corpus test in flight: `_STATE/2026-09-03-gone-in-30s-preregistration.md`. Interim
(35 of 125 transcripts read): rate 0.33, inconclusive; hits cluster on "I need a demo / an example"
(show-don't-tell) rather than "too dense"; three counterparts pulled toward depth. This ADR therefore
gates the ORDER and the DISCLOSURE, not the total depth available.

---

## Options Considered

### Option A — Keep it as memory + design principle (status quo)
- Already tried three times (met-at-your-level, design-for-arriving-cognitive-state, adaptive-altitude).
- Pro: zero build. Con: failed in the field three times; prose cannot block a render.

### Option B — Per-counterpart tuning (an "Ahmed eval")
- Pro: high fit for one reader. Con: repeats the instance-not-class failure; over-fits to one taste.

### Option C — A class-level gate: fixed grammar + mechanical tripwire + judgment facet (CHOSEN)
- Pro: stops a page before a counterpart sees it; calibration set grows by one page per counterpart
  verdict, so it tracks the class. Con: thresholds are a first guess; over-fit risk managed by the
  revisit trigger and the calibration contract.

---

## Decision detail

1. **Grammar (fixed order).** Verdict · 3 reasons · 3 questions + answers · tasks · evidence in
   `<details>` (one table / number / plot per step, takeaway → evidence → takeaway) · full record linked.
2. **Mechanical gate** `scripts/cold_reader_gate.py`: R1 verdict above fold · R2 first screen ≤ 250
   words · R3 depth behind disclosure, ≤ 1 figure before it · R4 one figure per step · R5 read-time
   stamp · R6 zero em-dashes · R7 an action cue above the fold. Exit non-zero blocks publish.
3. **Judgment gate**: cold-reader facet in `counterpart-gauntlet`; from the first screen ONLY it must
   answer what is this / why should I care / what do I do next. Any "not sure" fails.
4. **Calibration contract**: ahmed-ext FAILS, saul (current) FAILS, the verdict-first re-render
   PASSES. If the gate disagrees with a counterpart's stated verdict, the gate is wrong.
5. **Index change**: feedback memories and recoil-close receipts carry mechanism tags from one shared
   folksonomy; `gravity_well_fork_scan.py` runs over them with distinct-counterparts as the spread axis.
   Two subjects on one tag = digest line; three = fork recommendation, default no.
6. **Build-vs-consume**: read time stamped on every artifact; if read time exceeds one tenth of
   build time, it does not ship without an explicit override noted in the receipt.

---

## Consequences

- The forge and PREP renderer emit the grammar; authors do not choose the order.
- saul.arcs.care is re-rendered first; Ahmed's read of it is the acceptance test (falsifier: he
  cannot say what it is and what to do inside two minutes).
- The Ahmed pre-call bundle built 2026-09-03 (start / one-table / loop / atlas) is re-rendered through
  the gate before any of it is sent.
- Memories merged: design-for-arriving-cognitive-state, adaptive-altitude-lineage,
  feedback_takeaway_first_delivery_grammar → `pull-not-push-pre-render-legibility-gate` (class).

## Amendment A (2026-09-03, same day): one gate doctrine, two ends

The render gate catches a wall on the way out. It cannot catch building the wrong thing well: wrong
reader, wrong Receipt Loop stage, the reader in the subject slot, their stated format ignored, their
explicit asks unanswered. Every one of those was decided before the first line of the Ahmed pages was
written, and every one was answerable from the raw inputs. So the doctrine has two ends:

- **Input end, `scripts/pre_prep_gate.py`** (P0 to P7): a `pre_prep` block in the account SSOT, filed
  before the build, from raw sources on disk. Checks: filed-before · verbatim transcript/thread on disk
  · asks enumerated verbatim · reader + stage declared · subject slot consistent (about = for, or the
  reader asked) · format spec in their words or explicit none · arriving state with quote · read budget
  ≤ build/10. Wired as Step 1.5 of /recoil-prep, blocking. The block is the ex-ante receipt for the
  artifact; /recoil-close scores it.
- **Output end, `scripts/cold_reader_gate.py`** (R1 to R7): unchanged. Wired into /recoil-ship.

Retroactive contract: the Ahmed SSOT as of 2026-09-03 FAILS the input gate (no block). A block filled
honestly from the July 22 transcript would have failed P4 (about the reader, reader did not ask) and
flagged asks 7 and 9 as unanswered. Zach, 2026-09-03: "sure one gate doctrine two ends it is."

## Amendment B (2026-09-03, evening): instance-first, and the rubric made literal

Corpus read (50 of 125 calls): "show me an example" cues outnumbered "too dense" cues 9 to 3, and four
counterparts asked for more. So R1 now requires a verdict cue AND an instance from the reader's world (a
quotation, or a figure with a unit) above the fold. Depth is unchanged; order and anchor are what the gate
governs. Ahmed's feedback is now a literal 13-item rubric, cross-referenced to published standards (Minto,
BLUF, NN/g, Knaflic, Few, Tufte, Duarte, Butterick, WCAG, Krug) with two items the standards add (action
titles, contrast): `_SPECS/cold-reader-rubric-v1.md` + `_SPECS/cold-reader-rubric-sources.md`. Live Saul
scorecard: passes craft (A9, A11, A12), fails order and disclosure (A1 to A8, A10, A13).

## Lineage

witness 2026-09-03T14:29:34-04:00 (GREEN) → this ADR (oracle next-free 75) → DEWY
`_STATE/2026-09-03-legibility-gate.dewy.json` → apex `_CANON/apex-spine-pull-not-push-legibility-gate.md`
→ atlas nodes in `_ARTIFACTS/atlas/digest-ahmed.json` → memory `pull-not-push-pre-render-legibility-gate`.
Supersedes nothing; sharpens WORLD.md "The Render Scale" (earned fidelity) with an order rule.
