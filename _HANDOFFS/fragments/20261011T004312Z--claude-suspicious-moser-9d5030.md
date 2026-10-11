<!--
session: atlas bundle observatory spec
branch: claude/suspicious-moser-9d5030
head: b1b5a17f
created_at: 2026-10-11T00:43:12Z
-->
## Changed
- #1145 merged (a9097538): `runtime/specs/atlas-bundle-observatory-spec.md` v0.2, a design spec and the `atlas-bundle.v1` schema for a private observatory view over the monday take-home's exported bundle (lattice/ziggurat, altimeter F1-F7, heading arrows, ballistic repairs, red ruin paths, camera fly-over). Receipt `2026-10-10--atlas-bundle-observatory-spec-pr1145--ZH`.

## State
- No code yet. `~/ret-rfp-intelligence/atlas-bundle.json` does not exist (checked 18:07 ET).

## Decisions
- Zach 2026-10-10: admin-only route (isAdmin, fail-closed), 2.5D isometric canvas with no new deps, local-only data (prod shows "bundle not available"), take-home emits atlas-bundle.v1 as specified.
- Boundaries: never public; read-only on the take-home repo; nothing from arcs-v9 flows into it.

## Open
1. Zach: pass the schema block from the spec to the take-home writer session.
2. After Thu 2026-10-15 17:00 ET and once the bundle exists: build the admin route, run npm run build + page gate, PR, merge receipt.

## Next action
After submission, confirm the bundle file exists, then build the route against it.
