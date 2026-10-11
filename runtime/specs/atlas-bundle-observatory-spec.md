---
spec: atlas-bundle-observatory
version: 0.3
status: SCOPE CONFIRMED by Zach 2026-10-10; build after 2026-10-15 5 PM ET
date: 2026-10-10
build_window: after take-home submission (Thu 2026-10-15 5 PM ET), alongside sprint 2
---

# Atlas Bundle Observatory (private)

A private view in arcs-v9 that loads one `atlas-bundle.json` exported by `./rfp build` in the
take-home repo and renders it in the Field OS explorer grammar (lattice/ziggurat, altimeter F1-F7,
holds, slope and visibility gauges, safe-approach heading tape) with a camera fly-over.

## Hard boundaries
1. **Never public.** Route sits behind `isAdmin(session)` (src/lib/admin.ts, fail-closed in prod),
   rendered server-side. No file under `public/`, no rewrite, no host in `next.config.ts`, no row in
   any public surface catalog. The bundle is never committed to arcs-v9: it is read at request time
   from a local path (dev) or uploaded to a private store (prod, see Open question 3).
   Fallback delivery: a private claude.ai artifact built from the same renderer.
2. **Read-only on the take-home repo.** arcs-v9 reads the exported file only; never writes there.
3. **One-way air gap.** Nothing from arcs-v9 flows into the take-home repo or its ZIP. The bundle
   schema below uses the take-home's own nouns; arcs vocabulary lives only in the arcs-v9 adapter.

## Proposed bundle schema (`atlas-bundle.v1`) — for the take-home session to emit
```jsonc
{
  "schema": "atlas-bundle.v1",
  "generated_at": "ISO-8601",
  "source_head": "git sha",
  "nodes":     [{ "id", "title", "needs": ["id"], "status", "cluster", "epic", "rank",
                  "done_at": "ISO|null" }],                       // from plan.json
  "mistakes":  [{ "id": "K42", "title", "caught_by": "test|canary|war-game|review|user|blind-set",
                  "severity": "ruin|major|minor", "detected_at", "repaired_at",
                  "node_ids": [], "commit": "sha|null" }],         // from KINTSUGI.md
  "decisions": [{ "id", "title", "chosen", "rejected": [{ "option", "why" }],
                  "evidence_grade": "A|B|C|D", "decided_at", "node_ids": [] }],  // DECISIONS.md
  "evals":     [{ "run_id", "at", "set": "dev|blind", "metric", "value", "n" }],
  "predictions": [{ "id", "claim", "p": 0.0, "resolved_at": "|null", "outcome": true, "brier": 0.0 }],
  "snapshots": [{ "at", "label", "path" }],
  "timeline":  [{ "sha", "at", "subject" }]
}
```
Every array may be empty; the renderer shows an empty band, never invents points.

## Mapping (adapter, arcs-v9 side only)
| Visual | Source |
|---|---|
| Position x | `cluster` (job cluster lanes) |
| Position z | time (`done_at` / `decided_at` / `detected_at`) |
| Altitude (F1-F7) | evidence grade A..D and prediction calibration; ungraded = F1 |
| Ziggurat tiers | plan.json `needs` depth (topological level) |
| Vector headings | decisions: arrow toward `chosen`, ghost stubs for each `rejected` |
| Ballistic arcs (gold) | mistakes caught pre-ruin by `canary` / `war-game` / `blind-set`: arc from blind spot to repair |
| Red ruin paths | `severity: ruin` mistakes (K42 silent empty parse, K40 scaled PDF, K35 stale figures), drawn to a cliff edge and terminated at `caught_by` |
| Visibility gauge | blind-set score at time t |
| Slope gauge | open mistakes / open nodes at time t |
| Heading tape | rolling direction of the last N decisions |
| Holds | snapshots |

## Camera script
1. Wide establishing shot, whole lattice, 3 s.
2. One slow spiral around the ziggurat (time scrubs start to end with it).
3. Dwell at vantage points in order: first ruin path caught, each ballistic repair, final blind-set run.
Pausable, scrubbable, `prefers-reduced-motion` => static vantage cards instead of flight.

## Build constraints
Inline styles only; tokens from `src/ui-kit/recoil-report/_tokens.css`; no new deps (3D via hand-rolled
canvas/SVG isometric projection like the existing Scope organisms, unless Zach approves a lib);
`npm run build` + page gate before merge; Decision Receipt on merge.

## Scope decisions (Zach, 2026-10-10)
1. Delivery: admin-only route in arcs-v9 (no claude.ai artifact).
2. Render: 2.5D isometric on canvas, no new deps.
3. Data: local-only. The route reads `~/ret-rfp-intelligence/atlas-bundle.json` from disk in dev;
   in prod it renders an explicit "bundle not available" state, never a fallback dataset.
4. Schema: the take-home session emits `atlas-bundle.v1` exactly as above via `./rfp build`.

## Amendment v0.3 (2026-10-10): source realities from the take-home session
- `KINTSUGI.md` has no detected_at, repaired_at or severity columns, so under the no-backfill rule those
  fields are mostly null. repaired_at comes from the commit naming each K-number (~40 of 50).
- predictions.jsonl outcome 0/1 maps to booleans; 10 of 39 resolved.
- The take-home's older `dist/atlas-bundle.json` (scripts/catch_net.py) is replaced by v1 at the repo root.

Adapter rules (arcs-v9 side only; the bundle is never edited):
1. **Ruin list is curated, not inferred.** Red ruin paths come from a Zach-maintained list in arcs-v9
   (seed: K35, K40, K42). A bundle `severity` value, when present, can add to it but never removes from it.
2. **Missing detected_at:** place the mistake at repaired_at; draw no arc length (a point, not a path).
3. **Missing both timestamps:** list in an "unplaced" side band, never positioned on the time axis.
