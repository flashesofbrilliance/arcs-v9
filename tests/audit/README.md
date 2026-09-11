# Audit-script unit tests

Stdlib `unittest` only (no pytest, no deps). Tests the PURE, deterministic functions
of the four audit scripts — git-touching code paths are integration surface and are
NOT exercised here (functions that parse git output are tested by injecting canned
output, never by shelling to a real repo).

Scripts under test:
- `scripts/believability_ledger.py` — `score_ledger`, `ruin_weight`, `high_conf_reel_ins`, `ReceiptOutcomeResolver`
- `scripts/reel_in_scan.py` — `verdict`, `archetypes`
- `scripts/corrections_link.py` — `numeric_nci`, `Candidate.strength`/`.self_link`, `removed_lines_by_file` (diff parser)
- `scripts/receipt_outcome_resolver.py` — `resolve`, `load_export`

Modules are imported by file path via `importlib` (they are not a package); see `_loader.py`.
`believability_ledger.py` is loaded from the sibling `determined-herschel-e59b29` worktree,
falling back to this worktree's `scripts/` if absent.

## Run

From the worktree root:

```
python3 -m unittest discover -s tests/audit -v
```
