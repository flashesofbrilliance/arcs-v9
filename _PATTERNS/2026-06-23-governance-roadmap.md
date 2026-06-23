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

---

## Pattern catalog — what we've actually been finding, named

Every drift instance this session got fixed individually, with no shared taxonomy connecting them.
`operators/arcs_kintsugi.py` already specifies the right shape for this — `PathogenType`, organized
into Data integrity / Coherence / Process categories, each pathogen detected → diagnosed → repaired
with a **visible golden seam** (never hidden) → logged to an append-only repair log, with a
permanent trust discount even after repair (`repair_nci_discount` — repaired is never as trusted as
never-broken). Kintsugi's own doc is explicit: "Court: frontline defense (prevents bad decisions
from entering); Kintsugi: after-the-fact detection (heals receipts that slipped through)." That
distinction reframes this whole roadmap below.

Mirroring Kintsugi's three categories, built from actual instances found this session, not
hypotheticals:

**Data integrity pathogens** (the artifact itself is internally wrong)
- `SNAPSHOT_STALE` — `_STATE/snapshot.json` claimed facts 15 days out of date
- `VERSION_DIVERGENCE` — `MEMORY.md` (v2.6.0) / `CLAUDE.md` handoff log (v2.5.0) /
  `.claude/arcs-session-state.md` (v2.9.0) disagreed with each other, silently
- `CREDENTIAL_EXPOSED` — plaintext password in `settings.local.json`, never rotated

**Coherence pathogens** (claims contradict observable live reality)
- `TOPOLOGY_INVERSION` — documented domain→project mapping was the literal opposite of live state
  (arcs.care/app.arcs.care)
- `PHANTOM_OPEN_ITEM` — an item stayed listed OPEN after being silently resolved. Found **four**
  in one session: ADR-016 auth wiring, DATABASE_URL-missing-from-Preview, DMARC monitor-only,
  compass-kit Phase 2. This is the single most common pathogen found today.
- `ORPHANED_ARTIFACT` — real work disconnected from canonical history (3 commits in the stale
  `/Users/zharris/arcs` clone — 2 superseded, 1 genuinely lost)

**Process pathogens** (the mechanism meant to prevent drift failed)
- `SILENT_SENSOR` — a designated check exists in prose ("read DRIFT_LOG.md at session start") with
  nothing enforcing it ran. 26 days silent.
- `UNCLOSED_CEREMONY` — opening a gap is an active, written act ("ADR-016: OPEN"); closing one
  currently isn't — it just stops being mentioned, and nobody re-derives that as "closed." This is
  the pathogen that *produces* every `PHANTOM_OPEN_ITEM` above. It is the best single explanation
  for the pattern, not just one instance among several.
- `UNENFORCED_CONVENTION` — a rule exists in writing with no mechanical check behind it (`[NCI:XX]`
  commit tags, "inline styles only," the DRIFT_LOG read instruction itself). Full catalog is task
  #5's job; named here because it's the same shape as the other two process pathogens.

## The abductive read

Asked for the single best explanation covering all of the above, not a list of unrelated causes:
**every one of these artifacts only updates as a side-effect of someone doing the adjacent work in
a live session. Nothing revisits state independent of session activity, and nothing marks a gap
closed when it closes — only when it opens.** That's `SILENT_SENSOR` and `UNCLOSED_CEREMONY`
together, and they're upstream of almost everything else in the catalog.

This changes the roadmap's priority, using Kintsugi's own Court/Kintsugi distinction:
- **#6 (DEWY closing trailers) is Court-equivalent — frontline prevention.** A commit trailer that
  can say `Closes: ADR-016` the way GitHub issues support `Closes #123` gives every resolution a
  closing ceremony at the moment it happens, when the cost of writing it down is lowest.
- **#4 (drift sensor) is Kintsugi-equivalent — after-the-fact healing.** It catches what slipped
  through *despite* a closing ceremony existing, or what nobody had a ceremony for yet (infra
  drift, which has no commit to attach a trailer to in the first place).

Court before Kintsugi, per the source doc. That argues for **#6 outranking #4** in the execution
order above, not just running alongside it — prevention is cheaper than detection, and #6 is also
the thing #4's "ADR-vs-commit Y consistency" check structurally depends on existing first.

## Pre-mortem — fat-tail and long-tail failure modes per item

Fat-tail: low-probability, high-impact, sudden. Long-tail: slow-accumulating, easy to dismiss any
single instance of, compounds silently — exactly the shape of everything in the pattern catalog
above. Most of what we found this session was long-tail; that's worth sitting with before assuming
the fix should be a fat-tail-shaped one (a big dramatic safeguard) rather than a long-tail-shaped
one (a small, cheap, repeated check).

- **#1 backup repo** — *Fat-tail:* a secret missed in manual review (I checked `mcp.json` and
  `settings.json` by reading them once; that's not the same as a systematic secret-scan, and "I
  read it and it looked clean" is exactly the failure mode that let the `settings.local.json`
  password sit undetected for weeks). *Long-tail:* the backup repo itself goes stale and becomes a
  second `SNAPSHOT_STALE` instance — false confidence that something is versioned when the habit
  of committing to it has quietly stopped.
- **#2 password rotation** — *Long-tail (the dominant risk, not fat-tail):* this is the one task
  blocked on a human action outside any session, which is exactly the profile of task that ages
  out silently, per `UNCLOSED_CEREMONY` above. *Fat-tail:* rotating it breaks an undocumented
  script still depending on it, discovered much later, somewhere else entirely.
- **#3 consolidate 3 logs** — *Fat-tail:* picking the wrong file as canonical and losing genuinely
  load-bearing content from the other two in the process (`arcs-session-state.md` has real
  infra gotchas — e.g. the `!` in a DB password breaking `pg`'s URL parser — that aren't duplicated
  anywhere else). *Long-tail:* consolidating to one file doesn't stop a fourth shadow-log from
  appearing later if nothing makes the existing one easy to find.
- **#4 drift sensor** — *Fat-tail:* the sensor's own checklist (which domains, which env vars) is
  itself a hardcoded snapshot that can go stale — a new domain added outside its known list would
  slip past the exact mechanism built to catch that. Self-referential failure: a watcher with a
  blind spot recreates the original problem one level removed. *Long-tail:* alert fatigue —
  miscalibrated severity thresholds train you to dismiss flags, so by the time a real finding
  appears it's lost in noise nobody's reading carefully anymore. Also long-tail: scheduled-run
  cost compounding unnoticed over months — the exact shape of problem this whole roadmap exists to
  prevent, now applied to its own infrastructure spend.
- **#5 prose-rule audit** — *Long-tail:* the audit's own findings list becomes the next
  `SNAPSHOT_STALE` instance if nothing re-checks it. Low fat-tail risk — bounded, low blast radius.
- **#6 DEWY stamps** — *Fat-tail:* shipping a new required convention with no mechanical enforcement
  behind it is just adding a second `UNENFORCED_CONVENTION` instance on top of the first
  (`[NCI:XX]` tags already are one). *Long-tail:* every commit before this ships permanently lacks
  the trailer, splitting git history into two eras any future tooling has to special-case forever.
- **#7 Observatory cherry-pick** — *Fat-tail:* the cherry-pick conflicts with `next.config.ts`'s
  existing static rewrite and silently breaks the currently-working static demo while "fixing"
  it. *Long-tail:* recovering it starts a new maintenance burden (dataset refresh, GitHub-ingest
  re-runs) rather than ending one — recovery isn't the finish line, it's a new commitment.

## Open question — needs Zach's definition before proceeding

"5D 5W 5C 5R 5H" was referenced as the bar for S-tier status on this plan. Not found anywhere in
this repo's canon, specs, or `_CANON/`. Rather than guess a definition and apply it incorrectly,
flagging this as genuinely undefined — need the actual framework before any of the above can be
run through it.
