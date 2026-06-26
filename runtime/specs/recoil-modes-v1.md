# Recoil Protocol — Reverse Listening & Deep Recall modes (v0.1.0)

**Status:** DRAFT — defined this session, not yet canon-ratified. Routed for review,
not unilaterally declared final (per the standing canon-collision discipline).

## Why this exists

The Recoil Report (`runtime/recoil/*.md`, `src/document/screens/RecoilReport.tsx`) already
has a shape: D/E/W signal-delta/Y-gate-shift/confidence/next-steps. What it didn't have was
a defined **pass structure** for how the transcript itself gets read before that shape gets
filled in. Two passes, run every time, in this order:

## Pass 1 — Reverse Listening

Read the transcript **end-to-start**. The point: outcomes (how the call actually landed,
what the other party's closing tone/ask was) are known before cause is examined, which
blocks the common recoil failure mode of rationalizing a weak moment because "it worked out
anyway." Reverse listening extracts:

- The actual close (what was said last, what was asked/committed)
- Working backward, every moment that either supports or contradicts that close
- Flags moments where the conversation's stated trajectory (what it seemed to be building
  toward, heard forward) diverges from where it actually landed (heard backward)

## Pass 2 — Deep Recall

Read the transcript **start-to-end**, normally, but scored against the pre-call expectation
captured in the originating PrepSession/calendar context (the ex-ante receipt) rather than
read cold. Deep recall extracts:

- Signal delta per moment (expected vs. actual, the existing Recoil Report table)
- The single highest-leverage recoil moment (the existing "load-bearing quote" pattern)
- Behavioral pattern repetition (e.g. the existing "verbosity flag, twice" finding)

## Scoring cadence — 1/(call duration)

Both passes sample at a rate of **1 finding-check per (1 / duration_minutes) of transcript**,
i.e. the granularity is the reciprocal of the call length: a 10-minute call gets checked at
a coarser grain (fewer, larger segments) than a 60-minute call would at the same total
finding budget — short calls get fewer, higher-signal segments; long calls get more,
finer-grained ones, but the total review effort stays roughly call-length-invariant rather
than scaling linearly with duration. Concretely: `segment_count = round(duration_minutes / (1 / duration_minutes))`
is the wrong reading of "1/(duration)" if taken as a literal rate — the operative rule
adopted here is simpler and avoids that algebra trap: **segment the transcript into
`max(3, round(sqrt(duration_minutes)))` chunks**, each independently run through both
passes. This is the working definition; flagged for Zach to correct if "1/(duration)" meant
something more literal that this paraphrase missed.

## Output contract

Each pass produces a list of `{ timestamp_pct, finding, pass: 'reverse'|'deep', signal: 'supports'|'contradicts'|'neutral' }`
records. These feed directly into the existing Recoil Report sections:
- Reverse Listening's divergence flags → "Signal Delta Table"
- Deep Recall's load-bearing quote → "Signal Quote" (Sec 01)
- Both passes' chronological findings, merged and time-sorted → "Call Walk" Timeline (Sec 02)
