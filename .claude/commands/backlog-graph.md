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
   - `debt`: add `--debt` (open GitHub debt issues become `debt:<id>` nodes; read-only gh call)
   - `risk` or `tradeoff`: add `--lens risk` or `--lens tradeoff` (each lens stands alone; `--json` carries both)
2. Run `python3 scripts/backlog_graph.py [flags]` from your own worktree, not by the main checkout
   path (AGENTS.md gotcha 14).
3. Show the output as printed. Without `gh`, say that PR-gated triggers were not checked, because the
   script prints that line and a silent omission would read as "none".
4. Do not turn a label into a claim. NOT-RESOLVED means no path or command in `route.tool` matched the
   repo or the tool catalog; it does not mean the work is impossible. A short path such as
   `compass/route.ts` is matched by suffix, `/name` by a repo slash command, a Claude Code built-in (such as `/mcp`) or a URL route, and a bare name
   with several matches is AMBIGUOUS (counted as found). "Stale" means named, not found, and the row
   does not say it will build it; "planned" means named, not found, and the row says build or create.
   A stale entry can still be an unbuilt tool the row forgot to mark, so ask the row owner.
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
`python3 scripts/backlog_graph.py --self-test` (28 fixtures, no network).

## Adding rows: only through `scripts/backlog_append.py`

Never add a row by rewriting `_QUEUE/induced-backlog.jsonl` (a whole-file write can silently drop lines
another session added). Put the new rows in a JSONL file and run, from your own worktree:

```
python3 scripts/backlog_append.py --rows new.jsonl --dry-run   # validate, show graph findings, write nothing
python3 scripts/backlog_append.py --rows new.jsonl             # append in one write, then show findings and waves
```

It refuses the whole batch, and changes nothing, if any row is bad JSON, lacks `id`, `state` or `jtbd`, reuses
an id already in the file or the batch, names a `depends_on` or `unblocks` id that exists in neither, uses a
state outside `runtime/specs/backlog-status.json`, carries the legacy `status` key, or is RUNNING without a
claim. Rows also read from stdin. Self-test: `python3 scripts/backlog_append.py --self-test`. Changing an
existing row is a separate, reviewed edit; this script never touches one.
