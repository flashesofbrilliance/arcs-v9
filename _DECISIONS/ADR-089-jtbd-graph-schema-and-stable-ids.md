# ADR-089: JTBD graph schema: four atom kinds, six edge types, source-derived stable ids

> **Status:** PROPOSED (write-locked id scheme; merge needs Zach's explicit approval)
> **Date:** 2026-10-18
> **Author:** Claude Opus 5.5 (Sprint 0 child of `jtbd-graph-conductor`)
> **Oracle:** number allocated via `scripts/oracle.py next adr` (89); `_SEEDS/_oracle.json` committed.
> **Backlog:** `jtbd-graph-s0-schema`; unblocks `jtbd-graph-s1-nodes`.

## D — The Decision

**Sharp question:** What is the one schema every later sprint writes against, so that every Tool,
Job, Blocker and Dependency in arcs-v9 is retrievable as one universe generated from catalogs that
already exist, not a new store?

**Decision:** `runtime/specs/jtbd-graph-schema.json` v1.0.0.
- Atom kinds: `tool`, `job`, `blocker`, `dep`.
- Edge types with legal (from, to) kind pairs: `serves` (tool to job), `blocks` (blocker to job or
  tool), `needs` (job to tool, dep or job), `design-dep` and `runtime-dep` (tool to tool or dep),
  `replaces` (tool to tool, job to job).
- Evidence per edge type, from six formats: `file:line`, `import:file:line`, `backlog:<id>`,
  `route.tool:<row id>`, `commit:<sha>`, `receipt:<id>`. Every edge carries a non-empty evidence
  list and an `inferred` flag; inferred edges name who inferred them.
- **Id scheme (the one-way door):** `id = <kind>:<namespace>:<natural key>`, where the key is the
  source catalog's own key copied verbatim: tool-catalog `name` per kind, registry `op` number,
  surface `host` + `path`, backlog row `id`, memory front-matter `name`, pattern file stem,
  package.json dependency name, env var name. Never a row index, line number or content hash.
  A rename at source is a new id plus a `replaces` edge. A duplicate key inside one source is a
  hard error (SOURCE-DUP); the adapter does not number its way out.
- **One thing, one canonical id.** An operator appears in two sources: the registry (by
  periodic-table number) and tool-catalog (by file name). `tool:op:<n>` is canonical; the
  `tool:operator:<file>` atom is the implementing file and links to it with a `design-dep` edge
  citing the registry binding. Each source still reconciles its own count; retrieval answers
  with the canonical id. Added before merge (review 2026-10-18) so the write-lock covers it.
- Checker: `scripts/jtbd_graph_schema_check.py` (stdlib). `--self-test` runs one good fixture and
  eight bad ones (fixtures beside `runtime/specs/fixtures/jtbd-graph/good.json`): unknown kind, illegal pair, no evidence,
  malformed evidence, unstable id, duplicate id, inferred edge without `by`, dangling edge.
- Gates for s1 to s4 are fixed in `_PATTERNS/2026-10-18-jtbd-graph-preregistration.md`, committed
  in the same commit as this ADR and before any sprint count.

## WRITE-LOCK (ROM primitive 7)

The id derivation rule above is declared irreversible. Once s1 emits atoms, receipts (s5), edges
and Librarian answers cite these ids; changing derivation orphans every citation. Kinds, edge
types, namespaces and evidence formats may be extended (minor version); changing how an existing
namespace derives its id needs a new ADR and a major version with a mapping table. This ADR does
not merge without Zach's explicit approval of the id scheme.

## E — Evidence: the kill condition, checked

Kill condition (row gate): if jobs cannot get stable ids from backlog rows plus memory plus
_PATTERNS, stop and fix job identity first. Checked on 2026-10-18 against origin/main `432e7dde`:

| Source | Units | Natural key | Missing key | Duplicate key |
|---|---|---|---|---|
| `_QUEUE/induced-backlog.jsonl` | 303 rows | `id` | 0 | **1: `phosphor-slip-sync` (lines 164 and 214, byte-identical rows)** |
| memory `*.md` (excl. MEMORY.md) | 334 files | front-matter `name` | 0 | 0 (10 files have name differing from stem; the scheme uses `name`) |
| `_PATTERNS/*.md` | 70 files | file stem | 0 | 0 (filesystem-unique) |

**Verdict: PASS, with one source defect.** Every job source has a natural key that is present on
every unit and does not depend on order. The one defect is a duplicated backlog row; the schema
treats it as SOURCE-DUP, so s1 cannot emit until that row is deduplicated at source (it is not this
sprint's row to touch; reported to the conductor). Caveat on coverage, not identity: only 38 of 334
memory files and 6 of 70 pattern files mention JTBD by keyword, so most job atoms will come from
backlog rows; whether a memory or pattern file *states a job* is s1's mining rule, gated in the
pre-registration (80% agreement on a 30-file labelled sample, else those namespaces ship empty).

## Correction (2026-10-18, amendment 1)
A claims-skeptic check after merge refuted three statements here. (1) The memory row's "Missing key 0"
is wrong: `project_yuri_kleban_google.md` has no top-of-file front matter. (2) The good fixture linked
`arcs_librarian.py` to op 21; the registry binds op 21 to `arcs_store.py` (line 332). The fixture now
uses that binding and cites that line. (3) Wildcard-host surfaces had no legal id; host `*` is written
`any` (Zach). The checker now uses full matches (a trailing newline no longer passes) and requires
`source.line` to be a positive int. Details: `_PATTERNS/2026-10-18-jtbd-graph-preregistration-amendment-1.md`.

## W — What would change this
- A source whose natural key is itself unstable (e.g. tool names that churn with every refactor).
  Mitigation is `replaces` edges, not a new derivation.
- If s4 loses to /catalog, the graph's retrieval value is killed, but the schema still serves the
  s3 integrity gates.

## Y — Consequences
- s1 builds its universe adapter against this schema, pattern of
  `scripts/universe_receipts_adapter.py`.
- No new dependency, no new store: the graph is generated output from existing catalogs.
