# _HANDOFFS

`fragments/` holds one handoff per session, written by `/handoff` via `scripts/handoff_fold.py new`.
Each is a new file, so two sessions finishing at once never edit the same lines.
`scripts/handoff_fold.py fold` assigns `vX.Y.Z`, prepends the blocks to `CLAUDE.md`, relocates
overflow to `_ARCHIVE/handoffs.md`, and deletes the folded fragments. Decision: ADR-085 part (d).
