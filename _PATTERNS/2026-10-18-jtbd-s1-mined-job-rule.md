# JTBD graph s1: the "states a job" rule for mined jobs (2026-10-18)

Status: fixed before the miner ran (this file is committed before the s1 JTBD adapter (new in the s1 PR)
counts any memory or _PATTERNS file). Required by `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`, s1.

## Rule
A memory file (`~/.claude/projects/-Users-zharris-arcs-v9/memory/*.md`, excluding `MEMORY.md`) or a
pattern file (`_PATTERNS/*.md`) states a job when its text, case-insensitive, contains any of:
`jtbd`, `job to be done`, `job-to-be-done`, `jobs to be done`, `jobs-to-be-done`.

- Memory atoms are keyed by front-matter `name`; a memory file with no front-matter `name` is not
  emitted and is listed as skipped. Cited line: the front-matter `name:` line.
- Pattern atoms are keyed by file stem. Cited line: the first line that matches the rule.
- This file itself and the pre-registration file are excluded from the pattern miner (they define
  the rule; they do not state a job).

## Gate (unchanged from the pre-registration)
Zach labels 30 mined files drawn by `random.Random(20261018)` over the sorted candidate id list
(yes = states a job). Miner and labels must agree on at least 24 of 30, else `job:memory` and
`job:pattern` ship empty. Until the labels exist, the adapter emits them only with `--mined`;
the default graph carries backlog jobs only.
