# Phosphor cold molt, 2026-10-17

## Goal
Phosphor (`_ARTIFACTS/phosphor.html`, single-file offline audio instrument, "baby DJ that grows with you") for family co-creation: Kid track (pads, simple faders) and Parent track (decks, synths, patch boards). Zach now wants two things in a NEW session: (1) decouple front end from back end of the build process, (2) true up a design system: atomic elements, composition rules, interaction states, motion and animation guidelines, tracking, rendering, light design.

## State (verified at head c788e697 + one uncommitted-then-committed backlog row)
- Shipped and merged: PRs #1428 to #1431 (glitch switch + sticky dock, Eject lock + Song/Sing switch, wide 32:9 frame + Esc-hold + Impeccable install + PRODUCT.md, hide-player bump). Artifact https://claude.ai/artifact/C8SZP9o3ezaHUtKJAveBTe at v36.
- Local, unpushed until this molt: c788e697 (audience tags on 89 backlog rows), plus row `phosphor-consonance-shavasana`.
- Page is 279,611 bytes against a 280,000 cap in `scripts/phosphor_check.mjs` V8. Do NOT raise the cap (raised four times); trim comments or split the build.
- Tempo map (`phosphor-pins-tempo-map`, ruin high, reach 8, blocks 20 rows): STARTED, NO CODE WRITTEN. Relevant code in phosphor.html: `setTempo` (~1848), `pinsUse` (~1414, single grid from anchors), `snapTime` (~1638), beat markers (~1623), `GRID0`/`BPM` used ~25 places (grep). Plan: anchors to piecewise-linear beat positions, fall back to single grid under 2 anchors; pre-register in `_PATTERNS/2026-10-15-phosphor-visualizer-prereg.md` (next amendment is 33) with a drifting-tempo fixture and a mutation proving the check can fail.

## Do NOT redo
Wide frame, hide bump, Eject lock, Song/Sing switch, dock, Impeccable install (project copy done; Codex/Cursor/user-level held), TypeSafe skill (decided not for Phosphor).

## Open
1. Front/back decoupling: today one hand-edited 280 KB HTML. Candidate: source partials (CSS tokens, engine JS, UI) built into the single file by a small stdlib script, so the cap and token gates run on the output. Adopt-vs-build lens: `runtime/specs/phosphor-adopt-vs-build.md`. No new dependency without Zach's approval.
2. Design system true-up: kit at `src/ui-kit/recoil-report/_tokens.css` (inline verbatim, sentinel header kept, `token_source_gate.py`), DESIGN.md radii 3/6/10/16, type ramp 0.6875/0.925/1.15rem. Backlog rows: `design-system-trueup-claude-design-magic-patterns` (Material/MUI reference only; a new dep needs approval), `phosphor-heading-light-rays` (HOLDING). Needs: atomic primitives, composition rules, state matrix (rest/hover/press/focus/disabled/locked), motion guide (durations, easing, reduced-motion, the kintsugi design-debt bans on glow shadows and wide blur), tracking and rendering notes, light design.
3. Kid pad bank in the dock tray (`phosphor-pad-block-banks`, unblocked), conventional DJ deck layout (CSS regrid, keep ids dbplay/dbcue/dbsync/mxla/mxx/mxlb), mini draggable widget, `phosphor-parent-kid-access` (awaiting Zach: per-child profiles/time limits or parent passkey first), key bindings (which variable Ctrl +/- sweeps; suggest effect wet amount), `phosphor-consonance-shavasana` (after the tempo map).
4. Owed: decision receipts for PRs #1422 to #1431 (Supabase `decision_receipt`, project xbbpiryokswwvcrcutge; use the lock: dry run, canary, review, batch); results sections for prereg amendments 31 and 32; reword the Gold Coast true-up row (reference only); hosting on an arcs subdomain (needs Zach's go and subdomain choice; kid-safety gating first).
5. Environment: `gold` and `fx` audio checks read silence since the last resume, identical on merged HEAD (not a regression, undiagnosed). Known failing: sing S2, slice S4. `keys`/`quick` flake under load.

## Tools, skills, memory to load in the new session
- Skills: `impeccable` (project copy in .claude/skills, user-level 4.0.0; run `impeccable context` once), `token-savings-bank` before fan-out, `witness`, `artifact-design`.
- Memory slugs: `single-file-artifacts-inherit-tokens-never-copy`, `arcs-fieldos-design-system`, `design-full-width-lede-matches-heading`, `run-the-repos-own-gates-before-shipping`, `preview-serves-root-branch-trap`, `when-to-teleport-to-terminal-vs-agents`.
- Docs: `PRODUCT.md` (Phosphor section), `DESIGN.md`, `_PATTERNS/arcs-artifact-css-base.css`, `runtime/specs/phosphor-adopt-vs-build.md`, prereg file above.
- Gates: `page_gate.py --matrix full`, `token_source_gate.py`, `component_source_gate`, kintsugi design-debt, `artifact_wrap_lint.py`, `card_gutter_check.mjs`.
- Tests: 38 `scripts/phosphor_*_check.mjs`; run ONE process at a time, no `timeout` on macOS; fixtures `python3 scripts/beat_truth_tracks.py <dir>` then PHOSPHOR_FILES=break-100.wav (mixer: break-100.wav,break-120.wav) for bars/dock/gate/glitchoff/pins/mixer; exclude slice, twin, sing.
- Ship: `scripts/ship_docs.sh "<title>" "<body>"` (clean tracked tree; move untracked `_STATE/witness/2026-10-15.jsonl` aside), merges with `--merge`. Republish the artifact with `Artifact publish url=https://claude.ai/code/artifact/5a1e7b86-43c1-4d04-95c8-ae79282b7869 file_path=<phosphor.html>`.
- Comment threads awaiting Zach: 2786a303 (parent-kid-access), 8688ee2f (key bindings).

## Next action
Pick one lane per session: (A) design-system true-up with Impeccable (`/impeccable document` then `extract`), or (B) build decoupling, or (C) tempo map. Recommend A and B in separate sessions; C keeps the byte cap in view, so do B first if C is wanted.

## Cold-start recipe
Branch `claude/phosphor-beat-fix`; read this file only, then `git log --oneline -8` and `grep -n "GRID0\|setTempo" _ARTIFACTS/phosphor.html`.
