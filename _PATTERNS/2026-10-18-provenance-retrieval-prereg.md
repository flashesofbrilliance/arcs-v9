# Pre-registration: mechanical provenance retrieval against windowed matching

Date: 2026-10-18. Registered by the commit that adds this file; nothing in it has been run. Origin: Zach asked for faster, more mechanically efficient and deterministically safer ways to retrieve and pin down source provenance than conventional RAG or lineage-graph models, and asked for these conditions to be written down before any benchmark. Rule applied: memory `pre-register-rule-before-counting`.

Corpus is frozen at origin/main `fd8bf4e78bfcc09090e98d20156e5bd13502a83a` (committed 2026-10-18T13:42:03-04:00). Every file is read with `git show <that sha>:<path>`, so later commits to main cannot move the data.

## The question, and what this can and cannot support

Question: does an n-gram index with hash verification find the source of a quoted sentence faster than the matching the repo uses today, without making more confident-wrong provenance claims?

This benchmark can support claims about three things only: speed against the current windowed matching, accuracy on verbatim and lightly edited text, and the safety properties listed below (tamper detection, determinism, confident-wrong rate). It cannot support "better than RAG". There is no embedding head-to-head unless the optional system B2 runs, and even then only on paraphrases. The stack Zach approved on 2026-10-18 stays a hypothesis for any layer this benchmark does not test.

## Corpus and datasets

Indexed corpus: `_CANON/*.md`, `_DECISIONS/*.md` and `_PATTERNS/*.md` at the frozen sha `fd8bf4e7`: 191 files, 10,398 sentences of 8 or more tokens, 10,271 of them occurring in exactly one place. Tokens are lowercase runs of `[a-z0-9']`. A sentence is text split after `.`, `!` or `?` followed by whitespace, with whitespace collapsed.

All sampling uses `random.Random(20261018)` over lists sorted by path then position. A sentence is eligible only if it occurs in exactly one place in the whole 191-file corpus (this is the shared-boilerplate control from [[template-aliasing-shared-boilerplate-fakes-cross-domain-echo]], already applied in `scripts/universe_sweep.py`; ambiguous ground truth is dropped, and the number dropped is reported).

- Held-out files: 19 files (10 percent of 191, drawn by the seed) are removed from the index. They exist only to supply negatives.
- Set A, verbatim, n = 300: sentences from the 172 indexed files. Ground truth: the file.
- Set B, lightly edited, n = 300, disjoint from A: 100 each of B1 (delete 10 percent of tokens, seeded), B2 (swap three adjacent token pairs), B3 (strip case and punctuation and renormalize whitespace). Ground truth: the file.
- Set C, paraphrase, n = 40: 40 further sentences, each rewritten by Claude to keep the meaning and change at least 60 percent of the content words. The 40 pairs are committed as a data file before any system runs. Descriptive only.
- Set D, negatives, n = 200: sentences from the 19 held-out files, kept only if they occur nowhere in the 172 indexed files. Ground truth: no source.
- Set E, speaker attribution, n = 36: the 18 quote atoms in `wonderful-ai` and `scout-global` attributed to the correct speaker, plus the same 18 attributed to the other side. Runs only on this machine, because the transcript is gitignored.
- Set T, tamper: 100 sampled files each get one byte flipped at a seeded position in a temp copy (100 detections to count), 20 files get a whitespace-only byte change (reported separately, flagged by design), and 100 unmodified re-reads (false alarms to count).

The frozen dataset files and their sha256 values are committed before any system code touches them.

## Systems under test

- B0, the current approach: for each query, compare its tokens to every indexed sentence with `difflib.SequenceMatcher` and accept the best sentence if its ratio is at least 0.80 (the `VERBATIM_T` constant in `scripts/attribution_provenance_lint.py`). Otherwise the verdict is UNSOURCED.
- B1, plain substring search: whitespace-normalized exact substring match over the indexed files. Otherwise UNSOURCED.
- S, shingle index: posting lists from 5-token shingles to sentence ids. A query collects candidates by shared shingles, ranks them by shared-shingle count, and verifies the top 3 with the same SequenceMatcher rule as B0 (best ratio at least 0.80). The verdict rule is identical to B0 on purpose, so any difference in confident-wrong rate comes from candidate generation and not from a different threshold.
- S+Bloom: per-file Bloom filters of 5-shingles, sized for a 1 percent false-positive rate, applied as a prefilter before S.
- B2, optional: cosine top-1 with the repo's existing local embedding model, on Set C only, and only if the local Python virtual environment used for the operators has the declared embeddings extra installed and the model is cached offline (a gitignored local setup, so this cannot be re-run from a clean clone). Otherwise reported as "not run", with no substitute.

Stdlib only; Python 3.9.6 as installed. No new dependencies.

## Hypotheses, thresholds and kill conditions

Thresholds are fixed now. A kill condition is binary.

| # | Hypothesis | Metric and threshold | Kill condition |
|---|---|---|---|
| H1 | S is much faster than B0 | Median per-query latency on Set A at full corpus, index build excluded: at least 10x faster than B0. 3x to 10x is a weak pass. | Under 3x: layer 4 is dropped as a speed play. |
| H2 | S is accurate on verbatim text (B0 and B1 are the reference points; the verdict rule comes from `scripts/attribution_provenance_lint.py`) | Top-1 source accuracy on Set A at least 99 percent, and not below B1. | Under 97 percent. |
| H3 | S keeps recall under light edits | Top-1 recall on Set B at least 90 percent, and no more than 3 points below B0. | Recall more than 3 points below B0, or under 85 percent. |
| H4 | S fails safe on text it cannot source | On Set D, at most 1 percent of negatives receive a CLEAN or ANCHORED source. On Set C, any miss must be UNSOURCED, never a confident wrong source. | More than 2 percent on Set D, or any confident-wrong source on Set C. |
| H5 | The Bloom prefilter is safe and useful | No false negatives on Sets A and B (a missed file is a failure), and at least 80 percent of candidate files removed before verification. | Any false negative, or under 50 percent removed. |
| H6 | Hash verification detects tampering (the rehash `canon_drift` in `scripts/universe_ask.py` already does this for canon atoms) | 100 of 100 single-byte mutations flagged, 0 of 100 unmodified re-reads flagged. | Any miss, or any false alarm. |
| H7 | Outputs are deterministic (`scripts/universe_sweep.py` was the first tool found to depend on hash order) | Byte-identical results from all systems under four values of `PYTHONHASHSEED` (1, 2, 3, 4), and across 3 repeated runs. | Any difference. |
| H8 | Operator 21's lineage step (`operators/arcs_librarian.py`, the pairwise pass in `recommend()`) is the cause of the added Librarian time, and an index fixes it | First, profile `recommend()` with the 854 receipt candidates loaded: the lineage pass must account for at least 50 percent of its wall time, or this hypothesis is dropped. Then a posting-list lineage must give exactly the same in-degree for every candidate as today, and cut `recommend()` wall time to 3.7 s or less (from 5.3 s measured on 2026-10-18), with a time-versus-candidates exponent of at most 1.2 at 25, 50 and 100 percent of the pool. | Lineage under 50 percent of time, any in-degree mismatch, or under a 15 percent reduction: the Librarian is left untouched. |
| H9 | Speaker attribution is not weakened | On Set E, all 18 correct attributions CLEAN or ANCHORED and all 18 swapped ones CONTAMINATED, matching `scripts/attribution_provenance_lint.py` as it is today. | Any deviation from that script's results. |

Primary safety metric: confident-wrong provenance. This counts a verdict of CLEAN or ANCHORED that names a source other than the ground truth, or that names any source for a negative. Threshold for S over Sets A, B and D combined (800 queries): at most 0.5 percent (4 or fewer), and not above B0's own count. Kill condition: more than 1 percent (9 or more).

## Speed protocol

Per-query latency uses `time.perf_counter` over every query in Set A. Report the median and the 95th percentile. Run 3 cold and 5 warm repetitions on this machine with no other heavy process (record `uptime` load at the start). Report index build time separately, and the break-even query count (build time divided by the per-query saving). Scaling: repeat at 25, 50 and 100 percent of the indexed files and fit a log-log exponent. "Scales linearly" may be claimed only if the exponent is 1.2 or less.

## Decisions that follow

- Adopt layer 4 if H1, H2, H3, H4 and H7 all pass. A weak H1 pass (3x to 10x) gives a partial adoption, stated as such.
- Adopt layer 5 only if H5 passes and layer 4 is adopted.
- Layer 2 (hash verification) is judged by H6 alone.
- H8 and H9 each decide their own change independently.
- Layers 1, 3, 6 and 7 are not tested by this benchmark and keep their current status.

## Predictions, written before any run

For calibration: I expect H1 to pass strongly (20x to 100x), H2 and H3 to pass, H5 to pass, H6 and H7 to pass, and H9 to pass. I expect the index to miss most paraphrases on Set C (under 40 percent recall), and I am treating that as a correct fail-safe when the misses come back UNSOURCED. I am least sure of H8: roughly even odds that the lineage pass is at least half of the added time, because my attribution of the 2 s to it is an inference, not a profile.

## Order of operations

1. Merge this file.
2. Commit the dataset generator, the frozen dataset files and their sha256 values, before any system code runs on them.
3. Commit the scoring script.
4. Implement S, S+Bloom and the lineage index.
5. Run everything once as specified. A bug-fix rerun is allowed only for a crash, and the crashed run is kept.
6. Publish all results, including failures, in `_STATE/` with a decision receipt.
7. A separate `claims-skeptic` agent re-scores the committed raw outputs. It does not re-run the systems. It shares a model family with me, which limits what that check can catch.

## Rules for the analysis

No threshold, metric or dataset changes after the first run. A change needs a new registration file, and the old result stays on the record. Proportions are reported with Wilson 95 percent intervals and their n. Set C (n = 40) is descriptive and decides nothing by itself. Deviations get a dated entry in the log below, never an edit to the sections above.

## Threats to validity

- The corpus is the repo's own markdown, written by few authors in templated styles. It is probably easier than real foreign text, and the unique-sentence rule only partly offsets that.
- Negatives come from held-out files of the same repo, so they share vocabulary with the index. A false-positive rate here is likely a floor.
- The paraphrases in Set C are written by the same model that built the system, so they may be systematically closer to or further from the index than a human's would be.
- One machine, one Python version, one corpus. Nothing here supports a claim about other corpora.
- Set E depends on a local, gitignored transcript and cannot be re-run elsewhere.
- No semantic-retrieval baseline unless B2 runs, so the benchmark cannot show an advantage over RAG.

## Not claimed

That the approach beats RAG in general. That it handles paraphrase. That provenance means a claim is true (the 2026-10-17 canon strike showed correctly sourced claims can still be unbacked). Anything about layers 1, 3, 6 and 7.

## Deviation log

None. Entries are added below this line, dated, never in the sections above.
