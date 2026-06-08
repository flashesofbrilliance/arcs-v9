# Provenance Ledger

Every scored finding and risk in the Observatory cites where its claim came from.
The **Source** cell links to the artifact (a GitHub commit, or a file/line blob);
the **ID** cell links here, to the provenance method that substantiates the claim.

This ledger is the index of those methods. `P##` ids are stable references.

| ID  | Provenance method | What it asserts |
|-----|-------------------|-----------------|
| P00 | Author-me placeholder | Editorial slot — not yet substantiated; fill in for a tailored instance. |
| P04 | `git shortlog -sne` | Commit/author counts over the tracked span. |
| P09 | Source line count | A handler/module's size in lines, cited to its file path. |
| P10 | Source line count | Core gate-logic size, cited to `src/lib/ygate.ts`. |
| P28 | Test scan (`find`) | Presence/absence of automated tests in the tree. |
| P30 | Source line count | Load-test harness size, cited to `scripts/lattice_sim.py`. |

## Rules-engine datasets

For datasets built by `scripts/github_ingest.py`, provenance is the commit itself:
the **Source** is the commit SHA (links to `/commit/<sha>` on GitHub) and **Observed**
is `commit`. These findings carry no `P##` id — the commit *is* the receipt, so the
ID cell shows `—`. Re-run the ingester to reproduce the dataset from live history.

## Heuristic dataset

For `scripts/build_observatory.py`, findings are editorial assessments grounded in
repo signals (file metrics, ADR counts, git history). Each cites a `P##` method above
and a Source artifact. Re-run the generator to refresh.
