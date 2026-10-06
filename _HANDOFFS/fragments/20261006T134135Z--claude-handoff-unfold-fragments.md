<!--
branch: claude/handoff-unfold-fragments
head: 4f7fa6ab
created_at: 2026-10-06T13:41:35Z
-->
> **unfold reads handoff fragments (#899, `4f7fa6ab`, merged with a merge commit, CI green, on Zach's yes).**
> Receipt `2026-10-06--unfold-reads-fragments-pr899--ZH`.

## Done
- `scripts/unfold.py`: new `handoff_open(root)` gathers `## Open` items from every unfolded
  `_HANDOFFS/fragments/*.md` (newest first, via `handoff_fold.fragments`/`parse_fragment`), then the
  latest CLAUDE.md block. Self-test 14/14; the new fragment case fails under the old CLAUDE.md-only logic.
- Live check on main with a throwaway fragment: listed first, then v3.102.0's three items; probe deleted.
- Other readers of the latest CLAUDE.md block: none. `open_loops.py` does not parse it; no live
  `~/.claude/hooks` reads it (`precompact-handoff.sh.retired-2026-09-04` was a writer, retired);
  `handoff-pickup.md` already reads fragments (#898).

## Open (next session)
1. No real fragment has been through `unfold.py` yet (receipt lists it unconfirmed). First `/handoff` fragment closes it.
2. Deploy of `4f7fa6ab` not verified (Vercel CLI returned nothing this session).

## Lessons (in the record)
- #898 was merged by its own session mid-train; `merge_train.sh` refused cleanly (state MERGED), then #899 retargeted to main and merged alone.
