# Pre-registration: does the "gone in 30 seconds" mechanism hold across all calls?

Filed 2026-09-03, before any transcript beyond Ahmed (Jul 22, Sep 3) and the Jeben Apr 21 file was read for this purpose.

## Hypothesis (H1)
Counterparts, regardless of agenda, independently name the same mechanism: information offered to them
must open with the verdict and let them pull depth, or it is lost; receptivity is a state they walk in
with, not a trait. Prediction: the mechanism appears, in the counterpart's own words, in at least half
of calls where Zach presented an artifact or explained ARCS. Null (H0): it appears in fewer than a
quarter, or only when Zach prompts for feedback on format.

## What counts as a HIT (counterpart utterance, verbatim, any of):
- C1 **Legibility complaint**: says the material was hard to follow, too much, dense, lost, confusing, or asks how to consume/read it.
- C2 **Verdict-first demand**: asks for the short version, the TL;DR, the headline, the one thing, "what do I do with this", or the 30-second version.
- C3 **Depth-on-pull**: says they want detail later, behind a click, once interested, or "tell me the answer first".
- C4 **Receptivity-as-state**: says they or someone else was not ready to receive it, wrong time, too busy, need to be pulled not pushed.
- C5 **Mirror preference**: responds strongly to seeing their own words or situation reflected back, versus to the system's framing.

## What counts as a MISS:
- M1 Counterpart consumed a dense artifact and engaged with its depth unprompted.
- M2 Counterpart asked for MORE detail up front.
- M3 No artifact or explanation was presented; call is out of scope (recorded as N/A, not a miss).

## What does NOT count:
- Zach saying any of the above about himself or about the material (Zach-side lines are logged separately as Z-side, not as hits).
- Paraphrase. Only quoted transcript lines count. Speaker must be the counterpart ("Them" or a named non-Zach speaker).
- Politeness ("that makes sense", "cool") without a legibility or format content.

## Scoring
Per call: list of hits with tag + verbatim line + approximate position; list of misses; N/A flag.
Corpus: hit-calls / in-scope-calls. H1 supported at >= 0.50; H0 at < 0.25; between is inconclusive.
Secondary: which tags dominate; whether hits appear unprompted (before Zach asks about format) or prompted.

## Method
1. Enumerate all Granola meetings (all time). 2. Mechanical pass: pull each raw transcript, regex tripwires
(hard to follow|too much|lost|TL;DR|short version|30 second|headline|how (do I|to) (read|consume)|what do I do with|
not ready|right time|later|click|depth|detail|dense|simple|simpler). 3. Judgment residue: for each call with
tripwire hits or with an artifact presented, a reader applies C1 to C5 / M1 to M3 to the surrounding lines.
4. Aggregate mechanically; report with every hit line verbatim.
