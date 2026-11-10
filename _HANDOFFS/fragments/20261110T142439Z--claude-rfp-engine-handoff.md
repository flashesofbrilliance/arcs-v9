<!--
session: claude-rfp-engine-handoff
branch: claude/rfp-engine-handoff
head: 2d877499
created_at: 2026-11-10T14:24:39Z
-->
> Rebuilt good.arcs.care/rfp-engine from verbatim UI kit blocks with earned-fidelity rendering, merged as PR 2110, live and receipted.

### Shavasana — handoff pause, 2026-11-10 (Operator 25, mechanical half; spec runtime/specs/operator-25-shavasana-v0.md)

- **Exhale** (what went out): 0 commits, 0 merges to main (scope: branch claude/rfp-engine-handoff), receipts in digest: no digest file.
- **Inhale** (what came in): 0 falsification rows today, 0 dissent markers, 0 unconfirmed markers in the day's records.
- **Breath balance**: breathing (both directions).
- **Sycophancy check**: agreement 2 / dissent 0 (ratio 2.0) → OK: dissent present.
- **Cold re-read (canary on the draft frag.md)**: GROUNDED; no ground return: none; thin air: none.
- **Attachment release** (human): for each claim in the draft, does it survive without the momentum? Downgrade or drop, and say which.
- **Somatic read** (human, one question): certainty now vs certainty at the start of the session, and were there sends today?
- **Disposition** (human): release the handoff, or return it to the queue with this block attached.

_This block asserts nothing new. Counts, paths, and questions only._

- Attachment release: every claim cites a PR, sha, path or receipt id; the light-mode claim is held to "headless screenshot at 1280 only". Somatic: not asked. Disposition: release.

## Goal
Every good.arcs.care tool page snaps to the UI kit and design system, checked by gates rather than by eye.

## Changed
- PR 2110 merged (`2d877499`, head `bdce89e6`); receipt 2026-11-10--rfp-engine-kit-rebuild-pr2110--ZH (job:backlog:rfp-engine-public-good, tool:script:safe_merge.sh).
- `public/good-rfp-engine.html` now carries kit blocks 27 section-label, 30 button, 37 fidelity, 39 theme, 45 fact-tile and 51 display preferences, plus the generated grammar-chip CSS; tool swatch moved to steel `#3d6a9e` (plan C).
- `.impeccable/config.json`: four one-file waivers for kit-origin findings on this page; seam booked in `_PATTERNS/kintsugi-visual-grammar-seams.md`.
- `_QUEUE/induced-backlog.jsonl`: anthropic-spend-monitor resolve_by moved 2026-11-09 to 2026-11-16 (Zach), which had failed jtbd-graph --check for every commit.

## State
- The page follows the OS light/dark setting with a toggle (it was dark only). Zach chose to keep that, 2026-11-10.
- good.arcs.care/rfp-engine returns 200 and serves the fact-tile block; not looked at in a browser on the live domain.

## Decisions
- Zach: keep OS-following light/dark rather than pinning dark.
- Zach: move the expired resolve_by to 2026-11-16 rather than skip the hook.
- The chip block's internal sentinel comment was removed from the public copy (J24 leak check), not allowlisted; nothing reads it on the page.

## Open
1. Zach: cold-read header (Why, What, Why now, How, How to read) is not applied to tool-getting-started pages; a template-level decision.
2. Kit file 45 fact-tile label is .75rem, off the type ramp; fix in the kit file, then drop the font-size waiver.
3. The video facade on this page is a candidate kit primitive.
4. Copying the grammar chip block onto a public page needs its sentinel stripped; no build step does this yet.

## Next action
Fix the fact-tile label size in `src/ui-kit/recoil-report/45-fact-tile.html` and remove the matching waiver.

## Cold-start
- Read `docs/ui-kit-tool-template-plan.md` and `public/good-rfp-engine.html`; run `python3 scripts/kit_primitive_sync.py --check` and `bash scripts/leak_check.sh`.
- Debt lives in the tracker (https://claude.ai/artifact/AvE1T5TMQD164GPFGetHvm, `debt` collection).
