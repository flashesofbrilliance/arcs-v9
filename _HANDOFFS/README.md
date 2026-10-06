# _HANDOFFS

`fragments/` holds one handoff per session, written by `/handoff` via `scripts/handoff_fold.py new`.
Each is a new file, so two sessions finishing at once never edit the same lines. Fragments are raw
material (headed sections: Changed, State, Decisions, Open, Next action, Cold-start; schema in the
script docstring). `scripts/handoff_fold.py molt` synthesizes ALL of them into ONE arc block in
`CLAUDE.md`, numbered by `scripts/oracle.py next handoff`, gated against bookends, relocates overflow
(by version) to `_ARCHIVE/handoffs.md`, and deletes the molted fragments. Decision: ADR-085 part (d)
and its 2026-10-06 amendment.
