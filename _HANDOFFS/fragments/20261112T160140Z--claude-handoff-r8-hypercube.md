<!--
session: claude-handoff-r8-hypercube
branch: claude/handoff-r8-hypercube
head: f43a3f0d
created_at: 2026-11-12T16:01:40Z
-->
# R8 recoil hypercube index (J4) and its follow-ups, 2026-11-12

## Goal
Stage J4 of the recoil call service (ADR-060 penteract cells from J2 verbs and J3 claims) plus an explorer view.

## What changed
- #2166 merged as 101eeb1c (by the sweep session local_393c66c5 on Zach's "lets merge those"; receipt filed by that session, id not checked here): `scripts/recoil_stage_j4.py` (J4 as a stage plugin), `scripts/recoil_hypercube_explorer.py` generating `_ARTIFACTS/recoil-hypercube-explorer.html` (kit blocks, template recoil-skim; 2D slice plus filled-cell list; empty data renders grain n=0), and a `PLUGINS` list in `scripts/recoil_service.py`. Rows recoil-decompose-verbs and forecast-base-rates set DONE; recoil-hypercube-index DONE on main.
- #2177 open, head b0772883, not merged: J4 operator becomes a judged axis. The ruling-to-operator table (GROUNDED LAB, INFERENCE KKL, STRUCK FUNHOUSE) is dropped; operator glosses are bound to the periodic table and registry (LAB op 17 Detective, COURT op 18 Immune, KKL Kai force; BAR and FUNHOUSE from ADR-060 section 4) with a drift self-test. J4 version 1 to 2. Zach's go relayed from local_dfd22ff0: "go ahead". Handed to the recoil orchestrator local_6d106b64 to merge.
- Child session local_61d373e9 "Gasmi twin page: match the war-room look" is running, no PR yet: make `public/recoil-ext/2026-10-29-gasmi.html` (counterpart-safe twin, redirect added by PR 2168 ad288444) look like the war-room page Zach sent Doug on 2026-11-11. It confirms the target with Zach by screenshot first; no merge or deploy without his go.

## State
- No real J4 cells exist on main: Gasmi J4 is NOT RUN n=0 because J2 and J3 have never run with a model.
- Self-test PASS; explorer page_gate, wrap-lint, component and token source gates PASS; design detector 0.

## Decisions
- Zach: drop the ruling-to-operator mapping (operator is judgment).

## Open
1. Zach: merge PR 2177 (through the recoil orchestrator).
2. Zach: pre-register a J4 bar (proposal: 0 invented cells, at least 3 filled cells on one real call, cold reader agrees on at least 2 of 3 sampled cells), then give a budget and go for a live J2 to J4 run on Gasmi (`--budget-usd 1.00`). Brian has no committed SSOT, only the rendered page.
3. Zach: confirm the target look for the Gasmi twin in session local_61d373e9.
4. handoff-molt-guard in `scripts/git-hooks/pre-commit` blocks merge commits that bring a molt from main; it needed ARCS_ALLOW_DIRECT_HANDOFF=1 on c35957ca. Fix: skip when CLAUDE.md equals the merged parent.
5. `scripts/backlog_status_check.py` crashes on a date-only `claimed_at` (naive vs aware datetime).

## Next action
Zach pre-registers the J4 bar and approves the paid Gasmi run.

## Cold start
- `gh pr view 2177`; J4 design in the docstring of `scripts/recoil_stage_j4.py`.
- Validate offline: `python3 scripts/recoil_service.py --self-test`; explorer: `python3 scripts/recoil_hypercube_explorer.py --data <runs/<stem>/ssot.v2.json> <runs/<stem>/explorer.html>`.
- Hand-over notes: side-session-notes folder of local_dfd22ff0, file R8-recoil-hypercube-index.md.
