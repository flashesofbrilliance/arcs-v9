# Preregistration: gate reference set (committed BEFORE any gate or probe code, A1 of the loop 3 amendment)
Written 2026-10-17. Nothing below may be changed after gate code exists except by appending a dated "AMENDMENT" block.

## Definitions
- Verdict: VERIFIED or NOT_VERIFIED. Positive class = cases a gate must WITHHOLD "verified" for (receipt unresolved, stale, self-cited, or evidence_supports=false). Negative class = cases whose expected_verdict is VERIFIED ("true cases").
- recall(G) = positives withheld by G / positives. false_withhold(G) = true cases withheld by G.
## Reference gates (exact, deterministic; implemented in runtime/specs/farcaster-gate/gates.py)
- G0: VERIFIED iff receipt_resolves.
- G1: G0 AND keyword overlap AND freshness. Keyword tokens: lowercase, split on non-alphanumerics, keep length>=4, drop the stopword list in gates.py, no stemming. Overlap = at least 2 distinct tokens shared between claim and receipt_excerpt. Freshness = 0 <= (claim_date - receipt_date) <= 30 days.
- G2: G1 AND NOT self-citation. Self-citation = first whitespace-delimited token of receipt_author (lowercased) equals claim_author (lowercased).
## Sets
- Dev set: runtime/specs/farcaster-gate-falsifier-set.json (T1-T5, F1-F5, L8-L10 plus real cases R1-R4 from A2).
- Sealed hold-out H1-H4: agent-authored, written without sight of dev cases or gate code; sha256 recorded below; opened only after G2 exists.
## Pass lines (all pre-registered)
1. Dev set: G2 withholds every positive case AND wrongly withholds 0 true cases.
2. G0 misses at least 3 of the 4 false-with-receipt cases F2-F5.
3. recall(G0) < recall(G1) <= recall(G2), strictly at the first inequality.
4. Hold-out: G2 recall >= 3 of 4, else the result is reported as "set overfit".
5. Each probe's offline self-test classifies 4 of 4 broken fixtures correctly and the good fixture as "proven".
6. Secret canary FC_TEST_CANARY_0xDEADBEEF appears 0 times in any probe stdout, stderr, JSON or log.
7. quickstart: no FC_BUDGET_ALERT_ID -> create refuses; with it -> prints plan; teardown --verify --dry-run prints the tag filter.
If the set cannot separate G0 from G1 it is too easy: add cases through the hold-out process only, never by tuning to pass. Failures of a pass line are reported as failures, not repaired in place.
## Hold-out hash
HOLDOUT_SHA256: 6de0b429dda15d3d6a759ad7c7617b9e27a3e3e7a60385f8fb045658656b9232  (file: runtime/specs/farcaster-gate/sealed/holdout.json, agent-authored, unopened by the author as of this commit; committed before gates.py exists)

## AMENDMENT 2026-10-17 (after gate code; recorded, not retroactive)
1. Line 1 FAILED and stays recorded as failed (dev set: G2 misses F5, L9, L10, R2; wrongly withholds T1, T2, T3, T5, R1, R3). Finding: deterministic resolve/overlap/freshness/self-citation gates cannot judge scope or outcome. Consequence adopted by Zach ("good with your approach"): v1 gate wording is "checks resolution, freshness and authorship"; the word "verified" is not used for scope-level claims. No gate or case was tuned to pass.
2. Line 4 was implemented as "G2 verdict correct on >= 3 of 4 hold-out cases" because the hold-out has 3 positives and 1 true case, so positive-recall >= 3 of 4 was unsatisfiable by construction. Result under this reading: 4/4. The hold-out file remains tracked plaintext, so "sealed" means hash-committed only, not unread-by-anyone.
3. Reviewer fixes applied after the claims-skeptic pass (findings 7, 8, 13, 14 and the R4/_doc metadata in 4, 10): canary positive control + exit checks + mktemp; write probe now looks for the cast hash in /v1/events before setting merge_event; bare teardown requires FC_CONFIRM_TEARDOWN=yes; FC_DENY_FIDS trimmed; bootstrap pinned to snapchain fc87f268 (== v0.14.3).

## AMENDMENT 2 2026-10-17 (parent corrections C1, C2, C4; supersedes the wording of AMENDMENT 1 where they differ)
- C1. Pass line 4 as written ("G2 hold-out recall >= 3 of 4") was UNSATISFIABLE BY CONSTRUCTION: it was fixed before the hold-out's composition (3 positives, 1 true case) was known. That is a defect in the preregistration, not in the gate. The later reading "G2 verdict correct on >= 3 of 4" (result 4 of 4) was made AFTER the gate and the hold-out existed, so it is a POST HOC reading and is NOT counted as passing the pre-registered line. Line 4 stands as: not met (unsatisfiable). The hold-out result is not called a pass anywhere.
- C2. Contrast: G2 gets 4 of 4 on hold-out 1 but fails line 1 on the dev set (misses F5, L9, L10, R2; wrongly withholds T1, T2, T3, T5, R1, R3). Likely cause: hold-out 1 lacks scope-mismatch and outcome-mismatch cases. A second hold-out H5 to H8 was written blind by an agent (general-purpose with the chief-loki persona) specifically for scope and outcome mismatch. Its sha256 is committed here BEFORE any gate was run on it, and results will be reported as a second, separately labelled hold-out (hold-out 2).
HOLDOUT2_SHA256: 20fd4775de2ce5f5162b43c59fbcb15e8398242a4dc4afb1316c6845c5d7aced  (file: runtime/specs/farcaster-gate/sealed/holdout2.json; the author has not opened it)
- C4. The statement in AMENDMENT 1 that Zach adopted the gate-wording consequence ("good with your approach") is REPORTED BY THE CHILD SESSION, NOT VERIFIED BY THE PARENT. The v1 gate wording stands as: the gate checks resolution, freshness, keyword overlap and self-citation, and does not judge whether a receipt proves a claim (invariant I3).
