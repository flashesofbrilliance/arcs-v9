# Drift false-positive sample, 2026-10-18

First measured false-positive rate for the "broken path" count that the Docs Reconciliation page calls drift. Re-run it each cycle: the second run gives the first trend point.

## Result

19 of 20 sampled findings are false positives (95%; 95% Wilson interval 76% to 99%), measured at commit cd990f57 with seed 1018. One is a real stale cite.

| Label | Count | Meaning |
|---|---|---|
| H | 8 | historical or intentional: a dated record names a path as it was, or says it is absent |
| G | 6 | generated or ephemeral by design: molted handoff fragments, deleted on purpose |
| T | 5 | template, example, planned or runtime-generated path |
| R | 1 | real: a live go-live runbook says to deploy a deck that is not on main (it exists on other branches only) |
| U | 0 | undecided |

## Basis (read before quoting the number)

- Commit pinned: cd990f57, seed 1018, 20 drawn from 308 broken cites (197 distinct targets) of 3,247 cited paths in 1,002 tracked markdown files.
- The rule is a close rebuild of the 2026-10-06 per-file pass, not an exact copy. On that pass's base commit it gave 2,292 cited paths, 178 broken, 81 files with a break; the original gave 2,108, 166 and 83. The rule text and the label definitions are in the docstring of the sampler script added with this note.
- The 95% describes this rule on this commit. It is not the page's headline: the page sums 14 group-level rows measured on 2026-10-06 (399 broken of 2,327 over 710 files), and no per-file count reproduces that figure. The page's own source file calls its figures group-level estimates.
- The labels are one reader's judgment, assigned after the sample was drawn. The sample is small, and four of the twenty hits are the same cite repeated in dated audits.
- The 20 labeled items, with the reason for each, are in the TSV with the same date beside this note. They are kept out of this note on purpose: the integrity gate reads every path-shaped string in a tracked note, and most of the sampled paths do not exist.

## Population by class (commit cd990f57)

Counts from the sampler's measure mode at commit cd990f57, 308 broken cites in all.

| Class | Count | Share |
|---|---|---|
| molted handoff fragment | 80 | 26% |
| inside a dated drift audit | 19 | 6% |
| inside the archive (other) | 24 | 8% |
| everything else | 185 | 60% |

The first three are mechanically harmless by construction (123 of 308). The sample drew 9 items from the remaining 185, with 1 real and 8 false positives, which is too few to quote a rate for that group.

## What the count did

Between the 2026-10-06 base and this commit the same rule's broken count went from 178 to 308. Molted fragments are a large part of the rise: each handoff molt deletes fragments that the archive and the current handoff block then cite.

## Re-run

The sampler script added with this note has four modes, each documented in its docstring: measure a commit, draw a seeded sample (with a TSV to label), score a labeled TSV, and a self-test. Drawing at commit cd990f57 with seed 1018 reproduces the 20 items exactly. A new sample at a new commit needs fresh labels; only the same commit and seed reproduce these.

## Next steps, in order

1. Decide the exemption for the three mechanical classes (a visible marker or a rule in the script, not silent dropping), recount, then draw about 20 more from what remains.
2. Replace the page's headline with a reproducible figure and its basis, then show this rate beside it with n and the interval.
3. Add the trend once there are two points.
