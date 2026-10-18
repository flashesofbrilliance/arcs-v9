---
description: The induced backlog as a graph: what depends on what, in what order, what can start now, and whether the tool exists
---

# /backlog-graph: the backlog as a computational graph

> Read-only. Wraps `scripts/backlog_graph.py` (stdlib, no model calls). It orders and labels; it never
> changes a row and never decides a fate (NOTOMATION).

## Do this

1. Parse the argument:
   - none: the text summary
   - `json`: add `--json`; `dot`: add `--dot` (Graphviz text); `gh`: add `--gh` (also checks PR triggers, slow)
   - `top N`: add `--top N`
2. Run `python3 scripts/backlog_graph.py [flags]` from your own worktree, not by the main checkout
   path (AGENTS.md gotcha 14).
3. Show the output as printed. Without `gh`, say that PR-gated triggers were not checked, because the
   script prints that line and a silent omission would read as "none".
4. Do not turn a label into a claim. NOT-RESOLVED means no path or command in `route.tool` matched the
   repo or the tool catalog; it does not mean the work is impossible. "Stale" means a path that does not
   resolve as written, so a short form of a real path can be a false stale.
5. Close with ONE nudge, never a new loop:
   - the top "ready now" row, with `/readiness <id>` as the next step, or
   - if nothing is ready, the cheapest finding to clear (a dead dependency to re-point, or an
     `unblocks` and `depends_on` mismatch to reconcile).
   Offer the edit; do not make it unasked.

## What it reports

- **Order**: waves by longest dependency path over the active rows; ties by rank, order, priority, id.
- **Ready now**: wave 0, a startable state (OPEN, READY, HOLDING), trigger RIPE, no dead or missing dependency.
- **Biggest unblockers**: rows with the most downstream rows.
- **Tool for the job**: HAVE, PARTIAL, NOT-RESOLVED or NONE, plus a split of stale paths from prose.
- **Findings**: dangling ids, dependencies on COMPOSTED or SUPERSEDED rows, cycles, and
  `unblocks` versus `depends_on` disagreements (the graph holds the union).

## Limits

The graph is only as good as its edges: many rows carry `unblocks` and few carry `depends_on`, so the
ordering is shallow outside well-linked chains. Check the tool itself with
`python3 scripts/backlog_graph.py --self-test` (16 fixtures, no network).
