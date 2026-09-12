# ADR-065 — Corpus is SSOT; storage is induced projection; the Infra Compass reads the field

**Status:** DECIDED (doctrine) · instrument = ROM CANDIDATE, designed-not-built
**Date:** 2026-08-18
**Y-state:** GREEN (doctrine) · YELLOW (instrument, until built)
**Sequence:** allocated via oracle (`scripts/oracle.py next adr` → 65)

## Context

The self-cataloging work (memory_index_sync inchworm, memory_catalog_emit, the Terrain
Atlas, doll_export/doll_sprout) created a family of derived representations over the
memory/seed corpus. The question forced a storage doctrine: where do nodes, edges,
embeddings, and bundles live — blob, vector store, Postgres/Prisma — such that when
current is induced (a query, a session touch, an export), every representation points
at the right vector orientation under global serialization?

This session also demonstrated, live, the failure states the doctrine must govern:
three parallel v3.35.0 handoffs (**FORK**), repos publicly visible while their own
descriptions said "Private pending review" (**PARADOX** — two stores asserting
contradictory truth), a stale lattice count (**DRIFT**), and a PII-exposure near-miss
(**RED** class).

## Decision

### 1 · The corpus (git) is the single source of truth; every store below it is an induced projection
Memory files, seeds, ADRs, frontmatter, `[[links]]` live in git. Git is the write-lock
and the global clock (same authority ADR-057 gave ADR numbering). Postgres, vector,
and blob are **derived, re-derivable, and disposable**; they are never hand-written —
always emitted. Bodies are small text: **git IS the blob store**; blob storage holds
only heavy derived artifacts (tickets, atlas builds, PDFs), keyed by content hash.

### 2 · Four serialization invariants
1. **Embeddings pin to content, not names**: keyed `(node_id, content_sha, model_id)`;
   a changed file makes its old vector *visibly* stale, never silently wrong.
2. **Vector orientation is model-space-relative**: `model_id + dims + normalized` on
   every vector; a global serialize groups by model space and never compares across.
   Model upgrade = a new embedding epoch, cut over atomically.
3. **Edges are directed, typed, declared-only, with provenance**: `(from, to, rel,
   declared_in_file, declared_at_commit)`. `declares →` stored once; echo is the
   reverse traversal, never a second row. No row without a declaring source —
   absent ancestry stays absent (the anti-propaganda rule as a constraint).
4. **Global serialization = epochs on the git clock**: every emitter run mints a
   `CatalogEpoch(corpus_commit, catalog_sha)`; every export (doll, atlas, embedding
   batch) stamps its epoch. Cross-epoch artifacts are comparable-but-labeled, never
   silently merged.

### 3 · Field state is computed, never stored as truth
Echo weight, stratum, staleness are materialized views recomputed per epoch from
edges + mtimes — countables that cannot drift because no one can hand-write them.

### 4 · Namespace isolation
The knowledge-graph projection lives in a **separate schema/namespace** (or separate
Supabase project) from the compass product schema (Receipt/PrepSession) so projection
migrations can never tangle with product migrations. pgvector (a DB extension, not an
npm dep) is the vector store — same transaction boundary, JOINs between semantic
neighbors and declared edges. Adopting it remains an ask-first migration.

### 5 · The portable form: dolls
`doll_export.py` / `doll_sprout.py` are the User0 → UserN+1 pair: declared-closure
bundles, cycles as `@ref` pointers, `--bodies` for true tenant bootstrap, epoch-stamped,
with a **fail-closed air-gap gate** (frontmatter `audience:`; absent = internal; an
external cut excludes and *names* what it held). Sprout never overwrites a tenant
belief; the tenant's own inchworm self-catalogs what sprouted.

## The instrument — Infra Compass (ROM candidate)

The Question Compass reads a person's decision fog; the **Infra Compass reads the
meta field state** of corpus + projections + stores. L0 already exists: the
session-start inchworms (lattice-drift, seedbank-drift, memory-sync, snapshot) emit
atomic signals. The missing layers are L1–L5 synthesis over those receipts into a
bearing + epoch-stamped receipt, with the Y-gate mapped:

| Y | Infra condition | Session evidence |
|---|---|---|
| GREEN | corpus ↔ projections aligned at current epoch | post-merge state |
| DRIFT | a projection lags the corpus (regenerate) | lattice count 57 vs 59 |
| FORK | parallel canon minted unserialized | three v3.35.0 handoffs |
| PARADOX | two stores assert contradictory truth | "private pending review" repos sitting public |
| RED | ruin-class exposure (PII, secret, irreversible) | the class the air-gap gate exists for |

Judgment stays human-owned (ADR-051/052 doctrine): the compass reads and synthesizes;
regeneration of countables is mechanical; canon resolution and RED response are human.

### ROM candidate (Mad-Lib form, per Chapter-Book canon)

> "When any two stores assert contradictory truth about the same object (PARADOX),
> ARCS should fail closed to the more restrictive assertion and surface the
> contradiction as a receipt, because a silently resolved paradox is how ruin ships."

Pattern family: drift-receipt / serialization. Pattern name: **"Induced Projection."**

## Consequences

- The emitter (`memory_catalog_emit.py`) becomes the single ETL seam; adding epoch
  stamps + `--emit-sql` is the implementation path when the migration is approved.
- The Terrain Atlas is the compass's render surface (fog = the instrument's
  uncertainty display); dolls are its portable serialization.
- Origin-session / cross-session echo counts become `Activation` rows, not archaeology.
- Not built yet (honest): the Postgres/pgvector projection, the L1–L5 synthesis layer,
  `--bodies`-at-scale hygiene, and ratification of the ROM candidate above.

## Links

Derives from: ADR-051/052 (drift-receipt loop), ADR-053/054 (seed/activation, tao),
ADR-057 (sequence oracle — the git clock), ADR-064 (external corroboration).
Tao: tao-249 (minted with this ADR). Instruments: `scripts/memory_index_sync.py`,
`scripts/memory_catalog_emit.py`, `scripts/doll_export.py`, `scripts/doll_sprout.py`,
`_ARTIFACTS/terrain-atlas.html`.
