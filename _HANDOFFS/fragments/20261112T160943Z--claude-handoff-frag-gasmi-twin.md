<!--
session: claude-handoff-frag-gasmi-twin
branch: claude/handoff-frag-gasmi-twin
head: 80e9827b
created_at: 2026-11-12T16:09:43Z
-->
# Gasmi counterpart twin matches the war-room look Doug's link showed, 2026-11-12

## Goal
Make `public/recoil-ext/2026-10-29-gasmi.html` (where PR 2168 sends non-admins) look like the war-room page Zach emailed Doug (Dioptra) on 2026-11-11, with audience "both" content only.

## What changed
- #2180 open, head 0e2b16e7, not merged: `scripts/recoil_brief.py` gains layout "stack" (header card, then numbered sections in one scroll, CSS scoped under .stack, main landmark); the Gasmi SSOT sets it through `meta.external_sets` (`page.layout=stack`); twin regenerated with `scripts/recoil_ext_build.sh`. One hood line reworded ("tab" to "Sections 2 to 5 are the method..."). No receipt yet (nothing merged).
- Screenshots for the PR live on side branch `pr-assets/gasmi-twin-warroom-look` (not for merge).

## State
- Target confirmed by Zach in this session: look A (WarRoomReport.tsx at 723834b8, main as of the 11-11 17:49 UTC email), header chips dropped.
- Leak scan 0; page_gate --counterpart pass with no warnings; artifact_wrap_lint, token_source_gate, component_source_gate pass; pre-commit hooks pass. Other tabbed reports render unchanged.

## Decisions
- Zach: target is the 11-11 war-room look, not today's fold layout; drop the Y, NCI, topology and req-reality chips on the external page.

## Open
1. Zach: merge #2180 (`scripts/safe_merge.sh 2180 0e2b16e7`), then a decision receipt, then open Doug's link signed out after deploy.
2. Delete branch `pr-assets/gasmi-twin-warroom-look` after merge.

## Next
Zach gives the go on #2180.

## Cold start
- PR #2180 body (before, after, target screenshots; gate output).
- Note: side-session-notes/local_d5cf3d9b-e977-43c8-adac-8c86c2285a3c/gasmi-twin-warroom-look.md.
