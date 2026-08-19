# ADR-067 — Cross-subject comparative recoil: independently-derived beats corroborated across counterparts

**Status:** PROPOSED — number allocated by inference (highest confirmed file on main is ADR-066), NOT via `scripts/oracle.py next adr` (no local exec in this session). Per ADR-057, renumber on collision — do not treat 067 as final until run through the oracle.
**Date:** 2026-08-19
**Y-state:** YELLOW — pattern observed twice (Scott, Robin), not yet load-bearing across the corpus.

## D — The Decision
When an independent, from-scratch reverse-listening pass on one counterpart's transcript surfaces a beat
shape (e.g. monologue-density preceding a carrier-loss or Kairos moment) that also appears, independently
scored, in a *different* counterpart's already-published recoil, that convergence is itself a receipt-worthy
signal — not just corroboration of the individual read, but evidence the instrument is finding a real,
transferable pattern rather than overfitting to one relationship's idiosyncrasies.

Concretely, today: an independent fresh read of Robin Daniels' Aug 5 2026 call surfaced the same
monologue-density risk pattern (long, multi-metaphor monologues delivered inside a self-imposed time-box)
that caused carrier-loss with Scott Witt twice (Mar 5, Mar 20 2026). Robin's call hit its Kairos peak
*despite* the pattern; Scott's calls lost signal *because of* it — same mechanism, different outcome,
which is itself informative (the pattern is a risk factor, not a deterministic failure mode).

## E — Who's in the terrain
Zach Harris (operator/subject of the pattern). Scott Witt and Robin Daniels (counterparts, unaware their
reads are being cross-referenced against each other — this stays internal, never surfaced to either).

## W — The window
Surfaced today (2026-08-19) while building the Scott forge-tier surfaces and independently re-reading
Robin's Aug 5 call as a sanity check against the existing Claude-Code-built `robin-receipt.html`. The
window to formalize this is now, before a third counterpart's recoil is built without the cross-reference
step baked in.

## Y — Conviction
YELLOW. Two data points is a pattern candidate, not a validated instrument feature. Per the repo's own
rule-of-three convention (see ADR-066, prl-page-factory), this should NOT be built into tooling
(e.g. an automated cross-subject diff step in `forge_counterpart.py`) until a third independent
convergence is observed. Track it; do not automate it yet.

## Context
Until today, each counterpart's recoil (Robin, Yuri, Jeben/Louisville, Scott) was built and read in
isolation — the instrument never compared findings *across* subjects. The Scott build's carrier-loss
lock ("I don't want to be a thought leader," dense monologues) and Robin's independently-read
monologue-density risk are the first evidence that some beat shapes are properties of the *operator's*
pattern (Zach's own tendency to stack metaphors under time pressure), not just properties of the
counterpart's reaction.

## Options considered
- **A. Ignore the convergence, treat each counterpart's recoil as fully independent.** Simpler, but throws
  away a real signal about the operator's own behavior across relationships.
- **B. Formalize a cross-subject pattern-matching layer now, wire it into the forge pipeline.** Premature
  at n=2; violates rule-of-three.
- **C (chosen). Log the observation as an ADR, track it as a candidate pattern, revisit at the third
  independent convergence.** Cheap, honest about current evidence weight, doesn't over-build.

## Consequences
- Future counterpart recoils (any new `<name>-codex.html` build) should include a lightweight "cross-
  reference check" step: does this counterpart's beat shape rhyme with any other counterpart's published
  read? Not automated — a prompt for the operator to notice, per NOTOMATION.
- If a third convergence is found, revisit this ADR and consider whether `forge_counterpart.py` should gain
  an optional cross-subject diff mode.
- The specific finding (monologue-density as an operator-side risk factor, not counterpart-side) should
  inform Zach's own behavior going into future calls, independent of any tooling change.

## Linked receipts / ADRs
- ADR-057 — the sequence oracle (this ADR's own number is unverified against it)
- ADR-066 — Generative Recoil (rule-of-three gates generalization; applied here to NOT generalize yet)
- ADR-044 — temporal-provenance gate (the five-pager correction shipped alongside this ADR is a direct
  application: a claim was stated as "still outstanding" when it was actually "sent, unanswered")
