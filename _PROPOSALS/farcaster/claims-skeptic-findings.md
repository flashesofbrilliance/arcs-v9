# claims-skeptic findings (verbatim summary block as returned; severity-ranked; author did not edit)
Source: claims-skeptic agent, 2026-10-17, read-only, no network, did not read holdout.json, did not run accept.sh.

HIGH
1. Preregistered pass line 1 fails: eval_dev.py:10 reports line1 false, exit 1. G2 misses 4 positives (F5, L9, L10, R2) and wrongly withholds 6 true cases (T1, T2, T3, T5, R1, R3). accept.sh will report FAIL on line 1.
2. Line 1 is unsatisfiable by the gates as defined (design contradiction, not tuning): R3 is VERIFIED but 79 days old so G1/G2 must withhold it; T1's receipt_author "@tutorialauthor (own run log, signed)" is self-citation under the first-token rule while its note says own log is fine; F5, L9, L10, R2 are fresh, independent, keyword-overlapping, resolving, so no keyword/freshness/self-citation gate can withhold them.
3. Pass line 3 is gameable (compares recall only; G1 beats G0 by wrongly withholding 5 true cases; withhold-everything scores 1.0). Pass line 2 is a tautology (F2-F5 have receipt_resolves true by construction).
4. Dev set was authored against the gates and R1-R4 landed in the same commit as gates.py (4f31eb8d). The set _doc says "Committed before any resolver code": false for R1-R4. _doc says v0.2 while version is 0.3.0. F2 is withheld only because "merge" != "merged" without stemming.
5. Hold-out is sealed only by convention: holdout.json is tracked plaintext; hash proves unchanged, not unread; "written blind" cannot be verified from the repo.
6. Pass-line-4 implementation differs from the preregistration with no AMENDMENT block: prereg says G2 recall >= 3 of 4; eval_holdout.py tests verdict-correct on >= 3 of 4 cases.
7. Canary test can pass vacuously: exit codes ignored (canary.sh:6-8), no positive control, missing node gives 0 occurrences rc 0 (demonstrated); --fixture runs never read env vars; write-probe live path refuses at the guard and never reaches key-handling code; only events-probe live path (FC_NODE_URL=http://FC_TEST_CANARY....invalid) exercises anything, attempts DNS, unverified; fixed /tmp/fc-canary.log path.

MEDIUM
8. write-path-probe.mjs:46 sets merge_event: found (same boolean as readback); events response only logged; classify.mjs:29 reason "merge event seen" overclaims.
9. events-probe gap/duplicate detection assumes contiguous event IDs per shard (classify.mjs:11); reviewer recalls Snapchain event IDs may be block-number-based (unverified), in which case a healthy node is "killed". Restart cursor computed in-process (max+1), weak test. Synced node's empty final page forces "fallback"; "proven" unreachable near head.
10. R4 mislabels source: receipt_author "farcasterxyz/snapchain docs" but source is PR #1025; receipt_date copied from R3; claim_true false asserted while note admits mainnet status unlabelled; excerpt is a PR title.
11. Several excerpts/labels not checkable against primary docs: F5 excerpt differs from R1's of the same doc; R2 excerpt starts "In both cases..." with no referent; _unlabelled admits thread not fetched; L9 conflicts with T2 and R3 on mainnet gasless status.
12. stub_output.txt stale (13 cases/6 wrong vs 17/8); stub identical to G0.
13. quickstart.sh creates nothing without FC_BUDGET_ALERT_ID; --create exits 3 before plan; no code path runs aws run-instances. Gate is only non-empty (FC_BUDGET_ALERT_ID=x passes); "real billing alert" is prose. Accept 7b labels prints-plan as pass although --create still exits 2. Bare `teardown` terminates all tag-matched instances with no confirmation and no budget gate. Tagging covers only instance and volume specs.

LOW
14. guard.mjs:10 does not trim FC_DENY_FIDS entries; unset list means no deny; main-wallet key with unlisted FID passes on the acknowledgement string alone.
15. Probes README says "Nothing here has been executed": offline paths now have been. Install line pins no viem/@noble/curves versions.
16. Selftest fixtures are hand-built from the classifier's assumptions: 10/10 shows consistency, not correctness against real Snapchain output.

PASSED: no answer_key leak into gates; preregistration matches gates.py definitions; prereg text unchanged after 56150ad5; hold-out hash matches and predates gate code; probe fixtures classify as claimed; R3 age arithmetic right.
COULD NOT VERIFY: Snapchain docs vs R1-R4, PR #1025 content, endpoint params; @farcaster/core 0.20.0 signatures; event ID contiguity; hold-out blindness and content; AWS pricing; live aws behaviour; live events-probe canary; shellcheck.
SUMMARY: Pass line 1 fails; dev set contains cases the preregistered gate definitions cannot get right; set authored by same agent as gates; lines 2-3 weak; hold-out not enforceably sealed; line 4 diverges from prereg; canary can pass vacuously; quickstart cannot create anything and budget gate is only non-empty. Do not rely on this set as showing the gate separates good from bad evidence. Any status line saying the preregistered gates pass would be false.
