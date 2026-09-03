# Cold-Reader Rubric v1 (ADR-075 grammar, scored)

> Source of truth for the rubric: Ahmed Elsamadisi, 2026-09-03, raw Granola transcript `363c13a2`. Each item
> below is his line, taken literally, turned into a scorable check. Cross-references to published standards
> are in `cold-reader-rubric-sources.md` (delegated research, cited). Mechanical checks live in
> `scripts/cold_reader_gate.py`; judgment checks live in the counterpart-gauntlet cold-reader facet.

## A. The literal rubric (his words → the check)

| # | His line (verbatim) | The check | How scored |
|---|---|---|---|
| A1 | "here is my goal. Here are the things that I missed. And then here's how I fix it. Then supporting evidence" | Section order is goal → gaps → fixes → evidence. Nothing else precedes evidence. | mechanical (heading order) |
| A2 | "if you had to narrow it down to 3 reasons why I should care" | Exactly three reasons, each one line, before any detail. | mechanical (count) |
| A3 | "what are the first 3 questions I'm gonna have and what are those first 3 simple answers" | Three Q/A pairs; each answer ≤ 40 words. | mechanical (count, words) |
| A4 | "takeaway up front, supporting evidence, takeaway" | Every evidence block opens and closes with a one-line takeaway. | judgment (facet) |
| A5 | "maximum one plot, one big number" | ≤ 1 figure (table/chart/big number) per open block. | mechanical (DOM count) |
| A6 | "nobody wants depth front. You want depth once you know how to scan it" | Depth is behind a disclosure; first screen ≤ 250 words. | mechanical |
| A7 | "a little eye and I can click on it" | Every deep block has a visible affordance to open it. | mechanical (`<details>`/toggle present) |
| A8 | "if it takes the system a day to create it, it should take me an hour to consume it" | Read time stamped; read ≤ build/10. | mechanical (stamp + budget) |
| A9 | "you have to get my interest piqued so that I can go into the depth" | First screen contains one line in the reader's own world (quote or number about them). | mechanical (quote/figure above fold) |
| A10 | "what am I trying to do ... before my call, this is the things I need to know" | An imperative task list above the fold. | mechanical (action cue) |
| A11 | "it could be more like a deck versus like a long PDF ... intense amount of text, and it's also hard to read" | One idea per screen; measure 45 to 75 characters; body ≥ 16px; line-height ≥ 1.45; ≥ 3 distinguishable type levels. | mechanical (CSS) |
| A12 | "a VC doesn't care about your innovation before they care about the problem" | The reader's problem is named before any ARCS mechanism or vocabulary appears. | judgment (facet) |
| A13 | "I looked at yours and I skimmed through it ... multiple times and I have no idea what I'm trying to do" | Cold-reader facet answers what / why / do from the first screen only. | judgment (facet) |

## B. What Ahmed did NOT say (do not over-fit)
- He did not ask for less total depth. He paid for Co-Star's full report. Depth stays; order and disclosure change.
- He did not ask for fewer numbers. He asked for one per step, framed by a takeaway.
- Corpus check (50 of 125 calls, 2026-09-03): "show me an example" (9) outnumbers "too dense" cues (3). A9 is the load-bearing item.

## C. Cross-reference to standards (from `cold-reader-rubric-sources.md`, cited there)

| Rubric item | Standard that corroborates it | Numeric or structural rule it adds |
|---|---|---|
| A1, A12 | Minto Pyramid / SCQA · BLUF (military writing) · NN/g inverted pyramid · Sequoia deck order | answer first; problem before solution in document order |
| A2, A3 | Gestalt grouping · Minto "rule of three" at the summary layer | exactly 3 top-level items before any drill-down |
| A4 | McKinsey action titles · Knaflic "takeaway title" | every heading states the so-what, never a label |
| A5 | Knaflic (declutter) · Few (dashboard at a glance) · Tufte data-ink | one primary chart, one number; no chartjunk |
| A6, A7 | NN/g progressive disclosure · Krug "don't make me think" | depth opt-in via visible affordance, never inline |
| A8 | Bezos 6-pager (read time is designed) · counterpart's own rule | read ≤ build/10, stamped |
| A9 | Duarte (audience is the hero) · Co-Star headline→lede→math | the reader's own row above the fold |
| A11 | Butterick measure 45 to 90 ch · WCAG 1.4.8 (80 ch AAA) · WCAG 1.4.12 text spacing (lh ≥ 1.5) | measure and spacing floors |
| A13 | Bierut / Krug five-second test | reader states verdict + one reason unprompted |
| **A14 (added)** | McKinsey action titles | headings are sentences with a verb, not nouns |
| **A15 (added)** | WCAG 1.4.3 | text contrast ≥ 4.5:1 body, ≥ 3:1 large |

Where the standards disagree, and how this rubric resolves it:
- **Tufte's density vs Knaflic/Few's restraint.** Resolved by altitude: one figure per open block (Knaflic) at the
  fold; Tufte's small multiples permitted inside a disclosure. Density is allowed, never first.
- **Amazon 6-pager (slow prose by design) vs "nobody wants depth front."** Resolved by audience: the 6-pager is
  for a room that has committed an hour. A cold counterpart has committed thirty seconds. Full prose becomes the
  linked record (section 6 of the grammar), never the landing view.
- **Answer-first (Minto/BLUF) vs Duarte's earned arc.** Resolved by stage: verdict first for the cold reader;
  the arc is for the NFTT story class, where the reader has already opted in.

## D. Scorecards (2026-09-03)

### saul.arcs.care, live (main head d94919c7, the version Ahmed saw)
Isolated design review (impeccable Assessment A, Read mode) + detector (Assessment B) + cold_reader_gate on the rendered text.

| Item | Result | Evidence |
|---|---|---|
| A1 order goal→gaps→fix→evidence | FAIL | 7 equal-weight sections; nav lists them without priority |
| A2 three reasons | FAIL | none; thesis paragraph stands in for it |
| A3 three Q/A | FAIL | "Ask" has 5 questions, at the bottom |
| A4 takeaway→evidence→takeaway | PARTIAL | headline + thesis is a real takeaway; only "walk in with" closes |
| A5 one figure per block | FAIL | fit map 10 rows, 6 battle cards, 16 guardrail bullets, all open |
| A6 depth behind disclosure, ≤250 words first screen | FAIL / PASS | zero `<details>`; first screen ~99 to 150 words |
| A7 click-to-open affordance | FAIL | nav anchors jump, they do not disclose |
| A8 read ≤ build/10 | FAIL | self-stamped "READ: 7 MIN" |
| A9 reader's own world above fold | PASS | "You have run the delivery machine" is Saul's row |
| A10 tasks above fold | FAIL | tasks distributed across guardrails, bridges, ask |
| A11 typographic floor | PASS | measure 65 to 75 ch, lh 1.5, 4 to 5 levels; detector: side-tab border, Instrument Serif |
| A12 problem before mechanism | PASS | no ARCS vocabulary on the page |
| A13 what/why/do from first screen | FAIL | "what do I do" lives nowhere prominent |

Heuristics (0 to 4): control 1 · recognition 1 · efficiency 1 · minimalism 1 · match 3 · consistency 3.
Cognitive load: 3 decision points with more than 4 options; 7 of 7 sections open; ~2,400 words.
Reviewer's line: "the typography craft is not the problem; the editorial cut is."

### ahmed-ext.arcs.care (live)
cold_reader_gate: FAIL on A6/R3 (4 figures open before any disclosure) and A10/R7 (no action above fold). Counterpart verdict: "lost," twice.

### Show Me, Don't Tell Me (artifact, built in this grammar)
cold_reader_gate: PASS after one fix (action cue added to the verdict box). 201 words first screen, 4 disclosures, 1 figure each.

## E. What the scorecards say together
Saul passes everything about craft (A9, A11, A12) and fails everything about order and disclosure (A1 to A8, A10, A13).
That is the whole finding: the content and the typography are not the problem. The cut is. The fix is the
ADR-075 grammar applied to the existing content, not a rewrite.
