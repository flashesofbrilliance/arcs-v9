# _HANDOFFS

`fragments/` holds one handoff per session, written by `/handoff` via `scripts/handoff_fold.py new`.
Each is a new file, so two sessions finishing at once never edit the same lines. Fragments are raw
material (headed sections: Changed, State, Decisions, Open, Next action, Cold-start; schema in the
script docstring). `scripts/handoff_fold.py molt` synthesizes ALL of them into ONE arc block in
`CLAUDE.md`, numbered by `scripts/oracle.py next handoff`, gated against bookends, relocates overflow
(by version) to `_ARCHIVE/handoffs.md`, and deletes the molted fragments. Decision: ADR-085 part (d)
and its 2026-10-06 amendment.

## arcs/ (proposed 2026-10-06)

`arcs/<domain>.md` holds one long-lived, cold-moltable arc per domain (jobs, recoil, infra, compass,
canon, outward), in the molt schema (Goal, What changed, State, Decisions, Open, Next action,
Cold-start). The molt itself still writes ONE cross-domain block to `CLAUDE.md`; arcs are the
per-domain resume point that a cold session opens when its task names a domain. First set was
reconstructed from every handoff ever committed: `scripts/handoff_excavate.py` (index, no LLM) ->
`scripts/handoff_cluster.py` (deterministic domain clustering; Op20/Op21 ran but do not fit text
blocks) -> per-domain synthesis. Raw index, units and the salvage ledger (verdict + evidence for every
unmatched open loop) live in `_STATE/handoff-excavation/`.
