# Engineering Process Governance Roadmap — 2026-06-23

> Born from a single session's drift-correction work (see `MEMORY.md` `[v3.0.0]` and
> `DRIFT_LOG.md` `## 2026-06-23`). Seven proposals came out of that session, in conversation
> only — none built. This doc exists so the dependency structure between them survives the
> next context switch, not just the flat list.

## The 7 items

| # | Item | Standalone value? |
|---|---|---|
| 1 | Local-only git backup repo for `~/.claude` globals | Yes — version history on its own |
| 2 | Rotate/confirm-dead leaked Supabase password | Yes — security hygiene, unrelated to everything else |
| 3 | Consolidate arcs-v9's 3 overlapping narrative logs (`MEMORY.md` / `CLAUDE.md` handoff log / `.claude/arcs-session-state.md`) | Yes — reduces drift surface immediately |
| 4 | Drift-sensor: cadence + Y-gate/BAR/Time-Quality-ROM severity design + Observatory display | Design phase yes; build phase needs 7, and is stronger with 6 and 3 |
| 5 | Audit prose-rules (`SKILL.md`/`AGENTS.md`/`CLAUDE.md`/`WORLD.md`) for enforcement gaps | Yes — valuable even if nothing downstream gets built |
| 6 | DEWY commit/PR stamp (`ADR-Ref:` / `Y-Gate:` trailers) linking commits back to ADRs | Design phase yes; retrofit is stronger after 3 |
| 7 | Cherry-pick orphaned Observatory commit (`35070a3`) | Yes — a working interactive Observatory is useful regardless of drift-sensor plans |

Every item has standalone value. Nothing here is *purely* instrumental to something else — that's
worth stating plainly so this doesn't get treated as one big sequential project when most of it
isn't.

## Relationship types (not all dependencies are the same shape)

- **Parallel** — no dependency either direction, can run simultaneously.
- **Sequential** — B genuinely doesn't make sense to build until A is done (not just "tidier after").
- **Interlocking** — two tasks jointly define a shared artifact/interface; neither is *finished*
  until both agree on its shape, even though either could start alone.
- **Entangled** — each makes the other more justified or more valuable, but neither blocks the
  other. Could ship independently; shipping together produces a better combined result.

## The actual graph

```
WAVE 0 — fully parallel, zero dependencies, start any/all now
  #1  backup repo            (scope already decided: excludes settings.local.json)
  #2  rotate password        (blocked only on Zach checking the Supabase dashboard — not on me)
  #5  prose-rule audit       (feeds #4 and #6, entangled with both, blocks neither)
  #7  Observatory cherry-pick (standalone value; unblocks #4's display sub-component)
  #4a design only — cadence decision + severity spec (Y-gate/BAR/Time-Quality-ROM)
  #6a design only — exact trailer format proposal

WAVE 1 — sequencing point
  #3  consolidate the 3 logs
      → SEQUENTIAL before #4b and #6b (see below). Building automation against 3 files
        that are about to merge into 1 is throwaway work — decide the canonical file first.

WAVE 2 — the interlocking build phase, needs #3 + #6a settled, #7 merged
  #4b sensor build (cron job) — checks the ONE consolidated log (needs #3),
      optionally checks "does ADR's stated Y match its linked commits' Y-Gate trailer"
      (needs #6 actually shipped on a few commits first — no trailers exist yet to check)
  #4c Observatory display wiring — needs #7 (the real interactive page) AND needs #4a's
      severity schema decided, since that schema IS the data.drift-findings.json shape
  #6b retrofit — update AGENTS.md/CLAUDE.md commit-message convention, apply going forward
      → SEQUENTIAL after #3 (same reasoning: don't wire "auto-generate the handoff log
        from trailers" into a structure that's being deleted)
```

## Interlocking pairs (shared interface, not strict ordering)

- **#4 ↔ #7** — `#4c` needs `data.drift-findings.json` to actually load in the Observatory's
  dataset switcher. `#7`'s cherry-picked page needs to confirm its existing dataset-loading code
  can consume that shape (or take a small patch). Neither side can call this "done" without the
  other agreeing on the schema — but `#7` can be merged before that conversation happens; the
  page has value on its own.
- **#4 ↔ #6** — `#4b`'s "ADR-vs-commit Y consistency" check is meaningless until `#6`'s trailer
  syntax is fixed, because the parser needs to know exactly what string to grep for. This is a
  joint decision: how `#6` formats the trailer determines how `#4b` parses it.

## Entangled pairs (mutual reinforcement, no hard block)

- **#5 ↔ #6** — `#5`'s audit will very likely surface "commit message format is itself an
  unenforced prose convention" as a finding (it already is one — the existing `[NCI:XX]` tag has
  no check behind it). `#6` is the proposed fix for exactly that finding. Doing `#6` without `#5`
  fixes one instance without knowing if it's representative; doing `#5` without `#6` documents
  the gap without closing it. Worth sequencing `#5` to *inform* `#6a`, even though `#6a`'s design
  doesn't strictly require `#5` to exist first.
- **#3 ↔ #6** — `#6`'s pitch ("a script can reconstruct most of the handoff log from git
  trailers") only pays off once there's one canonical log to reconstruct *into*. Each makes the
  other more worth doing; neither requires the other to exist to be individually valid.

## Recommended execution order

1. Start `#1, #2, #5, #7` now, in any order, in parallel — no reason to sequence these.
2. Use `#5`'s findings to sharpen `#6a`'s design before writing it up formally.
3. Decide `#3` (which log is canonical) before touching `#4b`'s build or `#6b`'s retrofit.
4. Only after `#3` is settled and `#7` is merged: build `#4b` and `#4c` together, since they
   share the severity-schema interface, and apply `#6b`'s retrofit alongside.

## What this doc is not

Not a commitment to build all seven. Not a substitute for `TaskList` (which tracks live status —
this doc won't be kept in sync turn-by-turn, `TaskList` is the source of truth for "what's
pending/in-progress/done"). This is the dependency reasoning that's expensive to reconstruct from
scratch in a future session, written down once so it doesn't have to be re-derived.
