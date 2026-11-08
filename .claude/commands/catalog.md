---
description: Recommend the one right existing tool for a stated job from the tool catalog, and run it with consent
---

# /catalog — the induction surface for the toolset itself

> Given a stated job, recommend THE one right existing tool and (with consent) run it.
> Reads `runtime/specs/tool-catalog.json` (130 tools: skills · commands · workflows ·
> hooks · scripts · operators). SINGULAR recommendation by design — a menu IS the
> decision fatigue ARCS kills (ADR-070 induction surface). NOTOMATION: recommend and
> scaffold, never replace the choice; the human fires the tool (or says "run it").

## `/catalog --orphans` (install state, 2026-10-06)

If the argument is `--orphans`, skip the job match: run `python3 scripts/tool_orphan_audit.py`
(read-only; public-repo list from a daily gh cache) and show its report grouped by class:
AVAILABLE-NOT-INSTALLED (each with its one-line install command), INSTALLED-UNUSED, DUPLICATE,
BROKEN. Never install, uninstall, or retire anything from here; Zach decides. The same state is
in the catalog (`tools[].state`, `install_audit.gaps`), and session start prints the one-line
summary.

When matching a job (below), a tool whose `state` is AVAILABLE-NOT-INSTALLED still counts:
recommend it with its install command instead of inventing a replacement.

## Plain verbs (checked before step 0, 2026-11-08)

If the job starts with one of these verbs, route by this table and skip the lookup. The graph
scores these phrases badly: "connect the dots" ranked `universe_jtbd_adapter.py` and "tear it
down" ranked `design_debt_sweep.py`. Pick the row by what the target is. A verb not listed here,
or a target that fits no row, goes on to step 0. A row marked GAP has no tool yet: say so and
name its backlog row. Do not build the tool here.

| Verb | Target | Tool |
|---|---|---|
| connect the dots | an outside paper, post or field | `/echo-scan <source>` |
| connect the dots | a job, before planning it | `/prior-art <job>` |
| tear it down | a person or company (site + bio PDF) | `/teardown` |
| tear it down | a document's claims | Agent `claims-skeptic` |
| decompose | a session or scattered state | `/fold` |
| decompose | a page, into atoms to pages with params | GAP: backlog `decompose-page-atomic-params` |
| check it | an HTML page | `/page-gate <path>` |
| check it | a diff before merge | `python3 scripts/neighbor_scan.py`, then `/code-review` |
| ship it | a PR | `scripts/safe_merge.sh <pr> <head-sha>`, only on Zach's go |
| ship it | docs-only work | `scripts/ship_docs.sh` |

Say "(answered by the verb table)". The routes still fire only on consent (step 5).

## Steps

0. **Ask the JTBD graph first (since 2026-10-20; s4 blind test passed 16 of 18 against this
   command's 6, `runtime/specs/jtbd-s4/score.json`).** Run
   `python3 operators/jtbd_query.py --lookup "$ARGUMENTS"` from your own worktree. Its first line
   says which path answered:
   - `answered by: jtbd-graph`: lead with its **best** tool as the one recommendation (step 4
     format), then give its open blockers, what it needs (dependency closure) and its last
     receipts in one or two lines. The other assembly items may be named as the runner-up line;
     still never a menu. Say "(answered by the JTBD graph)".
   - `answered by: fallback (...)`: the graph was missing, stale and could not rebuild, or found
     nothing. Do steps 1 to 4 as before and say "(answered by the catalog fallback: <reason>)".
   The lookup rebuilds a graph older than its source catalogs and never serves a stale one.

1. **Load the catalog.** Read `runtime/specs/tool-catalog.json`. If it is missing or
   older than the newest file in `.claude/skills|commands|workflows|hooks`, `scripts/`,
   or `operators/`, regenerate first: `python3 scripts/tool_catalog_emit.py` (read-only
   over the repo; safe to run any time).

2. **Take the job.** The user's argument to /catalog is the stated job ("$ARGUMENTS").
   If no job was stated, do NOT dump the list — ask one question: "What's the job?"
   (If they explicitly ask for the full inventory, point them at
   `runtime/specs/tool-catalog.md` instead of pasting it.)

3. **Match by JTBD, not by name.** Scan the `jtbd` lines for the tool whose declared
   job fits the stated job. Reuse-before-invent is the law here
   (memory: jtbd-reuse-existing-tool-before-inventing): if an existing tool covers ≥80%
   of the job, it wins over building anything.

4. **Recommend ONE.** Output exactly:
   - **"You should use `<name>`"** — one line of why it fits (its harvested JTBD),
     and its invoke string from the catalog (`/skill`, `python3 scripts/...`, etc.).
   - If two tools genuinely tie, pick the cheaper/more-specific one and say in one
     sentence what the runner-up was and why it lost. Never render a menu.
   - If NOTHING fits, say so plainly and route to the backlog: propose a one-line
     `_QUEUE/induced-backlog.jsonl` item rather than improvising a new tool inline.

5. **Fire only on consent.** If the user says run it (or asked in the imperative),
   invoke the tool natively — Skill tool for skills/commands, Bash for scripts,
   Workflow for workflows. Hooks are automatic; never fire them manually.

## Later slices (do not build from here)
Kabuki-mask contour render (zero-shot low-poly, Golden-Inchworm sharpened) and
gravity-well binding to the generative backlog — each is its own session per the
backlog item `tool-catalog-dispatcher-induction-surface`.
