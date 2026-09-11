# Almanac cache manifest + back-propagation — v1 sketch

> The shared temporal backend. "Prompt caching for the corpus": cache the expensive
> query (auditor grading), keyed by content-scope + time + repo-SHA, so every
> reference work (Almanac, Chronicle, Concordance, public projections) reuses one
> graded slice instead of re-auditing. Status: SKETCH, pre-wiring.

## The unit: a slice

The atom of the cache is a **slice** = `(domain, epoch)`, graded at a commit.

- `domain` — one of the auditor domains: `memories | handoffs | product | recoil`.
- `epoch` — `YYYY-MM` (the time bucket the auditors now tag every node with).
- graded content = the nodes with that `(domain, epoch)`, living in `digest-<domain>.json`.

So the digests ARE the cache store; the manifest is the index over them.

## cache-manifest.json

```json
{
  "generated": "2026-09-04",
  "repo_head": "<current HEAD sha at manifest write>",
  "slices": [
    {
      "domain": "memories",
      "epoch": "2026-06",
      "node_count": 12,
      "graded_at_sha": "<sha the slice was graded against>",
      "graded_at": "2026-09-04",
      "scope_globs": ["memory/*.md"],
      "fresh": true
    }
    // ... one row per (domain, epoch)
  ]
}
```

`scope_globs` = the file globs whose changes could invalidate this slice (each
domain has a fixed provenance scope: memories -> `memory/*.md`; product ->
`_DECISIONS/*`, `_SEEDS/*`, `WORLD.md`, `AGENTS.md`; handoffs -> `CLAUDE.md`,
`_ARCHIVE/handoffs.md`; recoil -> `runtime/recoil/**`, the recoil memories).

## Freshness = the immune system, generalized

A slice is **fresh** iff nothing in its `scope_globs` changed between `graded_at_sha`
and current `HEAD`:

```
git diff --name-only <graded_at_sha> HEAD  ∩  scope_globs  ==  ∅   -> fresh
                                                             ≠ ∅   -> dirty
```

This is exactly the `lattice-drift` check (`lattice=<sha> repo=<HEAD>`), applied per
slice instead of to the whole corpus. A dirty slice is a cache miss waiting to happen.
(This is what made the ADR-074 nodes go stale in 24h: I edited `_DECISIONS/index.json`,
which is in the product scope, so every product slice touching it went dirty.)

## Request / back-propagate flow

A consumer asks for `(scope, time-range)` — e.g. Almanac wants `product, 2026-04..05`;
Chronicle wants `all-domains, 2026-04..2026-09`; a public Q3 brief wants `all, 2026-07..09`.

```
resolve request -> the set of (domain, epoch) slices it covers
for each slice:
    manifest hit AND fresh  -> REUSE  (read nodes from digest, no auditor run)
    missing OR dirty        -> BACK-PROPAGATE:
                                 run the Curator for just this (domain, epoch)
                                 write/refresh its nodes in digest-<domain>.json
                                 stamp manifest: graded_at_sha = HEAD, fresh = true
                                 -> now REUSE
serve the union of nodes to the consumer
```

The payoff is the reuse property: **a time-range is graded once and every consumer
reuses it.** Chronicle and Concordance stop being fresh audits — they're cheap views
over already-graded slices. A public brief for a quarter is just a fourth reader of
the same slices.

## The mechanical / judgment split (per the metabolism)

- **Mechanical (auto):** resolve slices, diff scope-globs for freshness, read cache,
  stamp the manifest, invalidate. No judgment.
- **Judgment (the Curator, once per back-propagation):** the grading itself
  (LIVE/DRIFTED/STALE), what counts as a node. Paid once per slice, cached after.
  This is the only expensive/judgment step, and the cache exists to not repeat it.

## v1 scope (what to wire first)

1. Stamp `graded_at_sha` onto each slice when a digest is (re)written; emit
   `cache-manifest.json`.
2. A `freshness` check: `git diff --name-only <sha> HEAD` ∩ scope-globs, marking
   slices fresh/dirty. (Reuses the drift-check machinery.)
3. Back-propagation as a targeted Curator run over one `(domain, epoch)` — not a
   full re-audit.
4. The Reader reads the manifest to (a) show freshness per slice and (b) only
   trigger a re-grade on dirty slices the viewer actually opens.

## Non-goals (v1)

- Not a live DB — the cache is the flat digests + a manifest, git-SHA keyed.
- No automatic back-propagation on every commit; back-prop is pull-driven (on
  request of a dirty/missing slice), so cost is paid only when a stale slice is
  actually read. Lazy, like a real cache.
