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

## Steps

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
