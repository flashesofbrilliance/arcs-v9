# Accumulation protocol (projection-map as an ADR-081 basin)

The first working instance of ADR-081 (Kairos Detector / Attractor-Basin Condenser), applied to Zach's
recorded calls. The ADR is the blueprint; this file is the run book. Propose-only: nothing here
becomes canon without Zach's ratification on the record.

## The frozen line

- **Discovery set:** every call recorded up to and including **2026-11-16** (114 scored calls).
  Patterns may be *found* here. Nothing found here can be *promoted* by this set again.
- **Test set:** every call recorded after 2026-11-16. Only these calls can move a candidate up.
- Re-running a test on the discovery set (another slice, another threshold) adds no evidence, however
  often it agrees. Three agreeing runs on one dataset are one observation.

## Basin states

| State | Entry rule | Exit up | Exit down |
|---|---|---|---|
| SPARK | Seen in data, not yet written as a test (an anecdote, an arc) | Written as a falsifiable test with a kill rule | Fails its first test: COMPOSTED |
| CANDIDATE | Pre-registered in `preregistration.md` with threshold and kill rule | p < 0.10 on its test | p >= 0.10: COMPOSTED |
| LEANING | p < 0.10 on the discovery set | Replicates on the test set (same direction, p < 0.10) | Misses on the test set twice: DECAYED |
| BOND | Replicated on the test set | A second independent stream agrees (ADR-081 rod 3) | Fails a later replication: back to LEANING |
| CANON | Two independent streams + Zach ratifies on the record | n/a | Superseded by a new receipt, never erased (Kintsugi) |

Independent streams for rod 3: (1) transcript counts, (2) outcome from calendar follow-up, (3) outcome
from email or a decision receipt, (4) Zach's own outcome marks, (5) a second coder (for example a
local model) whose agreement with a sample is measured first. Two labels from one stream are one stream.

## Run cadence

Every 20 new test-set calls, or monthly, whichever comes first:
1. Fetch only new calls (fetch-only helpers; `extract.py` verifies each against `total_chars`).
2. Score with the same scripts and thresholds. A changed threshold is a new CANDIDATE, not a retest.
3. Retest every LEANING and BOND row on the test set only. Update the ledger below.
4. Write new SPARKs as CANDIDATEs before looking at the test-set result for them.
5. Report state changes to Zach; propose, never promote to CANON yourself.

## Ledger (as of 2026-11-16, discovery set)

| Candidate | State | Evidence so far |
|---|---|---|
| Floor share rises with authority (recruiter 56% to client 71%) | BOND (descriptive) | Stable across 114 calls and 9 months; needs no outcome |
| Density alone does not reduce uptake | BOND (null) | 998 long turns, gap about 0, p 0.74 |
| More mid-curve in calls that died | LEANING | Within-room permutation p 0.052 (confirmed matches); one stream |
| More filler in calls that advanced | LEANING (against prediction) | p 0.083; one stream |
| Dense answers land better in interviews | LEANING | p 0.08 to 0.14 across runs on one dataset (counts as one observation) |
| Mid-curve follows their long turns (about 1.6x their usual) | BOND (descriptive) | Same in died and advanced calls |
| Listener cools before or after mid-curve | COMPOSTED | p 0.74 and 0.58 |
| First-call overshoot | COMPOSTED | Spark from two arcs; 4 of 9 counterparts, p 0.77. First known-fabrication kill for ADR-081 rod 4 |
| Naming a next step before hanging up changes outcomes | CANDIDATE (the Room Playbook experiment) | Test set only; detect from the last minutes of each transcript |
| "A later meeting means advanced" | SPARK (from the first full-loop demo, 2026-11-16) | The demo call was an impersonation from first contact (the Bitfury case). Its fast "advances" (same-day CV ask, quick next meeting) were the hook. Outcome labels need a trust check and a quality check from a second stream; an unverified counterpart's follow-up never counts as advanced |
| Trust tier gates the next-step move | CANDIDATE | In that call the named next step was the attacker's ask. Verify identity first (the precall brief's T2 gate), then name a next step |
| Recruiter room: go deep only on the deciding factor they name | CANDIDATE, weak | Same call, so the "recruiter" was not a real one. Kept only as a spark-grade lead until a verified recruiter call tests it |

| Register (Book of ARCS archetype) is a reliable second stream | BOND (reliability) | Two blind coders on different models: pilot kappa 0.75 (15 turns), scale-up kappa 0.69 (60 turns, 5 calls, rooms hidden, calls picked by rule) |
| Grug count matches perceived density | BOND (two streams agree) | Pilot kappa 0.67; scale-up 0.42 (Haiku) and 0.62 (Sonnet). Makes the density null credible |
| Counted uptake measures landing | CANDIDATE (reinstated, Kintsugi seam) | Pilot (15 turns) reversed and I composted it too early; scale-up (60 turns) agrees: judged-landed turns lift 0.99 to 1.0 vs 0.68 to 0.75. Coders agree on landing at kappa 0.60. Lesson: never retire a measure on a 15-turn pilot |
| Home registers: Sage, Shapeshifter, Heart; no register reliably loses | BOND (descriptive) | About three-quarters of 60 long turns; only 8 of 45 agreed turns judged not landing, spread across registers. Heart lands most with peers and recruiters, Shapeshifter with clients and interviews (cells of 5 to 20 turns) |
| High-stakes peer call: high floor share and mid-curve, polite decline | SPARK | One call (73% talk, 1.3 mid-curve per 10, a pilot declined twice). Consistent with the mid-curve leaning; one call is an anecdote |

Known gaps: one call deleted for card details; one call never fetched (mistyped id); outcome labels
from follow-up matching miss email follow-ups.
