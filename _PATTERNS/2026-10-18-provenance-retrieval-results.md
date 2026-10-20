# Provenance retrieval benchmark: results of the single registered run (2026-10-18)

Registration: `_PATTERNS/2026-10-18-provenance-retrieval-prereg.md`. One run, no reruns, no threshold changes. All raw outputs are published on this branch with a SHA-256 manifest. H8 (Librarian lineage) is NOT measured yet; see "Pending".

## Results

Scored by the frozen `scripts/provenance_bench_score.py` over the verdict files written by `scripts/provenance_bench_run.py`; datasets built by `scripts/provenance_bench_dataset.py`.

| Hypothesis | Measured | Verdict |
|---|---|---|
| H1 speed | B0 148.6 ms vs S 0.032 ms per query, 4,697x | PASS |
| H2 verbatim recall | S 300/300, B1 300/300 | PASS |
| H3 edited-text recall | S 85.0% (255/300), B0 87.0%. Per kind for S: B1 97, B2 58, B3 100 | FAIL, exactly on the 85% kill line |
| H4 no false confidence | 0/200 negatives answered confidently; paraphrase recall 0/40, 0 confident-wrong | PASS |
| H5 Bloom prefilter | 37 false negatives in 600, candidate reduction 79.6% | KILL |
| H6 tamper | 100/100 flips caught, 0/100 false alarms, 20/20 whitespace edits flagged | PASS |
| H7 determinism | 16 groups, byte-identical across 12 runs | PASS |
| H9 speaker attribution | 36/36, identical to the current lint | PASS |
| Primary safety | 0 confident-wrong in 800 (Wilson upper bound 0.48%) | PASS |

Scaling exponent: B0 1.135 (linear claim allowed), S 1.267 (not allowed).

## Registered decisions

- Layer 4, 5-token shingle index: NOT ADOPTED (H3 failed).
- Layer 5, Bloom prefilter: NOT ADOPTED (H5 kill).
- Layer 2, hash verification: SUPPORTED.
- Speaker attribution unchanged: SUPPORTED.
- Librarian lineage index: UNDETERMINED until H8 runs. The draft stays a draft.

## My predictions that were wrong

The predictions are in the registration, `_PATTERNS/2026-10-18-provenance-retrieval-prereg.md`, written before the run.

H3 (predicted pass), H5 (predicted pass), H1 magnitude (predicted 20x to 100x, got 4,697x). The paraphrase prediction (under 40% recall) was right, though the result was 0%.

## What the failures are

- H3 and H5 share one cause: short sentences. All 37 Bloom false negatives are Set B rows (34 B2, 3 B1) with a median of 10 tokens, too few for 5-token shingles to survive an edit. S misses the same 37, and B0 recovers 6 of them.
- S and S+Bloom give identical answers on every row, so the Bloom loss costs no recall beyond S's own, but it also buys nothing that was registered as worth the cost.
- Nothing in the data shows a safety failure. The wrong-answer risk is zero on this data; the cost of the shingle index is missed edited quotes, not false sources.

## Independent re-score

The agent's code is not committed; its inputs were the published raw results and the frozen datasets, and the comparison target was `scripts/provenance_bench_score.py` output. Its own script and report live only in this session's scratch, so treat the agreement as reported, not archived.

A separate claims-skeptic agent (same model family as the author, stated for what it is) recomputed every count with its own stdlib code and without importing the scorer. Both SHA-256 manifests verified. The frozen scorer's output matched the published scores exactly. Its counts equal the table above (for example S Set B 255, B0 261, 37 dropped true files, 0 confident-wrong, 12 identical hashes per group).

Its flags, none of which change a verdict:
- ANCHORED never occurs in sets A to D, so the confident class is CLEAN only there.
- B1 answers UNSOURCED on all of Set B by design, so its edited-text recall is 0.
- 9 of 40 paraphrases were kept with `valid` false (deviation 1 in the registration).
- Whether the S timing is a cached lookup was not checked by the skeptic from the files; the timing harness counts warm passes only, as registered.
- Lint and S agree on all 36 speaker cases; they may share a code path, so H9 shows equivalence, not independence.

## Addendum 2026-10-20: H8 measured (Librarian lineage index)

Run once with `scripts/provenance_bench_run.py h8` and scored by the frozen `scripts/provenance_bench_score.py`.

| Measure | Registered bar | Measured | Verdict |
|---|---|---|---|
| Lineage share of `recommend()` wall time | at least 50% | 80.5% | PASS |
| In-degree mismatches | 0 | 0 | PASS |
| Wall time, same-session before to after | at most 3.7 s and at least 15% cut | 5.15 s to 1.55 s, 69.9% cut | PASS |
| Time-versus-candidates exponent | at most 1.2 | 1.183 | PASS, close to the bar |

H8 PASS. The registered rule applies: the draft Librarian change (PR 1588) may merge. Merging stays Zach's call.

Disclosures, none of which I think changes the verdict:
- The pool was 2,677 candidates with 1,147 receipts loaded, not the 854 receipts in the registration, because the receipts universe grew before the run. The before-and-after comparison is in one session, so growth cancels, but the absolute 3.7 s bar was set for the smaller pool.
- The first attempt crashed before measuring, on a Python 3.9 dataclass lookup in `load_librarian`. The fix (register the module in `sys.modules` before executing it) is one line and does not touch the measurement. It is committed with this addendum.
- Machine state at start: load 2.7 (bar 3), swap about 90% full, no browser tests running. The exponent margin (1.183 against 1.2) is small enough that a noisy machine could flip it; I did not rerun, to keep one run.
- The audit trail: `h8.json` joins the published results with its checksum. The independent re-score by a second agent was not repeated for H8.
