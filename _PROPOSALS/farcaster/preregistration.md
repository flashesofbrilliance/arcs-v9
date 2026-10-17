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
