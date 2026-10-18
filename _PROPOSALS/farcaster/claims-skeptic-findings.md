<!-- Verbatim text returned by the claims-skeptic agent for the loop 3 deliverables, 2026-10-17. Unedited. Author's own summary is in claims-skeptic-findings-summary.md. -->
Findings, ranked by severity. I did not run `canary.sh` normally, because its live path would make a network call. I did not read `holdout.json`.

## What I ran
- `eval_dev.py` exits 1. Pass line 1 is false.
- `selftest.sh` passes 10/10.
- `stub_resolves_only.py` reports 8/17 wrong.
- The sha256 of `holdout.json` matches the preregistration hash. I hashed it only and did not read it.
- `quickstart.sh --create` refuses without `FC_BUDGET_ALERT_ID`.
- With the variable set, `--create` prints 3 `PLAN:` lines and then refuses at exit 2 on the placeholder commit.
- `canary.sh` with `node` removed from PATH printed `canary occurrences: 0` and exited 0.
- I did not run `accept.sh`, because it executes `eval_holdout.py`, which reads the sealed file.

## HIGH

1. **Preregistered pass line 1 fails.** `eval_dev.py:10` reports `line1_G2_withholds_all_positives_and_0_true_wrong: false`, and the script exits 1.
   - G2 misses 4 positives: F5, L9, L10 and R2.
   - G2 wrongly withholds 6 true cases: T1, T2, T3, T5, R1 and R3.
   - `accept.sh` will therefore report FAIL on line 1 and exit non-zero.
   - Nothing in the deliverables claims line 1 passes. Whoever relays "gates implemented" must say line 1 fails.

2. **Line 1 is unsatisfiable by the gates as defined, so it is a design contradiction rather than a tuning problem.**
   - R3 is labelled VERIFIED, but its own note (falsifier set, line 318) says "a 30-day freshness heuristic will wrongly withhold it." Its age is 79 days, so G1 and G2 must withhold it, which makes "0 true cases wrongly withheld" impossible.
   - T1 has `receipt_author` "@tutorialauthor (own run log, signed)". That is self-citation under the preregistered first-token rule (`gates.py:16-17`). The case note at line 21 says "own log is fine."
   - F5, L9, L10 and R2 are fresh, independent, keyword-overlapping and resolving. No keyword, freshness or self-citation gate can withhold them.

3. **Pass line 3 is gameable and says nothing about quality.**
   - It compares recall only.
   - G1 beats G0 (0.444 vs 0.111) by wrongly withholding 5 true cases. A gate that withholds everything would score recall 1.0.
   - Pass line 2 is a tautology. F2 to F5 are defined as "false with a receipt", so `receipt_resolves` is true by construction (`eval_dev.py:8,11`).

4. **The dev set was authored against the gates and in the same commit as the gate code.**
   - Every T and F case is `authored_by: claude`. F2, F3 and F4 each isolate one gate feature: overlap, freshness and self-citation.
   - F2 is withheld only because "merge" does not match "merged" without stemming, which is an accident of the tokenizer.
   - R1 to R4 were added in 4f31eb8d, the same commit as `gates.py`. R3's note references the 30-day heuristic by name.
   - The set's `_doc` says "Committed before any resolver code." That is false for R1 to R4.
   - The `_doc` text says "v0.2" while `version` is "0.3.0".

5. **The hold-out is "sealed" only by convention.**
   - `holdout.json` is a tracked plaintext file in the repo (`git ls-files` lists it). Any agent, including the gate author, can read it.
   - The hash proves the file is unchanged since sealing. It does not prove nobody read it.
   - "Written without sight of dev cases or gate code" and "unopened" cannot be verified from the repo.

6. **The pass-line-4 implementation differs from the preregistration, with no AMENDMENT block.**
   - `preregistration.md:18` says "G2 recall &gt;= 3 of 4."
   - `eval_holdout.py:7,10` instead tests G2 verdict correct on at least 3 of 4 cases. The docstring says it was "flagged to parent."
   - The preregistration forbids changes except by a dated AMENDMENT block, and there is none.
   - The recall reading would fail whenever the hold-out has fewer than 3 positives.

7. **The canary test can pass vacuously.**
   - Exit codes are ignored (`canary.sh:6-8`).
   - There is no positive control, so the test never shows that a leak would be caught.
   - Missing `node` gives 0 occurrences and rc 0. I demonstrated this above.
   - The `--fixture` runs never read env vars: `classify.mjs` has no `process.env`, and the fixture branch exits before the guard. They cannot leak, so they prove nothing.
   - The write probe's live path refuses at the guard on the bad key (`guard.mjs:7`) and never reaches the key-handling code or the `console.error("FAIL", res.error)` calls at `write-path-probe.mjs:19`.
   - Only the events probe's live path (`FC_NODE_URL=http://FC_TEST_CANARY….invalid`) exercises anything. It would attempt DNS, a network call, and a fetch error may print the canary host and fail the test. I did not run it, so this is unverified.
   - The log path `/tmp/fc-canary.log` is fixed, not made with `mktemp`.

## MEDIUM

8. **`write-path-probe.mjs:46` sets `merge_event: found`, the same boolean as `readback`.**
   - The events response status is only logged (line 44). The "merge event" is never checked.
   - `classify.mjs:29` still returns the reason "merge event seen" on proven.
   - The README does say the merge was not shown network-wide. The classifier text overclaims what the code observes.

9. **`events-probe` gap and duplicate detection rests on unstated assumptions.**
   - `classify.mjs:11` flags any step larger than +1 as a "killed" cursor gap. That assumes contiguous event IDs per shard.
   - I recall Snapchain event IDs being block-number-based, which would not be contiguous. I could not verify this offline.
   - If I am right, a healthy node is "killed." The README does not mention the assumption.
   - The restart cursor is computed in-process as `max+1` (`events-probe.mjs:28,37`). A duplicate can appear only if the server overlaps pages, so the "restart from saved cursor" test is weak.
   - A synced node returns an empty final page, which forces "fallback" (`classify.mjs:10,16`). "proven" is unreachable near head.

10. **R4 mislabels its source.** `receipt_author` is "farcasterxyz/snapchain docs" but the source is PR #1025.
    - `receipt_date` 2026-07-30 equals R3's docs date and looks copied. The "doc_last_changed" field says the PR was open at retrieval.
    - `claim_true: false` is asserted although the note admits the mainnet status is unlabelled.
    - The excerpt is a PR title, so the case does not test what its label claims.

11. **Several excerpts and labels are not checkable against the primary docs.**
    - F5's excerpt ("Read nodes may relay…", dated 2026-10-01, `docs.snapchain`) differs from the R1 excerpt of the same doc.
    - R2's excerpt starts "In both cases…" with no referent.
    - The set's `_unlabelled` field admits the poster's thread was not fetched and that claim wording is Claude's.
    - L9 conflicts with T2 and R3 on mainnet gasless status. L9's note concedes the conflict.
    - T2 and R3 are labelled true and L9 false for the same fact.

12. **`stub_output.txt` is stale.** It shows 13 cases and 6 wrong. The current set has 17 cases and the stub is wrong on 8. The stub is also identical to G0, so it adds no information.

13. **`quickstart.sh` creates nothing without `FC_BUDGET_ALERT_ID`.**
    - `--create` exits 3 before `plan`, and no code path runs `aws run-instances` at all.
    - The gate is only "non-empty": `FC_BUDGET_ALERT_ID=x` passes, so the "real billing alert" claim in the comment (line 4) is prose. Nothing checks that the alert exists.
    - Accept line 7b labels "prints plan" as a pass although `--create` still exits 2.
    - Bare `teardown` (line 50) terminates all tag-matched instances with no confirmation and no `FC_BUDGET_ALERT_ID` gate.
    - "Every resource is tagged" covers only the instance and volume specs. Snapshots and network resources are not covered.

## LOW

14. **`guard.mjs:10` does not trim the `FC_DENY_FIDS` entries.** "1, 2" would not match FID 2. The deny list is optional, and an unset list means no deny at all. A main-wallet key with an unlisted FID passes on the acknowledgement string alone. The README admits the balance cannot be checked.

15. **The probes README says "Nothing here has been executed."** The offline paths (selftest, fixtures) now have been. The live paths have not. The install line pins no versions for `viem` or `@noble/curves`, and the `ed25519` API import is version-sensitive.

16. **Selftest fixtures are hand-built from the classifier's own assumptions.** A 10/10 pass shows consistency, not correctness against real Snapchain output. The fixtures embed `expected_verdict` next to the observation. The classifier does not read it, so there is no leak.

## Checks that passed
- **No answer_key leak into gates.** `gates.py` reads only `c["input"]`, and `answer_key` is used only in `evaluate`. `stub_resolves_only.py` likewise reads only `input`.
- **Preregistration matches `gates.py` definitions.** The G0, G1 and G2 definitions match the code: stopword list, token length of at least 4, at least 2 shared tokens, a 0 to 30 day window, and the first-token self-citation rule.
- **The preregistration text itself was not changed** after 56150ad5.
- **The hold-out hash matches** and was committed before the gate code.
- **The probe fixtures classify as claimed** (10/10).
- **The R3 age arithmetic is right:** 2026-07-30 to 2026-10-17 is 79 days.

## Could not verify
- **Snapchain docs:** R1 to R4 against `node-types.mdx` and `writing-messages.mdx`, the content of PR #1025, and the `/v1/events`, `/v1/submitMessage` and `castById` endpoints and parameters. I made no network calls, and no local copy of those docs is in the repo.
- **Library API:** `@farcaster/core` 0.20.0 helper signatures.
- **Event IDs:** whether Snapchain event IDs are contiguous per shard (finding 9).
- **Hold-out:** that the hold-out was authored blind, and its contents or whether G2 passes line 4.
- **AWS:** the AWS pricing figures in `quickstart.sh`, and any live `aws` behavior (`aws` is not installed here).
- **Canary:** the live events-probe canary behavior.
- **shellcheck:** not installed.

## Summary
Pass line 1 fails. G2 misses 4 positives and wrongly withholds 6 true cases, and the dev set contains cases (R3, T1, F5, L9, L10, R2) that the preregistered gate definitions cannot get right. The set was authored by the same agent as the gates, and R1 to R4 were added in the gate commit. Pass lines 2 and 3 are weak. The hold-out is committed in plaintext, so it is not sealed in any enforceable sense. Line 4's implementation silently diverges from the preregistration. Pass line 6 (the canary) can pass with nothing running, and the write probe's `merge_event` is a duplicate of `readback`. `quickstart.sh` is safe in that it cannot create anything, but its budget gate is only "non-empty". The offline machinery (selftest and the quickstart refusal paths) behaves as described. Do not rely on this deliverable set as showing that the gate separates good from bad evidence. Any status line saying the preregistered gates pass would be false.

All paths are under `/Users/zharris/arcs-v9/.claude/worktrees/fc-cli-loop2-d953c2/`:
- `runtime/specs/farcaster-gate/gates.py`
- `runtime/specs/farcaster-gate/eval_dev.py`
- `runtime/specs/farcaster-gate/eval_holdout.py`
- `runtime/specs/farcaster-gate/stub_resolves_only.py`
- `runtime/specs/farcaster-gate/stub_output.txt`
- `runtime/specs/farcaster-gate-falsifier-set.json`
- `_PROPOSALS/farcaster/preregistration.md`
- `_PROPOSALS/farcaster/quickstart.sh`
- `_PROPOSALS/farcaster/accept.sh`
- `_PROPOSALS/farcaster/probes/` (including `canary.sh`, `classify.mjs`, `events-probe.mjs`, `write-path-probe.mjs`, `guard.mjs`, `README.md`)
