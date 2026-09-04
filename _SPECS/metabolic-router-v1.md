# The Metabolic Router — v1 spec

> **JTBD:** a new primary record (a ruling, a receipt, a lesson, a seed, a witness stub, a
> hardening) should reach every organ of the corpus the way a nutrient reaches every cell —
> without a human being the pump. Today every nutrient is hand-carried: write the memory,
> update `MEMORY.md`, patch `index.json`, sync the oracle, re-run the auditors. The router
> automates the **mechanical** half of that fan-out and surfaces only the **judgment** half.
>
> **Verdict (per the proactive-spec rule): FORK-AND-MOD / COMPOSE.** Reverse lookup found
> every organ already exists as a disconnected reflex — `/witness` (mouth), `oracle.py`
> (numbering), the drift hooks (immune system), `/canon-review` (judgment valve), the Atlas
> curators (digestion), `night-moves` (daily sweep). Nothing is net-new; the router is the
> connective tissue that fires them in sequence off one trigger. Compose: **Curator +
> Skeptic + Librarian** (curate the record → verify it exists on main → shelve it).
>
> Status: SPEC v1, pre-wiring. Priority: HIGH (flagged by Zach 2026-09-04).

## 1. The metabolic loop

```
MOUTH      ingest a raw nutrient        (/witness, session end, recoil-close, commit, night-moves)
STOMACH    classify its molecular form  (ADR | DEWY | Wisdom/Memory | Seed | Handoff | Witness | Hardening | Recoil)   [JUDGMENT, scaffolded]
LIVER      author it in canonical form  (oracle-numbered, gated, schema-conformant)                                    [semi-auto]
GATE       integrity check at write     (do the ADRs/commits/scripts it cites EXIST on origin/main?)                    [MECHANICAL — new]
BLOOD      route to every organ         (the routing manifest below)                                                   [MECHANICAL]
QUEUE      surface judgment calls       (canon promotion, public projection, VARIANT-vs-SUPERSEDED, consolidation)      [JUDGMENT]
IMMUNE     drift detection              (lattice-drift / seedbank-drift / memory-sync, per cache slice)                 [MECHANICAL detect, human resolve]
```

NOTOMATION holds: the router scaffolds and sequences; it never overrules a judgment node.

## 2. The routing manifest (nutrient-type → organs)

| Nutrient | Mechanical fan-out (auto) | Judgment queue (human) |
|---|---|---|
| **ADR** (a ruling) | `_DECISIONS/index.json` row · `oracle.py` counter · concordance links · cache-invalidate `product/<epoch>` · Almanac re-render | canon-propagation (`/canon-review` DEROT/ESCALATE/FORK) · supersedes-which? |
| **DEWY receipt** | `_STATE/` ledger · cache-invalidate `product/<epoch>` | outcome close-loop owed? |
| **Wisdom / Memory** | memory file · `MEMORY.md` index pointer · concordance links · cache-invalidate `memories/<epoch>` | consolidate if index over budget · VARIANT vs SUPERSEDED vs duplicate |
| **Seed** | `_SEEDS/index.jsonl` · ledger · cache-invalidate `product/<epoch>` | germination conditions met? |
| **Handoff** | CLAUDE.md live block (keep latest 1–2) · relocate oldest to `_ARCHIVE/handoffs.md` · cache-invalidate `handoffs/<epoch>` | — |
| **Witness stub** | `_STATE/` verbatim timestamped stub | promote-later (to ADR / DEWY) only if durable |
| **Hardening lesson** | — | **which factory accretes it?** (blueprint / skill / workflow) — the compounding rule |
| **Recoil close** | `runtime/recoil/` SSOT · cache-invalidate `recoil/<epoch>` | external projection (what/when to cast, air-gap) |

Every row's mechanical column is grep-able, deterministic, and idempotent. Every judgment cell lands in one queue, not in prose.

## 3. The integrity gate (the new organ)

Before routing, the record is **verified against `origin/main`**, not against the session's RAM:

- every `ADR-0NN` it cites → exists in `_DECISIONS/` and `index.json` (else: numbering gap, flag)
- every commit SHA it cites → `git merge-base --is-ancestor <sha> origin/main` (else: unmerged, flag)
- every script/path it cites → `git cat-file -e origin/main:<path>` (else: vapor, flag)

This is the check that would have caught the five "described-but-never-merged" memories the
full-temporal audit found (ADR-042 gap, ADR-075 next-free, three unmerged commits). A record
that cites vapor is routed with a `DRIFTED-AT-BIRTH` tag, never silently.

## 4. Trigger points

| Trigger | Fires the loop on |
|---|---|
| `/witness` | one stub (mouth only; promotion queued) |
| session end / `/handoff` | the session's new records, batched |
| `recoil-close` | one engagement's close-out |
| post-commit hook | any commit touching `_DECISIONS/ _SEEDS/ memory/ CLAUDE.md` (cheap: index + cache-invalidate only) |
| `night-moves` | the day's sweep (the existing digest becomes the router's daily batch) |
| on-demand `metabolize <path\|git-range>` | back-fill / re-route a range |

## 5. The cache coupling

Every route ends in **cache-invalidate `(domain, epoch)`** — the slice the record lands in
goes dirty in `cache-manifest.json` (see `_ARTIFACTS/atlas/cache-manifest.spec.md`). It is
re-graded lazily, on the next read of that slice, by a targeted Curator run — never a full
re-audit. Router + cache together are the shared temporal backend; Almanac / Chronicle /
Concordance / public projections are all readers of it.

## 6. The receipt

Every run prints a `metabolize` receipt: what was ingested, its classified form, the
integrity verdict, which organs it reached, and what is queued for judgment. The receipt is
itself a nutrient (a DEWY-shaped record) — the loop is self-describing.

## 7. v1 scope (wire in this order)

1. **Integrity gate** as a standalone check (`scripts/integrity_gate.py <file>`): cites-exist-on-main. Highest value, zero judgment, reusable by the pre-commit hook.
2. **Routing manifest** as data (`runtime/specs/routing-manifest.json`) + a `metabolize` script that applies the mechanical column for one record and emits the judgment queue.
3. **Cache coupling**: `metabolize` writes the dirty slice into `cache-manifest.json`.
4. **Triggers**: post-commit hook (cheap path) + `night-moves` batch. `/witness` and `/handoff` call it explicitly.
5. **Judgment queue UI**: fold into `/canon-review`'s existing multi-picker (fork-and-mod, not net-new).

## Non-goals (v1)

- No automatic canon promotion, public projection, or memory consolidation — those stay judgment.
- No live DB; the corpus stays flat files + git. Git's non-fast-forward is the cross-harness write-lock.
- Not a replacement for the auditors — the router *invalidates*; the Curator *re-grades*.
